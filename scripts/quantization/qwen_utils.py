#!/usr/bin/env python3
"""Audited numerical references for the 2026-09-04 quantization batch.

The functions intentionally distinguish paper-faithful operators from Qwen3-0.6B
engineering transfers. A PASS means that the declared path executed; it does
not turn a vision-only, tokenizer-only, CUDA-only, or pretraining method into a
full reproduction on Qwen.
"""
from __future__ import annotations

import argparse
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
PROMPTS = [
    "模型压缩需要同时验证精度和真实存储。",
    "低比特推理应报告量化误差与部署边界。",
    "校准样本需要覆盖不同的激活统计。",
    "稀疏与量化可以共享统一的预算视角。",
    "教师模型提供软目标，学生负责部署。",
    "长上下文推理的缓存带来显存瓶颈。",
    "硬件内核决定理论压缩是否转化为加速。",
    "公平比较必须控制码率和输入分布。",
]
EVAL_PROMPT = "端到端验证必须使用独立输入，并区分算法复现与工程代理。"


def metrics(a: torch.Tensor, b: torch.Tensor) -> dict[str, float]:
    a = a.float().reshape(-1)
    b = b.float().reshape(-1)
    return {
        "mse": torch.mean((a - b) ** 2).item(),
        "mae": torch.mean((a - b).abs()).item(),
        "cosine": torch.nn.functional.cosine_similarity(
            a.double(), b.double(), dim=0
        ).item(),
        "relative_l2": (
            torch.linalg.vector_norm(a - b)
            / torch.linalg.vector_norm(a).clamp_min(1e-12)
        ).item(),
    }


def environment() -> dict[str, object]:
    import transformers

    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "platform": platform.platform(),
        "cuda": torch.cuda.is_available(),
        "mps": torch.backends.mps.is_available(),
    }


def load():
    from transformers import AutoModelForCausalLM, AutoTokenizer

    for filename in ("config.json", "model.safetensors", "tokenizer.json"):
        if not (MODEL_DIR / filename).exists():
            raise FileNotFoundError(MODEL_DIR / filename)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR, local_files_only=True, dtype="auto"
    ).eval()
    return tokenizer, model


def ids_for(tokenizer, prompt: str) -> torch.Tensor:
    return tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids


def logits(model, input_ids: torch.Tensor) -> torch.Tensor:
    with torch.inference_mode():
        return model(input_ids=input_ids, use_cache=False).logits[0, -1].float()


def generated_token(tokenizer, model, input_ids: torch.Tensor) -> dict[str, object]:
    with torch.inference_mode():
        output = model.generate(
            input_ids,
            max_new_tokens=1,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(input_ids),
        )
    token_id = int(output[0, -1])
    return {"token_id": token_id, "text": tokenizer.decode([token_id])}


def backbone_linears(model):
    return [
        (name, module)
        for name, module in model.named_modules()
        if isinstance(module, torch.nn.Linear) and name != "lm_head"
    ]


def qsym(x: torch.Tensor, bits: int, axis: int | None = -1) -> torch.Tensor:
    source_dtype = x.dtype
    x = x.float()
    qmax = 2 ** (bits - 1) - 1
    if axis is None:
        bound = x.abs().amax()
    else:
        bound = x.abs().amax(dim=axis, keepdim=True)
    scale = bound.clamp_min(1e-12) / qmax
    return ((x / scale).round().clamp(-qmax, qmax) * scale).to(source_dtype)


def qaffine(
    x: torch.Tensor, lower: float | torch.Tensor, upper: float | torch.Tensor, bits: int
) -> torch.Tensor:
    source_dtype = x.dtype
    work = x.float()
    lower = torch.as_tensor(lower, dtype=torch.float32, device=x.device)
    upper = torch.as_tensor(upper, dtype=torch.float32, device=x.device)
    step = (upper - lower).clamp_min(1e-12) / (2**bits - 1)
    return (((work.clamp(lower, upper) - lower) / step).round() * step + lower).to(source_dtype)


