#!/usr/bin/env python3
"""
LightRot: A Light-Weighted Rotation Scheme for Accurate Low-Bit LLM Inference
=============================================================================
Paper: arXiv:2607.27704
Title:  LightRot: A Light-Weighted Rotation Scheme and Architecture for
        Accurate Low-Bit Large Language Model Inference

Core Methods:
  1. GLR (Grouped Local Rotation):
     Divide channels into local groups (e.g. group_size=128) and apply
     Hadamard rotation within each group instead of globally. This reduces
     rotation complexity from O(N^2) to O(g^2).

  2. ODA (Outlier Direction Aligning):
     Permute outlier channels to the all-ones row position of the Hadamard
     matrix. The all-ones row sums all elements, so the outlier is evenly
     dispersed to all channels in the group after rotation.

  3. Hierarchical FHT (Fast Hadamard Transform):
     For non-power-of-2 dimensions, decompose into power-of-2 sub-blocks
     and apply FHT (O(N log N)) to each block independently.

  4. 4-bit symmetric per-group quantization after rotation:
     x_hat = clip(round(x/s), qmin, qmax),  s = max(|x_group|) / (2^(b-1)-1)

  5. R1/R2 rotation matrices are merged offline with weights;
     R3/R4 are applied online using only additions (Hadamard has +/-1 entries).

Target Model: Qwen3-0.6B (falls back to MockTransformer if unavailable).
"""

import sys
import math
from pathlib import Path

import torch
import torch.nn as nn

# Import shared toolkit from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from quantization_toolkit import (
    hadamard_matrix,
    fast_hadamard_transform,
    hierarchical_hadamard,
    load_model_or_mock,
    symmetric_group_quantize,
    quantization_error_metrics,
)


# =============================================================================
# Core Algorithm: LightRot Quantizer
# =============================================================================

