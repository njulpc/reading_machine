#!/usr/bin/env python3
"""Activation-weighted seeded residual repair for an INT4 Qwen weight slice."""
import argparse, glob, os, torch

def checkpoint(p=None):
    if p and os.path.isfile(p):return p
    hits=glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"))+glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors")
    if not hits:raise FileNotFoundError("pass --checkpoint")
    return hits[0]

def load(path):
    from safetensors import safe_open
    with safe_open(path,framework="pt",device="cpu") as f:
        key=next(k for k in f.keys() if k.endswith("q_proj.weight"));w=f.get_tensor(key).float()[:256,:256].contiguous()
    return key,w

def int4_rtn(w,group=64):
    flat=w.flatten();out=torch.empty_like(flat)
    for i in range(0,flat.numel(),group):
        v=flat[i:i+group];s=max(float(v.abs().max())/7,1e-12);out[i:i+group]=torch.round(v/s).clamp(-7,7)*s
    return out.view_as(w)

def repair(w,w0,x,block=256,candidates=16):
    r=(w-w0).flatten();importance=x.square().mean(0).repeat(w.shape[0]).reshape(w.shape).flatten();rec=torch.zeros_like(r);selectors=[];coeff=[]
    for bi,i in enumerate(range(0,r.numel(),block)):
        v=r[i:i+block];imp=importance[i:i+block];best=None
        for seed in range(candidates):
            g=torch.Generator().manual_seed(100000*bi+seed);b=(torch.randint(0,2,(v.numel(),),generator=g)*2-1).float()
            c=(imp*v*b).sum()/(imp*b.square()).sum().clamp_min(1e-12);loss=((v-c*b).square()*imp).mean()
            if best is None or loss<best[0]:best=(loss,seed,b,c)
        _,seed,b,c=best;selectors.append(seed);coeff.append(float(c));rec[i:i+block]=b*c
    # Quantize one coefficient per block to signed 4-bit with a shared scale.
    scale=max(max(abs(c) for c in coeff)/7,1e-12);cq=torch.tensor(coeff).div(scale).round().clamp(-7,7)*scale
    for j,i in enumerate(range(0,r.numel(),block)):
        seed=selectors[j];g=torch.Generator().manual_seed(100000*j+seed);b=(torch.randint(0,2,(min(block,r.numel()-i),),generator=g)*2-1).float();rec[i:i+len(b)]=b*cq[j]
    return (w0.flatten()+rec).view_as(w),selectors,cq

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--checkpoint");a=ap.parse_args();torch.manual_seed(11)
    path=checkpoint(a.checkpoint);key,w=load(path);x=torch.randn(64,w.shape[1]);w0=int4_rtn(w);wr,sel,c=repair(w,w0,x)
    y=x@w.T;y0=x@w0.T;yr=x@wr.T
    mse0=float(torch.mean((y-y0)**2));mser=float(torch.mean((y-yr)**2));closed=(mse0-mser)/mse0*100
    sidecar_bits=len(sel)*(4+4+32);bpw=sidecar_bits/w.numel()
    print(f"checkpoint={path}\ntensor={key} slice={tuple(w.shape)}")
    print(f"INT4_output_mse={mse0:.10g} repaired_output_mse={mser:.10g} gap_closed={closed:.3f}%")
    print(f"selectors={len(sel)} candidates=16 sidecar_estimated_bits_per_weight={bpw:.6f}")
    assert torch.isfinite(yr).all()

if __name__=="__main__":main()
