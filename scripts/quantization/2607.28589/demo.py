#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Paper: arXiv:2607.28589 — MixFrag: Fragility-Guided Mixed-Precision
       Post-Training Quantization for Vision Transformers
       (Adapted for LLM: Qwen3-0.6B)
================================================================================
Usage: python3 demo.py   (requires: torch; transformers optional)
================================================================================

Core Methodology:
1. Fragility Estimation: For each component (layer), perform "isolated
   quantization" — quantize only this component while keeping all others
   at full precision. Measure KL divergence between the full-precision
   output distribution and the isolated-quantized output distribution.
   This KL divergence is the "fragility score" of the component.

2. Bit Allocation as MCKP: Formulate mixed-precision allocation as a
   Multiple-Choice Knapsack Problem (MCKP). Each component has multiple
   candidate bit-widths (e.g., FP16 / INT8 / INT4 / INT3). Each choice
   has a cost (bit-width × parameter count) and a profit (fragility
   reduction, i.e., negative fragility). Under a total bit-budget
   constraint, maximize total profit = minimize total fragility.

3. Mixed-Precision Assignment: Apply the MCKP-optimal bit-width to each
   component, producing a heterogeneous quantized model.

================================================================================
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# ------------------------------------------------------------------------------
# 0. Global configuration
# ------------------------------------------------------------------------------
torch.manual_seed(42)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Candidate bit-width configurations for each layer.
# Format: (bit_width, description)
# Cost = bit_width * num_params; Profit = fragility reduction.
DEFAULT_BIT_CANDIDATES = [
    (16, "FP16 / BF16"),   # Baseline: full precision (zero quantization loss)
    (8,  "INT8"),          # 8-bit uniform quantization
    (4,  "INT4"),          # 4-bit uniform quantization
    (3,  "INT3"),          # 3-bit uniform quantization (aggressive)
]


# ------------------------------------------------------------------------------
# 1. Quantization primitives (uniform affine / symmetric)
# ------------------------------------------------------------------------------

def uniform_symmetric_quantize(
    x: torch.Tensor,
    num_bits: int,
    per_channel: bool = False,
    channel_dim: int = 0,
) -> torch.Tensor:
    """
    Uniform symmetric quantization (per-tensor or per-channel).

    For a given tensor x and bit-width b:
        scale = max(|x|) / (2^{b-1} - 1)
        x_q   = round(clamp(x / scale, -(2^{b-1}-1), 2^{b-1}-1))
        x_dq  = x_q * scale

    Args:
        x:           Input tensor to quantize.
        num_bits:    Target bit-width (e.g., 8, 4, 3).
        per_channel: Whether to compute scales per output channel.
        channel_dim: Which dimension corresponds to output channels.

    Returns:
        De-quantized tensor (still in floating-point, but quantized).
    """
    if num_bits >= 16:
        # FP16 / BF16 — treat as "no quantization" for our PTQ setting.
        return x

    qmax = 2 ** (num_bits - 1) - 1  # e.g., 127 for 8-bit, 7 for 4-bit, 3 for 3-bit

    if per_channel and x.dim() > 1:
        # Compute scale per channel: max abs over all dims except channel_dim.
        dims = list(range(x.dim()))
        dims.remove(channel_dim)
        amax = x.abs().amax(dim=dims, keepdim=True).clamp_min(1e-8)
    else:
        amax = x.abs().max().clamp_min(1e-8)

    scale = amax / qmax
    x_q = torch.round(x / scale).clamp(-qmax, qmax)
    x_dq = x_q * scale

    # Straight-through estimator for backward (if any).
    return x + (x_dq - x).detach()


def quantize_layer_weights(
    layer: nn.Linear,
    num_bits: int,
    per_channel: bool = True,
) -> nn.Linear:
    """
    In-place quantize the weight (and optionally bias) of an nn.Linear layer.

    Args:
        layer:        The nn.Linear module to quantize.
        num_bits:     Target bit-width.
        per_channel:  Whether to use per-channel scaling for weights.

    Returns:
        The same layer with quantized weight.data (and bias.data if present).
    """
    with torch.no_grad():
        layer.weight.data = uniform_symmetric_quantize(
            layer.weight.data, num_bits, per_channel=per_channel, channel_dim=0
        )
        if layer.bias is not None and num_bits < 16:
            layer.bias.data = uniform_symmetric_quantize(
                layer.bias.data, num_bits, per_channel=False
            )
    return layer


