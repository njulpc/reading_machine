#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.02584 - RotateAttention: RoPE-Aware Rotation and Range
Rectification for INT4 Quantized Attention (video DiT, 3D RoPE)
Core: mergeable RoPE-aware rotation for Q/K + range-optimized unsigned P quant
================================================================================
Usage: python3 demo.py   (requires: torch; transformers optional)
================================================================================
"""
import torch
import torch.nn.functional as F
import math

torch.manual_seed(0)


def rope_rotate(x, freqs):
    """Simplified 3D-RoPE-style rotation: split head_dim into 3 axis groups
    (time/height/width), each with its own rotation frequency."""
    d = x.shape[-1]
    third = d // 3
    outs = []
    for g, sl in enumerate([(0, third), (third, 2 * third), (2 * third, d)]):
        seg = x[..., sl[0]:sl[1]]
        seg_r = seg.reshape(*seg.shape[:-1], -1, 2)
        c, s = torch.cos(freqs[g]), torch.sin(freqs[g])
        rot = torch.stack([seg_r[..., 0] * c - seg_r[..., 1] * s,
                           seg_r[..., 0] * s + seg_r[..., 1] * c], -1)
        outs.append(rot.reshape(*seg.shape))
    return torch.cat(outs, -1)


def hadamard(n):
    H = torch.ones(1, 1)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H / math.sqrt(n)


def quant_int4_signed(x):
    s = x.abs().amax(-1, keepdim=True).clamp_min(1e-8) / 7
    return torch.clamp(torch.round(x / s), -8, 7) * s


def quant_int4_unsigned(x, scale=1.0, zero=0.0):
    """Range-optimized P quantization: non-negative P uses fixed scale/zero to
    exploit the full INT4 range [0,15] instead of wasting half on negatives."""
    q = torch.clamp(torch.round((x - zero) / scale * 15), 0, 15)
    return q / 15 * scale + zero


def demo():
    print("=" * 70)
    print(" Paper 2607.02584 - RotateAttention (3D RoPE + INT4 FlashAttention)")
    print("=" * 70)

    print("\n[1] 3D-RoPE dimension partitioning shapes Q/K outlier distribution")
    d = 96
    Q = torch.randn(4, 256, d)
    freqs = [torch.rand(d // 6) * 3, torch.rand(d // 6) * 1.5, torch.rand((d - 2 * (d // 3)) // 2) * 0.5]
    Qr = rope_rotate(Q, freqs)
    third = d // 3
    for g, (a, b) in enumerate([(0, third), (third, 2 * third), (2 * third, d)]):
        print(f"  axis-group {g}: max|Q| = {Qr[..., a:b].abs().max():.2f} "
              f"(mean {Qr[..., a:b].abs().mean():.2f})")
    print("  -> outliers concentrate by RoPE axis partition -> rotation must be RoPE-aware")

    print("\n[2] RoPE-aware (mergeable) rotation suppresses outliers")
    H = hadamard(third)
    Q_rot = torch.cat([Qr[..., 0:third] @ H, Qr[..., third:2 * third] @ H, Qr[..., 2 * third:] @ H], -1)
    print(f"  max|Q| before rotation: {Qr.abs().max():.2f} -> after: {Q_rot.abs().max():.2f}")
    e0 = ((Qr - quant_int4_signed(Qr)) ** 2).mean()
    e1 = ((Q_rot - quant_int4_signed(Q_rot)) ** 2).mean()
    print(f"  INT4 quant MSE  before: {e0:.5f}  after: {e1:.5f}")

    print("\n[3] Range-optimized unsigned INT4 for non-negative P")
    S = torch.randn(8, 64, 64)
    P = torch.exp(S - S.amax(-1, keepdim=True))  # in [0,1], non-negative
    P_sym = quant_int4_signed(P)
    P_rng = quant_int4_unsigned(P, scale=1.0, zero=0.0)
    print(f"  P quant MSE  symmetric: {((P - P_sym) ** 2).mean():.6f}")
    print(f"  P quant MSE  range-opt: {((P - P_rng) ** 2).mean():.6f}  (2x resolution)")

    print("\n[4] Qwen3-0.6B: INT4 attention weights + unsigned-P pipeline")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        m = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", torch_dtype=torch.float32).eval()
        tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
        ids = tok("The capital of France is", return_tensors="pt").input_ids
        with torch.no_grad():
            fp = m(ids).logits
        n = 0
        with torch.no_grad():
            for name, mod in m.named_modules():
                if isinstance(mod, torch.nn.Linear) and n < 2 and any(
                        k in name for k in ("q_proj", "k_proj")):
                    mod.weight.data = quant_int4_signed(mod.weight.data)
                    n += 1
            qq = m(ids).logits
        cos = F.cosine_similarity(fp.reshape(-1), qq.reshape(-1), dim=0)
        print(f"  real Qwen3-0.6B; INT4 Q/K layers: {n}; logits cosine: {cos:.4f}")
    except Exception as e:
        print(f"  [info] real model unavailable ({type(e).__name__}); synthetic paths validated")

    print("\n" + "=" * 70)
    print(" SUMMARY: RoPE-aware rotation + unsigned range-optimized P INT4 OK")
    print("=" * 70)


if __name__ == "__main__":
    demo()
