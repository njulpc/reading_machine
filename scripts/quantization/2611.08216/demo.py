#!/usr/bin/env python3
"""ProQuant SRL, learned-scale W4A8 QAT, Eq.1 sensitivity and Algorithm 1.

Qwen3-0.6B is text-only: the executable smoke run uses a PROMPT-token proxy
mask, NOT visual tokens. It trains two decoder blocks, not the full MLLM.
The exact visual-sensitivity formula is separately checked on synthetic tensors.
"""
import argparse
import json
import math
import platform
import time
from pathlib import Path

import torch
from torch import nn
import torch.nn.functional as F


def ste_quant(x, scale, bits):
    lo, hi = -(2**(bits-1)), 2**(bits-1)-1
    r = (x / scale).clamp(lo, hi)
    q = r + (r.round()-r).detach()
    return q * scale


class QLinear(nn.Module):
    def __init__(self, old, wbits=4, abits=8):
        super().__init__()
        self.weight = nn.Parameter(old.weight.detach().float().clone())
        self.bias = None if old.bias is None else nn.Parameter(old.bias.detach().float().clone())
        s = self.weight.abs().amax(1, keepdim=True).clamp_min(1e-8)/(2**(wbits-1)-1)
        self.log_scale = nn.Parameter(s.log())
        self.wbits, self.abits, self.active = wbits, abits, False

    def forward(self, x):
        dtype = x.dtype
        a, w = x.float(), self.weight
        if self.active:
            # Dynamic per-token activation; static trainable per-output-channel weight scale.
            sa = a.detach().abs().amax(-1,keepdim=True).clamp_min(1e-8)/(2**(self.abits-1)-1)
            a = ste_quant(a,sa,self.abits)
            w = ste_quant(w,self.log_scale.exp().clamp_min(1e-8),self.wbits)
        return F.linear(a,w,self.bias).to(dtype)


def sensitivity(grad, mask):
    """Eq.1: mean subset-token L1 gradient / mean all-token L1 gradient."""
    assert mask.shape == grad.shape[:-1] and mask.any()
    g = grad.float().abs().sum(-1)
    return g[mask].mean()/g.mean().clamp_min(1e-12)


def budget(step, steps, layers):
    fractions = [(0,.5),(.3,.75),(.4,.88),(.5,1.)]
    share = max((ratio for when,ratio in fractions if step>=int(steps*when)), default=.5)
    return math.ceil(layers*share)


def qat_loss(student, teacher, labels, alpha, beta):
    ls, lt = student.float().log_softmax(-1), teacher.float().log_softmax(-1)
    ps, pt = ls.exp(), lt.exp()
    reverse = (ps*(ls-lt)).sum(-1).mean()
    forward = (pt*(lt-ls)).sum(-1).mean()
    ce = F.nll_loss(ls,labels)
    return alpha*reverse+(1-alpha)*forward+beta*ce, (forward,reverse,ce)


def unit_checks():
    g = torch.tensor([[[1.,1.],[3.,3.]]])
    assert torch.allclose(sensitivity(g,torch.tensor([[True,False]])),torch.tensor(.5))
    assert [budget(t,100,28) for t in [0,30,40,50]] == [14,21,25,28]
    q = QLinear(nn.Linear(8,4));q.active=True
    x = torch.randn(2,3,8,requires_grad=True);q(x).square().mean().backward()
    assert q.log_scale.grad is not None and torch.isfinite(q.log_scale.grad).all()
    assert q.weight.grad is not None and x.grad is not None
    logits=torch.randn(5,11);labels=torch.arange(5)
    loss,parts=qat_loss(logits,logits,labels,.5,0)
    assert abs(float(loss))<1e-6
    return {'assertions':5,'schedule_28_blocks':[14,21,25,28]}


def replace_linears(module, wrappers):
    for name, child in list(module.named_children()):
        if isinstance(child,nn.Linear):
            q=QLinear(child);setattr(module,name,q);wrappers.append(q)
        else:replace_linears(child,wrappers)


