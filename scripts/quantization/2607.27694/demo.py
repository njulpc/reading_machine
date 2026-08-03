#!/usr/bin/env python3
"""
GyRot: Leveraging Hidden Synergy between Rotation and Fine-grained
       Group Quantization for Low-bit LLM Inference
=============================================================================
Paper: arXiv:2607.27694

Core Methods:
  1. CoRFiG (Coarse Rotation, Fine Grouping):
     Perform rotation over a larger range (G_rot=128) than the quantization
     group (G_quant=32). Outliers are dispersed at the inter-group scale,
     while intra-group local variance is preserved. This resolves the
     conflict between rotation (global) and fine-grained grouping (local).

  2. HAP (Harmonic-Aligned Permutation):
     Map outlier channels to Hadamard matrix harmonic rows so that rotated
     outliers are dispersed in a pattern aligned with quantization group
     boundaries. More general than ODA (which uses only the all-ones row).

  3. Asymmetric quantization with zero-point:
     x_hat = clip(round(x/s) + z, qmin, qmax)
     s = (max - min) / (2^b - 1),  z = round(-min / s)

  4. Zero-point rounding strategy:
     Round z to the nearest integer to eliminate truncation error and
     enable fully-integer dequantization.

  5. Inner product reconstruction:
     y ≈ Σ_g s_x^(g) * s_w^(g) * Σ_i (x_hat_i - z_x^(g)) * w_hat_i

  6. INT4 fine-grained group quantization with group_size=32.

Target Model: Qwen3-0.6B (falls back to MockTransformer if unavailable).
"""

import sys
import math
from pathlib import Path

import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).parent.parent))
from quantization_toolkit import (
    hadamard_matrix,
    hierarchical_hadamard,
    load_model_or_mock,
    asymmetric_group_quantize,
    symmetric_group_quantize,
    quantization_error_metrics,
)


# =============================================================================
# Core Algorithm: GyRot Quantizer
# =============================================================================

