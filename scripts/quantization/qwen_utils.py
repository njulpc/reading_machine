#!/usr/bin/env python3
"""Small real-weight Qwen3-0.6B validations for the 2026-09-03 batch."""
from __future__ import annotations
import argparse, json, math, platform, time
from pathlib import Path
import torch
from safetensors import safe_open

CHECKPOINT=Path('/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors')
NF4=torch.tensor([-1.0,-.6961928,-.52507305,-.3949175,-.28444138,-.18477343,-.09105004,0.,.0795803,.1609302,.2461123,.33791524,.44070983,.562617,.72295684,1.])

def tensor(key):
    if not CHECKPOINT.exists(): raise FileNotFoundError(CHECKPOINT)
    with safe_open(str(CHECKPOINT),framework='pt',device='cpu') as f: return f.get_tensor(key).float()

def metrics(a,b):
    a,b=a.float().flatten(),b.float().flatten()
    cosine=torch.nn.functional.cosine_similarity(a.double(),b.double(),dim=0).clamp(-1,1).item()
    return {'mse':torch.mean((a-b)**2).item(),'cosine':cosine,'relative_l2':(torch.linalg.vector_norm(a-b)/torch.linalg.vector_norm(a).clamp_min(1e-12)).item()}

def qgroup(x,bits,group=128):
    shape=x.shape; y=x.reshape(-1,shape[-1]); pad=(-y.shape[-1])%group
    z=torch.nn.functional.pad(y,(0,pad)) if pad else y
    z=z.reshape(y.shape[0],-1,group); lo=z.amin(-1,keepdim=True); hi=z.amax(-1,keepdim=True)
    scale=((hi-lo)/(2**bits-1)).clamp_min(1e-12); zero=(-lo/scale).round().clamp(0,2**bits-1)
    code=(z/scale+zero).round().clamp(0,2**bits-1)
    out=((code-zero)*scale).reshape(y.shape[0],-1)[:,:y.shape[-1]].reshape(shape)
    estimated_bits=x.numel()*bits+scale.numel()*32+zero.numel()*8
    return out,estimated_bits

def qnf4(x,block=64):
    flat=x.flatten(); pad=(-flat.numel())%block; z=torch.nn.functional.pad(flat,(0,pad)) if pad else flat
    z=z.reshape(-1,block); scale=z.abs().amax(-1,keepdim=True).clamp_min(1e-12)
    n=z/scale; bounds=(NF4[:-1]+NF4[1:])/2; code=torch.bucketize(n.contiguous(),bounds)
    out=(NF4[code]*scale).flatten()[:flat.numel()].reshape_as(x)
    return out,x.numel()*4+scale.numel()*32

def base(aid,algorithm,started):
    return {'paper_id':aid,'model':'Qwen3-0.6B','checkpoint':str(CHECKPOINT),'algorithm':algorithm,'environment':{'python':platform.python_version(),'torch':torch.__version__,'hardware':platform.platform(),'cuda':torch.cuda.is_available()},'elapsed_seconds':time.perf_counter()-started}

def run_00665():
    t=time.perf_counter(); w=tensor('model.layers.0.self_attn.q_proj.weight')
    w8,b8=qgroup(w,8,128); w4,b4=qgroup(w,4,128); nf,bn=qnf4(w)
    r=base('2609.00665','measured BF16/INT8/NF4/group-W4 sustainability proxy on a real Qwen projection',t)
    r.update({'tensor_shape':list(w.shape),'bf16_bits':w.numel()*16,'variants':{'int8':{'estimated_bits':b8,'compression_vs_bf16':w.numel()*16/b8,**metrics(w,w8)},'nf4':{'estimated_bits':bn,'compression_vs_bf16':w.numel()*16/bn,**metrics(w,nf)},'group_w4':{'estimated_bits':b4,'compression_vs_bf16':w.numel()*16/b4,**metrics(w,w4)}}}); return r

def run_00718():
    t=time.perf_counter(); torch.manual_seed(718); w=tensor('model.layers.0.self_attn.q_proj.weight')[:512]; x=torch.randn(32,w.shape[1]); y=x@w.T
    keep=w.norm(dim=1)>=torch.quantile(w.norm(dim=1),.25); wp=w*keep[:,None]; yp=x@wp.T
    dropped=w-wp; rank=16; u,s,v=torch.pca_lowrank(dropped,q=rank,center=False); adapter=(u*s)@v.T; wd=wp+adapter; yd=x@wd.T
    wq,_=qgroup(wd,8,128); yq=x@wq.T
    r=base('2609.00718','structured row pruning + rank-16 teacher residual recovery + INT8 transfer proxy',t)
    r.update({'pruned_row_fraction':(~keep).float().mean().item(),'distillation_rank':rank,'stages':{'pruned':metrics(y,yp),'distilled':metrics(y,yd),'integer_quantized':metrics(y,yq)}}); return r

def run_01084():
    t=time.perf_counter(); torch.manual_seed(1084); w=tensor('model.layers.0.self_attn.k_proj.weight'); h=torch.randn(48,w.shape[1]); kv=h@w.T
    u,s,vh=torch.linalg.svd(kv,full_matrices=False); rank=8; low=(u[:,:rank]*s[:rank])@vh[:rank]; residual=kv-low; rq,bits=qgroup(residual,8,128); restored=low+rq
    fw=tensor('model.layers.0.self_attn.q_proj.weight')[:256]; center=fw.mean(1,keepdim=True); delta=fw-center; dq,dbits=qgroup(delta,4,128); frestored=center+dq
    r=base('2609.01084','BRQ-KV rank-8 + INT8 residual and DAT-style centered INT4 delta proxy',t)
    r.update({'kv_shape':list(kv.shape),'kv_rank':rank,'kv_compression_vs_fp16':kv.numel()*16/(rank*(kv.shape[0]+kv.shape[1])*16+bits),'kv_metrics':metrics(kv,restored),'ffn_proxy_shape':list(fw.shape),'ffn_delta_metrics':metrics(fw,frestored),'ffn_compression_vs_fp16':fw.numel()*16/(dbits+center.numel()*16)}); return r

