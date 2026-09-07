#!/usr/bin/env python3
"""Executable Qwen3-0.6B transfer of arXiv:2609.05334 components.

The paper is a ViT agricultural pipeline; this is NOT its end-to-end reproduction.
ptq: all nn.Linear layers of the full, real Qwen checkpoint, native dynamic INT8.
components: real CE Hessian/Taylor pruning, GQA-safe masks, attention KD, then PTQ.
No weights or datasets are downloaded by this script.
"""
import argparse
import copy
import gc
import io
import json
import math
import platform
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download

CALIBRATION = [
    "Model compression reduces storage through pruning, quantization and knowledge distillation.",
    "A fair experiment compares a compressed model with a directly trained small model.",
]
EVALUATION = "Low precision arithmetic can reduce memory without improving inference latency."


def emit(label, value):
    print(json.dumps({label: value}, ensure_ascii=False), flush=True)


def ratio_allocation(curvatures, ratio, lower=0.05, upper=0.95):
    """Algorithm 1 lines 9-13: max(C,0), DIRECT sqrt weighting, two clips.

    All-zero curvature is an explicitly chosen uniform fallback. Final clipping
    can change the mean; do not claim this algorithm exactly meets every budget.
    """
    root = curvatures.clamp_min(0).sqrt()
    weights = root / root.mean() if root.mean() > 0 else torch.ones_like(root)
    out = (ratio * weights).clamp(lower, upper)
    return (ratio * out / out.mean()).clamp(lower, upper)


def trace_estimate(loss, params, samples):
    grads = torch.autograd.grad(loss, params, create_graph=True, retain_graph=True)
    scores = [(p.detach() * g.detach()).abs() for p, g in zip(params, grads)]
    trace = 0.0
    for _ in range(samples):
        vec = [torch.empty_like(p).bernoulli_(0.5).mul_(2).sub_(1) for p in params]
        dot = sum((g * v).sum() for g, v in zip(grads, vec))
        hv = torch.autograd.grad(dot, params, retain_graph=True)
        trace += sum((v * h).sum().item() for v, h in zip(vec, hv)) / samples
    return trace, scores


def prune_block(block, scores, ratio):
    """Algorithm 1 Taylor ranking, adapted to Qwen GQA and SwiGLU.

    A group removes paired query heads, its KV head, and output columns. This
    preserves head counts/tensor shapes and handles Qwen's 16Q:8KV grouping.
    SwiGLU removes matching gate/up rows and down columns. No speedup claimed.
    """
    a, m = block.self_attn, block.mlp
    d = a.head_dim
    nq, nkv = a.q_proj.out_features // d, a.k_proj.out_features // d
    group = nq // nkv
    q = scores['self_attn.q_proj.weight'].reshape(nkv, group * d, -1).sum((1, 2))
    k = scores['self_attn.k_proj.weight'].reshape(nkv, d, -1).sum((1, 2))
    v = scores['self_attn.v_proj.weight'].reshape(nkv, d, -1).sum((1, 2))
    o = scores['self_attn.o_proj.weight'].reshape(-1, nkv, group * d).sum((0, 2))
    dead = torch.argsort(q + k + v + o)[:min(nkv - 1, math.ceil(ratio * nkv))]
    masks = {n: torch.ones_like(p) for n, p in block.named_parameters() if n in scores}
    for j in dead.tolist():
        for name, width in [('q_proj', group * d), ('k_proj', d), ('v_proj', d)]:
            masks[f'self_attn.{name}.weight'][j * width:(j + 1) * width] = 0
        masks['self_attn.o_proj.weight'][:, j * group * d:(j + 1) * group * d] = 0
    imp = (scores['mlp.gate_proj.weight'].sum(1) + scores['mlp.up_proj.weight'].sum(1)
           + scores['mlp.down_proj.weight'].sum(0))
    units = torch.argsort(imp)[:min(len(imp) - 1, math.ceil(ratio * len(imp)))]
    for name in ['gate_proj', 'up_proj']:
        masks[f'mlp.{name}.weight'][units] = 0
    masks['mlp.down_proj.weight'][:, units] = 0
    with torch.no_grad():
        for n, p in block.named_parameters():
            if n in masks:
                p.mul_(masks[n])
    return masks, {'gqa_groups_removed': len(dead), 'total_gqa_groups': nkv,
                   'mlp_units_removed': len(units), 'total_mlp_units': len(imp)}


