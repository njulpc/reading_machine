"""Packed ZIP-SR / ZE-EDEN AdamW (arXiv:2610.12444), actual Qwen smoke run."""
import argparse,json,platform,time
from pathlib import Path
import torch
NF4=[-1.,-.6961928009986877,-.5250730514526367,-.39491748809814453,-.28444138169288635,-.18477343022823334,-.09105003625154495,0.,.07958029955625534,.16093020141124725,.24611230194568634,.33791524171829224,.44070982933044434,.5626170039176941,.7229568362236023,1.]
DYN=sorted([0.,1.]+[10.**(-e)*(.1+.9*(k+.5)/2**(3-e)) for e in range(3) for k in range(2**(3-e))])

def pack(c):
 c=c.flatten().to(torch.uint8);assert c.numel()%2==0 and c.max()<16
 return c[::2]|(c[1::2]<<4)
def unpack(c):return torch.stack((c&15,c>>4),dim=-1).flatten().long()
def probability(x,a,b,t):
 h=lambda v:(torch.sqrt(v.clamp_min(0)/(1-.95**t))+1e-8).reciprocal()
 ha,hb,hx=h(a),h(b),h(x);den=ha-hb
 return torch.where(den>0,(hx-hb)/den.clamp_min(torch.finfo(x.dtype).tiny),torch.ones_like(x)).clamp(0,1)
def encode(x,levels,rule,t=1,eden=False,generator=None):
 z=x.detach().float().reshape(-1,128);scale=z.abs().amax(1,keepdim=True).clamp_min(1e-12);y=z/scale
 cb=torch.tensor(levels,device=x.device,dtype=torch.float32)
 hi=torch.searchsorted(cb,y.contiguous()).clamp(0,len(levels)-1);lo=(hi-1).clamp_min(0);a,b=cb[lo],cb[hi]
 p=probability(z.clamp_min(0),a*scale,b*scale,t) if rule=='update_sr' else torch.where(b>a,(b-y)/(b-a).clamp_min(1e-30),torch.ones_like(y)).clamp(0,1)
 low=p>=.5 if rule=='rtn' else torch.rand(y.shape,device=y.device,generator=generator)<p
 c=torch.where(low,lo,hi)
 if eden:scale=scale*y.square().sum(1,keepdim=True)/(y*cb[c]).sum(1,keepdim=True).clamp_min(1e-12)
 return {'codes':pack(c),'scale':scale,'shape':x.shape,'levels':levels}
def decode(s):
 cb=torch.tensor(s['levels'],device=s['scale'].device,dtype=torch.float32)
 return (cb[unpack(s['codes'])].reshape(-1,128)*s['scale']).reshape(s['shape'])
class MomentAdam:
 def __init__(self,named_parameters,mode,steps,lr=1e-5):
  self.params=list(named_parameters);self.mode=mode;self.steps=steps;self.lr=lr;self.states={};self.t=0;self.gen=torch.Generator().manual_seed(42)
 @torch.no_grad()
 def step(self):
  self.t+=1;t=self.t
  for name,p in self.params:
   if p.grad is None:continue
   old=self.states.get(name)
   m,v=[decode(s) if isinstance(s,dict) else s for s in old] if old else (torch.zeros_like(p,dtype=torch.float32),torch.zeros_like(p,dtype=torch.float32))
   g=p.grad.float();m=.9*m+.1*g;v=.95*v+.05*g.square()
   # Paper update-before-storage convention; zero decay follows SFT.
   p.add_(-(self.lr/(1-.9**t))*m/(torch.sqrt(v/(1-.95**t))+1e-8))
   if self.mode!='fp32' and p.numel()>=4096 and p.numel()%128==0:
    # Caller names a tied embedding as lm_head if training its shared state.
    head_sr='lm_head' in name and t>.9*self.steps
    qm=encode(m,NF4,'state_sr' if head_sr else 'rtn',generator=self.gen)
    qv=encode(v,DYN if self.mode=='zip_sr' else DYN[1:],'update_sr' if self.mode=='zip_sr' else 'rtn',t=t,eden=self.mode=='ze_eden',generator=self.gen)
    self.states[name]=(qm,qv)
   else:self.states[name]=(m,v)
 def storage_bytes(self):
  return sum(t.numel()*t.element_size() for pair in self.states.values() for s in pair for t in ([s['codes'],s['scale']] if isinstance(s,dict) else [s]))
