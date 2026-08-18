#!/usr/bin/env python3
"""Small real-weight Schur-complement groupwise 2-bit optimization."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.self_attn.q_proj.weight"

def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:
        return f.get_tensor(KEY)[:32,:256].float().contiguous()

def affine_init(w, bits=2):
    qmax=(1 << bits)-1
    lo=w.amin(1,keepdim=True); hi=w.amax(1,keepdim=True)
    s=((hi-lo)/qmax).clamp_min(1e-8); z=(-lo/s).round().clamp(0,qmax)
    q=(w/s+z).round().clamp(0,qmax); return q,s,z

def refit_grid(q, s_mat, target, bits=2):
    rows=q.shape[0]; best_loss=torch.full((rows,),float("inf")); best_s=torch.ones(rows); best_z=torch.zeros(rows)
    for zero in range(1 << bits):
        u=q-zero
        curvature=torch.einsum("bi,ij,bj->b",u,s_mat,u).clamp_min(1e-8)
        linear=(target*u).sum(1)
        scale=(linear/curvature).clamp_min(1e-8)
        loss=.5*scale.square()*curvature-scale*linear
        take=loss<best_loss; best_loss=torch.where(take,loss,best_loss); best_s=torch.where(take,scale,best_s); best_z=torch.where(take,torch.full_like(best_z,zero),best_z)
    return best_s[:,None],best_z[:,None]

def optimize_group(w,s_mat,target,iters=2,bits=2):
    q,s,z=affine_init(w)
    for _ in range(iters):
        s,z=refit_grid(q,s_mat,target,bits)
        deq=s*(q-z); phi=deq@s_mat
        for j in range(w.shape[1]):
            codes=torch.arange(1 << bits,dtype=w.dtype)[None,:]
            values=s*(codes-z)
            cross=phi[:,j]-deq[:,j]*s_mat[j,j]-target[:,j]
            losses=.5*s_mat[j,j]*values.square()+cross[:,None]*values
            best=losses.argmin(1); new=values.gather(1,best[:,None])[:,0]
            delta=new-deq[:,j]; q[:,j]=best.to(q); deq[:,j]=new; phi+=delta[:,None]*s_mat[j]
    return s*(q-z)

def schur_quantize(w,h,group_size):
    c=w@h; qw=torch.zeros_like(w)
    for start in range(0,w.shape[1],group_size):
        end=min(start+group_size,w.shape[1]); g=slice(start,end); r=slice(end,w.shape[1])
        c_eff_g=c[:,g]-(qw[:,:start]@h[:start,g] if start else 0)
        hgg=h[g,g]
        if end<w.shape[1]:
            c_eff_r=c[:,r]-(qw[:,:start]@h[:start,r] if start else 0)
            solve=torch.linalg.solve(h[r,r],h[r,g])
            s_mat=hgg-h[g,r]@solve; target=c_eff_g-c_eff_r@solve
        else:
            s_mat=hgg; target=c_eff_g
        qw[:,g]=optimize_group(w[:,g],s_mat,target)
    return qw

def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--group-size",type=int,default=128);p.add_argument("--seed",type=int,default=5)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x=torch.randn(96,w.shape[1]);h=x.T@x/x.shape[0]+1e-3*torch.eye(w.shape[1])
    qw=schur_quantize(w,h,a.group_size); base=torch.cat([affine_init(w[:,s:s+a.group_size])[1]*(affine_init(w[:,s:s+a.group_size])[0]-affine_init(w[:,s:s+a.group_size])[2]) for s in range(0,w.shape[1],a.group_size)],1)
    ref=x@w.T
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} bits=2 group={a.group_size}")
    print(f"affine_init_output_mse={torch.nn.functional.mse_loss(x@base.T,ref).item():.8g}")
    print(f"schur_coordinate_output_mse={torch.nn.functional.mse_loss(x@qw.T,ref).item():.8g}")

if __name__=="__main__":main()
