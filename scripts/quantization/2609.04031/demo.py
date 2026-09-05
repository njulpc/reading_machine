"""Exact DSA loss/guidance equations plus Qwen W4A4 numerical transfer."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def stage_loss(pred,teacher,target,t,alpha):
 w=torch.expm1(alpha*(1-t))/math.expm1(alpha)
 return (w*(pred-teacher.detach()).square()+(1-w)*(pred-target).square()).mean()
def guidance(cond,uncond,t,tau=0.9,omega=5.):
 return uncond+omega*(cond-uncond) if t<=tau else cond

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-json');p.add_argument('--alpha',type=float,default=5.);p.add_argument('--steps',type=int,default=50);p.add_argument('--cfg-drop-steps',type=int,default=9);a=p.parse_args();assert 0<a.cfg_drop_steps<a.steps;tau=(a.steps-a.cfg_drop_steps)/a.steps
 pred=torch.tensor([1.,2.],requires_grad=True); teacher=torch.tensor([.5,1.]);target=torch.tensor([0.,0.])
 torch.testing.assert_close(stage_loss(pred,teacher,target,torch.tensor(0.),a.alpha),(pred-teacher).square().mean())
 torch.testing.assert_close(stage_loss(pred,teacher,target,torch.tensor(1.),a.alpha),(pred-target).square().mean())
 stage_loss(pred,teacher,target,torch.tensor(.5),a.alpha).backward();assert torch.isfinite(pred.grad).all()
 torch.testing.assert_close(guidance(pred,teacher,1,tau),pred);torch.testing.assert_close(guidance(pred,teacher,tau,tau),teacher+5*(pred-teacher))
 r=run_full('symmetric W4A4');r.update({'stage_equations':'5/6/11 endpoint and gradient tests PASS','alpha':a.alpha,'scheduler_steps':a.steps,'cfg_drop_steps':a.cfg_drop_steps,'tau':tau,'hyperparameter_provenance':'paper-selected alpha=5 and final-nine-step CFG drop on the paper 50-step scheduler','boundary':'Qwen is autoregressive, has no native denoising time, video target or CFG. Exact stage functions tested independently; full Qwen forward/generation only validates symmetric W4A4. No DSA video training or VBench reproduction; paper needs 24-64 H20 GPUs and synthetic video data.'});save(r,a.output_json)
if __name__=='__main__':main()
