#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.08910 - Tied Trit-Planes
Title: Constraining PTQTP to a Uniform Nine-Level Quantizer
Core Method: TTP (Tied Trit-Planes) Quantization
Target Model: Qwen3-0.6B
================================================================================

This script demonstrates:
1. Original PTQTP (dual free-scale trit-planes)
2. Tied Trit-Planes (fixed ratio 3:1, uniform 9-level)
3. Storage comparison
4. Application to Qwen3-0.6B linear layers

Usage:
    python3 demo.py

Requirements:
    pip install torch numpy
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple


# =============================================================================
# 1. Trit Quantizer (3-level: -1, 0, +1)
# =============================================================================

class TritQuantizer:
    """
    Ternary quantization: values in {-1, 0, +1}.
    Uses 1.58 bits per element (log2(3)).
    """
    
    def __init__(self, block_size: int = 128):
        self.block_size = block_size
    
    def quantize(self, x: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        """
        Quantize x to trits with given scale.
        
        Args:
            x: input tensor
            scale: per-block scale (can be scalar for demo)
        
        Returns:
            quantized tensor (as float for demo)
        """
        q = torch.round(x / scale).clamp(-1, 1)
        return q * scale
    
    def find_scale(self, x: torch.Tensor) -> torch.Tensor:
        """Find optimal per-block scale for trit quantization."""
        # For simplicity, use max-based scaling
        block_max = x.abs().amax(dim=-1, keepdim=True).clamp_min(1e-8)
        return block_max


# =============================================================================
# 2. PTQTP: Original Dual-Scale Trit-Planes
# =============================================================================

class PTQTPQuantizer:
    """
    PTQTP: Post-Training Quantization with Ternary Planes.
    
    Decomposes weight into two trit-planes with independent per-group scales:
        W_eff = s1 * T1 + s2 * T2
    where T1, T2 in {-1, 0, +1}.
    
    Storage per element:
        - T1: ~1.58 bits (trit)
        - T2: ~1.58 bits (trit)
        - s1: 32-bit float per group
        - s2: 32-bit float per group
    """
    
    def __init__(self, block_size: int = 128, group_size: int = 128):
        self.block_size = block_size
        self.group_size = group_size
        self.trit = TritQuantizer(block_size)
    
    def quantize(self, weight: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Quantize weight using PTQTP.
        
        Returns:
            W_eff: effective quantized weight
            s1, s2: scales for two planes
        """
        # For demo: use simple decomposition
        # In practice, PTQTP optimizes T1, T2, s1, s2 jointly
        
        # Split weight into two components
        w1 = weight.clone()
        w2 = torch.zeros_like(weight)
        
        # Find scales independently
        s1 = self.trit.find_scale(w1)
        s2 = self.trit.find_scale(w1) * 0.5  # Different scale
        
        # Quantize each plane
        t1 = torch.round(w1 / s1).clamp(-1, 1)
        # Second plane captures residual
        residual = w1 - t1 * s1
        t2 = torch.round(residual / s2).clamp(-1, 1)
        
        # Effective weight
        w_eff = t1 * s1 + t2 * s2
        
        return w_eff, s1, s2
    
    def storage_bits(self, num_elements: int, num_groups: int) -> float:
        """Calculate storage requirement in bits."""
        trit_bits = num_elements * math.log2(3) * 2  # two trit-planes
        scale_bits = num_groups * 32 * 2  # two scales per group
        return trit_bits + scale_bits


# =============================================================================
# 3. TTP: Tied Trit-Planes (fixed ratio 3:1)
# =============================================================================

class TTPQuantizer:
    """
    Tied Trit-Planes: PTQTP with fixed scale ratio s2/s1 = 3.
    
    This collapses the representation to a uniform nine-level quantizer:
        Effective values: s1 * {-4, -3, -2, -1, 0, +1, +2, +3, +4}
    
    Storage per element:
        - T1: ~1.58 bits (trit)
        - T2: ~1.58 bits (trit)
        - s1: 32-bit float per group (only ONE scale!)
    """
    
    def __init__(self, block_size: int = 128, group_size: int = 128):
        self.block_size = block_size
        self.group_size = group_size
        self.trit = TritQuantizer(block_size)
        self.ratio = 3.0  # Fixed ratio: s2 = 3 * s1
    
    def quantize(self, weight: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight using Tied Trit-Planes.
        
        Returns:
            W_eff: effective quantized weight
            s1: single scale (s2 = 3 * s1 implicitly)
        """
        # Find single scale s1
        # The effective range needs to cover weight's range
        # With ratio=3, max effective value is s1 * (1 + 3) = 4 * s1
        # So s1 = max(|W|) / 4
        w_max = weight.abs().max()
        s1 = (w_max / 4.0).clamp_min(1e-8)
        s2 = self.ratio * s1
        
        # Quantize to two trit-planes with tied scales
        # Search for best T1, T2 combination
        best_err = float('inf')
        best_w = None
        
        # For demo: simple greedy assignment
        # Try each possible combination and pick closest
        levels = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        
        # Vectorized assignment
        w_scaled = weight / s1
        
        # Find nearest level for each element
        levels_t = torch.tensor(levels, dtype=weight.dtype, device=weight.device)
        w_expanded = w_scaled.unsqueeze(-1)  # [..., 1]
        levels_expanded = levels_t.view(1, -1)  # [1, 9]
        
        distances = (w_expanded - levels_expanded).abs()
        best_idx = distances.argmin(dim=-1)
        
        # Map back to two trit-planes
        # level = t1 + 3 * t2, where t1, t2 in {-1, 0, +1}
        # 4 = 1 + 3*1,  3 = 0 + 3*1,  2 = -1 + 3*1
        # 1 = 1 + 3*0,  0 = 0 + 3*0, -1 = -1 + 3*0
        # -2 = 1 + 3*(-1), -3 = 0 + 3*(-1), -4 = -1 + 3*(-1)
        
        level_to_trits = {
            4: (1, 1), 3: (0, 1), 2: (-1, 1),
            1: (1, 0), 0: (0, 0), -1: (-1, 0),
            -2: (1, -1), -3: (0, -1), -4: (-1, -1)
        }
        
        best_levels = levels_t[best_idx]
        w_eff = best_levels * s1
        
        return w_eff, s1
    
    def storage_bits(self, num_elements: int, num_groups: int) -> float:
        """Calculate storage requirement in bits."""
        trit_bits = num_elements * math.log2(3) * 2  # two trit-planes
        scale_bits = num_groups * 32 * 1  # only ONE scale per group
        return trit_bits + scale_bits
    
    def get_nine_level_grid(self, s1: torch.Tensor) -> torch.Tensor:
        """Return the uniform nine-level grid for given scale."""
        levels = torch.tensor([-4, -3, -2, -1, 0, 1, 2, 3, 4], 
                              dtype=s1.dtype, device=s1.device)
        return levels * s1


# =============================================================================
# 4. Qwen3-0.6B Linear Layer Quantization
# =============================================================================

class QuantizedLinear(nn.Module):
    """Linear layer with TTP quantization."""
    
    def __init__(self, in_features: int, out_features: int, 
                 quantizer: TTPQuantizer):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.quantizer = quantizer
        
        # Original weight (will be quantized)
        self.register_buffer('weight', torch.randn(out_features, in_features))
        self.register_buffer('quantized_weight', torch.zeros_like(self.weight))
        self.register_buffer('scale', torch.tensor(1.0))
        self.quantized = False
    
    def quantize_weights(self):
        """Apply TTP quantization to weights."""
        w_q, s = self.quantizer.quantize(self.weight)
        self.quantized_weight = w_q
        self.scale = s
        self.quantized = True
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.quantized:
            return F.linear(x, self.quantized_weight)
        else:
            return F.linear(x, self.weight)


# =============================================================================
# 5. Demonstration
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2608.08910 - Tied Trit-Planes")
    print(" Target: Qwen3-0.6B Linear Layers")
    print("=" * 70)
    
    # Create sample weight matrix (Qwen3-0.6B scale)
    print("\n[1] Creating sample weight matrix")
    in_f, out_f = 1024, 2816  # Qwen FFN dimensions
    W = torch.randn(out_f, in_f) * 0.02  # Typical LLM weight scale
    print(f"  Weight shape: {W.shape}")
    print(f"  Weight range: [{W.min():.4f}, {W.max():.4f}]")
    
    # PTQTP baseline
    print("\n[2] PTQTP Baseline (dual free scales)")
    ptqtp = PTQTPQuantizer(block_size=128)
    w_ptqtp, s1, s2 = ptqtp.quantize(W)
    
    mse_ptqtp = ((W - w_ptqtp) ** 2).mean().item()
    print(f"  MSE: {mse_ptqtp:.6f}")
    print(f"  Scale 1: {s1.mean():.6f}, Scale 2: {s2.mean():.6f}")
    
    num_elements = W.numel()
    num_groups = (num_elements + 127) // 128
    bits_ptqtp = ptqtp.storage_bits(num_elements, num_groups)
    print(f"  Storage: {bits_ptqtp / 8 / 1024:.2f} KB")
    
    # TTP
    print("\n[3] Tied Trit-Planes (fixed ratio 3:1)")
    ttp = TTPQuantizer(block_size=128)
    w_ttp, s = ttp.quantize(W)
    
    mse_ttp = ((W - w_ttp) ** 2).mean().item()
    print(f"  MSE: {mse_ttp:.6f}")
    print(f"  Single scale: {s:.6f} (s2 = {3*s:.6f})")
    
    bits_ttp = ttp.storage_bits(num_elements, num_groups)
    print(f"  Storage: {bits_ttp / 8 / 1024:.2f} KB")
    
    # Show nine-level grid
    grid = ttp.get_nine_level_grid(s)
    print(f"\n  Uniform 9-level grid: {grid.tolist()}")
    print(f"  Step size: {s:.6f}")
    
    # Comparison
    print("\n[4] Comparison")
    print(f"  MSE ratio (TTP / PTQTP): {mse_ttp / mse_ptqtp:.3f}")
    print(f"  Storage ratio (TTP / PTQTP): {bits_ttp / bits_ptqtp:.3f}")
    print(f"  Storage reduction: {(1 - bits_ttp/bits_ptqtp)*100:.1f}%")
    
    # Quantized Linear Layer
    print("\n[5] Quantized Linear Layer Inference")
    layer = QuantizedLinear(in_f, out_f, ttp)
    layer.weight = W
    
    # Before quantization
    x = torch.randn(1, 128, in_f)
    out_fp = layer(x)
    print(f"  FP output shape: {out_fp.shape}")
    
    # After quantization
    layer.quantize_weights()
    out_q = layer(x)
    print(f"  Quantized output shape: {out_q.shape}")
    
    output_diff = (out_fp - out_q).abs().mean().item()
    print(f"  Output diff (mean abs): {output_diff:.6f}")
    
    # Full model memory estimate
    print("\n[6] Qwen3-0.6B Full Model Estimate")
    total_params_06b = 600_000_000  # 0.6B parameters
    
    fp16_bytes = total_params_06b * 2
    ttp_bytes = total_params_06b * math.log2(3) * 2 / 8  # two trit planes
    # Plus scales: assume 1 scale per 128 elements, 32-bit each
    num_scales = total_params_06b / 128
    scale_bytes = num_scales * 4  # 32-bit float
    ttp_total = ttp_bytes + scale_bytes
    
    print(f"  FP16 model: {fp16_bytes / 1e6:.1f} MB")
    print(f"  TTP model: {ttp_total / 1e6:.1f} MB")
    print(f"  Compression ratio: {fp16_bytes / ttp_total:.2f}x")
    
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print("  Method: Tied Trit-Planes (TTP)")
    print("  Target: Qwen3-0.6B")
    print("  Effective levels: 9 (uniform)")
    print("  Fixed ratio: s2/s1 = 3")
    print("  Scale storage: 1 per group (vs 2 in PTQTP)")
    print("  Hardware friendly: uniform grid enables LUT dequantization")
    print("=" * 70)


if __name__ == "__main__":
    demo()