def quantize_weights(model, quantizer) -> tuple[int, int, int]:
    count = elements = metadata = 0
    with torch.no_grad():
        for name, module in backbone_linears(model):
            original = module.weight.detach().float()
            quantized, extra = quantizer(name, original)
            module.weight.copy_(quantized.to(module.weight.dtype))
            count += 1
            elements += original.numel()
            metadata += int(extra)
    return count, elements, metadata


def evaluate(tokenizer, model, input_ids, reference, *, generate=False):
    current = logits(model, input_ids)
    result = {
        "logits": metrics(reference, current),
        "finite_logits": bool(torch.isfinite(current).all()),
    }
    if generate:
        result["generation"] = generated_token(tokenizer, model, input_ids)
    return result


def collect_linear_bounds(tokenizer, model, prompt_indices):
    state: dict[str, dict[str, object]] = {}
    handles = []
    for name, module in backbone_linears(model):
        state[name] = {
            "min": math.inf,
            "max": -math.inf,
            "lower": None,
            "upper": None,
            "step": 0,
        }

        def hook(_module, args, key=name):
            x = args[0].detach().float().flatten()
            stride = max(1, x.numel() // 100_000)
            sample = x[::stride]
            item = state[key]
            item["min"] = min(float(item["min"]), sample.min().item())
            item["max"] = max(float(item["max"]), sample.max().item())
            lower = torch.quantile(sample, 0.001).item()
            upper = torch.quantile(sample, 0.999).item()
            step = int(item["step"])
            alpha = 0.2 / (1.0 + 0.01 * step)
            item["lower"] = (
                lower
                if item["lower"] is None
                else (1 - alpha) * float(item["lower"]) + alpha * lower
            )
            item["upper"] = (
                upper
                if item["upper"] is None
                else (1 - alpha) * float(item["upper"]) + alpha * upper
            )
            item["step"] = step + 1

        handles.append(module.register_forward_pre_hook(hook))
    for index in prompt_indices:
        logits(model, ids_for(tokenizer, PROMPTS[index]))
    for handle in handles:
        handle.remove()
    return state


def activation_quant_hooks(model, bounds, mode):
    handles = []
    for name, module in backbone_linears(model):
        item = bounds[name]
        lower, upper = (
            (item["min"], item["max"])
            if mode == "minmax"
            else (item["lower"], item["upper"])
        )

        def hook(_module, args, lo=lower, hi=upper):
            return (qaffine(args[0], lo, hi, 8),) + args[1:]

        handles.append(module.register_forward_pre_hook(hook))
    return handles


def remove_handles(handles):
    for handle in handles:
        handle.remove()


def run_01683(tokenizer, model):
    """FORGE formula transferred to three Transformer inputs."""
    input_ids = ids_for(tokenizer, PROMPTS[0])
    dense = logits(model, input_ids)
    selected = {
        "model.layers.0.self_attn.q_proj",
        "model.layers.13.self_attn.q_proj",
        "model.layers.27.self_attn.q_proj",
    }
    clean: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}
    handles = []
    for name, module in backbone_linears(model):
        if name not in selected:
            continue

        def capture(_module, args, key=name):
            x = args[0].detach().float()
            dims = tuple(range(x.ndim - 1))
            clean[key] = (
                x.mean(dims),
                x.var(dims, unbiased=False).sqrt().clamp_min(1e-5),
            )

        handles.append(module.register_forward_pre_hook(capture))
    logits(model, ids_for(tokenizer, " ".join(PROMPTS)))
    remove_handles(handles)
    count, elements, _ = quantize_weights(
        model, lambda _name, weight: (qsym(weight, 8, 1), 0)
    )
    clean_int8 = evaluate(tokenizer, model, input_ids, dense)

    mode = {"name": "corrupt"}
    running = {
        key: [mean.clone(), std.square()] for key, (mean, std) in clean.items()
    }
    handles = []
    for name, module in backbone_linears(model):
        if name not in selected:
            continue
        width = module.in_features
        gain = torch.linspace(0.65, 1.55, width)
        bias = 0.12 * torch.sin(torch.arange(width).float())

        def adapt(_module, args, key=name, g=gain, b=bias):
            x = args[0]
            corrupted = x * g.to(x.dtype) + b.to(x.dtype)
            if mode["name"] == "forge":
                work = corrupted.float()
                dims = tuple(range(work.ndim - 1))
                batch_mean = work.mean(dims)
                batch_var = work.var(dims, unbiased=False)
                momentum = 0.1
                running[key][0].mul_(1 - momentum).add_(batch_mean, alpha=momentum)
                running[key][1].mul_(1 - momentum).add_(batch_var, alpha=momentum)
                beta, gamma = clean[key]
                work = (work - running[key][0]) / running[key][1].sqrt().clamp_min(1e-5)
                corrupted = work * gamma + beta
            return (qsym(corrupted, 8, None).to(x.dtype),) + args[1:]

        handles.append(module.register_forward_pre_hook(adapt))
    raw = evaluate(tokenizer, model, input_ids, dense)
    mode["name"] = "forge"
    for key, (mean, std) in clean.items():
        running[key] = [mean.clone(), std.square()]
    adapted = evaluate(tokenizer, model, input_ids, dense, generate=True)
    remove_handles(handles)
    return {
        "algorithm": "FORGE equation (EMA mean/variance -> clean beta/abs(gamma)) on three Transformer proxy sites",
        "paper_method_applicable_to_qwen": False,
        "qwen_transfer_status": "PASS",
        "selected_sites": sorted(selected),
        "ema_momentum": 0.1,
        "weight_quantization": "all backbone Linear, per-output-channel symmetric INT8 fake quant",
        "quantized_linears": count,
        "quantized_weight_elements": elements,
        "dense_to_clean_int8": clean_int8,
        "dense_to_corrupted_int8": raw,
        "dense_to_forge_transfer": adapted,
        "boundary": "Qwen has no folded Conv-BN sites; clean empirical Transformer-input statistics replace beta/abs(gamma).",
    }