class LightRotQuantizer:
    """
    LightRot: GLR + ODA + 4-bit symmetric per-group quantization.

    Pipeline per weight matrix W [out_features, in_features]:
      1. Find outlier channels by column L2 norm.
      2. ODA: permute outliers to the all-ones-column (index 0) of each group.
      3. GLR: apply normalized Hadamard rotation within each group.
      4. Symmetric 4-bit quantize the rotated weights.
    """

    def __init__(self, bits: int = 4, group_size: int = 128,
                 outlier_ratio: float = 0.01):
        self.bits = bits
        self.group_size = group_size
        self.outlier_ratio = outlier_ratio
        # Precompute Hadamard matrix for the group size (if power of 2)
        if (group_size & (group_size - 1)) == 0:
            self._H = hadamard_matrix(group_size, normalize=True)
        else:
            self._H = hierarchical_hadamard(group_size)

    # ---- Step 1: Outlier Detection ----

    def find_outliers(self, weight: torch.Tensor) -> torch.Tensor:
        """
        Identify outlier channel indices by column L2 norm.
        Returns sorted indices of the top-k outlier columns.
        """
        n_in = weight.shape[1]
        col_norms = weight.pow(2).sum(dim=0).sqrt()  # [in_features]
        n_groups = math.ceil(n_in / self.group_size)
        # One outlier per group (at minimum)
        n_outliers = max(1, min(n_groups, int(n_in * self.outlier_ratio)))
        n_outliers = min(n_outliers, n_in)
        _, idx = torch.topk(col_norms, n_outliers)
        return idx.sort().values

    # ---- Step 2: ODA Permutation ----

    def oda_permutation(self, weight: torch.Tensor) -> torch.Tensor:
        """
        Outlier Direction Aligning: build a permutation that places each
        outlier channel at position 0 (all-ones column) of its group.

        The all-ones column of the Hadamard matrix ensures the outlier's
        energy is added uniformly to every output channel after rotation,
        producing the flattest possible distribution.
        """
        n_in = weight.shape[1]
        outliers = self.find_outliers(weight)
        outlier_set = set(outliers.tolist())

        non_outliers = [i for i in range(n_in) if i not in outlier_set]
        outliers_sorted = list(outliers.tolist())

        perm = []
        oi, ni = 0, 0  # pointers into outliers / non_outliers
        n_groups = math.ceil(n_in / self.group_size)

        for g in range(n_groups):
            start = g * self.group_size
            end = min(start + self.group_size, n_in)
            gs = end - start  # actual group size

            # Place one outlier at position 0 (all-ones column) of this group
            if oi < len(outliers_sorted):
                perm.append(outliers_sorted[oi])
                oi += 1
                fill_start = 1
            else:
                fill_start = 0

            # Fill remaining positions with non-outlier channels
            for _ in range(fill_start, gs):
                if ni < len(non_outliers):
                    perm.append(non_outliers[ni])
                    ni += 1
                else:
                    perm.append(0)  # safety fallback

        return torch.tensor(perm[:n_in], dtype=torch.long)

    # ---- Step 3: GLR (Grouped Local Rotation) ----

    def apply_glr(self, weight: torch.Tensor,
                  perm: torch.Tensor) -> torch.Tensor:
        """
        Apply Grouped Local Rotation: permute columns then rotate each group
        with the (normalized) Hadamard matrix.

        weight: [out_features, in_features]
        Returns rotated weight of the same shape.
        """
        w = weight[:, perm]  # ODA permutation
        n_in = w.shape[1]
        n_full_groups = n_in // self.group_size
        remainder = n_in % self.group_size

        H = self._H  # [group_size, group_size], orthogonal
        w_rot = w.clone()

        # Rotate each full group: W[:, g*gs:(g+1)*gs] @ H
        if n_full_groups > 0:
            w_full = w[:, :n_full_groups * self.group_size]
            w_full = w_full.reshape(
                w.shape[0], n_full_groups, self.group_size
            )
            w_rot_full = torch.matmul(w_full, H)  # broadcast
            w_rot[:, :n_full_groups * self.group_size] = \
                w_rot_full.reshape(w.shape[0], -1)

        # Handle remainder with hierarchical Hadamard
        if remainder > 0:
            H_rem = hierarchical_hadamard(remainder)
            w_rot[:, n_full_groups * self.group_size:] = \
                torch.matmul(w[:, n_full_groups * self.group_size:], H_rem)

        return w_rot

    # ---- Full pipeline ----

    def quantize_weight(self, weight: torch.Tensor):
        """
        Full LightRot pipeline: ODA -> GLR -> 4-bit symmetric quantization.

        Returns:
            w_rotated:  the rotated weight (before quantization)
            w_quantized: the fake-quantized rotated weight
            perm:        the ODA permutation indices
        """
        perm = self.oda_permutation(weight)
        w_rotated = self.apply_glr(weight, perm)
        w_quantized = symmetric_group_quantize(
            w_rotated, bits=self.bits, group_size=self.group_size
        )
        return w_rotated, w_quantized, perm


# =============================================================================
# FHT Verification
# =============================================================================

def verify_fht():
    """Verify that FHT produces the same result as matrix multiplication."""
    print("\n--- FHT Verification ---")
    n = 128
    x = torch.randn(4, n)
    H = hadamard_matrix(n, normalize=True)

    # Matrix multiplication
    y_mat = torch.matmul(x, H)
    # Fast Hadamard Transform
    y_fht = fast_hadamard_transform(x, dim=-1)

    max_diff = (y_mat - y_fht).abs().max().item()
    print(f"  Matrix size: {n}x{n}")
    print(f"  Max |y_mat - y_fht|: {max_diff:.2e}")
    print(f"  FHT matches matrix multiply: {max_diff < 1e-5}")

    # Timing comparison (conceptual)
    print(f"  Matrix multiply ops: O(N^2) = {n*n}")
    print(f"  FHT butterfly ops:   O(N log N) = {n * int(math.log2(n))}")
    print("---\n")


# =============================================================================
# Main Demo
# =============================================================================

