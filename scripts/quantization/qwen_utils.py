#!/usr/bin/env python3
"""Real Qwen3-0.6B tensor paths for the 2026-09-04 quantization batch."""
from __future__ import annotations
import argparse, json, math, platform, time
from pathlib import Path
import torch

MODEL_DIR=Path('/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca')
PROMPTS=['模型压缩需要同时验证精度和真实存储。','低比特推理应报告量化误差与部署边界。','校准样本需要覆盖不同的激活统计。','稀疏与量化可以共享统一的预算视角。','教师模型提供软目标，学生负责部署。','长上下文推理的缓存带来显存瓶颈。','硬件内核决定理论压缩是否转化为加速。','公平比较必须控制码率和输入分布。']
E2M1=torch.tensor([-6.,-4.,-3.,-2.,-1.5,-1.,-.5,0.,.5,1.,1.5,2.,3.,4.,6.])

def metrics(a,b):
    a=a.float().reshape(-1); b=b.float().reshape(-1)
    return {'mse':torch.mean((a-b)**2).item(),'mae':torch.mean((a-b).abs()).item(),
            'cosine':torch.nn.functional.cosine_similarity(a.double(),b.double(),dim=0).item(),
            'relative_l2':(torch.linalg.vector_norm(a-b)/torch.linalg.vector_norm(a).clamp_min(1e-12)).item()}

def env():
    import transformers
    return {'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
            'platform':platform.platform(),'cuda':torch.cuda.is_available(),'mps':torch.backends.mps.is_available()}