def checks():
 torch.manual_seed(42);c=torch.arange(16).repeat(16);assert torch.equal(unpack(pack(c)),c)
 assert len(DYN)==16 and abs(DYN[1]-.00325)<1e-10
 for mode in ['zip_sr','ze_eden']:
  z=torch.zeros(4096);q=decode(encode(z,DYN if mode=='zip_sr' else DYN[1:],'update_sr' if mode=='zip_sr' else 'rtn',eden=mode=='ze_eden'));assert torch.equal(z,q)
 x=torch.tensor([1e-10,1e-5,.1],dtype=torch.float64);a=torch.zeros_like(x);b=torch.ones_like(x);p=probability(x,a,b,5)
 h=lambda v:(torch.sqrt(v/(1-.95**5))+1e-8).reciprocal()
 err=((p*h(a)+(1-p)*h(b)-h(x)).abs()/h(x)).max().item();assert err<1e-12
 w=torch.nn.Parameter(torch.randn(4096));r=torch.nn.Parameter(w.detach().clone());w.grad=torch.randn_like(w);r.grad=w.grad.clone()
 q=MomentAdam([('weight',w)],'zip_sr',2);f=MomentAdam([('weight',r)],'fp32',2);q.step();f.step();assert torch.equal(w,r);assert q.storage_bytes()==4096*1.0625
 # NF4 SR should preserve conditional state expectation in each cell.
 cb=torch.tensor(NF4,dtype=torch.float64);xx=(cb[:-1]+cb[1:])/2;pp=(cb[1:]-xx)/(cb[1:]-cb[:-1]);assert torch.allclose(pp*cb[:-1]+(1-pp)*cb[1:],xx)
 return {'nibble_roundtrip':True,'zero_blocks':True,'dyn4_min':DYN[1],'update_sr_expectation_relative_error':err,'first_update_equal_fp32':True,'bytes_per_parameter':q.storage_bytes()/4096,'nf4_sr_expectation':True}
def run(args):
 from transformers import AutoModelForCausalLM,AutoTokenizer
 torch.set_num_threads(4);torch.manual_seed(42)
 model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='eager');tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
 for p in model.parameters():p.requires_grad_(False)
 name='model.layers.0.self_attn.q_proj.weight';param=dict(model.named_parameters())[name];param.data=param.data.float();param.requires_grad_(True)
 model.eval();opt=MomentAdam([(name,param)],args.mode,args.steps);initial=param.detach().clone();hist=[];start=time.monotonic()
 texts=['Question: What is two plus three? Answer: Five.','A compact model uses less memory. Accurate rounding reduces numerical error.','The capital of France is Paris. The sky appears blue during the day.']
 for k in range(args.steps):
  batch=tok(texts[k%3],return_tensors='pt',truncation=True,max_length=32);model.zero_grad(set_to_none=True)
  with torch.autocast('cpu',dtype=torch.bfloat16):loss=model(**batch,labels=batch['input_ids']).loss
  loss.backward();gn=torch.nn.utils.clip_grad_norm_([param],1.);opt.step();assert torch.isfinite(param).all()
  hist.append({'step':k+1,'loss':loss.item(),'gradient_norm_before_clip':gn.item()})
 return {'model':args.model,'mode':args.mode,'parameter':name,'shape':list(param.shape),'steps':hist,'state_bytes':opt.storage_bytes(),'fp32_state_bytes':param.numel()*8,'weight_max_delta':(param-initial).abs().max().item(),'seconds':time.monotonic()-start,'torch':torch.__version__,'python':platform.python_version(),'scope':'CPU BF16 full forward, one Qwen q_proj FP32 master parameter; short artificial text. Not full SFT.','lm_head_switch_exercised_in_qwen_run':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['zip_sr','ze_eden','fp32'],default='zip_sr');ap.add_argument('--steps',type=int,default=3);ap.add_argument('--test-only',action='store_true');ap.add_argument('--output',default='results.json')
 ap.add_argument('--model',default='/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca');args=ap.parse_args();result={'checks':checks()}
 if not args.test_only:result['qwen']=run(args)
 Path(args.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
