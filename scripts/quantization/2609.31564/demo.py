#!/usr/bin/env python3
"""WeightPE Appendix A CPU reference, with real Qwen3 layer calibration/QAT.
One shared grammar, row boundaries, length buckets, global code L2 budget,
frequency leaders, strict independent sets, batched merges, periodic STE.
"""
import argparse, collections, json, math, platform, time
from pathlib import Path
import numpy as np
import torch

MODEL='Qwen/Qwen3-0.6B'
REVISION='c1899de289a04d12100db370d81485cdf75e47ca'
CALIBRATION=['Explain the difference between a model and its weights.',
 'A compact representation can preserve useful patterns.',
 'The child reads a story about the moon.', 'Multiply a matrix by a vector.']
TEST=['Describe a cold winter morning.', 'How do birds find their way home?']

class Grammar:
    def __init__(self,codes,tau,leaders=32,target=64,seed=42):
        if not math.isfinite(tau) or tau < 0 or leaders <= 0 or target < 0:
            raise ValueError('tau must be finite/nonnegative, leaders positive, target nonnegative')
        raw=[np.asarray(row) for row in codes]
        if not raw or any(row.ndim != 1 or not row.size or not np.isfinite(row).all() or
                          np.any(row != np.round(row)) or np.any(row < -127) or np.any(row > 127) for row in raw):
            raise ValueError('codes must contain nonempty rows of signed symmetric INT8 integers')
        self.original=[np.array(row,dtype=np.int64,copy=True) for row in raw]
        for row in self.original: row.flags.writeable=False
        self.n_codes=sum(row.size for row in self.original)
        self.rows=[list(map(int,row)) for row in self.original]
        self.expansions={int(v):(int(v),) for row in self.original for v in np.unique(row)}
        self.rules={};self.next_symbol=128;self.tau=float(tau);self.leaders=leaders
        self.target=target;self.rng=np.random.default_rng(seed)
    def decode(self):
        rows=[np.array([v for sym in row for v in self.expansions[sym]],dtype=np.int64) for row in self.rows]
        return np.stack(rows) if len({len(row) for row in rows}) == 1 else rows
    def distortion(self):
        return float(sum(np.square(row-original).sum() for row,original in zip(self.decode(),self.original)))
    def size(self):return sum(map(len,self.rows))+2*len(self.rules)
    def occurrences(self):
        out=[]
        for row_idx,row in enumerate(self.rows):
            pos=0
            for j,sym in enumerate(row):
                if j+1<len(row):
                    pair=(sym,row[j+1]);value=self.expansions[pair[0]]+self.expansions[pair[1]]
                    out.append((row_idx,j,pos,pair,value))
                pos+=len(self.expansions[sym])
        return out
    @staticmethod
    def independent(occ,priorities):
        values={(r,j):priorities[k] for k,(r,j,*_) in enumerate(occ)}
        return [k for k,(r,j,*_) in enumerate(occ) if np.isfinite(priorities[k]) and
                priorities[k]>values.get((r,j-1),-np.inf) and priorities[k]>values.get((r,j+1),-np.inf)]
    def rewrite(self):
        occ=self.occurrences();cost=np.full(len(occ),np.inf);chosen={};buckets=collections.defaultdict(list)
        for k,o in enumerate(occ):buckets[len(o[4])].append(k)
        rho2=self.tau**2/self.n_codes
        for length,ks in buckets.items():
            if length<2 or len(ks)<2:continue
            freq=collections.Counter(occ[k][3] for k in ks);leader_pairs=[];vectors=[]
            for pair,count in sorted(freq.items(),key=lambda kv:(-kv[1],kv[0]))[:8*self.leaders]:
                v=np.array(self.expansions[pair[0]]+self.expansions[pair[1]],dtype=float)
                if not vectors or min(float(np.square(v-a).sum()) for a in vectors)>rho2*length:
                    leader_pairs.append(pair);vectors.append(v)
                if len(vectors)==self.leaders:break
            if not vectors:continue
            leaders=np.stack(vectors)
            for k in ks:
                r,j,pos,pair,current=occ[k];orig=self.original[r][pos:pos+length].astype(float)
                distances=np.square(leaders-orig).sum(1)
                if pair in leader_pairs:distances[leader_pairs.index(pair)]=np.inf
                t=int(distances.argmin())
                if not np.isfinite(distances[t]):continue
                cost[k]=distances[t]-np.square(np.asarray(current)-orig).sum();chosen[k]=leader_pairs[t]
        independent=self.independent(occ,-cost)
        independent.sort(key=lambda k:(cost[k],k));remaining=self.tau**2-self.distortion();spent=0.;accepted=[]
        for k in independent:
            if spent+cost[k]>remaining+1e-9:break
            accepted.append(k);spent+=float(cost[k])
        # All decisions use the round-start grammar, and spans never overlap.
        for k in accepted:
            r,j,_,_,_=occ[k];self.rows[r][j:j+2]=chosen[k]
        assert self.distortion()<=self.tau**2+1e-6
        return len(accepted)
    def merge(self):
        occ=self.occurrences();freq=collections.Counter(o[3] for o in occ)
        priorities=[freq[o[3]]+self.rng.uniform(0,1e-6) if freq[o[3]]>=2 else -np.inf for o in occ]
        selected=self.independent(occ,priorities);mapping={}
        for k in selected:
            pair=occ[k][3]
            if pair not in mapping:
                sym=self.next_symbol;self.next_symbol+=1;mapping[pair]=sym
                self.rules[sym]=pair;self.expansions[sym]=self.expansions[pair[0]]+self.expansions[pair[1]]
        # Reverse index order keeps positions in each token sequence valid.
        for k in sorted(selected,key=lambda k:(occ[k][0],occ[k][1]),reverse=True):
            r,j,_,pair,_=occ[k];self.rows[r][j:j+2]=[mapping[pair]]
        return len(mapping)
    def run(self,max_rounds=64):
        if max_rounds <= 0: raise ValueError('max_rounds must be positive')
        stall=0;trace=[];reason='max_rounds'
        for rnd in range(max_rounds):
            before=self.size()
            if before<=self.target or all(len(r)<2 for r in self.rows):reason='target_or_short';break
            rewrites=self.rewrite() if self.distortion()<self.tau**2 else 0
            merges=self.merge();after=self.size()
            trace.append({'round':rnd,'rewrites':rewrites,'new_rules':merges,'size':after,'distortion':self.distortion()})
            if rewrites==0 and merges==0:reason='no_change';break
            stall=stall+1 if after>=before else 0
            if stall==2:reason='two_stalls';break
        return self.decode(),{'symbols':self.size(),'rules':len(self.rules),'residual_length':sum(map(len,self.rows)),
             'distortion':self.distortion(),'budget':self.tau**2,'stop_reason':reason,'trace':trace}

