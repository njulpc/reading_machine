#!/usr/bin/env python3
"""PRQ-KMeans fitting and frozen-codebook encoding on Qwen3 embeddings."""
import argparse
import glob
import os

import torch
import torch.nn.functional as F


def ckpt(path=None):
    hits = [path] if path else glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
    ))
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B checkpoint missing")
    return hits[0]


def normalize(x):
    return F.normalize(x, p=2, dim=-1, eps=1e-12)


def remove_component(x, direction):
    denom = direction.square().sum(-1, keepdim=True).clamp_min(1e-12)
    return x - (x * direction).sum(-1, keepdim=True) / denom * direction


def refine_centroids(x, count, top_k, beta, iterations, generator):
    # Algorithm 1 samples current residuals rather than taking evenly spaced rows.
    centroids = x[torch.randperm(len(x), generator=generator)[:count]].clone()
    for _ in range(iterations):
        similarity = normalize(x) @ normalize(centroids).T
        values, indices = similarity.topk(min(top_k, count), dim=1)
        local_weights = torch.softmax(beta * values, dim=1)
        weights = torch.zeros_like(similarity).scatter(1, indices, local_weights)
        totals = weights.sum(0)
        updated = weights.T @ x / totals[:, None].clamp_min(1e-12)
        centroids = torch.where((totals > 0)[:, None], updated, centroids)
    assignment = (normalize(x) @ normalize(centroids).T).argmax(1)
    return centroids, assignment


def fit_prq(x, levels, codebook_size, top_k, beta, iterations, seed):
    normalized = normalize(x)
    global_mean = normalized.mean(0, keepdim=True)
    residual = normalize(remove_component(normalized, global_mean))
    generator = torch.Generator().manual_seed(seed)
    codebooks, fit_codes, orthogonality = [], [], []
    for level in range(levels):
        centroids, assignment = refine_centroids(
            residual, codebook_size, top_k, beta, iterations, generator
        )
        chosen = centroids[assignment]
        codebooks.append(centroids)
        fit_codes.append(assignment)
        if level + 1 < levels:
            projected = remove_component(residual, chosen)
            orthogonality.append(float((projected * chosen).sum(1).abs().mean()))
            residual = normalize(projected)
    return global_mean, codebooks, torch.stack(fit_codes, 1), orthogonality


def encode_prq(x, global_mean, codebooks):
    residual = normalize(remove_component(normalize(x), global_mean))
    codes = []
    for level, centroids in enumerate(codebooks):
        assignment = (normalize(residual) @ normalize(centroids).T).argmax(1)
        codes.append(assignment)
        if level + 1 < len(codebooks):
            residual = normalize(remove_component(residual, centroids[assignment]))
    return torch.stack(codes, 1)


def self_test():
    g = torch.Generator().manual_seed(7)
    x = torch.randn(64, 16, generator=g)
    mean, books, fit_codes, carry = fit_prq(x, 3, 8, 2, 15.0, 4, 7)
    assert torch.equal(fit_codes, encode_prq(x, mean, books))
    assert max(carry) < 1e-5


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--samples", type=int, default=512)
    parser.add_argument("--levels", type=int, default=3)
    parser.add_argument("--codebook-size", type=int, default=16)
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--beta", type=float, default=15.0)
    parser.add_argument("--iterations", type=int, default=8)
    args = parser.parse_args()
    self_test()

    from safetensors import safe_open
    with safe_open(ckpt(args.checkpoint), framework="pt", device="cpu") as handle:
        key = next(k for k in handle.keys() if k.endswith("embed_tokens.weight"))
        x = handle.get_tensor(key)[:args.samples].float()

    mean, books, fit_codes, carry = fit_prq(
        x, args.levels, args.codebook_size, args.top_k, args.beta,
        args.iterations, seed=24207,
    )
    encoded = encode_prq(x, mean, books)
    unique = len(torch.unique(encoded, dim=0))
    bits = args.levels * torch.log2(torch.tensor(float(args.codebook_size)))
    print(
        f"embedding={key} samples={args.samples} levels={args.levels} "
        f"K={args.codebook_size} top_k={args.top_k} beta={args.beta:g} "
        f"bits_per_sid={float(bits):.1f}"
    )
    print(
        "projection_carry=" + ",".join(f"{value:.3e}" for value in carry)
        + f" unique_sids={unique} fit_encode_equal={torch.equal(fit_codes, encoded)}"
    )
    assert torch.equal(fit_codes, encoded)
    assert not carry or max(carry) < 1e-4
    assert unique > 1


if __name__ == "__main__":
    main()
