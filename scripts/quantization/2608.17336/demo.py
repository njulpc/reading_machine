#!/usr/bin/env python3
"""TileMix core reproduction on real Qwen3-0.6B Q/K/V tensors.

This reproduces the paper's numerical mechanism, not its Triton/A100 kernel:
hardware-aligned score-tile groups choose FP16-like or symmetric INT8 QK
arithmetic, all legal attention edges are retained, and V/PV stay floating
point.  The reference implementation materializes the score matrix so it can
run on CPU/MPS and expose numerical error clearly.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class TileMixConfig:
    tile_size: int = 16
    group_factor: int = 1
    int8_coverage: float = 0.5


def symmetric_int8(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Per-token, per-head symmetric INT8; scale is shared over head_dim."""
    scale = x.abs().amax(dim=-1, keepdim=True).clamp_min(1e-8) / 127.0
    code = torch.round(x / scale).clamp(-127, 127).to(torch.int8)
    return code, scale


def make_static_route(
    heads: int,
    seq_len: int,
    cfg: TileMixConfig,
    device: torch.device,
) -> torch.Tensor:
    """SpTrans-inspired data-free routing.

    Far-history groups are quantized before the diagonal/recent groups.  This
    preserves the paper's key separation between layout and INT8 coverage.
    The exact Triton layout table is kernel-specific and is not claimed here.
    """
    q_tiles = math.ceil(seq_len / cfg.tile_size)
    k_tiles = math.ceil(seq_len / cfg.tile_size)
    k_groups = math.ceil(k_tiles / cfg.group_factor)
    route = torch.zeros((heads, q_tiles, k_groups), dtype=torch.bool, device=device)
    legal: list[tuple[float, int, int, int]] = []
    for head in range(heads):
        for q_idx in range(q_tiles):
            for group_idx in range(k_groups):
                first_k_tile = group_idx * cfg.group_factor
                if first_k_tile > q_idx:
                    continue
                distance = q_idx - first_k_tile
                # Stable tie-breakers distribute INT8 work across heads/rows.
                priority = distance + 0.01 * ((head + 3 * q_idx + group_idx) % 7)
                legal.append((priority, head, q_idx, group_idx))
    legal.sort(reverse=True)
    selected = round(cfg.int8_coverage * len(legal))
    for _, head, q_idx, group_idx in legal[:selected]:
        route[head, q_idx, group_idx] = True
    return route