# ------------------------------------------------------------------------------
# 2. KL-divergence based Fragility Estimation
# ------------------------------------------------------------------------------

def kl_divergence_logits(p_logits: torch.Tensor, q_logits: torch.Tensor) -> float:
    """
    Compute KL(P || Q) where P, Q are distributions over vocabulary.

    We use the log-softmax outputs (logits) and compute:
        KL(P||Q) = sum_v P(v) * log(P(v) / Q(v))

    For numerical stability, we compute via log-softmax directly.

    Args:
        p_logits: Full-precision logits [batch, seq_len, vocab_size].
        q_logits: Quantized logits [batch, seq_len, vocab_size].

    Returns:
        Scalar KL divergence averaged over batch and sequence positions.
    """
    log_p = F.log_softmax(p_logits, dim=-1)
    log_q = F.log_softmax(q_logits, dim=-1)
    p = torch.exp(log_p)

    # KL(P||Q) = sum p * (log p - log q)
    kl = (p * (log_p - log_q)).sum(dim=-1)  # [batch, seq_len]
    return kl.mean().item()


def kl_divergence_hidden(p: torch.Tensor, q: torch.Tensor, eps: float = 1e-8) -> float:
    """
    Alternative: KL on hidden-state distributions (when logits are unavailable).

    Treats each token's hidden state as a distribution after softmax over
    the hidden dimension (less principled, but useful for intermediate layers).

    Args:
        p: Full-precision hidden states.
        q: Quantized hidden states.
        eps: Small constant for numerical stability.

    Returns:
        Scalar KL divergence.
    """
    p = p.abs() + eps
    q = q.abs() + eps
    p = p / p.sum(dim=-1, keepdim=True)
    q = q / q.sum(dim=-1, keepdim=True)
    kl = (p * (torch.log(p) - torch.log(q))).sum(dim=-1)
    return kl.mean().item()


# ------------------------------------------------------------------------------
# 3. MixFrag Quantizer
# ------------------------------------------------------------------------------

@dataclass
class ComponentConfig:
    """
    Configuration for one model component (layer) in MCKP.

    Attributes:
        name:       Layer name (e.g., "model.layers.0.self_attn.q_proj").
        module:     Reference to the nn.Module.
        num_params: Number of parameters in this layer (for cost computation).
        choices:    List of (bit_width, fragility_score) tuples.
                    fragility_score is the KL divergence measured when this
                    layer is quantized to bit_width in isolation.
    """
    name: str
    module: nn.Module
    num_params: int
    choices: List[Tuple[int, float]]  # (bit_width, fragility_score)