def kd_loss(student, teacher_logits, teacher_attentions, mapping, labels, temperature=4.0):
    """Paper Eq. 11: .5 hard CE + .3 mean-head attention MSE + .2 T² KL.

    Adapted from 3-class ViT to causal next-token vocabulary prediction, and
    depth mapping replaces the paper's ViT layers 3/6/9/11. Padding is absent.
    """
    sl = student.logits[:, :-1].float()
    tl = teacher_logits[:, :-1].float()
    hard = F.cross_entropy(sl.reshape(-1, sl.shape[-1]), labels[:, 1:].reshape(-1))
    soft = F.kl_div(F.log_softmax(sl / temperature, -1), F.softmax(tl / temperature, -1),
                    reduction='sum') * temperature ** 2 / (sl.shape[0] * sl.shape[1])
    attn = torch.stack([F.mse_loss(sa.mean(1), teacher_attentions[j].mean(1))
                        for sa, j in zip(student.attentions, mapping)]).mean()
    total = .5 * hard + .3 * attn + .2 * soft
    return total, {'hard': hard.item(), 'attention': attn.item(), 'soft': soft.item(),
                   'total': total.item()}


def native_ptq(model):
    # Paper does not specify observers/backend. This is an explicit choice, not
    # an inferred author setting. FP32 API tensors; backend quantizes activations
    # dynamically. This is distinct from the paper's Core ML weight-only timing.
    torch.backends.quantized.engine = 'qnnpack'
    return torch.ao.quantization.quantize_dynamic(model.eval(), {nn.Linear},
                                                  dtype=torch.qint8, inplace=True)


def quant_stats(model):
    layers = [(n, m) for n, m in model.named_modules()
              if isinstance(m, torch.ao.nn.quantized.dynamic.Linear)]
    qnum = sum(m.weight().numel() for _, m in layers)
    float_num = sum(p.numel() for p in model.parameters())
    # Tensor payload only: shared tensors de-duplicated by model.parameters;
    # packed kernel overhead/serialization not counted. One scale/zero per tensor.
    payload = sum(p.numel() * p.element_size() for p in model.parameters())
    payload += qnum + 16 * len(layers)
    return {'linear_layers': len(layers), 'int8_weight_elements': qnum,
            'remaining_float_elements': float_num, 'estimated_tensor_payload_bytes': payload,
            'qscheme': str(layers[0][1].weight().qscheme()),
            'sample_scale': layers[0][1].weight().q_scale(),
            'sample_zero_point': layers[0][1].weight().q_zero_point()}


@torch.no_grad()
def evaluate(model, ids):
    t = time.perf_counter()
    out = model(input_ids=ids, labels=ids, use_cache=False)
    return out.logits.detach(), {'next_token_ce': out.loss.item(),
                                'single_forward_seconds': time.perf_counter() - t}


def difference(q, f):
    return {'relative_logits_l2': ((q - f).norm() / f.norm()).item(),
            'top1_agreement': (q.argmax(-1) == f.argmax(-1)).float().mean().item()}


def load_model(path):
    return AutoModelForCausalLM.from_pretrained(path, local_files_only=True,
        torch_dtype=torch.float32, attn_implementation='eager').eval()


def run_ptq(path, eval_ids):
    model = load_model(path)
    count = sum(isinstance(m, nn.Linear) for m in model.modules())
    before = sum(p.numel() * p.element_size() for p in model.parameters())
    baseline, bmetrics = evaluate(model, eval_ids)
    emit('full_model_fp32', bmetrics)
    model = native_ptq(model)
    stats = quant_stats(model)
    assert stats['linear_layers'] == count
    after, qmetrics = evaluate(model, eval_ids)
    result = {'fp32': bmetrics, 'dynamic_int8': qmetrics, 'comparison': difference(after, baseline),
              'quantization': stats, 'fp32_tensor_payload_bytes': before,
              'estimated_payload_ratio': before / stats['estimated_tensor_payload_bytes'],
              'full_qwen_forward_verified': True, 'paper_vision_reproduction': False}
    del model
    gc.collect()
    return result


