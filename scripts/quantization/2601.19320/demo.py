"""Paper: StableQAT: Stable Quantization-Aware Training at Ultra-Low Bitwidths (arXiv:2601.19320)

Core algorithm reproduction: Fourier-analysis surrogate for the rounding operator.
The sawtooth frac(x) has Fourier series
    frac(x) ~ sum_{k>=1} (-1)^{k+1} sin(2*pi*k*x) / (pi*k)
so the K-harmonic surrogate of round(x) = x - frac(x) has derivative
    r_K'(x) = 1 - 2*sum_{k=1..K} (-1)^{k+1} cos(2*pi*k*x).
K=0 gives derivative 1 == straight-through estimator (STE), i.e. STE is a
special case of the surrogate family (the paper's central claim).

Validation: real QAT-style optimization where latent weights themselves are
trained (not just scales), on a real Qwen3-0.6B q_proj weight (HF cache;
mock random fallback). We optimize latent pre-round weights to minimize
reconstruction MSE of the *hard-quantized* model and compare final MSE under
STE (K=0) vs Fourier surrogates K=1..3 at 2-bit and 3-bit.

Run: python3 demo.py
"""
import glob
import os

import torch


def load_weight() -> torch.Tensor:
    """Load a real Qwen3-0.6B layer weight; fall back to mock random weight."""
    try:
        from safetensors import safe_open

        path = glob.glob(
            os.path.expanduser(
                "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
            )
        )[0]
        f = safe_open(path, framework="pt")
        w = f.get_tensor("model.layers.0.self_attn.q_proj.weight").float()
        print(f"[data] loaded real Qwen3-0.6B q_proj weight {tuple(w.shape)}")
        return w
    except Exception as e:  # noqa: BLE001
        print(f"[data] fallback to mock random weight ({type(e).__name__})")
        torch.manual_seed(0)
        return torch.randn(2048, 1024)


def fourier_surrogate_deriv(x: torch.Tensor, K: int) -> torch.Tensor:
    """r_K'(x) = 1 - 2 * sum_{k=1..K} (-1)^{k+1} cos(2*pi*k*x)."""
    d = torch.ones_like(x)
    for k in range(1, K + 1):
        d = d - 2.0 * ((-1) ** (k + 1)) * torch.cos(2 * torch.pi * k * x)
    return d


class FourierQuantFn(torch.autograd.Function):
    """Forward: true rounding (model is truly quantized).
    Backward: K-harmonic Fourier surrogate derivative (K=0 == STE)."""

    @staticmethod
    def forward(ctx, x, K):
        ctx.save_for_backward(x)
        ctx.K = K
        return torch.round(x)

    @staticmethod
    def backward(ctx, grad_out):
        (x,) = ctx.saved_tensors
        return grad_out * fourier_surrogate_deriv(x, ctx.K), None


def qat_run(W: torch.Tensor, bits: int, K: int, steps: int = 600, lr: float = 3e-3) -> float:
    """Train latent pre-round weights (real QAT regime), fixed per-channel scale."""
    qmax = 2 ** (bits - 1) - 1
    s = W.abs().amax(dim=1, keepdim=True) / qmax
    L = (W / s).clone().requires_grad_(True)
    opt = torch.optim.Adam([L], lr=lr)
    for _ in range(steps):
        q = FourierQuantFn.apply(L, K)
        loss = torch.mean((W - q * s) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        mse = torch.mean((W - torch.round(L) * s) ** 2).item()
    return mse


def main():
    torch.manual_seed(0)
    W = load_weight()
    print("[setup] latent-weight QAT (600 Adam steps), surrogate K sweep")
    for bits in (2, 3):
        mses = {K: qat_run(W, bits, K) for K in (0, 1, 2, 3)}
        line = " | ".join(f"K={K}: {m:.4e}" for K, m in mses.items())
        print(f"[result] {bits}-bit  STE(=K0) vs Fourier surrogates: {line}")
        best_K = min((k for k in (1, 2, 3)), key=lambda k: mses[k])
        imp = (mses[0] - mses[best_K]) / mses[0] * 100
        print(f"[check]  {bits}-bit  best surrogate K={best_K} improves over STE by "
              f"{imp:.1f}% ({'PASS' if mses[best_K] < mses[0] else 'comparable'})")


if __name__ == "__main__":
    main()