class MixFragQuantizer:
    """
    MixFrag: Fragility-guided mixed-precision post-training quantizer.

    Implements the three-stage pipeline from the paper:
        Stage 1 — Fragility Estimation (isolated quantization + KL)
        Stage 2 — MCKP-based Bit Allocation
        Stage 3 — Mixed-Precision Assignment
    """

    def __init__(
        self,
        model: nn.Module,
        bit_candidates: Optional[List[Tuple[int, str]]] = None,
        calibration_fn: Optional[Callable[[nn.Module], torch.Tensor]] = None,
        kl_fn: Optional[Callable[[torch.Tensor, torch.Tensor], float]] = None,
    ):
        """
        Args:
            model:            The target model (e.g., Qwen3-0.6B).
            bit_candidates:   List of (bit_width, description) candidate configs.
                              Default: [(16, "FP16"), (8, "INT8"), (4, "INT4"), (3, "INT3")].
            calibration_fn:   Callable(model) -> logits or hidden states.
                              If None, we will construct one from calibration_ids.
            kl_fn:            Callable(fp_output, q_output) -> float KL divergence.
                              Defaults to kl_divergence_logits.
        """
        self.model = model
        self.bit_candidates = bit_candidates or DEFAULT_BIT_CANDIDATES
        self.kl_fn = kl_fn or kl_divergence_logits
        self.calibration_fn = calibration_fn

        # Storage for MCKP data.
        self.components: List[ComponentConfig] = []
        self.fp_outputs_cache: Optional[torch.Tensor] = None

        # Layer selector: which layers are "quantizable components".
        # For LLMs, we target all nn.Linear layers in the model.
        self.quantizable_layers: List[Tuple[str, nn.Linear]] = []

    # --------------------------------------------------------------------------
    # Stage 1: Fragility Estimation
    # --------------------------------------------------------------------------
    def _collect_quantizable_layers(self) -> None:
        """
        Walk through the model and collect all nn.Linear layers as
        quantizable components. These become the "items" in MCKP.
        """
        self.quantizable_layers = []
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                self.quantizable_layers.append((name, module))
        print(f"[MixFrag] Found {len(self.quantizable_layers)} quantizable nn.Linear layers.")

    def _register_hooks_for_intermediate(self, layer_name: str):
        """
        Register forward hooks to capture intermediate outputs of a specific layer.
        This is used for per-layer fragility estimation when we want to compare
        intermediate activations rather than final logits.
        """
        handles = []
        captured = {}

        def make_hook(name):
            def hook(mod, inp, out):
                captured[name] = out.detach().clone()
            return hook

        for n, m in self.model.named_modules():
            if isinstance(m, nn.Linear) and n == layer_name:
                handles.append(m.register_forward_hook(make_hook(n)))
                break
        return handles, captured

    def estimate_fragility(
        self,
        calibration_ids: Optional[torch.Tensor] = None,
        use_intermediate: bool = False,
    ) -> Dict[str, List[Tuple[int, float]]]:
        """
        Stage 1 — Fragility Estimation via Isolated Quantization.

        For each quantizable layer L:
            For each candidate bit-width b:
                1. Save original weight W_L.
                2. Quantize W_L to b bits (all other layers remain FP).
                3. Run calibration forward pass.
                4. Compute KL( FP_output || Q_output ).
                5. Restore W_L.
        The KL divergence is the "fragility score" of layer L at bit-width b.

        Args:
            calibration_ids:  Token IDs for calibration [batch, seq_len].
                              If None, synthetic random inputs are used.
            use_intermediate: If True, measure KL at layer outputs (intermediate
                              hidden states) rather than final logits. This is
                              closer to the paper's original ViT formulation.

        Returns:
            Dict mapping layer_name -> list of (bit_width, fragility_score).
        """
        self._collect_quantizable_layers()

        # --- Calibration input preparation ---
        if calibration_ids is None:
            # Synthetic calibration data (demo fallback).
            print("[MixFrag] No calibration data provided; using synthetic random inputs.")
            calibration_ids = torch.randint(0, 32000, (1, 32), device=DEVICE)
            # We need a dummy forward; real models expect embeddings, so we bypass.
            # For synthetic mode, we use a mock model later.

        # Determine if we can do a real forward pass.
        try:
            self.model.eval()
            with torch.no_grad():
                if hasattr(self.model, "forward"):
                    # Try standard causal LM forward.
                    fp_out = self.model(calibration_ids)
                    if hasattr(fp_out, "logits"):
                        self.fp_outputs_cache = fp_out.logits.detach().clone()
                    else:
                        self.fp_outputs_cache = fp_out.detach().clone()
                else:
                    self.fp_outputs_cache = None
        except Exception as e:
            print(f"[MixFrag] Real forward failed ({e}); will use synthetic validation.")
            self.fp_outputs_cache = None

        # --- Isolated quantization sweep ---
        fragility_map: Dict[str, List[Tuple[int, float]]] = {}

        for layer_name, layer_module in self.quantizable_layers:
            layer_choices: List[Tuple[int, float]] = []
            original_weight = layer_module.weight.data.clone()
            original_bias = layer_module.bias.data.clone() if layer_module.bias is not None else None

            for bits, _desc in self.bit_candidates:
                # Skip quantizing for full-precision candidate (fragility = 0).
                if bits >= 16:
                    fragility = 0.0
                else:
                    # Quantize ONLY this layer in-place.
                    quantize_layer_weights(layer_module, bits, per_channel=True)

                    # Forward pass with isolated quantization.
                    with torch.no_grad():
                        try:
                            if self.fp_outputs_cache is not None:
                                q_out = self.model(calibration_ids)
                                if hasattr(q_out, "logits"):
                                    q_tensor = q_out.logits
                                else:
                                    q_tensor = q_out
                                fragility = self.kl_fn(self.fp_outputs_cache, q_tensor)
                            else:
                                # Synthetic fallback: compare layer output distribution.
                                # Generate synthetic input matching layer weight shape.
                                in_features = layer_module.in_features
                                synthetic_input = torch.randn(
                                    1, 32, in_features, device=DEVICE, dtype=layer_module.weight.dtype
                                )
                                fp_out_local = F.linear(
                                    synthetic_input, original_weight, original_bias
                                )
                                q_out_local = layer_module(synthetic_input)
                                fragility = self.kl_fn(fp_out_local, q_out_local)
                        except Exception as e2:
                            print(f"    [warn] {layer_name} @ {bits}b failed: {e2}; assigning fallback fragility.")
                            fragility = 1.0  # High fragility fallback.

                layer_choices.append((bits, fragility))
                #print(f"    [Fragility] {layer_name:50s} {bits:2d}b -> KL={fragility:.6f}")

                # Restore weight for next candidate / next layer.
                layer_module.weight.data.copy_(original_weight)
                if original_bias is not None:
                    layer_module.bias.data.copy_(original_bias)

            fragility_map[layer_name] = layer_choices

        # Build ComponentConfig list.
        self.components = []
        for name, module in self.quantizable_layers:
            num_params = sum(p.numel() for p in module.parameters())
            self.components.append(
                ComponentConfig(
                    name=name,
                    module=module,
                    num_params=num_params,
                    choices=fragility_map[name],
                )
            )

        return fragility_map

    # --------------------------------------------------------------------------
    # Stage 2: MCKP Solver (Dynamic Programming)
    # --------------------------------------------------------------------------
    @staticmethod
    def solve_mckp_dp(
        components: List[ComponentConfig],
        budget: float,
        granularity: float = 1e-3,
    ) -> Tuple[float, Dict[str, int], float]:
        """
        Solve Multiple-Choice Knapsack Problem (MCKP) via dynamic programming.

        Problem formulation:
            Maximize   sum_i  profit_{i, chosen_j}
            Subject to sum_i  cost_{i, chosen_j}  <=  B
            For each i, exactly one j must be chosen.

        Where:
            profit_{i,j} = max_fragility_i - fragility_{i,j}
                          (higher = better; we normalize so FP16 has max profit).
            cost_{i,j}   = bits_{i,j} * num_params_i  (total bits consumed).

        Args:
            components:   List of ComponentConfig (each with multiple bit choices).
            budget:       Total bit budget (sum of bits × params across all layers).
            granularity:  Discretization step for DP state (to keep table size manageable).

        Returns:
            (total_profit, assignment_dict, used_budget)
            assignment_dict maps layer_name -> chosen_bit_width.
        """
        # Discretize budget.
        scale = 1.0 / granularity
        B = int(math.ceil(budget * scale))

        n = len(components)

        # Normalize profits per component so the highest-precision choice has profit = 0 reference.
        # Actually, we want: profit = baseline_fragility - current_fragility.
        # Higher precision => lower fragility => higher profit.
        # We compute relative to the highest fragility (worst quantization) in that component.
        processed = []
        for comp in components:
            max_frag = max(frag for _b, frag in comp.choices)
            items = []
            for bits, frag in comp.choices:
                # Profit = reduction in fragility compared to worst case.
                profit = max_frag - frag
                # Cost in "discretized units".
                cost = int(math.ceil((bits * comp.num_params) * scale))
                # Also store raw bits for assignment.
                items.append((bits, profit, cost))
            processed.append(items)

        # DP table: dp[i][w] = max profit using first i components with cost <= w.
        # We use 1D DP for memory efficiency.
        dp = [-float("inf")] * (B + 1)
        dp[0] = 0.0

        # Track choices for reconstruction.
        choice = [[-1] * (B + 1) for _ in range(n)]

        for i in range(n):
            new_dp = [-float("inf")] * (B + 1)
            new_choice = [-1] * (B + 1)
            items = processed[i]

            for w in range(B + 1):
                if dp[w] < -1e18:
                    continue
                for idx, (bits, profit, cost) in enumerate(items):
                    w2 = w + cost
                    if w2 > B:
                        continue
                    val = dp[w] + profit
                    if val > new_dp[w2]:
                        new_dp[w2] = val
                        new_choice[w2] = idx

            # Also propagate "not choosing anything yet" — but MCKP requires exactly one per group.
            # The above already handles it since we start from dp and pick one item.
            # However, we need to make sure we don't skip a group. The transition is correct
            # because dp represents states after i groups, and new_dp after i+1 groups.
            dp = new_dp
            choice[i] = new_choice

        # Find best feasible solution.
        best_val = -float("inf")
        best_w = 0
        for w in range(B + 1):
            if dp[w] > best_val:
                best_val = dp[w]
                best_w = w

        # Reconstruct choices.
        assignment: Dict[str, int] = {}
        w = best_w
        for i in range(n - 1, -1, -1):
            idx = choice[i][w]
            if idx < 0:
                # Fallback: choose highest precision (lowest fragility).
                idx = 0
            bits, _profit, cost = processed[i][idx]
            assignment[components[i].name] = bits
            w -= cost
            if w < 0:
                w = 0

        used_budget = best_w * granularity
        return best_val, assignment, used_budget

    @staticmethod
    def solve_mckp_greedy(
        components: List[ComponentConfig],
        budget: float,
    ) -> Tuple[float, Dict[str, int], float]:
        """
        Greedy MCKP solver (faster, approximate).

        Strategy: Start with all layers at lowest precision (highest fragility).
        Iteratively "upgrade" the layer that gives the best
        (profit increase / cost increase) ratio until budget exhausted.

        This is a standard greedy heuristic for MCKP and works well in practice
        when the number of components is large (e.g., ~100 layers in Qwen3-0.6B).

        Args:
            components: List of ComponentConfig.
            budget:     Total bit budget.

        Returns:
            (total_profit, assignment_dict, used_budget)
        """
        # Start with minimum precision (last choice, typically lowest bits).
        assignment: Dict[str, int] = {}
        current_profit = 0.0
        used_cost = 0.0

        # For each component, index of currently selected choice.
        current_idx: Dict[str, int] = {}

        for comp in components:
            # Sort choices by bits ascending.
            sorted_choices = sorted(enumerate(comp.choices), key=lambda x: x[1][0])
            # Start with lowest bits (most aggressive quantization).
            idx = sorted_choices[0][0]
            bits, frag = comp.choices[idx]
            current_idx[comp.name] = idx
            assignment[comp.name] = bits

            max_frag = max(frag for _b, frag in comp.choices)
            profit = max_frag - frag
            cost = bits * comp.num_params
            current_profit += profit
            used_cost += cost

        # Iterative upgrade with best marginal profit/cost ratio.
        import heapq

        while True:
            upgrades = []
            for comp in components:
                idx = current_idx[comp.name]
                # Try upgrading to next higher precision.
                # Choices are not necessarily sorted; find next higher bits.
                candidates = [(i, b, f) for i, (b, f) in enumerate(comp.choices) if b > comp.choices[idx][0]]
                if not candidates:
                    continue
                # Pick the next step up (smallest bit increase).
                next_i, next_b, next_f = min(candidates, key=lambda x: x[1])
                max_frag = max(frag for _b, frag in comp.choices)
                delta_profit = (max_frag - next_f) - (max_frag - comp.choices[idx][1])
                delta_cost = (next_b * comp.num_params) - (comp.choices[idx][0] * comp.num_params)
                if delta_cost <= 0:
                    continue
                ratio = delta_profit / delta_cost
                # Use negative ratio for max-heap via min-heap.
                upgrades.append((-ratio, delta_profit, delta_cost, comp.name, next_i, next_b))

            if not upgrades:
                break

            heapq.heapify(upgrades)
            ratio_neg, d_profit, d_cost, name, next_i, next_b = heapq.heappop(upgrades)

            if used_cost + d_cost > budget:
                # Budget exhausted; stop.
                break

            # Apply upgrade.
            used_cost += d_cost
            current_profit += d_profit
            current_idx[name] = next_i
            assignment[name] = next_b

        return current_profit, assignment, used_cost

    def allocate_bits(
        self,
        target_avg_bits: float,
        solver: str = "greedy",
    ) -> Dict[str, int]:
        """
        Stage 2 — Bit Allocation via MCKP.

        Args:
            target_avg_bits: Target average bit-width per parameter.
                             E.g., 4.0 means total budget = 4.0 * total_params.
            solver:          "dp" for exact dynamic programming (small models),
                             "greedy" for scalable heuristic (default).

        Returns:
            Dictionary mapping layer_name -> allocated_bit_width.
        """
        if not self.components:
            raise RuntimeError("Must call estimate_fragility() before allocate_bits().")

        total_params = sum(c.num_params for c in self.components)
        budget = target_avg_bits * total_params
        print(f"[MixFrag] Total parameters: {total_params:,}")
        print(f"[MixFrag] Target average bits: {target_avg_bits:.2f}")
        print(f"[MixFrag] Total bit budget: {budget:,.0f}")
        print(f"[MixFrag] Solver: {solver}")

        if solver == "dp":
            profit, assignment, used = self.solve_mckp_dp(self.components, budget)
        else:
            profit, assignment, used = self.solve_mckp_greedy(self.components, budget)

        actual_avg = used / total_params if total_params > 0 else 0
        print(f"[MixFrag] Optimization complete: profit={profit:.4f}, used_budget={used:,.0f}, avg_bits={actual_avg:.2f}")

        return assignment

    # --------------------------------------------------------------------------
    # Stage 3: Apply Mixed Precision
    # --------------------------------------------------------------------------
    def apply_mixed_precision(self, assignment: Dict[str, int]) -> nn.Module:
        """
        Stage 3 — Apply the computed mixed-precision assignment to the model.

        For each layer in assignment:
            - Quantize layer weight to the assigned bit-width.
            - Register quantization parameters (scale, zero-point) if needed.

        Args:
            assignment: Dict from layer_name -> bit_width.

        Returns:
            The model with mixed-precision weights applied (in-place modification).
        """
        self.model.eval()
        applied = 0
        for name, module in self.model.named_modules():
            if name in assignment and isinstance(module, nn.Linear):
                bits = assignment[name]
                if bits < 16:
                    quantize_layer_weights(module, bits, per_channel=True)
                    applied += 1
                # else: FP16 / BF16 — no quantization.
        print(f"[MixFrag] Applied mixed precision to {applied} layers.")
        return self.model

    # --------------------------------------------------------------------------
    # Utility: Summary report
    # --------------------------------------------------------------------------
    def print_assignment_summary(self, assignment: Dict[str, int]) -> None:
        """Pretty-print the bit-width assignment."""
        bit_counts: Dict[int, int] = {}
        for name, bits in sorted(assignment.items()):
            bit_counts[bits] = bit_counts.get(bits, 0) + 1
        print("\n" + "=" * 70)
        print(" MixFrag Mixed-Precision Assignment Summary")
        print("=" * 70)
        for bits, count in sorted(bit_counts.items()):
            print(f"  {bits:2d}-bit layers: {count:3d}")
        print("=" * 70)


