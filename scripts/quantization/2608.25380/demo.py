#!/usr/bin/env python3
"""APT dual-threshold pruning/precision assignment on Qwen3 attention."""
import argparse
import glob
import os

import torch


def model_dir(arg=None):
    if arg: return arg
    hits = glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits += glob.glob('/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*')
    hits = [x for x in hits if os.path.exists(os.path.join(x, 'tokenizer.json'))]
    if not hits: raise FileNotFoundError('Pass --model-dir')
    return hits[0]


def quant_rows(x, bits):
    qmax = 2 ** (bits - 1) - 1
    scale = x.abs().amax(-1, keepdim=True).clamp_min(1e-12) / qmax
    return (x / scale).round().clamp(-qmax, qmax).mul(scale)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--model-dir'); p.add_argument('--prompt',default='高分辨率生成模型需要联合剪枝和混合精度。')
    p.add_argument('--prune-quantile',type=float,default=0.50); p.add_argument('--high-quantile',type=float,default=0.85)
    args=p.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    d=model_dir(args.model_dir); tok=AutoTokenizer.from_pretrained(d,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(d,local_files_only=True,dtype=torch.float32).eval()
    captured={}
    handle=model.model.layers[0].register_forward_pre_hook(lambda _m, inp: captured.setdefault('h',inp[0].detach()))
    ids=tok(args.prompt,return_tensors='pt')['input_ids']
    with torch.inference_mode(): model(**{'input_ids':ids},use_cache=False)
    handle.remove(); torch.set_grad_enabled(False); h=captured['h']; attn=model.model.layers[0].self_attn
    q=attn.q_proj(h); k=attn.k_proj(h); v=attn.v_proj(h)
    heads=model.config.num_attention_heads; kv_heads=model.config.num_key_value_heads; dim=q.shape[-1]//heads
    q=q.view(1,-1,heads,dim).transpose(1,2); k=k.view(1,-1,kv_heads,dim).transpose(1,2); v=v.view(1,-1,kv_heads,dim).transpose(1,2)
    repeat=heads//kv_heads; k=k.repeat_interleave(repeat,1); v=v.repeat_interleave(repeat,1)
    scores=q@k.transpose(-1,-2)/(dim**0.5); causal=torch.triu(torch.ones(scores.shape[-2:],dtype=torch.bool),1)
    scores=scores.masked_fill(causal,float('-inf')); probs=scores.softmax(-1); reference=probs@v
    finite=probs[~causal.view(1,1,*causal.shape).expand_as(probs)]
    low=torch.quantile(finite,args.prune_quantile); high=torch.quantile(finite,args.high_quantile)
    keep=probs>=low; high_mask=probs>=high
    v4=quant_rows(v,4); v8=quant_rows(v,8)
    # APDT proxy: low-probability edges are removed; medium/high edges use 4/8-bit V.
    mixed=torch.where(high_mask.unsqueeze(-1),v8.unsqueeze(-3),v4.unsqueeze(-3))
    weighted=torch.where(keep.unsqueeze(-1),probs.unsqueeze(-1)*mixed,torch.zeros_like(mixed)).sum(-2)
    kept=keep.float().mean().item(); high_fraction=high_mask.float().mean().item()
    effective_bits=(high_mask.sum()*8 + (keep & ~high_mask).sum()*4).item()/keep.sum().item()
    rel=(weighted-reference).norm().div(reference.norm()).item()
    print(f'model=Qwen3-0.6B prompt_tokens={ids.numel()} heads={heads} head_dim={dim}')
    print(f'low_threshold={low.item():.8e} high_threshold={high.item():.8e} kept_edge_fraction={kept:.6f} high_precision_fraction={high_fraction:.6f}')
    print(f'effective_value_bits_per_kept_edge={effective_bits:.6f} attention_output_relative_l2={rel:.8f}')
    assert 0 < kept <= 1 and 4 <= effective_bits <= 8 and torch.isfinite(weighted).all()


if __name__=='__main__': main()
