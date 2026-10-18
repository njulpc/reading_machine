"""FALCON Eq. 8–9 quantization transfer experiment on Qwen3-0.6B.

This is a numerical PTQ experiment, not a Vitis/FPGA or integer-kernel port.
The exact nonnegative clip is deliberately tested alongside a signed adaptation.
"""
import argparse
import json
import math
import platform
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

MODEL = '/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca'
CALIBRATION = [
    'A compiler translates a program into instructions. Static tensor shapes make memory requirements predictable. ',
    'The library contains books about astronomy, music, history and mathematics. A reader compares several sources. ',
    'A neural network transforms an input using learned weights. Calibration measures the activation range before quantization. ',
    'A train travels between two cities. Passengers check departure times and choose a route. ',
]
EVALUATION = [
    'The gardener planted seeds in spring. Rain and sunshine helped the plants grow. In summer the garden was full of flowers. ',
    'To compute the mean of a sequence, add its elements and divide the sum by the number of elements. ',
]

def clip(x, mode, cap=32.0):
    if mode == 'paper_relu':
        return x.clamp(0, cap)
    if mode == 'signed':
        return x.clamp(-cap, cap)
    if mode == 'unclipped':
        return x
    raise ValueError(mode)

def exponent(lo, hi):
    # Conservative signed INT8 min-max fit. Positive and negative endpoints
    # have different ranges. FALCON fixes powers of two but does not specify
    # Vitis's tie-breaking/scale search; this convention is explicit.
    step = max(float(hi) / 127, -float(lo) / 128)
    return math.ceil(math.log2(step)) if step > 0 else 0

def encode(x, k):
    return torch.round(x.float() / (2.0 ** k)).clamp(-128, 127).to(torch.int8)

class QuantLinear(nn.Module):
    def __init__(self, original, mode, activation_k, cap=32.0):
        super().__init__()
        w = original.weight.detach().float()
        self.weight_k = exponent(w.min(), w.max())
        self.register_buffer('weight_int8', encode(w, self.weight_k))
        self.register_buffer('bias', None if original.bias is None else original.bias.detach().clone())
        self.mode, self.activation_k, self.cap = mode, activation_k, cap

    def forward(self, x):
        aq = encode(clip(x.float(), self.mode, self.cap), self.activation_k)
        # Dense floating arithmetic simulates the quantized values. No speed claim.
        a = (aq.float() * (2.0 ** self.activation_k)).to(x.dtype)
        w = (self.weight_int8.float() * (2.0 ** self.weight_k)).to(x.dtype)
        return F.linear(a, w, self.bias)

def checks():
    x = torch.tensor([-300., -1., 0., .24, .26, 6., 32., 206.6])
    expected = torch.tensor([0, 0, 0, 0, 1, 12, 64, 64], dtype=torch.int8)
    assert torch.equal(encode(clip(x, 'paper_relu'), -1), expected)
    assert exponent(-32., 32.) == -1
    assert exponent(0., 206.6) == 1
    assert encode(torch.tensor([-1000., 1000.]), 0).tolist() == [-128, 127]
    assert torch.equal(clip(x, 'signed'), torch.tensor([-32., -1., 0., .24, .26, 6., 32., 32.]))
    assert torch.equal(encode(torch.zeros(8), exponent(0, 0)), torch.zeros(8, dtype=torch.int8))
    layer = nn.Linear(2, 1, bias=False)
    with torch.no_grad(): layer.weight.copy_(torch.tensor([[.25, -.5]]))
    q = QuantLinear(layer, 'signed', -1)
    assert torch.equal(q(torch.tensor([[2., 4.]])), torch.tensor([[-1.5]]))
    return {'equations_8_9_known_vector': True, 'saturation': True,
            'power_two_minmax': True, 'zero_tensor': True,
            'signed_ablation': True, 'quantized_linear_known_answer': True}

def run(args):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import transformers
    torch.manual_seed(0)
    torch.set_num_threads(4)
    start = time.monotonic()
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
              torch_dtype=torch.bfloat16, attn_implementation='eager').eval()
    parent = model.model.layers[0].mlp
    original = parent.down_proj
    stats = {m: {'lo': 0., 'hi': 0.} for m in ['unclipped', 'paper_relu', 'signed']}
    raw = {'negative': 0, 'above_cap': 0, 'elements': 0}
    def observe(module, inputs):
        x = inputs[0].detach().float()
        raw['negative'] += int((x < 0).sum())
        raw['above_cap'] += int((x.abs() > args.cap).sum())
        raw['elements'] += x.numel()
        for m in stats:
            z = clip(x, m, args.cap)
            stats[m]['lo'] = min(stats[m]['lo'], float(z.min()))
            stats[m]['hi'] = max(stats[m]['hi'], float(z.max()))
    def batch(text):
        return tok(text * 12, return_tensors='pt', truncation=True, max_length=args.length)
    with torch.inference_mode():
        handle = original.register_forward_pre_hook(observe)
        try:
            for text in CALIBRATION: model(**batch(text), use_cache=False)
        finally: handle.remove()
        inputs = [batch(t) for t in EVALUATION]
        baseline = [model(**b, labels=b['input_ids'], use_cache=False) for b in inputs]
        metrics = {}
        try:
            for mode in stats:
                ak = exponent(stats[mode]['lo'], stats[mode]['hi'])
                q = QuantLinear(original, mode, ak, args.cap)
                parent.down_proj = q
                rows = []
                for b, ref in zip(inputs, baseline):
                    out = model(**b, labels=b['input_ids'], use_cache=False)
                    logp = F.log_softmax(ref.logits.float(), -1)
                    logq = F.log_softmax(out.logits.float(), -1)
                    rows.append({'loss': float(out.loss), 'baseline_loss': float(ref.loss),
                       'kl_baseline_to_quant': float((logp.exp() * (logp - logq)).sum(-1).mean()),
                       'top1_agreement': float((out.logits.argmax(-1) == ref.logits.argmax(-1)).float().mean())})
                metrics[mode] = {'activation_k': ak, 'weight_k': q.weight_k, 'evaluation': rows,
                     'stored_weight_bytes': q.weight_int8.numel(),
                     'baseline_bf16_weight_bytes': original.weight.numel() * 2}
        finally: parent.down_proj = original
    return {'model': args.model, 'module': 'model.layers.0.mlp.down_proj',
       'calibration_texts': CALIBRATION, 'evaluation_texts': EVALUATION,
       'sequence_length': args.length, 'cap': args.cap, 'stats': stats, 'raw_stats': raw,
       'results': metrics, 'seconds': time.monotonic() - start,
       'environment': {'torch': torch.__version__, 'transformers': transformers.__version__,
                       'python': platform.python_version(), 'device': 'CPU', 'dtype': 'BF16'},
       'limitations': ['One layer only; artificial text, not benchmark perplexity.',
          'Qwen has signed SiLU-gated inputs, unlike FALCON nonnegative BEV activations.',
          'paper_relu executes exact Eq.8 clipping; signed is an explicitly modified transfer ablation.',
          'INT8 weight storage with floating dequantized matmul, no integer accelerator or WCET validation.',
          'Fixed C=32 transferred from paper; calibration dataset and conservative scale rule are local choices.']}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default=MODEL)
    ap.add_argument('--length', type=int, default=128)
    ap.add_argument('--cap', type=float, default=32.)
    ap.add_argument('--test-only', action='store_true')
    ap.add_argument('--output', default='results.json')
    args = ap.parse_args()
    result = {'tests': checks()}
    if not args.test_only: result['experiment'] = run(args)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
