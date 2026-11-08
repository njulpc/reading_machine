#!/usr/bin/env python3
"""StrataFlux numerical components, Eqs. 2--4 and 7--8; no runtime speed claims.

Qwen3-0.6B real weights/activations. RTN resident weight quantizer is an
explicit substitute for YAQA/AWQ. KV correction is verified on small tensors;
KVarN encoding, CUDA/Metal scheduling and SSD delivery are not reproduced.
"""
import argparse
import json
import platform
import time
from pathlib import Path

import torch
import torch.nn.functional as F


def quantize(x, bits, dim):
    """Signed symmetric min/max, scale per retained dimension."""
    qmax = 2 ** (bits - 1) - 1
    scale = x.abs().amax(dim=dim, keepdim=True).clamp_min(1e-12) / qmax
    return (x / scale).round().clamp(-qmax - 1, qmax) * scale


def select(x, k, chunk=1024):
    """Paper's per-chunk largest |activation| selection; retain signed x."""
    z = torch.zeros_like(x)
    for begin in range(0, x.shape[-1], chunk):
        part = x[..., begin:begin + chunk]
        idx = part.abs().topk(min(k, part.shape[-1]), dim=-1).indices
        z[..., begin:begin + chunk].scatter_(-1, idx, part.gather(-1, idx))
    return z


def fit_refinement(weight, base, x, k, chunk=1024):
    """Eq. 4: C(M+lambda I)=R G+lambda R, row-batch input convention."""
    r = weight - base
    z = select(x, k, chunk)
    m = z.T @ z / len(x)
    g = x.T @ z / len(x)
    lam = m.diagonal().mean().clamp_min(1e-12)
    lhs = m + lam * torch.eye(m.shape[0], dtype=m.dtype)
    rhs = r @ g + lam * r
    c = torch.linalg.solve(lhs, rhs.T).T
    residual = (c @ lhs - rhs).norm() / rhs.norm().clamp_min(1e-12)
    return c, float(lam), float(residual)


