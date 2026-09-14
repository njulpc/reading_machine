"""E4M3FN attention numerical reproduction of arXiv:2609.13031.
CPU reference: true FP8 casts/storage; FP32 GEMMs, no FP8 speed claim.
Paired ICL validation preserves the paper's train-query scale reuse.
Qwen adaptation uses causal attention and explicitly forces the small-N path.
"""
import argparse
import json
import math
import platform
import time
from pathlib import Path
import torch
import torch.nn.functional as F


def quantize(x, scale=None):
    x = x.float()
    if scale is None:
        scale = x.abs().amax(dim=(-2, -1), keepdim=True) / 448.0
        scale = torch.where(scale == 0, torch.ones_like(scale), scale)
    code = (x / scale).clamp(-448, 448).to(torch.float8_e4m3fn)
    return code, scale


def dequant(x, scale=None):
    code, scale = quantize(x, scale)
    return code.float() * scale, scale


def reference_attention(q, k, v, mask=None, scaling=None, qscale=None,
                        tile=64, quantized=True):
    """Online softmax; FP8 exponent lift 256; denominator before P cast.

    B,H,S,D layout; Q/K/V absmax over S,D independently per batch/head.
    The original kernel is fused Triton; this readable CPU reference loops K.
    No full attention matrix is retained. Mask must leave each row a valid key.
    """
    if scaling is None:
        scaling = q.shape[-1] ** -0.5
    if quantized:
        q, _ = dequant(q, qscale)
        k, _ = dequant(k)
        v, _ = dequant(v)
    else:
        q, k, v = q.float(), k.float(), v.float()
    m = torch.full((*q.shape[:-1], 1), -torch.inf, device=q.device)
    denominator = torch.zeros_like(m)
    out = torch.zeros_like(q)
    for start in range(0, k.shape[-2], tile):
        end = min(start + tile, k.shape[-2])
        logits = (q @ k[..., start:end, :].transpose(-1, -2)) * scaling
        if mask is not None:
            logits = logits + mask[..., start:end]
        new_m = torch.maximum(m, logits.amax(-1, keepdim=True))
        rescale = torch.exp(m - new_m)
        p = torch.exp(logits - new_m) * 256.0
        denominator = denominator * rescale + p.sum(-1, keepdim=True)
        pv = p.to(torch.float8_e4m3fn).float() if quantized else p
        out = out * rescale + pv @ v[..., start:end, :]
        m = new_m
    return out / denominator


def rel(a, b):
    return float((a - b).norm() / b.norm().clamp_min(1e-12))


def self_test():
    torch.manual_seed(17)
    x = torch.randn(2, 3, 17, 16)
    code, scale = quantize(x)
    assert code.dtype == torch.float8_e4m3fn and code.element_size() == 1
    assert torch.equal(code.float().abs().amax((-2, -1), keepdim=True), torch.full_like(scale, 448))
    z, _ = dequant(torch.zeros_like(x)); assert torch.equal(z, torch.zeros_like(z))
    q, k, v = (torch.randn(1, 2, 19, 16) for _ in range(3))
    mask = torch.zeros(19, 19).masked_fill(torch.ones(19, 19, dtype=torch.bool).triu(1), -torch.inf)
    expected = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
    out = reference_attention(q, k, v, mask, tile=7, quantized=False)
    assert torch.allclose(out, expected, atol=5e-6, rtol=1e-5)
    qout = reference_attention(q, k, v, mask, tile=7)
    assert torch.isfinite(qout).all() and rel(qout, expected) < .15
    # Paper-specific paired train/test calls: K,V and train-derived Q scale shared.
    trainq = torch.randn(1, 2, 23, 16)
    testq = torch.randn(1, 2, 7, 16)
    traink, trainv = torch.randn_like(trainq), torch.randn_like(trainq)
    _, shared = quantize(trainq)
    train = reference_attention(trainq, traink, trainv, qscale=shared)
    together = reference_attention(testq, traink, trainv, qscale=shared)
    separate = torch.cat([reference_attention(testq[..., i:i+1, :], traink, trainv, qscale=shared) for i in range(7)], dim=-2)
    assert torch.allclose(together, separate, atol=1e-6, rtol=1e-5)
    fulltrain = F.scaled_dot_product_attention(trainq, traink, trainv)
    fulltest = F.scaled_dot_product_attention(testq, traink, trainv)
    return {'fp8_cast_and_zero': True, 'unquantized_online_matches_sdpa': True,
            'causal_fp8_relative_l2': rel(qout, expected),
            'paired_train_relative_l2': rel(train, fulltrain),
            'paired_test_relative_l2': rel(together, fulltest),
            'shared_query_scale_batch_invariance_max_abs': float((together-separate).abs().max()),
            'per_head_qkv_payload_ratio_vs_fp16': 2*x.numel()/(code.numel()+4*scale.numel())}


