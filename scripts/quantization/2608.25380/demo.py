#!/usr/bin/env python3
"""APDT 6/12-bit attention proxy installed across Qwen3-0.6B."""
import argparse
import glob
import os

import torch


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits += glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*")
    hits = [x for x in hits if os.path.exists(os.path.join(x, "tokenizer.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir")
    return hits[0]


def symmetric_quant(x, bits):
    qmax = 2 ** (bits - 1) - 1
    scale = x.detach().float().abs().amax(-1, keepdim=True).clamp_min(1e-12) / qmax
    return (x.float() / scale).round().clamp(-qmax, qmax).mul(scale).to(x.dtype)


def apdt_attention(
    module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs
):
    from transformers.models.qwen3.modeling_qwen3 import repeat_kv

    del dropout, kwargs
    key = repeat_kv(key, module.num_key_value_groups)
    value = repeat_kv(value, module.num_key_value_groups)
    reference_scores = torch.matmul(query, key.transpose(2, 3)) * scaling
    valid = torch.ones_like(reference_scores, dtype=torch.bool)
    if attention_mask is not None:
        causal = attention_mask[:, :, :, : key.shape[-2]]
        # Transformers uses a large finite negative sentinel, not necessarily -inf.
        valid = causal > -1.0e4
        reference_scores = reference_scores + causal
    reference_probs = reference_scores.softmax(-1, dtype=torch.float32).to(query.dtype)

    cfg = module._apdt_config
    sigma = reference_probs.float().std(dim=(-2, -1), unbiased=False)
    sigma_norm = ((sigma - cfg["sigma_min"]) / (cfg["sigma_max"] - cfg["sigma_min"])).clamp(0, 1)
    prune_threshold = (cfg["prune_alpha"] * sigma_norm + cfg["prune_beta"])[..., None, None]
    quant_threshold = (cfg["quant_alpha"] * sigma_norm + cfg["quant_beta"])[..., None, None]
    if not torch.all(quant_threshold > prune_threshold):
        raise RuntimeError("APDT quantization threshold must remain above pruning threshold")
    keep = valid & (reference_probs >= prune_threshold)
    # Every query row needs at least one finite edge.
    keep.scatter_(-1, reference_probs.argmax(-1, keepdim=True), True)
    high = keep & (reference_probs >= quant_threshold)

    q6, k6 = symmetric_quant(query, 6), symmetric_quant(key, 6)
    q12, k12 = symmetric_quant(query, 12), symmetric_quant(key, 12)
    scores6 = torch.matmul(q6, k6.transpose(2, 3)) * scaling
    scores12 = torch.matmul(q12, k12.transpose(2, 3)) * scaling
    scores = torch.where(high, scores12, scores6)
    if attention_mask is not None:
        scores = scores + causal
    scores = scores.masked_fill(~keep, torch.finfo(scores.dtype).min)
    probabilities = scores.softmax(-1, dtype=torch.float32).to(query.dtype)

    p6, p12 = symmetric_quant(probabilities, 6), symmetric_quant(probabilities, 12)
    v6, v12 = symmetric_quant(value, 6), symmetric_quant(value, 12)
    low_prob = torch.where(keep & ~high, p6, torch.zeros_like(p6))
    high_prob = torch.where(high, p12, torch.zeros_like(p12))
    output = torch.matmul(low_prob, v6) + torch.matmul(high_prob, v12)

    stats = module._apdt_stats
    stats["calls"] += 1
    stats["valid"] += int(valid.sum())
    stats["kept"] += int(keep.sum())
    stats["high"] += int(high.sum())
    stats["sigma_sum"] += float(sigma.mean())
    stats["threshold_sum"] += float(prune_threshold.mean())
    return output.transpose(1, 2).contiguous(), probabilities


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--prompt", default="高分辨率生成模型需要联合剪枝和混合精度。")
    p.add_argument("--sigma-min", type=float, default=0.0)
    p.add_argument("--sigma-max", type=float, default=0.5)
    p.add_argument("--prune-alpha", type=float, default=0.005)
    p.add_argument("--prune-beta", type=float, default=0.0)
    p.add_argument("--quant-alpha", type=float, default=0.04)
    p.add_argument("--quant-beta", type=float, default=0.02)
    args = p.parse_args()
    if args.sigma_max <= args.sigma_min:
        p.error("--sigma-max must be greater than --sigma-min")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS

    directory = model_dir(args.model_dir)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    encoded = tokenizer(args.prompt, return_tensors="pt")
    ids, attention_mask = encoded["input_ids"], encoded["attention_mask"]
    with torch.inference_mode():
        reference = model(input_ids=ids, attention_mask=attention_mask, use_cache=False).logits[:, -1].float()

    ALL_ATTENTION_FUNCTIONS.register("apdt_reference", apdt_attention)
    model.config._attn_implementation = "apdt_reference"
    stats = {"calls": 0, "valid": 0, "kept": 0, "high": 0, "sigma_sum": 0.0, "threshold_sum": 0.0}
    config = {
        "sigma_min": args.sigma_min,
        "sigma_max": args.sigma_max,
        "prune_alpha": args.prune_alpha,
        "prune_beta": args.prune_beta,
        "quant_alpha": args.quant_alpha,
        "quant_beta": args.quant_beta,
    }
    for layer in model.model.layers:
        layer.self_attn.config._attn_implementation = "apdt_reference"
        layer.self_attn._apdt_config = config
        layer.self_attn._apdt_stats = stats
    with torch.inference_mode():
        quantized = model(input_ids=ids, attention_mask=attention_mask, use_cache=False).logits[:, -1].float()
        generated = model.generate(input_ids=ids, attention_mask=attention_mask, max_new_tokens=1, do_sample=False, use_cache=True)
    kept_fraction = stats["kept"] / stats["valid"]
    high_fraction = stats["high"] / stats["valid"]
    effective_bits = (stats["high"] * 12 + (stats["kept"] - stats["high"]) * 6) / stats["kept"]
    cosine = torch.nn.functional.cosine_similarity(reference, quantized, dim=-1).item()
    print(f"model=Qwen3-0.6B prompt_tokens={ids.numel()} attention_layers={len(model.model.layers)} calls={stats['calls']}")
    print(
        f"kept_edge_fraction={kept_fraction:.8f} high_precision_fraction={high_fraction:.8f} "
        f"effective_bits_per_kept_edge={effective_bits:.8f} mean_sigma={stats['sigma_sum']/stats['calls']:.8f} "
        f"mean_prune_threshold={stats['threshold_sum']/stats['calls']:.8f}"
    )
    print(
        f"logits_mae={(reference-quantized).abs().mean().item():.8f} cosine={cosine:.8f} "
        f"generated={tokenizer.decode(generated[0, ids.shape[1]:])!r}"
    )
    assert stats["calls"] >= len(model.model.layers)
    assert 0 < kept_fraction <= 1 and 6 <= effective_bits <= 12
    assert torch.isfinite(quantized).all()


if __name__ == "__main__":
    main()
