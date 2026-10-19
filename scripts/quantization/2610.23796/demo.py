"""FuTransformer numerical reference on Qwen3-0.6B (CPU; no Hopper kernels).
Official equations and settings: https://arxiv.org/html/2610.23796v1 §3, §4.8.
Only first-layer q_proj is weight-quantized; first-layer KV uses a packed mirror.
"""
import argparse, json, math, platform, time
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F

REVISION = 'c1899de289a04d12100db370d81485cdf75e47ca'
DEFAULT_MODEL = str(Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots'/REVISION)
CALIBRATION = [
 'A scientific experiment compares a hypothesis against observations and reports uncertainty.',
 'Computer systems move weights and activations between memory and processors during inference.',
 'An ecosystem contains interacting organisms with different needs for energy and water.',
 'A mathematical proof explains each logical step from assumptions to a stated conclusion.']
EVALUATION = [
 'A traveler walks through a quiet village and asks the local baker for directions to the river.',
 'The software engineer measures the error and memory requirements before deploying a new model.']

def hadamard(x):
 n=x.shape[-1]
 assert n and n&(n-1)==0
 y=x.float().clone(); h=1
 while h<n:
  z=y.reshape(*y.shape[:-1],-1,2,h)
  a,b=z[...,0,:].clone(),z[...,1,:].clone()
  y=torch.stack((a+b,a-b),-2).reshape_as(y); h*=2
 return y/math.sqrt(n)

def scales(w,group=128):
 assert w.shape[-1]%group==0
 s=w.reshape(w.shape[0],-1,group).abs().amax(-1)/7
 return torch.where(s>0,s,torch.ones_like(s))

def pack(q):
 assert q.shape[-1]%2==0 and q.min()>=-8 and q.max()<=7
 u=(q.to(torch.int16)+8).to(torch.uint8)
 return u[...,0::2] | (u[...,1::2]<<4)

def unpack(p):
 return (torch.stack((p&15,p>>4),-1).flatten(-2).to(torch.int16)-8).to(torch.int8)

def rtn(w,group=128):
 s=scales(w,group)
 q=(w.reshape(w.shape[0],-1,group)/s[...,None]).round().clamp(-8,7).to(torch.int8)
 return pack(q.reshape_as(w)),s.float()

def dequant(p,s,group=128):
 q=unpack(p).float()
 return (q.reshape(q.shape[0],-1,group)*s[...,None]).reshape_as(q)

def gptq(w,x,group=128,damping=.05):
 # Static groups, no act order, FP64 Hessian/error feedback (§4.8).
 # Calibration is intentionally small: 4x128 artificial tokens, not WikiText-2.
 w=w.double().clone(); x=x.double(); h=2*x.T@x/x.shape[0]
 dead=h.diag()==0
 h[dead,dead]=1; w[:,dead]=0
 h.diagonal().add_(damping*h.diag().mean())
 inv=torch.cholesky_inverse(torch.linalg.cholesky(h))
 u=torch.linalg.cholesky(inv,upper=True)
 s=scales(w,group); q=torch.empty_like(w,dtype=torch.int8)
 for j in range(w.shape[1]):
  step=s[:,j//group]
  qi=(w[:,j]/step).round().clamp(-8,7)
  q[:,j]=qi.to(torch.int8)
  e=(w[:,j]-qi*step)/u[j,j]
  w[:,j:]-=e[:,None]*u[j,j:][None,:]
 return pack(q),s.float()

class PackedProjection(nn.Module):
 def __init__(self,p,s,gain):
  super().__init__(); self.register_buffer('packed',p); self.register_buffer('scale',s)
  self.register_buffer('gain',gain.float())
 def forward(self,x):
  # Input is RMSNorm(x)*gain. Undo gain because it was folded into W offline.
  return F.linear(x.float()/self.gain,dequant(self.packed,self.scale)).to(x.dtype)

class DelayedFP8:
 def __init__(self,initial_amax):
  assert initial_amax>=0
  self.previous=float(initial_amax)
 def __call__(self,x):
  s=max(self.previous/448,1e-12)
  saturation=int((x.abs()>448*s).sum())
  q=(x.float()/s).clamp(-448,448).to(torch.float8_e4m3fn)
  self.previous=float(x.abs().max())
  return q,s,saturation

def cache_pack(x):
 s=x.float().abs().amax(-1,keepdim=True)/7
 s=torch.where(s>0,s,torch.ones_like(s))
 q=(x.float()/s).round().clamp(-8,7).to(torch.int8)
 p=pack(q)
 return p,s

def cache_dequant(p,s):return unpack(p).float()*s

def tests():
 torch.manual_seed(9); results={}
 q=torch.arange(-8,8,dtype=torch.int8).reshape(2,8)
 assert torch.equal(unpack(pack(q)),q); results['all_nibble_values_roundtrip']=True
 x=torch.randn(3,128)
 assert torch.allclose(hadamard(hadamard(x)),x,atol=1e-6);results['hadamard_inverse']=True
 y=torch.randn_like(x)
 assert torch.allclose((x*y).sum(-1),(hadamard(x)*hadamard(y)).sum(-1),atol=1e-5);results['qk_dot_preserved']=True
 p,s=cache_pack(torch.zeros(2,4,128));assert torch.isfinite(cache_dequant(p,s)).all();results['zero_cache_finite']=True
 w=torch.randn(8,128);cal=torch.randn(512,128);p,s=gptq(w,cal);assert p.numel()==w.numel()//2
 assert torch.isfinite(dequant(p,s)).all();results['gptq_static_group_packing']=True
 gain=torch.rand(128)+.1
 assert torch.allclose(F.linear(x*gain,w),F.linear(x,w*gain),atol=1e-5);results['rms_gain_fold']=True
 d=DelayedFP8(0);a,b,c=d(torch.zeros(4)); assert torch.isfinite(a.float()).all()
 d=DelayedFP8(1);a,b,c=d(torch.tensor([2.]));assert c==1 and d.previous==2;results['delayed_fp8_saturation_and_zero']=True
 # Identity Hessian makes GPTQ exactly RTN because error updates are diagonal.
 pg,sg=gptq(w,torch.eye(128));pr,sr=rtn(w)
 assert torch.equal(pg,pr) and torch.equal(sg,sr);results['gptq_identity_hessian_equals_rtn']=True
 return results

@torch.inference_mode()
def run(model_path):
 import transformers
 from transformers import AutoModelForCausalLM,AutoTokenizer
 from transformers.models.qwen3 import modeling_qwen3 as mq
 torch.set_num_threads(4);torch.manual_seed(9);start=time.perf_counter()
 tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
 model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='eager').eval()
 layer=model.model.layers[0]; old_proj=layer.self_attn.q_proj; gain=layer.input_layernorm.weight.float()
 assert bool((gain!=0).all())
 def tokens(text):return tok((text+' ')*40,return_tensors='pt')['input_ids'][:,:128]
 collected=[]
 handle=old_proj.register_forward_pre_hook(lambda m,a:collected.append((a[0].float()/gain).reshape(-1,gain.numel()).cpu()))
 for text in CALIBRATION:model(tokens(text),use_cache=False)
 handle.remove();x=torch.cat(collected);folded=old_proj.weight.float()*gain
 variants={'rtn':rtn(folded),'gptq':gptq(folded,x)}
 orig_attention=mq.eager_attention_forward;cache_stats={}
 def mirrored(module,q,k,v,mask,**kw):
  if module.layer_idx!=0:return orig_attention(module,q,k,v,mask,**kw)
  kp,ks=cache_pack(hadamard(k));vp,vs=cache_pack(hadamard(v))
  cache_stats.update(packed_payload_bytes=kp.numel()+vp.numel(),scale_bytes=(ks.numel()+vs.numel())*4,bf16_primary_bytes=(k.numel()+v.numel())*2)
  out,weights=orig_attention(module,hadamard(q).to(q.dtype),cache_dequant(kp,ks).to(k.dtype),cache_dequant(vp,vs).to(v.dtype),mask,**kw)
  return hadamard(out).to(out.dtype),weights
 result={'environment':{'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,'device':'cpu','threads':4,'model_path':model_path,'revision':REVISION},'calibration':{'texts':CALIBRATION,'tokens_each':128,'samples':len(x),'group_size':128,'damping':.05,'act_order':False,'solve_dtype':'float64'},'evaluation_texts':EVALUATION,'measurements':[]}
 try:
  for text in EVALUATION:
   ids=tokens(text);base=model(ids,use_cache=False).logits.float();base_lp=base.log_softmax(-1)
   for mode in ['baseline','rtn','gptq','gptq_rotated_kv']:
    layer.self_attn.q_proj=old_proj if mode=='baseline' else PackedProjection(*variants['rtn' if mode=='rtn' else 'gptq'],gain)
    mq.eager_attention_forward=mirrored if mode=='gptq_rotated_kv' else orig_attention
    logits=model(ids,use_cache=False).logits.float(); lp=logits.log_softmax(-1)
    result['measurements'].append({'text':text,'mode':mode,'token_nll':F.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]),ids[:,1:].reshape(-1)).item(),'kl_base_to_variant':(base_lp.exp()*(base_lp-lp)).sum(-1).mean().item(),'top1_agreement':(base.argmax(-1)==logits.argmax(-1)).float().mean().item()})
   # Verify real Cache API updates with prefill + teacher-forced single-token decode.
   layer.self_attn.q_proj=old_proj;mq.eager_attention_forward=orig_attention
   pref=model(ids[:,:64],use_cache=True);past=pref.past_key_values;values=[]
   layer.self_attn.q_proj=PackedProjection(*variants['gptq'],gain);mq.eager_attention_forward=mirrored
   for j in range(64,72):
    out=model(ids[:,j:j+1],past_key_values=past,use_cache=True);past=out.past_key_values
    values.append(bool(torch.isfinite(out.logits).all()))
   result.setdefault('cached_decode',[]).append({'prefill_tokens':64,'decode_steps':8,'finite_logits':all(values),'final_cache_length':past.get_seq_length()})
   layer.self_attn.q_proj=old_proj;mq.eager_attention_forward=orig_attention
 finally:layer.self_attn.q_proj=old_proj;mq.eager_attention_forward=orig_attention
 p,s=variants['gptq'];result['weight_bytes']={'original_bf16':old_proj.weight.numel()*2,'packed_int4':p.numel(),'fp32_scales':s.numel()*4}
 result['cache_final_example']=cache_stats;result['elapsed_seconds']=time.perf_counter()-start
 result['scope']='First-layer q_proj plus first-layer KV numerical reference. Full-sequence metrics use simulated decode precision, not native prefill; cache smoke test uses BF16 prefill; no fused CUDA, no MMA layout, no latency or whole-model compression claim. Cache mirror is regenerated for each reference attention call; BF16 primary is retained. FP8 delayed emission is tensor-tested only.'
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',default=DEFAULT_MODEL);ap.add_argument('--test-only',action='store_true');ap.add_argument('--output',default='results.json');args=ap.parse_args()
 result={'tests':tests()}
 if not args.test_only:result.update(run(args.model))
 Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
