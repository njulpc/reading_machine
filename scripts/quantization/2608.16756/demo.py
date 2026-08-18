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
        super().__init__(); self.bias=torch.nn.Parameter(torch.zeros(channels));self.fuse=torch.nn.Conv1d(1,1,kernel_size=3,stride=3);self.channels=channels
    def forward(self,x):
        adjusted=x+self.bias
        desc=torch.stack([adjusted.mean(0),adjusted.abs().mean(0),adjusted.std(0,unbiased=False)],1)
        return torch.sigmoid(self.fuse(desc.reshape(1,1,-1))).reshape(1,self.channels).clamp_min(1e-6),adjusted
def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--steps",type=int,default=100);p.add_argument("--seed",type=int,default=23)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x=torch.randn(64,w.shape[1]);ref=x@w.T
    wscale=w.abs().mean(1,keepdim=True);bw=w.sign().masked_fill(w==0,1)*wscale
    baseline_scale=x.abs().mean(0,keepdim=True);baseline=(x.sign()*baseline_scale)@bw.T
    net=ScaleNet(x.shape[1]);opt=torch.optim.Adam(net.parameters(),lr=1e-2)
    for _ in range(a.steps):
        scale,adjusted=net(x);bx=adjusted.sign()*scale;y=bx@bw.T;loss=torch.nn.functional.mse_loss(y,ref);opt.zero_grad();loss.backward();opt.step()
    with torch.no_grad():
        scale,adjusted=net(x);loss=torch.nn.functional.mse_loss((adjusted.sign()*scale)@bw.T,ref)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} binary_weights_and_activations=1bit")
    print(f"absmean_scale_mse={torch.nn.functional.mse_loss(baseline,ref).item():.8g}")
    print(f"distribution_aware_mse={loss.item():.8g} descriptors=mean,absmean,std steps={a.steps}")
if __name__=="__main__":main()
