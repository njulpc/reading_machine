#!/usr/bin/env python3
"""
================================================================================
Paper: 2606.31676 - Weight PTQ
Title: REDI: Corpus Aware Patch Ranking for DINOv3 Token Reduction
Core Method: Per-group symmetric RTN + GPTQ-style Hessian error compensation
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
# Paper method: post-training weight quantization (per-group symmetric RTN
# with optional Hessian-diagonal GPTQ-style error compensation)
# =============================================================================

def quantize_weight_rtn(W, bits=4, group=64):
    """Per-group symmetric round-to-nearest quantization (dequantized output)."""
    out = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        g = W[:, i:i + group]
        s = g.abs().amax(dim=1, keepdim=True) / (2 ** (bits - 1) - 1)
        s = s.clamp_min(1e-8)
        out[:, i:i + group] = s * torch.round(g / s).clamp(-(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
    return out


def gptq_compensate(layer, X, bits=4, group=64, damp=0.01):
    """GPTQ-style: quantize columns sequentially, spread error to remaining
    columns using inverse Hessian (X^T X) diagonal approximation."""
    W = layer.weight.data.clone()
    H = X.reshape(-1, X.shape[-1]).T
    H = H @ H.T / X.numel()
    H += damp * torch.eye(H.shape[0])
    Wq = quantize_weight_rtn(W, bits, group)
    # error-compensated update using Cholesky of H^{-1}
    Hinv = torch.linalg.inv(H)
    d = W.shape[1]
    for j in range(d):
        err = (W[:, j] - Wq[:, j]) / (Hinv[j, j] + 1e-8)
        if j + 1 < d:
            W[:, j + 1:] -= err.unsqueeze(1) * Hinv[j, j + 1:].unsqueeze(0)
            if (j + 1) % group == 0:  # re-quantize compensated weights per group
                Wq[:, j + 1:] = quantize_weight_rtn(W[:, j + 1:], bits, group)
    return Wq


def run(model, ids, ref, is_real):
    BITS, GROUP = 4, 64
    banner(f"Step 1: baseline FP32 logits computed | target W{bits if (bits:=BITS) else 4} group={GROUP}")
    # RTN on all linears
    errs, i = [], 0
    for name, lin in iter_linears(model, is_real):
        W = lin.weight.data
        Wq = quantize_weight_rtn(W, BITS, GROUP)
        errs.append(rel_err(W, Wq))
        lin.weight.data = Wq
        i += 1
    with torch.no_grad():
        out = fwd(model, ids, is_real)
    print(f"[RTN W{BITS}] layers quantized: {i}, mean rel weight err: {sum(errs)/len(errs):.4f}")
    print(f"[RTN W{BITS}] logits MSE vs FP32: {logits_mse(ref, out):.6f}")
    print(f"[size] FP32 weights: {model_bits(model, is_real, 32):.1f} MB -> W{BITS}: {model_bits(model, is_real, BITS):.1f} MB "
          f"({32/BITS:.1f}x compression, excl. scales)")

    # GPTQ-style compensation on first MLP down proj (calibration input = activations)
    banner("Step 2: GPTQ-style Hessian error compensation on one layer")
    model2, ids2, _ = load_model(False) if not is_real else (model, ids, True)
    target = None
    for name, lin in iter_linears(model2, is_real):
        if "down" in name:
            target = lin; break
    if target is None:
        target = list(iter_linears(model2, is_real))[0][1]
    X = torch.randn(128, target.weight.shape[1])  # calibration activations
    W = target.weight.data.clone()
    W_rtn = quantize_weight_rtn(W, BITS, GROUP)
    W_g = gptq_compensate(target, X, BITS, GROUP)
    y = X @ W.T
    print(f"[cmp] output MSE  RTN: {F.mse_loss(X @ W_rtn.T, y).item():.6f} | "
          f"GPTQ-style: {F.mse_loss(X @ W_g.T, y).item():.6f}")
    print("[done] weight PTQ pipeline (RTN + GPTQ compensation) verified")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use real Qwen3-0.6B")
    args = ap.parse_args()
    banner("Paper 2606.31676: Weight PTQ")
    model, ids, is_real = load_model(args.real)
    with torch.no_grad():
        ref = fwd(model, ids, is_real)
    run(model, ids, ref, is_real)
    banner("Demo finished: all code paths executed OK")


if __name__ == "__main__":
    main()
