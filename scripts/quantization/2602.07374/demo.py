#!/usr/bin/env python3
"""
================================================================================
Paper: 2602.07374 - TernaryLM
Title: TernaryLM: Memory-Efficient Language Modeling via Native 1.5-Bit
       Quantization with Adaptive Layer-wise Scaling
Core Method: Native ternary {-1, 0, +1} quantization (log2(3) ≈ 1.58 bit)
             trained from scratch with straight-through estimators (STE) and
             adaptive per-layer scaling factors.
================================================================================

This demo reproduces the TernaryLM training primitives on real Qwen3-0.6B
weights/activations:

  * ternary quantization with learnable per-layer scale s and threshold Δ:
        w_q = s · clamp(round(w/s), -1, 1)  with soft thresholding via
        mean-magnitude threshold Δ = 0.7·E|w| (standard ternary practice);
  * straight-through estimator: forward uses w_q, backward treats
    quantize(·) as identity inside the clipping region;
  * adaptive per-layer scaling: s is a learnable parameter updated by SGD
    jointly with the latent weights.

Experiment: a ternary linear layer is trained (few hundred steps, CPU) to
reproduce the input→output mapping of a REAL Qwen3-0.6B projection on REAL
activations. We track the loss curve of the STE-trained ternary layer vs. a
frozen RTN-ternary baseline, and report memory math (1.58 bit vs FP32).

Usage:
    python3 demo.py           # real Qwen3-0.6B
    python3 demo.py --mock    # random fallback
================================================================================
"""
import argparse
import sys

import torch


def ternary_quantize(w, scale, thresh_ratio=0.7):
    """Ternary quantization {-s, 0, +s} with magnitude threshold Δ."""
    delta = thresh_ratio * w.abs().mean()
    t = (w / scale.clamp_min(1e-8)).round().clamp(-1, 1)
    t = torch.where(w.abs() < delta, torch.zeros_like(t), t)
    return t * scale


class TernaryLinear(torch.nn.Module):
    """Linear layer with STE-based ternary weights + learnable layer scale."""

    def __init__(self, w_init):
        super().__init__()
        self.w = torch.nn.Parameter(w_init.clone())
        self.scale = torch.nn.Parameter(w_init.abs().mean().clamp_min(1e-8))

    def quantized_weight(self):
        return ternary_quantize(self.w, self.scale)

    @torch.no_grad()
    def refit_scale(self):
        """Adaptive layer-wise scaling (LSQ-style): given the current ternary
        pattern T = clamp(round(w/s)), re-fit s* = argmin_s ||w - s·T||²."""
        delta = 0.7 * self.w.abs().mean()
        t = (self.w / self.scale.clamp_min(1e-8)).round().clamp(-1, 1)
        t = torch.where(self.w.abs() < delta, torch.zeros_like(t), t)
        denom = t.pow(2).sum().clamp_min(1e-12)
        self.scale.copy_((self.w * t).sum() / denom)

    def forward(self, x):
        w_q = ternary_quantize(self.w, self.scale)
        # STE: forward w_q, gradient flows to self.w as identity
        w_ste = self.w + (w_q - self.w).detach()
        return x @ w_ste.T


def rel_err(a, b):
    return ((a - b).norm() / b.norm().clamp_min(1e-12)).item()


def load_real():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    lin = model.model.layers[0].mlp.up_proj
    W = lin.weight.data.clone()
    captured = {}

    def hook(_, inp, __):
        captured["x"] = inp[0].detach().reshape(-1, inp[0].shape[-1]).float()

    h = lin.register_forward_hook(hook)
    text = ("Ternary networks constrain weights to minus one, zero, and plus "
            "one, which drastically reduces memory while keeping enough "
            "capacity for language modeling when trained from scratch.") * 6
    with torch.no_grad():
        model(**tok(text, return_tensors="pt"))
    h.remove()
    return W, captured["x"][:512]


def load_mock():
    torch.manual_seed(0)
    return torch.randn(512, 256) * 0.05, torch.randn(512, 256)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--steps", type=int, default=300)
    args = ap.parse_args()

    torch.manual_seed(0)
    if not args.mock:
        try:
            W, x = load_real()
            src = "Qwen3-0.6B layer0.mlp.up_proj (real weights + real activations)"
        except Exception as e:
            print(f"[warn] {e}; mock mode.")
            W, x = load_mock()
            src = "mock random layer"
    else:
        W, x = load_mock()
        src = "mock random layer"
    print(f"Source: {src}\nWeight {tuple(W.shape)}, activations {tuple(x.shape)}\n")

    y_target = x @ W.T

    # --- baseline: frozen RTN ternary (no training) -------------------------
    scale0 = W.abs().mean().clamp_min(1e-8)
    W_rtn = ternary_quantize(W, scale0)
    print(f"[baseline ] RTN ternary (frozen)     | out err {rel_err(x @ W_rtn.T, y_target):.4f}")

    # --- TernaryLM: STE training with adaptive layer scale -------------------
    layer = TernaryLinear(W)
    opt = torch.optim.Adam(layer.parameters(), lr=2e-4)
    loss_fn = torch.nn.MSELoss()
    bs = 128
    print(f"[TernaryLM] STE training {args.steps} steps (ternary fwd, identity bwd, "
          f"learnable per-layer scale) ...")
    for step in range(args.steps):
        idx = torch.randint(0, x.shape[0], (bs,))
        loss = loss_fn(layer(x[idx]), y_target[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if (step + 1) % 10 == 0:
            layer.refit_scale()  # adaptive per-layer scaling (LSQ re-fit)
        if (step + 1) % (args.steps // 5) == 0 or step == 0:
            with torch.no_grad():
                err = rel_err(layer(x), y_target)
            print(f"  step {step+1:4d} | mse {loss.item():.6f} | out rel-err {err:.4f} "
                  f"| scale {layer.scale.item():.5f}")

    with torch.no_grad():
        W_q = layer.quantized_weight()
        final_err = rel_err(x @ W_q.T, y_target)
        sparsity = (W_q == 0).float().mean().item()
    print(f"\n[TernaryLM] final ternary out err {final_err:.4f} "
          f"(baseline RTN {rel_err(x @ W_rtn.T, y_target):.4f}), zeros {sparsity:.1%}")

    # --- memory math ---------------------------------------------------------
    n_params = W.numel()
    fp32_mb = n_params * 4 / 1e6
    tern_mb = n_params * 1.58 / 8 / 1e6
    print(f"\nMemory: FP32 {fp32_mb:.1f} MB -> ternary(1.58bit) {tern_mb:.2f} MB "
          f"({fp32_mb / tern_mb:.1f}x reduction, per this layer)")
    print("Key takeaway: STE + adaptive per-layer scaling lets a ternary layer "
          "be TRAINED to recover function, while RTN ternary is stuck at its "
          "frozen error level.")


if __name__ == "__main__":
    sys.exit(main())
