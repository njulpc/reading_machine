#!/usr/bin/env python3
"""Global-weighted pruning of binarized Qwen3-0.6B projection weights."""
import argparse,glob,json,os
import torch

def model_dir(arg=None):
    if arg:return arg
    hits=glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits=[p for p in hits if os.path.exists(os.path.join(p,'config.json'))]
    if not hits:raise FileNotFoundError('Pass --model-dir')
    return hits[0]

def main():
    p=argparse.ArgumentParser();p.add_argument('--model-dir');p.add_argument('--pruning-ratio',type=float,default=.70);args=p.parse_args()
    if not 0<args.pruning_ratio<1:p.error('ratio must be in (0,1)')
    from transformers import AutoModelForCausalLM
    model=AutoModelForCausalLM.from_pretrained(model_dir(args.model_dir),local_files_only=True,dtype=torch.float32).eval()
    layer=model.model.layers[0]
    modules=[(n,m) for n,m in layer.named_modules() if isinstance(m,torch.nn.Linear)]
    weighted=[]
    for name,m in modules:
        w=m.weight.detach().float()
        # Paper's global weighting: per-output-channel L-infinity normalization,
        # then one threshold over the concatenated transformed tensors.
        norm=w.abs().amax(dim=1,keepdim=True).clamp_min(1e-12)
        weighted.append((name,m,w,(w/norm).abs()))
    scores=torch.cat([x[3].flatten() for x in weighted])
    threshold=torch.quantile(scores,args.pruning_ratio)
    kept=total=0;errors=[]
    with torch.no_grad():
        for name,m,w,score in weighted:
            mask=score>threshold
            scale=w.abs().mean(dim=1,keepdim=True).clamp_min(1e-12)
            binary=torch.where(w>=0,scale,-scale)*mask
            errors.append(((w-binary).pow(2).mean()/w.pow(2).mean()).item())
            kept+=mask.sum().item();total+=mask.numel()
    result={'model':'Qwen3-0.6B','block':0,'linear_modules':len(modules),'weights':total,'target_pruning_ratio':args.pruning_ratio,'actual_pruning_ratio':1-kept/total,'global_threshold':threshold.item(),'mean_normalized_mse':sum(errors)/len(errors),'global_weighting':'per-output-channel L_inf then one concatenated threshold','binarization':'per-output-channel mean-abs scale times sign'}
    print(json.dumps(result,indent=2))
    assert len(modules)==7 and abs(result['actual_pruning_ratio']-args.pruning_ratio)<1e-4

if __name__=='__main__':main()
