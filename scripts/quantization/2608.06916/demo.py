#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.06916 - MiCoPro
Title: End-to-End Mixed Precision HW/SW Co-design with HW-aware Proxy Model
Core Method: Mixed-precision quantization with hardware-aware latency proxy
================================================================================

This script demonstrates:
1. Layer-wise sensitivity analysis for quantization
2. Mixed-precision bit-width assignment under latency budget
3. Hardware-aware latency proxy model
4. Comparison: uniform vs mixed-precision quantization
5. Applied to Qwen3-0.6B

Usage:
    python3 demo.py

Requirements:
    pip install torch transformers
================================================================================
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple, Dict
import copy

# =============================================================================
# 1. Quantization Utilities
# =============================================================================

def quantize_uniform(w: torch.Tensor, bits: int) -> torch.Tensor:
    """Uniform per-tensor quantization."""
    if bits >= 16:
        return w.clone()
    w_min = w.min()
    w_max = w.max()
    scale = (w_max - w_min) / (2 ** bits - 1)
    scale = scale.clamp_min(1e-8)
    w_q = torch.round((w - w_min) / scale).clamp(0, 2 ** bits - 1)
    return w_q * scale + w_min


def compute_mse(w_fp: torch.Tensor, w_q: torch.Tensor) -> float:
    """Compute reconstruction MSE."""
    return ((w_fp - w_q) ** 2).mean().item()


# =============================================================================
# 2. Hardware-Aware Latency Proxy
# =============================================================================

class LatencyProxy:
    """
    Simplified hardware-aware latency proxy.

    Models latency as a function of layer dimensions and bit-width.
    In real MiCoPro, this would be calibrated on actual hardware.
    """

    def __init__(self, base_latency_per_op: float = 1e-9):
        self.base_latency = base_latency_per_op

    def estimate_layer_latency(
        self,
        in_features: int,
        out_features: int,
        bit_width: int,
    ) -> float:
        """
        Estimate latency for a linear layer.

        Assumptions:
        - Latency is proportional to MAC operations
        - Lower bit-width allows more ops per cycle (up to 2x for INT4 vs INT8)
        """
        macs = in_features * out_features

        # Bit-width speedup: INT4 ~ 2x INT8, INT8 ~ 2x FP16
        if bit_width <= 4:
            speedup = 2.0
        elif bit_width <= 8:
            speedup = 1.0
        else:
            speedup = 0.5

        latency = macs * self.base_latency / speedup
        return latency

    def estimate_model_latency(
        self,
        layer_dims: List[Tuple[int, int]],
        bit_configs: List[int],
    ) -> float:
        """Estimate total model latency."""
        total = 0.0
        for (in_f, out_f), bits in zip(layer_dims, bit_configs):
            total += self.estimate_layer_latency(in_f, out_f, bits)
        return total


# =============================================================================
# 3. Sensitivity Analysis
# =============================================================================

def analyze_layer_sensitivity(
    weight: torch.Tensor,
    candidate_bits: List[int] = [4, 6, 8, 16],
) -> Dict[int, float]:
    """
    Analyze how sensitive a layer is to quantization.

    Returns MSE for each candidate bit-width.
    Lower MSE at low bits = less sensitive = can use lower precision.
    """
    w_fp = weight.float()
    sensitivity = {}

    for bits in candidate_bits:
        if bits >= 16:
            sensitivity[bits] = 0.0  # FP16 is baseline
        else:
            w_q = quantize_uniform(w_fp, bits)
            mse = compute_mse(w_fp, w_q)
            sensitivity[bits] = mse

    return sensitivity


def compute_sensitivity_score(sensitivity: Dict[int, float]) -> float:
    """
    Compute a single sensitivity score.

    Higher score = more sensitive = needs higher precision.
    """
    # Use ratio of INT4 MSE to FP16 MSE as sensitivity indicator
    mse_4 = sensitivity.get(4, 1.0)
    mse_16 = sensitivity.get(16, 1e-8)
    if mse_16 < 1e-10:
        mse_16 = 1e-10
    return mse_4 / mse_16


