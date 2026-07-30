#!/usr/bin/env python3
"""
TurboAngle (arXiv:2603.27467) demo: uniform angle quantization in the FWHT
domain + per-layer early-boost for KV cache compression.
Mock Qwen3-0.6B KV cache (GQA, 2 KV heads, head_dim=128).
"""
import math
import torch

torch.manual_seed(0)


def fwht(x):
    n = x.shape[-1]
    out = x.clone()
    h = 1
    while h < n:
        y = out.reshape(*out.shape[:-1], n // (2 * h), 2, h)
        u, v = y[..., 0, :].clone(), y[..., 1, :].clone()
        y[..., 0, :] = u + v
        y[..., 1, :] = u - v
        out = y.reshape(*out.shape[:-1], n)
        h *= 2
    return out


def angle_quant_dequant(K, angle_bits, seed=0):
    """Rotate pairs to near-uniform circle, quantize angle uniformly."""
    n = K.shape[-1]
    assert n % 2 == 0
    g = torch.Generator().manual_seed(seed)
    D = torch.sign(torch.randn(n, generator=g))          # random diagonal rotation
    Kr = fwht(K.float() * D) / math.sqrt(n)              # FWHT domain
    a, b = Kr[..., 0::2], Kr[..., 1::2]
    r = torch.sqrt(a ** 2 + b ** 2).clamp_min(1e-12)
    theta = torch.atan2(b, a)                            # angle in [-pi, pi]
    L = 2 ** angle_bits
    step = 2 * math.pi / L
    tq = (theta / step).round().clamp(-L // 2, L // 2 - 1) * step
    ra, rb = r * torch.cos(tq), r * torch.sin(tq)
    Q = torch.stack([ra, rb], dim=-1).reshape(*K.shape)
    Kdq = fwht(Q) / math.sqrt(n) * D                     # fused inverse + unrotate
    return Kdq


def norm_quant(K, bits, log_space=False):
    """Asymmetric norm quantization (paper: K 8-bit, V 4-bit log-space)."""
    if log_space:
        s = torch.sign(K)
        v = torch.log1p(K.abs())
        qmax = 2 ** bits - 1
        vq = (v / v.max().clamp_min(1e-8) * qmax).round() / qmax * v.max()
        return s * torch.expm1(vq)
    qmax = 2 ** (bits - 1) - 1
    s = K.abs().max().clamp_min(1e-8) / qmax
    return torch.clamp((K / s).round(), -qmax, qmax) * s


def main():
    T, H, D = 512, 2, 128  # seq, kv heads, head dim (Qwen3-0.6B-like)
    K = torch.randn(T, H, D) * 0.5
    V = torch.randn(T, H, D) * 0.5

    # 1) angle uniformity after rotation
    g = torch.Generator().manual_seed(0)
    Dr = torch.sign(torch.randn(D, generator=g))
    Kr = fwht(K.float() * Dr) / math.sqrt(D)
    th = torch.atan2(Kr[..., 1::2], Kr[..., 0::2])
    hist = torch.histc(th, bins=12, min=-math.pi, max=math.pi)
    print(f"[angle] histogram (12 bins, ~uniform expected): {[int(x) for x in hist]}")

    # 2) uniform bit allocation vs per-layer early-boost
    n_layers = 4
    layer_sens = [3.0, 1.0, 0.8, 2.5]  # mock: layer 0 & 3 are critical (K-dominated)
    budget = 3.4 * n_layers            # ~3.4 angle bits/elem on average (paper: 3.28-3.67)
    uni = [3, 3, 4, 3]                 # uniform-ish
    boost = [4, 3, 3, 4]               # early-boost: +1 bit to critical layers 0 & 3
    mse_uni = mse_boost = 0.0
    for i, bits in enumerate(uni):
        Kdq = angle_quant_dequant(K, bits, seed=i)
        mse_uni += (Kdq - K).pow(2).mean().item() * layer_sens[i]
    for i, bits in enumerate(boost):
        Kdq = angle_quant_dequant(K, bits, seed=i)
        mse_boost += (Kdq - K).pow(2).mean().item() * layer_sens[i]
    print(f"[early-boost] bits(uni)={uni} bits(boost)={boost} avg={budget/n_layers:.2f}")
    print(f"  sens-weighted MSE uni={mse_uni:.4f} boost={mse_boost:.4f} "
          f"improvement={100*(1-mse_boost/mse_uni):.1f}%")

    # 3) asymmetric norm quantization path (K 8-bit, V 4-bit log)
    Kq = norm_quant(K, 8)
    Vq = norm_quant(V, 4, log_space=True)
    snr_k = 10 * math.log10(K.pow(2).mean().item() / (Kq - K).pow(2).mean().item())
    snr_v = 10 * math.log10(V.pow(2).mean().item() / (Vq - V).pow(2).mean().item())
    print(f"[norm-quant] K 8-bit SNR={snr_k:.1f}dB  V 4-bit log SNR={snr_v:.1f}dB")
    print("[demo] OK")


if __name__ == "__main__":
    main()
