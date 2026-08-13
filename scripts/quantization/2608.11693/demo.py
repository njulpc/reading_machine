#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.11693 - Spec Sheets Are Not Kernels
Title: ISA- and Source-Level Audit of INT8 Availability on NVIDIA Blackwell Ultra
Core Finding: INT8 W8A8 is nominally present but effectively undeployable on B300
================================================================================

This script demonstrates:
1. INT8 W8A8 quantization implementation
2. Calibration strategy comparison (abs-max vs percentile)
3. Simulated stack-level availability audit

Note: This is primarily a hardware audit paper. The demo shows the quantization
format that is being audited, not a new algorithm.

Usage:
    python3 demo.py

Requirements:
    pip install torch
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# =============================================================================
# 1. INT8 W8A8 Quantizer
# =============================================================================

class INT8W8A8Quantizer:
    """
    INT8 Weight and Activation Quantization (W8A8).
    
    This is the format whose availability is audited in the paper.
    """
    
    def __init__(self, weight_calibration='abs-max', act_calibration='percentile', act_percentile=99.9):
        self.weight_calibration = weight_calibration
        self.act_calibration = act_calibration
        self.act_percentile = act_percentile
        
        self.w_scale = None
        self.w_zero = None
        self.a_scale = None
        self.a_zero = None
    
    def calibrate_weights(self, weight):
        """Calibrate weight quantization."""
        if self.weight_calibration == 'abs-max':
            w_max = weight.abs().max()
            self.w_scale = w_max / 127.0
            self.w_zero = 0.0
        elif self.weight_calibration == 'percentile':
            p99 = torch.quantile(weight.abs(), 0.999)
            self.w_scale = p99 / 127.0
            self.w_zero = 0.0
    
    def calibrate_activations(self, activation_samples):
        """Calibrate activation quantization from samples."""
        all_acts = torch.cat([a.flatten() for a in activation_samples])
        
        if self.act_calibration == 'abs-max':
            a_max = all_acts.abs().max()
            self.a_scale = a_max / 127.0
            self.a_zero = 0.0
        elif self.act_calibration == 'percentile':
            p = torch.quantile(all_acts.abs(), self.act_percentile / 100.0)
            self.a_scale = p / 127.0
            self.a_zero = 0.0
    
    def quantize_weight(self, w):
        """Quantize weight to INT8."""
        if self.w_scale is None:
            self.calibrate_weights(w)
        q = torch.round(w / self.w_scale.clamp_min(1e-8)).clamp(-128, 127)
        return q, self.w_scale
    
    def quantize_activation(self, a):
        """Quantize activation to INT8."""
        if self.a_scale is None:
            raise ValueError("Activation quantizer not calibrated")
        q = torch.round(a / self.a_scale.clamp_min(1e-8)).clamp(-128, 127)
        return q, self.a_scale
    
    def dequantize(self, q, scale):
        """Dequantize from INT8."""
        return q * scale


# =============================================================================
# 2. Simulated Stack Audit
# =============================================================================

class StackAvailabilityAuditor:
    """
    Simulated audit of INT8 availability across software stack layers.
    
    Based on the paper's findings on B300:
    - Layer 1 (Spec): INT8 present (FP8:INT8 = 30:1)
    - Layer 2 (PTX ISA): INT8 .kind::i8 NOT exposed on sm_103a
    - Layer 3 (CUTLASS): INT8 UMMA explicitly skipped for 103a
    - Layer 4 (vLLM): No INT8 GEMM, hard runtime error
    - Layer 5 (SGLang): INT8 GEMM stops at Sm90
    """
    
    def __init__(self, gpu_arch='sm_103a'):
        self.gpu_arch = gpu_arch
        self.layers = {
            'spec_sheet': {'status': 'AVAILABLE', 'note': 'FP8:INT8 = 30:1 ratio'},
            'ptx_isa': {'status': 'MISSING', 'note': 'tcgen05.mma .kind::i8 not on sm_103a'},
            'cutlass': {'status': 'SKIPPED', 'note': 'Kernel generator skips INT8 for 103a'},
            'vllm': {'status': 'HARD_FAIL', 'note': 'No INT8 GEMM, crashes at first forward'},
            'sglang': {'status': 'NOT_COVERED', 'note': 'INT8 stops at Sm90'},
        }
    
    def audit(self):
        """Run full stack audit."""
        print(f"\nINT8 W8A8 Stack Availability Audit for {self.gpu_arch}")
        print("="*70)
        print(f"{'Layer':<15} {'Status':<15} {'Note'}")
        print("-"*70)
        
        overall_available = True
        for layer, info in self.layers.items():
            status = info['status']
            available = status in ['AVAILABLE', 'SUPPORTED']
            if not available:
                overall_available = False
            
            indicator = "✓" if available else "✗"
            print(f"{layer:<15} {status:<15} {info['note']}")
        
        print("-"*70)
        if overall_available:
            print("Result: INT8 W8A8 is FULLY DEPLOYABLE")
        else:
            print("Result: INT8 W8A8 is NOT DEPLOYABLE by default")
            print("Note: Escape hatch exists via Triton JIT backend")
        
        return overall_available


