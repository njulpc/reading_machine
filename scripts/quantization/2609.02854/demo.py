"""Mixed INT8 projection/PTQ component transfer; all Qwen attention/norms stay FP32."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def aq(x,lo,hi):
 s=max(hi-lo,1e-12)/255;zp=round(-lo/s)
 return ((x/s+zp).round().clamp(0,255)-zp)*s

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-json');a=p.parse_args();tok,model=load();ref=logits(tok,model,EVAL);mods=[(n,m) for n,m in model.named_modules() if isinstance(m,torch.nn.Linear) and '.mlp.' in n];bounds={n:[float('inf'),-float('inf')] for n,m in mods};handles=[]
 for n,m in mods:
  def cap(mod,args,key=n):bounds[key][0]=min(bounds[key][0],float(args[0].min()));bounds[key][1]=max(bounds[key][1],float(args[0].max()))
  handles.append(m.register_forward_pre_hook(cap))
 for text in CAL:logits(tok,model,text)
 for h in handles:h.remove()
 handles=[]
 with torch.no_grad():
  for n,m in mods:
   m.weight.copy_(sym(m.weight,8))
   handles.append(m.register_forward_pre_hook(lambda mod,args,key=n:(aq(args[0],*bounds[key]),)+args[1:]))
 out=logits(tok,model,EVAL);assert torch.isfinite(out).all();generation=generate_one(tok,model)
 for h in handles:h.remove()
 save({'model':'Qwen3-0.6B','linears':len(mods),'quantized_elements':sum(m.weight.numel() for _,m in mods),'weight_bits':8,'activation_bits':8,'weight_granularity':'per output channel symmetric','activation_granularity':'static per tensor asymmetric','calibration_texts':CAL,'heldout_logits':metrics(ref,out),'generation':generation,'full_paper_reproduced':False,'boundary':'Qwen MLP PTQ component transfer only; attention and norms kept FP32 rather than paper FP16. No GroupFisher, pose retraining, UNet QAT, latent-consistency distillation, geometric fusion or Apple Neural Engine export. Vision datasets/models unavailable locally.'},a.output_json)
if __name__=='__main__':main()