def run_01743(tokenizer, model):
    input_ids = ids_for(tokenizer, EVAL_PROMPT)
    dense = logits(model, input_ids)
    probe = model.model.embed_tokens.weight[:1024].detach().float()
    standardized = (probe - probe.mean()) / probe.std(unbiased=False).clamp_min(1e-12)
    skewness = standardized.pow(3).mean()
    kurtosis = standardized.pow(4).mean()
    uadr = 0.01 * torch.relu(skewness).square() + 0.01 * torch.relu(
        kurtosis - 3
    ).square()
    bounds = collect_linear_bounds(tokenizer, model, range(len(PROMPTS)))
    count, elements, _ = quantize_weights(
        model, lambda _name, weight: (qsym(weight, 4, 1), 0)
    )
    handles = activation_quant_hooks(model, bounds, "minmax")
    minmax = evaluate(tokenizer, model, input_ids, dense)
    remove_handles(handles)
    handles = activation_quant_hooks(model, bounds, "percentile")
    percentile = evaluate(tokenizer, model, input_ids, dense, generate=True)
    remove_handles(handles)
    return {
        "algorithm": "SCULPT deployment contract transferred to Qwen: W4 per-channel + A8 asymmetric with frozen 0.001/0.999 bounds",
        "paper_training_reproduced": False,
        "qwen_transfer_status": "PASS",
        "calibration_prompts": len(PROMPTS),
        "paper_calibration_batches": 32,
        "percentiles": [0.001, 0.999],
        "inverse_time_alpha": "0.2/(1+0.01*t)",
        "uadr_operator_probe": {
            "skewness": skewness.item(),
            "kurtosis": kurtosis.item(),
            "loss_alpha_beta_0_01": uadr.item(),
        },
        "quantized_linears": count,
        "quantized_weight_elements": elements,
        "minmax_w4a8": minmax,
        "percentile_w4a8": percentile,
        "boundary": "The public Qwen checkpoint was not fine-tuned with UADR/SPC; pre-Linear calibration is an engineering transfer, not SCULPT training.",
    }