def run_components(path, calib_ids, eval_ids, args):
    teacher = load_model(path)
    teacher.requires_grad_(False)
    block_ids = [int(x) for x in args.blocks.split(',')]
    selected = {}
    for i in block_ids:
        block = teacher.model.layers[i]
        for name, p in block.named_parameters():
            if name.endswith('.weight') and ('_proj.' in name):
                p.requires_grad_(True)
        selected[i] = [(n, p) for n, p in block.named_parameters() if p.requires_grad]
    traces = {i: [] for i in block_ids}
    scores = {i: {n: torch.zeros_like(p) for n, p in selected[i]} for i in block_ids}
    for ids in calib_ids:
        loss = teacher(input_ids=ids, labels=ids, use_cache=False).loss
        for i in block_ids:
            names, params = zip(*selected[i])
            # Separate attention/MLP traces as in paper; lambda unspecified there.
            ai = [j for j, n in enumerate(names) if n.startswith('self_attn')]
            mi = [j for j, n in enumerate(names) if n.startswith('mlp')]
            at, asc = trace_estimate(loss, [params[j] for j in ai], args.hutchinson)
            mt, msc = trace_estimate(loss, [params[j] for j in mi], args.hutchinson)
            traces[i].append({'attention': at, 'mlp': mt})
            for j, s in zip(ai + mi, asc + msc):
                scores[i][names[j]].add_(s / len(calib_ids))
            emit('hessian', {'block': i, 'attention': at, 'mlp': mt})
        del loss
    curvatures = torch.tensor([max(sum(t['attention'] + args.mlp_balance * t['mlp']
                                     for t in traces[i]), 0) / len(calib_ids) for i in block_ids])
    ratios = ratio_allocation(curvatures, args.prune_ratio)
    pruning, masks = {}, {}
    for i, ratio in zip(block_ids, ratios.tolist()):
        masks[i], pruning[str(i)] = prune_block(teacher.model.layers[i], scores[i], ratio)
        pruning[str(i)]['allocated_ratio'] = ratio
    del scores, selected
    teacher.requires_grad_(False)
    # Recovery performs an actual masked CE update on the selected blocks.
    recovery_parameters = []
    hooks = []
    for i in block_ids:
        for n, p in teacher.model.layers[i].named_parameters():
            if n in masks[i]:
                p.requires_grad_(True)
                hooks.append(p.register_hook(lambda g, mask=masks[i][n]: g * mask))
                recovery_parameters.append(p)
    opt = torch.optim.SGD(recovery_parameters, lr=1e-5)
    opt.zero_grad()
    recovery_loss = teacher(input_ids=calib_ids[0], labels=calib_ids[0], use_cache=False).loss
    recovery_loss.backward()
    opt.step()
    for h in hooks:
        h.remove()
    recovery_value = recovery_loss.item()
    del opt, recovery_loss, recovery_parameters, masks
    teacher.requires_grad_(False)
    teacher.zero_grad(set_to_none=True)
    teacher.eval()
    mapping = torch.linspace(0, len(teacher.model.layers) - 1, args.student_layers).round().int().tolist()
    config = copy.deepcopy(teacher.config)
    config.num_hidden_layers = args.student_layers
    student = type(teacher)(config).float().eval()
    student.model.embed_tokens.load_state_dict(teacher.model.embed_tokens.state_dict())
    student.model.norm.load_state_dict(teacher.model.norm.state_dict())
    for i, j in enumerate(mapping):
        student.model.layers[i].load_state_dict(teacher.model.layers[j].state_dict())
    student.tie_weights()
    student.model.embed_tokens.requires_grad_(False)
    student.model.norm.requires_grad_(False)
    # One teacher pass; reuse detached logits/maps, no pseudo teacher output.
    with torch.no_grad():
        tout = teacher(input_ids=calib_ids[0], use_cache=False, output_attentions=True)
        target_logits = tout.logits.detach()
        target_attn = tuple(a.detach() for a in tout.attentions)
    del tout, teacher
    gc.collect()
    before, before_metrics = evaluate(student, eval_ids)
    opt = torch.optim.AdamW((p for p in student.parameters() if p.requires_grad), lr=1e-5)
    losses = []
    for _ in range(args.steps):
        opt.zero_grad()
        out = student(input_ids=calib_ids[0], use_cache=False, output_attentions=True)
        loss, detail = kd_loss(out, target_logits, target_attn, mapping, calib_ids[0])
        loss.backward()
        opt.step()
        losses.append(detail)
        emit('kd_step', detail)
    del opt, out, loss, target_logits, target_attn
    fp, after_metrics = evaluate(student, eval_ids)
    student = native_ptq(student)
    qp, qmetrics = evaluate(student, eval_ids)
    return {'selected_blocks': block_ids, 'calibration_sequences': len(calib_ids),
            'hutchinson_per_group': args.hutchinson, 'traces': traces,
            'curvatures': curvatures.tolist(), 'pruning': pruning,
            'recovery_ce_before_step': recovery_value, 'student_layer_mapping': mapping,
            'student_before_kd': before_metrics, 'kd_losses': losses,
            'student_after_kd': after_metrics, 'student_int8': qmetrics,
            'student_ptq_comparison': difference(qp, fp), 'quantization': quant_stats(student),
            'paper_vision_reproduction': False,
            'limitations': ['Only selected Qwen blocks calibrated/pruned; no full 28-block H-BAC sweep.',
                'Causal language CE replaces vision classification; GQA groups replace independent ViT heads.',
                'One masked recovery step and short KD replace paper one epoch and 15 epochs.',
                'Student depth/initialization differs from ImageNet-pretrained TinyViT; no agricultural data.',
                'No physical structural compaction, Core ML conversion or smartphone benchmark.']}


