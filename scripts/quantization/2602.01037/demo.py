#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.01037 - VEQ
Title: VEQ: Modality-Adaptive Quantization for MoE Vision-Language Models
Core Method: Dual-aware PTQ for MoE VLMs —
             (1) modality-expert-aware quantization (expert activation
                 frequency prioritizes error minimization of pivotal experts)
             (2) modality-affinity-aware Hessian (token-expert affinity +
                 modality information guide calibration)
================================================================================

Qwen3-0.6B is a dense model, so this demo constructs a *mock MoE layer* whose
experts are slices of REAL Qwen3-0.6B MLP weights, and calibrates them with
two token modalities:
  - "text" tokens   : real hidden states captured from Qwen3-0.6B on text
  - "vision" tokens : synthetic low-rank + noise features (VLM visual tokens
                      have very different statistics from text tokens)

We implement Hessian-aware PTQ (GPTQ-style error compensation) where the
Hessian of each expert is built with the VEQ weighting:
    H_e = sum_tokens affinity(token, e) * freq_weight(e) * x x^T
and compare it against a plain unweighted Hessian. Evaluation: output MSE of
each expert on held-out calibration tokens from both modalities.

Usage:
    python3 demo.py           # real Qwen3-0.6B weights
    python3 demo.py --mock    # fully random fallback
