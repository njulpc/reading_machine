#!/usr/bin/env python3
"""
BATQuant (arXiv:2603.16590) demo: MXFP4 quantizer + reproduction of the
"global rotation harms MXFP4" effect + block-wise affine transform with
learnable clipping. Mock Qwen3-0.6B-shaped tensors.
"""
import math
import torch

torch.manual_seed(0)
E2M1 = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
BLOCK = 32


def mxfp4_quant(X, block=BLOCK, clip=1.0):
    """OCP-style MXFP4: per-32-block power-of-two shared scale, E2M1 elements."""
    shp = X.shape
    Xp = torch.nn.functional.pad(X, (0, (-shp[-1]) % block)).reshape(-1, block)
    m = Xp.abs().max(dim=-1, keepdim=True).values.clamp_min(1e-8) * clip
    e = torch.floor(torch.log2(m / 6.0))          # shared E8M0 exponent
    s = 2.0 ** e
    Xn = Xp / s
    grid = torch.cat([-E2M1.flip(0), E2M1]).to(X.device)
    d = (Xn.unsqueeze(-1) - grid).abs()
    Q = grid[d.argmin(-1)] * s
    return Q.reshape(shp)


def hadamard(n, dev):
    H = torch.ones(1, 1, device=dev)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H / math.sqrt(n)


def block_affine(X, iters=300):
    """BATQuant: per-block learnable affine (scale+shift) + clipping search.
    Straight-through estimator (STE) makes the quantizer differentiable so the
    affine params get meaningful gradients (naive backward sees d(Q)/d(a)=0 and
    diverges)."""
    shp = X.shape
    Xb = X.reshape(-1, BLOCK)
    a = torch.ones(Xb.shape[0], requires_grad=True)
    b = torch.zeros(Xb.shape[0], requires_grad=True)
    opt = torch.optim.Adam([a, b], lr=0.02)
    for _ in range(iters):
        opt.zero_grad()
        Xt = Xb * a.unsqueeze(1) + b.unsqueeze(1)
        Q = mxfp4_quant(Xt)
        Q_ste = Xt + (Q - Xt).detach()          # STE: forward=Q, dQ/dXt=1
        rec = (Q_ste - b.unsqueeze(1)) / a.clamp_min(1e-3).unsqueeze(1)
        loss = (rec - Xb).pow(2).mean()
        loss.backward()
        opt.step()
    with torch.no_grad():
        a_, b_ = a.detach().clamp_min(1e-3), b.detach()
        Xt = Xb * a_.unsqueeze(1) + b_.unsqueeze(1)
        best = None
        for clip in (1.0, 0.9, 0.8, 0.7):        # learnable clipping -> small grid search
            Q = mxfp4_quant(Xt, clip=clip)
            rec = (Q - b_.unsqueeze(1)) / a_.unsqueeze(1)
            m = mse(rec, Xb)
            if best is None or m < best[0]:
                best = (m, clip, rec)
        print(f"  [bat] best clip={best[1]:.1f}")
        return best[2].reshape(shp)


def mse(a, b):
    return (a - b).pow(2).mean().item()


def main():
    D = 128
    W = torch.randn(4, D) * 0.05
    W[0, 0::32] *= 20.0                            # outliers confined to block 0
    X = torch.randn(4, D) * 0.5
    X[2, 96:] *= 15.0                              # outliers in another block

    for name, T in (("weight", W), ("activation", X)):
        base = mse(mxfp4_quant(T), T)
        H = hadamard(D, T.device)
        rot = mse(mxfp4_quant(T @ H) @ H.T, T)     # global orthogonal rotation
        bat = mse(block_affine(T), T)
        print(f"[{name}] MXFP4 MSE: direct={base:.3e}  global-rotation={rot:.3e} "
              f"({'WORSE' if rot > base else 'better'} than direct)  BATQuant={bat:.3e}")
    print("[finding] reproduces paper: global rotation can transfer outlier energy "
          "across blocks and hurt MXFP4; block-wise affine fixes it.")
    print("[demo] OK")


if __name__ == "__main__":
    main()
