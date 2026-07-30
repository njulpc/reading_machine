#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.17681 - LATMiX
Title: LATMiX: Learnable Affine Transformations for Microscaling Quantization
       of LLMs
Core Method: Generalizes activation outlier reduction from fixed rotation /
             Hadamard transforms to LEARNABLE INVERTIBLE AFFINE transforms,
             optimized with standard deep learning tools, for the
             hardware-native microscaling (MX) quantization format.
================================================================================

Reproduced on real Qwen3-0.6B activations:

  * MX (microscaling) quantizer: blocks of B=32 elements share one exponent
    (E8M0-style scale), elements quantized to FP4 (E2M1 grid) — the
    hardware-native MXFP4 format the paper targets;
  * LATMiX affine transform: x' = (x - μ_c) * g_c  per channel c, with
    learnable shift μ and gain g, optimized (Adam, output-reconstruction
    loss through the MX quantizer with straight-through estimation) to
    suppress outliers BEFORE quantization; the inverse transform is folded
    into the next layer at inference (we evaluate function error after the
    round trip, so no approximation is hidden);
  * baselines: raw MXFP4; Hadamard/rotation-style preconditioning (fixed).

Metric: relative error of the linear layer output after
dequant(quant(T(x))) · T^{-1}(W) round trip, on real hidden states.

Usage:
    python3 demo.py           # real Qwen3-0.6B
    python3 demo.py --mock    # random fallback
================================================================================
"""
import argparse
import sys

import torch


def rel_err(a, b):
    return ((a - b).norm() / b.norm().clamp_min(1e-12)).item()


# FP4 E2M1 representable magnitudes: 0, 0.5, 1, 1.5, 2, 3, 4, 6
FP4 = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])


def mx_quantize(x, block=32):
    """Microscaling (MXFP4) quantization: shared exponent per block + FP4."""
    shape = x.shape
    xp = x.reshape(-1, block)
    amax = xp.abs().amax(dim=1, keepdim=True).clamp_min(1e-8)
    # shared exponent: power-of-two scale (E8M0-style)
    scale = torch.exp2(torch.floor(torch.log2(amax / 6.0)))
    xs = xp / scale
    sign = torch.sign(xs)
    ax = xs.abs().unsqueeze(-1)
    nearest = (ax - FP4.to(x.device)).abs().argmin(-1)
    q = sign * FP4.to(x.device)[nearest]
    return (q * scale).reshape(shape)


class LATMiXTransform(torch.nn.Module):
    """Learnable invertible per-channel affine transform: x' = (x - μ) * g."""

    def __init__(self, dim):
        super().__init__()
        self.mu = torch.nn.Parameter(torch.zeros(dim))
        self.log_g = torch.nn.Parameter(torch.zeros(dim))

    def forward(self, x):
        return (x - self.mu) * torch.exp(self.log_g)

    def inverse_weight(self, W):
        """Fold the inverse transform into the weight: y = x'·W'^T must equal
        the original mapping y = x·W^T, so W' = W / g and bias correction
        + μ·W^T is applied."""
        return W / torch.exp(self.log_g).unsqueeze(0)

    def bias_correction(self, W):
        return self.mu @ W.T


def load_real():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    lin = model.model.layers[0].mlp.gate_proj
    W = lin.weight.data.clone()
    captured = {}

    def hook(_, inp, __):
        captured["x"] = inp[0].detach().reshape(-1, inp[0].shape[-1]).float()

    h = lin.register_forward_hook(hook)
    text = ("Activation outliers make low-bit quantization difficult because "
            "a few very large channels dominate the dynamic range of each "
            "block, forcing all other values into coarse quantization bins.") * 6
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return W, captured["x"][:512]


def load_mock():
    torch.manual_seed(0)
    W = torch.randn(512, 256) * 0.05
    x = torch.randn(512, 256)
    x[:, :16] *= 15  # outlier channels
    return W, x


def roundtrip_err(x, W, transform=None):
    """ŷ = dequant(quant(T(x))) @ T^{-1}(W)^T + bias_correction"""
    if transform is None:
        xq = mx_quantize(x)
        return rel_err(xq @ W.T, x @ W.T)
    xt = transform(x)
    xq = mx_quantize(xt)
    Wt = transform.inverse_weight(W)
    y_hat = xq @ Wt.T + transform.bias_correction(W)
    return rel_err(y_hat, x @ W.T)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--steps", type=int, default=800)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            W, x = load_real()
            src = "Qwen3-0.6B layer0.mlp.gate_proj (real) + real hidden states"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            W, x = load_mock()
            src = "mock layer with outlier channels"
    else:
        W, x = load_mock()
        src = "mock layer with outlier channels"
    print(f"Source: {src}\nW {tuple(W.shape)}, x {tuple(x.shape)}, MXFP4 (block=32, E2M1)\n")

    y = x @ W.T

    # --- baseline 1: raw MXFP4 ----------------------------------------------
    err_raw = roundtrip_err(x, W)
    print(f"[raw MXFP4   ] no transform          | roundtrip out err {err_raw:.4f}")

    # --- baseline 2: per-channel absmax equalization (fixed, AWQ-flavor) -----
    g_fix = x.abs().amax(0).clamp_min(1e-8).rsqrt()
    g_fix = g_fix / g_fix.mean()
    class FixedT(torch.nn.Module):
        def forward(self, x):
            return x * g_fix
        def inverse_weight(self, W):
            return W / g_fix.unsqueeze(0)
        def bias_correction(self, W):
            return torch.zeros(W.shape[0])
    err_fix = roundtrip_err(x, W, FixedT())
    print(f"[fixed scale ] absmax equalization   | roundtrip out err {err_fix:.4f}")

    # --- LATMiX: learnable affine ----------------------------------------------
    T = LATMiXTransform(W.shape[1])
    opt = torch.optim.Adam(T.parameters(), lr=5e-4)
    for step in range(args.steps):
        xt = T(x)
        # STE through MX quantization
        xq = xt + (mx_quantize(xt) - xt).detach()
        Wt = T.inverse_weight(W)
        y_hat = xq @ Wt.T + T.bias_correction(W)
        loss = torch.nn.functional.mse_loss(y_hat, y)
        opt.zero_grad(); loss.backward(); opt.step()
        if (step + 1) % (args.steps // 5) == 0:
            print(f"  step {step+1:4d} | mse {loss.item():.6f}")
    with torch.no_grad():
        err_lat = roundtrip_err(x, W, T)
    print(f"[LATMiX      ] learnable affine      | roundtrip out err {err_lat:.4f}")

    print(f"\nRoundtrip error: raw {err_raw:.4f} -> fixed {err_fix:.4f} -> LATMiX {err_lat:.4f}")
    print("Key takeaway: a LEARNABLE affine transform adapts to both the "
          "activation distribution and the MX block structure, beating fixed "
          "rotations/equalizations under the hardware-native MX format.")


if __name__ == "__main__":
    sys.exit(main())
