#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.01027 - SFMP
Title: SFMP: Fine-Grained, Hardware-Friendly and Search-Free Mixed-Precision
       Quantization for Large Language Models
Core Method: Search-free block-wise mixed-precision quantization with
             fractional bit-width + saliency-based row-column reordering
================================================================================

This demo reproduces the four core ideas of SFMP on the real Qwen3-0.6B model:

1) Fractional bit-width: the average bit-width of a weight matrix is a
   continuous value (e.g. 3.25 bit), realized by assigning blocks to
   high/low precision so that the block mixture hits the fractional average.
2) Block-wise mixed-precision: the weight matrix is partitioned into
   regular B x B blocks (hardware-friendly), each block quantized at its
   assigned precision.
3) Row-column weight reordering: rows/columns are permuted so that salient
   weights aggregate into a contiguous region, so block-wise precision
   assignment can cover most salient weights with few high-precision blocks.
4) (Kernel-level idea 4 is hardware-specific and out of scope for this demo.)

Validation: real Qwen3-0.6B weights + real activations captured by a forward
hook on a calibration sentence. Falls back to a small random linear layer
(--mock) when the model cannot be loaded.

Usage:
    python3 demo.py           # real Qwen3-0.6B
    python3 demo.py --mock    # random-weight fallback
================================================================================
"""
import argparse
import sys

import torch


# -----------------------------------------------------------------------------
# Building blocks
# -----------------------------------------------------------------------------
def quantize_block_rtn(w, bits):
    """Round-to-nearest symmetric quantization of a block (per-row scale)."""
    qmax = 2 ** (bits - 1) - 1
    s = w.abs().amax(dim=1, keepdim=True).clamp_min(1e-8) / qmax
    return s * torch.clamp(torch.round(w / s), -qmax - 1, qmax)


def blockwise_mixed_quant(w, bits_map, block):
    """Quantize w block-by-block; bits_map[i, j] = bit-width of block (i, j)."""
    m, n = w.shape
    out = torch.zeros_like(w)
    for i in range(0, m, block):
        for j in range(0, n, block):
            blk = w[i:i + block, j:j + block]
            out[i:i + block, j:j + block] = quantize_block_rtn(blk, bits_map[i // block, j // block])
    return out


def saliency_scores(w, x):
    """Activation-aware saliency: |W_ij| * sqrt(E[x_j^2]) (AWQ-style)."""
    act = x.pow(2).mean(dim=0).sqrt()          # [n]
    return w.abs() * act.unsqueeze(0)          # [m, n]


def sfmp_quantize(w, x, avg_bits=3.25, hi_bits=4, lo_bits=3, block=32):
    """
    SFMP pipeline (search-free):
      1. saliency-aware row-column reordering (aggregate salient weights)
      2. fractional bit-width: choose the fraction of hi-precision blocks so
         that the block mixture equals avg_bits (continuous target)
      3. block-wise mixed-precision quantization
    Returns (dequantized weight in ORIGINAL layout, effective average bits).
    """
    m, n = w.shape
    sal = saliency_scores(w, x)

    # --- idea 3: row-column reordering -------------------------------------
    col_order = torch.argsort(sal.mean(dim=0), descending=True)
    row_order = torch.argsort(sal.mean(dim=1), descending=True)
    w_perm = w[row_order][:, col_order]
    sal_perm = sal[row_order][:, col_order]

    # --- idea 1+2: fractional bit-width via block mixture -------------------
    nb_m = (m + block - 1) // block
    nb_n = (n + block - 1) // block
    n_blocks = nb_m * nb_n
    frac_hi = (avg_bits - lo_bits) / (hi_bits - lo_bits)
    n_hi = int(round(frac_hi * n_blocks))

    # block saliency = mean saliency inside the block (search-free ranking)
    blk_sal = torch.zeros(nb_m, nb_n)
    for i in range(nb_m):
        for j in range(nb_n):
            blk_sal[i, j] = sal_perm[i * block:(i + 1) * block,
                                     j * block:(j + 1) * block].mean()
    thresh = blk_sal.flatten().sort(descending=True).values[min(n_hi, n_blocks - 1)]
    bits_map = torch.where(blk_sal >= thresh, torch.tensor(hi_bits), torch.tensor(lo_bits))
    eff_bits = bits_map.float().mean().item()

    w_q = blockwise_mixed_quant(w_perm, bits_map, block)

    # invert permutation
    w_q_orig = torch.zeros_like(w_q)
    w_q_orig[row_order] = w_q
    inv_col = torch.argsort(col_order)
    w_q_orig = w_q_orig[:, inv_col]
    return w_q_orig, eff_bits, n_hi, n_blocks


def rel_err(a, b):
    return ((a - b).norm() / b.norm().clamp_min(1e-12)).item()


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
def load_real(args):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    lin = model.model.layers[0].mlp.gate_proj
    W = lin.weight.data.clone()
    captured = {}

    def hook(_, inp, __):
        captured["x"] = inp[0].detach().reshape(-1, inp[0].shape[-1]).float()

    h = lin.register_forward_hook(hook)
    text = ("Large language models are increasingly deployed on edge devices, "
            "which requires aggressive weight compression. Mixed-precision "
            "quantization assigns different bit-widths to different parts of "
            "a weight matrix to trade off accuracy against memory.") * 4
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return W, captured["x"][:512]


def load_mock(args):
    torch.manual_seed(0)
    W = torch.randn(512, 256) * 0.05
    W[:20, :] *= 8  # salient rows
    x = torch.randn(512, 256)
    x[:, :32] *= 4  # salient input dims
    return W, x


# -----------------------------------------------------------------------------
# Main experiment
# -----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--avg-bits", type=float, default=3.25)
    ap.add_argument("--block", type=int, default=32)
    args = ap.parse_args()

    torch.manual_seed(0)
    if args.mock:
        W, x = load_mock(args)
        src = "mock random layer"
    else:
        try:
            W, x = load_real(args)
            src = "Qwen3-0.6B layer0.mlp.gate_proj (real weights + real activations)"
        except Exception as e:
            print(f"[warn] Qwen3-0.6B unavailable ({e}); falling back to mock.")
            W, x = load_mock(args)
            src = "mock random layer"
    print(f"Source: {src}")
    print(f"Weight: {tuple(W.shape)}, activations: {tuple(x.shape)}")
    print(f"Target average bit-width: {args.avg_bits} (fractional)\n")

    y_ref = x @ W.T

    # --- baseline 1: uniform RTN at floor(avg_bits) -------------------------
    lo = int(args.avg_bits)
    W_uni = quantize_block_rtn(W, lo)
    print(f"[baseline] uniform {lo}-bit RTN            | W err {rel_err(W_uni, W):.4f} "
          f"| out err {rel_err(x @ W_uni.T, y_ref):.4f} | avg bits {lo:.2f}")

    # --- baseline 2: block-wise mixed precision WITHOUT reordering ----------
    sal = saliency_scores(W, x)
    nb_m = (W.shape[0] + args.block - 1) // args.block
    nb_n = (W.shape[1] + args.block - 1) // args.block
    blk_sal = torch.zeros(nb_m, nb_n)
    for i in range(nb_m):
        for j in range(nb_n):
            blk_sal[i, j] = sal[i * args.block:(i + 1) * args.block,
                                j * args.block:(j + 1) * args.block].mean()
    frac_hi = (args.avg_bits - lo) / (lo + 1 - lo)
    n_hi = int(round(frac_hi * nb_m * nb_n))
    thresh = blk_sal.flatten().sort(descending=True).values[max(0, min(n_hi, nb_m * nb_n - 1))]
    bits_map = torch.where(blk_sal >= thresh, torch.tensor(lo + 1), torch.tensor(lo))
    W_nore = blockwise_mixed_quant(W, bits_map, args.block)
    print(f"[abl-1   ] block-mixed, no reorder          | W err {rel_err(W_nore, W):.4f} "
          f"| out err {rel_err(x @ W_nore.T, y_ref):.4f} | avg bits {bits_map.float().mean():.2f}")

    # --- SFMP full pipeline ---------------------------------------------------
    W_sfmp, eff, n_hi, n_blocks = sfmp_quantize(W, x, avg_bits=args.avg_bits,
                                                hi_bits=lo + 1, lo_bits=lo, block=args.block)
    print(f"[SFMP    ] reorder + frac-bit block-mixed  | W err {rel_err(W_sfmp, W):.4f} "
          f"| out err {rel_err(x @ W_sfmp.T, y_ref):.4f} | avg bits {eff:.2f}")
    print(f"\nSFMP assigned {n_hi}/{n_blocks} blocks to {lo+1}-bit, rest to {lo}-bit "
          f"(fractional bit-width realized exactly, no discrete search).")
    print("Key takeaway: saliency aggregation via row-column reordering lets a "
          "hardware-friendly REGULAR block grid behave like irregular fine-grained "
          "mixed precision.")


if __name__ == "__main__":
    sys.exit(main())
