#!/usr/bin/env python3
"""Low-rank ternary multiplicative adaptation on a real Qwen3 weight tile."""
import argparse, glob, os
import torch

def ckpt(p=None):
    h=[p] if p else glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not h: raise FileNotFoundError('Qwen checkpoint missing')
    return h[0]

def ternary_ste(x):
    hard=torch.where(x>.5,torch.ones_like(x),torch.where(x<-.5,-torch.ones_like(x),torch.zeros_like(x)))
    return x+(hard-x).detach()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint'); ap.add_argument('--tile',type=int,default=128); ap.add_argument('--rank',type=int,default=4); ap.add_argument('--steps',type=int,default=120); a=ap.parse_args()
    from safetensors import safe_open
    with safe_open(ckpt(a.checkpoint),framework='pt',device='cpu') as f:
        key=next(k for k in f.keys() if k.endswith('q_proj.weight')); w=f.get_tensor(key)[:a.tile,:a.tile].float()
    scale=w.abs().mean()*1.5; base=torch.round(w/scale).clamp(-1,1)
    g=torch.Generator().manual_seed(24469); true_a=torch.randint(-1,2,(a.tile,a.rank),generator=g).float(); true_b=torch.randint(-1,2,(a.tile,a.rank),generator=g).float()
    target_mask=torch.sign(true_a@true_b.T); target=torch.sign(base*target_mask)
    A=torch.randn(a.tile,a.rank,generator=g,requires_grad=True); B=torch.randn(a.tile,a.rank,generator=g,requires_grad=True); opt=torch.optim.Adam([A,B],lr=.05)
    initial=float((base-target).square().mean())
    for _ in range(a.steps):
        opt.zero_grad(); mask=ternary_ste(torch.tanh(A)@torch.tanh(B).T/a.rank); merged=ternary_ste(base)*mask
        loss=(merged-target).square().mean(); loss.backward(); opt.step()
    hard_mask=torch.sign(ternary_ste(torch.tanh(A)@torch.tanh(B).T/a.rank).detach()); merged=base*hard_mask
    values=sorted(float(x) for x in torch.unique(merged)); trainable=A.numel()+B.numel()
    print(f'weight={key} tile={a.tile} rank={a.rank} trainable={trainable} dense_update={w.numel()}')
    print(f'initial_mse={initial:.6f} final_mse={float((merged-target).square().mean()):.6f} merged_values={values}')
    assert set(values)<= {-1.0,0.0,1.0} and trainable<w.numel()

if __name__=='__main__': main()