def run_qwen(args):
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.models.qwen3 import modeling_qwen3 as modeling
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
                                               torch_dtype=torch.float32, attn_implementation='eager').eval()
    texts = [
        'A compressed neural network represents its computation with fewer bits. Attention compares a query to keys and combines the corresponding values. ',
        '模型量化需要比较精度和资源开销。动态缩放根据当前张量确定范围，推理实验必须记录真实条件。',
        'To compare two numerical algorithms, keep the inputs fixed and measure both output error and execution time. An optimization may improve speed only for sufficiently large problems. '
    ]
    inputs = [tokenizer(t*3, return_tensors='pt', truncation=True, max_length=args.tokens) for t in texts]
    calls = {'quantized': 0, 'gated_off': 0}
    original = modeling.eager_attention_forward
    def replacement(module, query, key, value, attention_mask, scaling, dropout=0., **kwargs):
        if key.shape[-2] <= 8192 and not args.force_small:
            calls['gated_off'] += 1
            return original(module, query, key, value, attention_mask, scaling, dropout, **kwargs)
        calls['quantized'] += 1
        key = modeling.repeat_kv(key, module.num_key_value_groups)
        value = modeling.repeat_kv(value, module.num_key_value_groups)
        # Qwen has no ICL train/test pair. Scales are dynamic per causal call.
        # For this prefill experiment all attention masks are supplied by Qwen.
        if attention_mask is None:
            raise RuntimeError('Causal mask required for this prefill-only experiment')
        out = reference_attention(query, key, value, attention_mask[..., :key.shape[-2]], scaling, tile=args.tile)
        return out.transpose(1, 2).contiguous().to(query.dtype), None
    rows = []
    with torch.inference_mode():
        model(**inputs[0], use_cache=False)  # warmup
        try:
            for i, inp in enumerate(inputs):
                modeling.eager_attention_forward = original
                start = time.perf_counter(); base = model(**inp, labels=inp['input_ids'], use_cache=False); bt = time.perf_counter()-start
                modeling.eager_attention_forward = replacement
                start = time.perf_counter(); quant = model(**inp, labels=inp['input_ids'], use_cache=False); qt = time.perf_counter()-start
                rows.append({'sample': i, 'tokens': int(inp['input_ids'].shape[1]), 'baseline_ce': float(base.loss),
                             'fp8_reference_ce': float(quant.loss), 'logits_relative_l2': rel(quant.logits,base.logits),
                             'argmax_agreement':float((base.logits.argmax(-1)==quant.logits.argmax(-1)).float().mean()),
                             'baseline_seconds':bt,'reference_seconds':qt})
        finally:
            modeling.eager_attention_forward = original
    return {'model':str(args.model),'model_layers':model.config.num_hidden_layers,
            'parameters':sum(p.numel() for p in model.parameters()),
            'torch':torch.__version__,'transformers':transformers.__version__,
            'platform':platform.platform(),'device':'cpu','weights_dtype':'float32',
            'fp8_native_gemm':False,'qwen_causal_adaptation':True,
            'paper_gate_train_rows_gt':8192,'force_small':args.force_small,'attention_calls':calls,
            'samples':rows,'full_paper_reproduction':False,
            'limitations':['No NVIDIA FP8 Triton kernel or GPU benchmark.',
                           'Qwen causal prefill has no tabular train/test partition; paired scale reuse validated separately.',
                           'Only three short fixed texts; not benchmark perplexity.',
                           'Weights and KV cache remain FP32; no model-file compression or acceleration claimed.']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', default='Qwen/Qwen3-0.6B')
    p.add_argument('--tokens',type=int,default=96)
    p.add_argument('--tile',type=int,default=64)
    p.add_argument('--threads',type=int,default=4)
    p.add_argument('--force-small',action='store_true')
    p.add_argument('--self-test-only',action='store_true')
    p.add_argument('--output',default='results.json')
    args=p.parse_args();torch.set_num_threads(args.threads)
    result={'self_test':self_test()}
    if not args.self_test_only: result['qwen']=run_qwen(args)
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
