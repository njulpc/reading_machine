#!/usr/bin/env python3
"""Audited reference paths for the 2026-09-02 quantization reproductions.

The papers in this batch do not describe one common quantizer. This module keeps
their evidence boundaries separate: LLM papers run a real Qwen3-0.6B model path;
CV/GNN/skeleton papers run their native algorithmic core and explicitly report
that Qwen model quantization is not applicable.
"""
from __future__ import annotations

import argparse
import copy
import gc
import json
import math
import platform
import time
from pathlib import Path

import torch


MODEL_DIR = Path(
    "/Users/lipengcheng/.cache/huggingface/hub/"
    "models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca"
)
PROMPT = "量化后的模型仍应能够稳定完成一次前向传播并生成下一个词。"
NF4 = torch.tensor(
    [-1.0, -.6961928, -.52507305, -.3949175, -.28444138, -.18477343,
     -.09105004, 0.0, .0795803, .1609302, .2461123, .33791524,
     .44070983, .562617, .72295684, 1.0], dtype=torch.float32,
)
NVFP4 = torch.tensor(
    [-6.0, -4.0, -3.0, -2.0, -1.5, -1.0, -.5, 0.0,
     .5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0], dtype=torch.float32,
)


def environment():
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": __import__("transformers").__version__,
        "hardware": platform.platform(),
        "cuda": torch.cuda.is_available(),
        "mps": torch.backends.mps.is_available(),
    }


def metrics(ref, approx):
    ref, approx = ref.float().reshape(-1), approx.float().reshape(-1)
    return {
        "mse": torch.mean((ref - approx) ** 2).item(),
        "cosine": torch.nn.functional.cosine_similarity(ref, approx, dim=0).item(),
        "relative_l2": (
            torch.linalg.vector_norm(ref - approx).item()
            / max(torch.linalg.vector_norm(ref).item(), 1e-12)
        ),
    }


def qsym(x, bits, dim=-1, eps=1e-12):
    qmax = 2 ** (bits - 1) - 1
    scale = x.float().abs().amax(dim=dim, keepdim=True).clamp_min(eps) / qmax
    code = (x.float() / scale).round().clamp(-qmax, qmax)
    return code * scale, code, scale


def qaffine_group(x, bits, group_size=128):
    original = x.shape
    rows = x.float().reshape(-1, original[-1])
    padding = (-rows.shape[-1]) % group_size
    padded = torch.nn.functional.pad(rows, (0, padding)) if padding else rows
    groups = padded.reshape(rows.shape[0], -1, group_size)
    minimum = groups.amin(-1, keepdim=True)
    maximum = groups.amax(-1, keepdim=True)
    scale = ((maximum - minimum) / (2**bits - 1)).clamp_min(1e-12)
    zero = (-minimum / scale).round().clamp(0, 2**bits - 1)
    code = (groups / scale + zero).round().clamp(0, 2**bits - 1)
    restored = ((code - zero) * scale).reshape(rows.shape[0], -1)[:, : rows.shape[-1]]
    return restored.reshape(original), code, scale, zero


def qcodebook_blocks(x, codebook, block_size):
    original = x.shape
    flat = x.float().reshape(-1)
    padding = (-flat.numel()) % block_size
    padded = torch.nn.functional.pad(flat, (0, padding)) if padding else flat
    blocks = padded.reshape(-1, block_size)
    peak = float(codebook.abs().max())
    scale = blocks.abs().amax(-1, keepdim=True).clamp_min(1e-12) / peak
    normalized = blocks / scale
    boundaries = (codebook[:-1] + codebook[1:]) / 2
    code = torch.bucketize(normalized.contiguous(), boundaries)
    restored = codebook.to(x.device)[code] * scale
    return restored.reshape(-1)[: flat.numel()].reshape(original), code, scale


def qnf4(x, block_size=64):
    return qcodebook_blocks(x, NF4, block_size)[0]


def model_path(override=None):
    path = Path(override).expanduser() if override else MODEL_DIR
    if path.is_file():
        path = path.parent
    required = ("config.json", "model.safetensors", "tokenizer.json")
    missing = [name for name in required if not (path / name).exists()]
    if missing:
        raise FileNotFoundError(f"incomplete Qwen3-0.6B checkpoint {path}: {missing}")
    return path


def load_model(args):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_path(args.checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32,
    ).eval()
    return tokenizer, model, directory


def block_linears(model):
    for block_index, block in enumerate(model.model.layers):
        for local_name, module in block.named_modules():
            if isinstance(module, torch.nn.Linear):
                yield block_index, f"model.layers.{block_index}.{local_name}", module


def prompt_ids(tokenizer, prompt=PROMPT):
    return tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids


def logits(model, input_ids, **kwargs):
    with torch.inference_mode():
        return model(input_ids=input_ids, **kwargs).logits[:, -1].float()


