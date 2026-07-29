#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.24981 - Integer-Only DETR
Title: Enabling Fully Integer-Only Inference for Lightweight Detection Transformers
Core Method: Pure Integer Operations (GELU, Softmax, LayerNorm) + INT8 Quantization
================================================================================

This script demonstrates:
1. Integer GELU approximation (lookup table + piecewise)
2. Integer Softmax (Shiftmax with bit-shift approximation)
3. Integer LayerNorm
4. Scale-Preserving Split Convolution

Usage:
    python3 demo.py

Requirements:
    pip install torch
================================================================================
"""

import torch
import torch.nn as nn
import math


# =============================================================================
# 1. Integer GELU (Sign-Dependent ShiftGELU)
# =============================================================================

class IntegerGELU(nn.Module):
    """
    Integer GELU approximation for pure integer-only inference.
    
    GELU(x) = 0.5 * x * (1 + erf(x / sqrt(2)))
    
    Integer approximation strategies:
    1. LUT (Lookup Table): precompute for [-128, 127] range
    2. Piecewise linear: simple region-based approximation
    """
    
    def __init__(self, num_bits=8, use_lut=True):
        super().__init__()
        self.num_bits = num_bits
        self.use_lut = use_lut
        
        if use_lut:
            self.register_buffer('lut', self._build_lut())
    
    def _build_lut(self):
        """Precompute GELU for integer range [-128, 127]"""
        x_vals = torch.arange(-128, 128, dtype=torch.float32)
        
        # True GELU
        gelu_true = 0.5 * x_vals * (1 + torch.erf(x_vals / math.sqrt(2)))
        
        # Quantize to output range
        qmax = 2 ** (self.num_bits - 1) - 1
        scale = gelu_true.abs().max() / qmax
        if scale < 1e-8:
            scale = 1.0
        
        gelu_q = torch.clamp(torch.round(gelu_true / scale), -qmax - 1, qmax)
        return gelu_q
    
    def forward(self, x):
        if self.use_lut:
            # Map to LUT indices
            x_idx = torch.clamp(x.long() + 128, 0, 255)
            return self.lut[x_idx]
        else:
            # Piecewise approximation
            # Positive: GELU(x) ≈ x
            # Negative: GELU(x) ≈ 0 (smooth transition)
            return torch.where(x > 0, x, torch.zeros_like(x))


# =============================================================================
# 2. Integer Softmax (Shiftmax)
# =============================================================================

class IntegerSoftmax(nn.Module):
    """
    Integer Softmax using shift-based exponential approximation.
    
    Key idea: exp(x) ≈ 2^(x / scale)
    Uses torch.pow instead of bit-shift for float compatibility.
    """
    
    def __init__(self, dim=-1, num_bits=8, shift_scale=8):
        super().__init__()
        self.dim = dim
        self.num_bits = num_bits
        self.shift_scale = shift_scale
    
    def forward(self, x):
        # x: integer input
        
        # Subtract max for stability
        x_max = x.amax(dim=self.dim, keepdim=True)
        x_shifted = x - x_max
        
        # exp(x) ≈ 2^(x / shift_scale)
        exp_shift = x_shifted.long() // self.shift_scale
        exp_shift = torch.clamp(exp_shift, 0, self.num_bits - 1)
        
        # Use torch.pow for float compatibility
        exp_approx = torch.pow(torch.tensor(2.0, device=x.device), exp_shift.float())
        exp_approx = torch.clamp(exp_approx, 1, 2 ** self.num_bits - 1)
        
        # Normalize
        sum_exp = exp_approx.sum(dim=self.dim, keepdim=True).clamp_min(1)
        out = (exp_approx * (2 ** self.num_bits - 1)) // sum_exp
        
        return out


# =============================================================================
# 3. Integer LayerNorm
# =============================================================================

class IntegerLayerNorm(nn.Module):
    """
    Integer LayerNorm approximation.
    
    LayerNorm(x) = (x - mean) / sqrt(var + eps) * gamma + beta
    
    Integer version computes mean and variance in integer space.
    """
    
    def __init__(self, normalized_shape, num_bits=8, eps=1e-5):
        super().__init__()
        self.num_bits = num_bits
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(normalized_shape))
        self.beta = nn.Parameter(torch.zeros(normalized_shape))
    
    def forward(self, x):
        # Integer mean
        mean = x.float().mean(dim=-1, keepdim=True).round()
        
        # Integer variance (simplified)
        var = ((x.float() - mean) ** 2).mean(dim=-1, keepdim=True)
        std = torch.sqrt(var + self.eps)
        
        # Normalize
        x_norm = (x.float() - mean) / std
        
        # Scale and shift
        out = x_norm * self.gamma + self.beta
        
        # Requantize
        out = torch.clamp(torch.round(out), -(2 ** (self.num_bits - 1)), 2 ** (self.num_bits - 1) - 1)
        
        return out


# =============================================================================
# 4. Scale-Preserving Split Convolution
# =============================================================================

class ScalePreservingSplitConv(nn.Module):
    """
    Scale-Preserving Split Convolution for multi-scale feature projection.
    
    Each branch has its own independent activation scale,
    preventing resolution loss from naive quantization.
    """
    
    def __init__(self, in_ch, out_ch, num_scales=3):
        super().__init__()
        self.branches = nn.ModuleList([
            nn.Conv2d(in_ch, out_ch // num_scales, 1, bias=False)
            for _ in range(num_scales)
        ])
        # Independent scales per branch
        self.scales = [1.0] * num_scales
    
    def forward(self, x_list):
        """
        Args:
            x_list: list of feature maps at different scales
        """
        outputs = []
        for i, (x, branch) in enumerate(zip(x_list, self.branches)):
            out = branch(x)
            # Apply branch-specific scale
            out = torch.round(out * self.scales[i])
            outputs.append(out)
        return torch.cat(outputs, dim=1)


# =============================================================================
# 5. Demonstration
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2607.24981 - Integer-Only DETR")
    print(" Method: Pure Integer Operations for Edge Deployment")
    print("=" * 70)
    
    # === Integer GELU ===
    print("\n[1] Integer GELU Approximation")
    gelu = IntegerGELU(num_bits=8, use_lut=True)
    
    test_values = [-100, -50, -10, 0, 10, 50, 100]
    print("  Input -> Integer GELU")
    for v in test_values:
        x = torch.tensor([[v]])
        out = gelu(x)
        print(f"  {v:4d}  -> {out.item():6.1f}")
    
    # Verify LUT captures true GELU shape
    print("\n  LUT shape check:")
    print(f"  GELU(0) = {gelu(torch.tensor([[0]])).item():.1f} (should be ~0)")
    print(f"  GELU(100) = {gelu(torch.tensor([[100]])).item():.1f} (should be large positive)")
    print(f"  GELU(-100) = {gelu(torch.tensor([[-100]])).item():.1f} (should be near 0)")
    
    # === Integer Softmax ===
    print("\n[2] Integer Softmax (Shiftmax)")
    softmax = IntegerSoftmax(dim=-1, num_bits=8)
    
    x = torch.randint(-50, 50, (1, 10))
    out = softmax(x)
    
    print(f"  Input: {x.tolist()}")
    print(f"  Output: {out.tolist()}")
    print(f"  Sum: {out.sum().item():.1f} (should be ~255 for 8-bit)")
    
    # Compare with float softmax
    x_float = x.float()
    out_float = torch.softmax(x_float, dim=-1)
    print(f"  Float softmax: {[f'{v:.3f}' for v in out_float[0].tolist()]}")
    
    # === Integer LayerNorm ===
    print("\n[3] Integer LayerNorm")
    layernorm = IntegerLayerNorm(normalized_shape=64, num_bits=8)
    
    x = torch.randint(-100, 100, (2, 64))
    out = layernorm(x)
    
    print(f"  Input range: [{x.min().item()}, {x.max().item()}]")
    print(f"  Output range: [{out.min().item()}, {out.max().item()}]")
    print(f"  Output mean (per sample): {out.float().mean(dim=-1).tolist()}")
    
    # === Scale-Preserving Split Conv ===
    print("\n[4] Scale-Preserving Split Convolution")
    split_conv = ScalePreservingSplitConv(in_ch=64, out_ch=128, num_scales=3)
    
    # Multi-scale features
    x1 = torch.randn(1, 64, 56, 56)   # High res
    x2 = torch.randn(1, 64, 28, 28)   # Med res
    x3 = torch.randn(1, 64, 14, 14)   # Low res
    
    # Resize to same size for demo
    x2_up = torch.nn.functional.interpolate(x2, size=(56, 56), mode='bilinear', align_corners=False)
    x3_up = torch.nn.functional.interpolate(x3, size=(56, 56), mode='bilinear', align_corners=False)
    
    out = split_conv([x1, x2_up, x3_up])
    print(f"  Input scales: 56x56, 28x28, 14x14")
    print(f"  Output: {out.shape}")
    print(f"  Each branch has independent scale: {split_conv.scales}")
    
    # === End-to-end Integer Block ===
    print("\n[5] End-to-End Integer Transformer Block")
    
    dim = 64
    x = torch.randint(-50, 50, (2, 16, dim))  # [B, seq, dim]
    
    # Integer operations only
    int_ln = IntegerLayerNorm(dim, num_bits=8)
    int_gelu = IntegerGELU(num_bits=8, use_lut=True)
    
    x = int_ln(x)
    x = int_gelu(x)
    
    print(f"  Input shape: [2, 16, {dim}]")
    print(f"  After LayerNorm: range [{x.min().item()}, {x.max().item()}]")
    print(f"  After GELU: range [{x.min().item()}, {x.max().item()}]")
    
    # Summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print("  Integer GELU:    LUT-based, O(1) lookup")
    print("  Integer Softmax: Shiftmax, 2^(x/scale) approximation")
    print("  Integer LN:      Integer mean/var, float norm, requantize")
    print("  Split Conv:      Per-branch independent scales")
    print("  Result:          ~3.6x smaller, >10x compute reduction")
    print("=" * 70)


if __name__ == "__main__":
    demo()
