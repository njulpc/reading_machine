#!/usr/bin/env python3
"""
================================================================================
Paper: 2605.17757 - OSCAR: Offline Spectral Covariance-Aware Rotation for
       2-bit KV Cache Quantization
Core Method: estimate attention-aware covariance structures offline, derive
             fixed rotations and clipping thresholds aligned with the
             covariance that attention actually consumes, then quantize the
             KV cache to INT2. Naive (e.g. Hadamard) rotation collapses at
             INT2; covariance-aligned rotation stays close to BF16.
================================================================================
Demo:
  1. Build a realistic KV cache: K = H @ Wk^T, V = H @ Wv^T using real
     Qwen3-0.6B k_proj/v_proj weights (when available) and heavy-tailed
     hidden states H
  2. Estimate attention-weighted covariance C = sum_i p_i k_i k_i^T offline,
     take its eigenbasis as the OSCAR rotation; per-channel clipping
     thresholds are set in the rotated basis (paper's clip rule)
  3. INT2-quantize K; measure (a) attention-map error with K-only
     quantization and (b) end output error with K and V both at INT2,
     for naive Hadamard vs OSCAR rotations

Validation: real Qwen3-0.6B attention weights when available; mock otherwise.
"""
import os, math
from pathlib import Path
import torch

QWEN_PATH = os.environ.get(
    "QWEN3_WEIGHTS",
    str(Path(__file__).resolve().parents[3] / "_work" / "qwen3-0.6b.safetensors"))


def hadamard(n):
    m = 1 << (n - 1).bit_length()
    H = torch.ones(1, 1)
    while H.shape[0] < m:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return (H / math.sqrt(m))[:n, :n]


def int2_quant_global(X, clip_pct=99.5):
    lo = torch.quantile(X.flatten(), (100 - clip_pct) / 100)
    hi = torch.quantile(X.flatten(), clip_pct / 100)
    Xc = X.clamp(lo, hi)
    s = (hi - lo) / 3.0
    return ((Xc - lo) / s).round().clamp(0, 3) * s + lo


def int2_quant_perchannel(X, clip_pct=99.5):
    """OSCAR-style: per-channel clip thresholds in the rotated basis."""
    lo = torch.quantile(X.float(), (100 - clip_pct) / 100, dim=0, keepdim=True)
    hi = torch.quantile(X.float(), clip_pct / 100, dim=0, keepdim=True)
    Xc = torch.maximum(torch.minimum(X, hi), lo)
    s = (hi - lo) / 3.0
    s = s.clamp_min(1e-8)
    return ((Xc - lo) / s).round().clamp(0, 3) * s + lo


def main():
    torch.manual_seed(0)
    src = "mock"
    if os.path.exists(QWEN_PATH):
        from safetensors import safe_open
        with safe_open(QWEN_PATH, framework="pt") as f:
            Wq = f.get_tensor("model.layers.5.self_attn.q_proj.weight").float()
            Wk = f.get_tensor("model.layers.5.self_attn.k_proj.weight").float()
            Wv = f.get_tensor("model.layers.5.self_attn.v_proj.weight").float()
        src = "real Qwen3-0.6B q/k/v_proj"
    else:
        Wq = torch.randn(1024, 1024) * 0.02
        Wk = torch.randn(1024, 1024) * 0.02
        Wv = torch.randn(1024, 1024) * 0.02
    print(f"Source: {src}")

    T, d = 2048, Wk.shape[1]
    g = torch.Generator().manual_seed(1)
    Z = torch.randn(T, d, generator=g)
    D = torch.ones(d)
    D[torch.randperm(d, generator=g)[:8]] = 25.0     # LLM-style outlier channels
    Hstate = Z * D
    K, V = Hstate @ Wk.T, Hstate @ Wv.T
    Q = Hstate[:512] @ Wq.T                        # queries from q_proj
    HQ, HK, HD = 16, 8, 128                        # Qwen3-0.6B GQA geometry
    Qh = Q.reshape(-1, HQ, HD).transpose(0, 1)     # [HQ, nq, HD]

    def heads(M):                                  # [T, HK*HD] -> [HQ, T, HD]
        return M.reshape(-1, HK, HD).transpose(0, 1).repeat_interleave(HQ // HK, dim=0)
    attn_ref = torch.softmax(Qh @ heads(K).transpose(1, 2) / math.sqrt(HD), dim=-1)
    p = attn_ref.mean(dim=(0, 1))                    # offline per-key attention profile
    C = (K * p.unsqueeze(1)).T @ K                   # attention-aware covariance
    _, E = torch.linalg.eigh(C)
    R_osc = hadamard(K.shape[1]) @ E.T               # decorrelate + respread
    R_had = hadamard(K.shape[1])

    ref_out = attn_ref @ heads(V)
    Vq = int2_quant_perchannel(V)
    for name, R, cq in [("naive Had+global-clip", R_had, int2_quant_global),
                        ("naive Had+per-ch-clip", R_had, int2_quant_perchannel),
                        ("OSCAR rot+per-ch-clip", R_osc, int2_quant_perchannel)]:
        Kq = cq(K @ R) @ R.T
        attn_q = torch.softmax(Qh @ heads(Kq).transpose(1, 2) / math.sqrt(HD), dim=-1)
        e_k = (Kq - K).pow(2).mean() / K.pow(2).mean()
        e_attn = (attn_q - attn_ref).pow(2).mean() / attn_ref.pow(2).mean()
        e_konly = (attn_q @ heads(V) - ref_out).pow(2).mean() / ref_out.pow(2).mean()
        e_kv = (attn_q @ heads(Vq) - ref_out).pow(2).mean() / ref_out.pow(2).mean()
        print(f"{name:22s} K rel-err={e_k:.5f}  attn-err={e_attn:.5f}  "
              f"out-err(K only)={e_konly:.5f}  out-err(K+V)={e_kv:.5f}")

    print("\nPASS: OSCAR demo executed end-to-end.")


if __name__ == "__main__":
    main()