def collect_hdiag(tokenizer, model):
    stats: dict[str, torch.Tensor] = {}
    handles = []
    for name, module in backbone_linears(model):

        def hook(_module, args, key=name):
            x = args[0].detach().float().reshape(-1, args[0].shape[-1])
            stats[key] = x.square().mean(0)

        handles.append(module.register_forward_pre_hook(hook))
    logits(model, ids_for(tokenizer, " ".join(PROMPTS)))
    remove_handles(handles)
    return stats


def e2m_atq_blockwise(weight, hdiag, group_size=128):
    output = torch.empty_like(weight)
    second_total = 0
    for start in range(0, weight.shape[1], group_size):
        block = weight[:, start : start + group_size]
        mean = block.mean(1, keepdim=True)
        centered = block - mean
        threshold = 0.75 * centered.abs().mean(1, keepdim=True)
        plane0 = torch.where(
            centered > threshold,
            1.0,
            torch.where(centered < -threshold, -1.0, 0.0),
        )
        alpha0 = (plane0 * centered).sum(1, keepdim=True) / plane0.square().sum(
            1, keepdim=True
        ).clamp_min(1)
        residual = centered - alpha0 * plane0
        threshold1 = 0.75 * residual.abs().mean(1, keepdim=True)
        candidate1 = torch.where(
            residual > threshold1,
            1.0,
            torch.where(residual < -threshold1, -1.0, 0.0),
        )
        score = centered.abs() * hdiag[
            start : start + block.shape[1]
        ].sqrt().clamp_min(1e-12)
        k = max(1, round(block.shape[1] * 0.036))
        salient = torch.zeros_like(block, dtype=torch.bool)
        salient.scatter_(1, score.topk(k, dim=1).indices, True)
        plane1 = candidate1 * salient
        alpha1 = (plane1 * residual).sum(1, keepdim=True) / plane1.square().sum(
            1, keepdim=True
        ).clamp_min(1)
        for _ in range(15):
            mean = (block - alpha0 * plane0 - alpha1 * plane1).mean(
                1, keepdim=True
            )
            centered = block - mean
            alpha0 = (
                (plane0 * (centered - alpha1 * plane1)).sum(1, keepdim=True)
                / plane0.square().sum(1, keepdim=True).clamp_min(1)
            )
            alpha1 = (
                (plane1 * (centered - alpha0 * plane0)).sum(1, keepdim=True)
                / plane1.square().sum(1, keepdim=True).clamp_min(1)
            )
        output[:, start : start + block.shape[1]] = (
            mean + alpha0 * plane0 + alpha1 * plane1
        )
        second_total += int(salient.sum())
    return output, second_total


def run_01962(tokenizer, model):
    input_ids = ids_for(tokenizer, EVAL_PROMPT)
    dense = logits(model, input_ids)
    hdiag = collect_hdiag(tokenizer, model)
    second = {"count": 0}

    def quantizer(name, weight):
        converted, n_second = e2m_atq_blockwise(weight, hdiag[name])
        second["count"] += n_second
        return converted, 0

    count, elements, _ = quantize_weights(model, quantizer)
    result = evaluate(tokenizer, model, input_ids, dense, generate=True)
    fraction = second["count"] / elements
    return {
        "algorithm": "group-128 E2M-ATQ order-[2,2,1,1] transfer with Hessian-diagonal salience proxy",
        "paper_pipeline_reproduced": False,
        "qwen_transfer_status": "PASS",
        "calibration": {
            "prompts": len(PROMPTS),
            "tokens": int(ids_for(tokenizer, " ".join(PROMPTS)).numel()),
            "paper": "64 WikiText-2 samples x 2048 tokens",
        },
        "group_size": 128,
        "threshold_factor": 0.75,
        "refinement_iterations": 15,
        "second_plane_fraction": fraction,
        "symbol_only_effective_bpw": (1 + fraction) * math.log2(3),
        "quantized_linears": count,
        "quantized_weight_elements": elements,
        "quantized_model": result,
        "boundary": "No learned KOTMS checkpoint and no inverse-Hessian column propagation; salience uses w^2*diag(H), embeddings/lm_head stay floating, payload is fake-quantized rather than packed.",
    }


