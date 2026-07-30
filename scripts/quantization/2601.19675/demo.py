"""Paper: LoPRo: Enhancing Low-Rank Quantization via Permuted Block-Wise Rotation (arXiv:2601.19675)

Core algorithm reproduction: low-rank + rotated residual quantization.
  W ~= L (low-rank sketch) + R (residual)
  1) R1SVD-style fast low-rank approximation of W (randomized sketch SVD).
  2) Column-wise importance of residual R (L2 norm); permute columns so that
     columns of similar importance fall into the same block (block-wise
     permutation, LoPRo's key step).
  3) The most salient column block is kept in FP16 (explicit protection).
  4) Remaining blocks are rotated with a Walsh-Hadamard transform to spread
     outliers, then quantized to 2-bit; dequantize with the inverse rotation.

Validation: real Qwen3-0.6B q_proj weight (HF cache) with mock fallback.
We compare reconstruction MSE of (L + dequant(R)) for LoPRo vs naive 2-bit
quantization of the residual without permutation/rotation.

Run: python3 demo.py
"""
import glob
import math
import os

import torch


def load_weight() -> torch.Tensor:
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


def sketch_svd(W: torch.Tensor, rank: int, iters: int = 4):
    """R1SVD-style randomized low-rank approximation via sketched power iteration."""
    m, n = W.shape
    torch.manual_seed(0)
    Omega = torch.randn(n, rank)
    Y = W @ Omega
    for _ in range(iters):
        Y = W @ (W.T @ Y)
    Q, _ = torch.linalg.qr(Y)
    B = Q.T @ W
    Ub, S, Vh = torch.linalg.svd(B, full_matrices=False)
    U = Q @ Ub
    return U * S.unsqueeze(0), Vh  # W ~= (U*S) @ Vh


def hadamard(n: int) -> torch.Tensor:
    """Walsh-Hadamard matrix of size n (n power of 2), normalized."""
    H = torch.tensor([[1.0]])
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H / math.sqrt(n)


def quant_2bit(X: torch.Tensor, scale: torch.Tensor):
    qmax = 1  # 2-bit symmetric: levels {-1, 0, 1}
    q = torch.clamp(torch.round(X / scale), -qmax, qmax)
    return q * scale


def lopro(W: torch.Tensor, rank: int = 16, block: int = 128, protect: int = 128):
    US, Vh = sketch_svd(W, rank)
    L = US @ Vh
    R = W - L
    imp = R.norm(dim=0)  # column importance
    perm = torch.argsort(imp, descending=True)
    inv = torch.empty_like(perm)
    inv[perm] = torch.arange(perm.numel())
    Rp = R[:, perm]
    n = Rp.shape[1]
    Rq = torch.zeros_like(Rp)
    for start in range(0, n, block):
        blk = Rp[:, start:start + block]
        if start < protect:
            Rq[:, start:start + block] = blk  # salient block kept FP16
            continue
        h = hadamard(blk.shape[1]) if blk.shape[1] & (blk.shape[1] - 1) == 0 else torch.eye(blk.shape[1])
        rot = blk @ h  # block-wise Walsh-Hadamard rotation
        scale = rot.abs().amax() / 1.0  # 2-bit symmetric, block scale
        Rq[:, start:start + block] = quant_2bit(rot, scale) @ h.T
    Rq = Rq[:, inv]
    return L + Rq, L, R


def naive(W: torch.Tensor, rank: int = 16):
    US, Vh = sketch_svd(W, rank)
    L = US @ Vh
    R = W - L
    scale = R.abs().amax() / 1.0
    return L + quant_2bit(R, scale), L, R


def main():
    torch.manual_seed(0)
    W = load_weight()
    W_lopro, L, R = lopro(W)
    W_naive, _, _ = naive(W)
    mse_lopro = torch.mean((W - W_lopro) ** 2).item()
    mse_naive = torch.mean((W - W_naive) ** 2).item()
    low_rank_share = torch.mean((W - L) ** 2).item() / torch.mean(W**2).item()
    print(f"[info] residual energy share after rank-16 sketch: {low_rank_share:.2%}")
    print(f"[result] recon MSE  naive 2-bit residual: {mse_naive:.6e}")
    print(f"[result] recon MSE  LoPRo (perm+Hadamard+protect): {mse_lopro:.6e}")
    imp = (mse_naive - mse_lopro) / mse_naive * 100
    print(f"[check] LoPRo reduces error by {imp:.1f}% "
          f"({'PASS' if mse_lopro < mse_naive else 'FAIL'})")


if __name__ == "__main__":
    main()
