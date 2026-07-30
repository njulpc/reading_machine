"""
GSQ Utilities
=============
Evaluation and analysis utilities for GSQ quantization.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple


def compute_quantization_metrics(original_weight: torch.Tensor, quantized_weight: torch.Tensor) -> Dict:
    """
    Compute metrics for quantization quality.
    
    Returns:
        Dictionary with MSE, relative error, SNR, etc.
    """
    diff = original_weight - quantized_weight
    mse = (diff ** 2).mean().item()
    rmse = np.sqrt(mse)
    
    orig_norm = torch.norm(original_weight).item()
    rel_error = rmse / orig_norm if orig_norm > 0 else float('inf')
    
    # Signal-to-noise ratio
    signal_power = (original_weight ** 2).mean().item()
    noise_power = mse
    snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
    
    # Compression ratio
    orig_bits = 16  # FP16
    # Estimate quantized bits (approximate)
    unique_vals = torch.unique(quantized_weight).numel()
    quant_bits = np.ceil(np.log2(unique_vals)) if unique_vals > 1 else 1
    
    return {
        "mse": mse,
        "rmse": rmse,
        "relative_error": rel_error,
        "snr_db": snr,
        "unique_values": unique_vals,
        "estimated_bits": quant_bits,
        "compression_ratio": orig_bits / quant_bits if quant_bits > 0 else 1.0,
    }


def count_parameters(model: nn.Module) -> Tuple[int, int]:
    """Count total and trainable parameters."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def estimate_model_size(model: nn.Module, bits_per_param: float = 16.0) -> Dict:
    """
    Estimate model size in memory.
    
    Args:
        model: PyTorch model
        bits_per_param: Bits per parameter (16 for FP16, 2 for 2-bit, etc.)
        
    Returns:
        Size estimates in bytes, MB, GB
    """
    total_params, _ = count_parameters(model)
    bytes_per_param = bits_per_param / 8
    total_bytes = total_params * bytes_per_param
    
    return {
        "parameters": total_params,
        "bits_per_param": bits_per_param,
        "total_bytes": total_bytes,
        "total_mb": total_bytes / (1024 ** 2),
        "total_gb": total_bytes / (1024 ** 3),
    }


def compare_model_sizes(original_model: nn.Module, quantized_model: nn.Module, quant_bits: float) -> Dict:
    """Compare sizes of original and quantized models."""
    orig_size = estimate_model_size(original_model, bits_per_param=16.0)
    quant_size = estimate_model_size(quantized_model, bits_per_param=quant_bits)
    
    return {
        "original_mb": orig_size["total_mb"],
        "quantized_mb": quant_size["total_mb"],
        "reduction_mb": orig_size["total_mb"] - quant_size["total_mb"],
        "reduction_pct": (1 - quant_size["total_mb"] / orig_size["total_mb"]) * 100,
        "compression_ratio": orig_size["total_mb"] / quant_size["total_mb"],
    }


def analyze_weight_distribution(weight: torch.Tensor, title: str = "Weight Distribution"):
    """Print statistics about weight distribution."""
    w = weight.flatten()
    print(f"\n{title}:")
    print(f"  Shape: {tuple(weight.shape)}")
    print(f"  Mean: {w.mean().item():.6f}")
    print(f"  Std: {w.std().item():.6f}")
    print(f"  Min: {w.min().item():.6f}")
    print(f"  Max: {w.max().item():.6f}")
    print(f"  Abs Mean: {w.abs().mean().item():.6f}")
    print(f"  Sparsity (% zero): {(w == 0).float().mean().item() * 100:.2f}%")
    print(f"  Unique values: {torch.unique(w).numel()}")
