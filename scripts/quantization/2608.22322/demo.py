#!/usr/bin/env python3
"""AL optimizer-state quantization on real Qwen3-0.6B weights."""
import argparse, glob, math, os
import torch

def find_checkpoint(explicit=None):
    if explicit and os.path.isfile(explicit): return explicit
    pats=[os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"),
          "/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"]
    hits=sum((glob.glob(p) for p in pats),[])
    if not hits: raise FileNotFoundError("Qwen3-0.6B model.safetensors not found; pass --checkpoint")
    return hits[0]

def load_weight(path, max_elements=524288):
    from safetensors import safe_open
    with safe_open(path, framework="pt", device="cpu") as f:
        keys=[k for k in f.keys() if k.endswith("q_proj.weight")]
        key=keys[0] if keys else next(k for k in f.keys() if k.endswith("weight"))
        w=f.get_tensor(key).float().flatten()[:max_elements].contiguous()
    return key,w

def al_quantize(x,bits=8,block=256):
    assert torch.all(x>=0); levels=(1<<bits)-2; out=torch.zeros_like(x); codes=[]; meta=[]
    for i in range(0,x.numel(),block):
        v=x[i:i+block]; nz=v>0
        if not nz.any(): codes.append(torch.zeros_like(v,dtype=torch.int32)); meta.append((0.,0.)); continue
        lo=torch.log2(v[nz].min()); hi=torch.log2(v[nz].max()); span=max(float(hi-lo),1e-12)
        q=torch.zeros_like(v,dtype=torch.int32)
        q[nz]=(1+torch.round((torch.log2(v[nz])-lo)/span*levels)).clamp(1,levels+1).int()
        rec=torch.zeros_like(v); rec[nz]=torch.pow(2.0,lo+(q[nz].float()-1)/levels*span)
        out[i:i+block]=rec; codes.append(q); meta.append((float(lo),float(hi)))
    return out,torch.cat(codes),meta

def signed_int8(x,block=256):
    out=torch.empty_like(x)
    for i in range(0,x.numel(),block):
        v=x[i:i+block]; s=max(float(v.abs().max())/127,1e-12); out[i:i+block]=torch.round(v/s).clamp(-127,127)*s
    return out

def rel_rmse(a,b): return float(torch.sqrt(torch.mean((a-b)**2))/torch.sqrt(torch.mean(a**2)).clamp_min(1e-20))

def self_test():
    x=torch.tensor([0.,1e-6,1e-3,1.,10.]); y,q,_=al_quantize(x,8,8)
    assert y[0]==0 and q[0]==0 and torch.isfinite(y).all()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--checkpoint"); ap.add_argument("--max-elements",type=int,default=524288); a=ap.parse_args()
    self_test(); path=find_checkpoint(a.checkpoint); key,w=load_weight(path,a.max_elements)
    second=w.square(); momentum=w
    al8,codes,meta=al_quantize(second,8); m8=signed_int8(momentum)
    n=w.numel(); blocks=math.ceil(n/256); packed=n+n+blocks*8; baseline=2*n*4
    print(f"checkpoint={path}\ntensor={key} elements={n}")
    print(f"AL8_second_rel_rmse={rel_rmse(second,al8):.8f} zeros_preserved={bool(torch.all(al8[second==0]==0))}")
    print(f"INT8_momentum_rel_rmse={rel_rmse(momentum,m8):.8f}")
    print(f"estimated_state_bytes_fp32={baseline} quantized={packed} compression={baseline/packed:.3f}x")

if __name__=="__main__": main()
