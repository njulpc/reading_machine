#!/usr/bin/env python3
"""Global-weighted pruning transferred from BNNs to Qwen3-0.6B MLPs."""
import argparse
import glob
import json
import math
import os

import torch


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits = [p for p in hits if os.path.exists(os.path.join(p, "config.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir")
    return hits[0]


def score_tensor(weight, normalization):
    w = weight.detach().float()
    if normalization == "channel":
        norm = w.abs().amax(dim=1, keepdim=True).clamp_min(1e-12)
    else:
        norm = w.abs().amax().clamp_min(1e-12)
    return w.abs() / norm


def exact_streaming_quantile(modules, ratio, normalization, bins=65536):
    """Find the global order statistic without materializing every score."""
    hist = torch.zeros(bins, dtype=torch.float64)
    total = 0
    for _, module in modules:
        score = score_tensor(module.weight, normalization)
        hist += torch.histc(score, bins=bins, min=0.0, max=1.0).double()
        total += score.numel()
    target = min(total - 1, max(0, math.floor(ratio * total)))
    bucket = int(torch.searchsorted(hist.cumsum(0), torch.tensor(target + 1)).item())
    low = max(0.0, (bucket - 1) / bins)
    high = min(1.0 + 1e-7, (bucket + 2) / bins)
    below = 0
    candidates = []
    for _, module in modules:
        score = score_tensor(module.weight, normalization)
        below += int((score < low).sum())
        selected = score[(score >= low) & (score < high)]
        if selected.numel():
            candidates.append(selected.cpu())
    candidates = torch.cat(candidates)
    rank = target - below
    if rank < 0 or rank >= candidates.numel():
        raise RuntimeError("streaming quantile bracket did not contain target")
    return torch.kthvalue(candidates, rank + 1).values, total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--pruning-ratio", type=float, default=.70)
    p.add_argument("--normalization", choices=("channel", "layer"), default="channel")
    p.add_argument("--scope", choices=("all-mlp", "block0"), default="all-mlp")
    p.add_argument("--prompt", default="全局加权剪枝需要在量化后验证模型前向。")
    args = p.parse_args()
    if not 0 < args.pruning_ratio < 1:
        p.error("ratio must be in (0,1)")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_dir(args.model_dir)
    tok = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32).eval()
    inputs = tok(args.prompt, return_tensors="pt")
    with torch.inference_mode():
        clean_logits = model(**inputs).logits.detach().float()

    if args.scope == "block0":
        root = model.model.layers[0]
        modules = [("model.layers.0." + n, m) for n, m in root.named_modules()
                   if isinstance(m, torch.nn.Linear)]
    else:
        modules = [(n, m) for n, m in model.named_modules()
                   if isinstance(m, torch.nn.Linear) and ".mlp." in n]
    threshold, total = exact_streaming_quantile(
        modules, args.pruning_ratio, args.normalization)
    target_pruned = round(args.pruning_ratio * total)
    strictly_below = sum(int((score_tensor(module.weight, args.normalization)
                              < threshold).sum()) for _, module in modules)
    ties_to_prune = target_pruned - strictly_below
    kept = 0
    errors = []
    with torch.no_grad():
        for _, module in modules:
            w = module.weight.detach().float()
            score = score_tensor(w, args.normalization)
            mask = score >= threshold
            tie_indices = (score == threshold).flatten().nonzero().flatten()
            prune_here = min(ties_to_prune, tie_indices.numel())
            if prune_here:
                mask.flatten()[tie_indices[:prune_here]] = False
                ties_to_prune -= prune_here
            # Qwen has no BN to absorb sign-weight amplitude. This explicit
            # XNOR-style alpha is an engineering transfer, not the paper's BNN.
            alpha = w.abs().mean(dim=1, keepdim=True).clamp_min(1e-12)
            binary = torch.where(w >= 0, alpha, -alpha) * mask
            errors.append(((w - binary).pow(2).mean() /
                           w.pow(2).mean().clamp_min(1e-30)).item())
            module.weight.copy_(binary.to(module.weight.dtype))
            kept += int(mask.sum())
    with torch.inference_mode():
        pruned_logits = model(**inputs).logits.detach().float()
        generated = model.generate(**inputs, max_new_tokens=1, do_sample=False,
                                   use_cache=False)
    assert torch.isfinite(pruned_logits).all()
    actual = 1 - kept / total
    result = {
        "model": "Qwen3-0.6B", "scope": args.scope,
        "linear_modules": len(modules), "weights": total,
        "target_pruning_ratio": args.pruning_ratio,
        "actual_pruning_ratio": actual, "global_threshold": threshold.item(),
        "global_weighting": f"per-{args.normalization} L_inf then one global ordering",
        "threshold_algorithm": "exact streaming histogram bracket plus local order statistic",
        "binary_transfer": "per-output-channel mean-abs alpha times sign (Qwen engineering substitute)",
        "mean_normalized_weight_mse": sum(errors) / len(errors),
        "bmac_before": total, "bmac_after": kept,
        "logits_mae": (clean_logits - pruned_logits).abs().mean().item(),
        "last_token_cosine": torch.nn.functional.cosine_similarity(
            clean_logits[:, -1].flatten(), pruned_logits[:, -1].flatten(), dim=0).item(),
        "one_token_generation": tok.decode(generated[0], skip_special_tokens=True),
        "paper_training_and_accuracy_search_executed": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert ties_to_prune == 0
    assert abs((total - kept) - target_pruned) == 0


if __name__ == "__main__":
    main()
