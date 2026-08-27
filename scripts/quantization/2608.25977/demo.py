#!/usr/bin/env python3
"""Layer-wise W4/W2 behavioral-drift proxy on Qwen3-0.6B."""
import argparse
import gc
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


def quant_weight_(weight,bits,group=128):
    qmax=2**(bits-1)-1; x=weight.detach().float().flatten(); pad=(-x.numel())%group
    if pad: x=torch.nn.functional.pad(x,(0,pad))
    b=x.view(-1,group); scale=b.abs().amax(1,keepdim=True).clamp_min(1e-12)/qmax
    q=(b/scale).round().clamp(-qmax,qmax).mul(scale).flatten()[:weight.numel()].view_as(weight)
    weight.copy_(q.to(weight.dtype))


def run(directory,tok,batch,bits=None):
    from transformers import AutoModelForCausalLM
    model=AutoModelForCausalLM.from_pretrained(directory,local_files_only=True,dtype=torch.float32).eval()
    count=elements=0
    if bits:
        with torch.no_grad():
            for name,m in model.named_modules():
                if isinstance(m,torch.nn.Linear) and name!='lm_head':
                    quant_weight_(m.weight,bits); count+=1; elements+=m.weight.numel()
    with torch.inference_mode(): out=model(**batch,use_cache=False,output_hidden_states=True,return_dict=True)
    hidden=torch.stack([x[:,-1].float().cpu() for x in out.hidden_states])
    logits=out.logits[:,-1].float().cpu()
    del model; gc.collect()
    return hidden,logits,count,elements


def entropy(logits):
    p=logits.softmax(-1); return (-(p*p.clamp_min(1e-30).log()).sum(-1)).mean().item()


def main():
    p=argparse.ArgumentParser(); p.add_argument('--model-dir'); args=p.parse_args()
    from transformers import AutoTokenizer
    d=model_dir(args.model_dir); tok=AutoTokenizer.from_pretrained(d,local_files_only=True)
    prompts=['I prefer meeting many people, but I also need quiet time. The best description is','面对新任务时，我通常先制定计划，然后根据反馈调整。最符合我的选项是']
    batch=tok(prompts,return_tensors='pt',padding=True)
    base_h,base_l,_,_=run(d,tok,batch)
    for bits in (4,2):
        h,l,count,elements=run(d,tok,batch,bits)
        layer_cos=torch.nn.functional.cosine_similarity(base_h,h,dim=-1).mean(1)
        logit_cos=torch.nn.functional.cosine_similarity(base_l,l,dim=-1).mean().item()
        top=(base_l.argmax(-1)==l.argmax(-1)).float().mean().item()
        worst=int(layer_cos.argmin())
        print(f'W{bits} layers={count} elements={elements} top1_match={top:.6f} logit_cosine={logit_cos:.8f} entropy={entropy(l):.8f} worst_layer={worst} worst_layer_cosine={layer_cos[worst].item():.8f}')
        assert count==196 and elements==440401920 and torch.isfinite(l).all()
    print(f'FP32 entropy={entropy(base_l):.8f} hidden_states={base_h.shape[0]} prompts={len(prompts)}')


if __name__=='__main__': main()
