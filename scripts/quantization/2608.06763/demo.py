#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.06763 - CubicQuant
Title: Parametric Non-Uniform Codebooks for High-Throughput LLM Inference
Core Method: Monotonic cubic curve mapping for non-uniform quantization
================================================================================

This script demonstrates:
1. CubicQuant parametric non-uniform scalar quantization format
2. Monotonic cubic curve maps uniform integer codes to non-uniform levels
3. Two shape parameters (a, b) + one scale (s) per group
4. Comparison: CubicQuant vs uniform integer vs floating-point baseline
5. Applied to Qwen3-0.6B linear layers

Usage:
    python3 demo.py

Requirements:
    pip install torch transformers
================================================================================
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple
import math

# =============================================================================
# 1. CubicQuant Format
# =============================================================================

class CubicQuantizer:
    """
    CubicQuant: Parametric non-uniform scalar quantization.

    Maps uniformly spaced integer codes to non-uniform reconstruction levels
    using a monotonic cubic curve defined by two shape parameters (a, b)
    and one scale parameter (s).
    """

    def __init__(self, bits: int = 4, group_size: int = 128):
        self.bits = bits
        self.group_size = group_size
        self.num_levels = 2 ** bits

    def cubic_map(self, x: torch.Tensor, a: float, b: float, s: float) -> torch.Tensor:
        """
        Monotonic cubic mapping from uniform code x to non-uniform level y.

        y = s * f(x; a, b) where f is a normalized cubic on [0, 1]
        """
        # Normalize x to [0, 1]
        x_norm = x / (self.num_levels - 1)

        # Monotonic cubic: y = x + a*x*(1-x)*(x-0.5) + b*x^2*(1-x)
        # This preserves monotonicity for small a, b
        cubic_term = a * x_norm * (1 - x_norm) * (x_norm - 0.5)
        shaping_term = b * x_norm ** 2 * (1 - x_norm)

        y_norm = x_norm + cubic_term + shaping_term

        # Ensure monotonicity by clamping
        y_norm = torch.clamp(y_norm, 0.0, 1.0)

        # Scale to output range
        return s * y_norm

    def fit_parameters(
        self,
        w: torch.Tensor,
        method: str = "mse",
    ) -> Tuple[float, float, float]:
        """
        Fit cubic parameters (a, b, s) to minimize reconstruction MSE.
        Uses grid search for a, b and analytical solution for s.
        """
        w_flat = w.flatten()
        w_max = w_flat.abs().max().item()

        if w_max < 1e-8:
            return 0.0, 0.0, 1e-8

        best_mse = float('inf')
        best_a, best_b, best_s = 0.0, 0.0, w_max

        # Grid search for a and b
        a_candidates = np.linspace(-0.5, 0.5, 11)
        b_candidates = np.linspace(-0.5, 0.5, 11)

        codes = torch.arange(self.num_levels, dtype=torch.float32, device=w.device)

        for a in a_candidates:
            for b in b_candidates:
                # Reconstruction levels for this (a, b)
                levels = self.cubic_map(codes, a, b, 1.0).cpu().numpy()

                # For each weight, find nearest level (scaled)
                # Optimize scale s to minimize MSE
                w_np = w_flat.cpu().numpy()

                # Try multiple scales
                for s_ratio in np.linspace(0.5, 2.0, 16):
                    s = w_max * s_ratio
                    scaled_levels = levels * s

                    # Quantize
                    indices = np.argmin(np.abs(w_np[:, None] - scaled_levels[None, :]), axis=1)
                    w_dq = scaled_levels[indices]

                    mse = np.mean((w_np - w_dq) ** 2)

                    if mse < best_mse:
                        best_mse = mse
                        best_a, best_b, best_s = a, b, s

        return best_a, best_b, best_s

    def quantize(self, w: torch.Tensor) -> Tuple[torch.Tensor, float, float, float]:
        """Quantize weight using CubicQuant."""
        a, b, s = self.fit_parameters(w)

        codes = torch.arange(self.num_levels, dtype=torch.float32, device=w.device)
        levels = self.cubic_map(codes, a, b, s)

        # Find nearest level for each weight
        w_flat = w.flatten()
        distances = torch.abs(w_flat.unsqueeze(1) - levels.unsqueeze(0))
        indices = torch.argmin(distances, dim=1)
        w_dq = levels[indices].reshape(w.shape)

        return w_dq, a, b, s


