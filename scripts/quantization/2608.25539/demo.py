#!/usr/bin/env python3
"""Per-channel W8 plus dynamic activation PTQ on Qwen3-0.6B."""
import argparse
import glob
import os

import torch


def model_dir(arg=None):
    if arg: return arg
    hits=glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits+=glob.glob('/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*')
    hits=[x for x in hits if os.path.exists(os.path.join(x,'tokenizer.json'))]
    if not hits: raise FileNotFoundError('Pass --model-dir')
    return hits[0]


def fake_int8(x, dim):
    scale=x.detach().float().abs().amax(dim=dim,keepdim=True).clamp_min(1e-12)/127
    return (x.float()/scale).round().clamp(-127,127).mul(scale).to(x.dtype)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--model-dir')
    args=p.parse_args(); from transformers import AutoModelForCausalLM,AutoTokenizer
    d=model_dir(args.model_dir); tok=AutoTokenizer.from_pretrained(d,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(d,local_files_only=True,dtype=torch.float32).eval()
    prompts=['healthy tomato leaf','番茄叶片出现褐色斑点','plant disease classification']
    batch=tok(prompts,return_tensors='pt',padding=True)
    with torch.inference_mode(): ref=model(**batch,use_cache=False).logits.float()
    hooks=[]; layers=elements=0
    with torch.no_grad():
        for name,module in model.named_modules():
            if isinstance(module,torch.nn.Linear) and name!='lm_head':
                module.weight.copy_(fake_int8(module.weight,dim=1))
                # Dynamic per-token activation scale; hook returns transformed positional input.
                hooks.append(module.register_forward_pre_hook(lambda _m,inp:(fake_int8(inp[0],dim=-1),)+inp[1:]))
                layers+=1; elements+=module.weight.numel()
    with torch.inference_mode(): out=model(**batch,use_cache=False).logits.float()
    for h in hooks: h.remove()
    ref_last=ref[torch.arange(len(prompts)),batch['attention_mask'].sum(1)-1]
    out_last=out[torch.arange(len(prompts)),batch['attention_mask'].sum(1)-1]
    top_match=(ref_last.argmax(-1)==out_last.argmax(-1)).float().mean().item()
    cosine=torch.nn.functional.cosine_similarity(ref_last,out_last,dim=-1).mean().item()
    print(f'model=Qwen3-0.6B prompts={len(prompts)} linear_layers={layers} quantized_elements={elements}')
    print(f'weight_scheme=per_output_channel_int8 activation_scheme=dynamic_per_token_int8 analytical_weight_payload_bytes={elements}')
    print(f'top1_match_rate={top_match:.6f} last_token_cosine_mean={cosine:.8f} logits_mae={float((ref_last-out_last).abs().mean()):.8f}')
    assert layers==196 and elements==440401920 and cosine>0.95 and torch.isfinite(out).all()


if __name__=='__main__': main()
