"""
Utility Functions for MAB Pruning
==================================
Helper utilities for data loading, evaluation, and analysis.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
from pathlib import Path
import json


def compute_flops_reduction(
    original_config: Dict,
    pruned_config: Dict,
    seq_length: int = 512,
) -> Dict:
    """
    Compute FLOPs reduction after pruning.
    
    Args:
        original_config: Original model config dict
        pruned_config: Pruned model config dict
        seq_length: Input sequence length
        
    Returns:
        Dictionary with FLOPs analysis
    """
    # Original parameters
    orig_hidden = original_config.get("hidden_size", 1024)
    orig_intermediate = original_config.get("intermediate_size", 3072)
    orig_layers = original_config.get("num_hidden_layers", 28)
    orig_heads = original_config.get("num_attention_heads", 16)
    orig_kv_heads = original_config.get("num_key_value_heads", 8)
    head_dim = orig_hidden // orig_heads
    
    # Pruned parameters
    pruned_hidden = pruned_config.get("hidden_size", orig_hidden)
    pruned_intermediate = pruned_config.get("intermediate_size", orig_intermediate)
    pruned_layers = pruned_config.get("num_hidden_layers", orig_layers)
    pruned_heads = pruned_config.get("num_attention_heads", orig_heads)
    
    # Attention FLOPs per layer
    # Q/K/V projection + attention computation + O projection
    orig_attn_flops = (
        2 * seq_length * orig_hidden * (orig_heads + 2 * orig_kv_heads) * head_dim +  # QKV
        2 * seq_length * seq_length * orig_heads * head_dim +  # attention scores
        2 * seq_length * orig_heads * head_dim * orig_hidden  # O projection
    )
    pruned_attn_flops = (
        2 * seq_length * pruned_hidden * (pruned_heads + 2 * orig_kv_heads) * head_dim +
        2 * seq_length * seq_length * pruned_heads * head_dim +
        2 * seq_length * pruned_heads * head_dim * pruned_hidden
    )
    
    # FFN FLOPs per layer (SwiGLU: gate + up -> multiply -> down)
    # gate_proj: [hidden, intermediate]
    # up_proj: [hidden, intermediate]
    # down_proj: [intermediate, hidden]
    orig_ffn_flops = (
        2 * seq_length * orig_hidden * orig_intermediate +  # gate
        2 * seq_length * orig_hidden * orig_intermediate +  # up
        2 * seq_length * orig_intermediate * orig_hidden    # down
    )
    pruned_ffn_flops = (
        2 * seq_length * pruned_hidden * pruned_intermediate +
        2 * seq_length * pruned_hidden * pruned_intermediate +
        2 * seq_length * pruned_intermediate * pruned_hidden
    )
    
    # Total FLOPs
    orig_total = orig_layers * (orig_attn_flops + orig_ffn_flops)
    pruned_total = pruned_layers * (pruned_attn_flops + pruned_ffn_flops)
    
    return {
        "original_flops": orig_total,
        "pruned_flops": pruned_total,
        "flops_reduction": orig_total - pruned_total,
        "flops_reduction_pct": (orig_total - pruned_total) / orig_total * 100,
        "attention_flops_reduction_pct": (orig_attn_flops - pruned_attn_flops) / orig_attn_flops * 100,
        "ffn_flops_reduction_pct": (orig_ffn_flops - pruned_ffn_flops) / orig_ffn_flops * 100,
    }


def count_parameters(model: nn.Module) -> Tuple[int, int]:
    """
    Count total and trainable parameters in a model.
    
    Returns:
        (total_params, trainable_params)
    """
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def compare_models(original_model: nn.Module, pruned_model: nn.Module) -> Dict:
    """
    Compare original and pruned models.
    
    Returns:
        Comparison metrics dictionary
    """
    orig_total, orig_trainable = count_parameters(original_model)
    pruned_total, pruned_trainable = count_parameters(pruned_model)
    
    return {
        "original_params": orig_total,
        "pruned_params": pruned_total,
        "params_reduction": orig_total - pruned_total,
        "params_reduction_pct": (orig_total - pruned_total) / orig_total * 100,
        "original_trainable": orig_trainable,
        "pruned_trainable": pruned_trainable,
    }


def plot_pruning_results(
    results: Dict,
    save_path: Optional[str] = None,
):
    """
    Visualize pruning results.
    
    Args:
        results: Results dictionary from MABPruner.prune()
        save_path: Optional path to save the plot
    """
    scores = np.array(results["all_scores"])
    arm_names = results["arm_names"]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Score distribution
    axes[0].hist(scores, bins=50, alpha=0.7, edgecolor='black')
    axes[0].set_xlabel("Safe-Removal Score")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Distribution of Safe-Removal Scores")
    axes[0].axvline(np.mean(scores), color='r', linestyle='--', label=f'Mean: {np.mean(scores):.4f}')
    axes[0].legend()
    
    # Top-K scores
    top_k_scores = np.array(results["top_k_scores"])
    top_k_arms = results["top_k_arms"][:20]  # Show top 20
    y_pos = np.arange(len(top_k_arms))
    
    axes[1].barh(y_pos, top_k_scores[:20], alpha=0.7)
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(top_k_arms, fontsize=8)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Safe-Removal Score")
    axes[1].set_title(f"Top {len(top_k_arms)} Arms Selected for Pruning")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def load_pruning_metadata(metadata_path: str) -> Dict:
    """Load pruning metadata from JSON file."""
    with open(metadata_path, 'r') as f:
        return json.load(f)


def print_pruning_summary(results: Dict):
    """Print a formatted summary of pruning results."""
    print("\n" + "=" * 60)
    print("PRUNING SUMMARY")
    print("=" * 60)
    print(f"Policy: {results['policy'].upper()}")
    print(f"Total Arms: {results['num_arms']}")
    print(f"Play Budget: {results['play_budget']}")
    print(f"Top-K Selected: {results['top_k']}")
    print(f"\nTop 10 Arms to Prune:")
    for i, (arm, score) in enumerate(zip(results['top_k_arms'][:10], results['top_k_scores'][:10])):
        print(f"  {i+1:2d}. {arm}: {score:.4f}")
    print("=" * 60)
