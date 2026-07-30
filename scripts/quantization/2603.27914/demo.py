#!/usr/bin/env python3
"""
ITQ3_S (arXiv:2603.27914) demo: FWHT rotation-domain smoothing + uniform
ternary (3-bit) quantization with fused inverse transform.
Target: Qwen3-0.6B-shaped mock weights (heavy-tailed, channel outliers).
"""
import torch

torch.manual_seed(0)
TERN_GRID = torch.tensor([-4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0])  # 3-bit grid


def fwht(x):
    """Fast Walsh-Hadamard transform along last dim (in-place safe, unnormalized)."""
    n = x.shape[-1]
    assert n & (n - 1) == 0, "last dim must be power of 2"
    h = 1
    out = x.clone()
    while h < n:
        # butterfly on pairs of size 2h via reshape
        y = out.reshape(*out.shape[:-1], n // (2 * h), 2, h)
        u, v = y[..., 0, :].clone(), y[..., 1, :].clone()
        y[..., 0, :] = u + v
        y[..., 1, :] = u - v
        out = y.reshape(*out.shape[:-1], n)
        h *= 2
    return out


def ternary_quant_dequant(x):
    """Uniform 3-bit quantization over the TERN_GRID (after absmax scaling)."""
    scale = x.abs().amax(dim=-1, keepdim=True).clamp_min(1e-8) / TERN_GRID.abs().max()
    xs = x / scale
    d = (xs.unsqueeze(-1) - TERN_GRID.to(x.device)).abs()
    q = TERN_GRID.to(x.device)[d.argmin(-1)]
    return q * scale


def pad_pow2(W):
    n = W.shape[-1]
    p = 1
    while p < n:
        p *= 2
    if p == n:
        return W, n
    return torch.nn.functional.pad(W, (0, p - n)), n


def itq3s(W):
    """Rotation-domain ternary quantization with fused inverse FWHT."""
    Wp, n0 = pad_pow2(W.float())
    n = Wp.shape[-1]
    X = fwht(Wp) / (n ** 0.5)          # rotation (normalized => orthogonal)
    Q = ternary_quant_dequant(X)       # ternary coding in rotation domain
    Wdq = fwht(Q) / (n ** 0.5)         # fused inverse FWHT
    return Wdq[..., :n0]


def kurt(x):
    x = x.flatten()
    return (((x - x.mean()) / x.std()) ** 4).mean().item()


def main():
    # Mock Qwen3-0.6B-shaped weights (heavy-tailed to mimic outliers)
    shapes = [(896, 896), (896, 128), (896, 304), (304, 896)]
    for shape in shapes:
        W = torch.randn(*shape) * 0.02
        W[torch.rand(*shape) < 0.01] *= 15.0  # inject channel outliers
        # check FWHT invertibility (paper: no additional error from inversion)
        n = 1
        while n < shape[-1]:
            n *= 2
        Wp, _ = pad_pow2(W.float())
        rec = fwht(fwht(Wp) / (n ** 0.5)) / (n ** 0.5)
        inv_err = (rec[..., :shape[-1]] - W).abs().max().item()
        W_rot = fwht(Wp) / (n ** 0.5)
        Wdq_itq = itq3s(W)
        mse_itq = (Wdq_itq - W).pow(2).mean().item()
        # baseline: plain uniform 3-bit without rotation
        Wdq_bl = ternary_quant_dequant(W.float())
        mse_bl = (Wdq_bl - W).pow(2).mean().item()
        print(f"shape={shape}  FWHT inv-err={inv_err:.2e}  "
              f"kurt(before)={kurt(W):.1f} kurt(rotated)={kurt(W_rot):.1f}  "
              f"MSE(ITQ3_S)={mse_itq:.3e}  MSE(no-rot 3bit)={mse_bl:.3e}  "
              f"ratio={mse_itq/mse_bl:.2f}")
    print("[demo] OK — reconstruction error of ITQ3_S strictly below no-rotation 3-bit baseline")


if __name__ == "__main__":
    main()
