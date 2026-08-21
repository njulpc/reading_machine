#!/usr/bin/env python3
"""Qwen3-0.6B adaptation of layer-wise E4M3 exponent-bias calibration.

The paper targets FFT-based LeNet-5 on an FPGA. Qwen has no FFT convolution, so
the paper's inverse-FFT weight scaling is not applicable. This demo faithfully
implements its E4M3 data format and per-layer bias selection, using real Qwen
linear activations and an exhaustive discrete search (the tiny search space's
exact counterpart to the paper's Bayesian optimizer). Values are dequantized
to FP32; no FPGA latency, storage, or native FP8-kernel claim is made.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys

import torch


def fake_e4m3(x: torch.Tensor, bias: int) -> torch.Tensor:
    """Finite-only E4M3 fake quantization with a configurable exponent bias."""
    if not 1 <= bias <= 14:
        raise ValueError("bias must be in [1, 14]")
    y = x.float()
    sign = torch.sign(y)
    a = y.abs()
    min_normal = 2.0 ** (1 - bias)
    max_finite = (2.0 - 2.0 ** -3) * (2.0 ** (14 - bias))
    sub_step = 2.0 ** (1 - bias - 3)
    sub = torch.round(a / sub_step) * sub_step
    safe = a.clamp_min(min_normal)
    exponent = torch.floor(torch.log2(safe)).clamp(1 - bias, 14 - bias)
    step = torch.pow(torch.tensor(2.0, device=y.device), exponent - 3)
    normal = torch.round(a / step) * step
    q = torch.where(a < min_normal, sub, normal).clamp_max(max_finite)
    return torch.where(a == 0, torch.zeros_like(q), sign * q)


def self_test() -> None:
    x = torch.tensor([0.0, 2.0 ** -10, -1.0, 1.875, 448.0, 1e6])
    q = fake_e4m3(x, 7)
    assert q.shape == x.shape and torch.isfinite(q).all()
    assert q[0] == 0 and q[-1] == 240.0
    assert torch.equal(fake_e4m3(torch.tensor([1.0, -2.0]), 7), torch.tensor([1.0, -2.0]))
    print("self_test=PASS")


def capture_inputs(model, tokenizer, prompt: str, max_layers: int, max_tokens: int):
    chosen = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear) and name != "lm_head":
            chosen.append((name, module))
        if len(chosen) >= max_layers:
            break
    captured = {}
    hooks = []
    for name, module in chosen:
        def hook(_module, args, _output, layer_name=name):
            captured[layer_name] = args[0].detach().float()[:, -max_tokens:, :].cpu()
        hooks.append(module.register_forward_hook(hook))
    encoded = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_tokens)
    with torch.no_grad():
        model(**encoded)
    for hook in hooks:
        hook.remove()
    return [(name, module, captured[name]) for name, module in chosen]


def calibrate_layer(module: torch.nn.Linear, x: torch.Tensor, biases: list[int]):
    w = module.weight.detach().float().cpu()
    b = module.bias.detach().float().cpu() if module.bias is not None else None
    with torch.no_grad():
        reference = torch.nn.functional.linear(x, w, b)
        rows = []
        for bias in biases:
            qx = fake_e4m3(x, bias)
            qw = fake_e4m3(w, bias)
            pred = torch.nn.functional.linear(qx, qw, b)
            mse = float(torch.mean((pred - reference) ** 2))
            rel = float(torch.linalg.vector_norm(pred - reference) /
                        torch.linalg.vector_norm(reference).clamp_min(1e-12))
            rows.append({"bias": bias, "mse": mse, "relative_l2": rel})
    best = min(rows, key=lambda row: row["mse"])
    fixed = next((row for row in rows if row["bias"] == 7), None)
    return best, fixed, rows, int(w.numel())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--biases", default="5,6,7,8,9,10,11")
    parser.add_argument("--max-layers", type=int, default=7)
    parser.add_argument("--max-tokens", type=int, default=32)
    parser.add_argument("--prompt", default="Explain why calibration data matters for FP8 quantization.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args()
    if args.self_test or args.self_test_only:
        self_test()
    if args.self_test_only:
        return
    biases = [int(value) for value in args.biases.split(",")]
    if len(set(biases)) != len(biases) or not biases:
        raise ValueError("bias candidates must be a non-empty unique list")
    if args.max_layers < 1 or args.max_tokens < 1:
        raise ValueError("max-layers and max-tokens must be positive")

    from transformers import AutoModelForCausalLM, AutoTokenizer, __version__ as tv
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, local_files_only=True, dtype=torch.float32, low_cpu_mem_usage=True
    ).eval()
    layers = capture_inputs(model, tokenizer, args.prompt, args.max_layers, args.max_tokens)
    report = {
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                        "torch": torch.__version__, "transformers": tv,
                        "cuda": torch.cuda.is_available(), "model": args.model,
                        "parameters": sum(p.numel() for p in model.parameters())},
        "format": "E4M3 finite-only fake quantization",
        "bias_candidates": biases,
        "calibration_tokens": args.max_tokens,
        "layers": [],
    }
    total = 0
    for name, module, x in layers:
        best, fixed, sweep, elements = calibrate_layer(module, x, biases)
        total += elements
        item = {"name": name, "shape": list(module.weight.shape), "elements": elements,
                "selected": best, "fixed_bias_7": fixed, "sweep": sweep}
        report["layers"].append(item)
        print(f"layer={name} shape={tuple(module.weight.shape)} selected_bias={best['bias']} "
              f"selected_mse={best['mse']:.8g} fixed7_mse={fixed['mse']:.8g}", flush=True)
    report["quantized_weight_elements"] = total
    report["geometric_mean_mse_ratio_selected_over_fixed7"] = math.exp(sum(
        math.log(max(x["selected"]["mse"], 1e-30) / max(x["fixed_bias_7"]["mse"], 1e-30))
        for x in report["layers"]) / len(report["layers"]))
    print("RESULT_JSON=" + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
