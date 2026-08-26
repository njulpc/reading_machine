#!/usr/bin/env python3
"""Minima-KV mixed FP8/ternary page reference on Qwen3-0.6B projections."""
import argparse, glob, os, math
import torch

def ckpt(p=None):
    h=[p] if p else glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors'))
    if not h: raise FileNotFoundError('Qwen3-0.6B checkpoint missing')
    return h[0]

def fp8(x):
    # CPU-safe E4M3FN fake quantization.
    return x.to(torch.float8_e4m3fn).float()

def fwht(x):
    """Normalized Walsh-Hadamard rotation along the feature dimension."""
    n=x.shape[-1]
    if n & (n-1): raise ValueError('feature dimension must be a power of two')
    y=x.clone(); h=1
    while h<n:
        y=y.view(*y.shape[:-1],-1,2,h)
        a,b=y[...,0,:].clone(),y[...,1,:].clone()
        y=torch.stack((a+b,a-b),dim=-2).flatten(-3)
        h*=2
    return y/(n**0.5)

def tq3(x):
    # Paper-style rotated scalar quantization, with a per-page norm/scale.
    rotated=fwht(x)
    scale=rotated.abs().amax(dim=(-2,-1),keepdim=True).clamp_min(1e-12)/3
    q=torch.round(rotated/scale).clamp(-3,3)
    return fwht(q*scale)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint'); ap.add_argument('--tokens',type=int,default=128); ap.add_argument('--page-size',type=int,default=16); ap.add_argument('--recent-pages',type=int,default=2); ap.add_argument('--anchor-stride',type=int,default=4); a=ap.parse_args()
    from safetensors import safe_open
    with safe_open(ckpt(a.checkpoint),framework='pt',device='cpu') as f:
        kkey=next(k for k in f.keys() if k.endswith('k_proj.weight')); vkey=next(k for k in f.keys() if k.endswith('v_proj.weight'))
        kw=f.get_tensor(kkey).float(); vw=f.get_tensor(vkey).float()
    g=torch.Generator().manual_seed(23834); x=torch.randn(a.tokens,kw.shape[1],generator=g)
    k=x@kw.T; v=x@vw.T; pages=math.ceil(a.tokens/a.page_size); pad=pages*a.page_size-a.tokens
    if pad: k=torch.nn.functional.pad(k,(0,0,0,pad)); v=torch.nn.functional.pad(v,(0,0,0,pad))
    k=k.view(pages,a.page_size,-1); v=v.view_as(k); kh=[]; vh=[]; kinds=[]
    for i in range(pages):
        anchor=(i%a.anchor_stride==0); recent=i>=pages-a.recent_pages
        fn=fp8 if anchor or recent else tq3; kinds.append('FP8' if fn is fp8 else 'TQ3'); kh.append(fn(k[i])); vh.append(fn(v[i]))
    kh=torch.stack(kh); vh=torch.stack(vh); q=torch.randn(kw.shape[0],generator=g)
    ref=torch.softmax((k.reshape(-1,k.shape[-1])@q)/math.sqrt(k.shape[-1]),0)@v.reshape(-1,v.shape[-1])
    out=torch.softmax((kh.reshape(-1,kh.shape[-1])@q)/math.sqrt(kh.shape[-1]),0)@vh.reshape(-1,vh.shape[-1])
    bits=sum((8 if t=='FP8' else 3)*a.page_size*k.shape[-1]*2 for t in kinds); bf16=pages*a.page_size*k.shape[-1]*2*16
    print(f'pages={pages} formats={kinds} page_size={a.page_size}')
    print(f'compression_vs_bf16={bf16/bits:.4f}x relative_l2={torch.linalg.vector_norm(out-ref)/torch.linalg.vector_norm(ref):.8f}')
    assert len(kinds)==pages and torch.isfinite(out).all()

if __name__=='__main__': main()
