#!/usr/bin/env python3
"""AWSRC-U reference for arXiv:2608.23144.

Implements row-wise C=128 tiles, normalized signed/permuted Hadamard bases,
activation-weighted least squares, P=2 signed 4-bit coefficients with one
power-of-two scale per retained tile, and byte-aware positive-gain selection.
"""

import argparse
import glob
import math
import os
import time

import torch


def checkpoint(explicit=None):
    if explicit:
        if os.path.isdir(explicit):
            explicit = os.path.join(explicit, "model.safetensors")
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


def load_slice(path, size):
    from safetensors import safe_open

    with safe_open(path, framework="pt", device="cpu") as handle:
        key = next(key for key in handle.keys() if key.endswith("q_proj.weight"))
        weight = handle.get_tensor(key).float()[:size, :size].contiguous()
    return key, weight


def int4_rtn(weight, group_size=128):
    """Symmetric per-row, per-group INT4 RTN backbone (range -7..7)."""
    if weight.ndim != 2 or weight.shape[1] % group_size:
        raise ValueError("weight input dimension must be divisible by group size")
    groups = weight.float().reshape(weight.shape[0], -1, group_size)
    scales = groups.abs().amax(2, keepdim=True).clamp_min(1e-12) / 7.0
    codes = torch.round(groups / scales).clamp(-7, 7).to(torch.int8)
    reconstructed = codes.float() * scales
    return reconstructed.reshape_as(weight), codes, scales.squeeze(-1)


def hadamard(order):
    if order < 1 or order & (order - 1):
        raise ValueError("Hadamard order must be a power of two")
    matrix = torch.ones(1, 1)
    while matrix.shape[0] < order:
        matrix = torch.cat(
            (torch.cat((matrix, matrix), 1), torch.cat((matrix, -matrix), 1)), 0
        )
    return matrix


def seeded_basis(seed, tile_size, coefficients):
    generator = torch.Generator().manual_seed(seed)
    signs = (torch.randint(0, 2, (tile_size,), generator=generator) * 2 - 1).float()
    permutation = torch.randperm(tile_size, generator=generator)
    columns = torch.randperm(tile_size, generator=generator)[:coefficients]
    basis = hadamard(tile_size)[:, columns]
    basis = signs[:, None] * basis[permutation]
    return basis / math.sqrt(tile_size)


def quantize_coefficients(alpha, bits=4):
    qmax = (1 << (bits - 1)) - 1
    raw_scale = alpha.abs().amax(1).clamp_min(1e-30) / qmax
    exponent = torch.ceil(torch.log2(raw_scale)).clamp(-126, 127).to(torch.int16)
    scale = torch.pow(2.0, exponent.float())
    codes = torch.round(alpha / scale[:, None]).clamp(-qmax, qmax).to(torch.int8)
    return codes.float() * scale[:, None], codes, exponent


def record_bytes(total_tiles, seed_pool, coefficients, bits, exponent_bits=8):
    payload = (
        math.ceil(math.log2(max(total_tiles, 2)))
        + math.ceil(math.log2(max(seed_pool, 2)))
        + exponent_bits
        + coefficients * bits
    )
    return math.ceil(payload / 8)


