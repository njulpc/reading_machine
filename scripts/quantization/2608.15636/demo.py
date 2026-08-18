#!/usr/bin/env python3
"""Residual-ranked blockwise mixed precision on Qwen3-0.6B."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.self_attn.o_proj.weight"
def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:return f.get_tensor(KEY)[:256,:256].float().contiguous()

def qsym(block,bits):
    qmax=(1<<(bits-1))-1;scale=block.abs().amax().clamp_min(1e-8)/qmax
    return torch.round(block/scale).clamp(-qmax,qmax)*scale

def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--block",type=int,default=64);p.add_argument("--eight-bit-fraction",type=float,default=.25);p.add_argument("--seed",type=int,default=13)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x=torch.randn(32,w.shape[1]);ref=x@w.T
    specs=[]
    for r in range(0,w.shape[0],a.block):
        for c in range(0,w.shape[1],a.block):
            b=w[r:r+a.block,c:c+a.block];q4=qsym(b,4);score=((b-q4).square()*x[:,c:c+b.shape[1]].square().mean(0)).mean();specs.append((score.item(),r,c,q4,qsym(b,8)))
    keep=max(1,round(len(specs)*a.eight_bit_fraction));high={(r,c) for _,r,c,_,_ in sorted(specs,reverse=True)[:keep]}
    mixed=torch.empty_like(w);all4=torch.empty_like(w)
    for _,r,c,q4,q8 in specs:
        all4[r:r+q4.shape[0],c:c+q4.shape[1]]=q4;mixed[r:r+q4.shape[0],c:c+q4.shape[1]]=q8 if (r,c) in high else q4
    avg_bits=(keep*8+(len(specs)-keep)*4)/len(specs)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} block={a.block}")
    print(f"all4_output_mse={torch.nn.functional.mse_loss(x@all4.T,ref).item():.8g}")
    print(f"mixed_output_mse={torch.nn.functional.mse_loss(x@mixed.T,ref).item():.8g} average_bits={avg_bits:.2f}")
if __name__=="__main__":main()