def main():
    print("=" * 70)
    print("LightRot: GLR + ODA + 4-bit Symmetric Quantization")
    print("Paper: arXiv:2607.27704")
    print("=" * 70)

    device = "cpu"

    # Verify FHT first
    verify_fht()

    # Load model
    print("Loading model...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)

    quantizer = LightRotQuantizer(bits=4, group_size=128, outlier_ratio=0.01)

    model_type = "MOCK" if is_mock else "REAL"
    print(f"\nModel: {info['name']} ({model_type})")
    print(f"Quantization: {quantizer.bits}-bit symmetric, "
          f"group_size={quantizer.group_size}")

    # Collect per-layer results
    layer_results = []
    total_params = 0
    total_no_rot_sq = 0.0
    total_glr_sq = 0.0
    total_oda_sq = 0.0

    for name, module in model.named_modules():
        if not isinstance(module, nn.Linear):
            continue

        w = module.weight.data.float()
        if w.numel() == 0:
            continue
        n_params = w.numel()
        total_params += n_params

        # --- Baseline: no rotation, 4-bit symmetric quant ---
        w_q_baseline = symmetric_group_quantize(
            w, bits=4, group_size=quantizer.group_size
        )
        m_base = quantization_error_metrics(w, w_q_baseline)

        # --- GLR only (random permutation, no ODA) ---
        random_perm = torch.randperm(w.shape[1])
        w_glr = quantizer.apply_glr(w, random_perm)
        w_q_glr = symmetric_group_quantize(
            w_glr, bits=4, group_size=quantizer.group_size
        )
        m_glr = quantization_error_metrics(w_glr, w_q_glr)

        # --- LightRot: ODA + GLR + 4-bit quant ---
        w_rot, w_q_rot, oda_perm = quantizer.quantize_weight(w)
        m_oda = quantization_error_metrics(w_rot, w_q_rot)

        total_no_rot_sq += m_base["mse"] * n_params
        total_glr_sq += m_glr["mse"] * n_params
        total_oda_sq += m_oda["mse"] * n_params

        layer_results.append({
            "name": name,
            "shape": tuple(w.shape),
            "n_params": n_params,
            "no_rot_mse": m_base["mse"],
            "glr_mse": m_glr["mse"],
            "oda_mse": m_oda["mse"],
            "no_rot_cos": m_base["cosine_similarity"],
            "oda_cos": m_oda["cosine_similarity"],
        })

    # Print per-layer table
    header = (f"{'Layer':<45} {'Shape':<14} {'NoRot MSE':>11} "
              f"{'GLR MSE':>11} {'ODA MSE':>11} {'Improv%':>8}")
    print(f"\n{header}")
    print("-" * len(header))
    for r in layer_results[:20]:
        imp = (1.0 - r["oda_mse"] / max(r["no_rot_mse"], 1e-12)) * 100
        print(f"{r['name']:<45} {str(r['shape']):<14} "
              f"{r['no_rot_mse']:>11.6f} {r['glr_mse']:>11.6f} "
              f"{r['oda_mse']:>11.6f} {imp:>+7.1f}%")
    if len(layer_results) > 20:
        print(f"  ... ({len(layer_results) - 20} more layers)")

    # Summary
    avg_no_rot = total_no_rot_sq / max(total_params, 1)
    avg_glr = total_glr_sq / max(total_params, 1)
    avg_oda = total_oda_sq / max(total_params, 1)

    print(f"\n{'=' * 70}")
    print("Summary")
    print(f"{'=' * 70}")
    print(f"  Total layers quantized : {len(layer_results)}")
    print(f"  Total parameters       : {total_params:,}")
    print(f"  Avg MSE (no rotation)  : {avg_no_rot:.8f}")
    print(f"  Avg MSE (GLR only)    : {avg_glr:.8f}")
    print(f"  Avg MSE (GLR + ODA)   : {avg_oda:.8f}")
    if avg_no_rot > 0:
        print(f"  GLR improvement        : "
              f"{(1 - avg_glr / avg_no_rot) * 100:+.1f}%")
        print(f"  GLR+ODA improvement    : "
              f"{(1 - avg_oda / avg_no_rot) * 100:+.1f}%")
    print()
    print("  Key insights:")
    print("  - GLR reduces rotation complexity from O(N^2) to O(g^2)")
    print("  - ODA aligns outliers to the Hadamard all-ones column,")
    print("    uniformly dispersing their energy across all channels")
    print("  - FHT (O(N log N)) replaces matrix multiply for online rotation")
    print("  - R1/R2 merged offline with weights; R3/R4 online (additions only)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