class GyRotQuantizer:
    """
    GyRot: CoRFiG + HAP + asymmetric INT4 fine-grained group quantization.

    Key innovation: rotation range (G_rot) > quantization group (G_quant).
    This turns the rotation-grouping conflict into synergy.
    """

    def __init__(self, bits: int = 4, quant_group_size: int = 32,
                 rot_group_size: int = 128, outlier_ratio: float = 0.01):
        self.bits = bits
        self.quant_group_size = quant_group_size  # G_quant = 32
        self.rot_group_size = rot_group_size      # G_rot = 128
        self.outlier_ratio = outlier_ratio

        assert rot_group_size >= quant_group_size, \
            "CoRFiG requires G_rot >= G_quant"
        assert rot_group_size % quant_group_size == 0, \
            "G_rot must be a multiple of G_quant"

        # Precompute rotation Hadamard
        if (rot_group_size & (rot_group_size - 1)) == 0:
            self._H_rot = hadamard_matrix(rot_group_size, normalize=True)
        else:
            self._H_rot = hierarchical_hadamard(rot_group_size)

        self._n_quant_per_rot = rot_group_size // quant_group_size

    # ---- Step 1: Outlier Detection ----

    def find_outliers(self, weight: torch.Tensor) -> torch.Tensor:
        """Find outlier channel indices by column L2 norm."""
        n_in = weight.shape[1]
        col_norms = weight.pow(2).sum(dim=0).sqrt()
        n_rot_groups = math.ceil(n_in / self.rot_group_size)
        # Multiple outliers per rotation group (distribute across harmonics)
        n_outliers = max(1, min(
            n_rot_groups * self._n_quant_per_rot,
            int(n_in * self.outlier_ratio * self._n_quant_per_rot)
        ))
        n_outliers = min(n_outliers, n_in)
        _, idx = torch.topk(col_norms, n_outliers)
        return idx.sort().values

    # ---- Step 2: HAP Permutation ----

    def hap_permutation(self, weight: torch.Tensor) -> torch.Tensor:
        """
        Harmonic-Aligned Permutation: distribute outlier channels across
        harmonic positions within each rotation group.

        Unlike ODA (which places all outliers at the all-ones column), HAP
        spreads outliers across multiple Hadamard frequency columns. This
        aligns the outlier dispersion pattern with quantization group
        boundaries (G_quant sub-blocks within G_rot).
        """
        n_in = weight.shape[1]
        outliers = self.find_outliers(weight)
        outlier_list = list(outliers.tolist())
        outlier_set = set(outlier_list)
        non_outliers = [i for i in range(n_in) if i not in outlier_set]

        # Harmonic positions within each rotation group:
        # Place outliers at the start of each quant sub-group (every G_quant channels).
        # These correspond to different Hadamard frequency bands.
        harmonic_offsets = [
            q * self.quant_group_size for q in range(self._n_quant_per_rot)
        ]

        perm = []
        oi, ni = 0, 0
        n_rot_groups = math.ceil(n_in / self.rot_group_size)

        for g in range(n_rot_groups):
            start = g * self.rot_group_size
            end = min(start + self.rot_group_size, n_in)
            gs = end - start

            # Initialize group with non-outliers
            group_perm = list(range(start, end))

            # Place outliers at harmonic positions
            for offset in harmonic_offsets:
                if offset < gs and oi < len(outlier_list):
                    # Replace the channel at this position with an outlier
                    group_perm[offset] = outlier_list[oi]
                    oi += 1

            # Fill remaining positions with non-outliers
            used = set()
            for offset in harmonic_offsets:
                if offset < gs:
                    used.add(offset)
            ni_local = 0
            for j in range(gs):
                if j not in used:
                    if ni + ni_local < len(non_outliers):
                        group_perm[j] = non_outliers[ni + ni_local]
                        ni_local += 1
            ni += ni_local

            perm.extend(group_perm[:gs])

        return torch.tensor(perm[:n_in], dtype=torch.long)

    # ---- Step 3: CoRFiG Rotation ----

    def apply_corfig_rotation(self, weight: torch.Tensor,
                               perm: torch.Tensor) -> torch.Tensor:
        """
        CoRFiG: rotate over G_rot-sized groups (coarse), while quantization
        will use G_quant-sized sub-groups (fine) within each rotation group.
        """
        w = weight[:, perm]
        n_in = w.shape[1]
        n_full = n_in // self.rot_group_size
        remainder = n_in % self.rot_group_size

        H = self._H_rot
        w_rot = w.clone()

        if n_full > 0:
            w_full = w[:, :n_full * self.rot_group_size]
            w_full = w_full.reshape(
                w.shape[0], n_full, self.rot_group_size
            )
            w_rot_full = torch.matmul(w_full, H)
            w_rot[:, :n_full * self.rot_group_size] = \
                w_rot_full.reshape(w.shape[0], -1)

        if remainder > 0:
            H_rem = hierarchical_hadamard(remainder)
            start = n_full * self.rot_group_size
            w_rot[:, start:] = torch.matmul(w[:, start:], H_rem)

        return w_rot

    # ---- Step 4: Asymmetric Quantization with Zero-point Rounding ----

    def quantize_asymmetric(self, x: torch.Tensor):
        """
        Asymmetric INT4 per-group quantization with zero-point rounding.
        Group size = G_quant (32).

        Returns (dequantized, scales, zeros).
        """
        return asymmetric_group_quantize(
            x, bits=self.bits, group_size=self.quant_group_size
        )

    # ---- Full pipeline ----

    def quantize_weight(self, weight: torch.Tensor):
        """
        Full GyRot pipeline: HAP -> CoRFiG rotation -> asymmetric INT4 quant.

        Returns:
            w_rotated:  rotated weight (before quantization)
            w_quantized: fake-quantized weight
            scales, zeros: quantization parameters
            perm: HAP permutation
        """
        perm = self.hap_permutation(weight)
        w_rotated = self.apply_corfig_rotation(weight, perm)
        w_quantized, scales, zeros = self.quantize_asymmetric(w_rotated)
        return w_rotated, w_quantized, scales, zeros, perm


# =============================================================================
# Integer Inner Product Demo (Zero-point Rounding)
# =============================================================================

