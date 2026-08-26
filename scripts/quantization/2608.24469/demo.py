#!/usr/bin/env python3
"""Kronecker-structured ternary multiplicative adaptation on a Qwen3 tile."""
import argparse
import glob
import os

import torch


def ckpt(path=None):
    hits = [path] if path else glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
    ))
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B checkpoint missing")
    return hits[0]


def ternary_ste(x):
    # The paper obtains ternary factors from real proxies using an abs-mean
    # threshold but does not bind its multiplier; 0.7 is an engineering choice.
    threshold = 0.7 * x.detach().abs().mean().clamp_min(1e-12)
    hard = torch.where(
        x > threshold, torch.ones_like(x),
        torch.where(x < -threshold, -torch.ones_like(x), torch.zeros_like(x)),
    )
    return x + (hard - x).detach()


def ternarize_weight(w):
    # Qwen is not a pretrained ternary backbone. This abs-mean PTQ is only a
    # structural transfer used to exercise the paper's merge algebra.
    scale = 1.5 * w.abs().mean(1, keepdim=True).clamp_min(1e-12)
    return torch.round(w / scale).clamp(-1, 1)


def factor_shapes(rows, cols, p, q):
    if rows % p or cols % q:
        raise ValueError("factor dimensions must divide the weight tile")
    return (p, q), (rows // p, cols // q)


def self_test():
    a = torch.tensor([[1.0, -1.0], [0.0, 1.0]])
    b = torch.tensor([[1.0, 0.0], [-1.0, 1.0]])
    mask = torch.kron(a, b)
    assert mask.shape == (4, 4)
    assert set(torch.unique(mask).tolist()) <= {-1.0, 0.0, 1.0}
    base = torch.tensor([[1.0, 0.0, -1.0, 1.0]]).repeat(4, 1)
    assert set(torch.unique(base * mask).tolist()) <= {-1.0, 0.0, 1.0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--tile", type=int, default=128)
    parser.add_argument("--factor-p", type=int, default=16)
    parser.add_argument("--factor-q", type=int, default=16)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--lr", type=float, default=0.03)
    args = parser.parse_args()
    self_test()

    from safetensors import safe_open
    with safe_open(ckpt(args.checkpoint), framework="pt", device="cpu") as handle:
        key = next(k for k in handle.keys() if k.endswith("q_proj.weight"))
        w = handle.get_tensor(key)[:args.tile, :args.tile].float()

    base = ternarize_weight(w)
    shape_a, shape_b = factor_shapes(*base.shape, args.factor_p, args.factor_q)
    generator = torch.Generator().manual_seed(24469)
    true_a = torch.randint(-1, 2, shape_a, generator=generator).float()
    true_b = torch.randint(-1, 2, shape_b, generator=generator).float()
    target_mask = torch.kron(true_a, true_b)
    target = base * target_mask

    # A perturbed identity-style start keeps the initial merged layer close to
    # the ternary backbone while breaking symmetry between factor entries.
    proxy_a = (torch.ones(shape_a) + 0.05 * torch.randn(shape_a, generator=generator)).requires_grad_()
    proxy_b = (torch.ones(shape_b) + 0.05 * torch.randn(shape_b, generator=generator)).requires_grad_()
    optimizer = torch.optim.AdamW([proxy_a, proxy_b], lr=args.lr, weight_decay=0.0)
    initial_mask = torch.kron(ternary_ste(proxy_a), ternary_ste(proxy_b)).detach()
    initial = float((base * initial_mask - target).square().mean())
    for _ in range(args.steps):
        optimizer.zero_grad()
        mask = torch.kron(ternary_ste(proxy_a), ternary_ste(proxy_b))
        loss = (base * mask - target).square().mean()
        loss.backward()
        optimizer.step()

    factor_a = ternary_ste(proxy_a).detach()
    factor_b = ternary_ste(proxy_b).detach()
    hard_mask = torch.kron(factor_a, factor_b)
    merged = base * hard_mask
    values = sorted(float(value) for value in torch.unique(merged))
    trainable = proxy_a.numel() + proxy_b.numel()
    final = float((merged - target).square().mean())
    print(
        f"weight={key} tile={args.tile} factors={tuple(shape_a)}x{tuple(shape_b)} "
        f"trainable={trainable} dense_update={w.numel()}"
    )
    print(
        f"initial_mse={initial:.6f} final_mse={final:.6f} "
        f"merged_values={values} mask_rank={int(torch.linalg.matrix_rank(hard_mask))}"
    )
    assert set(values) <= {-1.0, 0.0, 1.0}
    assert trainable < w.numel()
    assert final < initial


if __name__ == "__main__":
    main()
