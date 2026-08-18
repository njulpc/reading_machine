#!/usr/bin/env python3
"""Gradient-ranked INT8 bit flips on a real Qwen3-0.6B linear weight."""
import argparse
from pathlib import Path
import torch


KEY = "model.layers.0.self_attn.q_proj.weight"


def load_weight(model_dir: Path, rows: int, cols: int) -> torch.Tensor:
    from safetensors import safe_open
    with safe_open(str(model_dir / "model.safetensors"), framework="pt", device="cpu") as f:
        return f.get_tensor(KEY)[:rows, :cols].float().contiguous()


def quantize_int8(w):
    scale = w.abs().amax(1, keepdim=True).clamp_min(1e-8) / 127
    code = torch.round(w / scale).clamp(-128, 127).to(torch.int16)
    return code, scale


def flip_signed(code, bit):
    unsigned = torch.bitwise_and(code, 255)
    changed = torch.bitwise_xor(unsigned, 1 << bit)
    return torch.where(changed >= 128, changed - 256, changed)


def attack(code, scale, grad, flips):
    gains = []
    for bit in range(8):
        delta = (flip_signed(code, bit) - code) * scale
        gains.append(-(grad * delta))
    gains = torch.stack(gains)
    best_gain, best_bit = gains.max(0)
    positive = torch.nonzero(best_gain.flatten() > 0, as_tuple=False).flatten()
    k = min(flips, positive.numel())
    if k == 0:
        return code.clone(), torch.empty((0, 2), dtype=torch.long)
    pos = positive[torch.topk(best_gain.flatten()[positive], k=k).indices]
    bits = best_bit.flatten()[pos]
    attacked = code.clone()
    for scalar_pos, bit in zip(pos.tolist(), bits.tolist()):
        attacked.view(-1)[scalar_pos] = flip_signed(attacked.view(-1)[scalar_pos], bit)
    return attacked, torch.stack([pos, bits], dim=1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--flips", type=int, default=5)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args(); torch.manual_seed(a.seed)
    w = load_weight(a.model_dir, 64, 256)
    x = torch.randn(6, w.shape[1])
    code, scale = quantize_int8(w)
    q = (code * scale).detach().requires_grad_(True)
    clean = x @ w.T
    quantized = x @ q.T
    loss = -quantized.mean()
    loss.backward()
    attacked_code, chosen = attack(code, scale, q.grad, a.flips)
    attacked = x @ (attacked_code * scale).T
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)}")
    print(f"clean_quant_mse={torch.nn.functional.mse_loss(quantized, clean).item():.8g}")
    print(f"attacked_mse={torch.nn.functional.mse_loss(attacked, clean).item():.8g}")
    print(f"directional_mean_shift={(attacked-quantized).mean().item():.8g}")
    print(f"gradient_ranked_bit_flips={chosen.shape[0]} unique_weights={chosen[:, 0].unique().numel()}")


if __name__ == "__main__": main()
