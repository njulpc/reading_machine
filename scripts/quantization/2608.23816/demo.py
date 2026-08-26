#!/usr/bin/env python3
"""AQLoRA zero-search allocation plus Qwen3 NF4 fake-quant smoke test."""
import argparse
import glob
import math
import os
import random
import time

import torch


NF4 = torch.tensor([
    -1.0, -0.6961928, -0.5250731, -0.3949175,
    -0.2844414, -0.1847734, -0.0910500, 0.0,
    0.0795803, 0.1609302, 0.2461123, 0.3379152,
    0.4407098, 0.5626170, 0.7229568, 1.0,
])
LINEAR_SUFFIXES = (
    "q_proj.weight", "k_proj.weight", "v_proj.weight", "o_proj.weight",
    "gate_proj.weight", "up_proj.weight", "down_proj.weight",
)


def checkpoint(path=None):
    hits = [path] if path else glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
    ))
    if not hits:
        raise FileNotFoundError("pass --checkpoint for Qwen3-0.6B model.safetensors")
    return hits[0]


def nf4_blocks(flat, group=64, chunk_groups=4096):
    original_count = flat.numel()
    pad = (-original_count) % group
    if pad:
        flat = torch.nn.functional.pad(flat, (0, pad))
    blocks = flat.float().view(-1, group)
    output = torch.empty_like(blocks)
    for start in range(0, len(blocks), chunk_groups):
        part = blocks[start:start + chunk_groups]
        scale = part.abs().amax(1).clamp_min(1e-12)
        normalized = part / scale[:, None]
        indices = (normalized[:, :, None] - NF4[None, None, :]).abs().argmin(-1)
        output[start:start + chunk_groups] = NF4[indices] * scale[:, None]
    return output.flatten()[:original_count]


def nf4_mse(x, group=64):
    flat = x.float().flatten()
    reconstructed = nf4_blocks(flat, group)
    return float((reconstructed - flat).square().mean())


def quantize_nf4_(weight, group=64):
    reconstructed = nf4_blocks(weight.detach().flatten(), group).view_as(weight)
    weight.copy_(reconstructed.to(weight.dtype))


def model_directory(path):
    return path if os.path.isdir(path) else os.path.dirname(path)


def self_test():
    x = torch.linspace(-2, 2, 129)
    y = nf4_blocks(x)
    assert y.shape == x.shape and torch.isfinite(y).all()
    assert nf4_mse(torch.zeros(64)) == 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--protect-fraction", type=float, default=0.20)
    parser.add_argument("--max-elements", type=int, default=0,
                        help="0 scans every weight element; positive values are diagnostic only")
    parser.add_argument("--scan-only", action="store_true")
    parser.add_argument("--prompt", default="量化后模型仍然可以")
    args = parser.parse_args()
    if not 0 <= args.protect_fraction <= 1:
        raise ValueError("protect-fraction must be in [0, 1]")
    self_test()
    path = checkpoint(args.checkpoint)

    from safetensors import safe_open
    started = time.perf_counter()
    rows = []
    with safe_open(path, framework="pt", device="cpu") as handle:
        keys = [key for key in handle.keys() if key.endswith(LINEAR_SUFFIXES)]
        for key in keys:
            weight = handle.get_tensor(key)
            sample = weight.flatten()
            if args.max_elements > 0:
                sample = sample[:args.max_elements]
            rows.append((nf4_mse(sample), key, weight.numel(), sample.numel()))
    rows.sort(key=lambda row: row[0], reverse=True)
    keep = math.ceil(len(rows) * args.protect_fraction)
    protected = rows[:keep]
    random_control = random.Random(23816).sample(rows, keep) if keep else []
    total = sum(count for _, _, count, _ in rows)
    fp16 = sum(count for _, _, count, _ in protected)
    nf4 = total - fp16
    # Double-quantized NF4 accounting: 4-bit codes, one 8-bit block absmax per
    # 64 values, and one FP32 scale per 256 block scales. This is an analytical
    # payload estimate, not allocator/GPU peak memory.
    bytes_est = fp16 * 2 + nf4 * 0.5 + math.ceil(nf4 / 64) + 4 * math.ceil(nf4 / (64 * 256))
    scan_seconds = time.perf_counter() - started
    top_mean = sum(value for value, *_ in protected) / max(1, keep)
    random_mean = sum(value for value, *_ in random_control) / max(1, keep)
    print(
        f"linear_layers={len(rows)} protected={keep} layer_fraction={keep/len(rows):.4f} "
        f"protected_parameter_fraction={fp16/total:.4f} scan_seconds={scan_seconds:.3f}"
    )
    print(
        f"estimated_weight_bytes={bytes_est:.0f} effective_bits={bytes_est*8/total:.4f} "
        f"scanned_elements={sum(sampled for *_, sampled in rows)}"
    )
    print("top_protected=" + ",".join(key for _, key, _, _ in protected[:8]))
    print(f"top_mean_nf4_mse={top_mean:.8e} random_mean_nf4_mse={random_mean:.8e}")
    assert len(rows) == 196 and total == 440401920
    assert all(protected[i][0] >= protected[i + 1][0] for i in range(max(0, keep - 1)))
    if args.scan_only:
        return

    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_directory(path)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32,
    ).eval()
    encoded = tokenizer(args.prompt, return_tensors="pt")
    with torch.inference_mode():
        reference = model(**encoded, use_cache=False).logits[:, -1].float()
    protected_modules = {key[:-7] for _, key, _, _ in protected}
    quantized_layers = quantized_elements = 0
    quant_started = time.perf_counter()
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head" and name not in protected_modules:
                quantize_nf4_(module.weight)
                quantized_layers += 1
                quantized_elements += module.weight.numel()
    with torch.inference_mode():
        logits = model(**encoded, use_cache=False).logits[:, -1].float()
        generated = model.generate(**encoded, max_new_tokens=1, do_sample=False, use_cache=True)
    suffix = tokenizer.decode(generated[0, encoded["input_ids"].shape[1]:])
    print(
        f"quantized_layers={quantized_layers} quantized_elements={quantized_elements} "
        f"quant_and_infer_seconds={time.perf_counter()-quant_started:.3f} "
        f"logits_mae={float((logits-reference).abs().mean()):.8f} "
        f"last_token_cosine={float(torch.nn.functional.cosine_similarity(logits,reference,dim=-1)):.8f} "
        f"generated={suffix!r}"
    )
    assert quantized_layers == len(rows) - keep
    assert torch.isfinite(logits).all() and generated.shape[1] > encoded["input_ids"].shape[1]


if __name__ == "__main__":
    main()
