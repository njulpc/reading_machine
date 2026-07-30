"""
CAT-Q Utilities
===============
Evaluation and analysis utilities for ternary quantization.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple


def compute_ternary_metrics(original_weight: torch.Tensor, ternary_weight: torch.Tensor) -> Dict:
    """
    Compute metrics for ternary quantization quality.
    
    Returns:
        Dictionary with MSE, sparsity, ternary ratio, etc.
    """
    diff = original_weight - ternary_weight
    mse = (diff ** 2).mean().item()
    rmse = np.sqrt(mse)
    
    # Sparsity (% zeros)
    sparsity = (ternary_weight == 0).float().mean().item() * 100
    
    # Distribution of ternary values
    t_flat = ternary_weight.flatten()
    n_neg1 = (t_flat == -1).float().mean().item() * 100
    n_zero = (t_flat == 0).float().mean().item() * 100
    n_pos1 = (t_flat == 1).float().mean().item() * 100
    
    # Signal-to-noise ratio
    signal_power = (original_weight ** 2).mean().item()
    snr = 10 * np.log10(signal_power / mse) if mse > 0 else float('inf')
    
    # Compression ratio (FP16 → 1.58-bit ternary)
    # Ternary needs ~1.58 bits per weight + scale
    compression_ratio = 16 / 1.58
    
    return {
        "mse": mse,
        "rmse": rmse,
        "snr_db": snr,
        "sparsity_pct": sparsity,
        "pct_minus_1": n_neg1,
        "pct_zero": n_zero,
        "pct_plus_1": n_pos1,
        "compression_ratio": compression_ratio,
    }


def count_parameters(model: nn.Module) -> Tuple[int, int]:
    """Count total and trainable parameters."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def estimate_model_size(model: nn.Module, bits_per_param: float = 16.0) -> Dict:
    """Estimate model size in memory."""
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


def compare_model_sizes(original_model: nn.Module, quantized_model: nn.Module) -> Dict:
    """Compare original FP16 vs ternary model sizes."""
    orig_size = estimate_model_size(original_model, bits_per_param=16.0)
    # Ternary: ~1.58 bits per weight + overhead for scales
    quant_size = estimate_model_size(quantized_model, bits_per_param=1.58)
    
    return {
        "original_mb": orig_size["total_mb"],
        "ternary_mb": quant_size["total_mb"],
        "reduction_mb": orig_size["total_mb"] - quant_size["total_mb"],
        "reduction_pct": (1 - quant_size["total_mb"] / orig_size["total_mb"]) * 100,
        "compression_ratio": orig_size["total_mb"] / quant_size["total_mb"],
    }


def analyze_ternary_distribution(weight: torch.Tensor, title: str = "Ternary Distribution"):
    """Print statistics about ternary weight distribution."""
    w = weight.flatten()
    print(f"\n{title}:")
    print(f"  Shape: {tuple(weight.shape)}")
    print(f"  Total elements: {w.numel()}")
    print(f"  -1: {(w == -1).sum().item()} ({(w == -1).float().mean().item()*100:.2f}%)")
    print(f"   0: {(w == 0).sum().item()} ({(w == 0).float().mean().item()*100:.2f}%)")
    print(f"  +1: {(w == 1).sum().item()} ({(w == 1).float().mean().item()*100:.2f}%)")
    print(f"  Sparsity: {(w == 0).float().mean().item()*100:.2f}%")
