#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.07019 - ReQuant
Title: Fixed-Grid Discrete Refinement for Post-Training Quantization
Core Method: Backpropagation-free fixed-grid refinement for PTQ
================================================================================

This script demonstrates:
1. Simple round-to-nearest PTQ initialization (INT4/INT8)
2. ReQuant iterative refinement on the fixed quantization grid
3. Comparison: simple init vs ReQuant-refined
4. Applied to Qwen3-0.6B linear layers (or synthetic fallback)

Usage:
    python3 demo.py

Requirements:
    pip install torch transformers
================================================================================
"""

import torch
import torch.nn as nn
from typing import Tuple

# =============================================================================
# 1. Quantization Utilities
# =============================================================================

def round_to_nearest_quantize(
    weight: torch.Tensor,
    bits: int = 4,
    group_size: int = 128
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Simple round-to-nearest PTQ. Returns (dequantized, q_indices, scales, zeros)."""
    orig_shape = weight.shape
    w_flat = weight.flatten()
    numel = w_flat.numel()
    pad = (group_size - numel % group_size) % group_size
    if pad:
        w_flat = torch.cat([w_flat, torch.zeros(pad, dtype=w_flat.dtype, device=w_flat.device)])

    n_groups = w_flat.numel() // group_size
    groups = w_flat.reshape(n_groups, group_size)

    w_min = groups.min(dim=1, keepdim=True)[0]
    w_max = groups.max(dim=1, keepdim=True)[0]
    qmax = 2 ** bits - 1
    scales = ((w_max - w_min) / qmax).clamp_min(1e-8)
    zeros = torch.round(-w_min / scales).clamp(0, qmax)

    # Quantize to integer indices
    q = torch.round((groups - w_min) / scales).clamp(0, qmax)
    # Dequantize
    dq = q * scales + w_min

    q = q.flatten().long()
    dq = dq.flatten()
    if pad:
        q = q[:-pad]
        dq = dq[:-pad]

    return dq.reshape(orig_shape), q.reshape(orig_shape), scales, zeros


# =============================================================================
# 2. ReQuant Refinement
# =============================================================================

class ReQuantRefiner:
    def __init__(self, bits: int = 4, group_size: int = 128, max_sweeps: int = 2):
        self.bits = bits
        self.group_size = group_size
        self.max_sweeps = max_sweeps
        self.qmax = 2 ** bits - 1

    def refine_group(self, w_fp, q_init, scale, zero):
        """Refine one group: try all levels per position, accept if MSE reduces."""
        q_cur = q_init.clone().long()
        levels = torch.arange(self.qmax + 1, dtype=w_fp.dtype, device=w_fp.device)

        for _ in range(self.max_sweeps):
            improved = False
            for i in range(w_fp.numel()):
                # current dequantized value
                cur_val = (levels[q_cur[i]] - zero) * scale
                best_mse = (cur_val - w_fp[i]) ** 2
                best_q = q_cur[i].item()

                for q in range(self.qmax + 1):
                    cand_val = (levels[q] - zero) * scale
                    cand_mse = (cand_val - w_fp[i]) ** 2
                    if cand_mse < best_mse:
                        best_mse = cand_mse
                        best_q = q
                        improved = True

                q_cur[i] = best_q
            if not improved:
                break
        return q_cur

    def refine_layer(self, w_fp, q_idx, scales, zeros):
        """Refine entire layer group by group."""
        orig_shape = w_fp.shape
        w_flat = w_fp.flatten()
        q_flat = q_idx.flatten()
        n_groups = w_flat.numel() // self.group_size
        q_ref = torch.zeros_like(q_flat).long()

        s_flat = scales.flatten()
        z_flat = zeros.flatten()

        for g in range(n_groups):
            st = g * self.group_size
            ed = min((g + 1) * self.group_size, w_flat.numel())
            s = s_flat[g] if s_flat.numel() > 1 else s_flat[0]
            z = z_flat[g] if z_flat.numel() > 1 else z_flat[0]
            q_ref[st:ed] = self.refine_group(w_flat[st:ed], q_flat[st:ed], s, z)

        if w_flat.numel() % self.group_size != 0:
            st = n_groups * self.group_size
            q_ref[st:] = q_flat[st:]

        # Dequantize refined indices
        dq = torch.zeros_like(w_flat)
        levels = torch.arange(self.qmax + 1, dtype=w_fp.dtype, device=w_fp.device)
        for g in range(n_groups):
            st = g * self.group_size
            ed = min((g + 1) * self.group_size, w_flat.numel())
            s = s_flat[g] if s_flat.numel() > 1 else s_flat[0]
            z = z_flat[g] if z_flat.numel() > 1 else z_flat[0]
            dq[st:ed] = (levels[q_ref[st:ed]] - z) * s

        if w_flat.numel() % self.group_size != 0:
            st = n_groups * self.group_size
            dq[st:] = w_flat[st:]

        return dq.reshape(orig_shape)


