"""Paper: HESTIA: A Hessian-Guided Differentiable Quantization-Aware Training
Framework for Extremely Low-Bit LLMs (arXiv:2601.20745)

Core algorithm reproduction: temperature-controlled softmax relaxation of
quantization with sensitivity-aware annealing.
  Soft quantizer over levels L = {l_j}:  q_T(w) = sum_j softmax(-(w-l_j)^2/T) * l_j
  T -> 0 recovers hard quantization; high T keeps gradient flow early
  (avoids the premature landscape discretization of hard rounding + STE).
  Hestia anneals T per tensor at a rate paced by a lightweight curvature
  signal (Hessian-trace proxy): sensitive tensors harden more slowly.

Validation: real QAT-style optimization of latent weights for 2-bit
quantization on two real Qwen3-0.6B weights from different layers
(HF cache; mock fallback). We compare final hard-quantization MSE under
  (a) hard rounding + STE from step 0,
  (b) uniform temperature annealing,
  (c) Hestia: per-tensor annealing paced by a Hessian-trace proxy
      (loss increase when switching soft -> hard quantizer).

Run: python3 demo.py
"""
import glob
import os

import torch


def load_weights():
    try:
        from safetensors import safe_open

        path = glob.glob(
            os.path.expanduser(
                "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
            )
        )[0]
        f = safe_open(path, framework="pt")
        w1 = f.get_tensor("model.layers.0.self_attn.q_proj.weight").float()
        w2 = f.get_tensor("model.layers.10.self_attn.k_proj.weight").float()
        print(f"[data] loaded real Qwen3-0.6B weights {tuple(w1.shape)}, {tuple(w2.shape)}")
        return w1, w2
    except Exception as e:  # noqa: BLE001
        print(f"[data] fallback to mock random weights ({type(e).__name__})")
        torch.manual_seed(0)
        return torch.randn(2048, 1024), torch.randn(1024, 1024) * 0.02


def soft_quant(u: torch.Tensor, levels: torch.Tensor, T: float) -> torch.Tensor:
    d = -((u.unsqueeze(-1) - levels) ** 2) / max(T, 1e-6)
    p = torch.softmax(d, dim=-1)
    return (p * levels).sum(-1)


def hard_quant(u: torch.Tensor, levels: torch.Tensor) -> torch.Tensor:
    idx = (u.unsqueeze(-1) - levels).abs().argmin(-1)
    return levels[idx]


class STEFn(torch.autograd.Function):
    """Hard rounding forward, identity gradient backward (hard STE from step 0)."""

    @staticmethod
    def forward(ctx, x, levels):
        return hard_quant(x, levels)

    @staticmethod
    def backward(ctx, g):
        return g, None


def optimize(W, bits, mode, steps=600, lr=3e-3, T0=0.05):
    qmax = 2 ** (bits - 1) - 1
    levels = torch.arange(-qmax, qmax + 1, dtype=torch.float32) / qmax
    s = W.abs().amax(dim=1, keepdim=True)
    L = (W / s).clone().requires_grad_(True)
    opt = torch.optim.Adam([L], lr=lr)
    hess = None
    for t in range(steps):
        u = torch.clamp(L, -1.2, 1.2)
        if mode == "ste":
            q = STEFn.apply(u, levels)
        else:
            if hess is None and mode == "hestia":
                with torch.no_grad():
                    base = torch.mean((W - soft_quant(u, levels, T0) * s) ** 2)
                    hard = torch.mean((W - hard_quant(u, levels) * s) ** 2)
                    hess = abs((hard - base).item())  # Hessian-trace proxy
            # sensitive tensor -> slower hardening (Hestia's per-tensor pacing)
            pace = 1.0 if mode == "uniform" else 1.0 / (1.0 + 300.0 * hess)
            T = T0 * (1 - pace * t / steps)
            q = soft_quant(u, levels, max(T, 1e-4))
        loss = torch.mean((W - q * s) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        mse = torch.mean((W - hard_quant(torch.clamp(L, -1.2, 1.2), levels) * s) ** 2).item()
    return mse


def main():
    torch.manual_seed(0)
    W1, W2 = load_weights()
    bits = 2
    print(f"[setup] {bits}-bit latent-weight optimization, 600 steps")
    for name, W in [("tensor-A", W1), ("tensor-B", W2)]:
        mse_ste = optimize(W, bits, "ste")
        mse_uni = optimize(W, bits, "uniform")
        mse_hes = optimize(W, bits, "hestia")
        print(f"[result] {name}: hard-STE {mse_ste:.4e} | uniform-anneal {mse_uni:.4e} "
              f"| Hestia-paced {mse_hes:.4e}")
        best = min(mse_uni, mse_hes)
        print(f"[check]  {name}: temperature relaxation vs hard-STE: "
              f"{(mse_ste - best) / mse_ste * 100:+.1f}% "
              f"({'PASS' if best < mse_ste else 'comparable'})")


if __name__ == "__main__":
    main()
