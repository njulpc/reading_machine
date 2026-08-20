#!/usr/bin/env python3
"""Portable TileMix reproduction for Qwen3-0.6B.

The implementation follows the paper's public numerical configuration and
SpTrans routing definition. It is a CPU/MPS reference, not the Triton/A100
kernel: it uses PyTorch matmuls and FP32 streaming-softmax state while keeping
tile-group routing, blockwise INT8 Q/K, dense connectivity, and FP16-like V/PV
explicit and testable.
"""

from __future__ import annotations

import argparse
import math
import platform
import time
from dataclasses import dataclass
from typing import Optional

import torch


@dataclass(frozen=True)
class TileMixConfig:
    block_m: int = 64
    block_n: int = 64
    q_quant_block: int = 128
    k_quant_block: int = 64
    group_factor: int = 0  # 0 selects the paper's automatic <=64-group rule.
    int8_coverage: float = 0.5


def effective_group_factor(k_len: int, cfg: TileMixConfig) -> int:
    """Appendix B grouping rule that keeps one 64-bit word sufficient."""
    if min(cfg.block_m, cfg.block_n, cfg.q_quant_block, cfg.k_quant_block) <= 0:
        raise ValueError("compute and quantization block sizes must be positive")
    if cfg.group_factor > 0:
        factor = cfg.group_factor
    else:
        b64 = math.ceil(k_len / 64)
        mask_width = cfg.block_n * math.ceil(
            max(b64, cfg.block_n) / cfg.block_n
        )
        factor = mask_width // cfg.block_n
    if math.ceil(k_len / (cfg.block_n * factor)) > 64:
        raise ValueError("group_factor leaves more than 64 route groups")
    return factor