def demo_integer_inner_product():
    """
    Demonstrate the integer-only inner product reconstruction:
      y ≈ Σ_g s_x^(g) * s_w^(g) * Σ_i (x_hat_i - z_x^(g)) * w_hat_i

    Shows that zero-point rounding enables fully-integer dequantization.
    """
    print("\n--- Integer Inner Product with Zero-Point Rounding ---")
    G = 32  # quantization group size
    x = torch.randn(1, G)
    w = torch.randn(G, 1)

    # Quantize both x (activations) and w (weights) asymmetrically
    x_dq, s_x, z_x = asymmetric_group_quantize(x, bits=4, group_size=G)
    w_dq, s_w, z_w = asymmetric_group_quantize(w, bits=4, group_size=G)

    # Exact inner product (float reference)
    y_exact = torch.matmul(x, w).item()

    # Integer inner product reconstruction:
    # y ≈ s_x * s_w * Σ_i (x_q_i - z_x) * (w_q_i - z_w)
    x_q = torch.clamp(torch.round(x / s_x.unsqueeze(1)) + z_x.unsqueeze(1), 0, 15)
    w_q = torch.clamp(torch.round(w / s_w.unsqueeze(1)) + z_w.unsqueeze(1), 0, 15)

    # Integer subtraction (zero-point removal)
    x_int = (x_q - z_x.unsqueeze(1))  # integer values
    w_int = (w_q - z_w.unsqueeze(1))  # integer values

    # Integer dot product
    int_dot = torch.matmul(x_int, w_int).item()
    y_reconstructed = (s_x * s_w * int_dot).item()

    print(f"  Group size: {G}")
    print(f"  Exact inner product:    {y_exact:.6f}")
    print(f"  Reconstructed (integer): {y_reconstructed:.6f}")
    print(f"  Relative error:          "
          f"{abs(y_exact - y_reconstructed) / max(abs(y_exact), 1e-8) * 100:.2f}%")
    print(f"  Zero-points: z_x={z_x.item():.0f}, z_w={z_w.item():.0f} (integers)")
    print(f"  All-zero-point subtraction is integer-only: "
          f"x_int dtype={x_int.dtype}, values in [{x_int.min():.0f}, {x_int.max():.0f}]")
    print("---\n")


# =============================================================================
# Main Demo
# =============================================================================