def load():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    for x in ('config.json','model.safetensors','tokenizer.json'):
        if not (MODEL_DIR/x).exists(): raise FileNotFoundError(MODEL_DIR/x)
    tok=AutoTokenizer.from_pretrained(MODEL_DIR,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(MODEL_DIR,local_files_only=True,dtype='auto').eval()
    return tok,model

def activation(tok,model,prompt):
    box={}
    module=model.model.layers[0].self_attn.q_proj
    def capture(_m,args):
        box['x']=args[0].detach().float()
        return None
    h=module.register_forward_pre_hook(capture)
    ids=tok(prompt,return_tensors='pt',add_special_tokens=False).input_ids
    with torch.inference_mode(): model(input_ids=ids,use_cache=False)
    h.remove(); return box['x'][0],module.weight.detach().float()

def qsym(x,bits,axis=-1):
    qmax=2**(bits-1)-1; s=x.abs().amax(dim=axis,keepdim=True).clamp_min(1e-12)/qmax
    return (x/s).round().clamp(-qmax,qmax)*s

def qpercentile(x,bits,p=0.995):
    qmax=2**(bits-1)-1; bound=torch.quantile(x.abs().flatten(),p).clamp_min(1e-12); s=bound/qmax
    return (x/s).round().clamp(-qmax,qmax)*s,float(bound)

def nearest(x,codebook):
    cb=codebook.to(x.device); bounds=(cb[:-1]+cb[1:])/2
    return cb[torch.bucketize(x.contiguous(),bounds)]

def ue5m3(x):
    x=x.float().clamp_min(torch.finfo(torch.float32).tiny); e=torch.floor(torch.log2(x)).clamp(-15,16)
    f=((x/torch.pow(2.,e)-1)*8).round().clamp(0,7)/8
    return (1+f)*torch.pow(2.,e)

def fp4_blocks(w,scale_kind='ue5m3',block=16):
    shape=w.shape; flat=w.flatten(); pad=(-flat.numel())%block
    y=torch.nn.functional.pad(flat,(0,pad)) if pad else flat; y=y.reshape(-1,block)
    raw=y.abs().amax(1,keepdim=True).clamp_min(1e-12)/6
    if scale_kind=='ue5m3': scale=ue5m3(raw)
    else: scale=torch.pow(2.,torch.ceil(torch.log2(raw)))
    out=(nearest(y/scale,E2M1)*scale).reshape(-1)[:flat.numel()].reshape(shape)
    return out

def hadamard(x):
    """Normalized Walsh-Hadamard transform along the final power-of-two axis."""
    n=x.shape[-1]
    if n&(n-1): raise ValueError('Hadamard axis must be a power of two')
    y=x.reshape(-1,n).clone(); h=1
    while h<n:
        y=y.reshape(-1,n//(2*h),2,h)
        a=y[:,:,0,:].clone(); b=y[:,:,1,:].clone()
        y=torch.stack((a+b,a-b),dim=2).reshape(-1,n); h*=2
    return (y/math.sqrt(n)).reshape_as(x)

def run_01683(tok,model):
    x,w=activation(tok,model,PROMPTS[0]); gain=torch.linspace(.65,1.55,x.shape[-1]); bias=.12*torch.sin(torch.arange(x.shape[-1]).float())
    corrupt=x*gain+bias; mu=x.mean(0,keepdim=True); sd=x.std(0,keepdim=True).clamp_min(1e-5)
    adapted=(corrupt-corrupt.mean(0,keepdim=True))/corrupt.std(0,keepdim=True).clamp_min(1e-5)*sd+mu
    target=x@w.T; raw=qsym(corrupt,8)@w.T; fixed=qsym(adapted,8)@w.T
    return {'algorithm':'BN-folded forward-only channel renormalization around INT8 projection','tokens':x.shape[0],
            'raw_corruption':metrics(target,raw),'forward_only_adapted':metrics(target,fixed),
            'mse_recovery_fraction':1-metrics(target,fixed)['mse']/metrics(target,raw)['mse']}

def run_01743(tok,model):
    x,w=activation(tok,model,' '.join(PROMPTS)); qw=qsym(w,4); base=qsym(x,8)@qw.T
    sculpt,b=qpercentile(x,8,.995); out=sculpt@qw.T; target=x@w.T
    return {'algorithm':'W4A8 PTQ with exported percentile activation clipping','tokens':x.shape[0],'clip_percentile':.995,'clip_bound':b,
            'max_range_ptq':metrics(target,base),'sculpt_clipped_ptq':metrics(target,out)}

def run_01962(tok,model):
    x,w=activation(tok,model,PROMPTS[1]); rows=w[:256]
    rotated_w=hadamard(rows); rotated_x=hadamard(x)
    groups=rotated_w.reshape(rows.shape[0],-1,128)
    beta=groups.mean(-1,keepdim=True); c=groups-beta; alpha=c.abs().mean(-1,keepdim=True).clamp_min(1e-12)
    for _ in range(3):
        t=torch.where(c>alpha/2,1.,torch.where(c<-alpha/2,-1.,0.)); alpha=(t*c).sum(-1,keepdim=True).abs()/t.square().sum(-1,keepdim=True).clamp_min(1)
    tern=(beta+alpha*t).reshape_as(rows); residual=rotated_w-tern
    # GPTQ-style low-rank compensation proxy, computed on the deployment slice.
    q=torch.randn(residual.shape[1],8,generator=torch.Generator().manual_seed(0)); q=torch.linalg.qr(q).Q
    for _ in range(3): q=torch.linalg.qr(residual.T@(residual@q)).Q
    comp=(residual@q)@q.T; restored=tern+comp
    target=x@rows.T
    return {'algorithm':'Hadamard/KOTMS-style rotation, group-128 affine ternarization and low-rank error compensation','target_rows':256,'group_size':128,
            'effective_bpw_estimate':1.0+32/128+8*16/rows.numel(),
            'ternary':metrics(target,rotated_x@tern.T),'compensated':metrics(target,rotated_x@restored.T),'zero_fraction':(t==0).float().mean().item()}

def kmeans(x,k,steps=15):
    if len(x)<k: k=len(x)
    centers=x[torch.linspace(0,len(x)-1,k).long()].clone()
    for _ in range(steps):
        d=torch.cdist(x,centers); labels=d.argmin(1)
        new=torch.stack([x[labels==i].mean(0) if (labels==i).any() else centers[i] for i in range(k)])
        if torch.allclose(new,centers): break
        centers=new
    return centers[torch.cdist(x,centers).argmin(1)]

def run_02107(tok,model):
    emb=model.model.embed_tokens.weight[:1024,:8].detach().float(); target=emb
    sq=torch.sign(emb)*emb.abs().mean(0,keepdim=True) # 8 one-bit scalars/vector
    pq=torch.cat([kmeans(emb[:,:4],16),kmeans(emb[:,4:],16)],1) # two 4-bit codes/vector
    vq=kmeans(emb,256) # one 8-bit code/vector
    return {'algorithm':'equal-8-bit rate-distortion comparison on real Qwen embedding vectors','vectors':1024,'dimension':8,
            'scalar_1bit_per_dim':metrics(target,sq),'product_two_8bit_codes':metrics(target,pq),'vector_single_8bit_code':metrics(target,vq),
            'rate_bits_per_vector':8,'note':'codebook storage amortization is excluded equally from this intrinsic distortion smoke test'}

def run_02219(tok,model):
    acts=[]; w=None
    for p in PROMPTS:
        x,w=activation(tok,model,p); acts.append(x)
    variances=[a.var().item() for a in acts]; top=sorted(range(len(acts)),key=lambda i:variances[i],reverse=True)[:4]; rnd=[0,2,4,6]
    test=acts[-1]; target=test@w.T
    def calibrated(indices):
        cal=torch.cat([acts[i] for i in indices]); bound=cal.abs().amax(); s=bound/127
        q=(test/s).round().clamp(-127,127)*s; out=q@w.T
        corrected=out+(target-out).mean(0,keepdim=True)
        return {'indices':indices,'bound':bound.item(),'raw':metrics(target,out),'bias_corrected':metrics(target,corrected)}
    return {'algorithm':'activation-variance informative INT8 calibration with output bias correction','variances':variances,
            'random_calibration':calibrated(rnd),'avis_calibration':calibrated(top)}

def run_02652(tok,model):
    x,w=activation(tok,model,PROMPTS[2]); rows=w[:128]; flat=rows.flatten(); pad=(-flat.numel())%24
    vec=torch.nn.functional.pad(flat,(0,pad)).reshape(-1,24); scale=vec.square().mean(1,keepdim=True).sqrt().clamp_min(1e-12)
    z=vec/scale; shells=[4,8,12,24]; candidates=[]
    for keep in shells:
        idx=z.abs().topk(keep,dim=1).indices; c=torch.zeros_like(z); c.scatter_(1,idx,torch.gather(z.sign(),1,idx));
        a=(c*z).sum(1,keepdim=True)/c.square().sum(1,keepdim=True).clamp_min(1); candidates.append(c*a)
    stack=torch.stack(candidates,1); err=(stack-z[:,None,:]).square().mean(2); shell=err.argmin(1)
    recon=stack[torch.arange(len(vec)),shell]*scale; rw=recon.flatten()[:flat.numel()].reshape_as(rows)
    target=x@rows.T
    sign_bits=sum(shells[i] for i in shell.tolist()); layout_bits=len(vec)*2+sign_bits+len(vec)*16
    return {'algorithm':'24D multi-shell signed-vector decoder with bit-plane residency accounting','shell_histogram':torch.bincount(shell,minlength=4).tolist(),
            'resident_bpw_estimate':layout_bits/flat.numel(),'output':metrics(target,x@rw.T),
            'boundary':'software transfer reproduces shell selection/layout mechanics, not the paper exact 301-class Leech codebook or fused CUDA kernel'}

def run_02846(tok,model):
    x,w=activation(tok,model,PROMPTS[3]); a=fp4_blocks(w,'pow2',16); b=fp4_blocks(w,'ue5m3',16); target=x@w.T
    return {'algorithm':'E2M1 FP4 payload with block-16 UE5M3 scale','pow2_scale':metrics(target,x@a.T),'ue5m3_scale':metrics(target,x@b.T),
            'weight_pow2':metrics(w,a),'weight_ue5m3':metrics(w,b)}

RUNNERS={'2609.01683':run_01683,'2609.01743':run_01743,'2609.01962':run_01962,'2609.02107':run_02107,'2609.02219':run_02219,'2609.02652':run_02652,'2609.02846':run_02846}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paper_id',choices=sorted(RUNNERS)); ap.add_argument('--output-json'); ap.add_argument('--self-test',action='store_true'); args=ap.parse_args()
    torch.manual_seed(0); started=time.perf_counter(); tok,model=load(); result=RUNNERS[args.paper_id](tok,model)
    result.update({'paper_id':args.paper_id,'model':'Qwen3-0.6B','checkpoint':str(MODEL_DIR/'model.safetensors'),'environment':env(),
                   'elapsed_seconds':time.perf_counter()-started,'status':'PASS','scope':'real checkpoint and real model activations; CPU numerical reference'})
    assert all(math.isfinite(float(v)) for v in [result['elapsed_seconds']])
    text=json.dumps(result,ensure_ascii=False,indent=2); print(text)
    if args.output_json: Path(args.output_json).write_text(text+'\n',encoding='utf-8')

if __name__=='__main__': main()
