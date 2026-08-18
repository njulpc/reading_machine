#!/usr/bin/env python3
"""Small real-weight Schur-complement groupwise 2-bit optimization."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.self_attn.q_proj.weight"

def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:
        return f.get_tensor(KEY)[:32,:128].float().contiguous()

def affine_init(w):
    lo=w.amin(1,keepdim=True); hi=w.amax(1,keepdim=True)
    s=((hi-lo)/3).clamp_min(1e-8); z=(-lo/s).round().clamp(0,3)
    q=(w/s+z).round().clamp(0,3); return q,s,z

def optimize_group(w,h_eff,iters=2):
    q,s,z=affine_init(w)
    for _ in range(iters):
        # Least-squares refit w ~= s*q + b, with b=-s*z.
        qm=q-q.mean(1,keepdim=True); wm=w-w.mean(1,keepdim=True)
        s=(qm*wm).sum(1,keepdim=True)/(qm.square().sum(1,keepdim=True).clamp_min(1e-8))
        s=s.abs().clamp_min(1e-8); b=w.mean(1,keepdim=True)-s*q.mean(1,keepdim=True); z=(-b/s).clamp(0,3)
        deq=s*(q-z); err=deq-w
        for j in range(w.shape[1]):
            best=q[:,j].clone(); best_loss=torch.einsum("bi,ij,bj->b",err,h_eff,err)
            old=deq[:,j].clone()
            for code in range(4):
                trial=err.clone(); trial[:,j]=s[:,0]*(code-z[:,0])-w[:,j]
                loss=torch.einsum("bi,ij,bj->b",trial,h_eff,trial)
                take=loss<best_loss; best=torch.where(take,torch.full_like(best,code),best); best_loss=torch.where(take,loss,best_loss)
            q[:,j]=best; deq[:,j]=s[:,0]*(best-z[:,0]); err[:,j]=deq[:,j]-w[:,j]
    return s*(q-z)

def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--group-size",type=int,default=32);p.add_argument("--seed",type=int,default=5)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x=torch.randn(96,w.shape[1]);h=x.T@x/x.shape[0]+1e-3*torch.eye(w.shape[1])
    out=[]
    for start in range(0,w.shape[1],a.group_size):
        end=min(start+a.group_size,w.shape[1]); g=torch.arange(start,end); r=torch.arange(end,w.shape[1])
        hgg=h[g][:,g]
        if len(r): h_eff=hgg-h[g][:,r]@torch.linalg.solve(h[r][:,r],h[r][:,g])
        else: h_eff=hgg
        out.append(optimize_group(w[:,g],h_eff))
    qw=torch.cat(out,1); base=torch.cat([affine_init(w[:,s:s+a.group_size])[1]*(affine_init(w[:,s:s+a.group_size])[0]-affine_init(w[:,s:s+a.group_size])[2]) for s in range(0,w.shape[1],a.group_size)],1)
    ref=x@w.T
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} bits=2 group={a.group_size}")
    print(f"affine_init_output_mse={torch.nn.functional.mse_loss(x@base.T,ref).item():.8g}")
    print(f"schur_coordinate_output_mse={torch.nn.functional.mse_loss(x@qw.T,ref).item():.8g}")

if __name__=="__main__":main()