def main():
    print("=" * 70)
    print("GyRot: CoRFiG + HAP + Asymmetric INT4 Quantization")
    print("Paper: arXiv:2607.27694")
    print("=" * 70)

    device = "cpu"

    # Demo integer inner product with zero-point rounding
    demo_integer_inner_product()

    # Load model
    print("Loading model...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)

    quantizer = GyRotQuantizer(
        bits=4, quant_group_size=32, rot_group_size=128, outlier_ratio=0.01
    )

    model_type = "MOCK" if is_mock else "REAL"
    print(f"\nModel: {info['name']} ({model_type})")
    print(f"Quantization: {quantizer.bits}-bit asymmetric INT4")
    print(f"  G_quant (quantization group): {quantizer.quant_group_size}")
    print(f"  G_rot   (rotation group):     {quantizer.rot_group_size}")
    print(f"  Quant sub-groups per rotation: {quantizer._n_quant_per_rot}")

    # Collect per-layer results
    layer_results = []
    total_params = 0
    total_sq = {"no_rot": 0.0, "naive": 0.0, "corfig": 0.0, "full": 0.0}

    for name, module in model.named_modules():
        if not isinstance(module, nn.Linear):
            continue

        w = module.weight.data.float()
        if w.numel() == 0:
            continue
        n_params = w.numel()
        total_params += n_params

        # --- Baseline: no rotation, asymmetric INT4 (G_quant=32) ---
        w_q0, _, _ = asymmetric_group_quantize(
            w, bits=4, group_size=quantizer.quant_group_size
        )
        m0 = quantization_error_metrics(w, w_q0)

        # --- Naive: rotation group = quant group = 32 (shows conflict) ---
        H_naive = hadamard_matrix(32, normalize=True)
        n_in = w.shape[1]
        n_full32 = n_in // 32
        w_naive = w.clone()
        if n_full32 > 0:
            w32 = w[:, :n_full32 * 32].reshape(w.shape[0], n_full32, 32)
            w_naive[:, :n_full32 * 32] = torch.matmul(w32, H_naive).reshape(
                w.shape[0], -1)
        w_q1, _, _ = asymmetric_group_quantize(
            w_naive, bits=4, group_size=quantizer.quant_group_size
        )
        m1 = quantization_error_metrics(w_naive, w_q1)

        # --- CoRFiG: rotation G_rot=128 > G_quant=32 (without HAP) ---
        random_perm = torch.randperm(n_in)
        w_corfig = quantizer.apply_corfig_rotation(w, random_perm)
        w_q2, _, _ = asymmetric_group_quantize(
            w_corfig, bits=4, group_size=quantizer.quant_group_size
        )
        m2 = quantization_error_metrics(w_corfig, w_q2)

        # --- Full GyRot: HAP + CoRFiG + asymmetric INT4 ---
        w_rot, w_q3, scales, zeros, hap_perm = quantizer.quantize_weight(w)
        m3 = quantization_error_metrics(w_rot, w_q3)

        total_sq["no_rot"] += m0["mse"] * n_params
        total_sq["naive"] += m1["mse"] * n_params
        total_sq["corfig"] += m2["mse"] * n_params
        total_sq["full"] += m3["mse"] * n_params

        layer_results.append({
            "name": name,
            "shape": tuple(w.shape),
            "n_params": n_params,
            "no_rot_mse": m0["mse"],
            "naive_mse": m1["mse"],
            "corfig_mse": m2["mse"],
            "full_mse": m3["mse"],
        })

    # Print per-layer table
    header = (f"{'Layer':<42} {'Shape':<14} {'NoRot':>10} "
              f"{'Naive':>10} {'CoRFiG':>10} {'Full':>10}")
    print(f"\n{header}")
    print("-" * len(header))
    for r in layer_results[:20]:
        print(f"{r['name']:<42} {str(r['shape']):<14} "
              f"{r['no_rot_mse']:>10.6f} {r['naive_mse']:>10.6f} "
              f"{r['corfig_mse']:>10.6f} {r['full_mse']:>10.6f}")
    if len(layer_results) > 20:
        print(f"  ... ({len(layer_results) - 20} more layers)")

    # Summary
    avg = {k: v / max(total_params, 1) for k, v in total_sq.items()}

    print(f"\n{'=' * 70}")
    print("Summary (weighted average MSE)")
    print(f"{'=' * 70}")
    print(f"  Total layers quantized : {len(layer_results)}")
    print(f"  Total parameters       : {total_params:,}")
    print(f"  Avg MSE (no rotation)         : {avg['no_rot']:.8f}")
    print(f"  Avg MSE (naive rot G=32)      : {avg['naive']:.8f}")
    print(f"  Avg MSE (CoRFiG G_rot=128)    : {avg['corfig']:.8f}")
    print(f"  Avg MSE (CoRFiG+HAP full)     : {avg['full']:.8f}")

    base = max(avg["no_rot"], 1e-12)
    print(f"\n  Improvement vs no-rotation:")
    print(f"    Naive  (G_rot=G_quant=32): "
          f"{(1 - avg['naive'] / base) * 100:+.1f}%  "
          f"{'(conflict!)' if avg['naive'] > avg['corfig'] else ''}")
    print(f"    CoRFiG (G_rot=128>G_quant): "
          f"{(1 - avg['corfig'] / base) * 100:+.1f}%")
    print(f"    Full   (CoRFiG+HAP)       : "
          f"{(1 - avg['full'] / base) * 100:+.1f}%")

    print(f"\n  Key insights:")
    print(f"  - CoRFiG: G_rot(128) > G_quant(32) resolves rotation-grouping conflict")
    print(f"  - HAP: distributes outliers across Hadamard harmonic rows")
    print(f"  - Zero-point rounding enables fully-integer dequantization")
    print(f"  - Naive rotation (G_rot=G_quant) can INCREASE error (conflict)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
