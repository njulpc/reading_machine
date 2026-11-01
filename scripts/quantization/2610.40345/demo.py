"""H_Z-PTQ equations 12--17 on a real Qwen3-0.6B projection component.

This is a CPU numerical experiment, not whole-model compression. It collects
sampled-label output gradients through the full model, then quantizes a 128x64
submatrix. See README for the difference from the paper's calibration budget.
"""
import argparse
import json
import platform
import time
from pathlib import Path

import torch
import torch.nn.functional as F

REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
TEXTS = [
    "A scientific experiment compares predictions with observations and measures uncertainty.",
    "The engineer measures memory usage and numerical error before deploying a model.",
    "A traveler follows the river through a quiet village to reach the railway station.",
    "The garden contains many flowers and trees that grow under different conditions.",
]


def regularize(a):
    a = (a + a.T) / 2
    # Explicit numerical deviation: tiny calibration requires a positive floor.
    return a + torch.eye(len(a), dtype=a.dtype) * max(a.diag().mean().item() * .01, 1e-12)


def power(a, exponent):
    values, vectors = torch.linalg.eigh((a + a.T) / 2)
    return (vectors * values.clamp_min(1e-16).pow(exponent)) @ vectors.T


def hadamard(n):
    assert n > 0 and n & (n - 1) == 0
    h = torch.ones((1, 1), dtype=torch.float64)
    while len(h) < n:
        h = torch.cat([torch.cat([h, h], 1), torch.cat([h, -h], 1)], 0)
    return h / n ** .5


def block_ldl(a, block):
    """A=L D L^T, with full matrix-valued diagonal blocks."""
    n = len(a)
    assert n % block == 0
    lower = torch.eye(n, dtype=a.dtype)
    diagonal = torch.zeros_like(a)
    for j in range(0, n, block):
        sl = slice(j, j + block)
        prev = lower[sl, :j]
        diagonal[sl, sl] = a[sl, sl] - prev @ diagonal[:j, :j] @ prev.T
        if j + block < n:
            rhs = a[j + block:, sl] - lower[j + block:, :j] @ diagonal[:j, :j] @ prev.T
            lower[j + block:, sl] = torch.linalg.solve(diagonal[sl, sl], rhs.T).T
    assert torch.allclose(lower @ diagonal @ lower.T, a, atol=1e-9, rtol=1e-6)
    return lower, diagonal


