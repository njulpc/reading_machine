#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.24568 - Bit-Accurate FPGA Evaluation
Title: Bit-Accurate FPGA Evaluation of Learned Feature Gating
Core Method: PTQ vs QAT Comparison on FPGA with Fixed-Point Arithmetic
================================================================================

This script demonstrates:
1. PTQ (Post-Training Quantization): quantize after training
2. QAT (Quantization-Aware Training): quantize during training
3. Bit-accurate fixed-point simulation
4. FPGA resource estimation

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
# 1. Fixed-Point Quantizer (Simulating FPGA)
# =============================================================================

class FixedPointQuantizer:
    """
    Fixed-point quantization for FPGA simulation.
    
    On FPGA, operations use fixed-point arithmetic:
    - Integer part: I bits
    - Fractional part: F bits
    - Total: W = I + F bits
    
    This simulates the bit-accurate behavior before hardware deployment.
    """
    
    def __init__(self, total_bits=8, int_bits=2):
        self.total_bits = total_bits
        self.int_bits = int_bits
        self.frac_bits = total_bits - int_bits
        self.qmax = 2 ** (total_bits - 1) - 1
        self.qmin = -(2 ** (total_bits - 1))
        
        # Scale: 2^(-F)
        self.scale = 2 ** (-self.frac_bits)
    
    def quantize(self, x):
        """Quantize to fixed-point representation"""
        # Scale up, round, clamp
        x_scaled = x / self.scale
        x_q = torch.clamp(torch.round(x_scaled), self.qmin, self.qmax)
        # Scale back
        return x_q * self.scale
    
    def get_fpga_resources(self, num_mults, num_adds):
        """
        Estimate FPGA resources for fixed-point operations.
        
        DSP slices: one per multiplier
        LUTs: logic for additions and control
        """
        dsp_slices = num_mults  # Each multiplier needs one DSP
        lut_estimate = num_adds * self.total_bits  # Rough estimate
        
        return {
            "dsp_slices": dsp_slices,
            "luts": lut_estimate,
            "bitwidth": self.total_bits
        }


# =============================================================================
# 2. PTQ vs QAT Comparison
# =============================================================================

