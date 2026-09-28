#!/usr/bin/env python3
"""OPTQ Eq. 12--15 and lambda Eq. 35 on real Qwen3-0.6B activations.
CPU reference: first 32 output rows of layer-0 gate_proj, all input columns.
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

def optq(w, x, lam, stochastic=False, finite=False, seed=42):
    w = w.double().clone(); x = x.double()
    n = w.shape[1]
    assert lam > 0 and x.shape[1] == n
    h = x.T @ x + lam * torch.eye(n, dtype=x.dtype)
    inv = torch.cholesky_inverse(torch.linalg.cholesky(h))
    # Upper Cholesky of H^-1: U[i,j]/U[i,i] is constrained optimum v_j.
    u = torch.linalg.cholesky(inv, upper=True)
    delta = w.abs().amax(1, keepdim=True).clamp_min(1e-12) / 7
    q = torch.empty_like(w); g = torch.Generator().manual_seed(seed)
    overflow = 0
    for i in range(n):
        z = w[:, i] / delta[:, 0]
        if stochastic:
            lo = z.floor(); rounded = lo + (torch.rand(z.shape, generator=g, dtype=z.dtype) < z-lo)
        else:
            rounded = (z + .5).floor()
        overflow += int((rounded.abs() > 7).sum())
        if finite: rounded = rounded.clamp(-7, 7)
        q[:, i] = rounded * delta[:, 0]
        alpha = q[:, i] - w[:, i]
        w[:, i:] += alpha[:, None] * (u[i, i:] / u[i, i])[None, :]
    return q, {'lambda': lam, 'overflow_before_clamp': overflow,
               'mode': 'finite_signed_W4' if finite else 'infinite_lattice',
               'stochastic': stochastic, 'max_code': float((q/delta).abs().max())}

def tests():
    torch.manual_seed(7); x=torch.randn(9, 5, dtype=torch.float64)
    w=torch.randn(3,5,dtype=torch.float64); lam=.7
    actual,_=optq(w,x,lam); expected=w.clone(); step=w.abs().amax(1)/7
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

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--rows',type=int,default=32)
    ap.add_argument('--output',default='results.json');a=ap.parse_args();torch.set_num_threads(4)
    result={'tests':tests(),'environment':{'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','threads':4}}
    if a.self_test:
        print(json.dumps(result,indent=2));Path(a.output).write_text(json.dumps(result,indent=2)+'\n');return
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import transformers
    from huggingface_hub import snapshot_download
    model_path=snapshot_download(MODEL,revision=REVISION,local_files_only=True)
    start=time.time();tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.float32).eval()
    layer=model.model.layers[0].mlp.gate_proj; captured=[]
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
