#!/usr/bin/env python3
"""SandwichQuant affine-only pre/post correction on a Qwen3 RMSNorm->Linear path."""
import argparse, glob, os
import torch

def ckpt(p=None):
    h=[p] if p else glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not h: raise FileNotFoundError('Qwen3-0.6B checkpoint missing')
    return h[0]

def q4(w, group=128):
    shape=w.shape; x=w.flatten(); pad=(-x.numel())%group
    if pad: x=torch.nn.functional.pad(x,(0,pad))
    b=x.view(-1,group); s=b.abs().amax(1,keepdim=True).clamp_min(1e-12)/7
    y=(torch.round(b/s).clamp(-8,7)*s).flatten()
    return y[:w.numel()].view(shape)

def rms(x,scale): return x*torch.rsqrt(x.square().mean(-1,keepdim=True)+1e-6)*scale

def fit(scale,x,target,wq,steps,lr):
    opt=torch.optim.Adam([scale],lr=lr)
    for _ in range(steps):
        opt.zero_grad(); loss=(rms(x,scale)@wq.T-target).square().mean(); loss.backward(); opt.step()
    return float(loss.detach())

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint'); ap.add_argument('--steps',type=int,default=40); ap.add_argument('--lr',type=float,default=.02); ap.add_argument('--tokens',type=int,default=32); a=ap.parse_args()
    from safetensors import safe_open
    with safe_open(ckpt(a.checkpoint),framework='pt',device='cpu') as f:
        wk=next(k for k in f.keys() if k.endswith('q_proj.weight')); nk=next(k for k in f.keys() if k.endswith('input_layernorm.weight'))
        w=f.get_tensor(wk).float(); n=f.get_tensor(nk).float()
    g=torch.Generator().manual_seed(24173); x=torch.randn(a.tokens,w.shape[1],generator=g); target=rms(x,n)@w.T; wq=q4(w)
    base=float((rms(x,n)@wq.T-target).square().mean())
    pre=n.clone().requires_grad_(); pre_loss=fit(pre,x,target,wq,a.steps,a.lr)
    frozen=q4(w); post=pre.detach().clone().requires_grad_(); post_loss=fit(post,x,target,frozen,a.steps,a.lr/2)
    print(f'weight={wk} affine={nk} tokens={a.tokens} group=128 steps={a.steps}+{a.steps}')
    print(f'w4_mse={base:.8e} pre_affine_mse={pre_loss:.8e} post_affine_mse={post_loss:.8e} closure={(base-post_loss)/base:.4%}')
    assert post_loss<base and post.numel()==w.shape[1]

if __name__=='__main__': main()