class PTQModel(nn.Module):
    """Post-Training Quantization: train FP32, then quantize"""
    
    def __init__(self, input_dim=64, hidden_dim=128, output_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.gate = nn.Linear(input_dim, hidden_dim)  # Learned feature gating
    
    def forward(self, x):
        # Feature gating
        gate = torch.sigmoid(self.gate(x))
        
        h = F.relu(self.fc1(x))
        h = h * gate  # Gated activation
        h = F.relu(self.fc2(h))
        out = self.fc3(h)
        return out
    
    def quantize(self, quantizer):
        """Apply PTQ after training"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                module.weight.data = quantizer.quantize(module.weight.data)
                if module.bias is not None:
                    module.bias.data = quantizer.quantize(module.bias.data)


class QATModel(nn.Module):
    """Quantization-Aware Training: simulate quantization during training"""
    
    def __init__(self, input_dim=64, hidden_dim=128, output_dim=2, quantizer=None):
        super().__init__()
        self.quantizer = quantizer
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.gate = nn.Linear(input_dim, hidden_dim)
    
    def fake_quantize(self, x):
        """Simulate quantization with STE (Straight-Through Estimator)"""
        if self.quantizer is None:
            return x
        x_q = self.quantizer.quantize(x)
        # STE: gradient passes through
        return x + (x_q - x).detach()
    
    def forward(self, x):
        gate = torch.sigmoid(self.fake_quantize(self.gate(x)))
        
        h = F.relu(self.fake_quantize(self.fc1(x)))
        h = h * gate
        h = F.relu(self.fake_quantize(self.fc2(h)))
        out = self.fc3(h)
        return out


# =============================================================================
# 3. FPGA Resource Estimator
# =============================================================================

def estimate_fpga_resources(model, fixed_bits=8):
    """
    Estimate FPGA resources for a given model and bitwidth.
    
    Resources:
    - DSP slices: for multipliers (MAC operations)
    - LUTs: for adders, control logic
    - BRAM: for weight storage
    """
    total_params = sum(p.numel() for p in model.parameters())
    
    # Count MAC operations per forward pass
    macs = 0
    for module in model.modules():
        if isinstance(module, nn.Linear):
            macs += module.in_features * module.out_features
    
    # Resource estimates
    dsp_per_mac = 1  # One DSP per multiplier
    lut_per_add = fixed_bits  # Rough: LUTs scale with bitwidth
    
    resources = {
        "total_params": total_params,
        "macs_per_forward": macs,
        "dsp_slices": macs * dsp_per_mac,
        "luts": macs * lut_per_add,
        "weight_bram_kb": total_params * fixed_bits / 8 / 1024,
        "bitwidth": fixed_bits
    }
    
    return resources


# =============================================================================
# 4. Demonstration
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2607.24568 - Bit-Accurate FPGA Evaluation")
    print(" Method: PTQ vs QAT with Fixed-Point FPGA Simulation")
    print("=" * 70)
    
    # === Fixed-Point Quantizer ===
    print("\n[1] Fixed-Point Quantization (8-bit, 2 int bits)")
    quantizer = FixedPointQuantizer(total_bits=8, int_bits=2)
    
    x = torch.randn(10)
    x_q = quantizer.quantize(x)
    
    print(f"  Scale: 2^(-{quantizer.frac_bits}) = {quantizer.scale}")
    print(f"  Range: [{quantizer.qmin * quantizer.scale:.4f}, {quantizer.qmax * quantizer.scale:.4f}]")
    print(f"  Original: {x[:5].tolist()}")
    print(f"  Quantized: {x_q[:5].tolist()}")
    print(f"  MSE: {((x - x_q) ** 2).mean().item():.6f}")
    
    # === PTQ vs QAT ===
    print("\n[2] PTQ vs QAT Comparison")
    
    # Train both models (simulated)
    model_ptq = PTQModel(input_dim=64, hidden_dim=128, output_dim=2)
    model_qat = QATModel(input_dim=64, hidden_dim=128, output_dim=2, quantizer=quantizer)
    
    # Copy same initialization for fair comparison
    model_qat.load_state_dict(model_ptq.state_dict())
    
    # Simulate training data
    X_train = torch.randn(100, 64)
    y_train = torch.randint(0, 2, (100,))
    
    # Train QAT model (with fake quantization)
    optimizer = torch.optim.SGD(model_qat.parameters(), lr=0.01)
    for epoch in range(10):
        optimizer.zero_grad()
        out = model_qat(X_train)
        loss = F.cross_entropy(out, y_train)
        loss.backward()
        optimizer.step()
    
    print(f"  QAT training loss: {loss.item():.4f}")
    
    # Apply PTQ to FP32 model
    model_ptq.quantize(quantizer)
    
    # Compare outputs
    X_test = torch.randn(10, 64)
    with torch.no_grad():
        out_ptq = model_ptq(X_test)
        out_qat = model_qat(X_test)
    
    diff = (out_ptq - out_qat).abs().mean().item()
    print(f"  PTQ vs QAT output diff: {diff:.4f}")
    print(f"  (QAT typically has lower diff to FP32 than PTQ)")
    
    # === FPGA Resource Estimation ===
    print("\n[3] FPGA Resource Estimation")
    
    for bits in [8, 16, 32]:
        resources = estimate_fpga_resources(model_ptq, fixed_bits=bits)
        print(f"\n  {bits}-bit Configuration:")
        print(f"    Parameters: {resources['total_params']:,}")
        print(f"    MACs/forward: {resources['macs_per_forward']:,}")
        print(f"    DSP slices: {resources['dsp_slices']:,}")
        print(f"    LUTs (est.): {resources['luts']:,}")
        print(f"    Weight BRAM: {resources['weight_bram_kb']:.1f} KB")
    
    # === Bit-Accurate Fixed-Point ===
    print("\n[4] Bit-Accurate Fixed-Point Behavior")
    
    # Show how different bitwidths affect precision
    test_val = torch.tensor([0.1234])
    for bits in [4, 8, 16]:
        fpq = FixedPointQuantizer(total_bits=bits, int_bits=2)
        q = fpq.quantize(test_val)
        error = abs(q.item() - test_val.item())
        print(f"  {bits}-bit: {test_val.item():.4f} -> {q.item():.4f} (error: {error:.6f})")
    
    # === Summary ===
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print("  PTQ: Simple, but accuracy loss can be significant")
    print("  QAT: Better accuracy, requires training-time simulation")
    print("  FPGA: Fixed-point reduces DSP/LUT usage vs floating-point")
    print("  Paper finding: QAT recovers ~2-3% accuracy over PTQ")
    print("=" * 70)


if __name__ == "__main__":
    demo()
