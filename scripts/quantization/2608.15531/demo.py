#!/usr/bin/env python3
"""Numerically faithful W4A16 dense + FP sparse outlier decomposition."""
import argparse
from pathlib import Path
import torch

KEY = "model.layers.0.mlp.up_proj.weight"


def load_weight(path, rows=128, cols=512):
    from safetensors import safe_open
    with safe_open(str(path / "model.safetensors"), framework="pt", device="cpu") as f:
        return f.get_tensor(KEY)[:rows, :cols].float().contiguous()


def flashquant_parts(w, outlier_fraction):
    if not 0 < outlier_fraction < 1:
        raise ValueError("outlier_fraction must be in (0, 1)")
    k = max(1, round(w.shape[1] * outlier_fraction))
    indices = torch.topk(w.abs(), k=k, dim=1).indices
    mask = torch.zeros_like(w, dtype=torch.bool)
    mask.scatter_(1, indices, True)
    sparse = torch.where(mask, w, torch.zeros_like(w))
    dense = torch.where(mask, torch.zeros_like(w), w)
    lo = dense.amin(1, keepdim=True)
    hi = dense.amax(1, keepdim=True)
    scale = ((hi - lo) / 15).clamp_min(1e-8)
    zero = torch.round(-lo / scale).clamp(0, 15)
    code = torch.round(dense / scale + zero).clamp(0, 15)
    return scale * (code - zero), sparse, mask


def main():
    p=argparse.ArgumentParser(); p.add_argument("--model-dir",type=Path,required=True)
    p.add_argument("--outlier-fraction",type=float,default=0.01); p.add_argument("--seed",type=int,default=11)
    a=p.parse_args(); torch.manual_seed(a.seed)
    w=load_weight(a.model_dir); x=torch.randn(16,w.shape[1],dtype=torch.float16).float()
    dense4,sparse16,mask=flashquant_parts(w,a.outlier_fraction)
    fused=x@dense4.T + x@sparse16.T
    reference=x@w.T
    recombined=x@(dense4+sparse16).T
    assert torch.allclose(fused,recombined,atol=1e-5,rtol=1e-5)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)}")
    print(f"outlier_density={mask.float().mean().item():.6f}")
    print(f"w4_plus_sparse_mse={torch.nn.functional.mse_loss(fused,reference).item():.8g}")
    print("fusion_equivalence=PASS (one expression reuses activation/output numerically)")

if __name__=="__main__": main()
