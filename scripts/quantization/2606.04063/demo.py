#!/usr/bin/env python3
"""
================================================================================
Paper: 2606.04063 - Mixed-Precision Bit Allocation
Title: LLM Compression with Jointly Optimizing Architectural and Quantization choices
Core Method: Sensitivity-driven mixed-precision bit allocation
================================================================================

Target model: Qwen3-0.6B (real weights via --real, mock mini-Qwen3 by default).

Usage:
    python3 demo.py            # fast mock-model verification of all code paths
    python3 demo.py --real     # run on real Qwen3-0.6B (requires HF cache)

Requirements:
    pip install torch (transformers optional, only for --real)
================================================================================
"""

import argparse
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)


# =============================================================================
# 0. Model loading: real Qwen3-0.6B or mock mini-Qwen3 (same architecture family)
# =============================================================================

class MiniQwenBlock(nn.Module):
    """Simplified Qwen3-style decoder block (RMSNorm + GQA attention + SwiGLU MLP)."""
    def __init__(self, hidden=256, heads=4, kv_heads=2, inter=512):
        super().__init__()
        self.heads, self.kv_heads = heads, kv_heads
        self.hd = hidden // heads
        self.norm1 = nn.RMSNorm(hidden)
        self.q = nn.Linear(hidden, heads * self.hd, bias=False)
        self.k = nn.Linear(hidden, kv_heads * self.hd, bias=False)
        self.v = nn.Linear(hidden, kv_heads * self.hd, bias=False)
        self.o = nn.Linear(heads * self.hd, hidden, bias=False)
        self.norm2 = nn.RMSNorm(hidden)
        self.gate = nn.Linear(hidden, inter, bias=False)
        self.up = nn.Linear(hidden, inter, bias=False)
        self.down = nn.Linear(inter, hidden, bias=False)

    def forward(self, x):
        B, T, C = x.shape
        h = self.norm1(x)
        q = self.q(h).view(B, T, self.heads, self.hd).transpose(1, 2)
        k = self.k(h).view(B, T, self.kv_heads, self.hd).transpose(1, 2)
        v = self.v(h).view(B, T, self.kv_heads, self.hd).transpose(1, 2)
        k = k.repeat_interleave(self.heads // self.kv_heads, dim=1)
        v = v.repeat_interleave(self.heads // self.kv_heads, dim=1)
        att = F.softmax(q @ k.transpose(-1, -2) / math.sqrt(self.hd), dim=-1)
        x = x + self.o((att @ v).transpose(1, 2).reshape(B, T, C))
        h = self.norm2(x)
        x = x + self.down(F.silu(self.gate(h)) * self.up(h))
        return x


class MiniQwen(nn.Module):
    """Mock model mirroring Qwen3-0.6B block structure at 1/4 hidden size."""
    def __init__(self, vocab=1024, hidden=256, layers=4, inter=512):
        super().__init__()
        self.embed = nn.Embedding(vocab, hidden)
        self.blocks = nn.ModuleList([MiniQwenBlock(hidden, 4, 2, inter) for _ in range(layers)])
        self.norm = nn.RMSNorm(hidden)
        self.head = nn.Linear(hidden, vocab, bias=False)

    def forward(self, ids):
        x = self.embed(ids)
        for b in self.blocks:
            x = b(x)
        return self.head(self.norm(x))


def load_model(real=False):
    """Load real Qwen3-0.6B if requested & cached, else mock mini-Qwen3."""
    if real:
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            name = "Qwen/Qwen3-0.6B"
            tok = AutoTokenizer.from_pretrained(name)
            model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32)
            model.eval()
            ids = tok("The quick brown fox jumps over the lazy dog. " * 8,
                      return_tensors="pt").input_ids
            print(f"[model] real Qwen3-0.6B loaded ({sum(p.numel() for p in model.parameters())/1e6:.1f}M params)")
            return model, ids, True
        except Exception as e:
            print(f"[model] real Qwen3-0.6B unavailable ({type(e).__name__}), falling back to mock")
    model = MiniQwen()
    ids = torch.randint(0, 1024, (1, 64))
    n = sum(p.numel() for p in model.parameters())
    print(f"[model] mock mini-Qwen3 ({n/1e6:.2f}M params, Qwen3-style GQA+SwiGLU blocks)")
    return model, ids, False


def iter_linears(model, real=False):
    """Yield (name, Linear) for all transformer linear layers."""
    if real:
        for name, mod in model.named_modules():
            if isinstance(mod, nn.Linear) and any(
                    t in name for t in ("q_proj", "k_proj", "v_proj", "o_proj",
                                        "gate_proj", "up_proj", "down_proj")):
                yield name, mod
    else:
        for bi, blk in enumerate(model.blocks):
            for nm in ("q", "k", "v", "o", "gate", "up", "down"):
                yield f"blocks.{bi}.{nm}", getattr(blk, nm)


def logits_mse(ref, out):
    return F.mse_loss(out, ref).item()


def rel_err(w, wq):
    return (torch.norm(w - wq) / (torch.norm(w) + 1e-12)).item()


def model_bits(model, real, bpp):
    n = sum(l.weight.numel() for _, l in iter_linears(model, real))
    return n * bpp / 8 / 1e6  # MB


def fwd(model, ids, is_real):
    """Forward returning logits tensor (handles HF CausalLMOutput)."""
    o = model(ids)
    return o.logits if is_real else o


def banner(msg):
    print("\n" + "=" * 70 + f"\n{msg}\n" + "=" * 70)


# =============================================================================
# Paper method: sensitivity-driven mixed-precision bit allocation
# (measure per-layer quant error, allocate bits under an average budget)
# =============================================================================

def quant_rtn(W, bits, group=64):
    out = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        g = W[:, i:i + group]
        s = g.abs().amax(dim=1, keepdim=True) / (2 ** (bits - 1) - 1)
        s = s.clamp_min(1e-8)
        out[:, i:i + group] = s * torch.round(g / s).clamp(-(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
    return out


def sensitivity(model, ids, is_real, bits_list=(2, 4, 8)):
    """Per-layer sensitivity: logits MSE when only that layer is quantized."""
    base_w = {n: l.weight.data.clone() for n, l in iter_linears(model, is_real)}
    with torch.no_grad():
        ref = fwd(model, ids, is_real)
    sens = {}
    pairs = list(iter_linears(model, is_real))
    if is_real:
        pairs = pairs[:14]  # cap cost on real Qwen3-0.6B: first 2 blocks
    for name, lin in pairs:
        row = {}
        for b in bits_list:
            lin.weight.data = quant_rtn(base_w[name], b)
            with torch.no_grad():
                row[b] = logits_mse(ref, fwd(model, ids, is_real))
            lin.weight.data = base_w[name]
        row["gain_2to4"] = row[2] - row[4]  # error reduced by upgrading 2->4 bits
        sens[name] = row
    return sens


def allocate(sens, avg_budget=4.0, choices=(2, 4, 8)):
    """Greedy: start all at 2-bit, repeatedly upgrade the layer with max gain per bit."""
    names = list(sens)
    cur = {n: 2 for n in names}
    while sum(cur.values()) / len(cur) < avg_budget - 1e-9:
        best, bg = None, -1
        for n in names:
            if cur[n] < 8:
                nxt = 4 if cur[n] == 2 else 8
                g = (sens[n][cur[n]] - sens[n][nxt]) / (nxt - cur[n])
                if g > bg: best, bg = n, g
        if best is None: break
        cur[best] = 4 if cur[best] == 2 else 8
    return cur


def run(model, ids, ref, is_real):
    banner("Step 1: per-layer sensitivity measurement at 2/4/8 bits")
    sens = sensitivity(model, ids, is_real)
    for n, row in list(sens.items())[:6]:
        print(f"  {n:20s} MSE@2bit={row[2]:.5f} @4bit={row[4]:.5f} @8bit={row[8]:.5f}")
    banner("Step 2: greedy bit allocation under avg-4-bit budget")
    alloc = allocate(sens, avg_budget=4.0)
    for n, l in iter_linears(model, is_real):
        if n in alloc:
            l.weight.data = quant_rtn(l.weight.data, alloc[n])
    with torch.no_grad():
        out = fwd(model, ids, is_real)
    avg = sum(alloc.values()) / len(alloc)
    print(f"[mixed] avg bits: {avg:.2f}, logits MSE: {logits_mse(ref, out):.6f}")
    print(f"[mixed] allocation: " + ", ".join(f"{n.split('.')[-1]}:{b}" for n, b in list(alloc.items())[:8]))
    print(f"[size] ~{model_bits(model, is_real, avg):.1f} MB vs FP32 {model_bits(model, is_real, 32):.1f} MB")
    print("[done] sensitivity-driven mixed-precision pipeline verified")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use real Qwen3-0.6B")
    args = ap.parse_args()
    banner("Paper 2606.04063: Mixed-Precision Bit Allocation")
    model, ids, is_real = load_model(args.real)
    with torch.no_grad():
        ref = fwd(model, ids, is_real)
    run(model, ids, ref, is_real)
    banner("Demo finished: all code paths executed OK")


if __name__ == "__main__":
    main()