def generated_token(model, tokenizer, input_ids):
    with torch.inference_mode():
        output = model.generate(
            input_ids, attention_mask=torch.ones_like(input_ids),
            max_new_tokens=1, do_sample=False, use_cache=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0, -1:])


def quantize_all_linears(model, quantizer):
    modules = elements = 0
    absolute_error = 0.0
    with torch.no_grad():
        for _, _, module in block_linears(model):
            original = module.weight.float()
            quantized = quantizer(original)
            absolute_error += (original - quantized).abs().mean().item()
            module.weight.copy_(quantized.to(module.weight.dtype))
            modules += 1
            elements += module.weight.numel()
    return {
        "linear_modules": modules,
        "weight_elements": elements,
        "mean_layer_weight_mae": absolute_error / max(modules, 1),
    }


def full_model_result(model, tokenizer, ids, baseline, quantization, started, status, extra=None):
    quantized = logits(model, ids, use_cache=False)
    result = {
        "quantization": quantization,
        "logits": metrics(baseline, quantized),
        "generated_token": generated_token(model, tokenizer, ids),
        "finite_logits": bool(torch.isfinite(quantized).all()),
        "qwen3_0_6b": status,
        "elapsed_seconds": time.perf_counter() - started,
    }
    if extra:
        result.update(extra)
    assert result["finite_logits"]
    return result


def run_qat(args):
    """Survey-compatible W4 fake-quant smoke; the survey has no unique algorithm."""
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    baseline = logits(model, ids, use_cache=False)
    first = next(block_linears(model))[2]
    original = first.weight.detach().float().clone()
    log_scale = (original.abs().amax(1, keepdim=True).clamp_min(1e-12) / 7).log().requires_grad_()
    optimizer = torch.optim.Adam([log_scale], lr=.03)
    losses = []
    for _ in range(args.steps):
        scale = log_scale.exp()
        raw = original / scale
        code = raw + (raw.round() - raw).detach()
        fake = code.clamp(-7, 7) * scale
        loss = torch.mean((fake - original) ** 2)
        optimizer.zero_grad(); loss.backward(); optimizer.step()
        losses.append(loss.item())
    optimized_first = (original / log_scale.exp()).round().clamp(-7, 7) * log_scale.exp()
    stats = quantize_all_linears(model, lambda w: qsym(w, 4, dim=1)[0])
    with torch.no_grad():
        first.weight.copy_(optimized_first)
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "survey-derived symmetric per-output W4 fake-quant with STE scale calibration",
        "consistency_scope": "engineering transfer; survey has no single method to reproduce",
        "scale_calibration_steps": args.steps,
        "first_layer_initial_mse": losses[0], "first_layer_final_mse": losses[-1],
        **full_model_result(model, tokenizer, ids, baseline, stats, started,
            "已跑通（W4 fake-quant 工程迁移；非综述中任一完整训练配方）"),
    }