def awsrc_u(
    weight,
    backbone,
    activation_diagonal,
    retain_fraction=0.1,
    tile_size=128,
    coefficients=2,
    coefficient_bits=4,
    seed_pool=2,
):
    """Fit candidates after coefficient quantization and keep gain-ranked records."""
    if weight.shape != backbone.shape or weight.shape[1] % tile_size:
        raise ValueError("invalid weight/backbone/tile shape")
    residual = (weight.float() - backbone.float()).reshape(-1, tile_size)
    groups_per_row = weight.shape[1] // tile_size
    diagonal = activation_diagonal.float().reshape(groups_per_row, tile_size)
    importance = diagonal.repeat(weight.shape[0], 1).clamp_min(1e-12)
    baseline_error = (residual.square() * importance).sum(1)
    best_error = torch.full_like(baseline_error, float("inf"))
    best_reconstruction = torch.zeros_like(residual)
    best_selector = torch.zeros(len(residual), dtype=torch.int8)
    best_codes = torch.zeros(len(residual), coefficients, dtype=torch.int8)
    best_exponent = torch.zeros(len(residual), dtype=torch.int16)
    eye = torch.eye(coefficients)
    for seed in range(seed_pool):
        basis = seeded_basis(seed, tile_size, coefficients)
        gram = torch.einsum("cp,tc,cq->tpq", basis, importance, basis)
        rhs = torch.einsum("cp,tc,tc->tp", basis, importance, residual)
        alpha = torch.linalg.solve(
            gram + 1e-8 * eye[None], rhs.unsqueeze(-1)
        ).squeeze(-1)
        alpha_hat, codes, exponent = quantize_coefficients(alpha, coefficient_bits)
        reconstruction = alpha_hat @ basis.t()
        error = ((residual - reconstruction).square() * importance).sum(1)
        choose = error < best_error
        best_error[choose] = error[choose]
        best_reconstruction[choose] = reconstruction[choose]
        best_selector[choose] = seed
        best_codes[choose] = codes[choose]
        best_exponent[choose] = exponent[choose]

    gain = baseline_error - best_error
    eligible = torch.nonzero(gain > 0, as_tuple=False).flatten()
    requested = max(1, math.ceil(len(residual) * retain_fraction))
    kept = min(requested, len(eligible))
    if kept:
        ordered = eligible[torch.argsort(gain[eligible], descending=True)[:kept]]
    else:
        ordered = torch.empty(0, dtype=torch.long)
    correction = torch.zeros_like(residual)
    correction[ordered] = best_reconstruction[ordered]
    repaired = (backbone.float().reshape(-1, tile_size) + correction).reshape_as(weight)
    bytes_per_record = record_bytes(
        len(residual), seed_pool, coefficients, coefficient_bits
    )
    packet = {
        "tile_indices": ordered.to(torch.int32),
        "seed_selectors": best_selector[ordered],
        "coefficient_codes": best_codes[ordered],
        "scale_exponents": best_exponent[ordered],
        "tile_size": tile_size,
        "coefficients": coefficients,
        "coefficient_bits": coefficient_bits,
        "seed_pool": seed_pool,
        "record_bytes": bytes_per_record,
    }
    stats = {
        "tiles": len(residual),
        "eligible": len(eligible),
        "retained": kept,
        "record_bytes": bytes_per_record,
        "sidecar_bytes": 904 + kept * bytes_per_record,
        "weighted_gain": float(gain[ordered].sum()) if kept else 0.0,
    }
    return repaired, packet, stats


def decode_sidecar(backbone, packet):
    """Deterministically decode complete AWSRC-U records against a fixed parent."""
    tile_size = int(packet["tile_size"])
    coefficients = int(packet["coefficients"])
    residual = torch.zeros_like(backbone.float().reshape(-1, tile_size))
    indices = packet["tile_indices"].long()
    selectors = packet["seed_selectors"].long()
    codes = packet["coefficient_codes"].float()
    exponents = packet["scale_exponents"].float()
    for seed in range(int(packet["seed_pool"])):
        positions = torch.nonzero(selectors == seed, as_tuple=False).flatten()
        if not len(positions):
            continue
        basis = seeded_basis(seed, tile_size, coefficients)
        alpha = codes[positions] * torch.pow(2.0, exponents[positions])[:, None]
        residual[indices[positions]] = alpha @ basis.t()
    return (backbone.float().reshape(-1, tile_size) + residual).reshape_as(backbone)


def self_test():
    basis = seeded_basis(0, 128, 2)
    assert torch.allclose(basis.t() @ basis, torch.eye(2), atol=1e-6)
    weight = torch.linspace(-1, 1, 256).reshape(2, 128)
    backbone, _, _ = int4_rtn(weight)
    repaired, packet, stats = awsrc_u(
        weight, backbone, torch.ones(128), retain_fraction=1.0
    )
    assert repaired.shape == weight.shape and stats["retained"] > 0
    assert packet["coefficient_codes"].shape[1] == 2
    assert torch.equal(repaired, decode_sidecar(backbone, packet))


