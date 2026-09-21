#!/usr/bin/env python3
"""Score Centering Eq.8/14 with Qwen3 W8A8 + per-token/head KV8 reference.
CPU numerical reference: packed INT8 weights; FP32 dequantized GEMM, no GPU speed claim.
"""
import argparse, json, platform, time
from pathlib import Path
import torch
import transformers
from torch import nn
from torch.nn import functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache


def quantize(x, bits=8, floor=1e-30):
    qmax=2**(bits-1)-1
    scale=x.float().abs().amax(-1,keepdim=True).clamp_min(floor)/qmax
    q=(x.float()/scale).round().clamp(-qmax,qmax).to(torch.int8)
    return q,scale


def qdq(x, bits=8, kv=False):
    if kv:
        scale=(x.float().abs().amax(-1,keepdim=True)/(2**(bits-1)-1)).clamp_min(1e-9)
        return ((x.float()/scale).round()*scale).to(x.dtype)
    q,s=quantize(x,bits)
    return (q.float()*s).to(x.dtype)


class QuantLinear(nn.Module):
    def __init__(self, linear):
        super().__init__();self.base=linear;self.enabled=False
        self.register_buffer('q',torch.empty(0,dtype=torch.int8));self.register_buffer('scale',torch.empty(0))
        self.calls=0
    def sync(self): self.q,self.scale=quantize(self.base.weight.detach())
    def forward(self,x):
        if not self.enabled:return self.base(x)
        self.calls+=1
        return F.linear(qdq(x),self.q.float()*self.scale,self.base.bias)


class QuantEmbedding(nn.Module):
    def __init__(self,emb):
        super().__init__();self.base=emb;self.enabled=False
        self.register_buffer('q',torch.empty(0,dtype=torch.int8));self.register_buffer('scale',torch.empty(0))
    def sync(self):self.q,self.scale=quantize(self.base.weight.detach())
    def forward(self,x):
        if not self.enabled:return self.base(x)
        return F.embedding(x,self.q).float()*F.embedding(x,self.scale)


class KV8Cache(DynamicCache):
    def __init__(self,config):super().__init__(config=config);self.writes=0
    def update(self,key_states,value_states,layer_idx,cache_kwargs=None):
        self.writes+=1
        return super().update(qdq(key_states,kv=True),qdq(value_states,kv=True),layer_idx,cache_kwargs)


def weight_fn(r,mode):
    if mode=='sc':return torch.ones_like(r)
    if mode=='tis':return r.clamp_max(2.)
    if mode=='mis':return torch.where((r>=.5)&(r<=5.),r,torch.zeros_like(r))
    if mode=='is':return r
    raise ValueError(mode)


def sc_terms(logp, tokens, head_ids, head_logq, token_logq, mode='sc', eps=1e-6):
    """Eq.14: q_head*f(p/q) - rho*f(1/rho)*p_head, all detached."""
    hp=logp.gather(-1,head_ids)
    p=hp.detach().exp();q=head_logq.detach().exp()
    rho=(1-q.sum(-1)).clamp_min(eps)/(1-p.sum(-1)).clamp_min(eps)
    alpha=rho*weight_fn(1/rho,mode)
    # Match Appendix A.3: log-space ratios avoid bias from flooring q.
    coefficients=(q*weight_fn((hp.detach()-head_logq.detach()).exp(),mode)-alpha[...,None]*p).detach()
    correction=(coefficients*hp).sum(-1)
    chosen=logp.gather(-1,tokens[...,None]).squeeze(-1)
    w=weight_fn((chosen.detach()-token_logq.detach()).exp(),mode).detach()
    return w*chosen-correction,correction


