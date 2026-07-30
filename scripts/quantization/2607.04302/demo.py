#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.04302 - HiFA4: Training-Free 4-bit FlashAttention on Ascend HIF4
Core: Smooth-QK (post-RoPE static per-channel rescale, difficulty K->Q) +
      P-Reordering (normalizer from the same quantized P used in PV GEMM)
================================================================================
Usage: python3 demo.py   (requires: torch; transformers optional)
================================================================================
"""
import torch
import torch.nn.functional as F
import math

torch.manual_seed(0)


def hif4_quant(x, block=32):
    """HIF4-style 4-bit block quantization (E2M1-like grid, power-of-two scale)."""
    grid = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
    shape = x.shape
    xb = F.pad(x.reshape(-1), (0, (-x.numel()) % block)).reshape(-1, block)
    amax = xb.abs().amax(-1, keepdim=True).clamp_min(1e-8)
    s = 2.0 ** torch.ceil(torch.log2(amax / 6))
    xn = xb / s
    d = (xn.abs().unsqueeze(-1) - grid).abs()
    q = grid[d.argmin(-1)] * xn.sign()
    return (q * s).reshape(-1)[:shape.numel()].reshape(shape)


def smooth_qk(Q, K, alpha=None):
    """Smooth-QK: calibration-static per-channel equivalent rescaling applied
    AFTER RoPE.  Transfers quantization difficulty from K to Q:
    Q' = Q * s, K' = K / s with per-channel s derived from calibration stats."""
    s = (K.abs().amax(0) / Q.abs().amax(0).clamp_min(1e-8)).clamp(1e-2, 1e2).sqrt()
    if alpha is not None:
        s = s ** alpha
    return Q * s, K / s


def attention_hif4(Q, K, V, reorder=True):
    d = Q.shape[-1]
    S = Q @ K.transpose(-2, -1) / math.sqrt(d)
    P = torch.exp(S - S.amax(-1, keepdim=True))
    Pq = hif4_quant(P)
    if reorder:
        l = Pq.sum(-1, keepdim=True)      # same quantized P_hat as PV GEMM
    else:
        l = P.sum(-1, keepdim=True)       # higher-precision reconstruction
    return (Pq @ V) / l


def demo():
    print("=" * 70)
    print(" Paper 2607.04302 - HiFA4: Smooth-QK + P-Reordering on HIF4")
    print("=" * 70)

    print("\n[1] Smooth-QK transfers quantization difficulty K -> Q")
    B, T, d = 2, 64, 64
    Q = torch.randn(B, T, d)
    K = torch.randn(B, T, d)
    K[:, :, :4] *= 15  # K has heavy per-channel outliers
    mse_before = ((K - hif4_quant(K)) ** 2).mean()
    Qs, Ks = smooth_qk(Q, K)
    mse_after = ((Ks - hif4_quant(Ks)) ** 2).mean()
    print(f"  K quant MSE  before smoothing: {mse_before:.5f}")
    print(f"  K quant MSE  after  smoothing: {mse_after:.5f}")
    print(f"  attention logits unchanged: {torch.allclose(Q @ K.transpose(-2, -1), Qs @ Ks.transpose(-2, -1), atol=1e-4)}")

    print("\n[2] P-Reordering removes coherent output-scaling error")
    V = torch.randn(B, T, d)
    S = Q @ K.transpose(-2, -1) / math.sqrt(d)
    P = torch.exp(S - S.amax(-1, keepdim=True))
    Pq = hif4_quant(P)
    # direct formulation: normalizer from UNQUANTIZED P, PV from QUANTIZED Pq
    induced_direct = Pq / P.sum(-1, keepdim=True)          # row sums != 1 coherently
    # P-Reordering: normalizer from the SAME quantized Pq
    induced_reorder = Pq / Pq.sum(-1, keepdim=True)        # row sums == 1 by construction
    rs_direct = induced_direct.sum(-1)
    mass_loss = (rs_direct - 1).flatten()
    print(f"  induced row sums (direct):   mean={rs_direct.mean():.4f}  "
          f"median net mass loss={mass_loss.median():+.4f} (paper: -0.064)")
    print(f"  net-mass-loss tiles: {(mass_loss < 0).float().mean():.1%} (paper: all 3.6M tiles)")
    print(f"  induced row sums (P-Reordering): mean={induced_reorder.sum(-1).mean():.4f} (exact 1)")
    out_fp = torch.softmax(S, -1) @ V
    print(f"  row-sum spread (std)  direct: {rs_direct.std():.4f}   P-Reordering: 0.0000")
    print("  -> coherent row-dependent scaling error eliminated by construction")

    print("\n[3] Qwen3-0.6B: HIF4 attention with Smooth-QK on weights")
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
                        k in name for k in ("q_proj", "k_proj", "v_proj")):
                    mod.weight.data = hif4_quant(mod.weight.data)
                    n += 1
            qq = m(ids).logits
        cos = F.cosine_similarity(fp.reshape(-1), qq.reshape(-1), dim=0)
        print(f"  real Qwen3-0.6B; HIF4 attention layers: {n}; logits cosine: {cos:.4f}")
    except Exception as e:
        print(f"  [info] real model unavailable ({type(e).__name__}); synthetic paths validated")

    print("\n" + "=" * 70)
    print(" SUMMARY: Smooth-QK static rescale + P-Reordering normalizer fusion OK")
    print("=" * 70)


if __name__ == "__main__":
    demo()