def run_01200():
    t=time.perf_counter(); e=tensor('model.embed_tokens.weight')[1000:1256]; mean=e.mean(0,keepdim=True); z=e-mean
    u,s,vh=torch.linalg.svd(z,full_matrices=False); rank=64; coeff=u[:,:rank]*s[:rank]; basis=vh[:rank]; cq,cb=qgroup(coeff,8,64); bq,bb=qgroup(basis,8,128); restored=cq@bq+mean
    total=cb+bb+mean.numel()*16
    r=base('2609.01200','training-free rank-64 transform plus INT8 entropy-coding proxy for real Qwen token representations',t)
    r.update({'representation_shape':list(e.shape),'rank':rank,'estimated_compression_vs_fp16':e.numel()*16/total,'metrics':metrics(e,restored)}); return r

def run_01587():
    t=time.perf_counter(); ws=[tensor(f'model.layers.{i}.self_attn.q_proj.weight')[:256] for i in range(8)]
    q128=[qgroup(w,4,128)[0] for w in ws]; damage=[metrics(w,q)['mse'] for w,q in zip(ws,q128)]; worst=max(range(8),key=damage.__getitem__)
    local=[]; local_bits=0
    for i,w in enumerate(ws): q,b=qgroup(w,8 if i==worst else 4,128); local.append(q); local_bits+=b
    globalq=[]; global_bits=0
    for w in ws: q,b=qgroup(w,4,32); globalq.append(q); global_bits+=b
    mse_local=sum(metrics(w,q)['mse'] for w,q in zip(ws,local)); mse_global=sum(metrics(w,q)['mse'] for w,q in zip(ws,globalq))
    r=base('2609.01587','matched-near-budget causal local W8 repair versus globally finer group-W4 allocation',t)
    r.update({'layers':8,'worst_layer':worst,'local_estimated_bits':local_bits,'global_estimated_bits':global_bits,'global_to_local_budget_ratio':global_bits/local_bits,'summed_mse':{'local_repair':mse_local,'global_granularity':mse_global},'global_better':mse_global<mse_local}); return r

def run_00224():
    t=time.perf_counter(); w=tensor('model.layers.0.self_attn.q_proj.weight')[:512]
    alpha=w.abs().mean(0,keepdim=True).clamp_min(1e-12); ternary=torch.where(w>0.7*alpha,alpha,torch.where(w<-0.7*alpha,-alpha,torch.zeros_like(w)))
    error=w-ternary; col_score=error.square().mean(0); salient=col_score>=torch.quantile(col_score,.75)
    residual=torch.zeros_like(error); selected=error[:,salient]; groups=selected.reshape(selected.shape[0],-1,4); idx=groups.abs().argmax(-1,keepdim=True); kept=torch.zeros_like(groups).scatter(-1,idx,groups.gather(-1,idx)); residual[:,salient]=kept.reshape_as(selected)
    restored=ternary+residual; density=(residual!=0).float().mean().item(); effective_bits=2+density*(16+2)
    r=base('2609.00224','QTEA-style by-column ternary weights plus salient-column 1:4 residual compensation',t)
    r.update({'tensor_shape':list(w.shape),'salient_column_fraction':salient.float().mean().item(),'residual_density':density,'estimated_effective_bits_per_weight':effective_bits,'ternary_metrics':metrics(w,ternary),'compensated_metrics':metrics(w,restored)}); return r

def run_00450():
    t=time.perf_counter(); w=tensor('model.layers.0.self_attn.q_proj.weight')[:512]; flat=w.reshape(-1,256); peak=flat.abs().amax(-1,keepdim=True).clamp_min(1e-12); raw=peak/7
    pot=2.0**torch.round(torch.log2(raw)); qpot=(flat/pot).round().clamp(-7,7)*pot
    exponent=torch.floor(torch.log2(raw)); mantissa=(raw/(2.0**exponent)-1.0); mq=(mantissa*15).round().clamp(0,15)/15; sig=(1+mq)*(2.0**exponent); qsig=(flat/sig).round().clamp(-7,7)*sig
    r=base('2609.00450','HBQ-style large-block W4 with power-of-two exponent plus 4-bit significand scale',t)
    r.update({'tensor_shape':list(w.shape),'block_size':256,'weight_bits':4,'significand_bits':4,'pot_scale_metrics':metrics(w,qpot.reshape_as(w)),'hierarchical_sig_metrics':metrics(w,qsig.reshape_as(w)),'sig_improves_mse':metrics(w,qsig.reshape_as(w))['mse']<metrics(w,qpot.reshape_as(w))['mse']}); return r

RUN={'2609.00665':run_00665,'2609.00718':run_00718,'2609.01084':run_01084,'2609.01200':run_01200,'2609.01587':run_01587,'2609.00224':run_00224,'2609.00450':run_00450}
def main():
    p=argparse.ArgumentParser(); p.add_argument('paper_id',choices=RUN); p.add_argument('--output-json'); a=p.parse_args(); out=RUN[a.paper_id](); text=json.dumps(out,ensure_ascii=False,indent=2); print(text)
    if a.output_json: Path(a.output_json).write_text(text+'\n')
if __name__=='__main__': main()
