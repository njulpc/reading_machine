#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.08692 - AAAC: Activation-Aware Adaptive Codebooks for 4-bit LLM
       Weight Quantization
Core Method: replace the fixed scalar 4-bit codebook with two small learned
             scalar codebooks (64 bytes each) per layer; each weight group
             picks the codebook minimizing activation-weighted reconstruction
             error, with the choice encoded in the unused sign bit of the
             group's positive scale (zero storage overhead).
================================================================================
Demo on Qwen3-0.6B:
  1. Learn two non-uniform 16-level codebooks by weighted Lloyd iterations on
     the layer's weights (activation-weighted)
  2. Per group of 128 weights, select codebook by activation-weighted MSE
  3. Compare against the standard fixed symmetric 4-bit grid (AWQ/GPTQ-style)

Validation: real Qwen3-0.6B weights when available; mock otherwise.
"""
import os
from pathlib import Path
import torch

QWEN_PATH = os.environ.get(
    "QWEN3_WEIGHTS",
    str(Path(__file__).resolve().parents[3] / "_work" / "qwen3-0.6b.safetensors"))


def get_weight():
    if os.path.exists(QWEN_PATH):
        from safetensors import safe_open
        with safe_open(QWEN_PATH, framework="pt") as f:
            W = f.get_tensor("model.layers.5.mlp.down_proj.weight").float()
        return W[:1024, :1024], "real Qwen3-0.6B tensor"
    g = torch.Generator().manual_seed(0)
    return torch.randn(1024, 1024, generator=g) * 0.02, "mock weight"


def fixed_grid_quant(W, aw, group=128, bits=4):
    """Baseline fixed symmetric 4-bit grid, per-group scale."""
    q = 2 ** (bits - 1) - 1
    Wq = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        G = W[:, i:i + group]
        s = G.abs().amax(dim=1, keepdim=True) / q
        Wq[:, i:i + group] = (G / s).round().clamp(-q, q) * s
    return Wq


def learn_codebook(w, weights, k=16, iters=30):
    qs = torch.linspace(0.001, 0.999, k)
    c = torch.quantile(w, qs)
    for _ in range(iters):
        a = (w.unsqueeze(1) - c.unsqueeze(0)).abs().argmin(1)
        for j in range(k):
            m = a == j
            if m.any():
                c[j] = (w[m] * weights[m]).sum() / weights[m].sum()
    return c


def aaac_quant(W, aw, group=128):
    w = W.flatten()
    awf = aw.flatten()
    # two complementary codebooks: one density-optimized, one tail-optimized
    c0 = learn_codebook(w, awf)
    c1 = learn_codebook(w, awf * w.abs().clamp_min(1e-8))
    Wq = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        G, A = W[:, i:i + group], aw[:, i:i + group]
        best, best_err = None, None
        for c in (c0, c1):
            idx = (G.unsqueeze(-1) - c.view(1, 1, -1)).abs().argmin(-1)
            Q = c[idx]
            err = ((Q - G).pow(2) * A).sum()
            if best_err is None or err < best_err:
                best, best_err = Q, err
        Wq[:, i:i + group] = best
    return Wq


def main():
    torch.manual_seed(0)
    W, src = get_weight()
    print(f"Weight source: {src}  shape={tuple(W.shape)}")
    aw = torch.rand_like(W) * 0.5 + 0.5      # activation-aware weights proxy

    for name, fn in [("fixed 4-bit grid", fixed_grid_quant), ("AAAC 4-bit", aaac_quant)]:
        Wq = fn(W, aw)
        err = ((Wq - W).pow(2) * aw).sum() / (W.pow(2) * aw).sum()
        print(f"{name:18s} activation-weighted rel-err = {err:.5f}")

    print("\nPASS: AAAC demo executed end-to-end.")


if __name__ == "__main__":
    main()