def run_operator(path, size, retain_fraction):
    key, weight = load_slice(path, size)
    if size % 128:
        raise ValueError("--size must be divisible by 128")
    generator = torch.Generator().manual_seed(11)
    calibration = torch.randn(64, weight.shape[1], generator=generator)
    diagonal = calibration.square().mean(0)
    backbone, _, _ = int4_rtn(weight, 128)
    repaired, _, stats = awsrc_u(
        weight, backbone, diagonal, retain_fraction=retain_fraction
    )
    reference = calibration @ weight.t()
    parent = calibration @ backbone.t()
    repaired_output = calibration @ repaired.t()
    parent_mse = float(torch.mean((reference - parent).square()))
    repaired_mse = float(torch.mean((reference - repaired_output).square()))
    closed = (parent_mse - repaired_mse) / parent_mse * 100.0
    sidecar_bpw = stats["sidecar_bytes"] * 8 / weight.numel()
    print(f"checkpoint={path}\ntensor={key} slice={tuple(weight.shape)}")
    print(
        f"INT4_group=128 output_mse={parent_mse:.10g} repaired_mse={repaired_mse:.10g} "
        f"gap_closed={closed:.3f}%"
    )
    print(
        f"tiles={stats['tiles']} eligible={stats['eligible']} retained={stats['retained']} "
        f"record_bytes={stats['record_bytes']} serialized_sidecar_bytes={stats['sidecar_bytes']} "
        f"incremental_bpw={sidecar_bpw:.6f}"
    )


def collect_calibration(model, tokenizer, targets, sample_count):
    sums = {name: torch.zeros(module.in_features) for name, module in targets}
    counts = {name: 0 for name, _ in targets}
    handles = []
    for name, module in targets:
        def hook(_module, args, key=name):
            values = args[0].detach().float().reshape(-1, args[0].shape[-1])
            sums[key].add_(values.square().sum(0))
            counts[key] += values.shape[0]

        handles.append(module.register_forward_pre_hook(hook))
    texts = [
        "Quantization calibration should cover representative language.",
        "A deterministic sidecar stores selectors, coefficients, and scales.",
        "Activation statistics prioritize errors that perturb layer outputs.",
        "Low-bit models need byte-audited evaluation and honest boundaries.",
    ][:sample_count]
    with torch.no_grad():
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt")
            model(**inputs, use_cache=False)
    for handle in handles:
        handle.remove()
    return {name: sums[name] / max(counts[name], 1) for name, _ in targets}, texts


