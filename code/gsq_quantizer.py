"""
GSQ: Gumbel-Softmax Quantization Core
======================================
Implementation of GSQ (arXiv:2604.18556) for post-training scalar quantization.

Key features:
  - Group-wise quantization (group_size=128)
  - GPTQ warm-start initialization
  - Gumbel-Softmax relaxation with temperature annealing
  - Lion optimizer (sign-based, handles vanishing gradients)
  - Local-shift formulation for b > 2 (with correct soft indexing)
  - Integer symmetric grid compatible with scalar inference kernels

Supports:
  - Ternary (1.58-bit) quantization
  - 2-bit quantization
  - General b-bit quantization with local-shift formulation
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Literal, Tuple
from dataclasses import dataclass


@dataclass
class GSQConfig:
    """Configuration for GSQ quantization."""
    bits: Literal["ternary", 2, 3, 4] = 2
    group_size: int = 128
    num_epochs: int = 20
    batch_size: int = 64
    # Gumbel-Softmax schedules
    temp_start: float = 2.0
    temp_end: float = 0.05
    kappa_start: float = 100.0
    kappa_end: float = 500.0
    # Optimizer: Lion with different LR for logits vs scales
    lr_logits: float = 1e-4
    lr_scales: float = 5e-5
    weight_decay: float = 1.0
    betas: Tuple[float, float] = (0.9, 0.95)
    # Initialization
    init_noise_std: float = 1.0
    init_alpha: float = 0.5  # GPTQ warm-start strength
    # Local-shift (for b > 2)
    local_shift_range: int = 2  # shifts in {-2, -1, 0, 1, 2}
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class GumbelSoftmaxSampler:
    """
    Gumbel-Softmax sampling for discrete grid selection.
    Algorithm 1 from the paper.
    """

    def __init__(self, temperature: float = 2.0, kappa: float = 100.0):
        self.temperature = temperature
        self.kappa = kappa

    def sample(self, logits: torch.Tensor, grid_values: torch.Tensor) -> torch.Tensor:
        """
        Sample from discrete set using Gumbel-Softmax.

        Args:
            logits: [..., n_candidates] learnable logits
            grid_values: [n_candidates] candidate grid values

        Returns:
            soft_sample: [...] weighted sum of grid values
        """
        # Draw Gumbel noise
        gumbel = -torch.log(-torch.log(torch.rand_like(logits) + 1e-10) + 1e-10)

        # Compute probabilities
        perturbed_logits = self.kappa * logits + gumbel
        probs = torch.softmax(perturbed_logits / self.temperature, dim=-1)

        # Weighted sum over grid values
        grid_view = grid_values.view(*([1] * (logits.dim() - 1) + [-1]))
        soft_sample = torch.sum(probs * grid_view, dim=-1)
        return soft_sample

    def hard_sample(self, logits: torch.Tensor, grid_values: torch.Tensor) -> torch.Tensor:
        """Hard argmax selection (for final quantization)."""
        idx = torch.argmax(logits, dim=-1)
        return grid_values[idx]


class LionOptimizer:
    """
    Lion optimizer (Chen et al., 2023).
    Sign-based update: θ = θ - lr * sign(m_t)
    Less sensitive to vanishing gradients than AdamW.
    """

    def __init__(self, param_groups, betas: Tuple[float, float] = (0.9, 0.99), weight_decay: float = 0.0):
        self.param_groups = param_groups  # List of dict: {'params': [...], 'lr': float}
        self.beta1, self.beta2 = betas
        self.weight_decay = weight_decay
        self.m = {}
        for group in self.param_groups:
            for p in group['params']:
                if p.requires_grad:
                    self.m[id(p)] = torch.zeros_like(p)

    def step(self):
        for group in self.param_groups:
            lr = group['lr']
            for p in group['params']:
                if not p.requires_grad or p.grad is None:
                    continue

                grad = p.grad

                # Weight decay
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * torch.sign(p)

                # Momentum update
                m = self.m[id(p)]
                m.mul_(self.beta2).add_(grad, alpha=1 - self.beta2)

                # Sign-based update
                update = torch.sign(self.beta1 * m + (1 - self.beta1) * grad)
                p.data.add_(update, alpha=-lr)

    def zero_grad(self):
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is not None:
                    p.grad.zero_()


class GSQQuantizer:
    """
    GSQ quantizer for a single linear layer.

    Implements group-wise ternary, 2-bit, and general b-bit quantization
    with local-shift formulation for b > 2.
    """

    def __init__(self, config: GSQConfig):
        self.config = config
        self.sampler = GumbelSoftmaxSampler(config.temp_start, config.kappa_start)
        self.device = torch.device(config.device)

    def _get_grid(self, bits):
        """Get quantization grid for given bit-width."""
        if bits == "ternary":
            return torch.tensor([-1.0, 0.0, 1.0], device=self.device)
        elif bits == 2:
            return torch.tensor([-2.0, -1.0, 0.0, 1.0], device=self.device)
        elif bits in [3, 4]:
            # Integer symmetric grid: {0, 1, 2, ..., 2^b - 1}
            # Scale factor handles the symmetry; grid is non-negative integers
            n_levels = 2 ** bits
            return torch.arange(n_levels, device=self.device).float()
        else:
            raise ValueError(f"Unsupported bit-width: {bits}")

    def _group_weights(self, weight: torch.Tensor):
        """
        Reshape weight for group-wise processing.

        Args:
            weight: [out_features, in_features]

        Returns:
            grouped: [num_groups, group_size] (flattened and transposed for row-wise grouping)
            out_features, in_features
        """
        out_f, in_f = weight.shape
        # Row-wise grouping: each row is split into groups of group_size
        # Pad if necessary
        pad = (self.config.group_size - (in_f % self.config.group_size)) % self.config.group_size
        if pad > 0:
            w_padded = torch.nn.functional.pad(weight, (0, pad))
        else:
            w_padded = weight

        # [out_features, num_groups_per_row, group_size]
        num_groups_per_row = w_padded.shape[1] // self.config.group_size
        grouped = w_padded.view(out_f, num_groups_per_row, self.config.group_size)
        # [num_groups, group_size]
        grouped = grouped.reshape(-1, self.config.group_size)
        return grouped, out_f, in_f, pad

    def _gptq_init(self, weight: torch.Tensor, grid: torch.Tensor):
        """
        Approximate GPTQ initialization: round-to-nearest on the grid.

        Returns:
            quantized_init: hard quantized values on the grid
            scales: per-group scales (absmax)
        """
        grouped, out_f, in_f, pad = self._group_weights(weight)
        num_groups = grouped.shape[0]

        # Per-group absmax scale
        scales = grouped.abs().amax(dim=1, keepdim=True)
        scales = scales.clamp(min=1e-6)

        # Normalize to [-1, 1] or [0, 1] depending on grid
        if grid.min().item() < 0:
            # Symmetric grid (ternary, 2-bit)
            normalized = grouped / scales
        else:
            # Non-negative integer grid (3-bit, 4-bit)
            # Map to [0, max_grid]
            normalized = (grouped / scales + 1) / 2
            normalized = normalized * (grid.max().item())

        # Round to nearest grid point
        distances = (normalized.unsqueeze(-1) - grid.view(1, 1, -1)).abs()
        init_idx = distances.argmin(dim=-1)
        quantized_init = grid[init_idx]

        # Restore padding mask
        if pad > 0:
            mask = torch.ones(out_f, in_f + pad, device=self.device)
            mask[:, -pad:] = 0
            mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
            quantized_init = quantized_init * mask

        return quantized_init, scales, init_idx, grouped, num_groups, out_f, in_f, pad

    def quantize_ternary(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight to ternary {-s, 0, s} using GSQ with group-wise scales.
        """
        w = weight.to(self.device)
        x = calibration_input.to(self.device)

        grid = self._get_grid("ternary")

        # GPTQ initialization with group-wise scales
        q_init, scales, init_idx, grouped, num_groups, out_f, in_f, pad = self._gptq_init(w, grid)

        # Flatten for per-coordinate processing
        grouped_flat = grouped.reshape(-1)
        q_init_flat = q_init.reshape(-1)
        d = grouped_flat.numel()

        # Initialize mask and sign logits from GPTQ warm-start
        mask_init = torch.where(q_init_flat != 0, 1.0, -1.0)
        sign_init = torch.where(q_init_flat > 0, 1.0, -1.0)
        sign_init = torch.where(q_init_flat == 0, 0.0, sign_init)

        mask_logits = (self.config.init_alpha * mask_init +
                       self.config.init_noise_std * torch.randn_like(mask_init)).requires_grad_(True)
        sign_logits = (self.config.init_alpha * sign_init +
                       self.config.init_noise_std * torch.randn_like(sign_init)).requires_grad_(True)

        # Scales: per-group, learnable
        scales_learnable = scales.reshape(-1).detach().clone().requires_grad_(True)

        # Separate optimizer groups for logits and scales
        opt = LionOptimizer([
            {'params': [mask_logits, sign_logits], 'lr': self.config.lr_logits},
            {'params': [scales_learnable], 'lr': self.config.lr_scales},
        ], betas=self.config.betas, weight_decay=self.config.weight_decay)

        # Target output
        with torch.no_grad():
            target_out = x @ w.t()

        num_steps = self.config.num_epochs

        for step in range(num_steps):
            progress = step / max(num_steps - 1, 1)
            self.sampler.temperature = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * progress
            self.sampler.kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * progress

            # Gumbel-Softmax sampling for mask and sign
            grid_mask = torch.tensor([0.0, 1.0], device=self.device)
            grid_sign = torch.tensor([-1.0, 1.0], device=self.device)

            # Mask: binary Gumbel-Softmax
            mask_logits_2 = torch.stack([-mask_logits, mask_logits], dim=-1)  # [d, 2]
            soft_mask = self.sampler.sample(mask_logits_2, grid_mask)  # [d]

            # Sign: binary Gumbel-Softmax
            sign_logits_2 = torch.stack([-sign_logits, sign_logits], dim=-1)  # [d, 2]
            soft_sign = self.sampler.sample(sign_logits_2, grid_sign)  # [d]

            # Compose ternary weight: repeat scales for each element in group
            scales_expanded = scales_learnable.unsqueeze(1).repeat(1, self.config.group_size).reshape(-1)[:d]
            soft_weight_flat = scales_expanded * soft_mask * soft_sign  # [d]
            soft_weight = soft_weight_flat.reshape(num_groups, self.config.group_size)

            # Restore padding
            if pad > 0:
                mask = torch.ones(out_f, in_f + pad, device=self.device)
                mask[:, -pad:] = 0
                mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
                soft_weight = soft_weight * mask

            # Reconstruct full weight
            soft_weight_full = soft_weight.reshape(out_f, -1)[:, :in_f]

            # Reconstruction loss
            pred_out = x @ soft_weight_full.t()
            loss = nn.functional.mse_loss(pred_out, target_out)

            loss.backward()
            opt.step()
            opt.zero_grad()

            if step % 5 == 0:
                print(f"  Step {step}/{num_steps}, Loss: {loss.item():.6f}, Temp: {self.sampler.temperature:.4f}")

        # Final hard quantization
        hard_mask = (mask_logits > 0).float()
        hard_sign = torch.where(sign_logits > 0, 1.0, -1.0)

        scales_expanded = scales_learnable.unsqueeze(1).repeat(1, self.config.group_size).reshape(-1)[:d]
        quantized_flat = scales_expanded.detach() * hard_mask * hard_sign
        quantized = quantized_flat.reshape(num_groups, self.config.group_size)

        if pad > 0:
            mask = torch.ones(out_f, in_f + pad, device=self.device)
            mask[:, -pad:] = 0
            mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
            quantized = quantized * mask

        quantized = quantized.reshape(out_f, -1)[:, :in_f]
        scales_final = scales_learnable.detach().cpu()

        return quantized.detach().cpu(), scales_final

    def quantize_2bit(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight to 2-bit with grid {-2, -1, 0, 1} using group-wise scales.
        """
        w = weight.to(self.device)
        x = calibration_input.to(self.device)

        grid = self._get_grid(2)

        # GPTQ initialization
        q_init, scales, init_idx, grouped, num_groups, out_f, in_f, pad = self._gptq_init(w, grid)

        grouped_flat = grouped.reshape(-1)
        q_init_flat = q_init.reshape(-1)
        d = grouped_flat.numel()

        # Initialize logits: Gaussian-like prior centered at GPTQ solution
        n_levels = grid.numel()
        logits = torch.zeros(d, n_levels, device=self.device)
        for i in range(d):
            idx = init_idx.reshape(-1)[i]
            for j in range(n_levels):
                logits[i, j] = -((j - idx) ** 2) / 2.0
        logits = logits + torch.randn_like(logits) * self.config.init_noise_std
        logits.requires_grad_(True)

        # Per-group scales
        scales_learnable = scales.reshape(-1).detach().clone().requires_grad_(True)

        opt = LionOptimizer([
            {'params': [logits], 'lr': self.config.lr_logits},
            {'params': [scales_learnable], 'lr': self.config.lr_scales},
        ], betas=self.config.betas, weight_decay=self.config.weight_decay)

        with torch.no_grad():
            target_out = x @ w.t()

        num_steps = self.config.num_epochs

        for step in range(num_steps):
            progress = step / max(num_steps - 1, 1)
            self.sampler.temperature = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * progress
            self.sampler.kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * progress

            # Sample quantized values
            soft_q = self.sampler.sample(logits, grid)  # [d]

            # Group-wise scale
            scales_expanded = scales_learnable.unsqueeze(1).repeat(1, self.config.group_size).reshape(-1)[:d]
            soft_weight_flat = scales_expanded * soft_q
            soft_weight = soft_weight_flat.reshape(num_groups, self.config.group_size)

            if pad > 0:
                mask = torch.ones(out_f, in_f + pad, device=self.device)
                mask[:, -pad:] = 0
                mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
                soft_weight = soft_weight * mask

            soft_weight_full = soft_weight.reshape(out_f, -1)[:, :in_f]

            pred_out = x @ soft_weight_full.t()
            loss = nn.functional.mse_loss(pred_out, target_out)

            loss.backward()
            opt.step()
            opt.zero_grad()

            if step % 5 == 0:
                print(f"  Step {step}/{num_steps}, Loss: {loss.item():.6f}")

        # Hard quantization
        hard_idx = torch.argmax(logits, dim=-1)
        hard_q = grid[hard_idx]

        scales_expanded = scales_learnable.unsqueeze(1).repeat(1, self.config.group_size).reshape(-1)[:d]
        quantized_flat = scales_expanded.detach() * hard_q
        quantized = quantized_flat.reshape(num_groups, self.config.group_size)

        if pad > 0:
            mask = torch.ones(out_f, in_f + pad, device=self.device)
            mask[:, -pad:] = 0
            mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
            quantized = quantized * mask

        quantized = quantized.reshape(out_f, -1)[:, :in_f]
        scales_final = scales_learnable.detach().cpu()

        return quantized.detach().cpu(), scales_final

    def quantize_general(self, weight: torch.Tensor, calibration_input: torch.Tensor, bits: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight to b-bit using local-shift formulation (for b > 2).

        FIXED: Uses soft indexing to maintain gradient flow through local shifts.
        """
        w = weight.to(self.device)
        x = calibration_input.to(self.device)

        grid = self._get_grid(bits)
        n_levels = grid.numel()

        # GPTQ initialization
        q_init, scales, init_idx, grouped, num_groups, out_f, in_f, pad = self._gptq_init(w, grid)

        grouped_flat = grouped.reshape(-1)
        init_idx_flat = init_idx.reshape(-1)
        d = grouped_flat.numel()

        # Local-shift candidates: {-2, -1, 0, 1, 2}
        shift_values = torch.tensor([-2, -1, 0, 1, 2], device=self.device).float()
        num_shifts = shift_values.numel()

        # Initialize shift logits: favor 0 shift (stay at GPTQ init)
        shift_logits = torch.zeros(d, num_shifts, device=self.device)
        shift_logits[:, 2] = 1.0  # center at 0 shift
        # Gaussian-like prior: closer shifts get higher prior
        for k in range(num_shifts):
            shift_logits[:, k] += -0.5 * (shift_values[k] ** 2)
        shift_logits = shift_logits + torch.randn_like(shift_logits) * self.config.init_noise_std
        shift_logits.requires_grad_(True)

        # Per-group scales
        scales_learnable = scales.reshape(-1).detach().clone().requires_grad_(True)

        opt = LionOptimizer([
            {'params': [shift_logits], 'lr': self.config.lr_logits},
            {'params': [scales_learnable], 'lr': self.config.lr_scales},
        ], betas=self.config.betas, weight_decay=self.config.weight_decay)

        with torch.no_grad():
            target_out = x @ w.t()

        num_steps = self.config.num_epochs

        for step in range(num_steps):
            progress = step / max(num_steps - 1, 1)
            self.sampler.temperature = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * progress
            self.sampler.kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * progress

            # Sample soft shifts: [d], differentiable
            soft_shift = self.sampler.sample(shift_logits, shift_values)  # [d]

            # Build soft grid values via differentiable soft indexing
            # For each coordinate i, soft_shift_i gives a float offset
            # We compute soft_q_i = grid[clip(init_idx_i + soft_shift_i)]
            # But this must be differentiable!
            # Solution: for each coordinate, compute weighted sum of grid values
            # for all possible final indices, weighted by shift probability.

            init_idx_f = init_idx_flat.float().unsqueeze(1)  # [d, 1]
            shift_values_expanded = shift_values.view(1, -1)  # [1, num_shifts]

            # Possible final indices for each shift
            candidate_indices = init_idx_f + shift_values_expanded  # [d, num_shifts]
            candidate_indices = torch.clamp(candidate_indices, 0, n_levels - 1).long()

            # Candidate grid values
            candidate_grid_values = grid[candidate_indices]  # [d, num_shifts]

            # Get shift probabilities from logits
            shift_probs = torch.softmax(self.sampler.kappa * shift_logits / self.sampler.temperature, dim=-1)
            # Soft quantized value = weighted sum over candidate grid values
            soft_q = torch.sum(shift_probs * candidate_grid_values, dim=-1)  # [d]

            # Group-wise scale
            scales_expanded = scales_learnable.unsqueeze(1).repeat(1, self.config.group_size).reshape(-1)[:d]
            soft_weight_flat = scales_expanded * soft_q
            soft_weight = soft_weight_flat.reshape(num_groups, self.config.group_size)

            if pad > 0:
                mask = torch.ones(out_f, in_f + pad, device=self.device)
                mask[:, -pad:] = 0
                mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
                soft_weight = soft_weight * mask

            soft_weight_full = soft_weight.reshape(out_f, -1)[:, :in_f]

            pred_out = x @ soft_weight_full.t()
            loss = nn.functional.mse_loss(pred_out, target_out)

            loss.backward()
            opt.step()
            opt.zero_grad()

            if step % 5 == 0:
                print(f"  Step {step}/{num_steps}, Loss: {loss.item():.6f}")

        # Hard quantization
        hard_shift_idx = torch.argmax(shift_logits, dim=-1)
        hard_shift = shift_values[hard_shift_idx].long()
        final_idx = init_idx_flat + hard_shift
        final_idx = torch.clamp(final_idx, 0, n_levels - 1)
        hard_q = grid[final_idx]

        scales_expanded = scales_learnable.unsqueeze(1).repeat(1, self.config.group_size).reshape(-1)[:d]
        quantized_flat = scales_expanded.detach() * hard_q
        quantized = quantized_flat.reshape(num_groups, self.config.group_size)

        if pad > 0:
            mask = torch.ones(out_f, in_f + pad, device=self.device)
            mask[:, -pad:] = 0
            mask = mask.view(out_f, -1, self.config.group_size).reshape(-1, self.config.group_size)
            quantized = quantized * mask

        quantized = quantized.reshape(out_f, -1)[:, :in_f]
        scales_final = scales_learnable.detach().cpu()

        return quantized.detach().cpu(), scales_final

    def quantize(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Dispatch to appropriate quantization method."""
        if self.config.bits == "ternary":
            return self.quantize_ternary(weight, calibration_input)
        elif self.config.bits == 2:
            return self.quantize_2bit(weight, calibration_input)
        else:
            return self.quantize_general(weight, calibration_input, self.config.bits)
