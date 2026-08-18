#!/usr/bin/env python3
"""SpecVLA-style 0/4/8-bit block quantization of temporal feature residuals."""
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

def quantize_residual(delta,block,zero_fraction,high_fraction):
    flat=delta.flatten(); chunks=list(flat.split(block)); scores=torch.tensor([v.abs().sum() for v in chunks])
    tz=torch.quantile(scores,zero_fraction); th=torch.quantile(scores,1-high_fraction)
    out=[]; counts=[0,0,0]
    for values,score in zip(chunks,scores):
        if score<tz: out.append(torch.zeros_like(values)); counts[0]+=1
        elif score>th: out.append(qsym(values,8)); counts[2]+=1
        else: out.append(qsym(values,4)); counts[1]+=1
    return torch.cat(out).reshape_as(delta),counts,tz.item(),th.item()

def main():
    p=argparse.ArgumentParser();p.add_argument("--model-dir",type=Path,required=True);p.add_argument("--block",type=int,default=64);p.add_argument("--zero-fraction",type=float,default=.358);p.add_argument("--high-fraction",type=float,default=.049);p.add_argument("--seed",type=int,default=13)
    a=p.parse_args();torch.manual_seed(a.seed);w=load_weight(a.model_dir);x_prev=torch.randn(32,w.shape[1]);x_cur=x_prev+.1*torch.randn_like(x_prev)
    delta=x_cur-x_prev;qdelta,counts,tz,th=quantize_residual(delta,a.block,a.zero_fraction,a.high_fraction)
    ref=x_cur@w.T;approx=x_prev@w.T+qdelta@w.T; total=sum(counts)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)} residual_block={a.block}")
    print(f"threshold_zero={tz:.8g} threshold_high={th:.8g}")
    print(f"block_fraction_0bit={counts[0]/total:.6f} block_fraction_4bit={counts[1]/total:.6f} block_fraction_8bit={counts[2]/total:.6f}")
    print(f"differential_accumulation_output_mse={torch.nn.functional.mse_loss(approx,ref).item():.8g}")
if __name__=="__main__":main()
