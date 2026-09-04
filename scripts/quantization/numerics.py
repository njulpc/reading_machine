"""CPU numerical references; all returned tensors are dequantized, not packed kernels."""
import json, math, os, platform, time
from pathlib import Path
import torch
import torch.nn.functional as F
MODEL = os.environ.get('QWEN_MODEL_PATH', 'Qwen/Qwen3-0.6B')
CAL = ['量化需要校准激活。', 'Compression balances quality and storage.', '不同层的数值范围并不相同。', 'The cache grows with sequence length.']
EVAL = '请简要解释为什么模型压缩需要独立测试。'
def resolve_model():
 if Path(MODEL).is_dir(): return MODEL
 from huggingface_hub import snapshot_download
 return snapshot_download(MODEL, local_files_only=True)
def load():
 from transformers import AutoModelForCausalLM, AutoTokenizer
 torch.set_num_threads(4); torch.manual_seed(42)
 checkpoint=resolve_model()
 tok=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True)
 model=AutoModelForCausalLM.from_pretrained(checkpoint,local_files_only=True,dtype=torch.float32).eval()
 return tok,model
def metrics(a,b):
 a,b=a.float().flatten(),b.float().flatten()
 return {'mse':float((a-b).square().mean()),'relative_l2':float((a-b).norm()/a.norm().clamp_min(1e-12)),'cosine':float(F.cosine_similarity(a,b,dim=0))}
def logits(tok,model,text):
 with torch.no_grad(): return model(**tok(text,return_tensors='pt'),use_cache=False).logits[:,-1].float()
def e2m1(x):
 # RNE at the midpoints: even encoded mantissa/significand wins.
 levels=x.new_tensor([0,.5,1,1.5,2,3,4,6]); a=x.abs()
 mid=(levels[1:]+levels[:-1])/2
 idx=torch.bucketize(a.contiguous(),mid)
 for j in [1,3,5]: idx=torch.where(a==mid[j],j+1,idx)
 return levels[idx]*x.sign()
def nvfp4(x,global_scale=None):
 shape=x.shape; width=shape[-1]; p=F.pad(x.float(),(0,(-width)%16)); blocks=p.reshape(*p.shape[:-1],-1,16)
 g=x.abs().max().clamp_min(1e-12)/(6*448) if global_scale is None else torch.as_tensor(global_scale).clamp_min(1e-12)
 local=(blocks.abs().amax(-1,keepdim=True)/(6*g)).clamp(max=448)
 local=local.to(torch.float8_e4m3fn).float().clamp_min(2**-9)
 return (e2m1(blocks/(g*local))*g*local).reshape(p.shape)[...,:width].to(x.dtype)
def sym(x,bits=4):
 s=x.detach().abs().amax(-1,keepdim=True).clamp_min(1e-12)/(2**(bits-1)-1)
 return ((x/s).round().clamp(-(2**(bits-1)-1),2**(bits-1)-1)*s).to(x.dtype)
def ste_sym(x,bits=4): return x+(sym(x,bits)-x).detach()
def nf4(x,block=64):
 levels=x.new_tensor([-1,-.6961928009986877,-.5250730514526367,-.39491748809814453,-.28444138169288635,-.18477343022823334,-.09105003625154495,0,.07958029955625534,.16093020141124725,.24611230194568634,.33791524171829224,.44070982933044434,.5626170039176941,.7229568362236023,1])
 f=x.flatten();p=F.pad(f,(0,(-f.numel())%block)).reshape(-1,block);s=p.abs().amax(-1,keepdim=True).clamp_min(1e-12)
 idx=torch.bucketize((p/s).contiguous(),(levels[1:]+levels[:-1])/2)
 return (levels[idx]*s).flatten()[:f.numel()].reshape(x.shape)
def run_full(kind):
 tok,model=load(); ref=logits(tok,model,EVAL); bounds={}; handles=[]
 linears=[(n,m) for n,m in model.named_modules() if isinstance(m,torch.nn.Linear) and n!='lm_head']
 if kind=='nvfp4':
  for n,m in linears:
   def cap(mod,args,key=n): bounds[key]=max(bounds.get(key,0),float(args[0].detach().abs().max()))
   handles.append(m.register_forward_pre_hook(cap))
  for p in CAL: logits(tok,model,p)
  for h in handles:h.remove()
  handles=[]
 count=0
 with torch.no_grad():
  for n,m in linears:
   q=nvfp4(m.weight) if kind=='nvfp4' else sym(m.weight)
   m.weight.copy_(q);count+=m.weight.numel()
   def hook(mod,args,key=n):
    q=nvfp4(args[0],bounds[key]/(6*448)) if kind=='nvfp4' else sym(args[0])
    return (q,)+args[1:]
   handles.append(m.register_forward_pre_hook(hook))
 out=logits(tok,model,EVAL)
 assert torch.isfinite(out).all()
 for h in handles:h.remove()
 return {'model':'Qwen3-0.6B','checkpoint':str(MODEL),'parameters':sum(p.numel() for p in model.parameters()),'linears':len(linears),'quantized_elements':count,'heldout_logits':metrics(ref,out),'calibration_texts':CAL if kind=='nvfp4' else [],'quantization':kind,'storage':'FP32 dequantized reference; no physical memory reduction claimed','full_paper_reproduced':False}
def save(result,path=None):
 import transformers
 result.update({'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,'platform':platform.platform(),'cuda':torch.cuda.is_available(),'status':'executed'})
 s=json.dumps(result,ensure_ascii=False,indent=2);print(s)
 if path:Path(path).write_text(s+'\n')