def activation_quantize(x, group, gamma=1.):
    shape = x.shape
    tiles = x.reshape(-1, shape[-1] // group, group)
    step = tiles.abs().amax(-1, keepdim=True).clamp_min(1e-20) * gamma / 7
    return ((tiles / step).round().clamp(-8, 7) * step).reshape(shape)


def quantize(w, x, grad, group):
    n, outputs = w.shape
    gw = torch.stack([a.T @ b for a, b in zip(x, grad)])
    fi = regularize((gw @ gw.transpose(-1, -2)).mean(0))
    fo = regularize((grad.transpose(-1, -2) @ grad).mean(0))
    gx = regularize(w @ fo @ w.T)
    transforms = []
    for j in range(0, n, group):
        a, b = fi[j:j+group, j:j+group], gx[j:j+group, j:j+group]
        invhalf, half = power(a, -.5), power(a, .5)
        geom = invhalf @ power(half @ b @ half, .5) @ invhalf
        transforms.append(power(geom, .5) @ hadamard(group))
    transform = torch.block_diag(*transforms)
    original = torch.linalg.solve(transform, w)
    xt = x @ transform
    assert torch.allclose(xt @ original, x @ w, atol=1e-8, rtol=1e-6)
    input_fisher = regularize(transform.T @ fi @ transform)
    # Quantize high-curvature input tiles and output channels first.
    tiles = input_fisher.diag().reshape(-1, group).sum(-1).argsort()
    perm_i = (tiles[:, None] * group + torch.arange(group)[None, :]).flatten()
    perm_o = fo.diag().argsort()
    li, di = block_ldl(input_fisher[perm_i][:, perm_i], group)
    lo, _ = block_ldl(fo[perm_o][:, perm_o], 1)
    reference = original[perm_i][:, perm_o]
    adjusted = reference.clone()
    quantized = torch.empty_like(reference)
    scales = torch.empty((n // group, outputs), dtype=w.dtype)
    coordinates = [(i, j) for i in range(n // group) for j in range(outputs)]
    coordinates.sort(key=lambda pair: (sum(pair), pair[0]), reverse=True)
    for i, j in coordinates:
        sl = slice(i * group, (i + 1) * group)
        values = adjusted[sl, j]
        # Appendix B: 500 range candidates in [max|w|, 2max|w|].
        steps = torch.linspace(1, 2, 500, dtype=w.dtype) * values.abs().max().clamp_min(1e-20) / 15
        proposals = (values[:, None] / steps).round().clamp(-8, 7) * steps
        errors = reference[sl, j, None] - proposals
        costs = (errors * (di[sl, sl] @ errors)).sum(0)
        best = costs.argmin()
        quantized[sl, j] = proposals[:, best]
        scales[i, j] = steps[best]
        # Eq. 16, restricted to remaining coordinates by triangular L factors.
        correction = torch.zeros_like(reference)
        correction[sl, j] = errors[:, best]
        adjusted += li.T @ correction @ lo
    quantized = quantized[torch.argsort(perm_i)][:, torch.argsort(perm_o)]
    gamma = torch.tensor(1., dtype=w.dtype)
    if group == n:
        invt = torch.linalg.inv(transform)
        curvature = invt @ gx @ invt.T
        token_energy = grad.square().sum(-1).mean(0)
        candidates = torch.linspace(.5, 1, 100, dtype=w.dtype)
        costs = []
        for c in candidates:
            delta = xt - activation_quantize(xt, group, c)
            costs.append(((delta @ curvature) * delta).sum(-1).mul(token_energy).mean())
        gamma = candidates[torch.stack(costs).argmin()]
    assert torch.isfinite(quantized).all() and (scales > 0).all()
    return transform, quantized, float(gamma), scales


def collect(model_path):
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
        torch_dtype=torch.bfloat16, attn_implementation="eager").eval()
    model.requires_grad_(False)
    projection = model.model.layers[0].self_attn.q_proj
    capture = {}
    def hook(module, inputs, output):
        capture['x'] = inputs[0].detach()[0, :, :128].double()
        capture['z'] = output.detach().requires_grad_(True)
        return capture['z']
    handle = projection.register_forward_hook(hook)
    xs, gs = [], []
    for text in TEXTS:
        tokens = tokenizer((text + ' ') * 16, return_tensors='pt').input_ids[:, :64]
        logits = model(tokens, use_cache=False).logits.float()[0]
        labels = torch.multinomial(logits.detach().softmax(-1), 1).squeeze(-1)
        loss = F.cross_entropy(logits, labels, reduction='sum')
        gradient, = torch.autograd.grad(loss, capture['z'])
        xs.append(capture['x']); gs.append(gradient[0, :, :64].detach().double())
    handle.remove()
    weights = projection.weight[:64, :128].detach().double().T
    metadata = dict(model=str(model_path), revision=REVISION, python=platform.python_version(),
        torch=torch.__version__, transformers=transformers.__version__, device='cpu',
        seed=7, texts=TEXTS, tokens_per_text=64, calibration_sequences=2, heldout_sequences=2)
    return weights, torch.stack(xs), torch.stack(gs), metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, default=Path.home() / '.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots' / REVISION)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('results.json'))
    args = parser.parse_args()
    torch.set_num_threads(4); torch.manual_seed(7)
    start = time.monotonic()
    w, x, g, metadata = collect(args.model)
    results = []
    for group in (128, 32):
        t, q, gamma, scales = quantize(w, x[:2], g[:2], group)
        truth = x[2:] @ w
        predicted = activation_quantize(x[2:] @ t, group, gamma) @ q
        baseline_w = activation_quantize(w.T, group).T
        baseline = activation_quantize(x[2:], group) @ baseline_w
        mse = lambda y: float((y-truth).square().sum() / truth.square().sum())
        results.append(dict(group=group, transform_block=group, gamma=gamma,
            relative_output_mse=mse(predicted), rtn_relative_output_mse=mse(baseline),
            weight_scale_candidates=500, activation_clip_candidates=100 if group==128 else 0,
            scale_count=scales.numel(), numerical_assertions_passed=4))
    result = dict(environment=metadata, seconds=time.monotonic()-start, results=results,
        scope='Real first-layer 128x64 component; output gradients from full Qwen3-0.6B. Numerical dequantized execution only.',
        limitations='Two hand-written calibration sequences, not 2048x2048 DCLM-Edu. Sliced input/output Fisher is a component approximation. No whole-model W4A4KV4, KV quantization, packed checkpoint, benchmark perplexity or CUDA speed claim. 1% damping is added for undersampled curvature.')
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
