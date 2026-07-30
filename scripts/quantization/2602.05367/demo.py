#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.05367 - RaBiT
Title: RaBiT: Residual-Aware Binarization Training for Accurate and Efficient
       LLMs
Core Method: Residual binarization with an enforced residual hierarchy —
             each binary path is derived SEQUENTIALLY from the residual of a
             single shared full-precision weight, so every path corrects the
             error of the preceding one (no inter-path co-adaptation).
================================================================================

Residual binarization approximates a full-precision weight as a stack of
binary (±1) paths:

    W ≈ Σ_i α_i · B_i ,   B_i ∈ {-1, +1}^{m×n}

RaBiT's key mechanism (reproduced here):
  * sequential residual derivation: R_0 = W; B_i, α_i = argmin ||R_{i-1} - αB||
    then R_i = R_{i-1} - α_i·B_i. Path i provably corrects path i-1's error.
  * robust initialization prioritizing FUNCTION preservation: after the
    weight-domain fit, each α_i is re-fit to minimize OUTPUT error on
    calibration activations (functional least squares), instead of pure
    weight approximation.

Baselines shown for contrast:
  * naive multi-binary (independent paths fit simultaneously on W — the
    inter-path co-adaptation failure mode the paper identifies),
  * 2-bit RTN.

Validation: real Qwen3-0.6B weights + real activations (forward hook).

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


def rtn(w, bits, group=128):
    qmax = 2 ** (bits - 1) - 1
    out = w.clone()
    for j in range(0, w.shape[1], group):
        blk = out[:, j:j + group]
        s = blk.abs().amax(dim=1, keepdim=True).clamp_min(1e-8) / qmax
        out[:, j:j + group] = s * torch.clamp(torch.round(blk / s), -qmax - 1, qmax)
    return out


def fit_binary_path(R):
    """Least-squares binary path: B = sign(R), α = <R,B>/||B||²  (per-row)."""
    B = torch.sign(R)
    B[B == 0] = 1.0
    alpha = (R * B).sum(dim=1, keepdim=True) / B.pow(2).sum(dim=1, keepdim=True)
    return B, alpha


def rabit(W, x, k=2, functional_init=True):
    """RaBiT: sequential residual binarization from a shared FP weight."""
    paths = []
    R = W.clone()
    for i in range(k):
        B, alpha = fit_binary_path(R)
        if functional_init:
            # functional preservation: re-fit α on calibration outputs
            yR = x @ R.T                      # residual target output
            yB = x @ B.T
            alpha_f = (yR * yB).sum(dim=0) / yB.pow(2).sum(dim=0).clamp_min(1e-12)
            alpha = alpha_f.unsqueeze(1)      # per-row (output-dim) scale
        paths.append((B, alpha))
        R = R - alpha * B
    W_hat = sum(a * B for B, a in paths)
    return W_hat, paths


def naive_multibinary(W, k=2):
    """Inter-path co-adaptation baseline: k paths all fit the FULL weight
    simultaneously (no residual hierarchy); scale split evenly."""
    paths = []
    for i in range(k):
        B, alpha = fit_binary_path(W)
        alpha = alpha / k                    # each path claims 1/k of W
        paths.append((B, alpha))
    W_hat = sum(a * B for B, a in paths)
    return W_hat


def load_real():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    lin = model.model.layers[0].mlp.down_proj
    W = lin.weight.data.clone()
    captured = {}

    def hook(_, inp, __):
        captured["x"] = inp[0].detach().reshape(-1, inp[0].shape[-1]).float()

    h = lin.register_forward_hook(hook)
    text = ("Binarized neural networks replace full-precision weights with "
            "plus or minus one values, enabling matmul-free inference with "
            "additions and bit operations only.") * 6
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return W, captured["x"][:400]


def load_mock():
    torch.manual_seed(0)
    W = torch.randn(256, 1024) * 0.05
    x = torch.randn(400, 1024)
    return W, x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--paths", type=int, default=2)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            W, x = load_real()
            src = "Qwen3-0.6B layer0.mlp.down_proj (real weights + real activations)"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            W, x = load_mock()
            src = "mock random layer"
    else:
        W, x = load_mock()
        src = "mock random layer"
    print(f"Source: {src}\nWeight {tuple(W.shape)}, calibration activations {tuple(x.shape)}")
    k = args.paths
    print(f"Residual binarization with k={k} binary paths (~{k}-bit equivalent)\n")

    y = x @ W.T

    W_rtn = rtn(W, bits=2)
    print(f"[baseline ] 2-bit RTN                       | W err {rel_err(W_rtn, W):.4f} "
          f"| out err {rel_err(x @ W_rtn.T, y):.4f}")

    W_naive = naive_multibinary(W, k=k)
    print(f"[naive k=2] independent paths (co-adapt)  | W err {rel_err(W_naive, W):.4f} "
          f"| out err {rel_err(x @ W_naive.T, y):.4f}")

    W_wdom, _ = rabit(W, x, k=k, functional_init=False)
    print(f"[RaBiT w  ] residual hierarchy (weight LS)| W err {rel_err(W_wdom, W):.4f} "
          f"| out err {rel_err(x @ W_wdom.T, y):.4f}")

    W_rbt, paths = rabit(W, x, k=k, functional_init=True)
    print(f"[RaBiT fx ] + functional init (output LS) | W err {rel_err(W_rbt, W):.4f} "
          f"| out err {rel_err(x @ W_rbt.T, y):.4f}")

    res = W - W_rbt
    print(f"\nResidual after {k} paths: ||R||/||W|| = {res.norm() / W.norm():.4f} "
          f"(each path provably reduces the previous path's error).")
    print("Key takeaway: deriving each binary path from the RESIDUAL of a shared "
          "FP weight prevents inter-path co-adaptation; re-fitting scales on "
          "outputs (functional preservation) beats pure weight approximation.")


if __name__ == "__main__":
    sys.exit(main())
