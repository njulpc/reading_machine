#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.11222 - ADMM-Q: An Improved Hessian-based Weight Quantizer for
       Post-Training Quantization of Large Language Models
Core Method: combinatorial ADMM for the layer-wise quantization problem:
             minimize ||W X^T - Z X^T||^2 w.r.t. continuous W (preconditioned
             least squares) while Z is projected onto the quantization grid
             each iteration; penalty scheduling gradually enforces the
             discrete constraint, with convergence guarantees.
================================================================================
Demo on Qwen3-0.6B (3-bit, group=128):
  1. Baseline RTN
  2. ADMM-Q: with H = X^T X (Hessian proxy), iterate
       W <- Z - rho * U (H + rho I)^{-1}     (continuous update, closed form)
       Z <- quantize(W + U)                  (discrete projection)
       U <- U + W - Z                        (dual update)
       rho <- rho * 1.6                      (penalty scheduling)
  3. Report layer output reconstruction error ||(Wq-W)X^T||^2 / ||WX^T||^2

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
        return W[:256, :512], "real Qwen3-0.6B tensor"
    g = torch.Generator().manual_seed(0)
    return torch.randn(256, 512, generator=g) * 0.02, "mock weight"


def grid(W, bits, group):
    q = 2 ** (bits - 1) - 1
    scales = []
    for i in range(0, W.shape[1], group):
        G = W[:, i:i + group]
        scales.append(G.abs().amax(dim=1, keepdim=True) / q)
    s = torch.cat(scales, dim=1).repeat_interleave(group, dim=1)[:, :W.shape[1]]
    return s, q


def project(W, s, q):
    return (W / s).round().clamp(-q, q) * s


def rtn(W, bits=3, group=128):
    s, q = grid(W, bits, group)
    return project(W, s, q)


def admm_q(W, X, bits=3, group=128, iters=15, rho0=0.5):
    """Consensus ADMM:  min_W,Z ||WX^T - W_fp X^T||^2  s.t. Z on the grid.
    W-update (closed form):  W = (W_fp H + rho(Z - U)) (H + rho I)^{-1}
    Z-update: grid projection;  U-update: dual ascent;  rho: scheduled."""
    s, q = grid(W, bits, group)
    H = X.T @ X                                   # Hessian proxy [in, in]
    WH = W @ H                                    # data term anchor
    Z, U = rtn(W, bits, group), torch.zeros_like(W)
    rho = rho0
    for _ in range(iters):
        Ainv = torch.linalg.inv(H + rho * torch.eye(H.shape[0]))
        Wc = (WH + rho * (Z - U)) @ Ainv          # continuous update
        Z = project(Wc + U, s, q)                 # discrete projection
        U = U + Wc - Z                            # dual update
        rho *= 1.6                                # penalty scheduling
    return Z


def main():
    torch.manual_seed(0)
    W, src = get_weight()
    print(f"Weight source: {src}  shape={tuple(W.shape)}")
    X = torch.randn(512, W.shape[1])

    def out_err(Wq):
        return ((Wq - W) @ X.T).pow(2).mean() / (W @ X.T).pow(2).mean()

    print(f"RTN    3-bit output rel-err = {out_err(rtn(W)):.5f}")
    print(f"ADMM-Q 3-bit output rel-err = {out_err(admm_q(W, X)):.5f}")
    print("\nPASS: ADMM-Q demo executed end-to-end.")


if __name__ == "__main__":
    main()
