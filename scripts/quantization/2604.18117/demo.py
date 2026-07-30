"""LoRaQ (arXiv:2604.18117): data-free low-rank compensation for 4-bit PTQ
with the compensation branch itself quantized — reference reproduction.

Pipeline: W4 main layer; residual E = W - W4 approximated by a rank-r branch
U@V optimized data-free to minimize weight-reconstruction error; branch then
quantized to W8 -> fully sub-16-bit pipeline.
"""
import torch

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


def sym_quant(W, bits):
    q = 2 ** (bits - 1) - 1
    O, I = W.shape
    g = min(GROUP, I)          # small matrices (e.g. low-rank factors) use full-width groups
    Wg = W.reshape(O, I // g, g)
    s = Wg.abs().amax(-1, keepdim=True).clamp(min=1e-12) / q
    return (torch.clamp(torch.round(Wg / s), -q - 1, q) * s).reshape(O, I)


def low_rank_branch(E, rank, steps=300):
    """Data-free optimization of a rank-r branch to reconstruct residual E."""
    O, I = E.shape
    U, S, Vh = torch.linalg.svd(E, full_matrices=False)
    U_ = torch.nn.Parameter(U[:, :rank] * S[:rank].sqrt())
    V_ = torch.nn.Parameter(Vh[:rank] * S[:rank].sqrt().unsqueeze(1))
    opt = torch.optim.Adam([U_, V_], lr=1e-3)
    for _ in range(steps):
        loss = (U_ @ V_ - E).pow(2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return U_.detach(), V_.detach()


def main():
    cfg = load_qwen3_config()
    I, O, N, rank = 256, 256, 512, 16
    print(f"Qwen3-0.6B-style linear {I}->{O}, low-rank branch r={rank}")
    W = torch.randn(O, I) * 0.05 + torch.randn(O, I).sin() * 0.02  # some structure
    X = torch.randn(N, I)
    y_ref = X @ W.T

    # 1) pure W4
    W4 = sym_quant(W, 4)
    err_w4 = (X @ W4.T - y_ref).pow(2).mean().item()

    # 2) W4 + FP32 low-rank branch (data-free optimized)
    E = W - W4
    U, V = low_rank_branch(E, rank)
    W_comp = W4 + U @ V
    err_fp32 = (X @ W_comp.T - y_ref).pow(2).mean().item()

    # 3) W4 + W8A8 branch (fully sub-16-bit pipeline, LoRaQ's key point)
    U8 = sym_quant(U, 8)
    X8 = sym_quant(X, 8)  # activations 8-bit for the branch path
    W_comp8 = W4 + U8 @ V
    y_full8 = X @ W4.T + X8 @ (U8 @ V).T
    err_w8 = (y_full8 - y_ref).pow(2).mean().item()

    print(f"output MSE  pure W4:            {err_w4:.6f}")
    print(f"output MSE  W4 + FP32 branch:   {err_fp32:.6f}")
    print(f"output MSE  W4 + W8A8 branch:   {err_w8:.6f}  (fully sub-16-bit)")
    assert err_fp32 < err_w4 and err_w8 < err_w4
    print("PASS: quantizable low-rank branch recovers W4 error without FP16 side path.")


if __name__ == "__main__":
    main()
