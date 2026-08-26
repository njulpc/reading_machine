#!/usr/bin/env python3
"""Minima-KV three-tier cache transfer on a real Qwen3-0.6B decode."""
import argparse
import copy
import glob
import math
import os
import time

import torch


def model_dir(path=None):
    if path:
        return path if os.path.isdir(path) else os.path.dirname(path)
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
    ))
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B checkpoint missing")
    return os.path.dirname(hits[0])


def fp8(x):
    return x.to(torch.float8_e4m3fn).float()


def fwht(x):
    """Normalized Walsh-Hadamard rotation along the power-of-two last axis."""
    size = x.shape[-1]
    if size & (size - 1):
        raise ValueError("head dimension must be a power of two")
    y = x.clone()
    width = 1
    while width < size:
        y = y.view(*y.shape[:-1], -1, 2, width)
        left, right = y[..., 0, :].clone(), y[..., 1, :].clone()
        y = torch.stack((left + right, left - right), dim=-2).flatten(-3)
        width *= 2
    return y / math.sqrt(size)


def quantize_symmetric_q3(x):
    scale = x.abs().amax(dim=(-2, -1), keepdim=True).clamp_min(1e-12) / 3
    return torch.round(x / scale).clamp(-3, 3) * scale


def quantize_affine_q3(x):
    minimum = x.amin(dim=(-2, -1), keepdim=True)
    maximum = x.amax(dim=(-2, -1), keepdim=True)
    scale = ((maximum - minimum) / 7).clamp_min(1e-12)
    return torch.round((x - minimum) / scale).clamp(0, 7) * scale + minimum


def tq3_key(x):
    # The paper records an FP16 key-norm correction. Preserve each token norm,
    # quantize only the rotated direction, then restore that norm.
    norm = x.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    direction = x / norm
    reconstructed = fwht(quantize_symmetric_q3(fwht(direction)))
    return torch.nn.functional.normalize(reconstructed, dim=-1) * norm


def tq3_value(x):
    # Paper evidence binds FP16 scale/zero metadata for values.
    return fwht(quantize_affine_q3(fwht(x)))


def retier_tensor(x, page_size, recent_pages, anchor_stride, is_key):
    # x: [batch, kv_heads, tokens, head_dim]
    token_count = x.shape[-2]
    pages = math.ceil(token_count / page_size)
    output = x.clone()
    kinds = []
    metadata_bits = 0
    for page in range(pages):
        start, stop = page * page_size, min(token_count, (page + 1) * page_size)
        anchor = page % anchor_stride == 0
        recent = page >= pages - recent_pages
        block = x[..., start:stop, :].float()
        if anchor or recent:
            output[..., start:stop, :] = fp8(block).to(output.dtype)
            kinds.append("FP8")
        else:
            function = tq3_key if is_key else tq3_value
            output[..., start:stop, :] = function(block).to(output.dtype)
            kinds.append("TQ3")
            heads = x.shape[0] * x.shape[1]
            # key: per-token FP16 norm + per-head/page FP16 scale;
            # value: per-head/page FP16 scale and zero.
            metadata_bits += (stop - start) * heads * 16 if is_key else 0
            metadata_bits += heads * (16 if is_key else 32)
    return output, kinds, metadata_bits


def self_test():
    g = torch.Generator().manual_seed(3)
    x = torch.randn(2, 8, 128, generator=g)
    assert torch.allclose(fwht(fwht(x)), x, atol=1e-5)
    key = tq3_key(x)
    assert torch.allclose(key.norm(dim=-1), x.norm(dim=-1), atol=1e-5)
    assert torch.isfinite(tq3_value(x)).all()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--tokens", type=int, default=128)
    parser.add_argument("--page-size", type=int, default=16)
    parser.add_argument("--recent-pages", type=int, default=2)
    parser.add_argument("--anchor-stride", type=int, default=4)
    args = parser.parse_args()
    self_test()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_dir(args.checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32,
    ).eval()
    seed_ids = tokenizer("量化缓存仍应保留所有历史信息。", add_special_tokens=False)["input_ids"]
    repeated = (seed_ids * math.ceil(args.tokens / len(seed_ids)))[:args.tokens]
    input_ids = torch.tensor([repeated])
    started = time.perf_counter()
    with torch.inference_mode():
        prefill = model(input_ids=input_ids, use_cache=True)
    dense_cache = copy.deepcopy(prefill.past_key_values)
    quantized_cache = copy.deepcopy(prefill.past_key_values)

    all_kinds = None
    metadata_bits = payload_bits = bf16_bits = 0
    for layer in quantized_cache.layers:
        keys, kinds, key_meta = retier_tensor(
            layer.keys, args.page_size, args.recent_pages, args.anchor_stride, True
        )
        values, value_kinds, value_meta = retier_tensor(
            layer.values, args.page_size, args.recent_pages, args.anchor_stride, False
        )
        assert kinds == value_kinds
        layer.keys, layer.values = keys, values
        all_kinds = kinds
        elements_per_page = layer.keys.shape[0] * layer.keys.shape[1] * args.page_size * layer.keys.shape[-1]
        for index, kind in enumerate(kinds):
            actual_tokens = min(args.page_size, args.tokens - index * args.page_size)
            actual_elements = elements_per_page * actual_tokens / args.page_size
            payload_bits += int(actual_elements * 2 * (8 if kind == "FP8" else 3))
            bf16_bits += int(actual_elements * 2 * 16)
        metadata_bits += key_meta + value_meta

    continuation = torch.tensor([[seed_ids[-1]]])
    attention_mask = torch.ones(1, args.tokens + 1, dtype=torch.long)
    with torch.inference_mode():
        dense = model(
            input_ids=continuation, attention_mask=attention_mask,
            past_key_values=dense_cache, use_cache=True,
        ).logits[:, -1].float()
        compressed = model(
            input_ids=continuation, attention_mask=attention_mask,
            past_key_values=quantized_cache, use_cache=True,
        ).logits[:, -1].float()
    next_token = compressed.argmax(-1)
    total_bits = payload_bits + metadata_bits
    print(
        f"layers={len(quantized_cache.layers)} tokens={args.tokens} pages={len(all_kinds)} "
        f"formats={all_kinds} page_size={args.page_size}"
    )
    print(
        f"compression_vs_bf16={bf16_bits/total_bits:.4f}x payload_bits={payload_bits} "
        f"metadata_bits={metadata_bits} logits_relative_l2="
        f"{float(torch.linalg.vector_norm(compressed-dense)/torch.linalg.vector_norm(dense)):.8f} "
        f"next_token={tokenizer.decode(next_token)!r} elapsed_seconds={time.perf_counter()-started:.3f}"
    )
    assert len(quantized_cache.layers) == 28
    assert "TQ3" in all_kinds and "FP8" in all_kinds
    assert torch.isfinite(compressed).all()


if __name__ == "__main__":
    main()