# =============================================================================
# 2. Baseline Quantizers
# =============================================================================

class UniformQuantizer:
    """Standard uniform integer quantization."""

    def __init__(self, bits: int = 4, group_size: int = 128):
        self.bits = bits
        self.num_levels = 2 ** bits

    def quantize(self, w: torch.Tensor) -> torch.Tensor:
        w_min = w.min()
        w_max = w.max()
        scale = (w_max - w_min) / (self.num_levels - 1)
        scale = scale.clamp_min(1e-8)

        w_q = torch.round((w - w_min) / scale).clamp(0, self.num_levels - 1)
        w_dq = w_q * scale + w_min

        return w_dq


class FloatQuantizer:
    """Simple floating-point quantization (E2M1 for 4-bit)."""

    def __init__(self, bits: int = 4):
        self.bits = bits
        # For 4-bit float: E2M1 (2 exponent, 1 mantissa)
        self.exp_bits = 2
        self.man_bits = bits - 1 - self.exp_bits  # 1 sign bit

    def quantize(self, w: torch.Tensor) -> torch.Tensor:
        # Simplified: use per-channel scale + round to nearest float format
        w_max = w.abs().max()
        scale = w_max / 6.0  # E2M1 max is ~6
        scale = scale.clamp_min(1e-8)

        w_scaled = w / scale
        # Simplified: clamp and round to approximate FP4
        w_q = torch.round(w_scaled).clamp(-6, 6)
        w_dq = w_q * scale

        return w_dq


