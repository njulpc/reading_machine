"""
GSQ: Gumbel-Softmax Quantization Core
======================================
Implementation of GSQ (arXiv:2604.18556) for post-training scalar quantization.

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
    # Lion optimizer
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
        soft_sample = torch.sum(probs * grid_values.view(*([1] * (logits.dim() - 1) + [-1])), dim=-1)
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
    
    def __init__(self, params, lr: float = 1e-4, betas: Tuple[float, float] = (0.9, 0.99), weight_decay: float = 0.0):
        self.params = list(params)
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.weight_decay = weight_decay
        self.m = {id(p): torch.zeros_like(p) for p in self.params if p.requires_grad}
    
    def step(self):
        for p in self.params:
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
            p.data.add_(update, alpha=-self.lr)
        
        self.zero_grad()
    
    def zero_grad(self):
        for p in self.params:
            if p.grad is not None:
                p.grad.zero_()


class GSQQuantizer:
    """
    GSQ quantizer for a single linear layer.
    
    Implements ternary, 2-bit, and general b-bit quantization
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
            # For b > 2, we use local-shift; grid is computed dynamically
            n_levels = 2 ** bits
            return torch.arange(n_levels, device=self.device).float() - (n_levels - 1) / 2
        else:
            raise ValueError(f"Unsupported bit-width: {bits}")
    
    def quantize_ternary(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight to ternary {-s, 0, s} using GSQ.
        
        Args:
            weight: [out_features, in_features]
            calibration_input: [batch, seq_len, in_features]
            
        Returns:
            quantized_weight: [out_features, in_features]
            scale: scalar or [num_groups]
        """
        w = weight.to(self.device)
        x = calibration_input.to(self.device)
        
        # GPTQ-style initialization
        w_flat = w.view(-1)
        
        # Initialize scale (absmean)
        scale = w_flat.abs().mean().detach().clone().requires_grad_(True)
        
        # Initialize mask and sign logits from GPTQ warm-start
        # Simple heuristic: weights with |w| > threshold are non-zero
        threshold = scale.item() * 0.5
        mask_init = torch.where(w_flat.abs() > threshold, 1.0, -1.0)
        sign_init = torch.where(w_flat > 0, 1.0, -1.0)
        sign_init = torch.where(w_flat.abs() <= threshold, 0.0, sign_init)
        
        # Add noise
        mask_logits = (self.config.init_alpha * mask_init + 
                      self.config.init_noise_std * torch.randn_like(w_flat)).requires_grad_(True)
        sign_logits = (self.config.init_alpha * sign_init + 
                      self.config.init_noise_std * torch.randn_like(w_flat)).requires_grad_(True)
        
        # Optimizer
        opt = LionOptimizer([mask_logits, sign_logits, scale], 
                           lr=self.config.lr_logits, 
                           betas=self.config.betas,
                           weight_decay=self.config.weight_decay)
        
        # Target output
        with torch.no_grad():
            target_out = x @ w.t()
        
        num_steps = self.config.num_epochs
        
        for step in range(num_steps):
            # Anneal temperature and kappa
            progress = step / num_steps
            self.sampler.temperature = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * progress
            self.sampler.kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * progress
            
            # Gumbel-Softmax sampling for mask and sign
            grid_mask = torch.tensor([0.0, 1.0], device=self.device)
            grid_sign = torch.tensor([-1.0, 1.0], device=self.device)
            
            # Mask: binary Gumbel-Softmax (single logit → two logits)
            mask_logits_2 = torch.stack([-mask_logits, mask_logits], dim=-1)  # [d, 2]
            soft_mask = self.sampler.sample(mask_logits_2, grid_mask)  # [d]
            
            # Sign: binary Gumbel-Softmax
            sign_logits_2 = torch.stack([-sign_logits, sign_logits], dim=-1)  # [d, 2]
            soft_sign = self.sampler.sample(sign_logits_2, grid_sign)  # [d]
            
            # Compose ternary weight
            soft_weight = scale * soft_mask * soft_sign  # [d]
            soft_weight = soft_weight.view_as(w)
            
            # Reconstruction loss
            pred_out = x @ soft_weight.t()
            loss = nn.functional.mse_loss(pred_out, target_out)
            
            loss.backward()
            opt.step()
            
            if step % 5 == 0:
                print(f"  Step {step}/{num_steps}, Loss: {loss.item():.6f}, Temp: {self.sampler.temperature:.4f}")
        
        # Final hard quantization
        hard_mask = (mask_logits > 0).float()
        hard_sign = torch.where(sign_logits > 0, 1.0, -1.0)
        quantized = scale * hard_mask * hard_sign
        quantized = quantized.view_as(w)
        
        return quantized.detach().cpu(), scale.detach().cpu()
    
    def quantize_2bit(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight to 2-bit with grid {-2, -1, 0, 1}.
        
        Args:
            weight: [out_features, in_features]
            calibration_input: [batch, seq_len, in_features]
            
        Returns:
            quantized_weight: [out_features, in_features]
            scale: scalar
        """
        w = weight.to(self.device)
        x = calibration_input.to(self.device)
        w_flat = w.view(-1)
        d = w_flat.numel()
        
        # Grid
        grid = torch.tensor([-2.0, -1.0, 0.0, 1.0], device=self.device)
        
        # Initialize logits: Gaussian-like prior around GPTQ solution
        # Simple init: center at zero
        logits = torch.randn(d, 4, device=self.device) * 0.1
        logits.requires_grad_(True)
        
        # Initialize scale
        scale = w_flat.abs().mean().detach().clone().requires_grad_(True)
        
        opt = LionOptimizer([logits, scale], lr=self.config.lr_logits, betas=self.config.betas,
                           weight_decay=self.config.weight_decay)
        
        with torch.no_grad():
            target_out = x @ w.t()
        
        num_steps = self.config.num_epochs
        
        for step in range(num_steps):
            progress = step / num_steps
            self.sampler.temperature = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * progress
            self.sampler.kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * progress
            
            # Sample quantized values
            soft_q = self.sampler.sample(logits, grid)  # [d]
            soft_weight = scale * soft_q
            soft_weight = soft_weight.view_as(w)
            
            pred_out = x @ soft_weight.t()
            loss = nn.functional.mse_loss(pred_out, target_out)
            
            loss.backward()
            opt.step()
            
            if step % 5 == 0:
                print(f"  Step {step}/{num_steps}, Loss: {loss.item():.6f}")
        
        # Hard quantization
        hard_idx = torch.argmax(logits, dim=-1)
        hard_q = grid[hard_idx]
        quantized = scale * hard_q
        quantized = quantized.view_as(w)
        
        return quantized.detach().cpu(), scale.detach().cpu()
    
    def quantize_general(self, weight: torch.Tensor, calibration_input: torch.Tensor, bits: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize weight to b-bit using local-shift formulation (for b > 2).
        
        Args:
            weight: [out_features, in_features]
            calibration_input: [batch, seq_len, in_features]
            bits: bit-width (3 or 4)
            
        Returns:
            quantized_weight: [out_features, in_features]
            scale: scalar
        """
        w = weight.to(self.device)
        x = calibration_input.to(self.device)
        w_flat = w.view(-1)
        d = w_flat.numel()
        
        n_levels = 2 ** bits
        grid = torch.arange(n_levels, device=self.device).float() - (n_levels - 1) / 2
        
        # GPTQ-style initialization: find closest grid point for each weight
        scale_init = w_flat.abs().max() / (n_levels / 2)
        normalized = w_flat / scale_init
        init_idx = torch.argmin(torch.abs(normalized.unsqueeze(-1) - grid.unsqueeze(0)), dim=-1)
        
        # Local-shift logits: 5 candidates {-2, -1, 0, 1, 2}
        shift_values = torch.tensor([-2, -1, 0, 1, 2], device=self.device)
        shift_logits = torch.zeros(d, 5, device=self.device)
        
        # Center at 0 shift (keep GPTQ initialization)
        shift_logits[:, 2] = 1.0  # favor 0 shift
        shift_logits = shift_logits + torch.randn_like(shift_logits) * 0.1
        shift_logits.requires_grad_(True)
        
        scale = scale_init.detach().clone().requires_grad_(True)
        
        opt = LionOptimizer([shift_logits, scale], lr=self.config.lr_logits, betas=self.config.betas,
                           weight_decay=self.config.weight_decay)
        
        with torch.no_grad():
            target_out = x @ w.t()
        
        num_steps = self.config.num_epochs
        
        for step in range(num_steps):
            progress = step / num_steps
            self.sampler.temperature = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * progress
            self.sampler.kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * progress
            
            # Sample shifts
            soft_shift = self.sampler.sample(shift_logits, shift_values.float())  # [d]
            
            # Compute final grid indices
            final_idx = init_idx + soft_shift.long()
            final_idx = torch.clamp(final_idx, 0, n_levels - 1)
            
            # Get grid values
            soft_q = grid[final_idx]
            soft_weight = scale * soft_q
            soft_weight = soft_weight.view_as(w)
            
            pred_out = x @ soft_weight.t()
            loss = nn.functional.mse_loss(pred_out, target_out)
            
            loss.backward()
            opt.step()
            
            if step % 5 == 0:
                print(f"  Step {step}/{num_steps}, Loss: {loss.item():.6f}")
        
        # Hard quantization
        hard_shift_idx = torch.argmax(shift_logits, dim=-1)
        hard_shift = shift_values[hard_shift_idx]
        final_idx = init_idx + hard_shift.long()
        final_idx = torch.clamp(final_idx, 0, n_levels - 1)
        hard_q = grid[final_idx]
        quantized = scale * hard_q
        quantized = quantized.view_as(w)
        
        return quantized.detach().cpu(), scale.detach().cpu()
    
    def quantize(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Dispatch to appropriate quantization method."""
        if self.config.bits == "ternary":
            return self.quantize_ternary(weight, calibration_input)
        elif self.config.bits == 2:
            return self.quantize_2bit(weight, calibration_input)
        else:
            return self.quantize_general(weight, calibration_input, self.config.bits)
