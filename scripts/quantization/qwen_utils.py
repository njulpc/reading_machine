#!/usr/bin/env python3
"""Shared real-weight utilities for the 2026-09-02 Qwen3-0.6B reproductions."""
from __future__ import annotations

import json
import math
from pathlib import Path

import torch
from safetensors import safe_open

MODEL = Path("/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors")


def tensor(name="model.layers.0.self_attn.q_proj.weight"):
    if not MODEL.exists():
        raise FileNotFoundError(f"Qwen3-0.6B checkpoint not found: {MODEL}")
    with safe_open(str(MODEL), framework="pt", device="cpu") as f:
        return f.get_tensor(name).float()


def qsym(x, bits, dim=-1, eps=1e-8):
    qmax = 2 ** (bits - 1) - 1
    scale = x.abs().amax(dim=dim, keepdim=True).clamp_min(eps) / qmax
    code = (x / scale).round().clamp(-qmax, qmax)
    return code * scale, code, scale


def metrics(ref, approx):
    ref = ref.float().reshape(-1)
    approx = approx.float().reshape(-1)
    mse = torch.mean((ref - approx) ** 2).item()
    cosine = torch.nn.functional.cosine_similarity(ref, approx, dim=0).item()
    rel = torch.linalg.vector_norm(ref - approx).item() / max(torch.linalg.vector_norm(ref).item(), 1e-12)
    return {"mse": mse, "cosine": cosine, "relative_l2": rel}


def fwht(x):
    n = x.shape[-1]
    if n & (n - 1):
        raise ValueError("FWHT dimension must be a power of two")
    y = x.clone()
    h = 1
    while h < n:
        y = y.reshape(*y.shape[:-1], -1, h * 2)
        a, b = y[..., :h].clone(), y[..., h:].clone()
        y[..., :h], y[..., h:] = a + b, a - b
        y = y.reshape(*x.shape)
        h *= 2
    return y / math.sqrt(n)


def run_qat():
    w = tensor()[:256, :256]
    qmax = 7
    log_scale = torch.tensor(math.log(w.abs().max().item() / qmax), requires_grad=True)
    opt = torch.optim.Adam([log_scale], lr=0.08)
    losses = []
    for _ in range(20):
        scale = log_scale.exp()
        raw = w / scale
        code = raw + (raw.round() - raw).detach()
        dq = code.clamp(-qmax, qmax) * scale
        loss = torch.mean((dq - w) ** 2)
        opt.zero_grad(); loss.backward(); opt.step()
        losses.append(loss.item())
    return {"algorithm": "target-centric symmetric W4 QAT/STE", "bits": 4, "granularity": "tensor slice", "steps": 20, "initial_mse": losses[0], "final_mse": losses[-1], "scale": log_scale.exp().item()}


def run_masq():
    x = tensor()[:192, :128].reshape(24, 8, 128).mean(1)
    mask = torch.ones_like(x); mask[:, ::4] = 0
    masked = x * mask
    codebook = masked[torch.linspace(0, len(masked)-1, 8).long()].clone()
    for _ in range(8):
        dist = torch.cdist(masked, codebook)
        ids = dist.argmin(1)
        for k in range(len(codebook)):
            if (ids == k).any(): codebook[k] = masked[ids == k].mean(0)
    recon = codebook[torch.cdist(masked, codebook).argmin(1)]
    visible_mse = (((recon-x)*mask)**2).sum().item()/mask.sum().item()
    switches = (torch.cdist(masked, codebook).argmin(1)[1:] != torch.cdist(masked, codebook).argmin(1)[:-1]).float().mean().item()
    return {"algorithm": "mask-aware spatiotemporal vector quantization", "codebook_size": 8, "masked_feature_fraction": 0.25, "visible_mse": visible_mse, "code_switch_rate": switches}