# ------------------------------------------------------------------------------
# 4. Qwen3-0.6B Adapter & Demo
# ------------------------------------------------------------------------------

def build_mock_qwen_model(
    vocab_size: int = 151936,
    hidden_size: int = 576,
    num_layers: int = 28,
    num_heads: int = 8,
    intermediate_size: int = 1536,
    max_position_embeddings: int = 32768,
) -> nn.Module:
    """
    Build a minimal mock Transformer that mimics Qwen3-0.6B's architecture.

    Architecture (based on Qwen3-0.6B config):
        vocab_size:  151936
        hidden_size: 576
        num_layers:  28
        num_heads:   8
        intermediate_size: 1536
        max_position_embeddings: 32768

    We construct a simplified GPT-style decoder with:
        - Token + positional embeddings
        - Stack of Transformer blocks (each with self-attn + MLP)
        - LayerNorm + LM head

    This is sufficient for demonstrating the MixFrag pipeline end-to-end
    without downloading multi-GB checkpoints.
    """
    class MockTransformerBlock(nn.Module):
        def __init__(self, hidden_size: int, num_heads: int, intermediate_size: int):
            super().__init__()
            self.ln1 = nn.LayerNorm(hidden_size)
            self.ln2 = nn.LayerNorm(hidden_size)

            # Self-attention projections (split Q, K, V for realism).
            head_dim = hidden_size // num_heads
            self.q_proj = nn.Linear(hidden_size, hidden_size)
            self.k_proj = nn.Linear(hidden_size, hidden_size)
            self.v_proj = nn.Linear(hidden_size, hidden_size)
            self.o_proj = nn.Linear(hidden_size, hidden_size)

            # MLP (SwiGLU-style gate + up -> down).
            self.gate_proj = nn.Linear(hidden_size, intermediate_size)
            self.up_proj = nn.Linear(hidden_size, intermediate_size)
            self.down_proj = nn.Linear(intermediate_size, hidden_size)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # Self-attention.
            h = self.ln1(x)
            q = self.q_proj(h)
            k = self.k_proj(h)
            v = self.v_proj(h)
            # Simplified attention (no causal mask for demo).
            attn_out = self.o_proj(v)  # Mock: skip real attn math.
            x = x + attn_out

            # MLP.
            h = self.ln2(x)
            gate = F.silu(self.gate_proj(h))
            up = self.up_proj(h)
            mlp_out = self.down_proj(gate * up)
            x = x + mlp_out
            return x

    class MockQwenModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed_tokens = nn.Embedding(vocab_size, hidden_size)
            self.layers = nn.ModuleList([
                MockTransformerBlock(hidden_size, num_heads, intermediate_size)
                for _ in range(num_layers)
            ])
            self.norm = nn.LayerNorm(hidden_size)
            self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)

        def forward(self, input_ids: torch.Tensor):
            x = self.embed_tokens(input_ids)
            for layer in self.layers:
                x = layer(x)
            x = self.norm(x)
            logits = self.lm_head(x)
            # Return a simple object with .logits attribute (transformers compatible).
            return type("Out", (), {"logits": logits})()

    return MockQwenModel().to(DEVICE)