def tilemix_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    cfg: TileMixConfig,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Dense causal attention with tile-group FP/INT8 score routing."""
    if q.shape != k.shape or q.shape != v.shape:
        raise ValueError(f"q/k/v shapes must match after GQA expansion: {q.shape}, {k.shape}, {v.shape}")
    batch, heads, seq_len, head_dim = q.shape
    route = make_static_route(heads, seq_len, cfg, q.device)
    q8, q_scale = symmetric_int8(q)
    k8, k_scale = symmetric_int8(k)
    scores = torch.empty((batch, heads, seq_len, seq_len), dtype=torch.float32, device=q.device)
    int8_cells = 0
    legal_cells = 0
    group_width = cfg.tile_size * cfg.group_factor
    inv_sqrt_d = 1.0 / math.sqrt(head_dim)

    for q_start in range(0, seq_len, cfg.tile_size):
        q_stop = min(q_start + cfg.tile_size, seq_len)
        q_idx = q_start // cfg.tile_size
        for k_start in range(0, seq_len, group_width):
            k_stop = min(k_start + group_width, seq_len)
            group_idx = k_start // group_width
            fp_score = torch.matmul(
                q[:, :, q_start:q_stop].float(),
                k[:, :, k_start:k_stop].float().transpose(-1, -2),
            )
            int_score = torch.matmul(
                q8[:, :, q_start:q_stop].float(),
                k8[:, :, k_start:k_stop].float().transpose(-1, -2),
            )
            int_score = int_score * q_scale[:, :, q_start:q_stop] * k_scale[:, :, k_start:k_stop].transpose(-1, -2)
            use_int8 = route[:, q_idx, group_idx].view(1, heads, 1, 1)
            scores[:, :, q_start:q_stop, k_start:k_stop] = torch.where(use_int8, int_score, fp_score) * inv_sqrt_d

            q_pos = torch.arange(q_start, q_stop, device=q.device).view(-1, 1)
            k_pos = torch.arange(k_start, k_stop, device=q.device).view(1, -1)
            cell_mask = k_pos <= q_pos
            cells = int(cell_mask.sum().item()) * batch * heads
            legal_cells += cells
            int8_cells += int(cell_mask.sum().item()) * batch * int(route[:, q_idx, group_idx].sum().item())

    causal = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=q.device), diagonal=1)
    scores.masked_fill_(causal.view(1, 1, seq_len, seq_len), torch.finfo(scores.dtype).min)
    probs = torch.softmax(scores, dim=-1)
    output = torch.matmul(probs, v.float())
    return output, {
        "requested_int8_coverage": cfg.int8_coverage,
        "realized_cell_coverage": int8_cells / max(legal_cells, 1),
        "tile_size": float(cfg.tile_size),
        "group_factor": float(cfg.group_factor),
    }


def fp_attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    scores = torch.matmul(q.float(), k.float().transpose(-1, -2)) / math.sqrt(q.shape[-1])
    seq_len = q.shape[-2]
    causal = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=q.device), diagonal=1)
    scores.masked_fill_(causal.view(1, 1, seq_len, seq_len), torch.finfo(scores.dtype).min)
    return torch.matmul(torch.softmax(scores, dim=-1), v.float())


def load_qwen_qkv(model_id: str, seq_len: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, str]:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb, repeat_kv

    tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        local_files_only=True,
        dtype=torch.float32,
        low_cpu_mem_usage=True,
    ).eval()
    calibration_text = (
        "TileMix routes hardware-aligned attention score tiles between full precision and INT8. "
        "The route is static and data-free; this prompt is used only to measure numerical error. "
        "模型压缩需要同时核验精度、内存、延迟与真实硬件可执行性。 "
    ) * 8
    encoded = tokenizer(calibration_text, return_tensors="pt", add_special_tokens=True)
    input_ids = encoded["input_ids"][:, :seq_len]
    if input_ids.shape[1] < seq_len:
        repeats = math.ceil(seq_len / input_ids.shape[1])
        input_ids = input_ids.repeat(1, repeats)[:, :seq_len]

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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--seq-len", type=int, default=96)
    parser.add_argument("--tile-size", type=int, default=16)
    parser.add_argument("--group-factor", type=int, default=1)
    parser.add_argument("--self-test", action="store_true", help="Do not load Qwen weights.")
    args = parser.parse_args()

    torch.manual_seed(20260820)
    if args.self_test:
        q, k, v, source = synthetic_qkv(args.seq_len)
    else:
        q, k, v, source = load_qwen_qkv(args.model, args.seq_len)
    reference = fp_attention(q, k, v)
    print(f"source={source}")
    print(f"qkv_shape={tuple(q.shape)} tile_size={args.tile_size} group_factor={args.group_factor}")
    for coverage in (0.25, 0.50, 0.75, 1.00):
        cfg = TileMixConfig(args.tile_size, args.group_factor, coverage)
        mixed, stats = tilemix_attention(q, k, v, cfg)
        diff = mixed - reference
        cosine = torch.nn.functional.cosine_similarity(
            mixed.flatten().unsqueeze(0), reference.flatten().unsqueeze(0)
        ).item()
        print(
            f"coverage={coverage:.2f} realized={stats['realized_cell_coverage']:.4f} "
            f"mae={diff.abs().mean().item():.8f} max_abs={diff.abs().max().item():.8f} "
            f"cosine={cosine:.8f}"
        )
        if not torch.isfinite(mixed).all():
            raise RuntimeError("non-finite TileMix output")
    print("validation=PASS")


if __name__ == "__main__":
    main()

