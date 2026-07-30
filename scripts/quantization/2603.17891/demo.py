#!/usr/bin/env python3
"""
RAMP (arXiv:2603.17891) demo: 11-dim per-layer state embedding + selective
Scale Folding + budget-constrained joint W/A bit allocation with zero-shot
transfer. (The SAC policy is replaced by an embedding-derived sensitivity
ranking surrogate; pipeline structure kept.)

Mock Qwen3-0.6B (24 layers). Heterogeneous sensitivity construction:
a few "sensitive" layers have outlier activation channels; the rest have
small-magnitude weights (low output contribution, hence insensitive) —
mirroring the real-LLM observation that layer sensitivity is highly skewed.
"""
import torch
import torch.nn as nn

torch.manual_seed(0)


def state_embedding(W, X):
    """11-dim embedding: activation stats, weight properties, structural descriptors."""
    kurt = (((X - X.mean()) / X.std()) ** 4).mean().item()
    emb = [
        X.mean().item(), X.std().item(), X.abs().max().item(),          # act stats (3)
        kurt,                                                            # act kurtosis (1)
        W.abs().mean().item(), W.abs().max().item(), W.std().item(),    # weight props (3)
        float(W.shape[0]), float(W.shape[1]),                            # structural (2)
        (W.abs().max() / W.abs().mean()).item(),                         # weight outlier ratio (1)
        float((X.abs().amax(dim=0) > 3 * X.std()).float().mean().item()) # outlier channel frac (1)
    ]
    return torch.tensor(emb)


def sensitivity(feat):
    """Embedding-derived sensitivity surrogate (replaces the SAC policy):
    activation kurtosis x outlier-channel fraction x weight magnitude."""
    return feat[3] * (feat[10] + 1e-6) * feat[4]


def scale_folding(W, X, alpha=0.3):
    """Migrate activation outliers into weights via per-input-channel scaling.
    Keeps the matmul invariant: (X/s) @ (W*s).T == X @ W.T. alpha<1 balances
    the W-side cost vs X-side benefit (SmoothQuant-style migration strength)."""
    s = X.abs().amax(dim=0).clamp_min(1e-8).pow(alpha)
    s = s / s.mean()
    return W * s.unsqueeze(0), X / s


def quant(W, nbits):
    qmax = 2 ** (nbits - 1) - 1
    sc = W.abs().max().clamp_min(1e-8) / qmax
    return torch.clamp((W / sc).round(), -qmax, qmax) * sc


def quant_act(X, nbits):
    """Per-token absmax activation quantization."""
    qmax = 2 ** (nbits - 1) - 1
    sc = X.abs().amax(dim=-1, keepdim=True).clamp_min(1e-8) / qmax
    return torch.clamp((X / sc).round(), -qmax, qmax) * sc


def allocate(layers_feats, avg_budget=3.0):
    """Budgeted allocation by embedding sensitivity: top layers 4-bit,
    bottom layers 2-bit, rest 3-bit. Exact average budget preserved."""
    sens = torch.tensor([sensitivity(f) for f in layers_feats])
    order = torch.argsort(sens, descending=True).tolist()
    n = len(layers_feats)
    extra = int(round((avg_budget - 2.0) * n))  # bits above the 2-bit floor
    n_top = extra // 6                          # 4-bit layers cost 2 extra each
    n_mid = extra - 2 * n_top                   # 3-bit layers cost 1 extra each
    bits = [2] * n
    for rank, idx in enumerate(order):
        if rank < n_top:
            bits[idx] = 4
        elif rank < n_top + n_mid:
            bits[idx] = 3
    return bits, order


def evaluate(layers, Xs, bits, fold_mask, alpha=0.3):
    """Joint W{b}A{b} per-layer matmul error, summed over layers."""
    tot = 0.0
    for i, (L, X, b) in enumerate(zip(layers, Xs, bits)):
        W = L.weight.data
        if fold_mask[i]:
            W, X = scale_folding(W, X, alpha)
        tot += (quant_act(X, b) @ quant(W, b).T - X @ W.T).pow(2).mean().item()
    return tot


def make_model(n, dim, outlier_layers, outlier_frac=4):
    """Sensitive layers: outlier activation channels. Other layers: small
    weights (insensitive). Mirrors skewed layer sensitivity in real LLMs."""
    layers = nn.ModuleList([nn.Linear(dim, dim, bias=False) for _ in range(n)])
    with torch.no_grad():
        for i, L in enumerate(layers):
            if i not in outlier_layers:
                L.weight.mul_(0.3)
    Xs = []
    for i, L in enumerate(layers):
        X = torch.randn(16, dim)
        if i in outlier_layers:
            X[:, :outlier_frac] *= 8
        Xs.append(X)
    return layers, Xs


def run_pipeline(layers, Xs, tag):
    n = len(layers)
    feats = [state_embedding(L.weight.data, X) for L, X in zip(layers, Xs)]
    bits, order = allocate(feats, avg_budget=3.0)
    fold_mask = [f[10] > 0.04 for f in feats]  # fold only outlier-prone layers
    # (normal randn layers: outlier-channel frac ~= 0.02; outlier layers: >= 4/64)
    mse_u = evaluate(layers, Xs, [3] * n, [False] * n)
    mse_a = evaluate(layers, Xs, bits, [False] * n)
    mse_af = evaluate(layers, Xs, bits, fold_mask)
    print(f"[{tag}] 4-bit layers: {sorted(order[:4])}  fold layers: {[i for i, m in enumerate(fold_mask) if m]}")
    print(f"[{tag}] uniformW3A3={mse_u:.4f}  alloc={mse_a:.4f}  alloc+ScaleFolding={mse_af:.4f}  "
          f"(alloc win: {mse_a < mse_u}, fold win: {mse_af < mse_a})")
    return feats, bits, mse_u, mse_a, mse_af


def main():
    layers, Xs = make_model(24, 64, outlier_layers=(0, 5, 23))
    feats, bits, mse_u, mse_a, mse_af = run_pipeline(layers, Xs, "source-64d")
    print(f"[embed] 11-dim state embedding sample (layer0): {[round(v, 3) for v in feats[0].tolist()]}")
    print(f"[alloc] per-layer bits: {bits}  avg={sum(bits) / len(bits):.2f}  exact-budget={sum(bits) == 72}")
    assert mse_a < mse_u and mse_af < mse_a

    # zero-shot transfer: same embedding + allocation + folding on a bigger model
    layers2, Xs2 = make_model(24, 96, outlier_layers=(2, 11, 20), outlier_frac=6)
    _, _, mse_u2, mse_a2, mse_af2 = run_pipeline(layers2, Xs2, "transfer-96d")
    assert mse_af2 < mse_u2, "transferred pipeline should still beat uniform"
    print("[demo] OK")


if __name__ == "__main__":
    main()