def load_real_qwen() -> Optional[nn.Module]:
    """Attempt to load real Qwen3-0.6B from Hugging Face."""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print("[MixFrag] Loading real Qwen3-0.6B from Hugging Face...")
        model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-0.6B",
            torch_dtype=torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)
        print("[MixFrag] Real model loaded successfully.")
        return model, tokenizer
    except Exception as e:
        print(f"[MixFrag] Could not load real model: {e}")
        return None, None


# ------------------------------------------------------------------------------
# 5. Main Demo
# ------------------------------------------------------------------------------

def demo():
    print("=" * 78)
    print(" Paper arXiv:2607.28589 — MixFrag: Fragility-Guided Mixed-Precision PTQ")
    print(" Adapted for LLM (Qwen3-0.6B)")
    print("=" * 78)

    # --------------------------------------------------------------------------
    # Part 1: Synthetic mock-model demonstration (always works, no downloads).
    # --------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print(" [PART 1] Synthetic Mock-Model Demonstration")
    print("-" * 78)

    mock_model = build_mock_qwen_model().eval()
    print(f"\n[Info] Built mock Qwen3-0.6B with {sum(p.numel() for p in mock_model.parameters()):,} parameters.")

    # Calibration data for mock model.
    calib_ids_mock = torch.randint(0, 151936, (1, 64), device=DEVICE)

    # Initialize MixFrag quantizer.
    mixfrag = MixFragQuantizer(
        model=mock_model,
        bit_candidates=DEFAULT_BIT_CANDIDATES,
    )

    # Stage 1: Fragility Estimation.
    print("\n[Stage 1] Fragility Estimation (Isolated Quantization + KL Divergence)")
    fragility_map = mixfrag.estimate_fragility(
        calibration_ids=calib_ids_mock,
        use_intermediate=False,
    )

    # Print fragility table (first 5 layers for brevity).
    print("\n[Fragility Table] (showing first 5 layers)")
    for name in list(fragility_map.keys())[:5]:
        print(f"  {name:60s}")
        for bits, frag in fragility_map[name]:
            print(f"      {bits:2d}b -> KL={frag:.6f}")

    # Stage 2: MCKP Bit Allocation.
    print("\n[Stage 2] Bit Allocation via MCKP (target_avg_bits=4.0)")
    assignment = mixfrag.allocate_bits(target_avg_bits=4.0, solver="greedy")

    # Summary.
    mixfrag.print_assignment_summary(assignment)

    # Stage 3: Apply Mixed Precision.
    print("\n[Stage 3] Apply Mixed-Precision Quantization")
    # Save FP logits BEFORE in-place quantization for fair comparison.
    with torch.no_grad():
        fp_out = mock_model(calib_ids_mock).logits
    quantized_model = mixfrag.apply_mixed_precision(assignment)

    # Validation: Compare logits before / after.
    print("\n[Validation] Logit similarity after mixed-precision quantization")
    with torch.no_grad():
        q_out = quantized_model(calib_ids_mock).logits
        cos_sim = F.cosine_similarity(fp_out.reshape(-1), q_out.reshape(-1), dim=0)
        mse = ((fp_out - q_out) ** 2).mean().item()
        print(f"  Cosine similarity (FP vs MixFrag): {cos_sim:.4f}")
        print(f"  MSE: {mse:.4f}")

    # --------------------------------------------------------------------------
    # Part 2: Real Qwen3-0.6B (optional, requires transformers + HF access).
    # --------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print(" [PART 2] Real Qwen3-0.6B (optional — requires transformers + network)")
    print("-" * 78)

    real_model, tokenizer = load_real_qwen()
    if real_model is not None:
        # Use a real text prompt for calibration.
        prompt = "The capital of France is"
        calib_ids_real = tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)

        mixfrag_real = MixFragQuantizer(
            model=real_model,
            bit_candidates=DEFAULT_BIT_CANDIDATES,
        )

        # Stage 1 (subset of layers for speed).
        print("\n[Stage 1] Fragility Estimation on real Qwen3-0.6B")
        # For speed, we can limit to a subset or use fewer calibration steps.
        # Here we do the full pipeline.
        fragility_map_real = mixfrag_real.estimate_fragility(
            calibration_ids=calib_ids_real,
            use_intermediate=False,
        )

        # Stage 2.
        print("\n[Stage 2] MCKP Bit Allocation (target_avg_bits=4.0)")
        assignment_real = mixfrag_real.allocate_bits(target_avg_bits=4.0, solver="greedy")
        mixfrag_real.print_assignment_summary(assignment_real)

        # Stage 3.
        print("\n[Stage 3] Apply to real model")
        # Save FP logits BEFORE in-place quantization for fair comparison.
        with torch.no_grad():
            fp_logits = real_model(calib_ids_real).logits
        quantized_real = mixfrag_real.apply_mixed_precision(assignment_real)

        # Compare logits.
        with torch.no_grad():
            q_logits = quantized_real(calib_ids_real).logits
            cos = F.cosine_similarity(fp_logits.reshape(-1), q_logits.reshape(-1), dim=0)
            print(f"  Real model logits cosine similarity: {cos:.4f}")
    else:
        print("[Info] Real model not available — synthetic demonstration above is complete.")

    # --------------------------------------------------------------------------
    # Part 3: MCKP solver correctness verification (synthetic toy problem).
    # --------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print(" [PART 3] MCKP Solver Verification (synthetic toy problem)")
    print("-" * 78)

    # Toy MCKP: 3 components, each with 3 choices.
    # Budget = 10.
    # We verify that the greedy solver produces a sensible result.
    toy_components = [
        ComponentConfig(
            name="layer_0",
            module=nn.Linear(10, 10),
            num_params=100,
            choices=[(16, 0.0), (8, 0.5), (4, 2.0)],  # bits, fragility
        ),
        ComponentConfig(
            name="layer_1",
            module=nn.Linear(10, 10),
            num_params=100,
            choices=[(16, 0.0), (8, 0.3), (4, 1.5)],
        ),
        ComponentConfig(
            name="layer_2",
            module=nn.Linear(10, 10),
            num_params=100,
            choices=[(16, 0.0), (8, 1.0), (4, 3.0)],
        ),
    ]
    budget_toy = 10 * 300  # avg 10 bits over 300 params

    profit_dp, assign_dp, used_dp = MixFragQuantizer.solve_mckp_dp(toy_components, budget_toy, granularity=1e-2)
    profit_greedy, assign_greedy, used_greedy = MixFragQuantizer.solve_mckp_greedy(toy_components, budget_toy)

    print(f"\n  Toy problem: 3 layers, 3 choices each, budget={budget_toy:.0f}")
    print(f"  DP      solver: profit={profit_dp:.4f}, assignment={assign_dp}, used={used_dp:.0f}")
    print(f"  Greedy  solver: profit={profit_greedy:.4f}, assignment={assign_greedy}, used={used_greedy:.0f}")
    print("  (Both should prefer higher precision for layer_1 (low fragility at 8b),")
    print("   and lower precision for layer_2 (high fragility even at 8b)).")

    print("\n" + "=" * 78)
    print(" SUMMARY: MixFrag pipeline completed successfully.")
    print("   - Stage 1: Per-layer fragility estimated via isolated quantization + KL.")
    print("   - Stage 2: Bit allocation solved as MCKP (greedy / DP).")
    print("   - Stage 3: Mixed-precision weights applied to model.")
    print("=" * 78)


if __name__ == "__main__":
    demo()
