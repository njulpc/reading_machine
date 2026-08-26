#!/usr/bin/env python3
"""Projection-residual quantization on real Qwen3 embedding vectors."""
import argparse, glob, os
import torch

def ckpt(p=None):
    h=[p] if p else glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not h: raise FileNotFoundError('Qwen checkpoint missing')
    return h[0]

def kmeans(x,k,iters=8):
    c=x[torch.linspace(0,len(x)-1,k).long()].clone()
    for _ in range(iters):
        sim=torch.nn.functional.cosine_similarity(x[:,None,:],c[None,:,:],dim=-1); assign=sim.argmax(1)
        # Top-3 soft refinement around each sample, rather than hard-only updates.
        vals,ids=sim.topk(min(3,k),1); probs=torch.softmax(vals/0.07,1); new=[]
        for j in range(k):
            weight=(probs*(ids==j)).sum(1); new.append((weight[:,None]*x).sum(0)/weight.sum().clamp_min(1e-9))
        c=torch.stack(new)
    return c,assign

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint'); ap.add_argument('--samples',type=int,default=512); ap.add_argument('--levels',type=int,default=3); ap.add_argument('--codebook-size',type=int,default=16); a=ap.parse_args()
    from safetensors import safe_open
    with safe_open(ckpt(a.checkpoint),framework='pt',device='cpu') as f:
        key=next(k for k in f.keys() if k.endswith('embed_tokens.weight')); x=f.get_tensor(key)[:a.samples].float()
    x=x-x.mean(0,keepdim=True); residual=x.clone(); carry=[]; codes=[]
    for _ in range(a.levels):
        c,idx=kmeans(residual,a.codebook_size); chosen=c[idx]; denom=chosen.square().sum(1,keepdim=True).clamp_min(1e-12)
        projection=(residual*chosen).sum(1,keepdim=True)/denom*chosen
        next_residual=residual-projection
        carry.append(float((next_residual*chosen).sum(1).abs().mean())); codes.append(idx); residual=next_residual
    unique=len(torch.unique(torch.stack(codes,1),dim=0)); bits=a.levels*torch.log2(torch.tensor(float(a.codebook_size)))
    print(f'embedding={key} samples={a.samples} levels={a.levels} K={a.codebook_size} bits_per_sid={float(bits):.1f}')
    print('projection_carry='+','.join(f'{v:.3e}' for v in carry)+f' unique_sids={unique}')
    assert max(carry)<1e-4 and unique>1

if __name__=='__main__': main()
