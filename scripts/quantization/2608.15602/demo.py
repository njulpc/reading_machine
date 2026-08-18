#!/usr/bin/env python3
"""Decoupled binary bases, saliency residual and an actual 8-value LUT."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.mlp.down_proj.weight"
def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:return f.get_tensor(KEY)[:64,:256].float().contiguous()

def lut_binary_mm(x, signs, row_scale, group=8):
    batch,out=x.shape[0],signs.shape[0]; y=torch.zeros(batch,out)
    powers=(1<<torch.arange(group)).long()
    for start in range(0,x.shape[1],group):
        chunk=x[:,start:start+group]; sg=signs[:,start:start+group]
        if chunk.shape[1]<group:
            pad=group-chunk.shape[1];chunk=torch.nn.functional.pad(chunk,(0,pad));sg=torch.nn.functional.pad(sg,(0,pad),value=1)
        patterns=((sg>0).long()*powers).sum(1)
        ids=torch.arange(1<<group)
        pm=(2*((ids[:,None]>>torch.arange(group))&1)-1).float()
        table=chunk@pm.T
        y+=table[:,patterns]
    return y*row_scale.T

def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--salient-fraction",type=float,default=.05);p.add_argument("--seed",type=int,default=9)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x=torch.randn(8,w.shape[1])
    row=w.abs().mean(1,keepdim=True);b1=w.sign().masked_fill(w==0,1);r=w-row*b1
    col=r.abs().mean(0,keepdim=True);b2=r.sign().masked_fill(r==0,1);approx=row*b1+col*b2
    hdiag=x.square().mean(0);score=(w-approx).square()*hdiag
    k=max(1,int(score.numel()*a.salient_fraction));mask=torch.zeros_like(score,dtype=torch.bool);mask.view(-1)[torch.topk(score.flatten(),k).indices]=True
    salient=torch.where(mask,w-approx,torch.zeros_like(w))
    y_lut=lut_binary_mm(x,b1,row)+x@(col*b2+salient).T;ref=x@w.T
    direct=x@(row*b1+col*b2+salient).T;assert torch.allclose(y_lut,direct,atol=1e-4,rtol=1e-4)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)}")
    print(f"salient_fraction={mask.float().mean().item():.6f} output_mse={torch.nn.functional.mse_loss(y_lut,ref).item():.8g}")
    print("binary_group8_lut_equivalence=PASS")
if __name__=="__main__":main()
