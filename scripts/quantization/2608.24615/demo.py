#!/usr/bin/env python3
"""Bangla-sensitive Qwen3 projection audit under per-row INT8 and INT4."""
import argparse, glob, os
import torch

def model_dir(p=None):
    if p: return p if os.path.isdir(p) else os.path.dirname(p)
    h=glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not h: raise FileNotFoundError('Qwen checkpoint missing')
    return os.path.dirname(h[0])

def quant(w,bits):
    qmax=2**(bits-1)-1; s=w.abs().amax(1,keepdim=True).clamp_min(1e-12)/qmax
    return torch.round(w/s).clamp(-qmax-1,qmax)*s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint'); ap.add_argument('--text',default='বাংলা ভাষায় যুক্তি ও সাধারণ জ্ঞান বোঝার ক্ষমতা গুরুত্বপূর্ণ।'); a=ap.parse_args(); d=model_dir(a.checkpoint)
    from safetensors import safe_open
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(d,local_files_only=True); ids=tok(a.text,return_tensors='pt')['input_ids'][0]
    with safe_open(os.path.join(d,'model.safetensors'),framework='pt',device='cpu') as f:
        ek=next(k for k in f.keys() if k.endswith('embed_tokens.weight')); wk=next(k for k in f.keys() if k.endswith('q_proj.weight'))
        x=f.get_tensor(ek)[ids].float(); w=f.get_tensor(wk).float()
    ref=x@w.T
    print(f'tokens={len(ids)} token_ids={ids.tolist()} embedding={ek} weight={wk}')
    for bits in (8,4):
        out=x@quant(w,bits).T; mae=float((out-ref).abs().mean()); cos=float(torch.nn.functional.cosine_similarity(out,ref,dim=-1).mean())
        print(f'W{bits}A16 rowwise_mae={mae:.8f} cosine={cos:.8f} weight_compression_vs_fp16={16/bits:.2f}x')
    assert len(ids)>2

if __name__=='__main__': main()