def self_test():
    x = torch.tensor([1., 2., 3.], requires_grad=True)
    tr, _ = trace_estimate((x*x).sum(), [x], 10)
    assert abs(tr - 6) < 1e-6
    assert torch.allclose(ratio_allocation(torch.ones(4), .5), torch.full((4,), .5))
    assert torch.allclose(ratio_allocation(torch.zeros(4), .5), torch.full((4,), .5))
    c = ratio_allocation(torch.tensor([1., 4.]), .5)
    assert c[1] > c[0]
    # Real GQA-shaped module verifies masks for all three projections and output.
    from transformers import Qwen3Config, Qwen3ForCausalLM
    model = Qwen3ForCausalLM(Qwen3Config(vocab_size=32, hidden_size=16,
        intermediate_size=24, num_hidden_layers=1, num_attention_heads=4,
        num_key_value_heads=2, head_dim=4))
    b = model.model.layers[0]
    s = {n: p.detach().abs() for n, p in b.named_parameters() if '_proj.' in n}
    masks, stats = prune_block(b, s, .5)
    for n, p in b.named_parameters():
        if n in masks:
            assert torch.count_nonzero(p.detach()[masks[n] == 0]) == 0
    assert stats['gqa_groups_removed'] == 1
    q = native_ptq(nn.Sequential(nn.Linear(8, 8)).eval())
    assert torch.isfinite(q(torch.randn(2, 8))).all()
    return {'hutchinson_exact_quadratic': True, 'direct_allocation_and_zero_fallback': True,
            'gqa_swiglu_masks': True, 'native_dynamic_int8': True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['ptq', 'components', 'test'], default='ptq')
    ap.add_argument('--model', default='Qwen/Qwen3-0.6B')
    ap.add_argument('--blocks', default='0,14')
    ap.add_argument('--hutchinson', type=int, default=10)
    ap.add_argument('--mlp-balance', type=float, default=1.0)
    ap.add_argument('--prune-ratio', type=float, default=.5)
    ap.add_argument('--student-layers', type=int, default=4)
    ap.add_argument('--steps', type=int, default=1)
    ap.add_argument('--calibration-count', type=int, default=1)
    ap.add_argument('--seq-len', type=int, default=16)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--output', type=Path, default=Path('results.json'))
    args = ap.parse_args()
    assert 0 < args.prune_ratio < 1 and args.hutchinson > 0 and args.steps > 0
    assert 1 <= args.calibration_count <= len(CALIBRATION) and args.seq_len >= 4
    torch.set_num_threads(args.threads)
    torch.manual_seed(42)
    start = time.perf_counter()
    result = {'paper': '2609.05334', 'model': args.model, 'mode': args.mode,
              'seed': 42, 'device': 'cpu', 'torch': torch.__version__,
              'python': platform.python_version(), 'platform': platform.platform(),
              'arguments': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
              'full_paper_reproduction': False, 'tests': self_test()}
    if args.mode != 'test':
        path = str(Path(args.model)) if Path(args.model).is_dir() else snapshot_download(args.model, local_files_only=True)
        result['checkpoint_revision'] = Path(path).name
        tok = AutoTokenizer.from_pretrained(path, local_files_only=True)
        encode = lambda t: tok(t, return_tensors='pt', truncation=True, max_length=args.seq_len).input_ids
        calib = [encode(s) for s in CALIBRATION[:args.calibration_count]]
        ev = encode(EVALUATION)
        result['calibration_texts'] = CALIBRATION[:args.calibration_count]
        result['evaluation_text'] = EVALUATION
        result['result'] = run_ptq(path, ev) if args.mode == 'ptq' else run_components(path, calib, ev, args)
    result['elapsed_seconds'] = time.perf_counter() - start
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    emit('completed', str(args.output))


if __name__ == '__main__':
    main()