def run_masq(args):
    """Native MASQ core on a deterministic skeleton-shaped sequence."""
    started = time.perf_counter()
    torch.manual_seed(29891)
    n, timesteps, joints, channels, patch = 2, 24, 8, 6, 4
    raw = torch.randn(n, timesteps, joints, channels)
    visible = torch.ones(n, joints, dtype=torch.bool)
    visible[:, ::4] = False
    dropped = raw * visible[:, None, :, None]
    patches = dropped.reshape(n, timesteps // patch, patch, joints, channels).mean(2)
    vectors = patches.reshape(-1, joints * channels)
    codebook = vectors[torch.linspace(0, len(vectors) - 1, 8).long()].clone()
    counts = torch.zeros(8); ema_sum = torch.zeros_like(codebook)
    for _ in range(8):
        ids = torch.cdist(vectors, codebook).argmin(1)
        batch_counts = torch.bincount(ids, minlength=8).float()
        batch_sum = torch.zeros_like(codebook).index_add_(0, ids, vectors)
        counts.mul_(.9).add_(batch_counts, alpha=.1)
        ema_sum.mul_(.9).add_(batch_sum, alpha=.1)
        active = counts > 0
        codebook[active] = ema_sum[active] / counts[active, None]
        for inactive in (~active).nonzero().flatten():
            codebook[inactive] = vectors[int(inactive) % len(vectors)]
    assigned = torch.cdist(vectors, codebook).argmin(1)
    quantized = codebook[assigned].reshape_as(patches)
    reconstructed = quantized.repeat_interleave(patch, dim=1)
    commitment = torch.mean((patches - quantized.detach()) ** 2).item()
    velocity_error = (reconstructed[:, 1:] - reconstructed[:, :-1] - (raw[:, 1:] - raw[:, :-1])) ** 2
    valid = visible[:, None, :, None].expand_as(velocity_error)
    velocity_loss = velocity_error[valid].mean().item()
    switches = (assigned.reshape(n, -1)[:, 1:] != assigned.reshape(n, -1)[:, :-1]).float().mean().item()
    assert torch.all(dropped[:, :, ~visible[0], :] == 0)
    return {
        "algorithm": "MASQ JLSD + temporal patches + EMA VQ + visible-only velocity loss",
        "jlsd_rate": float((~visible).float().mean()), "patch_size": patch,
        "codebook_size": len(codebook), "commitment_loss": commitment,
        "visible_velocity_loss": velocity_loss, "code_switch_rate": switches,
        "qwen3_0_6b": "未跑通/不适用（论文量化骨架动作 token，不量化 LLM 权重）",
        "validation": "结构兼容 skeleton-shaped synthetic core",
        "elapsed_seconds": time.perf_counter() - started,
    }


def dark_channel_score(image, patch=15):
    channel_min = image.amin(dim=1, keepdim=True)
    dark = -torch.nn.functional.max_pool2d(-channel_min, patch, stride=1, padding=patch // 2)
    return dark.mean(dim=(-3, -2, -1))


def quint8(x):
    minimum, maximum = x.amin(), x.amax()
    scale = ((maximum - minimum) / 255).clamp_min(1e-12)
    zero = (-minimum / scale).round().clamp(0, 255)
    code = (x / scale + zero).round().clamp(0, 255)
    return (code - zero) * scale, scale, zero


def run_adaptive_uint8(args):
    started = time.perf_counter(); torch.manual_seed(30034)
    clear = torch.rand(1, 3, 64, 64) * .4
    dense = torch.rand(1, 3, 64, 64) * .2 + .75
    batch = torch.cat((clear, dense)); score = dark_channel_score(batch); gate = score > .585
    qimage, scale, zero = quint8(batch)
    assert gate.tolist() == [False, True]
    return {
        "algorithm": "15x15 dark-channel mean gate + full-integer UINT8 numerical round trip",
        "paper_threshold": .585, "dark_channel_scores": score.tolist(), "dehazer_gate": gate.tolist(),
        "uint8_scale": scale.item(), "uint8_zero_point": int(zero), "roundtrip": metrics(batch, qimage),
        "qwen3_0_6b": "未跑通/不适用（论文对象为 TFLite dehazer/edge CNN）",
        "validation": "synthetic clear/dense-smoke gate and UINT8 operator",
        "elapsed_seconds": time.perf_counter() - started,
    }


class SkipDecoderLayer(torch.nn.Module):
    def __init__(self, attention_type):
        super().__init__(); self.attention_type = attention_type

    def forward(self, hidden_states, **kwargs):
        return hidden_states


def quantize_cache_tensor(x, bits, group_size=None):
    if bits == 8:
        minimum = x.float().amin(-1, keepdim=True); maximum = x.float().amax(-1, keepdim=True)
        scale = ((maximum - minimum) / 255).clamp_min(1e-12)
        zero = (-minimum / scale).round().clamp(0, 255)
        code = (x.float() / scale + zero).round().clamp(0, 255)
        return ((code - zero) * scale).to(x.dtype), scale.numel() * 2
    restored, _, scale, zero = qaffine_group(x, bits, group_size or 64)
    return restored.to(x.dtype), scale.numel() + zero.numel()


def quantize_cache_per_head_symmetric(x):
    """Paper-aligned budget-pipeline KV8: one symmetric scale per KV head."""
    value = x.float()
    scale = value.abs().amax(dim=(-2, -1), keepdim=True).clamp_min(1e-12) / 127
    code = (value / scale).round().clamp(-127, 127)
    return (code * scale).to(x.dtype), scale.numel()


def run_pipeline(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    base_ids = prompt_ids(tokenizer, args.prompt)
    ids = base_ids.repeat(1, math.ceil(args.tokens / base_ids.shape[1]))[:, : args.tokens]
    with torch.inference_mode(): reference = model(ids, use_cache=False, output_hidden_states=True)
    baseline = reference.logits[:, -1].float(); importance = []
    for i in range(len(model.model.layers)):
        before, after = reference.hidden_states[i].float(), reference.hidden_states[i + 1].float()
        importance.append(1 - torch.nn.functional.cosine_similarity(before.reshape(-1), after.reshape(-1), dim=0).item())
    pruned = sorted(range(len(importance)), key=lambda i: importance[i])[:3]
    stats = quantize_all_linears(model, lambda w: qaffine_group(w, 4, 128)[0])
    for index in pruned:
        old = model.model.layers[index]; model.model.layers[index] = SkipDecoderLayer(old.attention_type)
    with torch.inference_mode(): prefill = model(ids, use_cache=True)
    cache = copy.deepcopy(prefill.past_key_values); metadata = elements = initialized = 0
    for layer in cache.layers:
        if not getattr(layer, "is_initialized", False): continue
        layer.keys, count_k = quantize_cache_per_head_symmetric(layer.keys)
        layer.values, count_v = quantize_cache_per_head_symmetric(layer.values)
        metadata += count_k + count_v; elements += layer.keys.numel() + layer.values.numel(); initialized += 1
    next_id = prefill.logits[:, -1].argmax(-1, keepdim=True)
    with torch.inference_mode():
        decoded = model(next_id, past_key_values=cache, use_cache=True,
            attention_mask=torch.ones(1, ids.shape[1] + 1, dtype=torch.long)).logits[:, -1].float()
    assert torch.isfinite(decoded).all()
    payload_bits = stats["weight_elements"] * 4 + elements * 8
    metadata_bits = stats["linear_modules"] * 64 + metadata * 32
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "AWQ numerical proxy -> ShortGPT BI layer pruning -> per-head symmetric INT8 KV",
        "paper_differences": "CPU smoke uses group-128 affine RTN instead of activation-calibrated AWQ; sequence is shorter than PyramidKV window, so eviction is not claimed",
        "pruned_layers": pruned, "prune_fraction": len(pruned) / 28,
        "cache_layers": initialized, "cache_tokens": args.tokens,
        "estimated_payload_plus_metadata_bytes": (payload_bits + metadata_bits) // 8,
        "prefill_logits": metrics(baseline, prefill.logits[:, -1].float()),
        "generated_token": tokenizer.decode(decoded.argmax(-1)), "finite_logits": True,
        "quantization": stats,
        "qwen3_0_6b": "已跑通（缩短上下文的 CPU 工程迁移；非 A40/70B 完整预算实验）",
        "elapsed_seconds": time.perf_counter() - started,
    }


def nvfp4_tensor(x):
    flat = x.float().reshape(-1); padding = (-flat.numel()) % 16
    padded = torch.nn.functional.pad(flat, (0, padding)) if padding else flat
    blocks = padded.reshape(-1, 16)
    scale = blocks.abs().amax(-1, keepdim=True).clamp_min(1e-12) / 6
    fp8_limit = torch.finfo(torch.float8_e4m3fn).max
    fp8_scale = scale.clamp(max=fp8_limit).to(torch.float8_e4m3fn).float().clamp_min(1e-12)
    normalized = blocks / fp8_scale
    code = torch.bucketize(normalized.contiguous(), (NVFP4[:-1] + NVFP4[1:]) / 2)
    return (NVFP4[code] * fp8_scale).reshape(-1)[: flat.numel()].reshape_as(x)


def run_nvfp4(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt); baseline = logits(model, ids, use_cache=False)
    stats = quantize_all_linears(model, nvfp4_tensor)
    counters = {"calls": 0, "elements": 0}; handles = []
    def hook(_module, inputs):
        value = inputs[0]; counters["calls"] += 1; counters["elements"] += value.numel()
        return (nvfp4_tensor(value).to(value.dtype),) + inputs[1:]
    for _, _, module in block_linears(model): handles.append(module.register_forward_pre_hook(hook))
    result = full_model_result(model, tokenizer, ids, baseline, stats, started,
        "已跑通（dense Qwen W4A4 NVFP4 数值迁移；非 experts-only A.X K2/NVIDIA kernel）",
        {"activation_quantizer": "block-16 E2M1 with E4M3FN block scale", "activation_calls": counters})
    for handle in handles: handle.remove()
    return {"model": "Qwen3-0.6B", "checkpoint": str(directory), "algorithm": "NVFP4 block-16 W4A4", **result}


def fwht_blocks(x, block=128):
    if x.shape[-1] % block: raise ValueError("smoke path requires dimension divisible by 128")
    shape = x.shape; y = x.reshape(-1, shape[-1] // block, block).clone(); width = 1
    while width < block:
        y = y.reshape(*y.shape[:-1], -1, 2, width)
        a, b = y[..., 0, :].clone(), y[..., 1, :].clone()
        y = torch.stack((a + b, a - b), dim=-2).flatten(-3); width *= 2
    return (y / math.sqrt(block)).reshape(shape)


def rslm_rotation(x, inverse=False):
    dimension, block = x.shape[-1], 128; generator = torch.Generator().manual_seed(30384)
    sign1 = torch.where(torch.rand(dimension, generator=generator) > .5, 1.0, -1.0)
    sign2 = torch.where(torch.rand(dimension, generator=generator) > .5, 1.0, -1.0)
    permutation = torch.randperm(block, generator=generator); blocks = dimension // block
    if not inverse:
        y = fwht_blocks(x * sign1)
        y = y.reshape(-1, blocks, block)[:, :, permutation].transpose(1, 2).reshape_as(x)
        return fwht_blocks(y * sign2)
    y = fwht_blocks(x) * sign2; interleaved = y.reshape(-1, block, blocks).transpose(1, 2)
    unpermuted = torch.empty_like(interleaved); unpermuted[:, :, permutation] = interleaved
    return fwht_blocks(unpermuted.reshape_as(x)) * sign1


def fixed_gaussian_codebook_2d():
    generator = torch.Generator().manual_seed(3038401); samples = torch.randn(32768, 2, generator=generator)
    centers = samples[torch.linspace(0, len(samples) - 1, 16).long()].clone()
    for _ in range(20):
        assignment = torch.cdist(samples, centers).argmin(1)
        for k in range(16):
            if (assignment == k).any(): centers[k] = samples[assignment == k].mean(0)
    return centers


def rslm2(x):
    rotated = rslm_rotation(x); dimension = x.shape[-1]
    emax = math.sqrt(2 * math.log(2 * dimension))
    initial_scale = rotated.abs().amax(-1, keepdim=True).clamp_min(1e-12) / emax
    pairs = (rotated / initial_scale).reshape(-1, 2); centers = fixed_gaussian_codebook_2d()
    ids = torch.cdist(pairs, centers).argmin(1)
    reconstructed = centers[ids].reshape_as(rotated) * initial_scale
    decoded = rslm_rotation(reconstructed, inverse=True)
    norm_scale = x.norm(dim=-1, keepdim=True) / decoded.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    return decoded * norm_scale, ids


def run_rslm(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    base = prompt_ids(tokenizer, args.prompt)
    ids = base.repeat(1, math.ceil(args.tokens / base.shape[1]))[:, : args.tokens]
    with torch.inference_mode(): output = model(ids, output_hidden_states=True, use_cache=False)
    vectors = output.hidden_states[-1][0].float(); decoded, codes = rslm2(vectors); query = vectors[-1]
    original_rank = (vectors[:-1] @ query).topk(min(10, len(vectors) - 1)).indices
    decoded_rank = (decoded[:-1] @ query).topk(min(10, len(vectors) - 1)).indices
    overlap = len(set(original_rank.tolist()) & set(decoded_rank.tolist())) / len(original_rank)
    norm_error = (vectors.norm(dim=-1) - decoded.norm(dim=-1)).abs().max().item(); assert norm_error < 1e-4
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "RSLM2 block-128 two-pass rotation + fixed Gaussian 2D/16 codebook + norm correction",
        "vectors": len(vectors), "dimension": vectors.shape[-1], "bits_per_dimension": 2,
        "code_count": codes.numel(), "top10_overlap": overlap, "maximum_norm_error": norm_error,
        "reconstruction": metrics(vectors, decoded),
        "qwen3_0_6b": "未跑通模型权重量化/不适用；已用真实 Qwen hidden-state 完成 RSLM ANN codec 路径",
        "elapsed_seconds": time.perf_counter() - started,
    }


def toppin(adjacency):
    degree = adjacency.sum(1).clamp_min(1)
    neighbor_inverse_degree = (adjacency / degree[None, :]).sum(1) / degree
    return torch.stack((degree, neighbor_inverse_degree), dim=1)


def toppin_groups(index, count=4):
    normalized = (index - index.mean(0)) / index.std(0).clamp_min(1e-12)
    centers = normalized[torch.linspace(0, len(normalized) - 1, count).long()].clone()
    for _ in range(12):
        assignment = torch.cdist(normalized, centers).argmin(1)
        for group in range(count):
            if (assignment == group).any():
                centers[group] = normalized[assignment == group].mean(0)
    return torch.cdist(normalized, centers).argmin(1)


def run_topgq(args):
    started = time.perf_counter(); torch.manual_seed(30394); nodes, features, outputs = 32, 16, 12
    adjacency = (torch.rand(nodes, nodes) < .12).float(); adjacency.fill_diagonal_(1)
    degree = adjacency.sum(1); normalized = adjacency / degree[:, None].sqrt() / degree[None, :].sqrt()
    x, weight = torch.randn(nodes, features), torch.randn(features, outputs); combined = x @ weight
    index = toppin(adjacency); groups = toppin_groups(index)
    node_scales = combined.abs().amax(1).clamp_min(1e-12)
    for group in groups.unique():
        mask = groups == group; node_scales[mask] = node_scales[mask].max()
    scaled = combined / node_scales[:, None]
    absorbed = normalized * node_scales[None, :]
    q_absorbed = qaffine_group(absorbed, 8, absorbed.shape[-1])[0]
    q_scaled = qaffine_group(scaled.T, 8, scaled.shape[0])[0].T
    dual_axis = q_absorbed @ q_scaled
    column = qaffine_group(combined.T, 8, combined.shape[0])[0].T; column_output = normalized @ column
    reference = normalized @ combined
    selected = "dual-axis" if metrics(reference, dual_axis)["mse"] < metrics(reference, column_output)["mse"] else "column-wise"
    assert index.shape == (nodes, 2) and groups.unique().numel() >= 2
    return {
        "algorithm": "TopPIN + selective dual-axis scale absorption PTQ", "bits": 8, "nodes": nodes,
        "toppin_groups": int(groups.unique().numel()), "dual_axis": metrics(reference, dual_axis),
        "column_wise": metrics(reference, column_output), "selected": selected,
        "qwen3_0_6b": "未跑通/不适用（TopGQ 量化 GNN node activations and adjacency）",
        "validation": "synthetic inductive GCN operator path", "elapsed_seconds": time.perf_counter() - started,
    }


def run_sparse_quant(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt); baseline = logits(model, ids, use_cache=False)
    samples = {}; collection_handles = []
    for _, name, module in block_linears(model):
        def collect(_module, inputs, key=name): samples[key] = inputs[0].detach().float().abs().reshape(-1)
        collection_handles.append(module.register_forward_pre_hook(collect))
    _ = logits(model, ids, use_cache=False)
    for handle in collection_handles: handle.remove()
    thresholds = {name: value.quantile(.40) for name, value in samples.items()}
    def ternary(w):
        scale = w.float().abs().mean(1, keepdim=True).clamp_min(1e-12)
        return (w.float() / scale).round().clamp(-1, 1) * scale
    stats = quantize_all_linears(model, ternary); counters = {"elements": 0, "zeros": 0, "calls": 0}; handles = []
    for _, name, module in block_linears(model):
        delta = thresholds[name]
        def sparse_hook(_module, inputs, threshold=delta):
            value = inputs[0]; sparse = value.sign() * torch.relu(value.abs() - threshold.to(value.device))
            quantized = qsym(sparse, 8, dim=-1)[0].to(value.dtype)
            counters["elements"] += quantized.numel(); counters["zeros"] += int((quantized == 0).sum()); counters["calls"] += 1
            return (quantized,) + inputs[1:]
        handles.append(module.register_forward_pre_hook(sparse_hook))
    result = full_model_result(model, tokenizer, ids, baseline, stats, started,
        "已跑通（Qwen ternary-W/INT8-A 稀疏门工程迁移；非 MMFreeLM 4B-token 训练/Loihi 2）",
        {"sparse_activation": "sign(x)*ReLU(abs(x)-delta), per-projection calibration", "activity": counters})
    result["activity"]["sparsity"] = counters["zeros"] / max(counters["elements"], 1)
    for handle in handles: handle.remove()
    return {"model": "Qwen3-0.6B", "checkpoint": str(directory),
            "algorithm": "trainable-threshold sparse pre-activation transfer", **result}


def jsd(reference_logits, candidate_logits):
    p = reference_logits.float().softmax(-1); q = candidate_logits.float().softmax(-1); m = (p + q) / 2
    return .5 * (torch.nn.functional.kl_div(m.log(), p, reduction="batchmean")
                 + torch.nn.functional.kl_div(m.log(), q, reduction="batchmean")).item()


def run_qstrata(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt); reference = logits(model, ids, use_cache=False)
    candidate_blocks = [0, 9, 18, 27]; w3 = {}
    stats = {"linear_modules": 0, "weight_elements": 0, "mean_layer_weight_mae": 0.0}
    with torch.no_grad():
        for block_index, name, module in block_linears(model):
            original = module.weight.float(); q4 = qaffine_group(original, 4, 128)[0]
            if block_index in candidate_blocks: w3[name] = qaffine_group(original, 3, 128)[0]
            stats["mean_layer_weight_mae"] += (original - q4).abs().mean().item()
            stats["linear_modules"] += 1; stats["weight_elements"] += original.numel(); module.weight.copy_(q4)
    stats["mean_layer_weight_mae"] /= stats["linear_modules"]; base_w4 = logits(model, ids, use_cache=False)
    scores = {}; modules = {name: module for _, name, module in block_linears(model)}
    for block in candidate_blocks:
        names = [name for name in w3 if name.startswith(f"model.layers.{block}.")]
        saved = {name: modules[name].weight.detach().clone() for name in names}
        with torch.no_grad():
            for name in names: modules[name].weight.copy_(w3[name])
        scores[str(block)] = jsd(reference, logits(model, ids, use_cache=False))
        with torch.no_grad():
            for name in names: modules[name].weight.copy_(saved[name])
    selected = sorted(candidate_blocks, key=lambda block: scores[str(block)])[:2]
    with torch.no_grad():
        for block in selected:
            for name in [name for name in w3 if name.startswith(f"model.layers.{block}.")]: modules[name].weight.copy_(w3[name])
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "Q-Strata dense outer-stage smoke using model-level JSD",
        "quantizer": "group-128 asymmetric W3/W4", "candidate_blocks": candidate_blocks,
        "candidate_jsd": scores, "selected_w3_blocks": selected,
        "effective_average_block_bits": (26 * 4 + 2 * 3) / 28,
        "paper_differences": "CPU smoke samples four block candidates and one W4->W3 level; no inner HQQ/GPTQ frontier or full lazy descent",
        **full_model_result(model, tokenizer, ids, reference, stats, started,
            "已跑通（dense appendix 的缩小 JSD 外层迁移；非 MoE 完整双层搜索）",
            {"w4_baseline_jsd": jsd(reference, base_w4)}),
    }


def run_gradcodes(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt); reference = logits(model, ids, use_cache=False)
    stats = quantize_all_linears(model, lambda w: qsym(w, 4, dim=1)[0]); target = next(block_linears(model))[2]
    for parameter in model.parameters(): parameter.requires_grad_(False)
    target.weight.requires_grad_(True)
    scale = target.weight.detach().float().abs().amax(1, keepdim=True).clamp_min(1e-12) / 7
    codes = (target.weight.detach().float() / scale).round().clamp(-7, 7); initial_codes = codes.clone(); labels = ids.clone()
    losses = []; initial_loss = None; generator = torch.Generator().manual_seed(30908)
    for _ in range(max(1, min(args.steps, 3))):
        with torch.no_grad(): target.weight.copy_(codes * scale)
        output = model(ids, use_cache=False).logits
        loss = torch.nn.functional.cross_entropy(output[:, :-1].reshape(-1, output.shape[-1]), labels[:, 1:].reshape(-1))
        if initial_loss is None: initial_loss = loss.item()
        model.zero_grad(set_to_none=True); loss.backward(); gradient = target.weight.grad.detach().float()
        # Algorithm 1 updates the continuous group scale before searching codes.
        scale_gradient = (gradient * codes).mean(1, keepdim=True)
        normalized_scale_gradient = scale_gradient / scale_gradient.abs().mean().clamp_min(1e-12)
        scale = (scale - .001 * scale.mean() * normalized_scale_gradient).clamp_min(1e-12)
        code_gradient = gradient * scale; direction = -gradient.sign()
        valid = ((direction > 0) & (codes < 7)) | ((direction < 0) & (codes > -7))
        flat_score = code_gradient.abs().masked_fill(~valid, 0).reshape(-1)
        top = flat_score.topk(min(4096, int(valid.sum()))).indices
        current_loss = loss.item(); best_loss = current_loss; best_codes = codes
        for candidate_index in range(4):
            candidate = codes.clone().reshape(-1); keep = torch.rand(len(top), generator=generator) < (.35 + .15 * candidate_index)
            chosen = top[keep]; candidate[chosen] += direction.reshape(-1)[chosen]
            candidate = candidate.reshape_as(codes).clamp(-7, 7)
            with torch.no_grad(): target.weight.copy_(candidate * scale)
            candidate_output = model(ids, use_cache=False).logits
            candidate_loss = torch.nn.functional.cross_entropy(
                candidate_output[:, :-1].reshape(-1, candidate_output.shape[-1]), labels[:, 1:].reshape(-1)).item()
            if candidate_loss < best_loss: best_loss, best_codes = candidate_loss, candidate
        codes = best_codes; losses.append(best_loss); target.weight.grad = None
    with torch.no_grad(): target.weight.copy_(codes * scale)
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "GradCodeS guide-sample-evaluate-select smoke in deployable INT4 code space",
        "optimized_matrix": "model.layers.0.self_attn.q_proj", "candidate_count": 4, "iterations": len(losses),
        "initial_task_loss": initial_loss, "final_task_loss": losses[-1],
        "changed_code_fraction": (codes != initial_codes).float().mean().item(),
        "paper_differences": "all 196 linears are W4, but CPU search updates one full matrix for <=3 iterations and omits paper-scale task training",
        **full_model_result(model, tokenizer, ids, reference, stats, started,
            "已跑通（全模型 W4 + 单矩阵真实 LM-loss code search；非完整 GSM8K/Alpaca/MASSIVE 微调）"),
    }


def run_kvquant(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    base = prompt_ids(tokenizer, args.prompt); ids = base.repeat(1, math.ceil(args.tokens / base.shape[1]))[:, : args.tokens]
    with torch.inference_mode(): prefill = model(ids, use_cache=True)
    next_id = prefill.logits[:, -1].argmax(-1, keepdim=True); results = {}; dense_cache = copy.deepcopy(prefill.past_key_values)
    with torch.inference_mode():
        dense = model(next_id, past_key_values=dense_cache, use_cache=True,
            attention_mask=torch.ones(1, ids.shape[1] + 1, dtype=torch.long)).logits[:, -1].float()
    for bits in (8, 4):
        cache = copy.deepcopy(prefill.past_key_values); elements = metadata_values = layers = 0
        for layer in cache.layers:
            if not getattr(layer, "is_initialized", False): continue
            layer.keys, mk = quantize_cache_tensor(layer.keys, bits, 64)
            layer.values, mv = quantize_cache_tensor(layer.values, bits, 64)
            elements += layer.keys.numel() + layer.values.numel(); metadata_values += mk + mv; layers += 1
        with torch.inference_mode():
            candidate = model(next_id, past_key_values=cache, use_cache=True,
                attention_mask=torch.ones(1, ids.shape[1] + 1, dtype=torch.long)).logits[:, -1].float()
        # Paper storage uses one 16-bit scale and one 16-bit zero-point.
        stored_bits = elements * bits + metadata_values * 16
        results[str(bits)] = {**metrics(dense, candidate), "compression_vs_bf16": elements * 16 / stored_bits,
            "metadata_fraction": metadata_values * 16 / stored_bits,
            "generated_token": tokenizer.decode(candidate.argmax(-1)), "layers": layers}
    assert results["8"]["layers"] == 28
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "unified prefill cache -> offline quantize/store/dequantize -> one-token decode",
        "sequence_tokens": args.tokens, "quantizers": {"INT8": "per-token asymmetric", "INT4": "group-64 asymmetric"},
        "results": results,
        "paper_differences": "uses Qwen3-0.6B and a local prompt, not Qwen2.5-7B/RGB/HotpotQA faithfulness judges",
        "qwen3_0_6b": "已跑通（28 层真实 unified KV cache round-trip 与量化后 decode）",
        "elapsed_seconds": time.perf_counter() - started,
    }


def multi_prompt_logits(model, tokenizer):
    prompts = ["年龄信息不足时，应避免刻板推断。答案：", "职业信息不足时，应避免刻板推断。答案：",
               "国籍信息不足时，应避免刻板推断。答案：", "性别信息不足时，应避免刻板推断。答案："]
    values = []
    with torch.inference_mode():
        for prompt in prompts: values.append(model(prompt_ids(tokenizer, prompt), use_cache=False).logits[:, -1].float())
    return torch.cat(values), prompts


def run_stress(args):
    started = time.perf_counter(); tokenizer, model, directory = load_model(args)
    baseline, prompts = multi_prompt_logits(model, tokenizer)
    stats8 = quantize_all_linears(model, lambda w: qsym(w, 8, dim=1)[0]); int8, _ = multi_prompt_logits(model, tokenizer)
    del model; gc.collect(); tokenizer4, model4, _ = load_model(args)
    stats4 = quantize_all_linears(model4, lambda w: qnf4(w, 64)); int4, _ = multi_prompt_logits(model4, tokenizer4)
    subgroup8 = [torch.mean((baseline[i] - int8[i]) ** 2).item() for i in range(len(prompts))]
    subgroup4 = [torch.mean((baseline[i] - int4[i]) ** 2).item() for i in range(len(prompts))]
    return {
        "model": "Qwen3-0.6B", "checkpoint": str(directory), "algorithm": "responsible-evaluation quantization stress-test transfer",
        "conditions": ["FP32/BF16 proxy", "per-output symmetric INT8", "block-64 NF4"],
        "prompt_groups": ["age", "occupation", "nationality", "gender"],
        "INT8": {"overall": metrics(baseline, int8), "subgroup_mse": subgroup8, "quantization": stats8},
        "INT4": {"overall": metrics(baseline, int4), "subgroup_mse": subgroup4, "quantization": stats4},
        "paper_differences": "four local text prompts are a smoke protocol, not frozen BBQ/BBQ-V, VL models, judge scores, batching, subsets, NVML energy, or bitsandbytes kernels",
        "qwen3_0_6b": "已跑通（真实整模 INT8/NF4 前向；论文 responsible-AI benchmark 未完整复现）",
        "elapsed_seconds": time.perf_counter() - started,
    }


RUNNERS = {
    "2608.29667": run_qat, "2608.29891": run_masq, "2608.30034": run_adaptive_uint8,
    "2608.30076": run_pipeline, "2608.30181": run_nvfp4, "2608.30384": run_rslm,
    "2608.30394": run_topgq, "2608.30439": run_sparse_quant, "2608.30564": run_qstrata,
    "2608.30908": run_gradcodes, "2608.30996": run_kvquant, "2608.31108": run_stress,
}


def run(paper_id):
    parser = argparse.ArgumentParser(description=f"Audited reproduction for arXiv:{paper_id}")
    parser.add_argument("--checkpoint", help="local Qwen3-0.6B directory or model.safetensors")
    parser.add_argument("--prompt", default=PROMPT); parser.add_argument("--tokens", type=int, default=64)
    parser.add_argument("--steps", type=int, default=3); parser.add_argument("--output-json")
    args = parser.parse_args(); torch.manual_seed(20260902)
    result = {"paper_id": paper_id, "review_date": "2026-09-02", "environment": environment(), **RUNNERS[paper_id](args)}
    text = json.dumps(result, ensure_ascii=False, indent=2); print(text)
    if args.output_json:
        output = Path(args.output_json); output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    return result
