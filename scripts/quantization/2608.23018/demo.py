#!/usr/bin/env python3
"""Quantized low-rank residual factors using Qwen3-0.6B layer dimensions."""
import argparse, glob, os, torch

def checkpoint(p=None):
    if p and os.path.isfile(p):return p
    hits=glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"))+glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors")
    if not hits:raise FileNotFoundError("pass --checkpoint")
    return hits[0]

def dims(path):
    from safetensors import safe_open
    with safe_open(path,framework="pt",device="cpu") as f:
        key=next(k for k in f.keys() if k.endswith("q_proj.weight")); shape=tuple(f.get_slice(key).get_shape())
    return key,shape

def q8(x):
    s=max(float(x.abs().max())/127,1e-12);q=torch.round(x/s).clamp(-127,127).to(torch.int8);return q.float()*s,q.numel()+4

def low_rank(m,n,rank,seed):
    g=torch.Generator().manual_seed(seed);return torch.randn(m,rank,generator=g)*.02,torch.randn(rank,n,generator=g)*.02

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--checkpoint");ap.add_argument("--rank",type=int,default=8);ap.add_argument("--rows",type=int,default=256);ap.add_argument("--cols",type=int,default=256);a=ap.parse_args()
    path=checkpoint(a.checkpoint);key,shape=dims(path);m=min(a.rows,shape[0]);n=min(a.cols,shape[1]);r=a.rank
    # Difference of two rank-r LoRA updates has rank <=2r, matching SplitLite's activation-residual prior.
    a1,b1=low_rank(m,n,r,1);a2,b2=low_rank(m,n,r,2);res=a2@b2-a1@b1
    u,s,vh=torch.linalg.svd(res,full_matrices=False);k=min(2*r,len(s));U=u[:,:k]*s[:k];V=vh[:k]
    Uq,bu=q8(U);Vq,bv=q8(V);rec=Uq@Vq;dense=res.numel()*4;packed=bu+bv
    rel=float(torch.linalg.norm(res-rec)/torch.linalg.norm(res));print(f"checkpoint={path}\ntensor={key} full_shape={shape} simulated_residual={m}x{n} lora_rank={r} svd_rank={k}")
    print(f"quantized_factor_rel_error={rel:.8f} dense_fp32_bytes={dense} factor_int8_bytes={packed} compression={dense/packed:.3f}x")
    assert torch.linalg.matrix_rank(res,tol=1e-5)<=2*r+1

if __name__=="__main__":main()