# =============================================================================
# 4. Mixed-Precision Assignment
# =============================================================================

def assign_mixed_precision(
    layer_sensitivities: List[Dict[int, float]],
    layer_dims: List[Tuple[int, int]],
    latency_budget: float,
    proxy: LatencyProxy,
    candidate_bits: List[int] = [4, 6, 8, 16],
) -> List[int]:
    """
    Assign mixed-precision bit-widths to layers under latency budget.

    Strategy:
    1. Start with all layers at lowest precision
    2. Iteratively upgrade the most sensitive layer until budget exhausted
    """
    n_layers = len(layer_sensitivities)

    # Initialize all layers to lowest precision
    assignments = [min(candidate_bits)] * n_layers

    # Compute sensitivity scores
    scores = [compute_sensitivity_score(s) for s in layer_sensitivities]

    # Sort layers by sensitivity (most sensitive first)
    sorted_indices = sorted(range(n_layers), key=lambda i: scores[i], reverse=True)

    # Iteratively upgrade most sensitive layers
    for idx in sorted_indices:
        current_bits = assignments[idx]

        # Find next higher precision
        higher_bits = [b for b in candidate_bits if b > current_bits]
        if not higher_bits:
            continue
        next_bits = min(higher_bits)

        # Check if upgrade fits budget
        test_assignments = assignments.copy()
        test_assignments[idx] = next_bits

        latency = proxy.estimate_model_latency(layer_dims, test_assignments)
        if latency <= latency_budget:
            assignments[idx] = next_bits

    return assignments


