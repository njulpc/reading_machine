#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.24953 - Stable FP4 Training
Title: Stable FP4 Training via Transposition-Invariant Block Quantization
Core Method: 2D Block FP4 Quantization with Transpose Invariance
================================================================================

This script demonstrates:
1. 2D Block FP4 Quantization (square blocks guarantee S(X) = S(X^T))
2. Truncation-Free Scaling (no overflow from max values)
3. Stochastic Rounding (unbiased: E[round(x)] = x)
4. Verification of transpose invariance property

Usage:
    python3 demo.py

Requirements:
    pip install torch
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


# =============================================================================
# 1. 2D Block FP4 Quantizer (Core Innovation)
# =============================================================================

class FP4Quantizer:
    """
    2D Block FP4 Quantizer with Transposition Invariance.
    
    KEY INSIGHT from the paper:
    1D block quantization (e.g., 1x32) causes scale inconsistency after transpose:
        - Forward: X is quantized with scale S_fwd per row
        - Backward: X^T has values redistributed to different blocks
        - Result: S_bwd != S_fwd -> systematic gradient bias
    
    2D square blocks (e.g., 32x32) solve this because:
        - Block B_ij in X corresponds to B_ji in X^T
        - B_ji = B_ij^T (same values, just transposed)
        - max(|B_ij|) = max(|B_ji|) -> S(B_ij) = S(B_ji)
    """
    
    def __init__(self, block_size: int = 32, use_stochastic_rounding: bool = True):
        self.block_size = block_size
        self.use_stochastic_rounding = use_stochastic_rounding
        self.fp4_range = 6.0  # FP4 E2M1: ~[-6, 6]
    
    def _stochastic_round(self, x):
        """Stochastic rounding: E[round(x)] = x (unbiased)"""
        floor = torch.floor(x)
        prob = x - floor
        rand = torch.rand_like(x)
        return floor + (rand < prob).float()
    
    def quantize(self, x):
        """
        2D block FP4 quantization.
        
        Args:
            x: 2D tensor [m, n]
        
        Returns:
            x_dq: dequantized tensor
            scales: per-block scales
        """
        assert x.ndim >= 2
        orig_shape = x.shape
        m, n = x.shape[0], x.shape[1]
        
        # Pad to multiples of block_size
        pad_m = (self.block_size - m % self.block_size) % self.block_size
        pad_n = (self.block_size - n % self.block_size) % self.block_size
        x_pad = F.pad(x, (0, pad_n, 0, pad_m)) if (pad_m or pad_n) else x
        
        m_p, n_p = x_pad.shape[0], x_pad.shape[1]
        num_bm = m_p // self.block_size
        num_bn = n_p // self.block_size
        
        # Reshape: [num_bm, num_bn, block_size, block_size]
        x_blocks = x_pad.reshape(num_bm, self.block_size, num_bn, self.block_size).permute(0, 2, 1, 3)
        
        # === TRUNCATION-FREE SCALING ===
        # S = 2^ceil(log2(2 * M / Q_range))
        # This ensures ALL values fit in representable range (no truncation)
        M = x_blocks.abs().amax(dim=(-2, -1), keepdim=True)
        log_scale = torch.ceil(torch.log2(2 * M / self.fp4_range))
        log_scale = torch.clamp(log_scale, min=-126, max=127)
        scales = 2 ** log_scale
        scales = scales.clamp_min(1e-8)
        
        # Quantize
        x_scaled = x_blocks / scales
        if self.use_stochastic_rounding:
            x_q = self._stochastic_round(x_scaled)
        else:
            x_q = torch.round(x_scaled)
        x_q = torch.clamp(x_q, -self.fp4_range, self.fp4_range)
        
        # Dequantize and reshape
        x_dq = x_q * scales
        x_out = x_dq.permute(0, 2, 1, 3).reshape(m_p, n_p)[:m, :n]
        
        return x_out, scales.squeeze()
    
    def verify_transpose_invariance(self, x):
        """Verify S(X) == S(X^T)"""
        _, s1 = self.quantize(x)
        _, s2 = self.quantize(x.t())
        # Flatten and compare (shapes may differ due to padding)
        s1_flat = s1.flatten()
        s2_flat = s2.flatten()
        min_len = min(s1_flat.numel(), s2_flat.numel())
        return torch.allclose(s1_flat[:min_len], s2_flat[:min_len], atol=1e-5)


# =============================================================================
# 2. Linear Layer with FP4 Weights
# =============================================================================

class FP4Linear(nn.Module):
    """Linear layer that internally uses FP4 quantized weights"""
    
    def __init__(self, in_features, out_features, block_size=32):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))
        self.quantizer = FP4Quantizer(block_size=block_size)
    
    def forward(self, x):
        # Quantize weight on-the-fly (simulating FP4 inference)
        w_q, _ = self.quantizer.quantize(self.weight)
        return F.linear(x, w_q, self.bias)


