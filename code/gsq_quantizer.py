"""
GSQ: Gumbel-Softmax Quantization Core
======================================
Compact implementation of GSQ (arXiv:2604.18556) for post-training scalar quantization.

Aligned with the paper / official implementation:
  - symmetric integer grids: ternary {-1,0,1}, 2-bit {-2,-1,0,1},
    b-bit {-(2^(b-1)), ..., 2^(b-1)-1}
  - group_size=128 row-wise groups with one learnable scale per group
  - GPTQ warm-start by default (RTN fallback for smoke tests)
  - Gumbel-Softmax relaxation, temperature annealed 2.0 -> 0.05 and
    logit scale kappa annealed 100 -> 500
  - Lion optimizer with separate LR / weight-decay for logits and scales
  - local-shift formulation for b > 2 with a validity mask at grid boundaries
"""

import math
import torch
import torch.nn as nn
from typing import Literal, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GSQConfig:
    """Configuration for GSQ quantization."""
    bits: Literal["ternary", 2, 3, 4] = 2
    group_size: int = 128
    num_epochs: int = 20
    batch_size: int = 64
    # Initialization: paper Eq. 4 / official defaults are std=0.01, strength=6.
    init_method: Literal["gptq", "rtn"] = "gptq"
    init_noise_std: float = 0.01      # sigma_init
    init_alpha: float = 6.0           # GPTQ warm-start strength
    gptq_percdamp: float = 0.01
    gptq_blocksize: int = 128
    # Gumbel-Softmax schedules
    temp_start: float = 2.0
    temp_end: float = 0.05
    kappa_start: float = 100.0
    kappa_end: float = 500.0
    # Optimizer: Lion with different LR for logits vs scales
    lr_logits: float = 1e-4
    lr_scales: float = 5e-5
    lr_min_ratio: float = 0.1         # cosine decay to 10% of base LR
    weight_decay: float = 1.0         # logits only; scales use weight_decay=0
    betas: Tuple[float, float] = (0.9, 0.95)
    # Local-shift (for b > 2)
    local_shift_range: int = 2        # shifts in {-2, -1, 0, 1, 2}
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class LionOptimizer:
    """Lion optimizer (Chen et al., 2023).

    Standard update order:
      c = beta1 * m + (1 - beta1) * g
      p <- p - lr * (sign(c) + weight_decay * p)
      m <- beta2 * m + (1 - beta2) * g
    """

    def __init__(self, param_groups, betas: Tuple[float, float] = (0.9, 0.95), weight_decay: float = 0.0):
        self.param_groups = param_groups
        self.beta1, self.beta2 = betas
        self.weight_decay = weight_decay
        self.m = {}
        for group in self.param_groups:
            group.setdefault("weight_decay", weight_decay)
            group["base_lr"] = group["lr"]
            for p in group["params"]:
                if p.requires_grad:
                    self.m[id(p)] = torch.zeros_like(p)

    def set_lr(self, progress: float, min_ratio: float = 0.1):
        """Cosine LR decay used by the official trainer."""
        progress = min(max(progress, 0.0), 1.0)
        factor = min_ratio + 0.5 * (1.0 - min_ratio) * (1.0 + math.cos(math.pi * progress))
        for group in self.param_groups:
            group["lr"] = group["base_lr"] * factor

    @torch.no_grad()
    def step(self):
        for group in self.param_groups:
            lr = group["lr"]
            wd = group.get("weight_decay", self.weight_decay)
            for p in group["params"]:
                if not p.requires_grad or p.grad is None:
                    continue
                grad = p.grad
                m = self.m[id(p)]
                c = m.mul(self.beta1).add(grad, alpha=1 - self.beta1)
                update = torch.sign(c)
                if wd > 0:
                    update = update + wd * p
                p.add_(update, alpha=-lr)
                m.mul_(self.beta2).add_(grad, alpha=1 - self.beta2)

    def zero_grad(self):
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is not None:
                    p.grad.zero_()