def run(args):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    started=time.time();torch.set_num_threads(4);torch.manual_seed(23)
    checks=unit_checks()
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,
        torch_dtype=torch.bfloat16,attn_implementation='eager').eval()
    prompts=['Explain in one sentence why model quantization saves memory.',
             'Explain why calibration data matters for numerical accuracy.']
    examples=[]
    with torch.no_grad():
        for prompt in prompts:
            rendered=tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,
                add_generation_prompt=True,enable_thinking=False)
            prefix=tok(rendered,return_tensors='pt')['input_ids']
            ids=model.generate(prefix,attention_mask=torch.ones_like(prefix),do_sample=True,
                temperature=.7,top_p=.8,top_k=20,repetition_penalty=1.,
                max_new_tokens=args.new_tokens,pad_token_id=tok.eos_token_id)
            start=prefix.shape[1]-1
            logits=model(ids,use_cache=False).logits[0,start:-1].float().detach()
            labels=ids[0,start+1:]
            examples.append({'ids':ids,'teacher':logits,'labels':labels,'start':start,
                'prompt_tokens':prefix.shape[1],'response':tok.decode(labels)})
    # Average target-token probability, fixed once; paper does not give a numeric beta.
    alpha=float(torch.cat([e['teacher'].softmax(-1).gather(-1,e['labels'][:,None]).flatten() for e in examples]).mean())
    model.requires_grad_(False)
    bylayer=[]
    for layer in model.model.layers[:args.train_blocks]:
        wrappers=[];replace_linears(layer,wrappers);bylayer.append(wrappers)
    params=[p for p in model.parameters() if p.requires_grad]
    weights=[p for group in bylayer for q in group for p in [q.weight] + ([] if q.bias is None else [q.bias])]
    scales=[q.log_scale for group in bylayer for q in group]
    opt=torch.optim.AdamW([{'params':weights,'lr':args.weight_lr},
                          {'params':scales,'lr':args.scale_lr}],weight_decay=0)
    saved={}
    handles=[]
    for index,layer in enumerate(model.model.layers[:args.train_blocks]):
        def hook(module,inputs,output,idx=index):
            value=output[0] if isinstance(output,tuple) else output
            value.retain_grad();saved[idx]=value
        handles.append(layer.register_forward_hook(hook))
    timings={int(args.steps*f) for f in [0,.3,.4,.5]}
    active=set();logs=[]
    for step in range(args.steps):
        e=examples[step%len(examples)];opt.zero_grad(set_to_none=True);saved.clear()
        logits=model(e['ids'],use_cache=False).logits[0,e['start']:-1]
        loss,parts=qat_loss(logits,e['teacher'],e['labels'],alpha,args.beta)
        loss.backward()
        mask=torch.zeros(e['ids'].shape,dtype=torch.bool)
        mask[:,:e['prompt_tokens']]=True  # Explicit text proxy, never represented as vision.
        tau=[float(sensitivity(saved[i].grad,mask)) for i in range(args.train_blocks)]
        torch.nn.utils.clip_grad_norm_(params,1.)
        opt.step()
        if step in timings:
            # Monotone PBA activation; rank remaining candidates by current tau.
            target=budget(step,args.steps,args.train_blocks)
            order=sorted(range(args.train_blocks),key=lambda i:tau[i],reverse=True)
            for i in order:
                if len(active)>=target:break
                active.add(i)
            for i in active:
                for q in bylayer[i]:q.active=True
        logs.append({'step':step,'loss':float(loss),'forward_kl':float(parts[0]),
            'reverse_kl':float(parts[1]),'ce':float(parts[2]),'prompt_proxy_tau':tau,
            'active_blocks_after_step':sorted(active)})
        assert torch.isfinite(loss)
        print(json.dumps(logs[-1]),flush=True)
    for h in handles:h.remove()
    results=[]
    with torch.no_grad():
        for e in examples:
            out=model(e['ids'],use_cache=False).logits[0,e['start']:-1]
            _,parts=qat_loss(out,e['teacher'],e['labels'],alpha,args.beta)
            results.append({'forward_kl':float(parts[0]),'ce':float(parts[2])})
    result={'paper':'2611.08216','model':args.model,'torch':torch.__version__,
        'python':platform.python_version(),'device':'cpu','model_dtype':'bfloat16',
        'trained_parameters_dtype':'float32','unit_checks':checks,'seed':23,
        'steps':args.steps,'train_blocks':args.train_blocks,'weight_bits':4,'activation_bits':8,
        'weight_lr':args.weight_lr,'scale_lr':args.scale_lr,'beta':args.beta,'alpha':alpha,
        'prompts':prompts,'srl_responses':[e['response'] for e in examples],
        'sampling':{'temperature':.7,'top_p':.8,'top_k':20,'max_new_tokens':args.new_tokens},
        'logs':logs,'final_training_examples':results,'elapsed_seconds':time.time()-started,
        'limitations':'Text-only Qwen3 cannot supply vision gradients. Prompt-token proxy used explicitly; exact Eq.1 checked synthetically. Only first two blocks W4A8 QAT, other blocks BF16. Two handwritten prompts, ten steps, not LLaVA-680K/5 epochs. No multimodal recovery claim, held-out task accuracy, packed low-bit checkpoint or hardware speed claim. Learning rates and beta are local smoke-test choices; not asserted to be paper defaults.'}
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('Saved',args.output,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--model',default='Qwen/Qwen3-0.6B')
    p.add_argument('--steps',type=int,default=10)
    p.add_argument('--train-blocks',type=int,default=2)
    p.add_argument('--new-tokens',type=int,default=16)
    p.add_argument('--weight-lr',type=float,default=1e-5)
    p.add_argument('--scale-lr',type=float,default=1e-4)
    p.add_argument('--beta',type=float,default=.1)
    p.add_argument('--output',default='results.json')
    run(p.parse_args())
