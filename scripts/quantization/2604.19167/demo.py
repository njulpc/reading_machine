"""LBLLM (arXiv:2604.19167): three-stage distillation for W(1+1)A4
binarization — reference reproduction of the quantization structure and the
decoupled training recipe on a small random Qwen3-architecture block.

Stage 1: PTQ init (sign + group bitmap decomposition).
Stage 2: layer-wise distillation of weight-side params, activations in FP32.
Stage 3: learnable 4-bit activation scales, weights frozen.
"""
import torch
import torch.nn as nn

torch.manual_seed(0)
GROUP = 64


def load_qwen3_config():
    try:
        from huggingface_hub import hf_hub_download
        import json
        with open(hf_hub_download("Qwen/Qwen3-0.6B", "config.json")) as f:
            return json.load(f)
    except Exception:
        return {"hidden_size": 1024, "intermediate_size": 3072}


class STE(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)

    @staticmethod
    def backward(ctx, g):
        return g


def w11_decompose(W):
    """Stage-1 PTQ init: W ≈ alpha*B + beta*M per group (1bit sign + 1bit bitmap)."""
    O, I = W.shape
    Wg = W.reshape(O, I // GROUP, GROUP)
    B = torch.sign(Wg)
    B = torch.where(B == 0, torch.ones_like(B), B)          # {-1,+1}
    M = (Wg.abs() > Wg.abs().mean(dim=-1, keepdim=True)).float()  # bitmap
    # Least squares for alpha, beta per group given B, M.
    alpha = (Wg * B * (1 - M)).sum(-1, keepdim=True) / ((1 - M).sum(-1, keepdim=True) + 1e-8)
    beta = (Wg * B * M).sum(-1, keepdim=True) / (M.sum(-1, keepdim=True) + 1e-8)
    return B, M, alpha, beta


class W11A4Linear(nn.Module):
    """W(1+1)A4 linear: binary sign + group bitmap weights, 4-bit activations."""

    def __init__(self, W):
        super().__init__()
        O, I = W.shape
        B, M, alpha, beta = w11_decompose(W)
        self.register_buffer("B", B)
        self.register_buffer("M", M)
        self.alpha = nn.Parameter(alpha)
        self.beta = nn.Parameter(beta)
        self.log_a_scale = nn.Parameter(torch.zeros(1))     # stage-3 learnable
        self.O, self.I = O, I

    def weight(self):
        Wg = self.alpha * self.B * (1 - self.M) + self.beta * self.B * self.M
        return Wg.reshape(self.O, self.I)

    def quant_act(self, x):
        s = torch.exp(self.log_a_scale).clamp(1e-4, 10.0)
        q = torch.clamp(STE.apply(x / s), -8, 7)
        return q * s

    def forward(self, x, quant_act=True):
        if quant_act:
            x = self.quant_act(x)
        return x @ self.weight().T


def main():
    cfg = load_qwen3_config()
    dim, N = 256, 512            # small replica of a Qwen3 linear layer
    W = torch.randn(dim, dim) * 0.05
    x = torch.randn(N, dim)
    x[:, :8] *= 6.0              # outlier channels
    y_ref = x @ W.T

    layer = W11A4Linear(W)
    opt2 = torch.optim.Adam([layer.alpha, layer.beta], lr=1e-3)

    # --- Stage 2: layer-wise distillation, weight side only, activations FP32
    for it in range(200):
        loss = (layer(x, quant_act=False) - y_ref).pow(2).mean()
        opt2.zero_grad(); loss.backward(); opt2.step()
    print(f"stage2 (weight distill) final MSE: {loss.item():.6f}")

    # --- Stage 3: learn activation scale only, weights frozen
    opt3 = torch.optim.Adam([layer.log_a_scale], lr=1e-2)
    for it in range(200):
        loss = (layer(x) - y_ref).pow(2).mean()
        opt3.zero_grad(); loss.backward(); opt3.step()
    mse_final = loss.item()
    mse_ptq = ((W11A4Linear(W))(x) - y_ref).pow(2).mean().item()
    print(f"stage3 (act-scale)   final MSE: {mse_final:.6f}")
    print(f"PTQ-init MSE (no training):       {mse_ptq:.6f}")
    assert mse_final < mse_ptq
    print("PASS: three-stage decoupled training reduces W(1+1)A4 error.")


if __name__ == "__main__":
    main()