def blockwise_symmetric_int8(
    x: torch.Tensor,
    block_tokens: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Signed symmetric INT8 with one absmax scale per token block and head."""
    if x.ndim != 4:
        raise ValueError(f"expected [batch, heads, tokens, dim], got {tuple(x.shape)}")
    if block_tokens <= 0:
        raise ValueError("block_tokens must be positive")
    batch, heads, tokens, _ = x.shape
    codes = torch.empty_like(x, dtype=torch.int8)
    token_scales = torch.empty((batch, heads, tokens, 1), dtype=torch.float32, device=x.device)
    scales: list[torch.Tensor] = []
    for start in range(0, tokens, block_tokens):
        stop = min(start + block_tokens, tokens)
        block = x[:, :, start:stop].float()
        scale = block.abs().amax(dim=(-2, -1), keepdim=True).clamp_min(1e-8) / 127.0
        codes[:, :, start:stop] = torch.round(block / scale).clamp(-127, 127).to(torch.int8)
        token_scales[:, :, start:stop] = scale
        scales.append(scale.squeeze(-1).squeeze(-1))
    return codes, token_scales, torch.stack(scales, dim=2)


def causal_compute_tile_weights(seq_len: int, cfg: TileMixConfig) -> torch.Tensor:
    """Released implementation's executed-compute-tile weight per mask bit."""
    factor = effective_group_factor(seq_len, cfg)
    mask_block_n = cfg.block_n * factor
    num_m = math.ceil(seq_len / cfg.block_m)
    num_mask_n = math.ceil(seq_len / mask_block_n)
    num_compute_n = math.ceil(seq_len / cfg.block_n)
    weights = torch.zeros((num_m, num_mask_n), dtype=torch.int64)
    for row in range(num_m):
        row_compute_tiles = min(
            num_compute_n,
            math.ceil(((row + 1) * cfg.block_m) / cfg.block_n),
        )
        full_groups, remainder = divmod(row_compute_tiles, factor)
        if full_groups:
            weights[row, :full_groups] = factor
        if remainder and full_groups < num_mask_n:
            weights[row, full_groups] = remainder
    return weights


def retarget_weighted_int8_fraction(
    route: torch.Tensor,
    weights: torch.Tensor,
    percentage: float,
) -> torch.Tensor:
    """Match authors' fixed-seed retargeting over causal compute tiles."""
    if percentage < 0.0 or percentage > 1.0:
        raise ValueError(f"coverage must be in [0, 1], got {percentage}")
    result = route.to(device="cpu", dtype=torch.bool).clone()
    weights = weights.to(device="cpu", dtype=torch.int64)
    legal = weights > 0
    result &= legal
    total_weight = int(weights.sum().item())
    if total_weight == 0:
        return result
    target = int(round(total_weight * percentage))
    current = int((weights * result).sum().item())
    if current == target:
        return result
    add_int8 = current < target
    candidates = torch.nonzero(((~result) if add_int8 else result) & legal, as_tuple=False)
    generator = torch.Generator(device="cpu").manual_seed(42)
    order = torch.randperm(len(candidates), generator=generator)
    for position in order.tolist():
        row, col = candidates[position].tolist()
        weight = int(weights[row, col].item())
        proposed = current + weight if add_int8 else current - weight
        if abs(target - proposed) <= abs(target - current):
            result[row, col] = add_int8
            current = proposed
        if current == target:
            break
    return result


def make_sptrans_route(
    q_len: int,
    k_len: int,
    cfg: TileMixConfig,
) -> tuple[torch.Tensor, torch.Tensor, int, int]:
    """Released SpTrans defaults plus fixed-seed compute-tile retargeting."""
    if q_len != k_len:
        raise ValueError("the portable reference validates the prefill path (q_len == k_len)")
    factor = effective_group_factor(k_len, cfg)
    mask_block_n = cfg.block_n * factor
    num_m = math.ceil(q_len / cfg.block_m)
    num_n = math.ceil(k_len / mask_block_n)
    route = torch.ones((num_m, num_n), dtype=torch.bool)
    stride = max(1, min(128, q_len // 4))
    tail = min(32, stride // 4)
    for row in range(num_m):
        query_start = row * cfg.block_m
        query_end = min(q_len, (row + 1) * cfg.block_m)
        first_stride = query_start // stride
        last_stride = (query_end - 1) // stride
        for query_stride in range(first_stride, last_stride + 1):
            stride_start = query_stride * stride
            stride_end = min((query_stride + 1) * stride, query_end)
            start_group = stride_start // mask_block_n
            end_group = min(num_n, math.ceil(stride_end / mask_block_n))
            route[row, start_group:end_group] = False
            for previous_stride in range(query_stride):
                previous_start = previous_stride * stride
                previous_end = (previous_stride + 1) * stride
                tail_start = max(previous_start, previous_end - tail)
                tail_start_group = tail_start // mask_block_n
                tail_end_group = min(num_n, math.ceil(previous_end / mask_block_n))
                route[row, tail_start_group:tail_end_group] = False
    weights = causal_compute_tile_weights(q_len, cfg)
    route = retarget_weighted_int8_fraction(route, weights, cfg.int8_coverage)
    return route, weights > 0, stride, tail


def pack_route_words(route: torch.Tensor) -> tuple[int, ...]:
    """Pack one row's group decisions as b_m=sum R[m,g] 2**g."""
    if route.ndim != 2 or route.shape[1] > 64:
        raise ValueError("route must have shape [query_tiles, <=64 groups]")
    words: list[int] = []
    for row in route.tolist():
        word = 0
        for group_idx, use_int8 in enumerate(row):
            if use_int8:
                word |= 1 << group_idx
        words.append(word)
    return tuple(words)


def _route_bit(words: tuple[int, ...], q_idx: int, group_idx: int) -> bool:
    return bool((words[q_idx] >> group_idx) & 1)


def tilemix_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    cfg: TileMixConfig,
    attention_mask: Optional[torch.Tensor] = None,
    scaling: Optional[float] = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Dense causal attention with packed tile-group FP/INT8 score routing."""
    if q.ndim != 4 or k.ndim != 4 or v.ndim != 4:
        raise ValueError("q/k/v must be rank-four [batch, heads, tokens, dim]")
    if q.shape[:2] != k.shape[:2] or k.shape != v.shape or q.shape[-1] != k.shape[-1]:
        raise ValueError(f"incompatible q/k/v shapes: {q.shape}, {k.shape}, {v.shape}")
    batch, heads, q_len, head_dim = q.shape
    k_len = k.shape[-2]
    route_cpu, legal_cpu, stride, tail = make_sptrans_route(q_len, k_len, cfg)
    words = pack_route_words(route_cpu)
    factor = effective_group_factor(k_len, cfg)
    group_width = cfg.block_n * factor
    inv_sqrt_d = scaling if scaling is not None else 1.0 / math.sqrt(head_dim)

    q8: Optional[torch.Tensor] = None
    k8: Optional[torch.Tensor] = None
    q_scale: Optional[torch.Tensor] = None
    k_scale: Optional[torch.Tensor] = None
    if route_cpu.any():
        q8, q_scale, _ = blockwise_symmetric_int8(q, cfg.q_quant_block)
        k8, k_scale, _ = blockwise_symmetric_int8(k, cfg.k_quant_block)

    output = torch.empty((batch, heads, q_len, head_dim), dtype=torch.float32, device=q.device)
    q_offset = k_len - q_len
    int8_cells = 0
    legal_cells = 0
    for q_start in range(0, q_len, cfg.block_m):
        q_stop = min(q_start + cfg.block_m, q_len)
        q_idx = q_start // cfg.block_m
        rows = q_stop - q_start
        running_max = torch.full((batch, heads, rows, 1), -torch.inf, device=q.device)
        normalizer = torch.zeros((batch, heads, rows, 1), dtype=torch.float32, device=q.device)
        accumulator = torch.zeros((batch, heads, rows, head_dim), dtype=torch.float32, device=q.device)
        q_positions = q_offset + torch.arange(q_start, q_stop, device=q.device).view(-1, 1)

        for k_start in range(0, k_len, cfg.block_n):
            if k_start > int(q_positions.max().item()):
                break
            k_stop = min(k_start + cfg.block_n, k_len)
            group_idx = k_start // group_width
            use_int8 = _route_bit(words, q_idx, group_idx)
            if use_int8:
                assert q8 is not None and k8 is not None and q_scale is not None and k_scale is not None
                score = torch.matmul(
                    q8[:, :, q_start:q_stop].float(),
                    k8[:, :, k_start:k_stop].float().transpose(-1, -2),
                )
                score = score * q_scale[:, :, q_start:q_stop]
                score = score * k_scale[:, :, k_start:k_stop].transpose(-1, -2)
            else:
                score = torch.matmul(
                    q[:, :, q_start:q_stop].to(torch.float16),
                    k[:, :, k_start:k_stop].to(torch.float16).transpose(-1, -2),
                ).float()
            score.mul_(inv_sqrt_d)

            k_positions = torch.arange(k_start, k_stop, device=q.device).view(1, -1)
            causal_legal = k_positions <= q_positions
            score.masked_fill_(~causal_legal.view(1, 1, rows, -1), -torch.inf)
            if attention_mask is not None:
                mask_tile = attention_mask[:, :, q_start:q_stop, k_start:k_stop]
                if mask_tile.dtype == torch.bool:
                    score.masked_fill_(~mask_tile, -torch.inf)
                else:
                    score.add_(mask_tile.float())

            tile_max = score.amax(dim=-1, keepdim=True)
            new_max = torch.maximum(running_max, tile_max)
            old_factor = torch.exp(running_max - new_max)
            probability = torch.exp(score - new_max)
            probability = torch.nan_to_num(probability, nan=0.0)
            normalizer = old_factor * normalizer + probability.sum(dim=-1, keepdim=True)
            pv = torch.matmul(
                probability.to(torch.float16),
                v[:, :, k_start:k_stop].to(torch.float16),
            ).float()
            accumulator = old_factor * accumulator + pv
            running_max = new_max

            cells = int(causal_legal.sum().item()) * batch * heads
            legal_cells += cells
            if use_int8:
                int8_cells += cells
        output[:, :, q_start:q_stop] = accumulator / normalizer.clamp_min(1e-20)

    realized_groups = float(route_cpu[legal_cpu].float().mean().item()) if legal_cpu.any() else 0.0
    weights = causal_compute_tile_weights(q_len, cfg)
    realized_compute_tiles = float(
        (weights * route_cpu).sum().item() / max(int(weights.sum().item()), 1)
    )
    return output, {
        "requested_int8_coverage": cfg.int8_coverage,
        "realized_group_coverage": realized_groups,
        "realized_compute_tile_coverage": realized_compute_tiles,
        "realized_cell_coverage": int8_cells / max(legal_cells, 1),
        "block_m": float(cfg.block_m),
        "block_n": float(cfg.block_n),
        "q_quant_block": float(cfg.q_quant_block),
        "k_quant_block": float(cfg.k_quant_block),
        "group_factor": float(factor),
        "sptrans_stride": float(stride),
        "sptrans_tail": float(tail),
        "packed_words": float(len(words)),
    }


def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, kv_heads, seq_len, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    expanded = hidden_states[:, :, None].expand(batch, kv_heads, n_rep, seq_len, head_dim)
    return expanded.reshape(batch, kv_heads * n_rep, seq_len, head_dim)


def transformers_tilemix_attention(
    module: torch.nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: Optional[torch.Tensor],
    scaling: float,
    dropout: float = 0.0,
    **_: object,
) -> tuple[torch.Tensor, None]:
    """Transformers AttentionInterface adapter used by every Qwen3 layer."""
    del dropout
    key = repeat_kv(key, module.num_key_value_groups)
    value = repeat_kv(value, module.num_key_value_groups)
    output, stats = tilemix_attention(
        query,
        key,
        value,
        module._tilemix_config,
        attention_mask=attention_mask,
        scaling=scaling,
    )
    module._tilemix_calls = getattr(module, "_tilemix_calls", 0) + 1
    module._tilemix_last_stats = stats
    return output.transpose(1, 2).contiguous().to(query.dtype), None


def calibration_text() -> str:
    return (
        "TileMix routes hardware-aligned attention score tiles between full precision and INT8. "
        "Its static route is data-free, so this text is only a numerical test input. "
        "模型压缩需要同时核验精度、内存、延迟与真实硬件可执行性。 "
    ) * 16


def load_qwen(model_id: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        local_files_only=True,
        dtype=torch.float32,
        low_cpu_mem_usage=True,
        attn_implementation="eager",
    ).eval()
    return tokenizer, model


def encode_fixed_length(tokenizer, seq_len: int) -> torch.Tensor:
    encoded = tokenizer(calibration_text(), return_tensors="pt", add_special_tokens=True)
    input_ids = encoded["input_ids"]
    if input_ids.shape[1] < seq_len:
        input_ids = input_ids.repeat(1, math.ceil(seq_len / input_ids.shape[1]))
    return input_ids[:, :seq_len]


def load_qwen_qkv(model_id: str, seq_len: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, str]:
    from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb

    tokenizer, model = load_qwen(model_id)
    input_ids = encode_fixed_length(tokenizer, seq_len)
    with torch.no_grad():
        hidden = model.model.embed_tokens(input_ids)
        layer = model.model.layers[0]
        normed = layer.input_layernorm(hidden)
        attn = layer.self_attn
        batch, length, _ = normed.shape
        q = attn.q_proj(normed).view(batch, length, attn.config.num_attention_heads, attn.head_dim)
        k = attn.k_proj(normed).view(batch, length, attn.config.num_key_value_heads, attn.head_dim)
        v = attn.v_proj(normed).view(batch, length, attn.config.num_key_value_heads, attn.head_dim)
        q = attn.q_norm(q).transpose(1, 2)
        k = attn.k_norm(k).transpose(1, 2)
        v = v.transpose(1, 2)
        position_ids = torch.arange(length).unsqueeze(0)
        cos, sin = model.model.rotary_emb(normed, position_ids)
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        groups = attn.config.num_attention_heads // attn.config.num_key_value_heads
        k = repeat_kv(k, groups)
        v = repeat_kv(v, groups)
    source = f"{model_id}; parameters={sum(p.numel() for p in model.parameters()):,}; layer=0"
    return q.contiguous(), k.contiguous(), v.contiguous(), source


def synthetic_qkv(seq_len: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, str]:
    generator = torch.Generator().manual_seed(20260820)
    shape = (1, 8, seq_len, 64)
    return (
        torch.randn(shape, generator=generator),
        torch.randn(shape, generator=generator),
        torch.randn(shape, generator=generator),
        "deterministic synthetic self-test",
    )


def validate_core_operators() -> None:
    x = torch.tensor([[[[1.0], [-2.0], [4.0], [-8.0]]]])
    code, token_scale, block_scale = blockwise_symmetric_int8(x, 2)
    assert code.shape == x.shape and block_scale.shape == (1, 1, 2)
    assert torch.allclose(token_scale[0, 0, :2], torch.full((2, 1), 2.0 / 127.0))
    assert torch.allclose(token_scale[0, 0, 2:], torch.full((2, 1), 8.0 / 127.0))
    route = torch.tensor([[True, False, True], [False, True, False]])
    words = pack_route_words(route)
    assert words == (5, 2)
    assert all(
        _route_bit(words, row, col) == bool(route[row, col])
        for row in range(2)
        for col in range(3)
    )
    official_route, legal, stride, tail = make_sptrans_route(256, 256, TileMixConfig())
    weights = causal_compute_tile_weights(256, TileMixConfig())
    assert official_route.shape == legal.shape == (4, 4)
    assert (stride, tail) == (64, 16)
    assert int(weights.sum().item()) == 10
    assert int((weights * official_route).sum().item()) == 5


def run_qkv_experiment(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, source: str, base: TileMixConfig) -> None:
    fp_cfg = TileMixConfig(
        base.block_m,
        base.block_n,
        base.q_quant_block,
        base.k_quant_block,
        base.group_factor,
        0.0,
    )
    reference, _ = tilemix_attention(q, k, v, fp_cfg)
    print(f"source={source}")
    print(
        f"qkv_shape={tuple(q.shape)} compute_tile={base.block_m}x{base.block_n} "
        f"quant_blocks=Q{base.q_quant_block}/K{base.k_quant_block} "
        f"group_factor={effective_group_factor(k.shape[-2], base)}"
    )
    for coverage in (0.25, 0.50, 0.75, 1.00):
        cfg = TileMixConfig(
            base.block_m,
            base.block_n,
            base.q_quant_block,
            base.k_quant_block,
            base.group_factor,
            coverage,
        )
        mixed, stats = tilemix_attention(q, k, v, cfg)
        diff = mixed - reference
        cosine = torch.nn.functional.cosine_similarity(
            mixed.flatten().unsqueeze(0), reference.flatten().unsqueeze(0)
        ).item()
        print(
            f"coverage={coverage:.2f} compute_tiles={stats['realized_compute_tile_coverage']:.4f} "
            f"groups={stats['realized_group_coverage']:.4f} "
            f"cells={stats['realized_cell_coverage']:.4f} stride={stats['sptrans_stride']:.0f} "
            f"tail={stats['sptrans_tail']:.0f} mae={diff.abs().mean().item():.8f} "
            f"max_abs={diff.abs().max().item():.8f} cosine={cosine:.8f}"
        )
        if not torch.isfinite(mixed).all():
            raise RuntimeError("non-finite TileMix output")


def run_full_model(model_id: str, seq_len: int, cfg: TileMixConfig) -> None:
    from transformers.masking_utils import ALL_MASK_ATTENTION_FUNCTIONS
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS

    tokenizer, model = load_qwen(model_id)
    input_ids = encode_fixed_length(tokenizer, seq_len)
    attention_mask = torch.ones_like(input_ids)
    parameters = sum(p.numel() for p in model.parameters())
    started = time.perf_counter()
    with torch.no_grad():
        baseline = model(
            input_ids=input_ids, attention_mask=attention_mask, use_cache=False
        ).logits
    baseline_seconds = time.perf_counter() - started

    ALL_ATTENTION_FUNCTIONS.register("tilemix_reference", transformers_tilemix_attention)
    ALL_MASK_ATTENTION_FUNCTIONS.register(
        "tilemix_reference", ALL_MASK_ATTENTION_FUNCTIONS["eager"]
    )
    model.config._attn_implementation = "tilemix_reference"
    attention_modules = [layer.self_attn for layer in model.model.layers]
    for attention in attention_modules:
        attention._tilemix_config = cfg
        attention._tilemix_calls = 0

    started = time.perf_counter()
    with torch.no_grad():
        mixed = model(
            input_ids=input_ids, attention_mask=attention_mask, use_cache=False
        ).logits
    tilemix_seconds = time.perf_counter() - started
    if not torch.isfinite(mixed).all():
        raise RuntimeError("non-finite full-model logits")
    calls_after_forward = sum(attention._tilemix_calls for attention in attention_modules)
    if calls_after_forward != len(attention_modules):
        raise RuntimeError(
            f"expected {len(attention_modules)} TileMix layer calls, got {calls_after_forward}"
        )

    with torch.no_grad():
        generated = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=1,
            do_sample=False,
            use_cache=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    calls_after_generation = sum(attention._tilemix_calls for attention in attention_modules)
    if calls_after_generation != 2 * len(attention_modules):
        raise RuntimeError(
            f"expected {2 * len(attention_modules)} cumulative TileMix calls after generation, "
            f"got {calls_after_generation}"
        )
    generated_token = int(generated[0, -1].item())
    generated_text = tokenizer.decode([generated_token], skip_special_tokens=False)
    diff = mixed - baseline
    cosine = torch.nn.functional.cosine_similarity(
        mixed[:, -1].double(), baseline[:, -1].double()
    ).item()
    first_stats = attention_modules[0]._tilemix_last_stats
    print(
        f"full_model={model_id} parameters={parameters:,} layers={len(attention_modules)} "
        f"seq_len={seq_len} device=cpu"
    )
    print(
        f"full_model_compute_tiles={first_stats['realized_compute_tile_coverage']:.4f} "
        f"full_model_groups={first_stats['realized_group_coverage']:.4f} "
        f"full_model_cells={first_stats['realized_cell_coverage']:.4f} "
        f"forward_calls={calls_after_forward} cumulative_generation_calls={calls_after_generation}"
    )
    print(
        f"logits_mae={diff.abs().mean().item():.8f} "
        f"logits_max_abs={diff.abs().max().item():.8f} last_token_cosine={cosine:.8f}"
    )
    print(
        f"baseline_seconds={baseline_seconds:.3f} tilemix_seconds={tilemix_seconds:.3f} "
        f"generated_token={generated_token} generated_text={generated_text!r}"
    )
    print("calibration=not-required route=static-data-free export=not-supported")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--seq-len", type=int, default=256)
    parser.add_argument("--block-m", type=int, default=64, help="Query compute-tile height")
    parser.add_argument("--block-n", type=int, default=64, help="Key compute-tile width")
    parser.add_argument("--q-quant-block", type=int, default=128)
    parser.add_argument("--k-quant-block", type=int, default=64)
    parser.add_argument("--group-factor", type=int, default=0, help="0 uses the paper's automatic rule")
    parser.add_argument("--coverage", type=float, default=0.5, help="Used by --full-model")
    parser.add_argument("--self-test", action="store_true", help="Use deterministic random Q/K/V")
    parser.add_argument(
        "--full-model",
        action="store_true",
        help="Run every Qwen attention layer with TileMix and generate one token",
    )
    args = parser.parse_args()

    torch.manual_seed(20260820)
    validate_core_operators()
    print(
        f"environment=Python-{platform.python_version()} PyTorch-{torch.__version__} "
        f"machine={platform.machine()} mps={torch.backends.mps.is_available()}"
    )
    print("operator_checks=PASS")
    base = TileMixConfig(
        args.block_m,
        args.block_n,
        args.q_quant_block,
        args.k_quant_block,
        args.group_factor,
        args.coverage,
    )
    if args.full_model:
        run_full_model(args.model, args.seq_len, base)
    else:
        if args.self_test:
            q, k, v, source = synthetic_qkv(args.seq_len)
        else:
            q, k, v, source = load_qwen_qkv(args.model, args.seq_len)
        run_qkv_experiment(q, k, v, source, base)
    print("validation=PASS")


if __name__ == "__main__":
    main()
