#!/usr/bin/env python3
"""
PolarQuant (arXiv:2603.29078) demo: block-wise hypersphere normalization +
Walsh-Hadamard rotation + Gaussian-matched centroid quantization.
Target: Qwen3-0.6B (falls back to an isomorphic tiny mock model).
"""
import math
import torch
import torch.nn as nn

torch.manual_seed(0)


def try_load_qwen3():
    try:
        from transformers import AutoModelForCausalLM
        m = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", local_files_only=True)
        print("[model] loaded real Qwen3-0.6B from local cache")
        return m
    except Exception as e:
        print(f"[model] Qwen3-0.6B unavailable ({type(e).__name__}); using isomorphic mock")
        return None


class MockBlock(nn.Module):
    """Qwen3-0.6B-shaped decoder block (scaled down depth for demo)."""

    def __init__(self, hidden=896, heads=14, kv_heads=2, ffn=4864 // 16):
        super().__init__()
        self.q_proj = nn.Linear(hidden, hidden, bias=False)
        self.k_proj = nn.Linear(hidden, hidden * kv_heads // heads, bias=False)
        self.v_proj = nn.Linear(hidden, hidden * kv_heads // heads, bias=False)
        self.o_proj = nn.Linear(hidden, hidden, bias=False)
        self.gate_proj = nn.Linear(hidden, ffn, bias=False)
        self.up_proj = nn.Linear(hidden, ffn, bias=False)
        self.down_proj = nn.Linear(ffn, hidden, bias=False)


# ---------------- PolarQuant core ----------------

def hadamard_matrix(n, device):
    """(Scaled) Walsh-Hadamard matrix, n must be power of two."""
    H = torch.ones(1, 1, device=device)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H / math.sqrt(n)


def next_pow2(n):
    p = 1
    while p < n:
        p *= 2
    return p


def polar_quantize(W, nbits=5, block=64, rotate=True):
    """PolarQuant 3-stage pipeline. Returns dequantized W and stats."""
    dev = W.device
    orig_shape = W.shape
    Wf = W.reshape(-1, W.shape[-1]).float()
    n_cols = Wf.shape[1]
    pad = (block - n_cols % block) % block
    Wp = torch.nn.functional.pad(Wf, (0, pad))
    # stage 1: block-wise normalize to unit hypersphere
    blocks = Wp.reshape(Wp.shape[0], -1, block)
    norms = blocks.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    X = blocks / norms
    # stage 2: Hadamard rotation
    H = hadamard_matrix(next_pow2(block), dev)[:block, :block]
    Xr = X @ H if rotate else X
    # stage 3: Gaussian-matched centroid quantization (Lloyd on N(0,1) grid, precomputed)
    levels = 2 ** nbits
    # Gaussian-optimal-ish centroids: quantiles of N(0,1) at (i+0.5)/L
    q = (torch.arange(levels, device=dev).float() + 0.5) / levels
    cent = torch.erfinv(2 * q - 1) * math.sqrt(2.0) * (1.0 / math.sqrt(block))
    dist = (Xr.unsqueeze(-1) - cent).abs()
    idx = dist.argmin(-1)
    Xq = cent[idx]
    # dequantize
    Xdq = Xq @ H.T if rotate else Xq
    Wdq = (Xdq * norms).reshape(Wp.shape)[:, :n_cols].reshape(orig_shape)
    mse = (Wdq - W).pow(2).mean().item()
    return Wdq.to(W.dtype), mse, Xr


def kurtosis(x):
    x = x.flatten().float()
    m, s = x.mean(), x.std()
    return (((x - m) / s) ** 4).mean().item()


def main():
    model = try_load_qwen3()
    if model is not None:
        linears = {n: p for n, p in model.named_parameters() if "proj" in n and p.dim() == 2}
    else:
        blk = MockBlock()
        linears = {n: p.detach() for n, p in blk.named_parameters()}

    print(f"[demo] {len(linears)} weight matrices")
    tot_r, tot_nr = 0.0, 0.0
    for i, (name, W) in enumerate(linears.items()):
        if i >= 4:
            break
        W = W.data
        _, mse_r, Xr = polar_quantize(W, nbits=5, rotate=True)
        _, mse_nr, _ = polar_quantize(W, nbits=5, rotate=False)
        tot_r += mse_r
        tot_nr += mse_nr
        print(f"  {name:30s} kurt(before)={kurtosis(W):7.2f} kurt(rotated)={kurtosis(Xr):6.2f} "
              f"MSE(rot)={mse_r:.3e} MSE(no-rot)={mse_nr:.3e}")
    gain = 100 * (1 - tot_r / max(tot_nr, 1e-12))
    print(f"[ablation] Hadamard rotation accounts for {gain:.1f}% of MSE reduction "
          f"(paper reports 98% of quality gain from rotation)")
    print("[demo] OK")


if __name__ == "__main__":
    main()