@torch.random.fork_rng(devices=[])
def self_test():
    torch.manual_seed(17)
    x=torch.randn(5,31);q,s=quantize(x);z=torch.zeros(2,7)
    assert q.dtype==torch.int8 and torch.isfinite(qdq(z)).all()
    assert torch.all((q.float()*s-x).abs()<=s*.5001)
    logits=torch.randn(3,11,dtype=torch.float64,requires_grad=True)
    lp=logits.log_softmax(-1);trueq=torch.randn(3,11,dtype=torch.float64).softmax(-1)
    hq,hi=trueq.topk(5,-1);p=lp.detach().exp();hp=p.gather(-1,hi)
    rho=(1-hq.sum(-1))/(1-hp.sum(-1));qhat=p*rho[:,None];qhat.scatter_(-1,hi,hq)
    tokens=torch.tensor([0,3,10]);errors={}
    for mode in ['sc','tis','mis','is']:
        _,c=sc_terms(lp,tokens,hi,hq.log(),trueq.gather(-1,tokens[:,None]).squeeze(-1).log(),mode)
        masses=(qhat*weight_fn(p/qhat,mode)).detach()
        full=(masses*lp).sum()
        g1=torch.autograd.grad(c.sum(),logits,retain_graph=True)[0]
        g2=torch.autograd.grad(full,logits,retain_graph=True)[0]
        errors[mode]=float((g1-g2).abs().max());assert errors[mode]<1e-12
    _,on=sc_terms(lp,tokens,hi,hp.log(),lp.detach().gather(-1,tokens[:,None]).squeeze(-1))
    assert on.abs().max()<1e-12
    # Expected centered gradient under fixed qhat and a constant reward is zero.
    scores=torch.eye(11,dtype=p.dtype)[None]-p[:,None,:]
    drift=(qhat[:,:,None]*scores).sum(1)
    centered=(qhat[:,:,None]*(scores-drift[:,None,:])).sum(1)
    assert centered.abs().max()<1e-12
    # A finite log-ratio can overflow exp in FP32. MIS must mask it to zero.
    assert weight_fn(torch.tensor([float('inf')]),'mis').item()==0
    extreme=torch.tensor([[0.,-120.]],requires_grad=True)
    terms,c=sc_terms(extreme.log_softmax(-1),torch.tensor([0]),torch.tensor([[0]]),torch.tensor([[-120.]]),torch.tensor([-120.]),'mis')
    g=torch.autograd.grad(terms.sum(),extreme)[0]
    assert torch.isfinite(terms).all() and torch.isfinite(c).all() and torch.isfinite(g).all()
    # KV quantization is independent for each token/head and uses a scale floor.
    kv=torch.randn(2,3,4,7);kv[0,0,0]=0
    kv_scale=(kv.abs().amax(-1,keepdim=True)/127).clamp_min(1e-9)
    assert torch.all((qdq(kv,kv=True)-kv).abs()<=kv_scale*.5001)
    return {'gradient_equivalence_max_error':errors,'constant_reward_centered_gradient_max':float(centered.abs().max()),'uncorrected_drift_norm':float(drift.norm()),'on_policy_correction_max':float(on.detach().abs().max()),'quantization_bound_pass':True,'mis_overflow_regression_pass':True,'kv_quantization_bound_pass':True}


