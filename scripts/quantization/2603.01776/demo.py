#!/usr/bin/env python3
"""
FreeAct (arXiv:2603.01776) demo: token-type-specific activation transforms
(decoupled from weights via activation rank deficiency) for quantization.
Mock Qwen3-0.6B-shaped linear layer with heterogeneous (vision/text) tokens.
"""
import torch

torch.manual_seed(0)


def quant_act(X, nbits=4):
    qmax = 2 ** (nbits - 1) - 1
    s = X.abs().amax(dim=-1, keepdim=True).clamp_min(1e-8) / qmax
    return torch.clamp((X / s).round(), -qmax, qmax) * s


def smooth_transform(X, iters=50, lr=0.05):
    """Learn a diagonal per-channel transform T that smooths activation outliers.
    FreeAct insight: since activations are rank-deficient, T need NOT be tied
    to the weight-side transform -> solve T only for activation smoothness."""
    T = torch.ones(X.shape[-1], requires_grad=True)
    opt = torch.optim.Adam([T], lr=lr)
    for _ in range(iters):
        opt.zero_grad()
        Xs = X * T
        loss = Xs.abs().amax(dim=-1).mean() / Xs.abs().mean().clamp_min(1e-8)  # peak/mean ratio
        loss.backward()
        opt.step()
    return T.detach()


def main():
    D = 896
    W = torch.randn(D, D) * 0.02
    # two token types with distinct distributions (vision vs text)
    X_vis = torch.randn(64, D) * 1.0
    X_vis[:, : D // 16] *= 8.0                      # vision: outliers in early channels
    X_txt = torch.randn(192, D) * 0.7
    X_txt[:, -D // 16:] *= 8.0                      # text: outliers in late channels
    X = torch.cat([X_vis, X_txt], 0)

    # rank deficiency check
    sv = torch.linalg.svdvals(X)
    erank = (sv.sum() ** 2 / (sv ** 2).sum()).item()
    print(f"[rank] effective rank of activations = {erank:.1f} / {D} (rank-deficient)")

    def output_mse(T_vis, T_txt, T_w):
        Y0 = X @ W.T
        Xv = quant_act(X_vis * T_vis) / T_vis
        Xt = quant_act(X_txt * T_txt) / T_txt
        Xq = torch.cat([Xv, Xt], 0)
        Wq = quant_act(W * T_w) / T_w
        return (Xq @ Wq.T - Y0).pow(2).mean().item()

    one = torch.ones(D)
    # static one-to-one baseline: single shared transform for all tokens
    T_shared = smooth_transform(X)
    mse_static = output_mse(T_shared, T_shared, T_shared)
    # FreeAct: per-token-type activation transforms, unified static weight transform
    Tv = smooth_transform(X_vis)
    Tt = smooth_transform(X_txt)
    mse_free = output_mse(Tv, Tt, one)
    # no-transform baseline
    mse_none = output_mse(one, one, one)
    print(f"[mse] no-transform={mse_none:.4f}  static-shared={mse_static:.4f}  "
          f"FreeAct(per-type act + unified W)={mse_free:.4f}")
    print(f"[gain] FreeAct vs static: {100*(1-mse_free/mse_static):.1f}% MSE reduction; "
          f"vs none: {100*(1-mse_free/mse_none):.1f}%")
    assert mse_free < mse_static
    print("[demo] OK")


if __name__ == "__main__":
    main()
