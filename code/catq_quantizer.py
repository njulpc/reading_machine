"""
CAT-Q: Cost-efficient and Accurate Ternary Quantization Core
============================================================
Implementation of CAT-Q (arXiv:2606.26650) for post-training ternary quantization.

Key components:
  - Learnable Modulation (LM): modulates weight distribution
  - Softened Ternarization (ST): differentiable → hard two-stage relay
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class CATQConfig:
    """Configuration for CAT-Q ternary quantization."""
    # Calibration
    num_calibration_samples: int = 512
    seq_length: int = 2048
    num_epochs: int = 60
    batch_size: int = 8
    # Softened Ternarization
    gamma: float = 0.5  # Fraction of epochs for differentiable stage
    s0: float = 30.0    # Initial sharpness
    delta0: float = 0.5 # Initial threshold
    # Optimization
    lr: float = 1e-3
    weight_decay: float = 0.0
    # Sliding window
    window_size: int = 2  # Number of layers to optimize together
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class LearnableModulation:
    """
    Learnable Modulation (LM) component.
    
    Modulates pre-trained weight distribution:
        Ŵ = (W - μ) / α
    where:
        μ = μ₀ + δ_μ · α₀
        α = α₀ · δ_α
        δ_μ ∈ (-1, 1), δ_α > 0 are learnable
    """
    
    def __init__(self, weight: torch.Tensor):
        self.device = weight.device
        w = weight.detach()
        
        # Compute statistics
        self.mu0 = w.mean().item()
        self.alpha0 = (w - self.mu0).abs().mean().item()
        
        # Learnable factors
        self.delta_mu = nn.Parameter(torch.tensor(0.0, device=self.device))
        self.delta_alpha = nn.Parameter(torch.tensor(1.0, device=self.device))
    
    def forward(self, weight: torch.Tensor) -> torch.Tensor:
        """Apply modulation to weights."""
        mu = self.mu0 + torch.tanh(self.delta_mu) * self.alpha0
        alpha = self.alpha0 * torch.nn.functional.softplus(self.delta_alpha)
        return (weight - mu) / alpha
    
    def get_scale_threshold(self) -> Tuple[float, float]:
        """Get current scale (alpha) and threshold (delta)."""
        alpha = self.alpha0 * torch.nn.functional.softplus(self.delta_alpha).item()
        # Threshold delta = delta_delta * delta0 (learned separately in full implementation)
        return alpha, self.delta0 if hasattr(self, 'delta0') else 0.5


class SoftenedTernarization:
    """
    Softened Ternarization (ST) component.
    
    Two-stage relay:
      Stage 1 (0 < t ≤ γ): differentiable ternarization via transition function
      Stage 2 (γ < t ≤ 1): hard ternarization
    
    Transition function:
        f(W; s, Δ) = (tanh(s·(W-Δ)) + tanh(s·(W+Δ))) / (2·tanh(s))
    """
    
    def __init__(self, config: CATQConfig):
        self.config = config
    
    def transition_function(self, w: torch.Tensor, s: float, delta: float) -> torch.Tensor:
        """
        Differentiable transition function approaching ternary.
        
        Args:
            w: weight tensor
            s: sharpness parameter
            delta: threshold
            
        Returns:
            Soft ternary output in [-1, 1]
        """
        return (torch.tanh(s * (w - delta)) + torch.tanh(s * (w + delta))) / (2.0 * np.tanh(s))
    
    def hard_ternarize(self, w: torch.Tensor, delta: float) -> torch.Tensor:
        """
        Hard ternarization: {-1, 0, 1}.
        
        Args:
            w: weight tensor (already modulated)
            delta: threshold
            
        Returns:
            Ternary weights
        """
        return torch.where(w > delta, 1.0,
                          torch.where(w < -delta, -1.0, 0.0))
    
    def forward(self, w_modulated: torch.Tensor, delta: float, 
                epoch: int, total_epochs: int) -> torch.Tensor:
        """
        Apply softened ternarization based on current epoch.
        
        Args:
            w_modulated: Modulated weights
            delta: Ternary threshold
            epoch: Current epoch (0-indexed)
            total_epochs: Total number of epochs
            
        Returns:
            Ternary (or soft-ternary) weights
        """
        t = epoch / total_epochs  # Normalized time [0, 1]
        gamma = self.config.gamma
        
        if t == 0:
            # Initialization: return original (modulated) weights
            return w_modulated
        elif t <= gamma:
            # Stage 1: Differentiable ternarization with progressive sharpness
            s = (t / gamma) * self.config.s0
            return self.transition_function(w_modulated, s, delta)
        else:
            # Stage 2: Hard ternarization
            # Use straight-through estimator for gradients
            hard = self.hard_ternarize(w_modulated, delta)
            soft = self.transition_function(w_modulated, self.config.s0, delta)
            # Straight-through: forward uses hard, backward uses soft
            return hard + (soft - soft.detach())


class CATQQuantizer:
    """
    CAT-Q quantizer for a single linear layer or sliding window.
    """
    
    def __init__(self, config: CATQConfig):
        self.config = config
        self.device = torch.device(config.device)
        self.st = SoftenedTernarization(config)
    
    def quantize_layer(self, weight: torch.Tensor, calibration_input: torch.Tensor,
                       delta_delta: Optional[nn.Parameter] = None) -> Tuple[torch.Tensor, float, float]:
        """
        Quantize a single linear layer to ternary.
        
        Args:
            weight: [out_features, in_features]
            calibration_input: [batch, seq_len, in_features]
            delta_delta: Optional learnable threshold factor
            
        Returns:
            quantized_weight: Ternary weights
            alpha: Scale factor
            delta: Threshold
        """
        w = weight.to(self.device).detach()
        x = calibration_input.to(self.device)
        
        # Learnable Modulation
        lm = LearnableModulation(w).to(self.device)
        
        # Threshold factor
        if delta_delta is None:
            delta_delta = nn.Parameter(torch.tensor(1.0, device=self.device))
        else:
            delta_delta = delta_delta.to(self.device)
        
        # Compute initial statistics
        mu0 = w.mean().item()
        alpha0 = (w - mu0).abs().mean().item()
        
        # Target output
        with torch.no_grad():
            target_out = x @ w.t()
        
        # Optimizer for LM factors and threshold
        params = list(lm.parameters()) + [delta_delta]
        opt = torch.optim.Adam(params, lr=self.config.lr, weight_decay=self.config.weight_decay)
        
        num_epochs = self.config.num_epochs
        
        for epoch in range(num_epochs):
            # Apply modulation
            w_mod = lm.forward(w)
            
            # Compute threshold
            delta = torch.nn.functional.softplus(delta_delta) * self.config.delta0
            
            # Apply softened ternarization
            ternary = self.st.forward(w_mod, delta.item(), epoch, num_epochs)
            
            # Compute scale (alpha)
            alpha = alpha0 * torch.nn.functional.softplus(lm.delta_alpha)
            
            # Reconstruct weight: W ≈ alpha * T
            w_recon = alpha * ternary
            
            # Output reconstruction loss
            pred_out = x @ w_recon.t()
            loss = nn.functional.mse_loss(pred_out, target_out)
            
            opt.zero_grad()
            loss.backward()
            opt.step()
            
            if epoch % 10 == 0:
                print(f"  Epoch {epoch}/{num_epochs}, Loss: {loss.item():.6f}, "
                      f"Delta: {delta.item():.4f}, Alpha: {alpha.item():.4f}")
        
        # Final hard quantization
        with torch.no_grad():
            w_mod = lm.forward(w)
            delta = torch.nn.functional.softplus(delta_delta) * self.config.delta0
            alpha = alpha0 * torch.nn.functional.softplus(lm.delta_alpha)
            
            ternary_hard = self.st.hard_ternarize(w_mod, delta.item())
            quantized = alpha * ternary_hard
        
        return quantized.detach().cpu(), alpha.item(), delta.item()
    
    def quantize_layers_sliding_window(self, layers: List[nn.Linear], 
                                       calibration_input: torch.Tensor) -> List[torch.Tensor]:
        """
        Quantize multiple layers using sliding-window output reconstruction.
        
        Args:
            layers: List of Linear layers
            calibration_input: Input features for the first layer
            
        Returns:
            List of quantized weights
        """
        # Simplified sliding window: optimize each layer with its output
        quantized_weights = []
        current_input = calibration_input.to(self.device)
        
        for i, layer in enumerate(layers):
            print(f"\nQuantizing layer {i+1}/{len(layers)}: {layer.weight.shape}")
            
            qw, alpha, delta = self.quantize_layer(layer.weight.data, current_input)
            quantized_weights.append(qw)
            
            # Update input for next layer (using quantized output)
            with torch.no_grad():
                current_input = current_input @ qw.t().to(self.device)
        
        return quantized_weights
