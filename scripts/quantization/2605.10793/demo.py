#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.10793 - ConQuR: Corner Aligned Activation Quantization via
       Optimized Rotations for LLMs
Core Method: learn orthogonal rotations that align normalized activations
             with the corners of an inscribed hypercube, spreading activation
             energy evenly; closed-form update via the orthogonal Procrustes
             problem; online calibration without storing activations.
================================================================================
Demo:
  1. Generate activation samples with LLM-style outliers (or derive them from
     real Qwen3-0.6B embedding rows when weights are available)
  2. Iteratively fit rotation R: project normalized x to nearest hypercube
     corner y, solve Procrustes R = U V^T from SVD(X^T Y)
  3. Quantize rotated activations to 4 bits; compare vs no-rotation and vs
     fixed Hadamard rotation

Validation: real Qwen3-0.6B embedding-derived activations when available;
mock heavy-tailed activations otherwise.
"""
import os, math
from pathlib import Path
import torch

QWEN_PATH = os.environ.get(
    "QWEN3_WEIGHTS",
    str(Path(__file__).resolve().parents[3] / "_work" / "qwen3-0.6b.safetensors"))


def get_activations(n=1024, d=1024):
    if os.path.exists(QWEN_PATH):
        from safetensors import safe_open
        with safe_open(QWEN_PATH, framework="pt") as f:
            E = f.get_tensor("model.embed_tokens.weight").float()
        idx = torch.randperm(E.shape[0])[:n]
        X = E[idx] * 8.0  # embedding-derived activations
        return X[:, :d], "real Qwen3-0.6B embedding-derived activations"
    g = torch.Generator().manual_seed(0)
    X = torch.randn(n, d, generator=g)
    X[torch.rand(n, d, generator=g) < 0.005] *= 12.0
    return X, "mock heavy-tailed activations"


def hadamard(n):
    m = 1 << (n - 1).bit_length()
    H = torch.ones(1, 1)
    while H.shape[0] < m:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return (H / math.sqrt(m))[:n, :n]


def fit_conqur(X, iters=10, batch=256):
    """Online Procrustes corner alignment (no stored corpus needed)."""
    d = X.shape[1]
    R = torch.eye(d)
    for it in range(iters):
        M = torch.zeros(d, d)
        for i in range(0, X.shape[0], batch):          # online batches
            Xb = X[i:i + batch] @ R.T
            xn = Xb / Xb.norm(dim=1, keepdim=True).clamp_min(1e-8)
            Y = torch.sign(xn) / math.sqrt(d)          # inscribed-cube corners
            M += Xb.T @ Y
        U, _, Vh = torch.linalg.svd(M)
        R = U @ Vh                                      # Procrustes update
    return R


def act_quant_static(X, scale, bits=4):
    """Static per-channel scales from calibration (deployment setting, where
    rotation choice matters most)."""
    q = 2 ** (bits - 1) - 1
    return (X / scale).round().clamp(-q, q) * scale


def rel_err(A, B):
    return ((A - B).pow(2).mean() / B.pow(2).mean()).item()


def run_case(X, tag):
    Rh = hadamard(X.shape[1])
    Rc = fit_conqur(X)
    X_cal, X_ev = X[: X.shape[0] // 2], X[X.shape[0] // 2:]
    for name, R in [("no rotation", torch.eye(X.shape[1])),
                    ("Hadamard", Rh), ("ConQuR", Rc)]:
        scale = (X_cal @ R.T).abs().amax(dim=0, keepdim=True) / 7.0
        Xq = act_quant_static(X_ev @ R.T, scale) @ R
        print(f"  {name:12s} act-4bit rel-err (static scales) = {rel_err(Xq, X_ev):.5f}")


def main():
    torch.manual_seed(0)
    X, src = get_activations()
    print(f"Activation source: {src}  shape={tuple(X.shape)}")
    print("[real/embedding-derived]")
    run_case(X, "real")

    # LLM-style massive outlier channels (the failure mode rotations target)
    g = torch.Generator().manual_seed(1)
    Z = torch.randn(1024, 1024, generator=g)
    D = torch.ones(1024)
    D[torch.randperm(1024)[:8]] = 25.0                  # 8 outlier channels
    Xo = Z * D
    print("[synthetic outlier-channel activations]")
    run_case(Xo, "synthetic")

    print("\nPASS: ConQuR demo executed end-to-end.")


if __name__ == "__main__":
    main()