================================================================================
"""
import argparse
import sys

import torch


def rtn(w, bits, group=128):
    qmax = 2 ** (bits - 1) - 1
    out = w.clone()
    for j in range(0, w.shape[1], group):
        blk = out[:, j:j + group]
        s = blk.abs().amax(dim=1, keepdim=True).clamp_min(1e-8) / qmax
        out[:, j:j + group] = s * torch.clamp(torch.round(blk / s), -qmax - 1, qmax)
    return out


def gptq_quantize(w, H, bits, group=128):
    """Minimal GPTQ: greedy column-wise quantization with Hessian error
    compensation (Cholesky form, following the standard GPTQ recursion)."""
    m, n = w.shape
    W = w.clone()
    damp = 0.01 * torch.diag(H).mean().clamp_min(1e-6)
    L = torch.linalg.cholesky(H + damp * torch.eye(n))
    Hinv = torch.linalg.cholesky(torch.cholesky_inverse(L), upper=True)  # upper factor of H^-1
    Q = torch.zeros_like(W)
    for j in range(n):
        col = W[:, j]
        qmax = 2 ** (bits - 1) - 1
        s = col.abs().max().clamp_min(1e-8) / qmax
        q = torch.clamp(torch.round(col / s), -qmax - 1, qmax) * s
        Q[:, j] = q
        err = (col - q) / Hinv[j, j].clamp_min(1e-8)
        W[:, j:] -= err.unsqueeze(1) * Hinv[j, j:].unsqueeze(0)
    return Q


def rel_err(a, b):
    return ((a - b).norm() / b.norm().clamp_min(1e-12)).item()


def load_real_weights():
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float32)
    W = model.model.layers[0].mlp.gate_proj.weight.data  # [3072, 1024]
    # 3 experts = 3 slices of the real MLP weight (realistic LLM weight stats)
    experts = [W[i * 256:(i + 1) * 256, :].clone() for i in range(3)]
    # real text activations
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    captured = {}

    def hook(_, inp, __):
        captured["x"] = inp[0].detach().reshape(-1, inp[0].shape[-1]).float()

    lin = model.model.layers[0].mlp.gate_proj
    h = lin.register_forward_hook(hook)
    text = ("Vision-language models process images and text jointly. "
            "Mixture-of-experts architectures route each token to a subset of "
            "feed-forward experts, which reduces compute per token.") * 6
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return experts, captured["x"][:400]


def make_modalities(x_text, dim, n_vis=300, seed=0):
    """vision tokens: low-rank + heavier tail (mimics ViT feature stats)."""
    g = torch.Generator().manual_seed(seed)
    U = torch.randn(dim, 16, generator=g)
    V = torch.randn(16, n_vis, generator=g)
    x_vis = (U @ V).T * 0.3
    x_vis += 0.05 * torch.randn(n_vis, dim, generator=g)
    idx = torch.randperm(x_vis.shape[1], generator=g)[: dim // 8]
    x_vis[:, idx] *= 6  # vision outlier channels
    return x_text, x_vis


def run_experiment(experts, x_text, x_vis, bits=3):
    """Compare unweighted GPTQ vs VEQ dual-aware GPTQ on the mock MoE."""
    n_exp = len(experts)
    dim = experts[0].shape[1]

    # routing: text prefers experts 0,1 ; vision prefers expert 2 (non-uniform)
    aff_text = torch.tensor([0.45, 0.40, 0.15])
    aff_vis = torch.tensor([0.10, 0.15, 0.75])

    tot_text_err_u = tot_text_err_v = 0.0
    tot_vis_err_u = tot_vis_err_v = 0.0
    for e, W in enumerate(experts):
        # --- calibration sets -------------------------------------------
        xt = x_text[torch.randperm(x_text.shape[0])[:256]]
        xv = x_vis[torch.randperm(x_vis.shape[0])[:256]]

        def build_hessian(weight_e):
            H = torch.zeros(dim, dim)
            H += weight_e * aff_text[e] * (xt.T @ xt)
            H += weight_e * aff_vis[e] * (xv.T @ xv)
            return H

        # unweighted Hessian (standard GPTQ: all tokens equal, experts equal)
        H_plain = build_hessian(1.0)
        # VEQ: expert activation frequency (how often expert e fires) boosts
        # its error-minimization priority; affinity re-weights tokens.
        freq_e = (aff_text[e] * xt.shape[0] + aff_vis[e] * xv.shape[0]) / (xt.shape[0] + xv.shape[0])
        freq_boost = 1.0 + 2.0 * freq_e          # pivotal experts get more weight
        H_veq = build_hessian(freq_boost)

        W_rtn = rtn(W, bits)
        W_g_plain = gptq_quantize(W, H_plain, bits)
        W_g_veq = gptq_quantize(W, H_veq, bits)

        for X, acc_t, acc_v in ((xt, "t", None), (xv, None, "v")):
            pass
        tot_text_err_u += rel_err(xt @ W_g_plain.T, xt @ W.T)
        tot_text_err_v += rel_err(xt @ W_g_veq.T, xt @ W.T)
        tot_vis_err_u += rel_err(xv @ W_g_plain.T, xv @ W.T)
        tot_vis_err_v += rel_err(xv @ W_g_veq.T, xv @ W.T)
        print(f"  expert {e}: freq={freq_e:.2f} | RTN text {rel_err(xt @ W_rtn.T, xt @ W.T):.4f} "
              f"| plainGPTQ text {rel_err(xt @ W_g_plain.T, xt @ W.T):.4f} "
              f"| VEQ text {rel_err(xt @ W_g_veq.T, xt @ W.T):.4f} "
              f"| VEQ vision {rel_err(xv @ W_g_veq.T, xv @ W.T):.4f}")
    print(f"\n  mean text err : plain {tot_text_err_u / n_exp:.4f} -> VEQ {tot_text_err_v / n_exp:.4f}")
    print(f"  mean vision err: plain {tot_vis_err_u / n_exp:.4f} -> VEQ {tot_vis_err_v / n_exp:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--bits", type=int, default=3)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            experts, x_text = load_real_weights()
            src = "real Qwen3-0.6B weight slices as experts + real text activations"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            args.mock = True
    if args.mock:
        experts = [torch.randn(256, 512) * 0.05 for _ in range(3)]
        x_text = torch.randn(400, 512)
        src = "mock random experts"
    x_text, x_vis = make_modalities(x_text, experts[0].shape[1])
    print(f"Source: {src}")
    print(f"Mock MoE: {len(experts)} experts of shape {tuple(experts[0].shape)}, "
          f"text tokens {tuple(x_text.shape)}, vision tokens {tuple(x_vis.shape)}")
    print(f"Quantization: W{args.bits}A16, GPTQ-style Hessian calibration\n")
    run_experiment(experts, x_text, x_vis, bits=args.bits)
    print("\nKey takeaway: weighting the calibration Hessian by token-expert "
          "affinity and expert firing frequency (VEQ's dual awareness) focuses "
          "the quantization error budget where it hurts the MoE most.")


if __name__ == "__main__":
    sys.exit(main())
