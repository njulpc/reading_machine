#!/usr/bin/env python3
"""Audited reference paths for the 2026-09-03 quantization batch.

LLM-compatible methods exercise a real Qwen3-0.6B forward/generation path.
The driving-policy paper exercises its native MLP pipeline and marks Qwen N/A.
Paper-only kernels, datasets and hardware are never represented as reproduced.
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import platform
import time
import zlib
from pathlib import Path

import torch

MODEL_DIR = Path(
    "/Users/lipengcheng/.cache/huggingface/hub/"
    "models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca"
)
PROMPT = "量化后的模型仍应完成前向传播，并稳定生成一个新词。"
NF4 = torch.tensor(
    [-1.0, -.6961928, -.52507305, -.3949175, -.28444138, -.18477343,
     -.09105004, 0.0, .0795803, .1609302, .2461123, .33791524,
     .44070983, .562617, .72295684, 1.0], dtype=torch.float32,
)
FP4_E2M1 = torch.tensor(
    [-6., -4., -3., -2., -1.5, -1., -.5, 0., .5, 1., 1.5, 2., 3., 4., 6.],
    dtype=torch.float32,
)
FP5_E2M2 = torch.tensor(
    [-7., -6., -5., -4., -3.5, -3., -2.5, -2., -1.75, -1.5, -1.25,
     -1., -.75, -.5, -.25, 0., .25, .5, .75, 1., 1.25, 1.5, 1.75, 2.,
     2.5, 3., 3.5, 4., 5., 6., 7.], dtype=torch.float32,
)


def environment():
    import transformers
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "hardware": platform.platform(),
        "cuda": torch.cuda.is_available(),
        "mps": torch.backends.mps.is_available(),
    }


def metrics(reference, approximate):
    reference = reference.float().reshape(-1)
    approximate = approximate.float().reshape(-1)
    norm = torch.linalg.vector_norm(reference).clamp_min(1e-12)
    return {
        "mse": torch.mean((reference - approximate) ** 2).item(),
        "cosine": torch.nn.functional.cosine_similarity(
            reference.double(), approximate.double(), dim=0
        ).clamp(-1, 1).item(),
        "relative_l2": (torch.linalg.vector_norm(reference - approximate) / norm).item(),
    }


def qsym_group(x, bits, group_size, scale_bits=16):
    """Symmetric group RTN along the input dimension."""
    original = x.shape
    rows = x.float().reshape(-1, original[-1])
    padding = (-rows.shape[-1]) % group_size
    padded = torch.nn.functional.pad(rows, (0, padding)) if padding else rows
    groups = padded.reshape(rows.shape[0], -1, group_size)
    qmax = 2 ** (bits - 1) - 1
    scale = groups.abs().amax(-1, keepdim=True).clamp_min(1e-12) / qmax
    code = (groups / scale).round().clamp(-qmax, qmax)
    restored = (code * scale).reshape(rows.shape[0], -1)[:, : rows.shape[-1]]
    storage_bits = x.numel() * bits + scale.numel() * scale_bits
    return restored.reshape(original), storage_bits


def qaffine_tensor(x, bits=8):
    lo, hi = x.float().amin(), x.float().amax()
    scale = ((hi - lo) / (2**bits - 1)).clamp_min(1e-12)
    zero = (-lo / scale).round().clamp(0, 2**bits - 1)
    return ((x.float() / scale + zero).round().clamp(0, 2**bits - 1) - zero) * scale


def qnf4(x, block_size=64):
    original = x.shape
    flat = x.float().reshape(-1)
    padding = (-flat.numel()) % block_size
    padded = torch.nn.functional.pad(flat, (0, padding)) if padding else flat
    blocks = padded.reshape(-1, block_size)
    scale = blocks.abs().amax(-1, keepdim=True).clamp_min(1e-12)
    boundaries = (NF4[:-1] + NF4[1:]) / 2
    code = torch.bucketize((blocks / scale).contiguous(), boundaries)
    restored = (NF4[code] * scale).reshape(-1)[: flat.numel()].reshape(original)
    return restored, x.numel() * 4 + scale.numel() * 16


def nearest_codebook(x, codebook):
    boundaries = (codebook[:-1] + codebook[1:]) / 2
    code = torch.bucketize(x.contiguous(), boundaries)
    return codebook.to(x.device)[code]


def quantize_ue5m3_scale(x):
    """Positive E5M3-like software scale (HBQ uses unsigned FP8 ue5m3)."""
    x = x.float().clamp_min(torch.finfo(torch.float32).tiny)
    exponent = torch.floor(torch.log2(x)).clamp(-15, 16)
    fraction = x / torch.pow(2.0, exponent) - 1.0
    fraction = (fraction * 8).round().clamp(0, 7) / 8
    return (1.0 + fraction) * torch.pow(2.0, exponent)


def hbq_tensor(x, bits, micro_block, weight=False):
    """HBQ B128 + 2-bit SIG dense numerical reference."""
    original = x.shape
    rows = x.float().reshape(-1, original[-1])
    padding = (-rows.shape[-1]) % 128
    padded = torch.nn.functional.pad(rows, (0, padding)) if padding else rows
    blocks = padded.reshape(rows.shape[0], -1, 128)
    codebook = FP4_E2M1 if bits == 4 else FP5_E2M2
    l1 = quantize_ue5m3_scale(blocks.abs().amax(-1, keepdim=True) / codebook.abs().max())
    micros = blocks.reshape(rows.shape[0], -1, 128 // micro_block, micro_block)
    l1m = l1.unsqueeze(-2)

    def candidate(sig_x):
        choices = 1.0 + torch.arange(4, dtype=torch.float32) / (2**sig_x)
        reconstructions = []
        for alpha in choices:
            scale = l1m * alpha
            reconstructions.append(nearest_codebook(micros / scale, codebook) * scale)
        stack = torch.stack(reconstructions, dim=-1)
        error = (stack - micros.unsqueeze(-1)).square().mean(-2)
        best = error.argmin(-1, keepdim=True).unsqueeze(-2).expand(*micros.shape, 1)
        return stack.gather(-1, best).squeeze(-1)

    if weight:
        sig2, sig3 = candidate(2), candidate(3)
        choose3 = (sig3 - micros).square().mean((-1, -2), keepdim=True) < \
                  (sig2 - micros).square().mean((-1, -2), keepdim=True)
        restored = torch.where(choose3, sig3, sig2)
    else:
        restored = candidate(1)
    return restored.reshape(rows.shape[0], -1)[:, : rows.shape[-1]].reshape(original)


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
        directory, local_files_only=True, dtype="auto"
    ).eval()
    return tokenizer, model, directory


def block_linears(model):
    for block_index, block in enumerate(model.model.layers):
        for local_name, module in block.named_modules():
            if isinstance(module, torch.nn.Linear):
                yield block_index, f"model.layers.{block_index}.{local_name}", module


def prompt_ids(tokenizer, prompt):
    return tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids


def last_logits(model, ids, use_cache=False):
    with torch.inference_mode():
        return model(input_ids=ids, use_cache=use_cache).logits[:, -1].float()


def generate_one(model, tokenizer, ids, use_cache=False):
    with torch.inference_mode():
        output = model.generate(
            ids, attention_mask=torch.ones_like(ids), max_new_tokens=1,
            do_sample=False, use_cache=use_cache, pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0, -1:])


def quantize_all_linears(model, quantizer, predicate=lambda _name: True):
    modules = elements = 0
    layer_mae = 0.0
    with torch.no_grad():
        for _, name, module in block_linears(model):
            if not predicate(name):
                continue
            original = module.weight.float()
            quantized = quantizer(original)
            if isinstance(quantized, tuple):
                quantized = quantized[0]
            layer_mae += (original - quantized).abs().mean().item()
            module.weight.copy_(quantized.to(module.weight.dtype))
            modules += 1
            elements += module.weight.numel()
    return {
        "linear_modules": modules,
        "weight_elements": elements,
        "mean_layer_weight_mae": layer_mae / max(modules, 1),
    }


def qwen_result(model, tokenizer, ids, baseline, started, stats, status, use_cache=False):
    quantized = last_logits(model, ids, use_cache=use_cache)
    result = {
        "quantization": stats,
        "logits": metrics(baseline, quantized),
        "finite_logits": bool(torch.isfinite(quantized).all()),
        "generated_token": generate_one(model, tokenizer, ids, use_cache=use_cache),
        "qwen3_0_6b": status,
        "elapsed_seconds": time.perf_counter() - started,
    }
    assert result["finite_logits"]
    return result


def collect_input_energy(model, ids):
    energy, counts, captured = {}, {}, {}
    handles = []
    for _, name, module in block_linears(model):
        def hook(_module, inputs, key=name):
            x = inputs[0].detach().float().reshape(-1, inputs[0].shape[-1])
            energy[key] = energy.get(key, 0) + x.square().sum(0)
            counts[key] = counts.get(key, 0) + x.shape[0]
            if key.endswith("layers.0.self_attn.q_proj"):
                captured[key] = x[:64].clone()
        handles.append(module.register_forward_pre_hook(hook))
    last_logits(model, ids)
    for handle in handles:
        handle.remove()
    return {key: value / counts[key] for key, value in energy.items()}, captured


def qtea_reference(weight, diag_h, salient_ratio=.05):
    """Diagonal-Hessian QTEA representation for full-model CPU transfer."""
    rows, columns = weight.shape
    padding = (-columns) % 128
    padded = torch.nn.functional.pad(weight.float(), (0, padding)) if padding else weight.float()
    groups = padded.reshape(rows, -1, 128)
    beta = groups.mean(-1, keepdim=True)
    centered = groups - beta
    alpha = centered.abs().mean(-1, keepdim=True).clamp_min(1e-12)
    ternary = torch.zeros_like(groups)
    for _ in range(2):
        ternary = torch.where(centered > alpha / 2, 1., torch.where(centered < -alpha / 2, -1., 0.))
        alpha = (ternary * centered).sum(-1, keepdim=True).abs() / ternary.square().sum(-1, keepdim=True).clamp_min(1)
    ternary_flat = ternary.reshape(rows, -1)[:, :columns]
    group_index = torch.arange(columns) // 128
    alpha_col = alpha[:, group_index, 0]
    beta_col = beta[:, group_index, 0]
    v = torch.ones(columns)
    for _ in range(2):
        nonzero = ternary_flat != 0
        ratios = (weight.float() - beta_col).abs() / alpha_col.clamp_min(1e-12)
        v = (ratios * nonzero).sum(0) / nonzero.sum(0).clamp_min(1)
        scale = alpha_col * v.unsqueeze(0)
        centered_now = weight.float() - beta_col
        ternary_flat = torch.where(centered_now > scale / 2, 1., torch.where(centered_now < -scale / 2, -1., 0.))
    base = beta_col + alpha_col * v.unsqueeze(0) * ternary_flat
    score = weight.float().square().amax(0) * diag_h.float().square()
    selected_count = max(1, int(math.ceil(columns * salient_ratio)))
    selected_columns = torch.topk(score, selected_count).indices
    error = weight.float() - base
    residual = torch.zeros_like(error)
    selected = error[:, selected_columns].T
    row_padding = (-rows) % 4
    selected_padded = torch.nn.functional.pad(selected, (0, row_padding)) if row_padding else selected
    groups4 = selected_padded.reshape(selected_count, -1, 4)
    index = groups4.abs().argmax(-1, keepdim=True)
    sparse = torch.zeros_like(groups4).scatter(-1, index, groups4.gather(-1, index))
    residual[:, selected_columns] = sparse.reshape(selected_count, -1)[:, :rows].T
    density = (residual != 0).float().mean().item()
    return base + residual, {
        "salient_column_fraction": selected_count / columns,
        "residual_density": density,
        "effective_bpw_first_order": math.log2(3) + selected_count / columns + density * 10,
    }


def qtea_tile_with_decay(weight, activations, decay=1.0):
    """Small exact GPTQ propagation check for QTEA Eq. (6)-(9)."""
    weight = weight.detach().float().clone()
    x = activations.detach().float().clone()
    hessian = 2 * x.T @ x / max(x.shape[0], 1)
    damp = .007 * torch.diag(hessian).mean().clamp_min(1e-8)
    hessian.diagonal().add_(damp)
    inverse = torch.linalg.inv(hessian)
    diag_mean = inverse.diag().mean().clamp_min(1e-12)
    original = weight.clone()
    for column in range(weight.shape[1]):
        current = weight[:, column]
        beta = current.mean()
        alpha = (current - beta).abs().mean().clamp_min(1e-12)
        code = torch.where(current - beta > alpha / 2, 1., torch.where(current - beta < -alpha / 2, -1., 0.))
        quantized = beta + alpha * code
        diagonal = inverse[column, column]
        safe_diagonal = diagonal.sign() * diagonal.abs().clamp_min(1e-12)
        error = (current - quantized) / safe_diagonal
        weight[:, column] = quantized
        if column + 1 < weight.shape[1]:
            gamma = torch.exp(-decay * diagonal / diag_mean * column / weight.shape[1])
            weight[:, column + 1:] -= gamma * error[:, None] * inverse[column, column + 1:]
    return metrics(activations @ original.T, activations @ weight.T)


def run_00224(args):
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    baseline = last_logits(model, ids)
    diag_h, captured = collect_input_energy(model, ids)
    first = next(block_linears(model))[2]
    x = captured["model.layers.0.self_attn.q_proj"][:, :128]
    tile_check = qtea_tile_with_decay(first.weight[:64, :128].float(), x)
    totals = {"residual_density": 0., "salient_column_fraction": 0.}
    modules = elements = 0
    mae = 0.
    with torch.no_grad():
        for _, name, module in block_linears(model):
            original = module.weight.float()
            quantized, detail = qtea_reference(original, diag_h[name], args.salient_ratio)
            for key in totals: totals[key] += detail[key]
            mae += (original - quantized).abs().mean().item()
            module.weight.copy_(quantized.to(module.weight.dtype))
            modules += 1; elements += module.weight.numel()
    stats = {
        "linear_modules": modules, "weight_elements": elements,
        "mean_layer_weight_mae": mae / modules,
        "calibration_sequences": 1, "calibration_tokens": ids.numel(),
        "group_size": 128, "salient_ratio": args.salient_ratio,
        "mean_residual_density": totals["residual_density"] / modules,
        "mean_salient_column_fraction": totals["salient_column_fraction"] / modules,
        "gptq_decay_tile_output": tile_check,
    }
    return {
        "paper_id": "2609.00224", "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "QTEA diagonal-Hessian full-model reference plus exact small-tile decay check",
        "consistency": "部分一致",
        "evidence_boundary": "full model omits dense GPTQ inverse-Hessian propagation and packed LUT CUDA kernel",
        "environment": environment(),
        **qwen_result(model, tokenizer, ids, baseline, started, stats,
            "已跑通（真实整模数值路径；非论文完整 256x2048 校准/GPTQ/CUDA）"),
    }


def run_00450(args):
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    baseline = last_logits(model, ids)
    stats = quantize_all_linears(model, lambda w: hbq_tensor(w, 4, 32, weight=True))
    counters = {"activation_calls": 0, "kv_calls": 0}
    handles = []

    def activation_hook(_module, inputs):
        counters["activation_calls"] += 1
        return (hbq_tensor(inputs[0], 5, 32, weight=False).to(inputs[0].dtype), *inputs[1:])

    def kv_hook(_module, _inputs, output):
        counters["kv_calls"] += 1
        return hbq_tensor(output, 4, 32, weight=False).to(output.dtype)

    for _, name, module in block_linears(model):
        handles.append(module.register_forward_pre_hook(activation_hook))
        if name.endswith(("k_proj", "v_proj")):
            handles.append(module.register_forward_hook(kv_hook))
    result = {
        "paper_id": "2609.00450", "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "HBQ-E B128/micro-B32 W4A5 with 2-bit SIG and KV4 reference",
        "consistency": "部分一致", "environment": environment(),
        **qwen_result(model, tokenizer, ids, baseline, started, stats,
            "已跑通（真实整模 W4A5/KV4 数值路径；非 28nm HBQ/MXINT8 内核）", use_cache=True),
    }
    result.update(counters)
    for handle in handles: handle.remove()
    return result


def run_quantized_variant(args, kind, baseline):
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    if kind == "int8":
        stats = quantize_all_linears(model, lambda w: qsym_group(w, 8, w.shape[-1]))
    elif kind == "nf4":
        stats = quantize_all_linears(model, lambda w: qnf4(w, 64))
    else:
        stats = quantize_all_linears(model, lambda w: qsym_group(w, 4, 128))
    tick = time.perf_counter()
    logits = last_logits(model, ids)
    latency = time.perf_counter() - tick
    result = {"checkpoint": str(directory), "quantization": stats,
              "logits": metrics(baseline, logits), "forward_seconds": latency,
              "generated_token": generate_one(model, tokenizer, ids),
              "finite_logits": bool(torch.isfinite(logits).all())}
    del model
    gc.collect()
    return result


def run_00665(args):
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    baseline = last_logits(model, ids)
    del model
    gc.collect()
    variants = {kind: run_quantized_variant(args, kind, baseline) for kind in ("int8", "nf4", "group_w4")}
    assert all(item["finite_logits"] for item in variants.values())
    return {
        "paper_id": "2609.00665", "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "real full-model BF16/INT8/NF4/group-W4 comparison",
        "consistency": "部分一致", "environment": environment(), "variants": variants,
        "hss": "未计算：缺少论文规定的五任务能力、GPU能耗、VRAM和安全ASR测量",
        "qwen3_0_6b": "已跑通（3 个真实整模 fake-quant 路径；非 bitsandbytes/GPTQ/GGUF 后端）",
        "elapsed_seconds": time.perf_counter() - started,
    }


class Actor(torch.nn.Module):
    def __init__(self, width=256):
        super().__init__()
        self.l1 = torch.nn.Linear(18, width)
        self.l2 = torch.nn.Linear(width, width)
        self.out = torch.nn.Linear(width, 2)

    def forward(self, x):
        return torch.tanh(self.out(torch.relu(self.l2(torch.relu(self.l1(x))))))


def prune_actor(teacher, width=64):
    score1 = teacher.l1.weight.norm(dim=1) + teacher.l2.weight.norm(dim=0) + teacher.l1.bias.abs()
    keep1 = torch.topk(score1, width).indices.sort().values
    score2 = teacher.l2.weight.norm(dim=1) + teacher.out.weight.norm(dim=0) + teacher.l2.bias.abs()
    keep2 = torch.topk(score2, width).indices.sort().values
    student = Actor(width)
    with torch.no_grad():
        student.l1.weight.copy_(teacher.l1.weight[keep1]); student.l1.bias.copy_(teacher.l1.bias[keep1])
        student.l2.weight.copy_(teacher.l2.weight[keep2][:, keep1]); student.l2.bias.copy_(teacher.l2.bias[keep2])
        student.out.weight.copy_(teacher.out.weight[:, keep2]); student.out.bias.copy_(teacher.out.bias)
    return student, keep1, keep2


def run_00718(args):
    started = time.perf_counter()
    torch.manual_seed(718)
    teacher = Actor(256).eval()
    student, keep1, keep2 = prune_actor(teacher)
    phases = [torch.randn(256, 18) + offset for offset in (-1., -.5, 0., .5, 1.)]
    calibration = torch.cat(phases)
    with torch.no_grad():
        targets = teacher(calibration)
        pruned_loss = torch.nn.functional.smooth_l1_loss(student(calibration), targets).item()
    optimizer = torch.optim.Adam(student.parameters(), lr=2e-3)
    for _ in range(args.actor_steps):
        loss = torch.nn.functional.smooth_l1_loss(student(calibration), targets)
        optimizer.zero_grad(); loss.backward(); optimizer.step()
    with torch.no_grad():
        distilled_loss = torch.nn.functional.smooth_l1_loss(student(calibration), targets).item()
        for module in student.modules():
            if isinstance(module, torch.nn.Linear):
                module.weight.copy_(qsym_group(module.weight, 8, module.weight.shape[-1])[0])
        activation_ranges = {}
        handles = []
        for name, module in student.named_modules():
            if isinstance(module, torch.nn.Linear):
                def collect(_module, inputs, key=name):
                    activation_ranges[key] = (inputs[0].amin().item(), inputs[0].amax().item())
                handles.append(module.register_forward_pre_hook(collect))
        student(calibration)
        for handle in handles: handle.remove()
        qhandles = []
        for module in student.modules():
            if isinstance(module, torch.nn.Linear):
                qhandles.append(module.register_forward_pre_hook(
                    lambda _m, inp: (qaffine_tensor(inp[0], 8).to(inp[0].dtype), *inp[1:])
                ))
        quantized = student(calibration)
        quantized_loss = torch.nn.functional.smooth_l1_loss(quantized, targets).item()
        assert torch.isfinite(quantized).all()
        for handle in qhandles: handle.remove()
    teacher_params = sum(p.numel() for p in teacher.parameters())
    student_params = sum(p.numel() for p in student.parameters())
    return {
        "paper_id": "2609.00718", "algorithm": "structured hidden-unit pruning -> balanced Smooth-L1 KD -> static INT8 reference",
        "consistency": "部分一致", "environment": environment(),
        "pruning": {"teacher_width": 256, "student_width": 64,
                    "teacher_parameters": teacher_params, "student_parameters": student_params,
                    "parameter_reduction": 1 - student_params / teacher_params,
                    "kept_units": [keep1.numel(), keep2.numel()]},
        "calibration": {"source": "seeded five-phase mock states", "states": calibration.shape[0],
                        "activation_ranges": activation_ranges},
        "loss": {"pruned": pruned_loss, "distilled": distilled_loss, "int8": quantized_loss},
        "closed_loop": "未跑通：论文模拟器、62,176 状态及固定 400 episodes 未公开在本仓库",
        "qwen3_0_6b": "未跑通/不适用（论文对象是 MobileNetV3 感知 + MLP 驾驶 actor，不是 LLM）",
        "elapsed_seconds": time.perf_counter() - started,
    }


def brq_hook_factory(counter):
    def hook(_module, _inputs, output):
        x = output.float()
        batch, tokens, width = x.shape
        heads, dim = 8, width // 8
        values = x.reshape(batch, tokens, heads, dim).permute(0, 2, 1, 3)
        restored = torch.empty_like(values)
        for b in range(batch):
            for h in range(heads):
                matrix = values[b, h]
                rank = min(2, *matrix.shape)
                u, s, vh = torch.linalg.svd(matrix, full_matrices=False)
                base = (u[:, :rank] * s[:rank]) @ vh[:rank]
                residual8 = qsym_group(matrix - base, 8, dim)[0]
                order = residual8.square().mean(-1).argsort(descending=True)
                tiers = torch.zeros(tokens, dtype=torch.int64)
                cuts = [math.ceil(tokens * .25), math.ceil(tokens * .5), math.ceil(tokens * .75)]
                tiers[order[:cuts[0]]] = 8; tiers[order[cuts[0]:cuts[1]]] = 4
                tiers[order[cuts[1]:cuts[2]]] = 2
                mixed = torch.zeros_like(residual8)
                for bits in (8, 4, 2):
                    mask = tiers == bits
                    if mask.any(): mixed[mask] = qsym_group(residual8[mask], bits, dim)[0]
                restored[b, h] = base + mixed
                counter["tier_counts"]["q0"] += int((tiers == 0).sum())
                for bits in (8, 4, 2): counter["tier_counts"][f"q{bits}"] += int((tiers == bits).sum())
        counter["kv_calls"] += 1
        return restored.permute(0, 2, 1, 3).reshape_as(x).to(output.dtype)
    return hook


def run_01084(args):
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    baseline = last_logits(model, ids, use_cache=True)
    stats = quantize_all_linears(
        model, lambda w: qsym_group(qsym_group(w, 8, 128)[0], 4, 128)[0],
        predicate=lambda name: ".mlp." in name,
    )
    counter = {"kv_calls": 0, "tier_counts": {"q8": 0, "q4": 0, "q2": 0, "q0": 0}}
    handles = []
    for _, name, module in block_linears(model):
        if name.endswith(("k_proj", "v_proj")):
            handles.append(module.register_forward_hook(brq_hook_factory(counter)))
    result = {
        "paper_id": "2609.01084", "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "BRQ-KV rank-2 q8-master/q8-q4-q2-q0 views + DAT q8->q4 FFN software transfer",
        "consistency": "部分一致", "environment": environment(),
        **qwen_result(model, tokenizer, ids, baseline, started, stats,
            "已跑通（真实 Qwen AR 工程迁移；论文 Fast-dLLM v2 块扩散/WIFiV/DAT carry 未跑通）", use_cache=True),
        **counter,
    }
    for handle in handles: handle.remove()
    return result


def codec_roundtrip(x, bits):
    lo, hi = x.float().amin(), x.float().amax()
    scale = ((hi - lo) / (2**bits - 1)).clamp_min(1e-12)
    code = ((x.float() - lo) / scale).round().clamp(0, 2**bits - 1).to(torch.uint8)
    payload = zlib.compress(code.cpu().numpy().tobytes(), level=9)
    return (code.float() * scale + lo).to(x.dtype), len(payload)


def run_01200(args):
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    baseline = last_logits(model, ids)
    counter = {"codec_calls": 0, "source_bytes": 0, "payload_bytes": 0}

    def hook(_module, _inputs, output):
        restored, payload = codec_roundtrip(output, args.codec_bits)
        counter["codec_calls"] += 1
        counter["source_bytes"] += output.numel() * output.element_size()
        counter["payload_bytes"] += payload
        return restored

    handle = model.model.embed_tokens.register_forward_hook(hook)
    result = {
        "paper_id": "2609.01200", "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "training-free uniform tensor codec round-trip at the model/decoder interface",
        "consistency": "部分一致", "environment": environment(),
        **qwen_result(model, tokenizer, ids, baseline, started,
            {"quantized_object": "token embeddings", "bits": args.codec_bits},
            "已跑通（真实文本 Qwen 接口代理；非 Qwen3-VL 四路视觉接口或 ISO NNC 位流）"),
    }
    result.update(counter)
    result["compression_vs_bfloat16"] = counter["source_bytes"] / max(counter["payload_bytes"], 1)
    handle.remove()
    return result


def apply_checkpoint_quantization(model, directory, quantizer, layer=None):
    from safetensors import safe_open
    modules = {name: module for _, name, module in block_linears(model)}
    touched = 0
    with safe_open(str(directory / "model.safetensors"), framework="pt", device="cpu") as handle:
        with torch.no_grad():
            for name, module in modules.items():
                if layer is not None and not name.startswith(f"model.layers.{layer}."):
                    continue
                source = handle.get_tensor(name + ".weight").float()
                quantized = quantizer(source)
                if isinstance(quantized, tuple): quantized = quantized[0]
                module.weight.copy_(quantized.to(module.weight.dtype))
                touched += 1
    return touched


def run_01587(args):
    started = time.perf_counter()
    tokenizer, model, directory = load_model(args)
    ids = prompt_ids(tokenizer, args.prompt)
    fp = last_logits(model, ids)
    row4 = lambda w: qsym_group(w, 4, w.shape[-1])[0]
    row8 = lambda w: qsym_group(w, 8, w.shape[-1])[0]
    group4 = lambda w: qsym_group(w, 4, 128)[0]
    apply_checkpoint_quantization(model, directory, row4)
    floor = last_logits(model, ids)
    apply_checkpoint_quantization(model, directory, row8)
    ceiling = last_logits(model, ids)
    apply_checkpoint_quantization(model, directory, row4)
    floor_mse = metrics(fp, floor)["mse"]
    ceiling_mse = metrics(fp, ceiling)["mse"]
    denominator = max(floor_mse - ceiling_mse, 1e-12)
    recovery = []
    for layer in range(len(model.model.layers)):
        apply_checkpoint_quantization(model, directory, row8, layer)
        intervened = last_logits(model, ids)
        recovery.append((floor_mse - metrics(fp, intervened)["mse"]) / denominator)
        apply_checkpoint_quantization(model, directory, row4, layer)
    best = max(range(len(recovery)), key=recovery.__getitem__)
    apply_checkpoint_quantization(model, directory, row8, best)
    local_logits = last_logits(model, ids)
    local_token = generate_one(model, tokenizer, ids)
    apply_checkpoint_quantization(model, directory, group4)
    global_logits = last_logits(model, ids)
    global_token = generate_one(model, tokenizer, ids)
    global_recovery = (floor_mse - metrics(fp, global_logits)["mse"]) / denominator
    assert torch.isfinite(global_logits).all()
    return {
        "paper_id": "2609.01587", "model": "Qwen3-0.6B", "checkpoint": str(directory),
        "algorithm": "full-model per-row RTN4 causal layer sweep vs global group-128 RTN4",
        "consistency": "部分一致", "environment": environment(),
        "quantization": {"linear_modules": sum(1 for _ in block_linears(model)),
                         "weight_elements": sum(m.weight.numel() for _, _, m in block_linears(model)),
                         "per_row_effective_bpw": 4.01, "group128_effective_bpw": 4.156,
                         "matched_local_layer_count": .0365 * len(model.model.layers)},
        "causal_proxy": {"metric": "single-prompt last-logit MSE (not CORE@200)",
                         "layers_swept": len(recovery), "best_layer": best,
                         "best_layer_recovery": recovery[best], "all_layer_recovery": recovery},
        "logits": {"row4_floor": metrics(fp, floor), "row8_ceiling": metrics(fp, ceiling),
                   "local_top1": metrics(fp, local_logits), "global_group128": metrics(fp, global_logits)},
        "global_recovery": global_recovery, "global_beats_local": global_recovery > recovery[best],
        "generated_tokens": {"local": local_token, "global": global_token},
        "qwen3_0_6b": "已跑通（真实整模 28 层因果 smoke；非论文 22 任务 CORE@200/GPTQ/AWQ）",
        "elapsed_seconds": time.perf_counter() - started,
    }


RUNNERS = {
    "2609.00224": run_00224, "2609.00450": run_00450,
    "2609.00665": run_00665, "2609.00718": run_00718,
    "2609.01084": run_01084, "2609.01200": run_01200,
    "2609.01587": run_01587,
}


def self_test():
    torch.manual_seed(3)
    x = torch.randn(5, 257)
    for bits in (2, 4, 8):
        quantized, storage = qsym_group(x, bits, 128)
        assert quantized.shape == x.shape and storage > 0 and torch.isfinite(quantized).all()
    assert qnf4(x)[0].shape == x.shape
    assert hbq_tensor(x, 4, 32, weight=True).shape == x.shape
    assert hbq_tensor(x, 5, 32, weight=False).shape == x.shape
    restored, detail = qtea_reference(torch.randn(8, 128), torch.ones(128), .05)
    assert restored.shape == (8, 128) and 0 < detail["residual_density"] <= .25
    decoded, payload = codec_roundtrip(x, 4)
    assert decoded.shape == x.shape and payload > 0
    return {"status": "PASS", "checks": ["group RTN", "NF4", "HBQ SIG", "QTEA 1:4 rows", "codec round-trip"]}


def main():
    parser = argparse.ArgumentParser(description="Audited quantization reproduction")
    parser.add_argument("paper_id", choices=RUNNERS)
    parser.add_argument("--checkpoint")
    parser.add_argument("--prompt", default=PROMPT)
    parser.add_argument("--output-json")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--salient-ratio", type=float, default=.05)
    parser.add_argument("--actor-steps", type=int, default=30)
    parser.add_argument("--codec-bits", type=int, choices=(2, 4, 8), default=8)
    args = parser.parse_args()
    result = self_test() if args.self_test else RUNNERS[args.paper_id](args)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n")


if __name__ == "__main__":
    main()
