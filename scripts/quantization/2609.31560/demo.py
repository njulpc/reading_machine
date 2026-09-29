#!/usr/bin/env python3
"""OPTQ Eq. 12--15 and lambda Eq. 35 on real Qwen3-0.6B activations.
CPU reference: local layer comparison or all decoder Linear weights via --full-model.
Infinite lattice matches theory; finite W4 is explicitly a separate extension.
"""
import argparse, json, math, platform, time
from pathlib import Path
import torch

MODEL = 'Qwen/Qwen3-0.6B'
REVISION = 'c1899de289a04d12100db370d81485cdf75e47ca'
CALIBRATION = ['Explain why calibration data matters for quantization.',
 'A matrix maps a vector into another vector.', 'The library opens every morning.',
 'Write a short function that adds two numbers.', 'A small model can learn from a teacher.',
 'Today we compare rounding error on training and test inputs.']
TEST = ['Describe a clear night with stars.', 'Why does the temperature change?',
 'Translate a simple mathematical statement into words.']

def optq(w, x, lam, stochastic=False, finite=False, seed=42, block_size=128):
    w = w.double().clone(); x = x.double()
    n = w.shape[-1]
    if w.ndim != 2 or x.ndim != 2 or not w.numel() or not x.numel() or x.shape[1] != n:
        raise ValueError('w and x must be nonempty matrices with matching input width')
    if not math.isfinite(lam) or lam <= 0 or block_size <= 0:
        raise ValueError('lambda and block_size must be positive and finite')
    if not torch.isfinite(w).all() or not torch.isfinite(x).all():
        raise ValueError('weights and calibration must be finite')
    h = x.T @ x + lam * torch.eye(n, dtype=x.dtype)
    inv = torch.cholesky_inverse(torch.linalg.cholesky(h))
    # Upper Cholesky of H^-1: U[i,j]/U[i,i] is constrained optimum v_j.
    u = torch.linalg.cholesky(inv, upper=True)
    delta = w.abs().amax(1, keepdim=True).clamp_min(1e-12) / 7
    q = torch.empty_like(w); g = torch.Generator().manual_seed(seed)
    overflow = 0
    # Delay only updates outside each block; algebraically the same tail update.
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        errors = torch.zeros((w.shape[0], end-start), dtype=w.dtype)
        for i in range(start, end):
            z = w[:, i] / delta[:, 0]
            if stochastic:
                lo = z.floor(); rounded = lo + (torch.rand(z.shape, generator=g, dtype=z.dtype) < z-lo)
            else:
                rounded = (z + .5).floor()
            overflow += int((rounded.abs() > 7).sum())
            if finite: rounded = rounded.clamp(-7, 7)
            q[:, i] = rounded * delta[:, 0]
            error = (q[:, i] - w[:, i]) / u[i, i]
            errors[:, i-start] = error
            w[:, i:end] += error[:, None] * u[i, i:end][None, :]
        w[:, end:] += errors @ u[start:end, end:]
    return q, {'lambda': lam, 'overflow_before_clamp': overflow,
               'mode': 'finite_signed_W4' if finite else 'infinite_lattice',
               'stochastic': stochastic, 'max_code': float((q/delta).abs().max())}