def fit_kmeans(train, k, steps=20):
    centers = train[torch.linspace(0, len(train) - 1, k).long()].clone()
    for _ in range(steps):
        labels = torch.cdist(train, centers).argmin(1)
        updated = torch.stack(
            [
                train[labels == index].mean(0)
                if (labels == index).any()
                else centers[index]
                for index in range(k)
            ]
        )
        if torch.allclose(updated, centers):
            break
        centers = updated
    return centers


def assign(test, centers):
    return centers[torch.cdist(test, centers).argmin(1)]


def run_02107(_tokenizer, model):
    embeddings = model.model.embed_tokens.weight[:5120, :8].detach().float()
    train, test = embeddings[:4096], embeddings[4096:]
    scalar_parts = []
    for column in range(8):
        centers = fit_kmeans(train[:, column : column + 1], 2)
        scalar_parts.append(assign(test[:, column : column + 1], centers))
    scalar = torch.cat(scalar_parts, 1)
    product = torch.cat(
        [
            assign(test[:, :4], fit_kmeans(train[:, :4], 16)),
            assign(test[:, 4:], fit_kmeans(train[:, 4:], 16)),
        ],
        1,
    )
    vector = assign(test, fit_kmeans(train, 256))
    return {
        "algorithm": "matched-source, matched-K=256 intrinsic rate-distortion comparison",
        "paper_method_applicable_to_qwen_model_quantization": False,
        "qwen_embedding_tensor_status": "PASS",
        "train_vectors": len(train),
        "test_vectors": len(test),
        "dimension": 8,
        "rate_bits_per_vector": 8,
        "scalar_8x2": metrics(test, scalar),
        "product_2x16": metrics(test, product),
        "vector_1x256": metrics(test, vector),
        "codebook_float_entries": {
            "scalar": 16,
            "product": 128,
            "vector": 2048,
        },
        "boundary": "This paper studies discrete visual-token latent quantizers, not LLM weight quantization; codebook storage and tokenizer reconstruction are outside this intrinsic split test.",
    }


def avis_scores(tokenizer, model):
    scores = []
    layers = list(model.model.layers)
    for prompt in PROMPTS:
        values = []
        handles = []
        for layer in layers:

            def hook(_module, _args, output):
                x = output[0] if isinstance(output, tuple) else output
                x = x.detach().float()
                values.append(x.var(dim=-2, unbiased=False).mean().item())

            handles.append(layer.register_forward_hook(hook))
        logits(model, ids_for(tokenizer, prompt))
        remove_handles(handles)
        scores.append(sum(values) / len(values))
    return scores


def collect_calibration(tokenizer, model, indices):
    state = {}
    handles = []
    for name, module in backbone_linears(model):
        state[name] = {
            "min": math.inf,
            "max": -math.inf,
            "sum": torch.zeros(module.in_features),
            "count": 0,
        }

        def hook(_module, args, key=name):
            x = args[0].detach().float().reshape(-1, args[0].shape[-1])
            item = state[key]
            item["min"] = min(float(item["min"]), x.min().item())
            item["max"] = max(float(item["max"]), x.max().item())
            item["sum"] += x.sum(0)
            item["count"] += len(x)

        handles.append(module.register_forward_pre_hook(hook))
    for index in indices:
        logits(model, ids_for(tokenizer, PROMPTS[index]))
    remove_handles(handles)
    for item in state.values():
        item["mean"] = item.pop("sum") / int(item["count"])
    return state


def calibrated_hooks(model, calibration, corrections):
    handles = []
    for name, module in backbone_linears(model):
        item = calibration[name]

        def pre(_module, args, lo=item["min"], hi=item["max"]):
            return (qaffine(args[0], lo, hi, 8),) + args[1:]

        def post(_module, _args, output, correction=corrections[name]):
            return output + correction.to(output.dtype)

        handles.extend(
            [module.register_forward_pre_hook(pre), module.register_forward_hook(post)]
        )
    return handles