# =============================================================================
# 5. Demo
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2608.06916 - MiCoPro")
    print(" Method: Mixed-Precision HW/SW Co-design")
    print("=" * 70)

    model_name = "Qwen/Qwen3-0.6B"
    fallback_name = "Qwen/Qwen2-0.5B"

    print(f"\n[1] Loading model...")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        print(f"  Loaded: {model_name}")
    except Exception as e:
        print(f"  Failed to load {model_name}: {e}")
        print(f"  Trying fallback: {fallback_name}")
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model = AutoModelForCausalLM.from_pretrained(
                fallback_name,
                torch_dtype=torch.float32,
                device_map="cpu",
                trust_remote_code=True,
            )
            tokenizer = AutoTokenizer.from_pretrained(fallback_name, trust_remote_code=True)
            print(f"  Loaded: {fallback_name}")
            model_name = fallback_name
        except Exception as e2:
            print(f"  Failed to load fallback: {e2}")
            print("  Running synthetic demo...")
            demo_synthetic()
            return

    # Collect all linear layers
    linear_layers = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            linear_layers.append((name, module))

    # Sample a subset for demo (first 12 layers)
    target_layers = linear_layers[:12]
    print(f"\n[2] Selected {len(target_layers)} linear layers for analysis")

    # Sensitivity analysis
    print(f"\n[3] Layer-wise sensitivity analysis")
    candidate_bits = [4, 6, 8, 16]
    layer_sensitivities = []
    layer_dims = []

    for name, layer in target_layers:
        w = layer.weight.data
        sensitivity = analyze_layer_sensitivity(w, candidate_bits)
        layer_sensitivities.append(sensitivity)
        layer_dims.append((w.shape[1], w.shape[0]))

        score = compute_sensitivity_score(sensitivity)
        print(f"  {name:50s} | Sensitivity: {score:.4f}")

    # Latency proxy
    proxy = LatencyProxy(base_latency_per_op=1e-9)

    # Compute uniform INT4 latency as baseline
    uniform_4_latency = proxy.estimate_model_latency(layer_dims, [4] * len(target_layers))
    uniform_8_latency = proxy.estimate_model_latency(layer_dims, [8] * len(target_layers))

    print(f"\n[4] Latency estimates")
    print(f"    Uniform INT4 latency: {uniform_4_latency * 1e6:.2f} us")
    print(f"    Uniform INT8 latency: {uniform_8_latency * 1e6:.2f} us")

    # Mixed-precision assignment under different budgets
    budgets = [
        uniform_4_latency * 1.2,  # 20% more than INT4
        uniform_4_latency * 1.5,  # 50% more than INT4
        uniform_8_latency * 0.8,  # 20% less than INT8
    ]

    print(f"\n[5] Mixed-precision assignment under latency budgets")
    for i, budget in enumerate(budgets):
        assignments = assign_mixed_precision(
            layer_sensitivities, layer_dims, budget, proxy, candidate_bits
        )

        latency = proxy.estimate_model_latency(layer_dims, assignments)
        avg_bits = np.mean(assignments)

        # Estimate weighted MSE
        total_mse = 0.0
        for j, bits in enumerate(assignments):
            mse = layer_sensitivities[j][bits]
            total_mse += mse
        avg_mse = total_mse / len(target_layers)

        print(f"\n  Budget {i+1}: {budget * 1e6:.2f} us")
        print(f"    Achieved latency: {latency * 1e6:.2f} us")
        print(f"    Avg bit-width: {avg_bits:.1f}")
        print(f"    Avg MSE: {avg_mse:.8f}")
        print(f"    Assignments: {assignments[:6]}... (showing first 6)")

    # Compare with uniform baselines
    print(f"\n[6] Comparison with uniform baselines")

    for uniform_bits in [4, 8, 16]:
        assignments = [uniform_bits] * len(target_layers)
        latency = proxy.estimate_model_latency(layer_dims, assignments)
        total_mse = sum(layer_sensitivities[j][uniform_bits] for j in range(len(target_layers)))
        avg_mse = total_mse / len(target_layers)

        print(f"  Uniform INT{uniform_bits:2d}: Latency={latency * 1e6:.2f} us, Avg MSE={avg_mse:.8f}")

    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(f"  Model: {model_name}")
    print(f"  MiCoPro demonstrates layer-wise sensitivity-aware")
    print(f"  mixed-precision assignment under hardware latency constraints.")
    print(f"  Different layers have different quantization sensitivity,")
    print(f"  enabling better accuracy-latency trade-offs than uniform precision.")
    print("=" * 70)


def demo_synthetic():
    """Synthetic demo."""
    print("\n[2] Running synthetic demo")

    torch.manual_seed(42)

    # Create synthetic layers with varying sensitivity
    n_layers = 8
    layer_dims = [(512, 512)] * n_layers
    layer_sensitivities = []

    for i in range(n_layers):
        # Simulate varying sensitivity
        sensitivity_factor = 0.5 + i * 0.1  # Layer 0 is least sensitive
        w = torch.randn(512, 512) * (1.0 + sensitivity_factor)

        sensitivity = {}
        for bits in [4, 6, 8, 16]:
            if bits >= 16:
                sensitivity[bits] = 0.0
            else:
                w_q = quantize_uniform(w, bits)
                sensitivity[bits] = compute_mse(w, w_q)
        layer_sensitivities.append(sensitivity)

    proxy = LatencyProxy()
    budget = proxy.estimate_model_latency(layer_dims, [4] * n_layers) * 1.3

    assignments = assign_mixed_precision(
        layer_sensitivities, layer_dims, budget, proxy
    )

    print(f"\n[3] Mixed-precision assignment")
    print(f"    Budget: {budget * 1e6:.2f} us")
    print(f"    Achieved: {proxy.estimate_model_latency(layer_dims, assignments) * 1e6:.2f} us")
    print(f"    Assignments: {assignments}")
    print(f"    Avg bits: {np.mean(assignments):.1f}")

    print("\n" + "=" * 70)
    print(" SUMMARY (Synthetic)")
    print("=" * 70)
    print("  Mixed-precision assigns higher bits to sensitive layers")
    print("  and lower bits to robust layers under latency budget.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
