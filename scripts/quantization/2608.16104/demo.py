#!/usr/bin/env python3
"""Per-expert INT4/FP4 fake-QAT using partitions of a Qwen3 FFN."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.mlp.up_proj.weight"
GRID=torch.tensor([-6.,-4.,-3.,-2.,-1.5,-1.,-.5,0.,.5,1.,1.5,2.,3.,4.,6.])
def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:return f.get_tensor(KEY)[:128,:256].float().contiguous()
def ste_qint4(w):
    s=w.abs().amax(1,keepdim=True).clamp_min(1e-8)/7;q=torch.round(w/s).clamp(-7,7)*s;return w+(q-w).detach()
def ste_fp4(x):
    clip=torch.quantile(x.abs().flatten(),.999).clamp_min(1e-8);s=clip/6;z=x/s
    idx=(z[...,None]-GRID.to(x)).abs().argmin(-1);q=GRID.to(x)[idx]*s;return x+(q-x).detach(),s
def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--experts",type=int,default=8);p.add_argument("--qat-steps",type=int,default=5);p.add_argument("--seed",type=int,default=17)
    a=p.parse_args();torch.manual_seed(a.seed);target=load_weight(a.model_dir);shadow=target.clone().requires_grad_(True);opt=torch.optim.SGD([shadow],lr=1e-3);x=torch.randn(32,target.shape[1]);ref=x@target.T
    rows=target.shape[0]//a.experts;scales=[]
    for _ in range(a.qat_steps):
        ys=[];scales=[]
        for e in range(a.experts):
            xe,s=ste_fp4(x);scales.append(float(s));ys.append(xe@ste_qint4(shadow[e*rows:(e+1)*rows]).T)
        y=torch.cat(ys,1);loss=torch.nn.functional.mse_loss(y,ref);opt.zero_grad();loss.backward();opt.step()
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(target.shape)} experts={a.experts}")
    print(f"qat_steps={a.qat_steps} output_mse={loss.item():.8g}")
    print("per_expert_fp4_scales="+",".join(f"{s:.6g}" for s in scales))
if __name__=="__main__":main()
