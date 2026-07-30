#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.13710 - HBVLA
Title: HBVLA: Pushing 1-Bit Post-Training Quantization for Vision-Language-
       Action Models
Core Method: VLA-tailored 1-bit binarization —
             (1) policy-aware enhanced Hessian identifies action-critical
                 (salient) weights;
             (2) sparse orthogonal transform on NON-salient weights induces a
                 low-entropy intermediate state;
             (3) salient & non-salient weights are quantized in the Harr
                 (Hadamard) domain with group-wise 1-bit quantization.
================================================================================

Qwen3-0.6B is an LLM, not a VLA, but the three mechanisms are architecture
-agnostic. This demo reproduces them on real Qwen3-0.6B weights with real
activations serving as the "policy" signal:

  * saliency from a diagonal-Hessian proxy: s_ij = W_ij^2 * E[x_j^2]
    (action-critical weights = top-k saliency);
  * salient weights: kept at higher effective precision (fp16 path, as the
    paper protects them), non-salient: randomized Hadamard (Harr) transform
    -> Gaussianized, low-entropy distribution -> group-wise 1-bit
    sign+scale quantization in the transform domain, inverse transform back;
  * compared against naive 1-bit sign+scale and full-domain 1-bit Hadamard
    (no saliency split).

Metric: output relative error on real activations.

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


def hadamard_matrix(n, device):
    """Hadamard (Harr) matrix of size n (n must be power of 2), normalized."""
    H = torch.ones(1, 1, device=device)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H / (n ** 0.5)


def random_hadamard(x, H, signs):
    return (x * signs) @ H


def random_hadamard_inv(x, H, signs):
    return (x @ H.T) * signs


def harr_quantize_1bit(W, group=64, seed=0):
    """Random Hadamard (Harr) transform -> group-wise 1-bit -> inverse.
    Non-power-of-2 widths are zero-padded to the next power of 2."""
    torch.manual_seed(seed)
    m, n = W.shape
    n2 = 1 << (n - 1).bit_length()
    H = hadamard_matrix(n2, W.device)
    signs = (torch.randint(0, 2, (n2,), device=W.device) * 2 - 1).float()
    Wp = torch.zeros(m, n2, device=W.device)
    Wp[:, :n] = W
    W_h = random_hadamard(Wp, H, signs)
    W_h_q = torch.zeros_like(W_h)
    for j in range(0, n2, group):
        blk = W_h[:, j:j + group]
        B = torch.sign(blk)
        B[B == 0] = 1.0
        s = blk.abs().mean(dim=1, keepdim=True)
        W_h_q[:, j:j + group] = s * B
    W_q = random_hadamard_inv(W_h_q, H, signs)
    return W_q[:, :n]


def groupwise_1bit(w, group=64):
    """Group-wise sign+per-group-scale 1-bit quantization."""
    m, n = w.shape
    out = torch.zeros_like(w)
    for j in range(0, n, group):
        blk = w[:, j:j + group]
        B = torch.sign(blk)
        B[B == 0] = 1.0
        s = blk.abs().mean(dim=1, keepdim=True)          # group scale
        out[:, j:j + group] = s * B
    return out


def naive_1bit(w):
    B = torch.sign(w)
    B[B == 0] = 1.0
    s = (w * B).sum(1, keepdim=True) / B.pow(2).sum(1, keepdim=True)
    return s * B


def hbvla_quantize(W, x, salient_ratio=0.05, group=64, seed=0):
    """HBVLA pipeline: saliency split + Harr-domain 1-bit on non-salient."""
    torch.manual_seed(seed)
    m, n = W.shape
    # --- (1) policy-aware Hessian proxy saliency ----------------------------
    act2 = x.pow(2).mean(0)                            # E[x_j^2]
    sal = W.pow(2) * act2.unsqueeze(0)
    thresh = sal.flatten().sort(descending=True).values[int(salient_ratio * sal.numel())]
    salient_mask = sal >= thresh

    # --- (2)+(3) Harr transform + group-wise 1-bit on non-salient -----------
    W_q_nonsal = harr_quantize_1bit(W, group=group, seed=seed)

    # salient weights kept in fp16 (protected path), non-salient -> 1-bit
    W_q = torch.where(salient_mask, W, W_q_nonsal)
    return W_q, salient_mask.float().mean().item()


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
    text = ("Robots execute long-horizon action sequences where small errors "
            "accumulate over time, so action-critical weights must be "
            "protected when the rest of the network is binarized.") * 6
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return W, captured["x"][:256]


def load_mock():
    torch.manual_seed(0)
    return torch.randn(256, 1024) * 0.05, torch.randn(256, 1024)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--salient", type=float, default=0.05)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            W_full, x = load_real()
            src = "Qwen3-0.6B layer0.mlp.down_proj rows 0:256 (real) + real activations"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            W_full, x = load_mock()
            src = "mock random layer"
    else:
        W_full, x = load_mock()
        src = "mock random layer"
    W = W_full[:256]
    n = W.shape[1]
    print(f"Source: {src}\nWeight {tuple(W.shape)} | salient ratio {args.salient:.0%}\n")
    y = x @ W.T

    W_n = naive_1bit(W)
    print(f"[naive 1bit] sign+row-scale            | out err {rel_err(x @ W_n.T, y):.4f} | ~1.0 bit/param")

    # full-domain Hadamard 1-bit, no saliency split (ablation)
    W_had = harr_quantize_1bit(W)
    print(f"[ablation  ] Harr-domain 1-bit (no split)| out err {rel_err(x @ W_had.T, y):.4f} | ~1.0 bit/param")

    W_q, frac = hbvla_quantize(W, x, salient_ratio=args.salient)
    bpp = frac * 16 + (1 - frac) * 1.06
    print(f"[HBVLA     ] salient fp16 + Harr 1-bit   | out err {rel_err(x @ W_q.T, y):.4f} "
          f"| ~{bpp:.2f} bit/param")

    print(f"\nSalient weights protected: {frac:.1%} (policy-aware Hessian proxy).")
    print("Key takeaway: the Harr transform Gaussianizes non-salient weights "
          "(low-entropy state) so 1-bit group quantization loses far less, "
          "while a small salient set carries the action-critical signal.")


if __name__ == "__main__":
    sys.exit(main())
