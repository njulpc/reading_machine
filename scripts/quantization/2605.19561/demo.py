#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.19561 - TORQ: Two-Level Orthogonal Rotation for MXFP4
       Quantization
Core Method: MXFP4 activation quantization suffers from (1) inter-block
             variance imbalance and (2) intra-block codebook-utilization
             imbalance. TORQ applies (a) inter-block orthogonal rotation to
             redistribute activation energy across blocks (macro level) and
             (b) maximum-entropy-guided intra-block rotation to avoid
             codebook collapse (micro level). Training-free PTQ.
================================================================================
Demo:
  1. Faithful MXFP4 (E2M1, block=32, shared E8M0 exponent) quantizer
  2. Baseline: direct MXFP4 on heavy-tailed activations
  3. TORQ: block-level Hadamard mixing (intra-block) + cross-block energy
     equalization via a full-basis orthogonal transform (macro level),
     then MXFP4
  4. Report relative quantization error

Validation: uses real Qwen3-0.6B embedding-derived activations when
available; mock heavy-tailed activations otherwise.
"""
import os, math
from pathlib import Path
import torch

QWEN_PATH = os.environ.get(
    "QWEN3_WEIGHTS",
    str(Path(__file__).resolve().parents[3] / "_work" / "qwen3-0.6b.safetensors"))

E2M1 = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])


def mxfp4_quant(X, block=32):
    n, d = X.shape
    dpad = (d + block - 1) // block * block
    Xp = torch.nn.functional.pad(X, (0, dpad - d))
    Xb = Xp.reshape(n, -1, block)
    amax = Xb.abs().amax(dim=-1, keepdim=True)
    e = torch.floor(torch.log2(amax.clamp_min(1e-12) / 6.0))
    scale = torch.pow(2.0, e)                       # E8M0 power-of-two scale
    Xn = Xb / scale
    grids = torch.cat([-E2M1.flip(0), E2M1]).to(X.device)
    idx = (Xn.unsqueeze(-1) - grids.view(1, 1, 1, -1)).abs().argmin(-1)
    Xq = grids[idx] * scale
    return Xq.reshape(n, dpad)[:, :d]


def hadamard(n):
    m = 1 << (n - 1).bit_length()
    H = torch.ones(1, 1)
    while H.shape[0] < m:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return (H / math.sqrt(m))[:n, :n]


def get_activations(n=512, d=1024):
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


def torq_rotate(X, block=32):
    """Macro: full-basis orthogonal mixing equalizes inter-block energy.
       Micro: per-block Hadamard spreads intra-block energy (anti-collapse)."""
    R = hadamard(X.shape[1])          # macro inter-block energy redistribution
    Xr = X @ R.T
    Hb = hadamard(block)              # micro intra-block rotation
    n, d = Xr.shape
    Xb = Xr.reshape(n, d // block, block)
    return (Xb @ Hb.T).reshape(n, d), R, Hb


def torq_unrotate(Xr, R, Hb, block=32):
    n, d = Xr.shape
    X = (Xr.reshape(n, d // block, block) @ Hb).reshape(n, d)
    return X @ R


def run_case(X, tag):
    e0 = ((mxfp4_quant(X) - X).pow(2).mean() / X.pow(2).mean()).item()
    Xr, R, Hb = torq_rotate(X)
    e1 = ((torq_unrotate(mxfp4_quant(Xr), R, Hb) - X).pow(2).mean()
          / X.pow(2).mean()).item()
    print(f"[{tag}] direct MXFP4 rel-err = {e0:.5f}   TORQ rel-err = {e1:.5f}")


def main():
    torch.manual_seed(0)
    X, src = get_activations()
    print(f"Activation source: {src}  shape={tuple(X.shape)}")
    run_case(X, "real/mixed activations")

    # synthetic block-imbalanced case (the failure mode TORQ targets):
    g = torch.Generator().manual_seed(1)
    Xs = torch.randn(512, 1024, generator=g)
    scales = torch.rand(32, generator=g) * 5 + 0.2      # per-block variance
    Xs = Xs * scales.repeat_interleave(32)
    run_case(Xs, "block-imbalanced synthetic")

    print("\nPASS: TORQ demo executed end-to-end.")


if __name__ == "__main__":
    main()