def tests():
    torch.manual_seed(7); x=torch.randn(9, 5, dtype=torch.float64)
    w=torch.randn(3,5,dtype=torch.float64); lam=.7
    actual,_=optq(w,x,lam,block_size=2); expected=w.clone(); step=w.abs().amax(1)/7
    h=x.T@x+lam*torch.eye(5,dtype=x.dtype)
    for i in range(5):
        val=(expected[:,i]/step+.5).floor()*step
        alpha=val-expected[:,i]
        if i<4:
            v=-torch.linalg.solve(h[i+1:,i+1:],h[i+1:,i])
            expected[:,i+1:]+=alpha[:,None]*v
        expected[:,i]=val
    err=float((actual-expected).abs().max()); assert err<1e-10
    r=(actual-w).T
    augmented=torch.cat([x,math.sqrt(lam)*torch.eye(5,dtype=x.dtype)])
    identity=float(((augmented@r).square().sum()-((x@r).square().sum()+lam*r.square().sum())).abs())
    assert identity<1e-10
    finite,_=optq(w,x,lam,finite=True);assert (finite.abs()<=w.abs().amax(1,keepdim=True)+1e-12).all()
    g=torch.Generator().manual_seed(5);z=torch.tensor([-.7,.2,1.9],dtype=torch.float64)
    q=z.floor()+(torch.rand((50000,3),generator=g,dtype=z.dtype)<z-z.floor())
    unbiased=float((q.mean(0)-z).abs().max());assert unbiased<.012
    return {'tail_solve_max_error':err,'augmented_error_identity':identity,
            'stochastic_rounding_mean_error_50000':unbiased,'finite_range':'PASS'}

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
    model,tok,batches,probe=load_model_inputs(a.mock);model.requires_grad_(False)
    targets={name:mod for name,mod in model.named_modules() if isinstance(mod,torch.nn.Linear) and name.startswith('model.layers.')}
    captured={name:[] for name in targets};handles=[]
    def hook(name):
        def collect(module,args):
            captured[name].append(args[0].detach().reshape(-1,module.in_features).cpu())
        return collect
    for name,mod in targets.items():handles.append(mod.register_forward_pre_hook(hook(name)))
    with torch.no_grad():
        for batch in batches:model(**batch,use_cache=False)
    for handle in handles:handle.remove()
    with torch.no_grad():baseline=model(**probe,use_cache=False).logits
    records=[]
    for name,mod in targets.items():
        x=torch.cat(captured.pop(name)).double();m,n=x.shape
        energy=float(x.square().sum());lam=energy/(m**(1/3)*min(m,n)**(2/3))
        # Zero-energy calibration provides no geometry: positive floor is an explicit engineering fallback.
        lam=max(lam,1e-12)
        q,info=optq(mod.weight.detach(),x,lam,finite=True)
        scale=mod.weight.detach().double().abs().amax(1,keepdim=True).clamp_min(1e-12)/7
        assert torch.isfinite(q).all() and (q.abs()<=scale*7+1e-10).all()
        with torch.no_grad():mod.weight.copy_(q.to(mod.weight.dtype))
        records.append({'module':name,'weights':mod.weight.numel(),'calibration_tokens':m,**info})
        print('quantized',name,flush=True)
    deployment=validate_deployment(model,tok,probe,baseline,a.export)
    return {'mock':a.mock,'model':'random tiny Qwen3' if a.mock else MODEL,'revision':None if a.mock else REVISION,
            'quantized_modules':len(records),'quantized_parameters':sum(r['weights'] for r in records),
            'method':'Eq35 beta1, full input width per output row, deterministic finite W4 extension, FP32 activations',
            'calibration':'Pre-quantization model activations; no act-order, grouping, outlier or mixed-precision policy',
            'modules':records,**deployment,'elapsed_seconds':time.monotonic()-start}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--rows',type=int,default=32)
    ap.add_argument('--output',default='results.json')
    ap.add_argument('--full-model',action='store_true',help='All decoder Linear weights, finite W4 CPU reference')
    ap.add_argument('--mock',action='store_true',help='Tiny randomly initialized Qwen3 full-model test')
    ap.add_argument('--export',help='Optional dequantized FP32 HF checkpoint directory; not a packed W4 artifact')
    a=ap.parse_args()
    if a.export and not (a.full_model or a.mock): ap.error('--export requires --full-model or --mock')
    if a.rows <= 0: ap.error('--rows must be positive')
    torch.set_num_threads(4)
    result={'tests':tests(),'environment':{'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','threads':4}}
    if a.self_test:
        print(json.dumps(result,indent=2));Path(a.output).write_text(json.dumps(result,indent=2)+'\n');return
    if a.full_model or a.mock:
        result['end_to_end'] = full_model(a)
        Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import transformers
    from huggingface_hub import snapshot_download
    model_path=snapshot_download(MODEL,revision=REVISION,local_files_only=True)
    start=time.time();tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.float32).eval()
    layer=model.model.layers[0].mlp.gate_proj; captured=[]
    if a.rows > layer.out_features: ap.error('--rows exceeds the selected module width')
    def hook(module,args):captured.append(args[0].detach().reshape(-1,args[0].shape[-1]).cpu())
    handle=layer.register_forward_pre_hook(hook)
    def collect(texts):
        captured.clear()
        with torch.no_grad():
            for txt in texts:model(**tok(txt,return_tensors='pt'),use_cache=False)
        return torch.cat(captured).double()
    x=collect(CALIBRATION);z=collect(TEST);handle.remove();w=layer.weight[:a.rows].detach().double()
    metrics=[]
    for m in sorted(set([min(16,len(x)),len(x)])):
        xx=x[:m];n=xx.shape[1];energy=float(xx.square().sum())
        configs=[('legacy_0.01',.01*energy/n),('eq35_beta1',energy/(m**(1/3)*min(m,n)**(2/3)))]
        for name,lam in configs:
            for stochastic,finite in [(False,False),(True,False),(False,True)]:
                q,info=optq(w,xx,lam,stochastic,finite)
                info.update({'rule':name,'m':m,'train_relative_l2':float(torch.linalg.norm(xx@(q-w).T)/torch.linalg.norm(xx@w.T)),
                    'test_relative_l2':float(torch.linalg.norm(z@(q-w).T)/torch.linalg.norm(z@w.T))})
                metrics.append(info)
    result.update({'model':MODEL,'revision':REVISION,'transformers':transformers.__version__,
      'weight_shape':list(w.shape),'calibration_tokens':len(x),'test_tokens':len(z),
      'calibration_texts':CALIBRATION,'test_texts':TEST,'results':metrics,'elapsed_seconds':time.time()-start,
      'scope':'Real Qwen layer subset; no whole-model W4 checkpoint, perplexity, native INT4 kernel, or speedup claim.'})
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
