"""
CAT-Q: Cost-efficient and Accurate Ternary Quantization Core
============================================================
Compact implementation of CAT-Q (arXiv:2606.26650) for post-training ternary quantization.

Aligned with the paper:
  - group-wise ternary quantization, group_size=128
  - Learnable Modulation (LM): per-group mu/alpha/threshold statistics with
    three learnable factors delta_mu, delta_alpha, delta_delta
      mu    = mu0 + tanh(delta_mu_raw) * alpha0
      alpha = alpha0 * softplus(delta_alpha_raw)
      Delta = softplus(delta_delta_raw) * Delta0
      What  = (W - mu) / alpha
      reconstruction uses W ~= alpha * T (mu is not added back)
  - Softened Ternarization (ST):
      f(W; s, Delta) = [tanh(s(W-Delta)) + tanh(s(W+Delta))] / [2 tanh(s)]
      t = (epoch + 1) / num_epochs, differentiable stage for 0 < t <= gamma,
      hard stage for gamma < t <= 1. Forward in the hard stage is exactly Q(.);
      gradients use a straight-through estimator (the paper does not specify a
      different backward rule for the hard stage).

Note: CAT-Q's full sliding-layer optimization follows SliderQuant. This compact
core implements the LM + ST layer objective; use the adapter for real activation
capture. `quantize_layers_sliding_window` is only for truly sequential Linear
layers and is not used by the Qwen3 adapter.
"""

import math
import torch
import torch.nn as nn
from typing import Tuple, List
from dataclasses import dataclass


_INV_SOFTPLUS_ONE = math.log(math.e - 1.0)  # softplus(x) == 1


@dataclass
class CATQConfig:
    """Configuration for CAT-Q ternary quantization."""
    # Calibration
    num_calibration_samples: int = 512
    seq_length: int = 2048
    num_epochs: int = 60
    batch_size: int = 8
    activation_rows: int = 512  # rows subsampled from real captured layer inputs
    group_size: int = 128
    # Softened Ternarization (paper default gamma=0.8, s0=30, Delta0=0.5)
    gamma: float = 0.8
    s0: float = 30.0
    delta0: float = 0.5
    # Optimization
    lr: float = 1e-3
    weight_decay: float = 0.0
    # Sliding window: 1 means per-layer output reconstruction in this compact port.
    window_size: int = 1
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class GroupLearnableModulation(nn.Module):
    """Per-group Learnable Modulation for a flattened/padded weight matrix."""

    def __init__(self, weight_groups: torch.Tensor, delta0: float):
        super().__init__()
        w = weight_groups.detach().float()
        mu0 = w.mean(dim=1)
        alpha0 = (w - mu0.unsqueeze(1)).abs().mean(dim=1).clamp(min=1e-8)
        self.register_buffer("mu0", mu0)
        self.register_buffer("alpha0", alpha0)
        self.delta0 = float(delta0)
        self.delta_mu_raw = nn.Parameter(torch.zeros_like(mu0))
        self.delta_alpha_raw = nn.Parameter(torch.full_like(alpha0, _INV_SOFTPLUS_ONE))
        self.delta_delta_raw = nn.Parameter(torch.full_like(alpha0, _INV_SOFTPLUS_ONE))

    def forward(self, weight_groups: torch.Tensor):
        mu = self.mu0 + torch.tanh(self.delta_mu_raw) * self.alpha0
        alpha = self.alpha0 * torch.nn.functional.softplus(self.delta_alpha_raw)
        delta = torch.nn.functional.softplus(self.delta_delta_raw) * self.delta0
        w_hat = (weight_groups - mu.unsqueeze(1)) / alpha.unsqueeze(1)
        return w_hat, alpha, delta


class SoftenedTernarization:
    """CAT-Q softened ternarization schedule."""

    def __init__(self, config: CATQConfig):
        self.config = config

    def transition_function(self, w: torch.Tensor, s: float, delta: torch.Tensor) -> torch.Tensor:
        d = delta.unsqueeze(1)
        s_t = torch.tensor(float(s), device=w.device, dtype=w.dtype)
        denom = 2.0 * torch.tanh(s_t)
        return (torch.tanh(s_t * (w - d)) + torch.tanh(s_t * (w + d))) / denom

    def hard_ternarize(self, w: torch.Tensor, delta: torch.Tensor) -> torch.Tensor:
        d = delta.unsqueeze(1)
        return torch.where(w > d, 1.0, torch.where(w < -d, -1.0, 0.0))

    def forward(self, w_hat: torch.Tensor, delta: torch.Tensor, epoch: int, total_epochs: int) -> torch.Tensor:
        # Use (epoch + 1) so t is in (0, 1]; the paper's t=0 case is just the
        # unquantized starting point and should not be reconstructed as alpha*T.
        t = (epoch + 1) / max(total_epochs, 1)
        if t <= self.config.gamma:
            s = (t / self.config.gamma) * self.config.s0
            return self.transition_function(w_hat, s, delta)
        hard = self.hard_ternarize(w_hat, delta)
        # Forward is exactly hard ternarization; backward uses STE for the
        # learnable factors. This keeps the hard stage trainable without
        # changing the deployed forward mapping.
        return hard + (w_hat - w_hat.detach())


