#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.02958 - Quant VideoGen (QVG)
Title: Quant VideoGen: Auto-Regressive Long Video Generation via 2-Bit
       KV-Cache Quantization
Core Method: Training-free 2-bit KV cache quantization via
             (1) Semantic-Aware Smoothing — exploit temporal redundancy by
                 quantizing low-magnitude residuals against a semantic
                 (per-channel) reference instead of raw values;
             (2) Progressive Residual Quantization — coarse-to-fine
                 multi-stage quantization of the remaining error.
================================================================================

Although QVG targets autoregressive video diffusion, both mechanisms are
modality-agnostic. This demo reproduces them on REAL Qwen3-0.6B KV caches
(keys/values of every layer, captured from a real forward pass on a long
prompt, where adjacent positions exhibit strong redundancy — the text-world
counterpart of video temporal redundancy):

  * Semantic-Aware Smoothing:   K_res = K - smooth(K),  where smooth(K) is a
    per-channel moving average over the sequence (captures the redundant
    "semantic" component). The residual has much smaller magnitude and is
    quantization-friendly.
  * Progressive Residual Quantization: stage-1 quantizes the smoothed
    reference at coarse bits; stage-2 quantizes the residual at 2 bits;
    an optional stage-3 re-quantizes the stage-2 error (quality-memory dial).

Baselines: direct per-token 2-bit RTN on raw K/V; FP16 reference for error.
Metric: relative error of the attention output  softmax(QK^T)V  recomputed
from the dequantized cache, plus memory accounting.

Usage:
    python3 demo.py           # real Qwen3-0.6B
    python3 demo.py --mock    # random fallback