def kv_refine(q, k0, v0, k1, v1, fraction=1/128, group=2):
    """Eqs. 7--8, GQA max over query heads after summing token groups.

    q:[Hq,D], k/v:[Hkv,T,D]; k1/v1 are candidate refined reconstructions.
    Stable common exponential shift includes refined scores.
    """
    hkv, tokens, d = k0.shape
    assert len(q) % hkv == 0 and tokens % group == 0
    repeat = len(q) // hkv
    kr, vr = k0.repeat_interleave(repeat, 0), v0.repeat_interleave(repeat, 0)
    l0 = torch.einsum('hd,htd->ht', q, kr) / d ** .5
    att = l0.softmax(-1)
    score = att.reshape(hkv, repeat, tokens // group, group).sum(-1).amax(1)
    budget = max(1, int((tokens // group) * fraction))
    chosen = score.topk(budget, -1).indices
    mask = torch.zeros_like(score, dtype=torch.bool).scatter_(1, chosen, True)
    mask = mask.repeat_interleave(group, -1)
    km = torch.where(mask[..., None], k1, k0).repeat_interleave(repeat, 0)
    vm = torch.where(mask[..., None], v1, v0).repeat_interleave(repeat, 0)
    l1 = torch.einsum('hd,htd->ht', q, km) / d ** .5
    shift = torch.maximum(l0.amax(-1), l1.amax(-1))[:, None]
    e0, e1 = (l0 - shift).exp(), (l1 - shift).exp()
    sel = mask.repeat_interleave(repeat, 0)
    numerator = torch.einsum('ht,htd->hd', e0, vr)
    numerator += torch.einsum('ht,htd->hd', e1 * sel, vm)
    numerator -= torch.einsum('ht,htd->hd', e0 * sel, vr)
    denominator = e0.sum(-1) + ((e1-e0)*sel).sum(-1)
    corrected = numerator / denominator[:, None]
    dense = torch.einsum('ht,htd->hd', l1.softmax(-1), vm)
    return corrected, dense, mask


def unit_checks():
    gen = torch.Generator().manual_seed(13)
    x = torch.randn(32, 16, generator=gen, dtype=torch.float64)
    w = torch.randn(8, 16, generator=gen, dtype=torch.float64)
    b = quantize(w, 3, 1)
    c, lam, err = fit_refinement(w, b, x, 4, 8)
    assert err < 1e-10
    z = select(x, 4, 8)
    objective = lambda a: ((x@(w-b).T-z@a.T)**2).sum()/len(x)+lam*((a-(w-b))**2).sum()
    assert objective(c) <= objective(w-b) + 1e-9
    full, _, _ = fit_refinement(w, b, x, 16, 16)
    assert torch.allclose(full, w-b, atol=1e-10)
    assert (select(x, 2, 8) != 0).sum(-1).eq(4).all()
    q = torch.randn(4, 8, generator=gen, dtype=torch.float64)*25
    k = torch.randn(2, 16, 8, generator=gen, dtype=torch.float64)
    v = torch.randn(2, 16, 8, generator=gen, dtype=torch.float64)
    out, dense, mask = kv_refine(q, quantize(k, 2, -1), quantize(v, 2, -1), k, v, .25)
    assert torch.isfinite(out).all() and torch.allclose(out, dense, atol=1e-10)
    assert mask.sum(-1).eq(4).all()
    return {'assertions': 6, 'fit_normal_equation_relative_error': err,
            'kv_correction_max_error': float((out-dense).abs().max())}


def run(args):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(4)
    torch.manual_seed(19)
    started = time.time()
    checks = unit_checks()
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
            torch_dtype=torch.bfloat16, attn_implementation='eager').eval()
    texts = [
        'Quantization reduces model storage while calibration measures numerical errors. ',
        'A cache keeps frequently used information close to the processor. ',
        'A scientist compares a compressed model with its unmodified reference. ',
        'Selected weight residuals can correct errors on important activation channels. ',
    ]
    captured = []
    layer = model.model.layers[0].self_attn.q_proj
    handle = layer.register_forward_pre_hook(lambda module, inputs: captured.append(inputs[0].detach().double().reshape(-1, inputs[0].shape[-1])))
    with torch.no_grad():
        for text in texts:
            ids = tok(text*6, return_tensors='pt', truncation=True, max_length=64)['input_ids']
            model(input_ids=ids, use_cache=False)
    handle.remove()
    weight = layer.weight.detach().double()
    train, heldout = torch.cat(captured[:2]), torch.cat(captured[2:])
    # Per-output-channel RTN resident base, per-input-column 4-bit correction.
    base = quantize(weight, args.bits, 1)
    fitted, lam, eqerr = fit_refinement(weight, base, train, args.k)
    correction = quantize(fitted, 4, 0)
    residual4 = quantize(weight-base, 4, 0)
    def mse(w, x):
        return float((w**2).mean())
    rows = {}
    for label, x in [('calibration', train), ('heldout', heldout)]:
        target = x @ weight.T
        y0 = x @ base.T
        z = select(x, args.k)
        rows[label] = {'base_mse':mse(y0-target,x),
            'raw_residual4_mse':mse(y0+z@residual4.T-target,x),
            'fitted4_mse':mse(y0+z@correction.T-target,x)}
    result = {'paper':'2611.08363','model':args.model, 'torch':torch.__version__,
        'python':platform.python_version(),'device':'cpu','model_dtype':'bfloat16',
        'arithmetic_dtype':'float64','unit_checks':checks,'projection':'model.layers.0.self_attn.q_proj',
        'weight_shape':list(weight.shape),'calibration_shape':list(train.shape),
        'heldout_shape':list(heldout.shape),'texts':texts,'tokens_per_text':64,
        'resident_bits':args.bits,'refinement_bits':4,'chunk':1024,'k':args.k,
        'lambda':lam,'normal_equation_error':eqerr,'results':rows,'elapsed_seconds':time.time()-started,
        'limitations':'One real Qwen projection only. Handwritten text, not RedPajama. RTN base, not YAQA/AWQ. KV Eq.8 only small-tensor verified; no KVarN, packed storage, neuron bundles, cache, fetch lead/lag runtime, whole-model PPL, SSD or GPU throughput validation.'}
    Path(args.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--model',default='Qwen/Qwen3-0.6B')
    p.add_argument('--bits',type=int,default=3)
    p.add_argument('--k',type=int,default=32)
    p.add_argument('--output',default='results.json')
    run(p.parse_args())
