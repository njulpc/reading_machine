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
    code = torch.round(w / scale).clamp(-127, 127).to(torch.int16)
    return code, scale


def flip_signed(code, bit):
    unsigned = torch.bitwise_and(code, 255)
    changed = torch.bitwise_xor(unsigned, 1 << bit)
    return torch.where(changed >= 128, changed - 256, changed)


def attack(code, scale, grad, flips):
    scores = []
    for bit in range(8):
        delta = (flip_signed(code, bit) - code) * scale
        scores.append((grad * delta).abs())
    score = torch.stack(scores)
    chosen = torch.topk(score.flatten(), k=min(flips, score.numel())).indices
    attacked = code.clone()
    plane = code.numel()
    for flat in chosen.tolist():
        bit, pos = divmod(flat, plane)
        attacked.view(-1)[pos] = flip_signed(attacked.view(-1)[pos], bit)
    return attacked, chosen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--flips", type=int, default=5)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args(); torch.manual_seed(a.seed)
    w = load_weight(a.model_dir, 64, 256)
    x = torch.randn(32, w.shape[1])
    code, scale = quantize_int8(w)
    q = (code * scale).detach().requires_grad_(True)
    clean = x @ w.T
    loss = torch.nn.functional.mse_loss(x @ q.T, clean)
    loss.backward()
    attacked_code, chosen = attack(code, scale, q.grad, a.flips)
    attacked = x @ (attacked_code * scale).T
    print(f"model=Qwen3-0.6B tensor={KEY} slice={tuple(w.shape)}")
    print(f"clean_quant_mse={loss.item():.8g}")
    print(f"attacked_mse={torch.nn.functional.mse_loss(attacked, clean).item():.8g}")
    print(f"gradient_ranked_bit_flips={chosen.numel()}")


if __name__ == "__main__": main()
