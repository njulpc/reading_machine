#!/usr/bin/env python3
"""Residual Fallback Quantization on real Qwen3-0.6B activations."""
import argparse,glob,json,os
import torch

GRID=torch.tensor([0.,0.5,1.,1.5,2.,3.,4.,6.])

def model_dir(arg=None):
    if arg:return arg
    hits=glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits=[p for p in hits if os.path.exists(os.path.join(p,'tokenizer.json'))]
    if not hits:raise FileNotFoundError('Pass --model-dir')
    return hits[0]

def mxfp4(x,block=32):
    shape=x.shape;flat=x.float().flatten();pad=(-flat.numel())%block
    padded=torch.nn.functional.pad(flat,(0,pad)) if pad else flat
    b=padded.view(-1,block);mx=b.abs().amax(1,keepdim=True).clamp_min(1e-12)
    scale=torch.pow(2,torch.ceil(torch.log2(mx/6)))
    n=b.abs()/scale;grid=GRID.to(n.device)
    idx=(n[...,None]-grid).abs().argmin(-1);q=grid[idx]*b.sign()*scale
    return q.flatten()[:flat.numel()].view(shape),q,pad

def main():
    p=argparse.ArgumentParser();p.add_argument('--model-dir');p.add_argument('--fallback-fraction',type=float,default=.10);p.add_argument('--prompt',default='极低比特激活量化需要处理异常值。');args=p.parse_args()
    from transformers import AutoModelForCausalLM,AutoTokenizer
    directory=model_dir(args.model_dir);tok=AutoTokenizer.from_pretrained(directory,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(directory,local_files_only=True,dtype=torch.float32).eval()
    captured={}
    def capture(_module,inputs):
        captured['x']=inputs[0].detach().cpu()
    handle=model.model.layers[0].mlp.gate_proj.register_forward_pre_hook(capture)
    with torch.inference_mode():model(**tok(args.prompt,return_tensors='pt'))
    handle.remove();x=captured['x'].float();base,base_blocks,pad=mxfp4(x)
    residual=x-base;_,res_blocks,_=mxfp4(residual)
    base_err=(x-base).flatten();padded=torch.nn.functional.pad(base_err,(0,pad)) if pad else base_err
    block_mse=padded.view(-1,32).pow(2).mean(1)
    k=max(1,round(block_mse.numel()*args.fallback_fraction));chosen=torch.topk(block_mse,k).indices
    mask=torch.zeros_like(block_mse,dtype=torch.bool);mask[chosen]=True
    corr=torch.zeros_like(base_blocks);corr[mask]=res_blocks[mask]
    rfq=(base_blocks+corr).flatten()[:x.numel()].view_as(x)
    mse0=(x-base).pow(2).mean().item();mse1=(x-rfq).pow(2).mean().item()
    result={'model':'Qwen3-0.6B','activation':'layer0.mlp.gate_proj input','shape':list(x.shape),'format':'MXFP4 E2M1 block32 power-of-two scale software reference','fallback_fraction':mask.float().mean().item(),'base_mse':mse0,'rfq_mse':mse1,'mse_reduction_fraction':1-mse1/mse0,'base_cosine':torch.nn.functional.cosine_similarity(x.flatten(),base.flatten(),dim=0).item(),'rfq_cosine':torch.nn.functional.cosine_similarity(x.flatten(),rfq.flatten(),dim=0).item()}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    assert mse1<mse0 and result['rfq_cosine']>=result['base_cosine']

if __name__=='__main__':main()
