"""Six-bit ramp/edge transport numerical model at a Qwen activation boundary."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def time_link(x,lo,hi,bits=6):
 step=(hi-lo)/(2**bits-1)
 # First ramp voltage that meets input: leading-edge comparator model.
 code=torch.ceil((x.clamp(lo,hi)-lo)/step).clamp(0,2**bits-1)
 return lo+code*step

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-json');a=p.parse_args();tok,model=load();m=model.model.layers[1].self_attn.q_proj;bounds=[float('inf'),-float('inf')]
 def collect(mod,args):bounds[0]=min(bounds[0],float(args[0].min()));bounds[1]=max(bounds[1],float(args[0].max()))
 h=m.register_forward_pre_hook(collect)
 for text in CAL:logits(tok,model,text)
 h.remove();ref=logits(tok,model,EVAL)
 h=m.register_forward_pre_hook(lambda mod,args:(time_link(args[0],*bounds),)+args[1:]);out=logits(tok,model,EVAL);generation=generate_one(tok,model);h.remove()
 x=torch.linspace(bounds[0],bounds[1],1024);y=time_link(x,*bounds);assert (y-x).abs().max()<=(bounds[1]-bounds[0])/63+1e-5
 save({'model':'Qwen3-0.6B','bounds':bounds,'bits':6,'levels':64,'transported_boundaries':1,'heldout_logits':metrics(ref,out),'generation':generation,'full_paper_reproduced':False,'boundary':'One activation boundary is transported using a numerical ramp. No analog convolution, photodiodes, circuit noise, wavelength scheduling or energy-delay reproduction. Calibration bounds are a Qwen transfer, not physical voltages.'},a.output_json)
if __name__=='__main__':main()
