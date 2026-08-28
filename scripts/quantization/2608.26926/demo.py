#!/usr/bin/env python3
"""Paper-faithful SA-PTQ output SQNR and roofline ranking on Qwen3-0.6B."""
import argparse
import glob
import json
import math
import os
import time

import torch
import torch.nn.functional as F


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits = [p for p in hits if os.path.exists(os.path.join(p, "config.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir")
    return hits[0]


def sa_ptq_row(weight, bits):
    """Paper equations (3)-(5): per-row asymmetric min/max quantization."""
    w = weight.detach().float()
    lo = w.amin(dim=1, keepdim=True)
    hi = w.amax(dim=1, keepdim=True)
    step = ((hi - lo) / (2 ** bits - 1)).clamp_min(1e-12)
    return ((w - lo) / step).round().clamp(0, 2 ** bits - 1) * step + lo


def sqnr_db(clean, dirty):
    signal = clean.float().pow(2).sum().clamp_min(1e-30)
    noise = (clean.float() - dirty.float()).pow(2).sum().clamp_min(1e-30)
    return 10 * torch.log10(signal / noise).item()


def quality_normalize(sqnr):
    # Equations (11)-(12) operate on the numerical dB value itself.
    value = 1 - math.log10(2) / math.log10(max(sqnr, 1.000001))
    return min(1.0, max(0.0, value))


def dirty_mlp(mlp, hidden, bits):
    gate = F.linear(hidden, sa_ptq_row(mlp.gate_proj.weight, bits))
    up = F.linear(hidden, sa_ptq_row(mlp.up_proj.weight, bits))
    return F.linear(mlp.act_fn(gate) * up,
                    sa_ptq_row(mlp.down_proj.weight, bits))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--quality-weight", type=float, default=.5)
    p.add_argument("--bandwidth-gbps", type=float, default=50)
    p.add_argument("--q8-layers", type=int, default=10)
    p.add_argument("--prompt", default="量化层的输出失真和速度收益需要联合评估。")
    args = p.parse_args()
    if not 0 <= args.quality_weight <= 1:
        p.error("--quality-weight must be in [0,1]")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_dir(args.model_dir)
    tok = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32).eval()
    inputs = tok(args.prompt, return_tensors="pt")
    captured = {}
    handles = []
    for index, layer in enumerate(model.model.layers):
        def capture(_module, module_inputs, i=index):
            captured[i] = module_inputs[0][:, -1:, :].detach().cpu()
        handles.append(layer.mlp.register_forward_pre_hook(capture))
    started = time.perf_counter()
    with torch.inference_mode():
        clean_logits = model(**inputs).logits.detach().float()
    baseline_seconds = time.perf_counter() - started
    for handle in handles:
        handle.remove()

    rows = []
    for index, layer in enumerate(model.model.layers):
        hidden = captured[index]
        with torch.inference_mode():
            clean = layer.mlp(hidden).float()
            dirty8 = dirty_mlp(layer.mlp, hidden, 8).float()
            dirty4 = dirty_mlp(layer.mlp, hidden, 4).float()
        sq8, sq4 = sqnr_db(clean, dirty8), sqnr_db(clean, dirty4)
        elements = sum(m.weight.numel() for m in
                       (layer.mlp.gate_proj, layer.mlp.up_proj, layer.mlp.down_proj))
        saving8 = elements / (args.bandwidth_gbps * 1e9)
        speedup8 = baseline_seconds / max(1e-12, baseline_seconds - saving8)
        speed_score = min(1.0, max(0.0, math.log(speedup8, 2)))
        quality = quality_normalize(sq8)
        rows.append({
            "layer": index, "ffn_weights": elements, "q8_output_sqnr_db": sq8,
            "q4_output_sqnr_db": sq4, "quality_score": quality,
            "single_layer_q8_speedup": speedup8, "speed_score": speed_score,
            "priority": args.quality_weight * quality +
                        (1 - args.quality_weight) * speed_score,
        })
    sensitive = {r["layer"] for r in sorted(rows, key=lambda r: r["quality_score"])
                 [:max(0, min(args.q8_layers, len(rows))) ]}
    quantized_weights = 0
    mixed_bits = {}
    with torch.no_grad():
        for index, layer in enumerate(model.model.layers):
            bits = 8 if index in sensitive else 4
            mixed_bits[index] = bits
            for module in (layer.mlp.gate_proj, layer.mlp.up_proj,
                           layer.mlp.down_proj):
                module.weight.copy_(sa_ptq_row(module.weight, bits))
                quantized_weights += module.weight.numel()
    with torch.inference_mode():
        mixed_logits = model(**inputs).logits.detach().float()
        generated = model.generate(**inputs, max_new_tokens=1, do_sample=False,
                                   use_cache=False)
    assert torch.isfinite(mixed_logits).all()

    total_saving = sum(r["ffn_weights"] * (2 - mixed_bits[r["layer"]] / 8)
                       for r in rows) / (args.bandwidth_gbps * 1e9)
    predicted_seconds = max(1e-12, baseline_seconds - total_saving)
    rows.sort(key=lambda r: r["priority"], reverse=True)
    result = {
        "model": "Qwen3-0.6B", "calibration": "one prompt, last-token hidden state",
        "target": "FFN per-row asymmetric SA-PTQ; attention/embedding/lm_head FP32",
        "quality_weight_alpha": args.quality_weight,
        "baseline_forward_seconds_cpu": baseline_seconds,
        "roofline": {"bandwidth_gbps_assumption": args.bandwidth_gbps,
                     "measured_baseline_anchor": True,
                     "mixed_predicted_seconds": predicted_seconds,
                     "mixed_predicted_speedup": baseline_seconds / predicted_seconds},
        "mixed_precision": {"q8_sensitive_layers": sorted(sensitive),
                            "q4_other_layers": len(rows) - len(sensitive),
                            "quantized_ffn_weights": quantized_weights},
        "ranking": rows,
        "full_model": {"finite_logits": True,
                       "logits_mae": (clean_logits - mixed_logits).abs().mean().item(),
                       "last_token_cosine": F.cosine_similarity(
                           clean_logits[:, -1].flatten(), mixed_logits[:, -1].flatten(), dim=0).item(),
                       "one_token_generation": tok.decode(generated[0], skip_special_tokens=True)},
        "real_int_kernel_benchmark_executed": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert len(rows) == len(model.model.layers)


if __name__ == "__main__":
    main()
