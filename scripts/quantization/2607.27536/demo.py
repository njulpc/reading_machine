#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.27536 - GyRot
Core Methods: CoRFiG, HAP, Zero-Rounded Asymmetric Quantization
================================================================================

Usage:
    python3 demo.py --synthetic        # Synthetic weights validation
    python3 demo.py --model MODEL      # Real model quantization
================================================================================
"""

import argparse, math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

def get_hadamard(n: int, device="cpu"):
    if n & (n - 1) != 0:
        raise ValueError(f"Hadamard size must be power of 2, got {n}")
    H = torch.tensor([[1.]], device=device, dtype=torch.float32)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], dim=1), torch.cat([H, -H], dim=1)], dim=0)
    return H / math.sqrt(n)

class CoRFIGQuantizer:
    """CoRFiG: Coarse Rotation, Fine Grouping Quantizer."""
    def __init__(self, n_bits=4, group_size=128, coarse_block_size=None, symmetric=False):
        self.n_bits = n_bits
        self.group_size = group_size
        self.coarse_block_size = coarse_block_size or group_size * 4
        self.symmetric = symmetric
        self.qmax = 2 ** n_bits - 1
    
    def quantize(self, weight: torch.Tensor) -> Tuple[torch.Tensor, dict]:
        w = weight.float()
        orig_shape = w.shape
        w_2d = w.reshape(-1, w.shape[-1]) if w.dim() > 2 else w
        out_f, in_f = w_2d.shape
        
        # Coarse rotation
        H_coarse = None
        pad_in = in_f
        if self.coarse_block_size > 0 and in_f >= self.coarse_block_size:
            pad_in = 1
            while pad_in < in_f:
                pad_in *= 2
            H_coarse = get_hadamard(pad_in, device=w.device)
            w_padded = F.pad(w_2d, (0, pad_in - in_f)) if pad_in > in_f else w_2d
            w_rot = (w_padded @ H_coarse.T)[:, :in_f]
        else:
            w_rot = w_2d
        
        # Fine grouping
        w_flat = w_rot.reshape(-1)
        n = w_flat.numel()
        pad_len = (self.group_size - n % self.group_size) % self.group_size
        if pad_len > 0:
            w_flat = F.pad(w_flat, (0, pad_len))
        n_groups = w_flat.numel() // self.group_size
        w_groups = w_flat.reshape(n_groups, self.group_size)
        
        # HAP: sort within groups
        w_sorted, perm_indices = torch.sort(w_groups, dim=1)
        
        # Asymmetric quantization with zero rounding
        wmin = w_sorted.amin(dim=1, keepdim=True)
        wmax = w_sorted.amax(dim=1, keepdim=True)
        scales = ((wmax - wmin) / self.qmax).clamp_min(1e-8)
        zps_raw = -wmin / scales
        zps = torch.round(zps_raw).clamp(0, self.qmax)
        w_q = torch.round(w_sorted / scales + zps).clamp(0, self.qmax)
        w_dq = (w_q - zps) * scales
        
        # Inverse HAP
        w_restored = torch.zeros_like(w_dq)
        for i in range(n_groups):
            w_restored[i] = w_dq[i][torch.argsort(perm_indices[i])]
        
        if pad_len > 0:
            w_restored = w_restored.reshape(-1)[:-pad_len]
        else:
            w_restored = w_restored.reshape(-1)
        w_restored = w_restored[:n].reshape(out_f, in_f)
        w_final = w_restored.reshape(orig_shape)
        
        return w_final, {'scales': scales, 'zps': zps, 'H_coarse': H_coarse, 'pad_in': pad_in, 'orig_in_f': in_f}
    
    def inference(self, x: torch.Tensor, w_q: torch.Tensor, meta: dict) -> torch.Tensor:
        """Inference with rotation: quantized weights live in rotated space,
        so input must be rotated too for correct matmul."""
        H = meta.get('H_coarse')
        if H is None:
            return F.linear(x, w_q)
        pad_in = meta['pad_in']
        orig_in = meta['orig_in_f']
        x_pad = F.pad(x, (0, pad_in - x.shape[-1])) if x.shape[-1] < pad_in else x
        x_rot = x_pad @ H.T
        if pad_in > orig_in:
            x_rot = x_rot[..., :orig_in]
        return F.linear(x_rot, w_q)

class IntegerDequantizer:
    @staticmethod
    def dequantize(x_q, z_r, scale_int, shift=8):
        diff = x_q - z_r
        return (diff.float() * scale_int.float()) / (2 ** shift)

class GyRotLinear(nn.Module):
    """Linear wrapper for weights quantized in GyRot's rotated space.

    The quantizer right-multiplies weights by a Hadamard rotation. A standard
    Linear forward is therefore incorrect after replacement; this wrapper applies
    the same rotation to activations before the matmul.
    """
    def __init__(self, linear: nn.Linear, w_q: torch.Tensor, meta: dict):
        super().__init__()
        self.in_features = linear.in_features
        self.out_features = linear.out_features
        self.register_buffer("weight", w_q.detach().to(dtype=linear.weight.dtype), persistent=True)
        if linear.bias is None:
            self.register_buffer("bias", None, persistent=True)
        else:
            self.register_buffer("bias", linear.bias.detach().clone(), persistent=True)
        H = meta.get("H_coarse")
        if H is None:
            self.register_buffer("H_coarse", None, persistent=True)
        else:
            self.register_buffer("H_coarse", H.detach().float(), persistent=True)
        self.pad_in = int(meta.get("pad_in", linear.in_features))
        self.orig_in_f = int(meta.get("orig_in_f", linear.in_features))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.H_coarse is None:
            return F.linear(x, self.weight, self.bias)
        if x.shape[-1] != self.orig_in_f:
            raise ValueError(f"Expected last dim {self.orig_in_f}, got {x.shape[-1]}")
        x_pad = F.pad(x, (0, self.pad_in - x.shape[-1])) if x.shape[-1] < self.pad_in else x
        x_rot = x_pad.float() @ self.H_coarse.to(device=x.device).T
        if self.pad_in > self.orig_in_f:
            x_rot = x_rot[..., :self.orig_in_f]
        return F.linear(x_rot.to(dtype=self.weight.dtype), self.weight, self.bias)

def demo_synthetic():
    print("=" * 70)
    print(" GyRot Demo - Synthetic Weight Validation")
    print("=" * 70)
    
    out_f, in_f = 2816, 1024
    torch.manual_seed(42)
    w = torch.randn(out_f, in_f)
    w[torch.rand(out_f, in_f) < 0.001] *= 10.0
    x = torch.randn(4, 128, in_f)
    y_ref = F.linear(x, w)
    
    print(f"\nWeight: {w.shape}, stats: mean={w.mean():.3f}, std={w.std():.3f}, max={w.max():.2f}")
    
    # Baseline
    print("\n--- Baseline: Direct Group Quantization (no rotation) ---")
    base = CoRFIGQuantizer(n_bits=4, group_size=128, coarse_block_size=0, symmetric=False)
    w_b, _ = base.quantize(w)
    y_b = F.linear(x, w_b)
    mse_b = ((y_ref - y_b) ** 2).mean().item()
    print(f"  output MSE: {mse_b:.4f}")
    
    # GyRot
    print("\n--- GyRot: CoRFiG (rotation + grouping) ---")
    gyrot = CoRFIGQuantizer(n_bits=4, group_size=128, coarse_block_size=512, symmetric=False)
    w_g, meta = gyrot.quantize(w)
    y_g = gyrot.inference(x, w_g, meta)
    mse_g = ((y_ref - y_g) ** 2).mean().item()
    print(f"  output MSE: {mse_g:.4f}")
    
    print(f"\n--- Improvement: {mse_b / (mse_g + 1e-10):.2f}x ---")
    
    # Integer dequantization demo
    print("\n--- Integer-Only Dequantization Demo ---")
    deq = IntegerDequantizer.dequantize(
        torch.tensor([0, 4, 8, 12, 15], dtype=torch.int32),
        torch.tensor(8, dtype=torch.int32),
        torch.tensor(51, dtype=torch.int32), 8
    )
    print(f"  Dequantized values: {deq.tolist()}")
    
    print("\n" + "=" * 70)

def _replace_submodule(root: nn.Module, dotted_name: str, new_module: nn.Module):
    parent_name, _, child_name = dotted_name.rpartition(".")
    parent = root.get_submodule(parent_name) if parent_name else root
    setattr(parent, child_name, new_module)

def demo_real_model(model_name="Qwen/Qwen3-0.6B", max_layers=0):
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        print("pip install transformers")
        return
    
    print(f"Loading {model_name}...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True
        )
    except Exception as e:
        print(f"Failed to load model: {e}")
        print("Falling back to synthetic validation. Run with --synthetic flag.")
        return
    
    gyrot = CoRFIGQuantizer(n_bits=4, group_size=128, coarse_block_size=512)
    quantized = 0
    targets = [(name, m) for name, m in model.named_modules()
               if isinstance(m, torch.nn.Linear) and 'q_proj' in name]
    for name, m in targets:
        if max_layers > 0 and quantized >= max_layers:
            break
        with torch.no_grad():
            w_q, meta = gyrot.quantize(m.weight.data)
        _replace_submodule(model, name, GyRotLinear(m, w_q, meta).to(device=m.weight.device))
        quantized += 1
        print(f"  Quantized and wrapped {name}: {tuple(m.weight.shape)}")
    if quantized == 0:
        raise RuntimeError("No q_proj Linear layers were found to quantize.")
    print(f"Quantized {quantized} q_proj layers with GyRotLinear wrappers.")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    inputs = tokenizer("The future of AI is", return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=20, do_sample=False)
    print(f"Generated: {tokenizer.decode(out[0], skip_special_tokens=True)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-0.6B")
    parser.add_argument("--max-layers", type=int, default=0,
                        help="Limit q_proj layers for real-model validation; 0 means all.")
    args = parser.parse_args()
    demo_synthetic() if args.synthetic else demo_real_model(args.model, args.max_layers)

if __name__ == "__main__":
    main()
