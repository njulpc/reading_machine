#!/usr/bin/env python3
"""Distribution-aware activation binarization on a Qwen3-0.6B linear layer."""
import argparse
from pathlib import Path
import torch

KEY="model.layers.0.mlp.gate_proj.weight"
def load_weight(path):
    from safetensors import safe_open
    with safe_open(str(path/"model.safetensors"),framework="pt",device="cpu") as f:return f.get_tensor(KEY)[:128,:256].float().contiguous()
class ScaleNet(torch.nn.Module):
    def __init__(self,channels):
        super().__init__(); self.net=torch.nn.Sequential(torch.nn.Linear(3,8),torch.nn.Tanh(),torch.nn.Linear(8,1)); self.channels=channels
        torch.nn.init.zeros_(self.net[-1].weight); torch.nn.init.zeros_(self.net[-1].bias)
    def forward(self,x):
        desc=torch.stack([x.mean(0),x.abs().mean(0),x.std(0,unbiased=False)],1)
        norm=desc/(desc.abs().mean(0,keepdim=True).clamp_min(1e-6))
        # Residual parameterization starts exactly at the abs-mean baseline.
        return (desc[:,1:2]*(1+0.5*torch.tanh(self.net(norm)))).T.clamp_min(1e-6)
def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--steps",type=int,default=100);p.add_argument("--seed",type=int,default=23)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x=torch.randn(64,w.shape[1]);ref=x@w.T
    wscale=w.abs().mean(1,keepdim=True);bw=w.sign().masked_fill(w==0,1)*wscale
    baseline_scale=x.abs().mean(0,keepdim=True);baseline=(x.sign()*baseline_scale)@bw.T
    net=ScaleNet(x.shape[1]);opt=torch.optim.Adam(net.parameters(),lr=1e-2)
    for _ in range(a.steps):
        scale=net(x);bx=x.sign()*scale;y=bx@bw.T;loss=torch.nn.functional.mse_loss(y,ref);opt.zero_grad();loss.backward();opt.step()
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} binary_weights_and_activations=1bit")
    print(f"absmean_scale_mse={torch.nn.functional.mse_loss(baseline,ref).item():.8g}")
    print(f"distribution_aware_mse={loss.item():.8g} descriptors=mean,absmean,std steps={a.steps}")
if __name__=="__main__":main()