def quantize(w):
    scale=w.detach().abs().amax(1,keepdim=True).clamp_min(1e-12)/127
    codes=torch.round(w.detach()/scale).clamp(-127,127).to(torch.int64)
    return codes,scale

def tests():
    x=np.array([[5,3,5,5,3,5,8,2,5,3,4,6]])
    g=Grammar(x,math.sqrt(5),leaders=2,target=0)
    assert g.rewrite()==2
    expected=np.array([[5,3,5,5,3,5,8,3,5,3,5,6]])
    assert np.array_equal(g.decode(),expected) and g.distortion()==2
    before=g.decode().copy();g.merge();assert np.array_equal(g.decode(),before)
    # Deterministic strict-local-max tie handling is implementation dependent;
    # decoding and global budget are invariant under merge ordering.
    g=Grammar(np.array([[1,2,1,2],[1,2,1,2]]),0,target=0)
    original=g.decode().copy();_,info=g.run();assert np.array_equal(g.decode(),original)
    assert all(len([v for s in row for v in g.expansions[s]])==4 for row in g.rows)
    w=torch.randn(2,4,requires_grad=True);projected=torch.zeros_like(w)
    (w+(projected-w).detach()).sum().backward();assert torch.equal(w.grad,torch.ones_like(w))
    a=np.array([[1,2,1,2]]);g=Grammar(a,0);a[0,0]=99
    assert g.distortion()==0
    g=Grammar([[1,2,1,2],[1,2]],0,target=0)
    decoded,_=g.run();assert [len(row) for row in decoded]==[4,2] and g.distortion()==0
    return {'immutable_original':'PASS','ragged_row_boundaries':'PASS','paper_worked_rewrite':'PASS','lossless_merge_decode':'PASS','row_boundaries':'PASS','STE_identity_gradient':'PASS'}