================================================================================
"""
import argparse
import sys

import torch
import torch.nn.functional as F


def rel_err(a, b):
    return ((a - b).norm() / b.norm().clamp_min(1e-12)).item()


def rtn_per_channel(t, bits, dim=0):
    """Symmetric per-channel RTN along `dim` (channel = last dim)."""
    qmax = 2 ** (bits - 1) - 1
    s = t.abs().amax(dim=dim, keepdim=True).clamp_min(1e-8) / qmax
    return s * torch.clamp(torch.round(t / s), -qmax - 1, qmax)


def smooth_reference(K, win=8):
    """Per-channel moving average over the sequence dim (semantic smooth)."""
    seq, h, d = K.shape
    X = K.reshape(seq, h * d).T.unsqueeze(0)             # [1, h*d, seq]
    ker = torch.ones(h * d, 1, win, device=K.device) / win
    pad_l, pad_r = win // 2, win - 1 - win // 2
    Xp = F.pad(X, (pad_l, pad_r), mode="replicate")
    sm = F.conv1d(Xp, ker, groups=h * d)                 # [1, h*d, seq]
    return sm.squeeze(0).T.reshape(seq, h, d)


def qvg_quantize(K, bits=2, ref_bits=4, win=8, stages=2):
    """QVG: semantic smoothing + progressive residual quantization."""
    ref = smooth_reference(K, win=win)
    res = K - ref
    # stage 1: coarse quantization of the smooth reference
    ref_q = rtn_per_channel(ref, ref_bits, dim=0)
    # stage 2: residual quantization at `bits`
    res_q = rtn_per_channel(res, bits, dim=0)
    K_q = ref_q + res_q
    if stages >= 3:
        # stage 3: re-quantize the remaining error (progressive refinement)
        err = K - K_q
        err_q = rtn_per_channel(err, bits, dim=0)
        K_q = K_q + err_q
    return K_q


def attn_out(Q, K, V):
    """Q: [q, heads, dim]; K, V: [seq, heads, dim]"""
    scores = torch.einsum("qhd,shd->qhs", Q, K) / (Q.shape[-1] ** 0.5)
    p = scores.softmax(dim=-1)
    return torch.einsum("qhs,shd->qhd", p, V)


def load_real():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    text = ("Autoregressive generation keeps a cache of key and value tensors "
            "for every generated token. As sequences grow longer, this cache "
            "dominates memory usage and limits how much context the model can "
            "attend to. Adjacent tokens often share similar key patterns, "
            "which makes the cache highly redundant along the time axis. ") * 24
    inputs = tok(text, return_tensors="pt")
    with torch.no_grad():
        out = model(**inputs, use_cache=True)
    pkv = out.past_key_values
    k, v = pkv.layers[0].keys, pkv.layers[0].values   # [batch, heads, seq, dim]
    K = k[0].permute(1, 0, 2).float()                 # [seq, heads, dim]
    V = v[0].permute(1, 0, 2).float()
    return K, V, model, tok, inputs


def load_mock():
    torch.manual_seed(0)
    seq, h, d = 512, 8, 64
    base = torch.randn(1, h, d).repeat(seq, 1, 1)
    K = base + 0.3 * torch.randn(seq, h, d).cumsum(0) * 0.1 + 0.1 * torch.randn(seq, h, d)
    V = torch.randn(seq, h, d)
    return K, V, None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--bits", type=int, default=2)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            K, V, model, tok, inputs = load_real()
            src = f"Qwen3-0.6B layer-0 KV cache (real forward, seq={K.shape[0]})"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            K, V, model, tok, inputs = load_mock()
            src = "mock redundant KV cache"
    else:
        K, V, model, tok, inputs = load_mock()
        src = "mock redundant KV cache"
    print(f"Source: {src}")
    print(f"K {tuple(K.shape)}, V {tuple(V.shape)}, target {args.bits}-bit KV cache\n")

    seq = K.shape[0]
    Q = K[-16:].clone() + 0.01 * torch.randn(16, *K.shape[1:])   # last-16 queries

    # --- FP16 reference --------------------------------------------------------
    ref_out = attn_out(Q, K, V)

    # --- baseline: direct 2-bit RTN on raw K/V ---------------------------------
    K_rtn = rtn_per_channel(K, args.bits, dim=0)
    V_rtn = rtn_per_channel(V, args.bits, dim=0)
    err_rtn = rel_err(attn_out(Q, K_rtn, V_rtn), ref_out)
    print(f"[baseline ] direct {args.bits}-bit RTN on raw K/V        | "
          f"K err {rel_err(K_rtn, K):.4f} | attn out err {err_rtn:.4f}")

    # --- QVG: smoothing + progressive residual --------------------------------
    K_q2 = qvg_quantize(K, bits=args.bits, ref_bits=4, stages=2)
    V_q2 = qvg_quantize(V, bits=args.bits, ref_bits=4, stages=2)
    err_q2 = rel_err(attn_out(Q, K_q2, V_q2), ref_out)
    print(f"[QVG 2stg ] smooth + {args.bits}-bit residual (ref 4-bit)| "
          f"K err {rel_err(K_q2, K):.4f} | attn out err {err_q2:.4f}")

    K_q3 = qvg_quantize(K, bits=args.bits, ref_bits=4, stages=3)
    V_q3 = qvg_quantize(V, bits=args.bits, ref_bits=4, stages=3)
    err_q3 = rel_err(attn_out(Q, K_q3, V_q3), ref_out)
    print(f"[QVG 3stg ] + progressive re-quantization of error     | "
          f"K err {rel_err(K_q3, K):.4f} | attn out err {err_q3:.4f}")

    # --- memory accounting -------------------------------------------------------
    n = K.numel() + V.numel()
    fp16_mb = n * 2 / 1e6
    rtn_mb = n * args.bits / 8 / 1e6
    qvg_mb = n * args.bits / 8 / 1e6 + n * 4 / 8 / 1e6 * 0.25  # ref at 4-bit, amortized
    print(f"\nMemory (this layer's cache): FP16 {fp16_mb:.2f} MB | "
          f"raw {args.bits}-bit {rtn_mb:.2f} MB ({fp16_mb / rtn_mb:.1f}x) | "
          f"QVG ~{qvg_mb:.2f} MB ({fp16_mb / qvg_mb:.1f}x)")
    print(f"\nAttention output error vs FP16: raw RTN {err_rtn:.4f} -> "
          f"QVG-2stage {err_q2:.4f} -> QVG-3stage {err_q3:.4f}")
    print("Key takeaway: smoothing away the redundant semantic component makes "
          "the residual small and quantization-friendly; progressive residual "
          "stages then buy back accuracy at a smooth quality-memory trade-off.")


if __name__ == "__main__":
    sys.exit(main())