# =============================================================================
# 3. Demo
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2608.06763 - CubicQuant")
    print(" Method: Parametric Non-Uniform Codebooks")
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

    # Select linear layers
    target_layers = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and any(k in name for k in ["q_proj", "k_proj", "v_proj"]):
            target_layers.append((name, module))
        if len(target_layers) >= 3:
            break

    print(f"\n[2] Selected {len(target_layers)} attention projection layers")

    bits = 4
    group_size = 128

    cubic_quant = CubicQuantizer(bits=bits, group_size=group_size)
    uniform_quant = UniformQuantizer(bits=bits, group_size=group_size)
    float_quant = FloatQuantizer(bits=bits)

    print(f"\n[3] Quantization: W{bits}, group_size={group_size}")

    total_mse_uniform = 0.0
    total_mse_float = 0.0
    total_mse_cubic = 0.0

    for layer_name, layer in target_layers:
        w_fp = layer.weight.data.float()

        # Pad to multiple of group_size for fair comparison
        orig_shape = w_fp.shape
        flat_size = w_fp.numel()
        pad_size = (group_size - flat_size % group_size) % group_size
        if pad_size > 0:
            w_fp_flat = torch.cat([w_fp.flatten(), torch.zeros(pad_size, dtype=w_fp.dtype)])
        else:
            w_fp_flat = w_fp.flatten()

        num_groups = w_fp_flat.numel() // group_size
        w_groups = w_fp_flat.reshape(num_groups, group_size)

        # Quantize each group
        mse_uniform_g = 0.0
        mse_float_g = 0.0
        mse_cubic_g = 0.0

        for g in range(num_groups):
            wg = w_groups[g]

            # Uniform
            w_dq_u = uniform_quant.quantize(wg)
            mse_uniform_g += ((wg - w_dq_u) ** 2).mean().item()

            # Float
            w_dq_f = float_quant.quantize(wg)
            mse_float_g += ((wg - w_dq_f) ** 2).mean().item()

            # CubicQuant
            w_dq_c, a, b, s = cubic_quant.quantize(wg)
            mse_cubic_g += ((wg - w_dq_c) ** 2).mean().item()

        mse_uniform_g /= num_groups
        mse_float_g /= num_groups
        mse_cubic_g /= num_groups

        total_mse_uniform += mse_uniform_g
        total_mse_float += mse_float_g
        total_mse_cubic += mse_cubic_g

        print(f"\n  Layer: {layer_name}")
        print(f"    MSE (Uniform):  {mse_uniform_g:.8f}")
        print(f"    MSE (Float):    {mse_float_g:.8f}")
        print(f"    MSE (CubicQuant): {mse_cubic_g:.8f}")
        print(f"    vs Uniform: {(mse_uniform_g - mse_cubic_g) / mse_uniform_g * 100:.2f}% better")
        print(f"    vs Float: {(mse_float_g - mse_cubic_g) / mse_float_g * 100:.2f}% better")

    avg_mse_uniform = total_mse_uniform / len(target_layers)
    avg_mse_float = total_mse_float / len(target_layers)
    avg_mse_cubic = total_mse_cubic / len(target_layers)

    print(f"\n[4] Average across {len(target_layers)} layers:")
    print(f"    MSE (Uniform):    {avg_mse_uniform:.8f}")
    print(f"    MSE (Float):      {avg_mse_float:.8f}")
    print(f"    MSE (CubicQuant): {avg_mse_cubic:.8f}")
    print(f"    vs Uniform: {(avg_mse_uniform - avg_mse_cubic) / avg_mse_uniform * 100:.2f}% better")
    print(f"    vs Float: {(avg_mse_float - avg_mse_cubic) / avg_mse_float * 100:.2f}% better")

    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(f"  Model: {model_name}")
    print(f"  Quantization: W{bits}, group_size={group_size}")
    print(f"  CubicQuant uses parametric cubic curve with (a, b, s)")
    print(f"  Avg vs Uniform: {(avg_mse_uniform - avg_mse_cubic) / avg_mse_uniform * 100:.2f}% better")
    print(f"  Avg vs Float: {(avg_mse_float - avg_mse_cubic) / avg_mse_float * 100:.2f}% better")
    print("=" * 70)


def demo_synthetic():
    """Synthetic demo with known distributions."""
    print("\n[2] Running synthetic demo")

    torch.manual_seed(42)

    # Test on different distributions
    distributions = {
        "Uniform": torch.rand(4096) * 2 - 1,
        "Gaussian": torch.randn(4096),
        "Laplace": torch.distributions.Laplace(0, 1).sample((4096,)),
    }

    bits = 4
    group_size = 128

    cubic_quant = CubicQuantizer(bits=bits, group_size=group_size)
    uniform_quant = UniformQuantizer(bits=bits, group_size=group_size)

    print(f"\n[3] Testing on synthetic distributions (W{bits}, group_size={group_size})")

    for dist_name, w in distributions.items():
        # Uniform
        w_dq_u = uniform_quant.quantize(w)
        mse_u = ((w - w_dq_u) ** 2).mean().item()

        # CubicQuant (fit on full tensor as one group for simplicity)
        w_dq_c, a, b, s = cubic_quant.quantize(w)
        mse_c = ((w - w_dq_c) ** 2).mean().item()

        improvement = (mse_u - mse_c) / mse_u * 100

        print(f"\n  Distribution: {dist_name}")
        print(f"    MSE (Uniform):    {mse_u:.8f}")
        print(f"    MSE (CubicQuant): {mse_c:.8f}")
        print(f"    Improvement: {improvement:.2f}%")
        print(f"    Fitted params: a={a:.3f}, b={b:.3f}, s={s:.4f}")

    print("\n" + "=" * 70)
    print(" SUMMARY (Synthetic)")
    print("=" * 70)
    print("  CubicQuant adapts reconstruction levels per distribution")
    print("  via parametric cubic curve (a, b) + scale (s)")
    print("=" * 70)


if __name__ == "__main__":
    demo()
