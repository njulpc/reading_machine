#!/usr/bin/env python3
"""SQNR + roofline layer-priority metric on Qwen3-0.6B."""
import argparse,glob,json,math,os
import torch

def model_dir(arg=None):
    if arg:return arg
    hits=glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits=[p for p in hits if os.path.exists(os.path.join(p,'config.json'))]
    if not hits:raise FileNotFoundError('Pass --model-dir')
    return hits[0]

def int4_row(weight):
    w=weight.detach().float();scale=w.abs().amax(1,keepdim=True).clamp_min(1e-12)/7
    return (w/scale).round().clamp(-7,7)*scale

def norm(values):
    lo,hi=min(values),max(values)
    return [0.5 for _ in values] if hi==lo else [(v-lo)/(hi-lo) for v in values]

def main():
    p=argparse.ArgumentParser();p.add_argument('--model-dir');p.add_argument('--quality-weight',type=float,default=.5);p.add_argument('--bandwidth-gbps',type=float,default=50);p.add_argument('--peak-gflops',type=float,default=100);args=p.parse_args()
    from transformers import AutoModelForCausalLM
    model=AutoModelForCausalLM.from_pretrained(model_dir(args.model_dir),local_files_only=True,dtype=torch.float32).eval()
    rows=[]
    for name,m in model.model.layers[0].named_modules():
        if not isinstance(m,torch.nn.Linear):continue
        w=m.weight.detach();q=int4_row(w);noise=(w.float()-q).pow(2).sum().clamp_min(1e-30);signal=w.float().pow(2).sum().clamp_min(1e-30)
        sqnr=10*torch.log10(signal/noise).item();elements=w.numel();out_dim,in_dim=w.shape
        fp16_bytes=elements*2;int4_bytes=math.ceil(elements/2)+out_dim*2
        flops=2*elements
        dense=max(fp16_bytes/(args.bandwidth_gbps*1e9),flops/(args.peak_gflops*1e9))
        quant=max(int4_bytes/(args.bandwidth_gbps*1e9),flops/(args.peak_gflops*1e9))
        rows.append({'module':name,'shape':[out_dim,in_dim],'sqnr_db':sqnr,'roofline_speedup':dense/quant,'fp16_bytes':fp16_bytes,'int4_payload_bytes':int4_bytes})
    qn=norm([r['sqnr_db'] for r in rows]);sn=norm([r['roofline_speedup'] for r in rows])
    for r,q,s in zip(rows,qn,sn):r['quality_score']=q;r['speed_score']=s;r['priority']=args.quality_weight*q+(1-args.quality_weight)*s
    rows.sort(key=lambda r:r['priority'],reverse=True)
    result={'model':'Qwen3-0.6B','scope':'transformer block 0','target':'row-wise symmetric INT4','quality_weight':args.quality_weight,'roofline':{'bandwidth_gbps':args.bandwidth_gbps,'peak_gflops':args.peak_gflops,'batch_tokens':1},'ranking':rows}
    print(json.dumps(result,indent=2))
    assert len(rows)==7 and all(torch.isfinite(torch.tensor(r['sqnr_db'])) for r in rows)

if __name__=='__main__':main()
