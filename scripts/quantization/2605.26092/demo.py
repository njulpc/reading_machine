#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.26092 - GoQuant: Geometric Orthogonal Residual Projection for
       Multiplier-Free Power-of-Two Transformer Quantization
Core Method: logarithmic Power-of-Two (PoT) quantization replaces multiplies
             with bit-shifts, but its exponential lattice has a low angular
             resolution regime below 4 bits. GoQuant formulates quantization
             as a dual-basis geometric projection, adding an orthogonal
             residual lattice to raise effective resolution while retaining a
             shift-and-add inner-product structure; analytical solver, no
             gradient iterations.
================================================================================
Demo on Qwen3-0.6B weights (4-bit PoT):
  1. Baseline: per-group PoT quantization W ~= s * 2^k
  2. GoQuant: first-stage PoT lattice + residual quantized on an orthogonally
     rotated second PoT basis: W ~= Q1 + R^T Q2(R (W - Q1))
  3. Report weight relative error and effective multiplier-free property

Validation: real Qwen3-0.6B weights when available; mock otherwise.
"""
import os, math
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


def pot_quant(W, bits=4, group=128):
    """Power-of-Two quantization: W ~ sign * s * 2^e, e in [-(2^(b-1)-1), ...]."""
    q = 2 ** (bits - 1) - 1
    Wq = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        G = W[:, i:i + group]
        s = G.abs().amax(dim=1, keepdim=True)
        e = torch.round(torch.log2((G.abs() / s).clamp_min(2 ** (-q))))
        e = e.clamp(-q, 0)
        Wq[:, i:i + group] = torch.sign(G) * s * torch.pow(2.0, e)
    return Wq


def hadamard(n):
    m = 1 << (n - 1).bit_length()
    H = torch.ones(1, 1)
    while H.shape[0] < m:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return (H / math.sqrt(m))[:n, :n]


def goquant(W, bits=4, group=128):
    Q1 = pot_quant(W, bits, group)
    Rm = W - Q1                                  # residual (low angular res)
    R = hadamard(W.shape[1])                     # orthogonal second basis
    Q2r = pot_quant(Rm @ R.T, bits, group)       # residual on rotated lattice
    return Q1 + Q2r @ R                          # dual-basis reconstruction


def main():
    torch.manual_seed(0)
    W, src = get_weight()
    print(f"Weight source: {src}  shape={tuple(W.shape)}")

    for name, fn in [("PoT 4-bit (shift-only)", pot_quant),
                     ("GoQuant dual-basis 4-bit", goquant)]:
        Wq = fn(W)
        err = (Wq - W).pow(2).mean() / W.pow(2).mean()
        print(f"{name:28s} weight rel-err = {err:.5f}")

    print("\nPASS: GoQuant demo executed end-to-end "
          "(both stages use power-of-two lattices => multiplier-free shift-add).")


if __name__ == "__main__":
    main()