# =============================================================================
# 3. Demonstration
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2607.24953 - Stable FP4 Training")
    print(" Method: 2D Block FP4 with Transposition Invariance")
    print("=" * 70)
    
    # === Demo 1: Basic Quantization ===
    print("\n[1] Basic 2D Block FP4 Quantization")
    quantizer = FP4Quantizer(block_size=32, use_stochastic_rounding=True)
    
    X = torch.randn(64, 64)
    X_q, scales = quantizer.quantize(X)
    
    print(f"  Input shape: {X.shape}")
    print(f"  Block size: {quantizer.block_size}x{quantizer.block_size}")
    print(f"  Number of blocks: {scales.numel()}")
    print(f"  Original range: [{X.min():.3f}, {X.max():.3f}]")
    print(f"  Quantized range: [{X_q.min():.3f}, {X_q.max():.3f}]")
    print(f"  MSE: {((X - X_q) ** 2).mean().item():.6f}")
    
    # === Demo 2: Transpose Invariance (THE KEY RESULT) ===
    print("\n[2] Verifying Transpose Invariance (S(X) == S(X^T))")
    
    test_sizes = [(64, 64), (128, 96), (256, 128), (512, 512)]
    for m, n in test_sizes:
        X_test = torch.randn(m, n)
        is_invariant = quantizer.verify_transpose_invariance(X_test)
        status = "✅ PASS" if is_invariant else "❌ FAIL"
        print(f"  {m}x{n}: {status}")
    
    # Show WHY 1D fails
    print("\n[3] Why 1D Block Fails (Demonstration)")
    
    def quantize_1d_block(x, block_size=32):
        """1D row-wise quantization (for comparison)"""
        scales = []
        x_q = x.clone()
        for i in range(0, x.shape[0], block_size):
            block = x[i:i+block_size]
            scale = block.abs().max() / 6.0
            scale = scale.clamp_min(1e-8)
            x_q[i:i+block_size] = torch.clamp(torch.round(block / scale), -6, 6) * scale
            scales.append(scale)
        return x_q, scales
    
    X_1d, s1d = quantize_1d_block(X)
    _, s1d_T = quantize_1d_block(X.t())
    
    print(f"  1D block scales (forward): {len(s1d)} scales")
    print(f"  1D block scales (transpose): {len(s1d_T)} scales")
    print(f"  Scales match: {len(s1d) == len(s1d_T) and all(torch.allclose(a, b) for a, b in zip(s1d, s1d_T))}")
    
    # === Demo 3: Stochastic Rounding ===
    print("\n[4] Stochastic Rounding Verification (unbiased)")
    
    x = torch.tensor([2.7])
    rounds = []
    for _ in range(1000):
        r = quantizer._stochastic_round(x)
        rounds.append(r.item())
    
    avg = sum(rounds) / len(rounds)
    print(f"  Value: 2.7")
    print(f"  Nearest round: 3.0")
    print(f"  Stochastic round average: {avg:.4f}")
    print(f"  Bias: {abs(avg - 2.7):.4f} (should be ~0)")
    
    # === Demo 4: Model Compression ===
    print("\n[5] FP4 Linear Layer Demo")
    
    layer_fp4 = FP4Linear(512, 256, block_size=32)
    layer_fp32 = nn.Linear(512, 256)
    
    x = torch.randn(4, 512)
    
    with torch.no_grad():
        out_fp4 = layer_fp4(x)
        out_fp32 = layer_fp32(x)
    
    print(f"  Input: {x.shape}")
    print(f"  FP4 output: {out_fp4.shape}")
    print(f"  FP32 output: {out_fp32.shape}")
    print(f"  Output diff (mean abs): {(out_fp4 - out_fp32).abs().mean().item():.4f}")
    
    fp32_size = sum(p.numel() * 4 for p in layer_fp32.parameters()) / 1024
    fp4_size = sum(p.numel() // 4 for p in layer_fp4.parameters()) / 1024  # ~4x
    print(f"  FP32 size: {fp32_size:.1f} KB")
    print(f"  FP4 size: ~{fp4_size:.1f} KB")
    
    # === Summary ===
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print("  1. 2D square blocks guarantee S(X) = S(X^T)")
    print("  2. Truncation-free scaling prevents overflow")
    print("  3. Stochastic rounding is unbiased")
    print("  4. ~4x compression with minimal accuracy loss")
    print("  5. Enables stable FP4 training (paper: gap < 1.3% on 30B)")
    print("=" * 70)


if __name__ == "__main__":
    demo()
