"""CoQuant (arXiv:2604.26378): joint weight-activation subspace projection
for mixed-precision LLMs — reference reproduction.

Output error of a quantized linear layer is driven by BOTH activation and
weight quantization noise. CoQuant balances both covariances via a weighted
PCA (closed form) to pick the high-precision subspace; baseline picks it
from activation covariance alone.
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


def int4(W):
    q = 2 ** 3 - 1
    O, I = W.shape
    Wg = W.reshape(O, I // GROUP, GROUP)
    s = Wg.abs().amax(-1, keepdim=True).clamp(min=1e-12) / q
    return (torch.clamp(torch.round(Wg / s), -q - 1, q) * s).reshape(O, I)


def subspace_mixed(W, X, rank, joint):
    """Quantize W to INT4 except a rank-r subspace kept in FP32.
    joint=False: subspace from activation covariance eigvecs (baseline).
    joint=True : weighted PCA balancing weight & activation covariances (CoQuant).
    """
    Xc = X - X.mean(0)
    Cact = Xc.T @ Xc / X.shape[0]                      # activation covariance (I,I)
    if joint:
        Gw = W.T @ W                                   # weight Gram (I,I): how input
        C = Gw @ Cact + Cact @ Gw                      # dirs are amplified by W
        C = C / 2
    else:
        C = Cact
    evals, evecs = torch.linalg.eigh(C)
    V = evecs[:, -rank:]                               # top-r directions
    P = V @ V.T
    W_hi = W @ P                                       # sensitive part, keep FP32
    W_lo = int4(W - W_hi)                              # rest quantized
    return X @ (W_hi + W_lo).T


def main():
    cfg = load_qwen3_config()
    I, O, N, rank = 256, 256, 2048, 32
    print(f"Qwen3-0.6B-style linear: {I}->{O}, FP32 subspace rank={rank}")
    W = torch.randn(O, I) * 0.05

    # Calibration activations with anisotropic structure (few heavy directions).
    basis, _ = torch.linalg.qr(torch.randn(I, I))
    scales = torch.linspace(3.0, 0.1, I)
    X = torch.randn(N, I) * scales @ basis.T

    y_ref = X @ W.T
    err_full = (X @ int4(W).T - y_ref).pow(2).mean().item()
    err_base = (subspace_mixed(W, X, rank, joint=False) - y_ref).pow(2).mean().item()
    err_co = (subspace_mixed(W, X, rank, joint=True) - y_ref).pow(2).mean().item()
    print(f"MSE full INT4:            {err_full:.6f}")
    print(f"MSE act-only subspace:    {err_base:.6f}")
    print(f"MSE CoQuant joint subspace:{err_co:.6f}")
    assert err_co <= err_base < err_full
    print("PASS: joint weight-activation subspace beats activation-only selection.")


if __name__ == "__main__":
    main()