class CATQQuantizer:
    """CAT-Q quantizer for one linear layer weight [out_features, in_features]."""

    def __init__(self, config: CATQConfig):
        self.config = config
        self.device = torch.device(config.device)
        self.st = SoftenedTernarization(config)
        self.last_group_alpha = None
        self.last_group_delta = None

    def _pad(self, w: torch.Tensor, x: torch.Tensor = None):
        out_f, in_f = w.shape
        gs = self.config.group_size
        pad = (gs - (in_f % gs)) % gs
        if pad:
            w = torch.nn.functional.pad(w, (0, pad))
            if x is not None:
                x = torch.nn.functional.pad(x, (0, pad))
        return w, x, out_f, in_f, pad

    @staticmethod
    def _to_groups(w_pad: torch.Tensor, group_size: int) -> torch.Tensor:
        # Row length is padded to a multiple of group_size, so flattening keeps
        # each group inside one output row.
        return w_pad.reshape(-1, group_size)

    @staticmethod
    def _from_groups(groups: torch.Tensor, out_f: int, in_pad: int) -> torch.Tensor:
        return groups.reshape(out_f, in_pad)

    def quantize_layer(self, weight: torch.Tensor, calibration_input: torch.Tensor) -> Tuple[torch.Tensor, float, float]:
        w = weight.to(self.device).float()
        x = calibration_input.to(self.device).float()
        if x.dim() > 2:
            x = x.reshape(-1, x.shape[-1])

        w_pad, x_pad, out_f, in_f, pad = self._pad(w, x)
        gs = self.config.group_size
        w_groups = self._to_groups(w_pad, gs)
        x_pad = x_pad.reshape(-1, x_pad.shape[-1])

        lm = GroupLearnableModulation(w_groups, self.config.delta0).to(self.device)
        opt = torch.optim.Adam(lm.parameters(), lr=self.config.lr, weight_decay=self.config.weight_decay)

        with torch.no_grad():
            target = x_pad @ w_pad.t()

        for epoch in range(self.config.num_epochs):
            w_hat, alpha, delta = lm(w_groups)
            ternary = self.st.forward(w_hat, delta, epoch, self.config.num_epochs)
            # Disentangled reconstruction: W ~= alpha * T (mu is intentionally omitted).
            w_recon = self._from_groups(alpha.unsqueeze(1) * ternary, out_f, w_pad.shape[1])
            pred = x_pad @ w_recon.t()
            loss = nn.functional.mse_loss(pred, target)

            opt.zero_grad()
            loss.backward()
            opt.step()

            if epoch % 10 == 0 or epoch == self.config.num_epochs - 1:
                print(
                    f"  Epoch {epoch + 1}/{self.config.num_epochs}, Loss: {loss.item():.6f}, "
                    f"Delta(mean): {delta.mean().item():.4f}, Alpha(mean): {alpha.mean().item():.4f}"
                )

        with torch.no_grad():
            w_hat, alpha, delta = lm(w_groups)
            ternary_hard = self.st.hard_ternarize(w_hat, delta)
            q_groups = alpha.unsqueeze(1) * ternary_hard
            quantized = self._from_groups(q_groups, out_f, w_pad.shape[1])[:, :in_f]
            self.last_group_alpha = alpha.detach().cpu()
            self.last_group_delta = delta.detach().cpu()

        return quantized.detach().cpu(), float(alpha.mean().item()), float(delta.mean().item())

    def quantize_layers_sliding_window(self, layers: List[nn.Linear], calibration_input: torch.Tensor) -> List[torch.Tensor]:
        """Quantize truly sequential Linear layers by propagating outputs.

        This is a small helper for sequential MLP-like chains. Do not pass
        parallel projections (q/k/v or gate/up) as if they were sequential.
        The Qwen3 adapter uses per-layer real activations instead.
        """
        quantized_weights = []
        current_input = calibration_input.to(self.device).float()
        if current_input.dim() > 2:
            current_input = current_input.reshape(-1, current_input.shape[-1])
        for i, layer in enumerate(layers):
            print(f"\nQuantizing sequential layer {i + 1}/{len(layers)}: {tuple(layer.weight.shape)}")
            qw, alpha, delta = self.quantize_layer(layer.weight.data, current_input)
            quantized_weights.append(qw)
            with torch.no_grad():
                current_input = current_input @ qw.t().to(self.device)
        return quantized_weights
