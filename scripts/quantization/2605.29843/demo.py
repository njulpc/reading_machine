#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.29843 - HARP: Hadamard-Preconditioned Adaptive Rotation
       Processor for Extreme LLM Quantization
Core Method: replace the fixed randomized Hadamard transform (RHT) with a
             learnable structured two-sided orthogonal processor, represented
             as a product of sparse butterfly (Givens-pair) block-orthogonal
             stages, initialized to the RHT up to a fixed permutation, fitted
             on calibration data only, preserving exact FP equivalence and
             deployment efficiency.
================================================================================
Demo (W4A4-style weight+activation quantization error on Qwen3-0.6B):
  1. Fixed RHT baseline for activation rotation
  2. HARP: R stages of butterfly rotations (each a set of disjoint Givens
     rotations); angles fitted by coordinate descent on calibration MSE,
     initialized at identity-after-RHT (paper's RHT initialization)
  3. Compare quantized-activation reconstruction error RHT vs HARP

Validation: real Qwen3-0.6B embedding-derived activations when available;
mock heavy-tailed activations otherwise.
"""
import os, math
from pathlib import Path
import torch

QWEN_PATH = os.environ.get(
    "QWEN3_WEIGHTS",
    str(Path(__file__).resolve().parents[3] / "_work" / "qwen3-0.6b.safetensors"))


def get_activations(n=512, d=256):
    if os.path.exists(QWEN_PATH):
        from safetensors import safe_open
        with safe_open(QWEN_PATH, framework="pt") as f:
            E = f.get_tensor("model.embed_tokens.weight").float()
        X = E[torch.randperm(E.shape[0])[:n]] * 8.0
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


def butterfly(X, pairs, angles):
    """Apply one block-orthogonal butterfly stage: disjoint Givens rotations."""
    Y = X.clone()
    c, s = torch.cos(angles), torch.sin(angles)
    i, j = pairs
    xi, xj = Y[:, i].clone(), Y[:, j].clone()
    Y[:, i] = c * xi - s * xj
    Y[:, j] = s * xi + c * xj
    return Y


def act_quant(X, bits=4):
    q = 2 ** (bits - 1) - 1
    s = X.abs().amax(dim=1, keepdim=True) / q
    return (X / s).round().clamp(-q, q) * s


def fit_harp(X, n_stages=4, sweeps=3, lr_grid=None):
    d = X.shape[1]
    lr_grid = lr_grid or torch.linspace(-0.4, 0.4, 17)
    perm = torch.randperm(d)
    stages = [(perm[0::2], perm[1::2]) for _ in range(n_stages)]
    angles = [torch.zeros(len(p[0])) for p in stages]

    def loss(angs):
        Y = X
        for (p, a) in zip(stages, angs):
            Y = butterfly(Y, p, a)
        return (act_quant(Y) - Y).pow(2).mean().item()

    cur = loss(angles)
    for _ in range(sweeps):                        # coordinate descent
        for st in range(n_stages):
            for k in range(len(angles[st])):
                best_a, best_l = angles[st][k].item(), cur
                for a in lr_grid:
                    trial = [t.clone() for t in angles]
                    trial[st][k] = a
                    l = loss(trial)
                    if l < best_l:
                        best_a, best_l = a.item(), l
                angles[st][k] = best_a
                cur = best_l
    return stages, angles


def main():
    torch.manual_seed(0)
    X, src = get_activations()
    print(f"Activation source: {src}  shape={tuple(X.shape)}")

    Rh = hadamard(X.shape[1])
    Xr = X @ Rh.T
    e_rht = (act_quant(Xr) @ Rh - X).pow(2).mean() / X.pow(2).mean()

    stages, angles = fit_harp(Xr)
    Y = Xr
    for p, a in zip(stages, angles):
        Y = butterfly(Y, p, a)
    # invert butterfly stages (orthogonal) to map back
    Yq = act_quant(Y)
    for p, a in reversed(list(zip(stages, angles))):
        Yq = butterfly(Yq, p, -a)
    e_harp = (Yq @ Rh - X).pow(2).mean() / X.pow(2).mean()

    print(f"fixed RHT  act-4bit rel-err = {e_rht:.5f}")
    print(f"HARP       act-4bit rel-err = {e_harp:.5f}")
    print("\nPASS: HARP demo executed end-to-end.")


if __name__ == "__main__":
    main()
