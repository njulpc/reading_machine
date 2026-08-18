#!/usr/bin/env python3
"""FluxBin row-column binary bases, structural saliency, and LUT reference path."""
import argparse
import itertools
from pathlib import Path

import torch

KEY = "model.layers.0.mlp.down_proj.weight"


def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path / "model.safetensors"), framework="pt", device="cpu") as f:
        return f.get_tensor(KEY)[:64, :256].float().contiguous()


def fit_bases(w, order=2, iterations=3):
    residual = w.clone()
    row_scales, col_scales, signs = [], [], []
    for _ in range(order):
        row = residual.abs().mean(1, keepdim=True).clamp_min(1e-8)
        col = torch.ones(1, w.shape[1])
        sign = residual.sign().masked_fill(residual == 0, 1)
        row_scales.append(row); col_scales.append(col); signs.append(sign)
        residual -= row * col * sign
    combos = torch.tensor(list(itertools.product([-1.0, 1.0], repeat=order)))
    for _ in range(iterations):
        magnitudes = torch.stack([row_scales[k] * col_scales[k] for k in range(order)])
        candidates = torch.einsum("ck,kij->cij", combos, magnitudes)
        choice = (candidates - w).abs().argmin(0)
        for k in range(order):
            signs[k] = combos[choice, k]
        for k in range(order):
            other = sum(row_scales[t] * col_scales[t] * signs[t] for t in range(order) if t != k)
            target = w - other
            rc = col_scales[k] * signs[k]
            row_scales[k] = ((rc * target).sum(1, keepdim=True) / rc.square().sum(1, keepdim=True).clamp_min(1e-8)).abs().clamp_min(1e-8)
            rr = row_scales[k] * signs[k]
            col_scales[k] = ((rr * target).sum(0, keepdim=True) / rr.square().sum(0, keepdim=True).clamp_min(1e-8)).abs().clamp_min(1e-8)
    approx = sum(row_scales[k] * col_scales[k] * signs[k] for k in range(order))
    return approx, list(zip(signs, row_scales, col_scales))


def lut_binary_mm(x, signs, row_scale, col_scale, group=8):
    x = x * col_scale
    batch, out = x.shape[0], signs.shape[0]
    y = torch.zeros(batch, out)
    powers = (1 << torch.arange(group)).long()
    ids = torch.arange(1 << group)
    patterns_table = (2 * ((ids[:, None] >> torch.arange(group)) & 1) - 1).float()
    for start in range(0, x.shape[1], group):
        chunk = x[:, start:start + group]
        sg = signs[:, start:start + group]
        if chunk.shape[1] < group:
            pad = group - chunk.shape[1]
            chunk = torch.nn.functional.pad(chunk, (0, pad))
            sg = torch.nn.functional.pad(sg, (0, pad), value=1)
        patterns = ((sg > 0).long() * powers).sum(1)
        y += (chunk @ patterns_table.T)[:, patterns]
    return y * row_scale.T


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--group-size", type=int, default=128)
    p.add_argument("--base-order", type=int, default=2)
    p.add_argument("--salient-columns", type=int, default=8)
    p.add_argument("--seed", type=int, default=9)
    a = p.parse_args(); torch.manual_seed(a.seed)
    w = load_weight(a.model_dir); x = torch.randn(256, w.shape[1])
    h = 2 * x.T @ x + 1e-3 * torch.eye(w.shape[1])
    h_inv = torch.linalg.inv(h)
    approx = torch.zeros_like(w); components = []
    salient_mask = torch.zeros(w.shape[1], dtype=torch.bool)
    for start in range(0, w.shape[1], a.group_size):
        end = min(start + a.group_size, w.shape[1]); block = w[:, start:end]
        base, bases = fit_bases(block, a.base_order)
        diag = h_inv.diag()[start:end]
        score = block.square().sum(0) / diag.square().clamp_min(1e-12)
        count = min(a.salient_columns, end - start)
        selected = torch.topk(score, count).indices
        mask = torch.zeros(end - start, dtype=torch.bool); mask[selected] = True
        refinement, refine_bases = fit_bases((block - base)[:, mask], a.base_order)
        base[:, mask] += refinement
        approx[:, start:end] = base; salient_mask[start:end] = mask
        components.append((start, end, bases, mask, refine_bases))
    y_lut = torch.zeros(x.shape[0], w.shape[0])
    for start, end, bases, mask, refine_bases in components:
        for signs, row, col in bases:
            y_lut += lut_binary_mm(x[:, start:end], signs, row, col)
        for signs, row, col in refine_bases:
            y_lut += lut_binary_mm(x[:, start:end][:, mask], signs, row, col)
    direct = x @ approx.T; ref = x @ w.T
    assert torch.allclose(y_lut, direct, atol=1e-4, rtol=1e-4)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} group={a.group_size} base_order={a.base_order}")
    print(f"salient_column_fraction={salient_mask.float().mean().item():.6f} output_mse={torch.nn.functional.mse_loss(y_lut, ref).item():.8g}")
    print("row_column_group8_lut_equivalence=PASS")


if __name__ == "__main__":
    main()
