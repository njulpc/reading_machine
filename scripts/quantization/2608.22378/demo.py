#!/usr/bin/env python3
"""Software simulation of variable-mantissa approximate PEs on Qwen weights."""
import argparse, glob, os, torch

def checkpoint(p=None):
    if p and os.path.isfile(p): return p
    hits=glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"))+glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors")
    if not hits: raise FileNotFoundError("pass --checkpoint")
    return hits[0]

def load_matrix(path):
    from safetensors import safe_open
    with safe_open(path,framework="pt",device="cpu") as f:
        key=next(k for k in f.keys() if k.endswith("q_proj.weight")); w=f.get_tensor(key).float()
    return key,w[:256,:256].contiguous()

def truncate_mantissa(x,keep):
    if keep>=23:return x.clone()
    i=x.contiguous().view(torch.int32); drop=23-keep; mask=~((1<<drop)-1)
    return (i & mask).view(torch.float32)

def metric(ref,y):
    rr=float(torch.sqrt(torch.mean((ref-y)**2))/torch.sqrt(torch.mean(ref**2)).clamp_min(1e-20))
    cos=float(torch.nn.functional.cosine_similarity(ref.flatten(),y.flatten(),dim=0)); return rr,cos

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--checkpoint");a=ap.parse_args();torch.manual_seed(7)
    path=checkpoint(a.checkpoint);key,w=load_matrix(path);x=torch.randn(32,256);ref=x@w.T
    print(f"checkpoint={path}\ntensor={key} slice={tuple(w.shape)}")
    for name,nominal,approx in [("FP32",23,16),("TF32",10,8),("BF16",7,5)]:
        base=truncate_mantissa(x,nominal)@truncate_mantissa(w,nominal).T
        y=truncate_mantissa(x,approx)@truncate_mantissa(w,approx).T
        rb,cb=metric(ref,base);ra,ca=metric(ref,y)
        print(f"{name} nominal_keep={nominal} rel_rmse={rb:.8f} cos={cb:.8f} | approx_keep={approx} rel_rmse={ra:.8f} cos={ca:.8f}")
    assert torch.isfinite(ref).all()

if __name__=="__main__":main()