def run_02219(tokenizer, model):
    input_ids = ids_for(tokenizer, EVAL_PROMPT)
    dense = logits(model, input_ids)
    scores = avis_scores(tokenizer, model)
    avis = sorted(
        [index for index, score in enumerate(scores) if score > 0],
        key=lambda index: scores[index],
        reverse=True,
    )[:4]
    random = [0, 2, 4, 6]
    random_cal = collect_calibration(tokenizer, model, random)
    avis_cal = collect_calibration(tokenizer, model, avis)
    corrections = {"random": {}, "avis": {}}

    def quantizer(name, weight):
        quantized = qsym(weight, 8, 1)
        error = weight - quantized
        corrections["random"][name] = random_cal[name]["mean"] @ error.T
        corrections["avis"][name] = avis_cal[name]["mean"] @ error.T
        return quantized, 0

    count, elements, _ = quantize_weights(model, quantizer)
    handles = calibrated_hooks(model, random_cal, corrections["random"])
    random_result = evaluate(tokenizer, model, input_ids, dense)
    remove_handles(handles)
    handles = calibrated_hooks(model, avis_cal, corrections["avis"])
    avis_result = evaluate(tokenizer, model, input_ids, dense, generate=True)
    remove_handles(handles)
    return {
        "algorithm": "AVIS score mean_l mean_c Var_token(A_l,c), deterministic positive Top-K, W8A8 and analytical weight-bias correction",
        "paper_method_applicable_to_qwen": False,
        "qwen_transfer_status": "PASS",
        "candidate_scores": scores,
        "random_indices": random,
        "avis_indices": avis,
        "calibration_samples": 4,
        "scored_layers": len(model.model.layers),
        "quantized_linears": count,
        "quantized_weight_elements": elements,
        "random_calibration": random_result,
        "avis_calibration": avis_result,
        "boundary": "Token variance substitutes for image HxW variance; this is not YOLO/Vitis-AI/XMODEL, lunar data, DPU execution, or radiation criticality analysis.",
    }


def pack_planes14(class_id: int, gain: int, sign_mask: int, levels: list[int]) -> bytes:
    if not 0 <= class_id < 512 or gain not in (0, 1) or len(levels) != 24:
        raise ValueError("invalid Planes14 field")
    record = class_id | (gain << 9) | ((sign_mask & ((1 << 24) - 1)) << 10)
    for plane in range(3):
        mask = sum(
            ((level >> plane) & 1) << index
            for index, level in enumerate(levels)
        )
        record |= mask << (34 + 24 * plane)
    return record.to_bytes(14, "little")


def unpack_planes14(record: bytes):
    value = int.from_bytes(record, "little")
    levels = []
    for index in range(24):
        levels.append(
            sum(
                ((value >> (34 + 24 * plane + index)) & 1) << plane
                for plane in range(3)
            )
        )
    return {
        "class_id": value & 0x1FF,
        "gain": (value >> 9) & 1,
        "sign_mask": (value >> 10) & ((1 << 24) - 1),
        "levels": levels,
        "padding": value >> 106,
    }


def run_02652(_tokenizer, model):
    weight = (
        model.model.layers[0]
        .self_attn.q_proj.weight[:128]
        .detach()
        .float()
        .flatten()
    )
    pad = (-weight.numel()) % 24
    blocks = torch.nn.functional.pad(weight, (0, pad)).reshape(-1, 24)
    records = []
    for block in blocks:
        bound = block.abs().max().clamp_min(1e-12)
        levels = (
            ((block.abs() / bound) * 4)
            .round()
            .clamp(0, 4)
            .to(torch.int64)
            .tolist()
        )
        sign_mask = sum(int(block[index] < 0) << index for index in range(24))
        record = pack_planes14(
            1,
            int(block.square().mean().sqrt() > block.abs().mean()),
            sign_mask,
            levels,
        )
        decoded = unpack_planes14(record)
        assert decoded["class_id"] == 1 and decoded["sign_mask"] == sign_mask
        assert decoded["levels"] == levels and decoded["padding"] == 0
        records.append(record)
    return {
        "algorithm": "Planes14 fixed-record pack/shift/mask geometry verification on synthetic fields derived from real Qwen weights",
        "exact_llvq_quantizer_run": False,
        "real_qwen3_0_6b_quantization": False,
        "records": len(records),
        "record_bytes": 14,
        "payload_bits": 106,
        "padding_bits": 6,
        "layout_stream_bpw": 112 / 24,
        "paper_whole_model_kernel_bpw": 4.804,
        "paper_on_disk_effective_bpw": 2.07,
        "roundtrip": "PASS",
        "boundary": "The 301-class Leech encoder, 47-bit index, class table, gain centroids, row scales, KOTMS rotation, sealed Qwen3-4B artifact, and CUDA kernel are not present; synthetic levels test bit geometry only and are not validated Leech records.",
    }


