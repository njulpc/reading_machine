#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.04738 - OSAQ: Outlier Self-Absorption for Accurate Low-bit LLM
       Quantization
Core Method: additive weight suppression guided by the Hessian null space.
             The Hessian shows low-rank consistency across inputs; directions
             with vanishing curvature form a stable null space. Additive
             transformations built from null-space vectors suppress weight
             outliers without affecting the task loss, and can be absorbed
             into the weights offline with zero inference overhead.
================================================================================
Demo pipeline on Qwen3-0.6B:
  1. Estimate layer Hessian H = X^T X from calibration activations X
  2. Compute the null space (bottom eigenvectors of H)
  3. For each weight row, fit a ridge-regularized combination of null-space
     vectors that cancels the row's outlier entries; accept the update only
     if it reduces the row's RTN quantization error (safe greedy absorption)
  4. Compare W4 RTN weight quantization error before/after suppression

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
        return W[:512, :1024], "real Qwen3-0.6B tensor"
    g = torch.Generator().manual_seed(0)
    W = torch.randn(512, 1024, generator=g) * 0.02
    W[torch.rand(512, 1024, generator=g) < 0.005] *= 8
    return W, "mock weight"


def rtn(W, bits=4, group=128):
    q = 2 ** (bits - 1) - 1
    Wq = torch.zeros_like(W)
    for i in range(0, W.shape[1], group):
        G = W[:, i:i + group]
        s = G.abs().amax(dim=1, keepdim=True) / q
        Wq[:, i:i + group] = (G / s).round().clamp(-q, q) * s
    return Wq


def rel_err(Wq, W):
    return (Wq - W).pow(2).mean() / W.pow(2).mean()


def osaq_suppress(W, X, null_dim=None, ridge=1e-3):
    """Outlier self-absorption along the Hessian null space (safe version)."""
    H = X.T @ X
    evals, evecs = torch.linalg.eigh(H)
    if null_dim is None:
        null_dim = int((evals < evals.max() * 1e-6).sum())  # true null-space dim
        null_dim = max(null_dim, 8)
    N = evecs[:, :null_dim]                        # vanishing-curvature basis
    print(f"null-space dim = {null_dim}")
    Ws = W.clone()
    accepted = 0
    for r in range(W.shape[0]):
        w = W[r]
        mask = w.abs() > w.abs().median() * 4.0    # outlier entries
        if int(mask.sum()) < 2:
            continue
        No = N[mask]                               # [n_out, null_dim]
        A = No.T @ No + ridge * torch.eye(null_dim)
        c = torch.linalg.solve(A, No.T @ w[mask])  # ridge least squares
        w_new = w - N @ c                          # dW in null space => dW@X ~ 0
        # accept only if the row's OUTPUT-domain RTN error improves
        e_old = ((rtn(w.unsqueeze(0)) - w.unsqueeze(0)) @ X.T).pow(2).mean()
        e_new = ((rtn(w_new.unsqueeze(0)) - w.unsqueeze(0)) @ X.T).pow(2).mean()
        if e_new < e_old:
            Ws[r] = w_new
            accepted += 1
    return Ws, accepted


def main():
    torch.manual_seed(0)
    W, src = get_weight()
    print(f"Weight source: {src}  shape={tuple(W.shape)}")
    # calibration activations with realistic low-rank covariance (rank d/2),
    # so the Hessian has a genuine null space (paper's key observation)
    d = W.shape[1]
    B = torch.randn(d, d // 2) / (d ** 0.5)
    X = torch.randn(512, d // 2) @ B.T * 2.0

    Ws, acc = osaq_suppress(W, X)
    delta_task = ((Ws - W) @ X.T).abs().max()
    print(f"rows accepted: {acc}/{W.shape[0]}")
    print(f"max |(dW) x| over calibration set = {delta_task:.2e}  (should be ~0)")

    # (a) self quantization error |Q(Wt)-Wt| (outlier suppression should help)
    print(f"W4 RTN self-quant err  original   = {rel_err(rtn(W), W):.5f}")
    print(f"W4 RTN self-quant err  suppressed = {rel_err(rtn(Ws), Ws):.5f}")
    # (b) task-output error |(Q(Wt)-W)X| / |WX| (what the task loss sees)
    def out_err(Wq):
        return ((Wq - W) @ X.T).pow(2).mean() / (W @ X.T).pow(2).mean()
    print(f"W4 RTN output err vs FP  original   = {out_err(rtn(W)).item():.5f}")
    print(f"W4 RTN output err vs FP  suppressed = {out_err(rtn(Ws)).item():.5f}")
    print("\nPASS: OSAQ demo executed end-to-end.")


if __name__ == "__main__":
    main()
