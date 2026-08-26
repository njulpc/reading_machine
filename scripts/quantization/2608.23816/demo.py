#!/usr/bin/env python3
"""Qwen3-0.6B AQLoRA layer-allocation reference (arXiv:2608.23816)."""
import argparse, glob, os, random
import torch

NF4 = torch.tensor([-1.0,-0.6961928,-0.5250731,-0.3949175,-0.2844414,-0.1847734,-0.0910500,0.0,0.0795803,0.1609302,0.2461123,0.3379152,0.4407098,0.5626170,0.7229568,1.0])

def checkpoint(path=None):
    hits=[path] if path else glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not hits: raise FileNotFoundError('pass --checkpoint for Qwen3-0.6B model.safetensors')
    return hits[0]

def nf4_mse(x, group=64):
    flat=x.float().flatten(); pad=(-flat.numel())%group
    if pad: flat=torch.nn.functional.pad(flat,(0,pad))
    b=flat.view(-1,group); scale=b.abs().amax(1).clamp_min(1e-12); z=b/scale[:,None]
    idx=(z[:,:,None]-NF4[None,None,:]).abs().argmin(-1)
    hat=NF4[idx]*scale[:,None]
    if pad: hat=hat.flatten()[:-pad]
    else: hat=hat.flatten()
    return float((hat-x.float().flatten()).square().mean())

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint'); ap.add_argument('--protect-fraction',type=float,default=.15); ap.add_argument('--max-elements',type=int,default=262144); a=ap.parse_args()
    from safetensors import safe_open
    rows=[]
    with safe_open(checkpoint(a.checkpoint),framework='pt',device='cpu') as f:
        keys=[k for k in f.keys() if k.endswith(('q_proj.weight','k_proj.weight','v_proj.weight','o_proj.weight'))]
        for k in keys:
            w=f.get_slice(k)[:].flatten()[:a.max_elements]
            rows.append((nf4_mse(w),k,w.numel()))
    rows.sort(reverse=True); keep=max(1,round(len(rows)*a.protect_fraction)); protected=rows[:keep]
    random.Random(23816).shuffle(rows); random_control=rows[:keep]
    total=sum(n for _,_,n in rows); fp16=sum(n for _,_,n in protected)
    bytes_est=fp16*2+(total-fp16)*.5
    print(f'layers={len(rows)} protected={keep} protect_fraction={keep/len(rows):.4f}')
    print(f'estimated_weight_bytes={bytes_est:.0f} effective_bits={bytes_est*8/total:.4f}')
    print('top_protected='+','.join(k for _,k,_ in protected[:8]))
    print(f'top_mean_nf4_mse={sum(x for x,_,_ in protected)/keep:.8e}')
    print(f'random_mean_nf4_mse={sum(x for x,_,_ in random_control)/keep:.8e}')
    assert all(protected[i][0]>=protected[i+1][0] for i in range(len(protected)-1))

if __name__=='__main__': main()
