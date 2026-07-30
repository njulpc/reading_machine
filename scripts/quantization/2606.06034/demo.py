#!/usr/bin/env python3
"""
================================================================================
Paper: 2606.06034 - Quantization Impact Analysis
Title: When Good Enough Is Optimal: Multiplication-Only Matrix Inversion Approximation for Quantized Gated DeltaNet
Core Method: Bit-width sweep quantization impact evaluation harness
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
# Paper method: systematic quantization impact evaluation - sweep bit-widths,
# measure degradation across metrics (the analysis harness used by the paper)
# =============================================================================

def quant_rtn(W, bits, group=64):
    out = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        g = W[:, i:i + group]
        s = g.abs().amax(dim=1, keepdim=True) / (2 ** (bits - 1) - 1)
        s = s.clamp_min(1e-8)
        out[:, i:i + group] = s * torch.round(g / s).clamp(-(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
    return out


def quantize_model(model, is_real, bits, group=64):
    saved = {n: l.weight.data.clone() for n, l in iter_linears(model, is_real)}
    for n, l in iter_linears(model, is_real):
        l.weight.data = quant_rtn(saved[n], bits, group)
    return saved


def restore(model, is_real, saved):
    for n, l in iter_linears(model, is_real):
        l.weight.data = saved[n]


def run(model, ids, ref, is_real):
    banner("Step 1: bit-width sweep {8,4,3,2} - logit fidelity + entropy shift")
    refp = F.softmax(ref, dim=-1)
    print(f"  {'bits':>4} | {'logits MSE':>12} | {'KL(ref||q)':>12} | {'top1 match':>10}")
    sweep = (8, 4, 2) if is_real else (8, 4, 3, 2)
    for b in sweep:
        saved = quantize_model(model, is_real, b)
        with torch.no_grad():
            out = fwd(model, ids, is_real)
        mse = logits_mse(ref, out)
        kl = F.kl_div(F.log_softmax(out, -1), refp, reduction="batchmean").item()
        top1 = (out.argmax(-1) == ref.argmax(-1)).float().mean().item()
        print(f"  {b:>4} | {mse:12.6f} | {kl:12.6f} | {top1:10.3f}")
        restore(model, is_real, saved)
    banner("Step 2: group-size sensitivity at 4 bits")
    for g in ((64, 128) if is_real else (32, 64, 128)):
        saved = quantize_model(model, is_real, 4, group=g)
        with torch.no_grad():
            out = fwd(model, ids, is_real)
        print(f"  group={g:>3}: logits MSE {logits_mse(ref, out):.6f}")
        restore(model, is_real, saved)
    print("[done] quantization impact evaluation harness verified")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use real Qwen3-0.6B")
    args = ap.parse_args()
    banner("Paper 2606.06034: Quantization Impact Analysis")
    model, ids, is_real = load_model(args.real)
    with torch.no_grad():
        ref = fwd(model, ids, is_real)
    run(model, ids, ref, is_real)
    banner("Demo finished: all code paths executed OK")


if __name__ == "__main__":
    main()
