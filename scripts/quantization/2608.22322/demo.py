#!/usr/bin/env python3
"""Adaptive Log-Space (AL8) and UF8 optimizer-state reference.

The quantizers follow arXiv:2608.22322 and the authors' PyTorch fallback.
The optional full-model path performs one real Qwen3-0.6B loss/backward/update
step on the first q_proj and verifies post-update forward/generation.
"""

import argparse
import glob
import math
import os
import time

import torch


def find_checkpoint(explicit=None):
    if explicit:
        if os.path.isdir(explicit):
            candidate = os.path.join(explicit, "model.safetensors")
            if os.path.isfile(candidate):
                return candidate
        if os.path.isfile(explicit):
            return explicit
        raise FileNotFoundError(explicit)
    patterns = [
        os.path.expanduser(
            "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/"
            "snapshots/*/model.safetensors"
        ),
        "/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/"
        "snapshots/*/model.safetensors",
    ]
    hits = sum((glob.glob(pattern) for pattern in patterns), [])
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B not found; pass --checkpoint")
    return hits[0]


def load_weight(path, max_elements=524288):
    from safetensors import safe_open

    with safe_open(path, framework="pt", device="cpu") as handle:
        keys = [key for key in handle.keys() if key.endswith("q_proj.weight")]
        key = keys[0] if keys else next(
            key for key in handle.keys() if key.endswith("weight")
        )
        weight = handle.get_tensor(key).float().flatten()
        if max_elements:
            weight = weight[:max_elements]
    return key, weight.contiguous()


def al_quantize(x, bits=8, block_size=2048, min_log_floor=-126.0):
    """Paper Eqs. (3)-(5), including exact zero and degenerate blocks."""
    if bits not in (8, 16):
        raise ValueError("AL reference supports 8 or 16 bits")
    if torch.any(x < 0):
        raise ValueError("AL is defined only for non-negative states")
    shape = x.shape
    flat = x.float().flatten()
    pad = (-flat.numel()) % block_size
    if pad:
        flat = torch.nn.functional.pad(flat, (0, pad))
    blocks = flat.view(-1, block_size)
    is_zero = blocks == 0
    logs = torch.log2(blocks.clamp_min(1e-38))
    min_log = logs.masked_fill(is_zero, float("inf")).amin(1)
    max_log = logs.amax(1).clamp_max(126.0)
    all_zero = is_zero.all(1)
    min_log = min_log.clamp_min(min_log_floor)
    min_log = torch.where(min_log >= max_log, max_log - 1.0, min_log)
    min_log = torch.where(all_zero, torch.zeros_like(min_log), min_log)
    delta = torch.where(all_zero, torch.zeros_like(max_log), max_log - min_log)
    delta = torch.where(all_zero, delta, delta.clamp_min(1e-12))

    levels = 1 << bits
    qmax = levels - 1
    normalized = (logs - min_log[:, None]) / delta.clamp_min(1e-12)[:, None]
    codes = (1 + torch.round(normalized * (qmax - 1))).clamp(1, qmax)
    codes[is_zero] = 0
    code_dtype = torch.uint8 if bits == 8 else torch.int32
    codes = codes.to(code_dtype)

    qfloat = codes.float()
    reconstructed = torch.pow(
        2.0,
        min_log[:, None]
        + (qfloat - 1.0) * delta[:, None] / float(qmax - 1),
    )
    reconstructed[codes == 0] = 0
    reconstructed = reconstructed.flatten()
    codes_flat = codes.flatten()
    if pad:
        reconstructed = reconstructed[:-pad]
        codes_flat = codes_flat[:-pad]
    return reconstructed.view(shape), codes_flat, min_log, delta


def uf8_quantize(x, block_size=256):
    """Authors' UF8: absmax/128 with the asymmetric integer range [-128,127]."""
    shape = x.shape
    flat = x.float().flatten()
    pad = (-flat.numel()) % block_size
    if pad:
        flat = torch.nn.functional.pad(flat, (0, pad))
    blocks = flat.view(-1, block_size)
    absmax = blocks.abs().amax(1).clamp_min(1e-12)
    signed = torch.round(blocks / absmax[:, None] * 128.0).clamp(-128, 127)
    codes = (signed + 128).to(torch.uint8)
    reconstructed = signed * (absmax[:, None] / 128.0)
    reconstructed = reconstructed.flatten()
    codes = codes.flatten()
    if pad:
        reconstructed = reconstructed[:-pad]
        codes = codes[:-pad]
    return reconstructed.view(shape), codes, absmax


def rel_l2(reference, actual):
    return float(
        torch.linalg.vector_norm(reference.float() - actual.float())
        / torch.linalg.vector_norm(reference.float()).clamp_min(1e-20)
    )


def self_test():
    x = torch.tensor([0.0, 1e-6, 1e-3, 1.0, 10.0, 10.0])
    reconstructed, codes, _, _ = al_quantize(x, 8, 8)
    assert reconstructed[0] == 0 and codes[0] == 0
    assert torch.all(codes[1:] > 0) and torch.isfinite(reconstructed).all()
    same = torch.full((8,), 3.0)
    same_hat, _, same_min, same_delta = al_quantize(same, 8, 8)
    assert torch.allclose(same_hat, same) and float(same_delta[0]) == 1.0
    assert float(same_min[0]) < math.log2(3.0)
    momentum = torch.tensor([-2.0, -0.5, 0.0, 1.984375])
    momentum_hat, _, _ = uf8_quantize(momentum, 4)
    assert torch.isfinite(momentum_hat).all() and momentum_hat[0] == -2.0