def round_float_format(x, *, signed, bias, fraction_bits, max_finite):
    work = x.float()
    if not signed and bool((work < 0).any()):
        raise ValueError("unsigned format received a negative value")
    negative = (
        torch.signbit(work)
        if signed
        else torch.zeros_like(work, dtype=torch.bool)
    )
    magnitude = work.abs() if signed else work
    nonzero = magnitude != 0
    safe = torch.where(nonzero, magnitude, torch.ones_like(magnitude))
    _, exponent = torch.frexp(safe)
    exponent = torch.clamp_min(exponent - 1, 1 - bias)
    quantum_exp = exponent - (fraction_bits + 1) + 1
    significand = torch.ldexp(safe, -quantum_exp)
    lower = torch.floor(significand)
    delta = significand - lower
    odd = lower.to(torch.int64).bitwise_and(1).bool()
    rounded = torch.ldexp(
        lower + ((delta > 0.5) | ((delta == 0.5) & odd)), quantum_exp
    )
    rounded = torch.where(nonzero, rounded, torch.zeros_like(rounded)).clamp(
        max=max_finite
    )
    return torch.where(negative, -rounded, rounded)


def round_e2m1(x):
    return round_float_format(
        x, signed=True, bias=1, fraction_bits=1, max_finite=6.0
    )


def round_ue5m3(x):
    return round_float_format(
        x, signed=False, bias=15, fraction_bits=3, max_finite=61_440.0
    )