def run(a):
    for name in ('threads','rollouts','new_tokens','topk'):
        if getattr(a,name)<=0:raise ValueError(name+' must be positive')
    torch.set_num_threads(a.threads);torch.manual_seed(a.seed)
    result={'self_test':self_test(),'full_paper_reproduction':False,'environment':{'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,'platform':platform.platform(),'device':'cpu','threads':a.threads},'arguments':vars(a)}
    if a.self_test_only:return result
    tokenizer=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').eval()
    if a.topk>model.config.vocab_size:raise ValueError('topk exceeds vocabulary size')
    layers=[]
    for name,m in list(model.named_modules()):
        if isinstance(m,nn.Linear):
            parent,_,leaf=name.rpartition('.');w=QuantLinear(m);setattr(model.get_submodule(parent),leaf,w);layers.append(w)
    embedding=QuantEmbedding(model.model.embed_tokens);model.model.embed_tokens=embedding
    wrappers=layers+[embedding]
    for w in wrappers:w.sync()
    prompt=tokenizer('Complete the arithmetic: 2 + 3 =',return_tensors='pt')['input_ids']
    with torch.no_grad():base=model(prompt,use_cache=False).logits
    for w in wrappers:w.enabled=True
    with torch.no_grad():quant=model(prompt,past_key_values=KV8Cache(model.config),use_cache=True).logits
    result['prefill']={'tokens':prompt.shape[-1],'logits_relative_l2':float((quant-base).norm()/base.norm()),'argmax_agreement':float((quant.argmax(-1)==base.argmax(-1)).float().mean())}
    rollouts=[];start=time.time()
    with torch.no_grad():
        for _ in range(a.rollouts):
            cache=KV8Cache(model.config);current=prompt
            tokens=[];heads=[];headqs=[];chosenqs=[]
            for step in range(a.new_tokens):
                logits=model(current,past_key_values=cache,use_cache=True).logits[:,-1,:].float()
                logq=logits.log_softmax(-1)
                token=torch.multinomial(logq.exp(),1)
                hq,hi=logq.topk(a.topk,-1)
                tokens.append(token);heads.append(hi);headqs.append(hq);chosenqs.append(logq.gather(-1,token))
                current=token
            completion=torch.cat(tokens,-1);decoded=tokenizer.decode(completion[0])
            # Deliberately small diagnostic objective, not Countdown accuracy.
            reward=sum(c.isdigit() for c in decoded)/max(1,len(decoded))
            rollouts.append({'tokens':completion,'head_ids':torch.cat(heads,0),'head_logq':torch.cat(headqs,0),'token_logq':torch.cat(chosenqs,0).squeeze(-1),'reward':reward,'text':decoded,'kv_writes':cache.writes})
    for w in wrappers:w.enabled=False
    rewards=torch.tensor([r['reward'] for r in rollouts]);advantages=rewards-rewards.mean()
    optimizer=torch.optim.SGD(model.parameters(),lr=.01);optimizer.zero_grad()
    losses=[];corrections=[]
    # One actual full-parameter SGD update; sampler stays fixed for this batch.
    before=model.model.layers[-1].mlp.down_proj.base.weight.detach().clone()
    for i,r in enumerate(rollouts):
        seq=torch.cat([prompt,r['tokens']],-1)
        lp=model(seq[:,:-1],use_cache=False).logits[0,prompt.shape[-1]-1:,:].float().log_softmax(-1)
        terms,c=sc_terms(lp,r['tokens'][0],r['head_ids'],r['head_logq'],r['token_logq'],a.mode)
        loss=-advantages[i]*terms.mean()/len(rollouts);loss.backward()
        losses.append(float(loss.detach()));corrections.append(float(c.detach().abs().mean()))
    gradnorm=sum(float(p.grad.detach().float().square().sum()) for p in model.parameters() if p.grad is not None)**.5
    assert torch.isfinite(torch.tensor(gradnorm))
    optimizer.step()
    changed=float((model.model.layers[-1].mlp.down_proj.base.weight.detach()-before).norm())
    for w in wrappers:w.sync() # state-dependent requantization after trainer sync
    # Exercise the refreshed sampler, rather than stopping after buffer creation.
    for w in wrappers:w.enabled=True
    with torch.no_grad():
        post=model(prompt,past_key_values=KV8Cache(model.config),use_cache=True).logits
    assert torch.isfinite(post).all()
    result['post_sync']={'finite_logits':True,'next_token_id':int(post[0,-1].argmax()),'quantized_modules':len(wrappers),'weight_export_supported':False}
    result.update({'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),'linear_modules':len(layers),'quantized_linear_calls':sum(w.calls for w in layers),'rollouts':[{'text':r['text'],'reward':r['reward'],'kv_writes':r['kv_writes']} for r in rollouts], 'advantages':advantages.tolist(),'losses':losses,'mean_abs_centering_correction':corrections,'gradient_norm':gradnorm,'last_down_projection_update_norm':changed,'elapsed_seconds':time.time()-start,'limitations':['CPU FP32 dequantized GEMM and trainer, not paper BF16/JAX GPU kernels','KV cache stores dequantized values with per-token/head INT8 error, not packed cache','Toy digit-density reward; not Countdown or INTELLECT-2','Single SGD step; no long-run stability or speedup claim']})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',default='Qwen/Qwen3-0.6B');p.add_argument('--output',default='results.json');p.add_argument('--self-test-only',action='store_true');p.add_argument('--threads',type=int,default=4);p.add_argument('--rollouts',type=int,default=4);p.add_argument('--new-tokens',type=int,default=8);p.add_argument('--topk',type=int,default=128);p.add_argument('--mode',choices=['sc','tis','mis'],default='sc');p.add_argument('--seed',type=int,default=17)
    a=p.parse_args();r=run(a);Path(a.output).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