# =============================================================================
# 3. Demo
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2608.07019 - ReQuant")
    print(" Method: Fixed-Grid Discrete Refinement for PTQ")
    print("=" * 70)

    model_name = "Qwen/Qwen3-0.6B"
    fallback = "Qwen/Qwen2-0.5B"

    print(f"\n[1] Loading model...")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="cpu", trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        print(f"  Loaded: {model_name}")
    except Exception as e:
        print(f"  Failed: {e}")
        try:
            model = AutoModelForCausalLM.from_pretrained(
                fallback, torch_dtype=torch.float16, device_map="cpu", trust_remote_code=True,
            )
            tokenizer = AutoTokenizer.from_pretrained(fallback, trust_remote_code=True)
            print(f"  Loaded fallback: {fallback}")
            model_name = fallback
        except Exception as e2:
            print(f"  Fallback failed: {e2}")
            demo_synthetic()
            return

    target_layers = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and "q_proj" in name:
            target_layers.append((name, module))
        if len(target_layers) >= 2:
            break

    print(f"\n[2] Selected {len(target_layers)} layers")
    bits, group_size, max_sweeps = 4, 128, 1
    refiner = ReQuantRefiner(bits=bits, group_size=group_size, max_sweeps=max_sweeps)
    print(f"[3] Config: INT{bits}, group_size={group_size}, sweeps={max_sweeps}")

    total_init, total_rq = 0.0, 0.0
    for name, layer in target_layers:
        w = layer.weight.data.float()
        w_dq, q_idx, scales, zeros = round_to_nearest_quantize(w, bits, group_size)
        mse_init = ((w - w_dq) ** 2).mean().item()
        w_rq = refiner.refine_layer(w, q_idx, scales, zeros)
        mse_rq = ((w - w_rq) ** 2).mean().item()
        total_init += mse_init
        total_rq += mse_rq
        imp = (mse_init - mse_rq) / mse_init * 100 if mse_init > 0 else 0
        print(f"  {name}: init={mse_init:.6f} | ReQuant={mse_rq:.6f} | {imp:+.2f}%")

    avg_imp = (total_init - total_rq) / total_init * 100 if total_init > 0 else 0
    print(f"\n[4] Average improvement: {avg_imp:+.2f}%")

    print(f"\n[5] Generation check")
    inputs = tokenizer("AI will", return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=10, do_sample=False)
    print(f"    '{tokenizer.decode(out[0], skip_special_tokens=True)}'")
    print("=" * 70)


def demo_synthetic():
    print("\n[Synthetic Demo]")
    torch.manual_seed(42)
    w = torch.randn(256, 256)
    bits, group_size, max_sweeps = 4, 128, 2

    refiner = ReQuantRefiner(bits, group_size, max_sweeps)
    w_dq, q_idx, scales, zeros = round_to_nearest_quantize(w, bits, group_size)
    mse_init = ((w - w_dq) ** 2).mean().item()

    w_rq = refiner.refine_layer(w, q_idx, scales, zeros)
    mse_rq = ((w - w_rq) ** 2).mean().item()
    imp = (mse_init - mse_rq) / mse_init * 100

    print(f"  Shape: {tuple(w.shape)} | Init={mse_init:.6f} | ReQuant={mse_rq:.6f} | {imp:+.2f}%")
    print("=" * 70)


if __name__ == '__main__':
    import sys; demo() if len(sys.argv) > 1 and sys.argv[1] == '--real' else demo_synthetic()