def ue5m3_fp4(tensor, *, two_dimensional):
    work = tensor.float()
    reference = work.abs().amax()
    encode = torch.where(
        reference == 0, torch.ones_like(reference), 448.0 * 6.0 / reference
    )
    if two_dimensional:
        rows, columns = work.shape
        padded_rows = math.ceil(rows / 16) * 16
        padded_columns = math.ceil(columns / 16) * 16
        padded = torch.nn.functional.pad(
            work.abs(), (0, padded_columns - columns, 0, padded_rows - rows)
        )
        block_amax = padded.reshape(
            padded_rows // 16, 16, padded_columns // 16, 16
        ).amax(dim=(1, 3))

        def expand(scales):
            return (
                scales[:, None, :, None]
                .expand(padded_rows // 16, 16, padded_columns // 16, 16)
                .reshape(padded_rows, padded_columns)[:rows, :columns]
            )

    else:
        width = work.shape[-1]
        padded_width = math.ceil(width / 16) * 16
        padded = torch.nn.functional.pad(work.abs(), (0, padded_width - width))
        leading = padded.shape[:-1]
        block_amax = padded.reshape(*leading, padded_width // 16, 16).amax(-1)

        def expand(scales):
            return (
                scales[..., :, None]
                .expand(*leading, padded_width // 16, 16)
                .reshape(*leading, padded_width)[..., :width]
            )

    scale_codes = round_ue5m3((block_amax * encode) * (1.0 / 6.0)).clamp(
        max=61_440.0
    )
    scale_codes = torch.where(
        scale_codes == 0, torch.ones_like(scale_codes), scale_codes
    )
    decoded_scale = expand(scale_codes) / encode
    payload = round_e2m1(work * torch.reciprocal(decoded_scale))
    return payload * decoded_scale, scale_codes.numel()


def run_02846(tokenizer, model):
    input_ids = ids_for(tokenizer, PROMPTS[3])
    dense = logits(model, input_ids)
    count, elements, scale_count = quantize_weights(
        model, lambda _name, weight: ue5m3_fp4(weight, two_dimensional=True)
    )
    handles = []
    for _name, module in backbone_linears(model):

        def hook(_module, args):
            quantized, _ = ue5m3_fp4(args[0], two_dimensional=False)
            return (quantized.to(args[0].dtype),) + args[1:]

        handles.append(module.register_forward_pre_hook(hook))
    result = evaluate(tokenizer, model, input_ids, dense, generate=True)
    remove_handles(handles)
    return {
        "algorithm": "E2M1 payload + exact finite UE5M3 scale value set, block-16, 2D weights, current-tensor inference scaling",
        "paper_pretraining_reproduced": False,
        "qwen_inference_transfer_status": "PASS",
        "quantized_linears": count,
        "quantized_weight_elements": elements,
        "weight_scale_codes": scale_count,
        "estimated_fake_quant_payload_bytes": math.ceil(elements * 4 / 8)
        + scale_count,
        "scale_target": 448,
        "weight_block": "16x16",
        "activation_block": 16,
        "qwen_w4a4": result,
        "boundary": "Inference transfer uses current amax (D=1); it does not reproduce D=50 pretraining, separate operand caches, stochastic dY, backward GEMMs, native/probe-matched accumulation, Nemotron-H, or throughput.",
    }


def core_self_test():
    x = torch.tensor([[-1.0, -0.25, 0.0, 0.75, 6.0]])
    assert torch.isfinite(qsym(x, 4, None)).all()
    expected_e2m1 = torch.tensor(
        [-6.0, -1.0, -0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 2.0, 2.0, 4.0, 4.0, 6.0]
    )
    test_e2m1 = torch.tensor(
        [-100.0, -0.75, -0.25, 0.0, 0.25, 0.5, 0.75, 1.25, 1.75, 2.5, 3.5, 5.0, 100.0]
    )
    torch.testing.assert_close(round_e2m1(test_e2m1), expected_e2m1)
    test_ue = torch.tensor(
        [0.0, 2.0**-18, 2.0**-17, 2.0**-14, 61_440.0, 100_000.0]
    )
    expected_ue = torch.tensor(
        [0.0, 0.0, 2.0**-17, 2.0**-14, 61_440.0, 61_440.0]
    )
    torch.testing.assert_close(round_ue5m3(test_ue), expected_ue)
    levels = [index % 5 for index in range(24)]
    decoded = unpack_planes14(pack_planes14(300, 1, 0xA5A5A5, levels))
    assert decoded == {
        "class_id": 300,
        "gain": 1,
        "sign_mask": 0xA5A5A5,
        "levels": levels,
        "padding": 0,
    }
    return "PASS"


RUNNERS = {
    "2609.01683": run_01683,
    "2609.01743": run_01743,
    "2609.01962": run_01962,
    "2609.02107": run_02107,
    "2609.02219": run_02219,
    "2609.02652": run_02652,
    "2609.02846": run_02846,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paper_id", choices=sorted(RUNNERS))
    parser.add_argument("--output-json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    torch.manual_seed(0)
    started = time.perf_counter()
    self_test = core_self_test()
    if args.self_test:
        result = {
            "paper_id": args.paper_id,
            "core_self_test": self_test,
            "status": "PASS",
        }
    else:
        tokenizer, model = load()
        result = RUNNERS[args.paper_id](tokenizer, model)
        result.update(
            {
                "paper_id": args.paper_id,
                "model": "Qwen3-0.6B",
                "checkpoint": str(MODEL_DIR / "model.safetensors"),
                "parameters": sum(
                    parameter.numel() for parameter in model.parameters()
                ),
                "environment": environment(),
                "elapsed_seconds": time.perf_counter() - started,
                "core_self_test": self_test,
                "status": "PASS",
            }
        )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
