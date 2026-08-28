#!/usr/bin/env python3
"""Qwen3-0.6B ternary checkpoint-to-mask reference for Ankhdjet."""
import argparse
import glob
import json
import os

import torch


def model_dir(arg=None):
    if arg:
        return arg
    hits=glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits=[p for p in hits if os.path.exists(os.path.join(p,'config.json'))]
    if not hits:
        raise FileNotFoundError('Pass --model-dir for a local Qwen3-0.6B snapshot')
    return hits[0]


def ternarize(weight):
    x=weight.detach().float()
    scale=x.abs().mean().clamp_min(1e-12)
    q=(x/scale).round().clamp(-1,1).to(torch.int8)
    return q,scale


def pack_two_bit(q):
    """Encode {-1,0,+1} as {0,1,2}, four weights per byte."""
    code=(q.flatten().to(torch.uint8)+1)
    pad=(-code.numel())%4
    if pad:
        code=torch.nn.functional.pad(code,(0,pad),value=1)
    code=code.view(-1,4)
    packed=code[:,0] | (code[:,1]<<2) | (code[:,2]<<4) | (code[:,3]<<6)
    return packed,pad


def unpack_two_bit(packed,count):
    shifts=torch.tensor([0,2,4,6],dtype=torch.uint8)
    code=((packed[:,None]>>shifts)&3).flatten()[:count]
    return code.to(torch.int8)-1


def main():
    p=argparse.ArgumentParser();p.add_argument('--model-dir');p.add_argument('--max-elements',type=int,default=1048576)
    args=p.parse_args()
    from transformers import AutoModelForCausalLM
    model=AutoModelForCausalLM.from_pretrained(model_dir(args.model_dir),local_files_only=True,dtype=torch.float32).eval()
    name,module=next((n,m) for n,m in model.named_modules() if isinstance(m,torch.nn.Linear) and n.endswith('q_proj'))
    weight=module.weight.detach().flatten()[:args.max_elements]
    q,scale=ternarize(weight)
    packed,pad=pack_two_bit(q)
    restored_q=unpack_two_bit(packed,q.numel())
    assert torch.equal(q.cpu(),restored_q.cpu())
    dequant=restored_q.float()*scale
    zeros=(q==0).float().mean().item()
    result={'model':'Qwen3-0.6B','tensor':name+'.weight','elements':q.numel(),'ternary_scale':scale.item(),'zero_fraction':zeros,'packed_bytes':packed.numel(),'effective_bits_per_weight':packed.numel()*8/q.numel(),'roundtrip_exact':True,'relative_l2':((weight-dequant).norm()/weight.norm()).item(),'simulated_mask_read_energy_pj_per_weight_from_paper':[0.98,1.73]}
    print(json.dumps(result,indent=2))
    assert set(q.unique().tolist()) <= {-1,0,1}
    assert result['effective_bits_per_weight'] <= 2.00001


if __name__=='__main__':main()
