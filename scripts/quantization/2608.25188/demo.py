#!/usr/bin/env python3
"""Transform/format co-design test on a real Qwen3-0.6B weight tile."""
import argparse
import glob
import os

import torch


E2M1 = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])


def checkpoint(arg=None):
    if arg:
        return arg
    hits = glob.glob('/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors')
    hits += glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not hits:
        raise FileNotFoundError('Pass --checkpoint')
    return hits[0]


def fwht(x):
    y = x.float().clone()
    n = y.shape[-1]
    if n & (n - 1):
        raise ValueError('last dimension must be a power of two')
    h = 1
    while h < n:
        shape = y.shape[:-1] + (-1, 2, h)
        z = y.reshape(shape)
        a, b = z[..., 0, :].clone(), z[..., 1, :].clone()
        z[..., 0, :], z[..., 1, :] = a + b, a - b
        y = z.reshape_as(y)
        h *= 2
    return y / n ** 0.5


def int4_group(x, group=128):
    flat = x.flatten()
    blocks = flat.view(-1, group)
    scale = blocks.abs().amax(1, keepdim=True).clamp_min(1e-12) / 7
    return (blocks / scale).round().clamp(-7, 7).mul(scale).view_as(x)


def mxfp4_group(x, group=32, qmax=7.25):
    flat = x.flatten(); blocks = flat.view(-1, group)
    maximum = blocks.abs().amax(1, keepdim=True).clamp_min(1e-30)
    power = torch.ceil(torch.log2(maximum / qmax))
    scale = torch.pow(2.0, power)
    norm = blocks / scale
    mag = norm.abs()
    idx = (mag[..., None] - E2M1).abs().argmin(-1)
    return (E2M1[idx] * norm.sign() * scale).view_as(x)


def metric(label, x, q):
    mse = (x - q).square().mean().item()
    rel = (x - q).norm().div(x.norm()).item()
    print(f'{label}_mse={mse:.10e} {label}_relative_l2={rel:.8f}')
    return mse


def main():
    p = argparse.ArgumentParser(); p.add_argument('--checkpoint'); p.add_argument('--size', type=int, default=1024)
    args = p.parse_args()
    from safetensors import safe_open
    with safe_open(checkpoint(args.checkpoint), framework='pt', device='cpu') as f:
        key = next(k for k in f.keys() if k.endswith('layers.0.self_attn.q_proj.weight'))
        w = f.get_tensor(key).float()[:args.size, :args.size].contiguous()
    if w.shape[1] & (w.shape[1]-1):
        raise ValueError('size must select a power-of-two input dimension')
    rotated = fwht(w)
    recovered = fwht(rotated)
    assert torch.allclose(w, recovered, atol=2e-6, rtol=2e-6)
    raw_peak = w.abs().view(-1, 128).amax(1).mean().item()
    rot_peak = rotated.abs().view(-1, 128).amax(1).mean().item()
    print(f'weight={key} tile={tuple(w.shape)} raw_group_peak_mean={raw_peak:.8f} rotated_group_peak_mean={rot_peak:.8f}')
    raw_i = metric('raw_int4', w, int4_group(w))
    rot_i = metric('rotated_int4', rotated, int4_group(rotated))
    raw_m = metric('raw_mxfp4', w, mxfp4_group(w))
    rot_m = metric('rotated_mxfp4', rotated, mxfp4_group(rotated))
    print(f'int4_rotation_mse_ratio={rot_i/raw_i:.8f} mxfp4_rotation_mse_ratio={rot_m/raw_m:.8f}')
    assert torch.isfinite(torch.tensor([raw_i, rot_i, raw_m, rot_m])).all()


if __name__ == '__main__':
    main()