def run_full_model(
    path,
    prompt,
    calibration_samples,
    retain_fraction,
    repair_modules,
    save_sidecar,
):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started = time.perf_counter()
    model_dir = os.path.dirname(path)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir, local_files_only=True, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    targets = [
        (name, module)
        for name, module in model.named_modules()
        if isinstance(module, torch.nn.Linear)
        and any(name.endswith(suffix) for suffix in ("mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"))
    ]
    diagonal, calibration_texts = collect_calibration(
        model, tokenizer, targets, calibration_samples
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        reference_logits = model(**inputs, use_cache=False).logits.detach()

    chosen = {name for name, _ in targets[:repair_modules]}
    originals = {
        name: module.weight.detach().float().clone()
        for name, module in targets
        if name in chosen
    }
    quantized_elements = 0
    scale_count = 0
    for _, module in targets:
        reconstructed, _, scales = int4_rtn(module.weight.detach(), 128)
        quantized_elements += module.weight.numel()
        scale_count += scales.numel()
        with torch.no_grad():
            module.weight.copy_(reconstructed.to(module.weight.dtype))
    with torch.no_grad():
        parent_logits = model(**inputs, use_cache=False).logits.detach()

    packets = {}
    total_sidecar_bytes = 904
    repaired_modules = 0
    retained_tiles = 0
    roundtrip_exact = True
    for name, module in targets:
        if name not in chosen:
            continue
        parent = module.weight.detach().float().clone()
        repaired, packet, stats = awsrc_u(
            originals[name],
            parent,
            diagonal[name],
            retain_fraction=retain_fraction,
        )
        roundtrip_exact = roundtrip_exact and torch.equal(
            repaired, decode_sidecar(parent, packet)
        )
        with torch.no_grad():
            module.weight.copy_(repaired.to(module.weight.dtype))
        packets[name] = packet
        repaired_modules += 1
        retained_tiles += stats["retained"]
        total_sidecar_bytes += stats["retained"] * stats["record_bytes"]
    with torch.no_grad():
        repaired_logits = model(**inputs, use_cache=False).logits
        generated = model.generate(
            **inputs, max_new_tokens=1, do_sample=False, use_cache=False
        )
    if save_sidecar:
        torch.save(
            {
                "format": "AWSRC-U-reference-not-standalone",
                "targets": packets,
                "backbone_group_size": 128,
                "header_bytes": 904,
            },
            save_sidecar,
        )
        loaded = torch.load(save_sidecar, map_location="cpu", weights_only=True)
        assert loaded["backbone_group_size"] == 128
        assert set(loaded["targets"]) == set(packets)
    parent_mae = float((reference_logits - parent_logits).abs().mean())
    repaired_mae = float((reference_logits - repaired_logits).abs().mean())
    gap_closed = (parent_mae - repaired_mae) / max(parent_mae, 1e-20) * 100.0
    parent_bpw = 4.0 + 32.0 * scale_count / quantized_elements
    sidecar_bpw = 8.0 * total_sidecar_bytes / quantized_elements
    cosine = float(
        torch.nn.functional.cosine_similarity(
            reference_logits[:, -1].float(), repaired_logits[:, -1].float(), dim=-1
        ).mean()
    )
    print(
        f"full_model=Qwen3-0.6B parameters={sum(p.numel() for p in model.parameters())} "
        f"target_modules={len(targets)} quantized_weight_elements={quantized_elements} "
        f"calibration_texts={len(calibration_texts)}"
    )
    print(
        f"INT4_parent_bpw={parent_bpw:.6f} parent_logits_mae={parent_mae:.8f} "
        f"AWSRC_repaired_modules={repaired_modules} retained_tiles={retained_tiles} "
        f"sidecar_bytes={total_sidecar_bytes} incremental_scope_bpw={sidecar_bpw:.8f}"
    )
    print(
        f"repaired_logits_mae={repaired_mae:.8f} logits_gap_closed={gap_closed:.3f}% "
        f"last_token_cosine={cosine:.8f} generated={tokenizer.decode(generated[0])!r}"
    )
    print(
        f"saved_sidecar={save_sidecar or 'disabled'} sidecar_roundtrip_exact={roundtrip_exact} "
        f"elapsed_seconds={time.perf_counter() - started:.3f}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--retain-fraction", type=float, default=0.1)
    parser.add_argument("--full-model", action="store_true")
    parser.add_argument("--calibration-samples", type=int, default=4, choices=(1, 2, 3, 4))
    parser.add_argument("--repair-modules", type=int, default=1)
    parser.add_argument("--save-sidecar")
    parser.add_argument(
        "--prompt",
        default="Activation-weighted residual coding should improve a fixed INT4 parent.",
    )
    args = parser.parse_args()
    if not 0 < args.retain_fraction <= 1:
        parser.error("--retain-fraction must be in (0,1]")
    self_test()
    path = checkpoint(args.checkpoint)
    run_operator(path, args.size, args.retain_fraction)
    if args.full_model:
        run_full_model(
            path,
            args.prompt,
            args.calibration_samples,
            args.retain_fraction,
            args.repair_modules,
            args.save_sidecar,
        )


if __name__ == "__main__":
    main()
