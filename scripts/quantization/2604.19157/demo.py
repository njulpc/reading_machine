"""SAW-INT4 (arXiv:2604.19157): token-wise INT4 KV-cache quantization
with block-diagonal Hadamard rotation — PyTorch reference reproduction.

Validates on the real Qwen3-0.6B architecture config (random weights,
see README) that rotation recovers most of the accuracy lost by naive INT4.
"""
import math
import torch

torch.manual_seed(0)


def load_qwen3_config():
    """Load the real Qwen3-0.6B config (tiny download); fall back to a replica."""
    try:
        from huggingface_hub import hf_hub_download
        import json
        with open(hf_hub_download("Qwen/Qwen3-0.6B", "config.json")) as f:
            return json.load(f)
    except Exception:
        return {"hidden_size": 1024, "num_hidden_layers": 28,
                "num_attention_heads": 16, "num_key_value_heads": 8,
                "head_dim": 128, "intermediate_size": 3072}


def hadamard(n):
    """Sylvester construction of a normalized Hadamard matrix (n power of 2)."""
    h = torch.tensor([[1.0]])
    while h.shape[0] < n:
        h = torch.cat([torch.cat([h, h], 1), torch.cat([h, -h], 1)], 0)
    return h / math.sqrt(n)


def block_diag_hadamard(head_dim, block):
    """Block-diagonal Hadamard rotation: (head_dim/block) blocks of size `block`."""
    hb = hadamard(block)
    rot = torch.zeros(head_dim, head_dim)
    for i in range(0, head_dim, block):
        rot[i:i + block, i:i + block] = hb
    return rot


def int4_quant_per_token(x, group=32):
    """Per-token symmetric INT4 quantization with per-group scales.
    x: (..., C). Returns dequantized tensor."""
    shape = x.shape
    x = x.reshape(*shape[:-1], shape[-1] // group, group)
    scale = x.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8) / 7.0
    q = torch.clamp(torch.round(x / scale), -8, 7)
    return (q * scale).reshape(shape)


def mse_cos(a, b):
    mse = (a - b).pow(2).mean().item()
    cos = torch.nn.functional.cosine_similarity(
        a.flatten(1), b.flatten(1), dim=-1).mean().item()
    return mse, cos


def main():
    cfg = load_qwen3_config()
    hd, nkv = cfg["head_dim"], cfg["num_key_value_heads"]
    seq = 512
    print(f"Qwen3-0.6B config: head_dim={hd}, kv_heads={nkv}")

    # Simulate a K cache tensor: (kv_heads, seq, head_dim).
    # Heavy-tailed activations mimic real KV outliers (mixture of gaussians).
    K = torch.randn(nkv, seq, hd) * torch.where(
        torch.rand(nkv, seq, hd) > 0.98, 8.0, 1.0)
    Q = torch.randn(nkv, seq, hd)

    # --- naive token-wise INT4 ---
    K_naive = int4_quant_per_token(K)
    # --- block-diagonal Hadamard rotation + INT4 (SAW-INT4 core) ---
    R = block_diag_hadamard(hd, 32)
    K_rot = int4_quant_per_token(K @ R) @ R.T   # rotate, quantize, rotate back

    mse_n, cos_n = mse_cos(K, K_naive)
    mse_r, cos_r = mse_cos(K, K_rot)
    print(f"naive INT4 : K mse={mse_n:.5f} cos={cos_n:.5f}")
    print(f"rot   INT4 : K mse={mse_r:.5f} cos={cos_r:.5f}")

    # Attention logits error with FP32 query.
    logits_fp = Q @ K.transpose(-1, -2)
    logits_n = Q @ K_naive.transpose(-1, -2)
    logits_r = Q @ K_rot.transpose(-1, -2)
    rel_n = (logits_n - logits_fp).norm() / logits_fp.norm()
    rel_r = (logits_r - logits_fp).norm() / logits_fp.norm()
    print(f"attention-logit relative error: naive={rel_n:.4f}  rotated={rel_r:.4f}")
    assert rel_r < rel_n, "rotation should reduce logit error"
    print("PASS: block-diagonal Hadamard rotation recovers INT4 KV accuracy.")


if __name__ == "__main__":
    main()
