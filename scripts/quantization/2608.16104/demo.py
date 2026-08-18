#!/usr/bin/env python3
"""Per-expert INT4/asymmetric-4-bit fake-QAT on routed Qwen FFN slices."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.mlp.up_proj.weight"
def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:return f.get_tensor(KEY)[:128,:256].float().contiguous()
def ste_qint4(w):
    s=w.abs().amax(1,keepdim=True).clamp_min(1e-8)/7;q=torch.round(w/s).clamp(-7,7)*s;return w+(q-w).detach()
def ste_asym4(x,scale,zero):
    lo=torch.quantile(x,.0005);hi=torch.quantile(x,.9995);clipped=x.clamp(lo,hi)
    code=clipped/scale+zero;rounded=code+(code.round()-code).detach()
    return scale*(rounded.clamp(0,15)-zero)
def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--experts",type=int,default=8);p.add_argument("--qat-steps",type=int,default=5);p.add_argument("--seed",type=int,default=17)
    a=p.parse_args();torch.manual_seed(a.seed);target=load_weight(a.model_dir);shadow=target.clone().requires_grad_(True);x=torch.randn(64,target.shape[1])
    rows=target.shape[0]//a.experts;init=[]
    for e in range(a.experts):
        xe=x[e::a.experts];lo=torch.quantile(xe,.0005);hi=torch.quantile(xe,.9995);s=((hi-lo)/15).clamp_min(1e-8);init.append((s,(-lo/s).clamp(0,15)))
    scales=torch.nn.Parameter(torch.stack([v[0] for v in init]));zeros=torch.nn.Parameter(torch.stack([v[1] for v in init]));opt=torch.optim.SGD([shadow,scales,zeros],lr=1e-3)
    for _ in range(a.qat_steps):
        losses=[]
        for e in range(a.experts):
            xe=x[e::a.experts];xq=ste_asym4(xe,scales[e].clamp_min(1e-8),zeros[e]);w=target[e*rows:(e+1)*rows];wq=ste_qint4(shadow[e*rows:(e+1)*rows]);losses.append(torch.nn.functional.mse_loss(xq@wq.T,xe@w.T))
        loss=torch.stack(losses).mean();opt.zero_grad();loss.backward();opt.step()
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(target.shape)} experts={a.experts}")
    print(f"qat_steps={a.qat_steps} output_mse={loss.item():.8g}")
    print("per_expert_scales="+",".join(f"{s:.6g}" for s in scales.detach().tolist()))
    print("per_expert_zero_points="+",".join(f"{z:.6g}" for z in zeros.detach().tolist()))
if __name__=="__main__":main()
