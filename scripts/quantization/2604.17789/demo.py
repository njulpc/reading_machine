"""DuQuant++ (arXiv:2604.17789): outlier-aware block-aligned rotation for
MXFP4 microscaling quantization — reference reproduction.

MXFP4: blocks of 32 elements share one power-of-two (E8M0) scale; each
element stored as a 4-bit grid value. One outlier inflates the shared scale
of its whole block. A rotation aligned to the 32-element block spreads
outlier energy and restores effective dynamic range.
"""
import math
import torch

torch.manual_seed(0)
BLOCK = 32


def load_qwen3_config():
    try:
        from huggingface_hub import hf_hub_download
        import json
        with open(hf_hub_download("Qwen/Qwen3-0.6B", "config.json")) as f:
            return json.load(f)
    except Exception:
        return {"hidden_size": 1024, "intermediate_size": 3072}


def mxfp4_quant(x):
    """Simulate MXFP4: per-32-block shared pow2 scale + 4-bit uniform elements."""
    *lead, C = x.shape
    assert C % BLOCK == 0
    xb = x.reshape(*lead, C // BLOCK, BLOCK)
    amax = xb.abs().amax(dim=-1, keepdim=True).clamp(min=1e-12)
    scale = torch.exp2(torch.ceil(torch.log2(amax / 7.0)))  # E8M0: pow-of-2
    q = torch.clamp(torch.round(xb / scale), -8, 7)
    return (q * scale).reshape(x.shape)


def hadamard(n):
    h = torch.tensor([[1.0]])
    while h.shape[0] < n:
        h = torch.cat([torch.cat([h, h], 1), torch.cat([h, -h], 1)], 0)
    return h / math.sqrt(n)


def outlier_aware_rotation(x, outlier_ratio=0.02):
    """DuQuant-style rotation: permute so outliers spread across blocks, then
    apply a per-block Hadamard (single rotation, block-aligned B=32)."""
    C = x.shape[-1]
    energy = x.pow(2).mean(dim=tuple(range(x.dim() - 1)))
    order = torch.argsort(energy, descending=True)
    n_out = max(1, int(C * outlier_ratio))
    # Interleave high-energy channels evenly across blocks.
    perm = torch.empty(C, dtype=torch.long)
    out_idx, rest_idx = order[:n_out], order[n_out:]
    n_blocks = C // BLOCK
    pos = torch.arange(n_out) % n_blocks * BLOCK  # one outlier per block start
    perm[pos] = out_idx
    mask = torch.ones(C, dtype=torch.bool)
    mask[pos] = False
    perm[mask] = rest_idx
    H = hadamard(BLOCK)
    R = torch.zeros(C, C)
    for b in range(n_blocks):
        R[b * BLOCK:(b + 1) * BLOCK, b * BLOCK:(b + 1) * BLOCK] = H
    P = torch.eye(C)[perm]          # permutation matrix
    return R @ P                    # single fused rotation


def main():
    cfg = load_qwen3_config()
    C = cfg["hidden_size"]
    tokens = 256
    print(f"Qwen3-0.6B hidden_size={C}")

    # Activation with outlier channels (~2% channels 20x larger), as in LLMs.
    x = torch.randn(tokens, C)
    out_ch = torch.rand(C) < 0.02
    x[:, out_ch] *= 20.0
    W = torch.randn(C, cfg["intermediate_size"]) / math.sqrt(C)

    y_ref = x @ W
    y_naive = mxfp4_quant(x) @ W

    R = outlier_aware_rotation(x)
    x_rot = x @ R.T
    W_rot = R @ W                    # fold rotation into weights (offline)
    y_duq = mxfp4_quant(x_rot) @ W_rot

    mse_n = (y_naive - y_ref).pow(2).mean().item()
    mse_d = (y_duq - y_ref).pow(2).mean().item()
    print(f"layer-output MSE: naive MXFP4={mse_n:.6f}  DuQuant++-style={mse_d:.6f}")
    print(f"error reduction: {mse_n / max(mse_d, 1e-12):.2f}x")
    assert mse_d < mse_n
    print("PASS: single block-aligned outlier-aware rotation improves MXFP4.")


if __name__ == "__main__":
    main()
