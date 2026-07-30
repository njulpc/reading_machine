#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.12609 - QuEPT
Title: QuEPT: Quantized Elastic Precision Transformers with One-Shot
       Calibration for Multi-Bit Switching
Core Method: Elastic-precision PTQ — a single 4-bit quantized base plus
             CASCADED LOW-RANK ADAPTERS per target bit-width, all calibrated
             in ONE SHOT on a small data slice, enabling real-time switching
             between 4/3/2-bit without repeated optimization.
================================================================================

Reproduced on real Qwen3-0.6B weights + activations:

  * Base: uniform per-channel 4-bit RTN quantization of a linear layer;
  * Elastic adapters: for each lower target bit-width b ∈ {3, 2}, the
    multi-bit reconstruction error E_b = W - Q_b(W) is approximated by a
    rank-r low-rank adapter, computed by ACTIVATION-WEIGHTED SVD
    (weighting s = sqrt(E[x^2]) per input channel, from the SAME small
    calibration slice — one-shot, no retraining);
  * Switching: attach adapter_b to go from the 4-bit base to b-bit
    deployment; effective bits = b + adapter overhead (r·(m+n)·16/(m·n)).

Metric: relative error of the linear layer output on real hidden states,
raw b-bit vs adapter-corrected b-bit vs 4-bit base.

Usage:
    python3 demo.py           # real Qwen3-0.6B
    python3 demo.py --mock    # random fallback
    python3 demo.py --rank 8
================================================================================
"""
import argparse
import sys

import torch


def rel_err(a, b):
    return ((a - b).norm() / b.norm().clamp_min(1e-12)).item()


def rtn_quant(W, bits):
    """Symmetric per-output-channel uniform quantization."""
    qmax = 2 ** (bits - 1) - 1
    amax = W.abs().amax(dim=1, keepdim=True).clamp_min(1e-8)
    scale = amax / qmax
    return torch.clamp(torch.round(W / scale), -qmax - 1, qmax) * scale


def calibrate_adapter(E, s, rank):
    """One-shot activation-weighted low-rank adapter for error E.

    Minimize ||(E - A B) diag(s)||_F via truncated SVD of E·diag(s),
    then fold diag(s)^{-1} into the right factor.
    """
    M = E * s.unsqueeze(0)
    U, S, Vh = torch.linalg.svd(M, full_matrices=False)
    r = min(rank, S.shape[0])
    A = U[:, :r] * S[:r].sqrt().unsqueeze(0)
    B = S[:r].sqrt().unsqueeze(1) * Vh[:r, :] / s.unsqueeze(0)
    return A, B


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
    text = ("Elastic precision quantization lets one stored model serve many "
            "deployment bit-widths by cascading low-rank adapters that "
            "reconstruct the error of each lower-precision variant.") * 6
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return W, captured["x"][:256]


def load_mock():
    torch.manual_seed(0)
    W = torch.randn(512, 256) * 0.05
    x = torch.randn(256, 256)
    x[:, :16] *= 15
    return W, x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--rank", type=int, default=16)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            W, x = load_real()
            src = "Qwen3-0.6B layer0.mlp.gate_proj (real) + real hidden states"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            W, x = load_mock()
            src = "mock layer"
    else:
        W, x = load_mock()
        src = "mock layer"
    m, n = W.shape
    print(f"Source: {src}\nW {tuple(W.shape)}, x {tuple(x.shape)}, rank r={args.rank}\n")

    y = x @ W.T
    s = (x ** 2).mean(0).sqrt().clamp_min(1e-8)  # one-shot calibration stats

    # --- 4-bit base ----------------------------------------------------------
    W4 = rtn_quant(W, 4)
    err4 = rel_err(x @ W4.T, y)
    print(f"[base 4-bit ]                        | out err {err4:.4f} | 4.00 bit/param")

    # --- elastic switch to 3-bit and 2-bit: cascaded adapters, one shot -----
    overhead = args.rank * (m + n) * 16 / (m * n)
    for bits in (3, 2):
        Wb = rtn_quant(W, bits)
        err_raw = rel_err(x @ Wb.T, y)
        A, B = calibrate_adapter(W - Wb, s, args.rank)
        W_fix = Wb + A @ B
        err_fix = rel_err(x @ W_fix.T, y)
        eff = bits + overhead
        print(f"[{bits}-bit raw ]                        | out err {err_raw:.4f} | {bits}.00 bit/param")
        print(f"[{bits}-bit+QuEPT] rank-{args.rank:<2} adapter (1-shot) | out err {err_fix:.4f} | {eff:.2f} bit/param")

    print("\nKey takeaway: one calibration slice yields per-bitwidth low-rank "
          "adapters; switching 4-bit -> 3/2-bit recovers much of the "
          "quantization error at a fraction of a bit per parameter, with "
          "no repeated optimization.")
    print("(Adapter overhead "
          f"= r·(m+n)·16/(m·n) = {overhead:.3f} bit/param for r={args.rank}.)")


if __name__ == "__main__":
    sys.exit(main())
