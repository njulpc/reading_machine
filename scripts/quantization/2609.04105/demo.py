"""Direct-P affine code map and represented normalization, not Blackwell kernel."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def direct_p(scores,A=1.5,B=1.2):
 # Exact row max reference for CPU stability; paper fast path uses no full scan.
 m=scores.amax(-1,keepdim=True);z=(scores-m)/math.log(2);width=z.shape[-1]
 z=F.pad(z,(0,(-width)%32),value=-float('inf'));blocks=z.reshape(*z.shape[:-1],-1,32)
 e=torch.ceil(blocks.amax(-1,keepdim=True)).clamp(min=-126,max=127)
 code=e2m1((A*(blocks-e+math.log2(6))+B).clamp_min(0));represented=(torch.pow(2.,e)*code/6).reshape(z.shape)[...,:width]
 return represented/represented.sum(-1,keepdim=True).clamp_min(1e-30)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-json');a=p.parse_args();tok,model=load();captured={}
 m=model.model.layers[0].self_attn
 def capture(mod,args):captured['x']=args[0].detach()
 h=m.q_proj.register_forward_pre_hook(capture);logits(tok,model,' '.join(CAL));h.remove();x=captured['x']
 with torch.no_grad():
  q=m.q_proj(x).reshape(1,-1,model.config.num_attention_heads,model.config.head_dim).transpose(1,2)
  k=m.k_proj(x).reshape(1,-1,model.config.num_key_value_heads,model.config.head_dim).transpose(1,2).repeat_interleave(model.config.num_attention_heads//model.config.num_key_value_heads,dim=1)
  v=m.v_proj(x).reshape(1,-1,model.config.num_key_value_heads,model.config.head_dim).transpose(1,2).repeat_interleave(model.config.num_attention_heads//model.config.num_key_value_heads,dim=1)
  scores=q@k.transpose(-1,-2)/math.sqrt(model.config.head_dim);ref=scores.softmax(-1)@v
  approx=direct_p(nvfp4(q)@nvfp4(k).transpose(-1,-2)/math.sqrt(model.config.head_dim));vt=v.transpose(-1,-2);width=vt.shape[-1];vp=F.pad(vt,(0,(-width)%32));vb=vp.reshape(*vp.shape[:-1],-1,32);amp=2**torch.ceil(torch.log2(vb.abs().amax(-1,keepdim=True).clamp_min(1e-30)));vq=(e2m1(vb*6/amp)*amp/6).reshape(vp.shape)[...,:width].transpose(-1,-2);out=approx@vq
  err=float((approx.sum(-1)-1).abs().max());assert err<1e-5 and torch.isfinite(out).all()
 save({'model':'Qwen3-0.6B','operator_shape':list(scores.shape),'output_error':metrics(ref,out),'row_sum_max_error':err,'A':1.5,'B':1.2,'P_block':32,'full_paper_reproduced':False,'boundary':'Real first-layer projections used as noncausal operator inputs before RoPE/QK normalization. V uses block-32 power-of-two MX reconstruction. No folded K64 scales, sampled guard, TMEM packing, backward or full-model substitution. Thus not a complete FP4 attention reproduction and no speedup claimed.'},a.output_json)
if __name__=='__main__':main()