def run_adaptive_uint8():
    w = tensor()[:512, :512]
    torch.manual_seed(7); x = torch.randn(16, 512)
    y = x @ w.T
    score = x.abs().mean(1)
    threshold = score.quantile(0.75).item()
    activate = score > threshold
    qw, _, _ = qsym(w, 8, dim=1)
    qy = x @ qw.T
    gated = torch.where(activate[:, None], qy, y)
    return {"algorithm": "input-adaptive UINT8 front-end gating", "weight_granularity": "per-output-channel", "gate_threshold_q75": threshold, "gate_rate": activate.float().mean().item(), **metrics(y, gated)}


def run_pipeline():
    w = tensor()[:512, :512]
    threshold = w.abs().quantile(0.20)
    pruned = w.masked_fill(w.abs() < threshold, 0)
    qw, _, _ = qsym(pruned, 8, dim=1)
    torch.manual_seed(11); h = torch.randn(64, 512)
    kv = h @ w.T; qkv, _, _ = qsym(kv, 8, dim=1)
    storage_bits = (w.numel() * 0.8 * 8) + kv.numel() * 8
    baseline_bits = (w.numel() + kv.numel()) * 16
    return {"algorithm": "pruning + W8 + KV8 coupled pipeline", "prune_fraction": (pruned==0).float().mean().item(), "estimated_compression": baseline_bits/storage_bits, "weight": metrics(w,qw), "kv": metrics(kv,qkv)}


def run_nvfp4():
    w = tensor()[:512, :512]
    flat = w.reshape(-1, 16)
    codebook = torch.tensor([-6,-4,-3,-2,-1.5,-1,-.5,0,.5,1,1.5,2,3,4,6], dtype=w.dtype)
    scale = flat.abs().amax(1, keepdim=True).clamp_min(1e-8) / 6
    normalized = flat/scale
    idx = (normalized[...,None]-codebook).abs().argmin(-1)
    dq = codebook[idx]*scale
    outlier = flat.abs() > (5.5*scale)
    guarded = torch.where(outlier, flat, dq).reshape_as(w)
    return {"algorithm":"NVFP4 group-16 with outlier guard", "group_size":16, "outlier_rate":outlier.float().mean().item(), **metrics(w,guarded)}


def run_rslm():
    w = tensor()[:256, :256]
    rotated = fwht(w)
    centers = torch.quantile(rotated.reshape(-1), torch.tensor([.125,.375,.625,.875]))
    for _ in range(12):
        ids=(rotated[...,None]-centers).abs().argmin(-1)
        for k in range(4):
            if (ids==k).any(): centers[k]=rotated[ids==k].mean()
    recon_rot=centers[(rotated[...,None]-centers).abs().argmin(-1)]
    recon=fwht(recon_rot)
    norm_scale=w.norm(dim=1,keepdim=True)/recon.norm(dim=1,keepdim=True).clamp_min(1e-8)
    recon=recon*norm_scale
    return {"algorithm":"RSLM-style FWHT + 2-bit Lloyd-Max + final norm correction", "bits":2, "centers":[round(x,7) for x in centers.tolist()], **metrics(w,recon)}


def run_topgq():
    w=tensor()[:512,:512]
    proxy=torch.nn.functional.normalize(w,dim=1)[:,:32].mean(1)
    bins=torch.bucketize(proxy, torch.quantile(proxy,torch.tensor([.25,.5,.75])))
    dq=torch.empty_like(w); scales=[]
    for g in range(4):
        part=w[bins==g]; scale=part.abs().max().clamp_min(1e-8)/127; scales.append(scale.item()); dq[bins==g]=(part/scale).round().clamp(-127,127)*scale
    return {"algorithm":"TopGQ topology-proxy grouped INT8", "groups":4, "scales":scales, **metrics(w,dq)}


def run_sparse_quant():
    w=tensor()[:512,:512]; torch.manual_seed(13); x=torch.randn(64,512); y=x@w.T
    delta=y.abs().quantile(.40); sparse=y.masked_fill(y.abs()<delta,0); dq,_,_=qsym(sparse,4,dim=1)
    return {"algorithm":"trainable-threshold proxy + INT4 event-driven activations", "threshold_quantile":.40, "activation_sparsity":(sparse==0).float().mean().item(), "effective_op_reduction":y.numel()/max((sparse!=0).sum().item(),1), **metrics(y,dq)}


