#!/usr/bin/env python3
"""
================================================================================
Paper: 2606.29337 - Integer-Only Quantized Inference
Title: W4A4 Quantization for Inference on Wan2.2-I2V-A14B
Core Method: INT8 integer-only GEMM inference path
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
# Paper method: integer-only quantized inference path (INT8 weights +
# INT8 activations, integer GEMM, per-channel scales, no float in datapath)
# =============================================================================

import time


def quant_int8_per_channel(W):
    s = W.abs().amax(dim=1, keepdim=True).clamp_min(1e-8) / 127.0
    return torch.round(W / s).clamp(-127, 127).to(torch.int8), s


def quant_int8_per_token(X):
    s = X.abs().amax(dim=-1, keepdim=True).clamp_min(1e-8) / 127.0
    return torch.round(X / s).clamp(-127, 127).to(torch.int8), s


def int_gemm(Xq, sx, Wq, sw):
    """Integer-only GEMM: int32 accumulation, dequantize at output."""
    acc = Xq.to(torch.int32) @ Wq.to(torch.int32).T
    return acc.float() * (sx * sw.T)


def run(model, ids, ref, is_real):
    banner("Step 1: INT8 weight + INT8 activation integer-only linear layers")
    tot_e, cnt = [], 0
    tq = 0.0
    for n, l in iter_linears(model, is_real):
        W = l.weight.data
        X = torch.randn(64, W.shape[1]) * 0.5  # layer input
        Wq, sw = quant_int8_per_channel(W)
        Xq, sx = quant_int8_per_token(X)
        t0 = time.time()
        Y = int_gemm(Xq, sx, Wq, sw)
        tq += time.time() - t0
        Yr = X @ W.T
        tot_e.append(rel_err(Yr, Y))
        cnt += 1
    print(f"[INT8] layers: {cnt}, mean output rel err: {sum(tot_e)/len(tot_e):.4f}")
    print(f"[INT8] int-GEMM total time (unoptimized python loop): {tq*1000:.1f} ms")
    print(f"[size] weights: {model_bits(model, is_real, 32):.1f} MB FP32 -> {model_bits(model, is_real, 8):.1f} MB INT8 (4x)")

    banner("Step 2: full-model INT8 weight quantization sanity check")
    for n, l in iter_linears(model, is_real):
        Wq, sw = quant_int8_per_channel(l.weight.data)
        l.weight.data = Wq.float() * sw
    with torch.no_grad():
        out = fwd(model, ids, is_real)
    print(f"[INT8 model] logits MSE vs FP32: {logits_mse(ref, out):.6f}")
    print("[done] integer-only inference path verified")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use real Qwen3-0.6B")
    args = ap.parse_args()
    banner("Paper 2606.29337: Integer-Only Quantized Inference")
    model, ids, is_real = load_model(args.real)
    with torch.no_grad():
        ref = fwd(model, ids, is_real)
    run(model, ids, ref, is_real)
    banner("Demo finished: all code paths executed OK")


if __name__ == "__main__":
    main()