def load_model_inputs(mock):
    from transformers import AutoModelForCausalLM, AutoTokenizer, Qwen3Config, Qwen3ForCausalLM
    if mock:
        torch.manual_seed(42)
        config=Qwen3Config(vocab_size=128,hidden_size=16,intermediate_size=32,
            num_hidden_layers=2,num_attention_heads=2,num_key_value_heads=1,head_dim=8,
            max_position_embeddings=128,tie_word_embeddings=True,bos_token_id=1,eos_token_id=2,pad_token_id=0)
        model=Qwen3ForCausalLM(config).eval()
        g=torch.Generator().manual_seed(43)
        batches=[{'input_ids':torch.randint(3,128,(1,8),generator=g)} for _ in range(3)]
        return model,None,batches,{'input_ids':torch.randint(3,128,(1,7),generator=g)}
    from huggingface_hub import snapshot_download
    path=snapshot_download(MODEL,revision=REVISION,local_files_only=True)
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,torch_dtype=torch.float32).eval()
    return model,tok,[tok(text,return_tensors='pt') for text in CALIBRATION],tok(TEST[0],return_tensors='pt')


def validate_deployment(model,tok,probe,baseline,export):
    import gc
    from transformers import AutoModelForCausalLM
    with torch.no_grad():
        logits=model(**probe,use_cache=False).logits
        assert torch.isfinite(logits).all(), 'nonfinite quantized logits'
        generated=model.generate(**probe,max_new_tokens=2,do_sample=False,use_cache=False,
                                 pad_token_id=model.config.pad_token_id or model.config.eos_token_id)
    result={'finite_logits':True,'logits_relative_l2':float(torch.linalg.norm(logits-baseline)/torch.linalg.norm(baseline)),
            'generated_token_ids':generated[0,probe['input_ids'].shape[1]:].tolist(),
            'generated_text':tok.decode(generated[0,probe['input_ids'].shape[1]:]) if tok else None,
            'forward_scope':'All decoder Linear weights replaced; embedding, norms and tied lm_head retained in FP32',
            'export':'not requested'}
    if export:
        model.save_pretrained(export,safe_serialization=True)
        if tok: tok.save_pretrained(export)
        restored=AutoModelForCausalLM.from_pretrained(export,local_files_only=True).eval()
        with torch.no_grad(): after=restored(**probe,use_cache=False).logits
        err=float((after-logits).abs().max());assert err<1e-5
        result.update({'export':'FP32 dequantized HF checkpoint, not packed low-bit storage',
                       'reload_max_logit_error':err})
        del restored;gc.collect()
    return result

