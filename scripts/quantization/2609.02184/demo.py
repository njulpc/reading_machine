"""CCA compression components on real Qwen weight blocks; not a 4DGS scene replica."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def linear_quant(x,bits):
 lo=x.amin(0,keepdim=True);hi=x.amax(0,keepdim=True);s=(hi-lo).clamp_min(1e-12)/(2**bits-1)
 return ((x-lo)/s).round()*s+lo

def compand(x,mu):return x.sign()*torch.log1p(mu*x.abs())/math.log1p(mu)
def expand(x,mu):return x.sign()*torch.expm1(x.abs()*math.log1p(mu))/mu

def residual_vq(x,k=256,steps=10):
 centers=x[torch.randperm(len(x))[:k]].clone()
 for _ in range(steps):
  idx=torch.cdist(x,centers).argmin(1)
  sums=torch.zeros_like(centers).index_add_(0,idx,x);counts=torch.bincount(idx,minlength=k).clamp_min(1).unsqueeze(1)
  centers=torch.where((torch.bincount(idx,minlength=k)>0).unsqueeze(1),sums/counts,centers)
 return centers,torch.cdist(x,centers).argmin(1)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-json');a=p.parse_args();tok,model=load();w=model.model.layers[0].self_attn.q_proj.weight.detach().flatten()[:32768].reshape(-1,32)
 norm=w.std().clamp_min(1e-8);x=w/norm;cond=torch.stack([x.mean(1),x.std(1),x.abs().max(1).values],1)
 enc=torch.nn.Sequential(torch.nn.Linear(35,32),torch.nn.ReLU(),torch.nn.Linear(32,8));dec=torch.nn.Sequential(torch.nn.Linear(11,32),torch.nn.ReLU(),torch.nn.Linear(32,32));opt=torch.optim.Adam(list(enc.parameters())+list(dec.parameters()),lr=.003)
 for _ in range(40):
  z=enc(torch.cat([x,cond],1));pred=dec(torch.cat([z,cond],1));loss=F.mse_loss(pred,x);opt.zero_grad();loss.backward();opt.step()
 with torch.no_grad():
  z=linear_quant(enc(torch.cat([x,cond],1)),8);pred=dec(torch.cat([z,cond],1));centers,idx=residual_vq(x-pred);out=pred+centers[idx]
  test=torch.linspace(-1,1,64);torch.testing.assert_close(expand(compand(test,255),255),test,atol=1e-6,rtol=1e-5)
 save({'model':'Qwen3-0.6B','rows':len(x),'residual_codebook':256,'scalar_bits':12,'autoencoder_only':metrics(x,pred),'autoencoder_residual':metrics(x,out),'scalar_12bit_error':metrics(cond,linear_quant(cond,12)),'full_paper_reproduced':False,'boundary':'Qwen rows and row statistics replace SH-AC/geometric conditions for component verification only. 8D latent, 8bit latent, mu=255 and 40 training steps are demo choices, not claimed paper defaults. No CDF deformation hash, scene rendering, archive Zstandard, or compressed Qwen checkpoint.'},a.output_json)
if __name__=='__main__':main()