class GSQQuantizer:
    """GSQ quantizer for a single linear layer weight [out_features, in_features]."""

    def __init__(self, config: GSQConfig):
        self.config = config
        self.device = torch.device(config.device)

    # ------------------------- grids / grouping -------------------------
    def _get_grid(self, bits) -> torch.Tensor:
        if bits == "ternary":
            return torch.tensor([-1.0, 0.0, 1.0], device=self.device)
        if bits == 2:
            return torch.tensor([-2.0, -1.0, 0.0, 1.0], device=self.device)
        if bits in (3, 4):
            lo = -(2 ** (bits - 1))
            hi = 2 ** (bits - 1) - 1
            return torch.arange(lo, hi + 1, device=self.device, dtype=torch.float32)
        raise ValueError(f"Unsupported bit-width: {bits}")

    def _pad_in_features(self, w: torch.Tensor, x: Optional[torch.Tensor] = None):
        out_f, in_f = w.shape
        gs = self.config.group_size
        pad = (gs - (in_f % gs)) % gs
        if pad:
            w = torch.nn.functional.pad(w, (0, pad))
            if x is not None:
                x = torch.nn.functional.pad(x, (0, pad))
        n_groups = (in_f + pad) // gs
        return w, x, out_f, in_f, pad, n_groups

    @staticmethod
    def _nearest_grid(values: torch.Tensor, grid: torch.Tensor) -> torch.Tensor:
        # values: [...,], grid: [m] -> nearest grid value with shape values.shape
        idx = (values.unsqueeze(-1) - grid).abs().argmin(dim=-1)
        return grid[idx]

    def _rtn_prior(self, w: torch.Tensor, grid: torch.Tensor):
        """Round-to-nearest prior, kept as an explicit smoke-test fallback."""
        w_pad, _, out_f, in_f, pad, n_groups = self._pad_in_features(w)
        gs = self.config.group_size
        wg = w_pad.view(out_f, n_groups, gs)
        max_abs_grid = max(abs(grid.min().item()), abs(grid.max().item()))
        scales = wg.abs().amax(dim=-1).clamp(min=1e-6) / max_abs_grid
        q_norm = self._nearest_grid(wg / scales.unsqueeze(-1), grid)
        q = q_norm * scales.unsqueeze(-1)
        q = q.view(out_f, n_groups * gs)
        if pad:
            q[:, -pad:] = 0.0
        q_norm = q / scales.repeat_interleave(gs, dim=1)
        return q_norm, scales

    def _gptq_prior(self, w: torch.Tensor, x: torch.Tensor, grid: torch.Tensor):
        """Compact GPTQ prior for one linear layer.

        Returns normalized grid values q_norm and per-group scales.
        Uses the standard GPTQ Cholesky update; intended as a warm-start for GSQ.
        """
        w_pad, x_pad, out_f, in_f, pad, n_groups = self._pad_in_features(w, x)
        gs = self.config.group_size
        block = self.config.gptq_blocksize
        n = w_pad.shape[1]
        max_abs_grid = max(abs(grid.min().item()), abs(grid.max().item()))

        X = x_pad.reshape(-1, x_pad.shape[-1]).float()
        W = w_pad.float().clone()
        H = X.T @ X / max(X.shape[0], 1)
        dead = torch.diag(H) == 0
        H[dead, dead] = 1.0
        W[:, dead] = 0.0
        damp = (self.config.gptq_percdamp * torch.mean(torch.diag(H))).clamp(min=1e-6)

        # Cholesky with progressively stronger damping if needed.
        Hinv_upper = None
        for _ in range(5):
            try:
                Hd = H + torch.eye(n, device=H.device, dtype=H.dtype) * damp
                L = torch.linalg.cholesky(Hd)
                Hinv = torch.cholesky_inverse(L)
                Hinv_upper = torch.linalg.cholesky(Hinv, upper=True)
                break
            except RuntimeError:
                damp *= 10.0
        if Hinv_upper is None:
            # Numerical fallback: still better to run GSQ from RTN than to crash.
            return self._rtn_prior(w, grid)

        scales = torch.zeros(out_f, n_groups, device=self.device, dtype=torch.float32)
        Q = torch.zeros_like(W)
        Err = torch.zeros_like(W)

        for i1 in range(0, n, block):
            i2 = min(i1 + block, n)
            count = i2 - i1
            W1 = W[:, i1:i2].clone()
            Err1 = torch.zeros_like(W1)
            Hinv1 = Hinv_upper[i1:i2, i1:i2]

            for j in range(count):
                col = i1 + j
                if col % gs == 0:
                    g = col // gs
                    gend = min(col + gs, n)
                    scales[:, g] = (W[:, col:gend].abs().amax(dim=1) / max_abs_grid).clamp(min=1e-6)
                s = scales[:, col // gs]
                w_col = W1[:, j]
                q_norm = self._nearest_grid(w_col / s, grid)
                Q[:, col] = q_norm * s
                d = Hinv1[j, j].clamp(min=1e-8)
                err = (w_col - Q[:, col]) / d
                W1[:, j:] -= err.unsqueeze(1) * Hinv1[j, j:].unsqueeze(0)
                Err1[:, j] = err

            Err[:, i1:i2] = Err1
            if i2 < n:
                W[:, i2:] -= Err1 @ Hinv_upper[i1:i2, i2:]

        if pad:
            Q[:, -pad:] = 0.0
        scale_full = scales.repeat_interleave(gs, dim=1)
        q_norm_full = Q / scale_full.clamp(min=1e-8)
        return q_norm_full, scales

    def _init_prior(self, weight: torch.Tensor, calibration_input: Optional[torch.Tensor], grid: torch.Tensor):
        w = weight.to(self.device).float()
        x = None if calibration_input is None else calibration_input.to(self.device).float()
        if x is not None and x.dim() > 2:
            x = x.reshape(-1, x.shape[-1])
        if self.config.init_method == "gptq" and x is not None:
            return self._gptq_prior(w, x, grid)
        return self._rtn_prior(w, grid)

    def _opt_loop(self, w, x, make_soft_norm, make_hard_norm, logit_params, scales_flat, out_f, in_f, n_groups):
        """Run annealed Gumbel optimization. make_*_norm(step_frac) -> [out_f, in_f+pad]."""
        gs = self.config.group_size
        opt = LionOptimizer([
            {"params": logit_params, "lr": self.config.lr_logits, "weight_decay": self.config.weight_decay},
            {"params": [scales_flat], "lr": self.config.lr_scales, "weight_decay": 0.0},
        ], betas=self.config.betas, weight_decay=self.config.weight_decay)

        N = x.shape[0]
        bs = min(self.config.batch_size, N)
        steps_per_epoch = max(1, (N + bs - 1) // bs)
        total_steps = max(1, self.config.num_epochs * steps_per_epoch)
        target = x @ w.t()
        step = 0
        for _ in range(self.config.num_epochs):
            perm = torch.randperm(N, device=x.device)
            for b in range(steps_per_epoch):
                idx = perm[b * bs:(b + 1) * bs]
                xb = x[idx]
                frac = step / max(total_steps - 1, 1)
                temp = self.config.temp_start + (self.config.temp_end - self.config.temp_start) * frac
                kappa = self.config.kappa_start + (self.config.kappa_end - self.config.kappa_start) * frac

                soft_norm = make_soft_norm(temp, kappa)
                scale_full = scales_flat.view(out_f, n_groups).repeat_interleave(gs, dim=1)
                soft_w = scale_full * soft_norm
                pred = xb @ soft_w[:, :in_f].t()
                loss = nn.functional.mse_loss(pred, target[idx])

                loss.backward()
                opt.set_lr(frac, self.config.lr_min_ratio)
                opt.step()
                opt.zero_grad()
                step += 1

        with torch.no_grad():
            hard_norm = make_hard_norm()
            scale_full = scales_flat.view(out_f, n_groups).repeat_interleave(gs, dim=1)
            q = (scale_full * hard_norm)[:, :in_f]
        return q.detach().cpu(), scales_flat.detach().cpu()

    # ------------------------- public quantizers -------------------------
    def quantize_ternary(self, weight: torch.Tensor, calibration_input: torch.Tensor):
        grid = self._get_grid("ternary")
        w = weight.to(self.device).float()
        x = calibration_input.to(self.device).float()
        if x.dim() > 2:
            x = x.reshape(-1, x.shape[-1])
        _, _, out_f, in_f, pad, n_groups = self._pad_in_features(w)
        q_norm, scales_mat = self._init_prior(w, x, grid)
        scales_flat = scales_mat.reshape(-1).detach().clone().requires_grad_(True)

        std, strength = self.config.init_noise_std, self.config.init_alpha
        sign_logits = (std * (torch.randn_like(q_norm) + torch.sign(q_norm) * strength)).requires_grad_(True)
        mask_logits = (std * (torch.randn_like(q_norm) + (2.0 * q_norm.abs() - 1.0) * strength)).requires_grad_(True)

        def soft_norm(temp, kappa):
            # Binary GSQ: logits {-ell, +ell}; difference of two Gumbels is logistic.
            u_m = torch.rand_like(mask_logits)
            noise_m = torch.logit(u_m, eps=1e-8)
            soft_mask = torch.sigmoid((2.0 * kappa * mask_logits + noise_m) / temp)
            u_s = torch.rand_like(sign_logits)
            noise_s = torch.logit(u_s, eps=1e-8)
            soft_sign = 2.0 * torch.sigmoid((2.0 * kappa * sign_logits + noise_s) / temp) - 1.0
            y = soft_mask * soft_sign
            if pad:
                y = y.clone(); y[:, -pad:] = 0.0
            return y

        def hard_norm():
            y = (mask_logits > 0).float() * torch.where(sign_logits > 0, 1.0, -1.0)
            if pad:
                y[:, -pad:] = 0.0
            return y

        return self._opt_loop(w, x, soft_norm, hard_norm, [mask_logits, sign_logits], scales_flat, out_f, in_f, n_groups)

    def quantize_2bit(self, weight: torch.Tensor, calibration_input: torch.Tensor):
        grid = self._get_grid(2)
        w = weight.to(self.device).float()
        x = calibration_input.to(self.device).float()
        if x.dim() > 2:
            x = x.reshape(-1, x.shape[-1])
        _, _, out_f, in_f, pad, n_groups = self._pad_in_features(w)
        q_norm, scales_mat = self._init_prior(w, x, grid)
        scales_flat = scales_mat.reshape(-1).detach().clone().requires_grad_(True)

        std, strength = self.config.init_noise_std, self.config.init_alpha
        logits = -0.5 * (q_norm.unsqueeze(-1) - grid).pow(2)
        logits = logits - logits.mean(dim=-1, keepdim=True)
        logits = (std * (torch.randn_like(logits) + logits * strength)).requires_grad_(True)

        def soft_norm(temp, kappa):
            u = torch.rand_like(logits)
            noise = -torch.log(-torch.log(u + 1e-8) + 1e-8)
            probs = torch.softmax((kappa * logits + noise) / temp, dim=-1)
            y = (probs * grid).sum(dim=-1)
            if pad:
                y = y.clone(); y[:, -pad:] = 0.0
            return y

        def hard_norm():
            y = grid[logits.argmax(dim=-1)]
            if pad:
                y[:, -pad:] = 0.0
            return y

        return self._opt_loop(w, x, soft_norm, hard_norm, [logits], scales_flat, out_f, in_f, n_groups)

    def quantize_general(self, weight: torch.Tensor, calibration_input: torch.Tensor, bits: int):
        grid = self._get_grid(bits)
        min_grid, max_grid = grid.min().item(), grid.max().item()
        w = weight.to(self.device).float()
        x = calibration_input.to(self.device).float()
        if x.dim() > 2:
            x = x.reshape(-1, x.shape[-1])
        _, _, out_f, in_f, pad, n_groups = self._pad_in_features(w)
        init, scales_mat = self._init_prior(w, x, grid)
        init = init.clamp(min_grid, max_grid)
        scales_flat = scales_mat.reshape(-1).detach().clone().requires_grad_(True)

        r = self.config.local_shift_range
        shift_values = torch.arange(-r, r + 1, device=self.device, dtype=torch.float32)
        cand = init.unsqueeze(-1) + shift_values
        valid = (cand >= min_grid) & (cand <= max_grid)

        std, strength = self.config.init_noise_std, self.config.init_alpha
        logits = -0.5 * shift_values.pow(2).view(1, 1, -1).expand_as(cand)
        denom = valid.sum(dim=-1, keepdim=True).clamp(min=1)
        mean = (logits * valid).sum(dim=-1, keepdim=True) / denom
        logits = logits - mean
        logits = (std * (torch.randn_like(logits) + logits * strength)).requires_grad_(True)

        def soft_norm(temp, kappa):
            masked = logits.masked_fill(~valid, -1e9)
            u = torch.rand_like(masked)
            noise = -torch.log(-torch.log(u + 1e-8) + 1e-8)
            probs = torch.softmax((kappa * masked + noise) / temp, dim=-1)
            soft_shift = (probs * shift_values).sum(dim=-1)
            y = init + soft_shift
            if pad:
                y = y.clone(); y[:, -pad:] = 0.0
            return y

        def hard_norm():
            masked = logits.masked_fill(~valid, -1e9)
            hard_shift = shift_values[masked.argmax(dim=-1)]
            y = init + hard_shift
            if pad:
                y[:, -pad:] = 0.0
            return y

        return self._opt_loop(w, x, soft_norm, hard_norm, [logits], scales_flat, out_f, in_f, n_groups)

    def quantize(self, weight: torch.Tensor, calibration_input: torch.Tensor):
        if self.config.bits == "ternary":
            return self.quantize_ternary(weight, calibration_input)
        if self.config.bits == 2:
            return self.quantize_2bit(weight, calibration_input)
        return self.quantize_general(weight, calibration_input, int(self.config.bits))