def full_model(a):
    start=time.monotonic()
    if not a.mock:
        from transformers import AutoConfig
        from huggingface_hub import snapshot_download
        path=snapshot_download(MODEL,revision=REVISION,local_files_only=True)
        c=AutoConfig.from_pretrained(path,local_files_only=True)
        n=3*c.hidden_size*c.intermediate_size*c.num_hidden_layers
        # Python occurrence tuples, values, indices, costs and dictionaries coexist.
        # 160 bytes/code is a conservative lower estimate, excluding model/optimizer memory.
        estimate=n*160
        if estimate>a.memory_budget_gib*1024**3:
            raise MemoryError(f'Shared MLP grammar has {n} codes; Python reference lower estimate '
                              f'{estimate/1024**3:.2f} GiB exceeds {a.memory_budget_gib} GiB budget. '
                              'Use --mock for structural coverage; real full-model run has NOT passed.')
    model,tok,batches,probe=load_model_inputs(a.mock);model.requires_grad_(False)
    modules={name:mod for name,mod in model.named_modules() if isinstance(mod,torch.nn.Linear) and name.startswith('model.layers.')}
    mlp={name:mod for name,mod in modules.items() if '.mlp.' in name}
    attention={name:mod for name,mod in modules.items() if '.self_attn.' in name}
    parameters={name+'.weight':mod.weight for name,mod in modules.items()}
    with torch.no_grad():
        baseline=model(**probe,use_cache=False).logits
        teacher=[model(**batch,use_cache=False).logits.detach() for batch in batches]
    for parameter in parameters.values():parameter.requires_grad_(True)
    opt=torch.optim.AdamW(parameters.values(),lr=1e-5,weight_decay=.1)
    def project():
        codes=[];scales={};ranges={}
        for name,mod in mlp.items():
            q,scale=quantize(mod.weight);ranges[name]=(len(codes),len(codes)+len(q))
            codes.extend(row.numpy() for row in q);scales[name]=scale
        tau=a.tau_frac*math.sqrt(sum(float(np.square(row.astype(float)).sum()) for row in codes))
        grammar=Grammar(codes,tau,leaders=a.leaders,target=64)
        decoded,info=grammar.run();projected={}
        for name in mlp:
            first,last=ranges[name]
            q=torch.from_numpy(np.stack(decoded[first:last])).float()*scales[name]
            projected[name+'.weight']=q
        return projected,info
    from torch.func import functional_call
    refreshes=[];losses=[];grad_norms=[]
    for step in range(a.steps):
        if step%10==0:
            projected,info=project();offset={name:(q-parameters[name]).detach() for name,q in projected.items()}
            refreshes.append({'step':step,**info})
        effective={name:parameters[name]+delta for name,delta in offset.items()}
        for name,mod in attention.items():
            q,scale=quantize(mod.weight);effective[name+'.weight']=mod.weight+(q*scale-mod.weight).detach()
        batch_idx=step%len(batches)
        logits=functional_call(model,effective,(),{**batches[batch_idx],'use_cache':False}).logits
        loss=(logits-teacher[batch_idx]).square().mean();assert torch.isfinite(loss)
        opt.zero_grad();loss.backward();norm=torch.nn.utils.clip_grad_norm_(parameters.values(),1)
        assert torch.isfinite(norm);opt.step();losses.append(float(loss));grad_norms.append(float(norm))
    deployed,final=project()
    with torch.no_grad():
        for name,q in deployed.items():parameters[name].copy_(q)
        for name,mod in attention.items():
            q,scale=quantize(mod.weight);mod.weight.copy_(q*scale)
    model.requires_grad_(False)
    deployment=validate_deployment(model,tok,probe,baseline,a.export)
    return {'mock':a.mock,'model':'random tiny Qwen3' if a.mock else MODEL,
            'quantized_modules':len(modules),'quantized_parameters':sum(m.weight.numel() for m in modules.values()),
            'shared_grammar_modules':list(mlp),'attention_int8_modules':list(attention),
            'steps':a.steps,'refreshes':refreshes,'final':final,'losses':losses,'gradient_norms':grad_norms,
            'training_objective':'logit MSE distillation smoke test, not original ViT/CIFAR training',
            'tau_interpretation':'tau_frac * original code L2; explicit engineering assumption',
            **deployment,'elapsed_seconds':time.monotonic()-start}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--rows',type=int,default=4)
    ap.add_argument('--steps',type=int,default=11);ap.add_argument('--tau-frac',type=float,default=.15)
    ap.add_argument('--leaders',type=int,default=32);ap.add_argument('--output',default='results.json')
    ap.add_argument('--full-model',action='store_true',help='Whole decoder W8: shared MLP grammar, attention INT8')
    ap.add_argument('--mock',action='store_true',help='Tiny random Qwen3, full decoder with shared ragged grammar')
    ap.add_argument('--export',help='Optional dequantized FP32 HF checkpoint; not compressed grammar bytes')
    ap.add_argument('--memory-budget-gib',type=float,default=8,help='Limit estimated Python grammar memory before allocation')
    a=ap.parse_args()
    if a.export and not (a.full_model or a.mock): ap.error('--export requires --full-model or --mock')
    if not math.isfinite(a.memory_budget_gib) or a.memory_budget_gib <= 0: ap.error('--memory-budget-gib must be finite and positive')
    if a.rows <= 0 or a.steps <= 0 or a.leaders <= 0: ap.error('--rows, --steps and --leaders must be positive')
    if not math.isfinite(a.tau_frac) or a.tau_frac < 0: ap.error('--tau-frac must be finite and nonnegative')
    torch.set_num_threads(4);torch.manual_seed(42)
    result={'tests':tests(),'environment':{'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'device':'cpu','threads':4}}
    if a.self_test:Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
    if a.full_model or a.mock:
        result['end_to_end'] = full_model(a)
        Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
    from transformers import AutoModelForCausalLM,AutoTokenizer
    import transformers
    from huggingface_hub import snapshot_download
    model_path=snapshot_download(MODEL,revision=REVISION,local_files_only=True)
    start=time.time();tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.float32).eval()
    mlp=model.model.layers[0].mlp;captured=[]
    if a.rows > min(mlp.gate_proj.out_features,mlp.up_proj.out_features): ap.error('--rows exceeds module width')
    def hook(module,args):captured.append(args[0].detach().reshape(-1,args[0].shape[-1]).cpu())
    handle=mlp.gate_proj.register_forward_pre_hook(hook)
    def collect(texts):
        captured.clear()
        with torch.no_grad():
            for txt in texts:model(**tok(txt,return_tensors='pt'),use_cache=False)
        return torch.cat(captured)
    x=collect(CALIBRATION);z=collect(TEST);handle.remove()
    original=torch.cat([mlp.gate_proj.weight[:a.rows],mlp.up_proj.weight[:a.rows]]).detach().clone()
    w=torch.nn.Parameter(original.clone());qat=torch.nn.Parameter(original.clone())
    opt=torch.optim.AdamW([w],lr=1e-5,weight_decay=.1);baseopt=torch.optim.AdamW([qat],lr=1e-5,weight_decay=.1)
    target=(x@original.T).detach();train=[];refreshes=[]
    def project(weights):
        codes,scale=quantize(weights);tau=a.tau_frac*float(torch.linalg.norm(codes.double()))
        grammar=Grammar(codes.numpy(),tau,leaders=a.leaders,target=64)
        decoded,info=grammar.run();q=torch.from_numpy(decoded).to(weights.dtype)*scale
        return q,info,codes
    for step in range(a.steps):
        if step%10==0:
            projected,info,_=project(w);offset=(projected-w).detach();refreshes.append({'step':step,**info})
        effective=w+offset;loss=(x@effective.T-target).square().mean()
        opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_([w],1);opt.step()
        codes,scale=quantize(qat);effective_qat=qat+(codes*scale-qat).detach()
        loss_qat=(x@effective_qat.T-target).square().mean()
        baseopt.zero_grad();loss_qat.backward();torch.nn.utils.clip_grad_norm_([qat],1);baseopt.step()
        train.append({'step':step,'weightpe_loss':float(loss),'qat_loss':float(loss_qat)})
    deployed,final,codes=project(w);basecodes,basescale=quantize(qat);base_deployed=basecodes*basescale
    _,baseline_grammar=Grammar(basecodes.numpy(),0,target=64).run()
    denom=torch.linalg.norm(z@original.T)
    result.update({'model':MODEL,'revision':REVISION,'transformers':transformers.__version__,
      'weight_shape':list(w.shape),'modules':['layer0.mlp.gate_proj','layer0.mlp.up_proj'],'rows_per_module':a.rows,
      'calibration_tokens':len(x),'test_tokens':len(z),'calibration_texts':CALIBRATION,'test_texts':TEST,
      'tau_frac':a.tau_frac,'tau_interpretation':'tau_frac * L2 norm of original int8 codes; explicit transplant assumption',
      'leaders':a.leaders,'refresh_interval':10,'training_objective':'layer output MSE, not CIFAR classification',
      'optimizer':f'AdamW lr=1e-5 weight_decay=.1 grad_clip=1, {a.steps} local updates; no 500-step warmup in this small test',
      'training':train,'refreshes':refreshes,'final':final,'baseline_grammar':baseline_grammar,
      'grammar_symbol_ratio':final['symbols']/baseline_grammar['symbols'],
      'test_relative_l2_weightpe':float(torch.linalg.norm(z@(deployed-original).T)/denom),
      'test_relative_l2_qat':float(torch.linalg.norm(z@(base_deployed-original).T)/denom),
      'weight_change_l2':float(torch.linalg.norm(w.detach()-original)), 'elapsed_seconds':time.time()-start,
      'scope':'Real Qwen sliced MLP weights, complete input width. CPU grammar and local STE training, not full-model compression, packed bytes, task accuracy or accelerated kernel.'})
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['refreshes','training','final','baseline_grammar']},indent=2))
if __name__=='__main__':main()