def run_qstrata():
    names=[f"model.layers.{i}.self_attn.q_proj.weight" for i in range(0,28,4)]
    ws=[tensor(n)[:128,:256] for n in names]
    choices={}
    for i,w in enumerate(ws):
        choices[i]={b:metrics(w,qsym(w,b,dim=1)[0])["mse"] for b in (2,3,4)}
    budget=20; dp={(0,0):(0.0,[])}
    for i in range(len(ws)):
        nd={}
        for (_,used),(loss,path) in dp.items():
            for b in (2,3,4):
                if used+b<=budget:
                    key=(i+1,used+b); cand=(loss+choices[i][b],path+[b])
                    if key not in nd or cand[0]<nd[key][0]: nd[key]=cand
        dp=nd
    loss,path=dp[(len(ws),budget)]
    return {"algorithm":"Q-Strata-style hierarchical model-budget allocation", "layers":len(ws), "average_bits":budget/len(ws), "allocated_bits":path, "summed_reconstruction_mse":loss}


def run_gradcodes():
    w=tensor()[:128,:256]; scale=w.abs().amax(1,keepdim=True)/7; codes=(w/scale).round().clamp(-7,7)
    target=w+0.05*torch.sin(torch.arange(w.numel()).reshape_as(w))
    initial=((codes*scale-target)**2).mean().item()
    for _ in range(12):
        current = codes * scale
        direction = torch.sign(target - current)
        proposal = (codes + direction).clamp(-7, 7)
        improve = (proposal * scale - target).abs() < (current - target).abs()
        codes = torch.where(improve, proposal, codes)
    final=((codes*scale-target)**2).mean().item()
    return {"algorithm":"4-bit code-surrogate gradient with guided integer projection", "steps":12, "initial_target_mse":initial, "final_target_mse":final, "changed_code_fraction":((codes-(w/scale).round().clamp(-7,7))!=0).float().mean().item()}


def run_kvquant():
    torch.manual_seed(17); h=torch.randn(32,1024)
    q=h@tensor("model.layers.0.self_attn.q_proj.weight").T; k=h@tensor("model.layers.0.self_attn.k_proj.weight").T; v=h@tensor("model.layers.0.self_attn.v_proj.weight").T
    q=q[:,:1024]; scores=q@k.T/math.sqrt(1024); attn=scores.softmax(-1); out=attn@v
    res={}
    for b in (8,4):
        qk=qsym(k,b,dim=1)[0]; qv=qsym(v,b,dim=1)[0]; qa=(q@qk.T/math.sqrt(1024)).softmax(-1); qo=qa@qv
        res[str(b)]={**metrics(out,qo),"top_evidence_flip_rate":(attn.argmax(-1)!=qa.argmax(-1)).float().mean().item()}
    return {"algorithm":"offline per-token KV-cache INT8/INT4 audit", "sequence":32, "head_width_proxy":1024, "results":res}


def run_stress():
    w=tensor()[:512,:512]; rows=torch.arange(len(w))%4; result={}
    for b in (8,4):
        dq=qsym(w,b,dim=1)[0]; result[str(b)]={"overall":metrics(w,dq),"subgroup_mse":[torch.mean((w[rows==g]-dq[rows==g])**2).item() for g in range(4)]}
    return {"algorithm":"responsible-AI quantization stress test", "conditions":["BF16 proxy","INT8","INT4"], "results":result}


RUNNERS={
    "2608.29667":run_qat, "2608.29891":run_masq, "2608.30034":run_adaptive_uint8,
    "2608.30076":run_pipeline, "2608.30181":run_nvfp4, "2608.30384":run_rslm,
    "2608.30394":run_topgq, "2608.30439":run_sparse_quant, "2608.30564":run_qstrata,
    "2608.30908":run_gradcodes, "2608.30996":run_kvquant, "2608.31108":run_stress,
}


def run(paper_id):
    torch.manual_seed(20260902)
    result={"paper_id":paper_id,"model":"Qwen3-0.6B","checkpoint":str(MODEL),**RUNNERS[paper_id]()}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result
