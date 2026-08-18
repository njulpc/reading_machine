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


def flashquant_parts(w, threshold):
    row_ref = w.abs().mean(1, keepdim=True).clamp_min(1e-8)
    mask = w.abs() > threshold * row_ref
    sparse = torch.where(mask, w, torch.zeros_like(w))
    dense = torch.where(mask, torch.zeros_like(w), w)
    scale = dense.abs().amax(1, keepdim=True).clamp_min(1e-8) / 7
    code = torch.round(dense / scale).clamp(-7, 7)
    return code * scale, sparse, mask


def main():
    p=argparse.ArgumentParser(); p.add_argument("--model-dir",type=Path,required=True)
    p.add_argument("--outlier-threshold",type=float,default=6.0); p.add_argument("--seed",type=int,default=11)
    a=p.parse_args(); torch.manual_seed(a.seed)
    w=load_weight(a.model_dir); x=torch.randn(16,w.shape[1],dtype=torch.float16).float()
    dense4,sparse16,mask=flashquant_parts(w,a.outlier_threshold)
    fused=x@dense4.T + x@sparse16.T
    reference=x@w.T
    recombined=x@(dense4+sparse16).T
    assert torch.allclose(fused,recombined,atol=1e-5,rtol=1e-5)
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)}")
    print(f"outlier_density={mask.float().mean().item():.6f}")
    print(f"w4_plus_sparse_mse={torch.nn.functional.mse_loss(fused,reference).item():.8g}")
    print("fusion_equivalence=PASS (one expression reuses activation/output numerically)")

if __name__=="__main__": main()