# =============================================================================
# 3. Demo Model and Evaluation
# =============================================================================

class SimpleMLP(nn.Module):
    def __init__(self, in_dim=128, hidden_dim=256, out_dim=10):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, out_dim)
        self.relu = nn.ReLU()
    
    def forward(self, x, return_acts=False):
        a1 = self.relu(self.fc1(x))
        a2 = self.relu(self.fc2(a1))
        out = self.fc3(a2)
        if return_acts:
            return out, [a1, a2]
        return out


def demo():
    print("="*70)
    print(" Paper: 2608.11693 - Spec Sheets Are Not Kernels")
    print(" Topic: INT8 W8A8 Availability on NVIDIA Blackwell Ultra")
    print("="*70)
    
    # Part 1: Stack Audit Simulation
    print("\n[1] Simulated Stack Availability Audit")
    auditor = StackAvailabilityAuditor(gpu_arch='sm_103a (B300)')
    auditor.audit()
    
    # Part 2: INT8 W8A8 Quantization Demo
    print("\n[2] INT8 W8A8 Quantization Demonstration")
    
    torch.manual_seed(42)
    model = SimpleMLP(in_dim=128, hidden_dim=256, out_dim=10)
    model.eval()
    
    # Calibration data
    calib_X = torch.randn(64, 128)
    test_X = torch.randn(100, 128)
    test_Y = torch.randint(0, 10, (100,))
    
    # Collect activation samples
    with torch.no_grad():
        _, acts_fp = model(calib_X, return_acts=True)
    
    # Compare calibration strategies
    print("\n[3] Calibration Strategy Comparison")
    strategies = [
        ('abs-max', 'abs-max', 99.9),
        ('percentile-99', 'percentile', 99.0),
        ('percentile-99.9', 'percentile', 99.9),
    ]
    
    print(f"\n{'Strategy':<20} {'FP Acc':>10} {'INT8 Acc':>10} {'Degradation':>12}")
    print("-"*60)
    
    for name, w_calib, a_pctl in strategies:
        quantizer = INT8W8A8Quantizer(
            weight_calibration=w_calib,
            act_calibration='percentile' if 'percentile' in name else 'abs-max',
            act_percentile=a_pctl
        )
        
        # Calibrate
        quantizer.calibrate_weights(model.fc1.weight)
        quantizer.calibrate_activations(acts_fp)
        
        # Quantized forward
        with torch.no_grad():
            # Layer 1
            w1_q, s1 = quantizer.quantize_weight(model.fc1.weight)
            a1_fp = model.relu(F.linear(test_X, model.fc1.weight, model.fc1.bias))
            a1_q, sa1 = quantizer.quantize_activation(a1_fp)
            a1_dq = quantizer.dequantize(a1_q, sa1)
            
            # Layer 2
            w2_q, s2 = quantizer.quantize_weight(model.fc2.weight)
            a2_fp = model.relu(F.linear(a1_dq, model.fc2.weight, model.fc2.bias))
            a2_q, sa2 = quantizer.quantize_activation(a2_fp)
            a2_dq = quantizer.dequantize(a2_q, sa2)
            
            # Layer 3 (output, keep FP)
            out_q = F.linear(a2_dq, model.fc3.weight, model.fc3.bias)
            
            # FP baseline
            out_fp = model(test_X)
            
            acc_fp = (out_fp.argmax(dim=1) == test_Y).float().mean().item()
            acc_q = (out_q.argmax(dim=1) == test_Y).float().mean().item()
            degradation = (acc_fp - acc_q) / acc_fp * 100 if acc_fp > 0 else 0
        
        print(f"{name:<20} {acc_fp:>10.2%} {acc_q:>10.2%} {degradation:>11.1f}%")
    
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    print("This paper's key finding: a quantization format's availability is")
    print("a property of the WHOLE STACK, not just the hardware spec sheet.")
    print("On B300, INT8 W8A8 is present in specs but undeployable by default")
    print("due to consistent withdrawal across PTX ISA, CUTLASS, and engines.")
    print("="*70)


if __name__ == "__main__":
    demo()