def run_operator(path, max_elements):
    key, weight = load_weight(path, max_elements)
    second = weight.square()
    momentum = weight
    al8, codes_v, min_log, _ = al_quantize(second, 8, 2048)
    uf8, codes_m, scale_m = uf8_quantize(momentum, 256)
    packed = codes_v.numel() + codes_m.numel() + len(min_log) * 8 + len(scale_m) * 4
    baseline = 2 * weight.numel() * 4
    print(f"checkpoint={path}\ntensor={key} elements={weight.numel()}")
    print(
        f"AL8_second_rel_l2={rel_l2(second, al8):.8f} "
        f"zeros_preserved={bool(torch.all(al8[second == 0] == 0))} "
        f"v_block=2048"
    )
    print(f"UF8_momentum_rel_l2={rel_l2(momentum, uf8):.8f} m_block=256")
    print(
        f"estimated_state_bytes_fp32={baseline} quantized={packed} "
        f"compression={baseline / packed:.3f}x"
    )


def run_full_model(path, prompt, learning_rate, save_state=None):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_dir = os.path.dirname(path)
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir, local_files_only=True, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    target_name, target = next(
        (name, parameter)
        for name, parameter in model.named_parameters()
        if name.endswith("q_proj.weight")
    )
    target.requires_grad_(True)
    inputs = tokenizer(prompt, return_tensors="pt")
    labels = inputs["input_ids"].clone()
    with torch.no_grad():
        reference_logits = model(**inputs, use_cache=False).logits.detach()

    output = model(**inputs, labels=labels, use_cache=False)
    output.loss.backward()
    gradient = target.grad.detach().float()
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    momentum = (1.0 - beta1) * gradient
    second = (1.0 - beta2) * gradient.square()
    momentum_hat, momentum_codes, momentum_scale = uf8_quantize(momentum, 256)
    second_hat, second_codes, second_min, second_delta = al_quantize(
        second, 8, 2048, min_log_floor=math.log2(eps * eps)
    )
    update = (momentum_hat / (1.0 - beta1)) / (
        torch.sqrt(second_hat / (1.0 - beta2)) + eps
    )
    with torch.no_grad():
        target.add_(update.to(target.dtype), alpha=-learning_rate)
    target.grad = None
    target.requires_grad_(False)
    with torch.no_grad():
        quantized_logits = model(**inputs, use_cache=False).logits
        generated = model.generate(
            **inputs, max_new_tokens=1, do_sample=False, use_cache=False
        )
    logits_mae = float((reference_logits - quantized_logits).abs().mean())
    cosine = float(
        torch.nn.functional.cosine_similarity(
            reference_logits[:, -1].float(), quantized_logits[:, -1].float(), dim=-1
        ).mean()
    )
    state_bytes = (
        momentum_codes.numel()
        + second_codes.numel()
        + momentum_scale.numel() * 4
        + second_min.numel() * 8
    )
    if save_state:
        packet = {
            "target": target_name,
            "shape": tuple(target.shape),
            "m_codes": momentum_codes,
            "m_absmax": momentum_scale,
            "v_codes": second_codes,
            "v_min_log": second_min,
            "v_delta_log": second_delta,
            "m_block_size": 256,
            "v_block_size": 2048,
        }
        torch.save(packet, save_state)
        loaded = torch.load(save_state, map_location="cpu", weights_only=True)
        assert loaded["target"] == target_name
    print(
        f"full_model=Qwen3-0.6B parameters={sum(p.numel() for p in model.parameters())} "
        f"target={target_name} target_elements={target.numel()}"
    )
    print(
        f"loss={float(output.loss.detach()):.8f} grad_norm={float(torch.linalg.vector_norm(gradient)):.8f} "
        f"AL8_v_rel_l2={rel_l2(second, second_hat):.8f} "
        f"UF8_m_rel_l2={rel_l2(momentum, momentum_hat):.8f}"
    )
    print(
        f"quantized_state_bytes={state_bytes} logits_mae={logits_mae:.8f} "
        f"last_token_cosine={cosine:.8f} generated={tokenizer.decode(generated[0])!r}"
    )
    print(
        f"saved_state={save_state or 'disabled'} elapsed_seconds={time.perf_counter() - started:.3f}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--max-elements", type=int, default=524288)
    parser.add_argument("--full-model", action="store_true")
    parser.add_argument("--prompt", default="Quantized optimizer states should preserve training stability.")
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--save-state")
    args = parser.parse_args()
    self_test()
    checkpoint = find_checkpoint(args.checkpoint)
    run_operator(checkpoint, args.max_elements)
    if args.full_model:
        run_full_model(
            checkpoint, args.prompt, args.learning_rate, save_state=args.save_state
        )


if __name__ == "__main__":
    main()
