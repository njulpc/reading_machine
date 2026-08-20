#!/usr/bin/env python3
"""Qwen3-0.6B reproduction of the proactive-interference PTQ evaluation.

The paper evaluates bitsandbytes FP16/LLM.int8/NF4 models. bitsandbytes has no
usable backend in this CPU-only environment, so this portable reference applies
data-free fake quantization to Qwen3 linear weights and evaluates the same causal
question: does lower precision make a model select an older value after a key is
rebound repeatedly? It never claims storage or kernel speedups.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import random
import time
from dataclasses import asdict, dataclass

import torch


NF4 = torch.tensor(
    [
        -1.0,
        -0.6961928009986877,
        -0.5250730514526367,
        -0.39491748809814453,
        -0.28444138169288635,
        -0.18477343022823334,
        -0.09105003625154495,
        0.0,
        0.07958029955625534,
        0.16093020141124725,
        0.24611230194568634,
        0.33791524171829224,
        0.44070982933044434,
        0.5626170039176941,
        0.7229568362236023,
        1.0,
    ],
    dtype=torch.float32,
)


@dataclass
class Result:
    mode: str
    task: str
    level: int
    trials: int
    accuracy: float
    intrusion_rate: float


def fake_int8(weight: torch.Tensor) -> torch.Tensor:
    """Symmetric per-output-channel INT8, returned dequantized."""
    if weight.ndim != 2:
        raise ValueError("INT8 reference expects a matrix")
    scale = weight.float().abs().amax(dim=1, keepdim=True).clamp_min(1e-12) / 127.0
    return (weight.float() / scale).round().clamp(-127, 127) * scale


def _double_quant_scales(scales: torch.Tensor, block_size: int = 256) -> torch.Tensor:
    """Portable approximation of NF4 compressed statistics."""
    result = torch.empty_like(scales)
    offset = scales.mean()
    centered = scales - offset
    for start in range(0, scales.numel(), block_size):
        stop = min(start + block_size, scales.numel())
        block = centered[start:stop]
        quant_scale = block.abs().max().clamp_min(1e-12) / 127.0
        result[start:stop] = (block / quant_scale).round().clamp(-127, 127) * quant_scale + offset
    return result.clamp_min(1e-12)


def fake_nf4(weight: torch.Tensor, block_size: int = 64) -> torch.Tensor:
    """Block-64 NF4 with double-quantized absmax statistics, dequantized."""
    flat = weight.float().reshape(-1)
    padding = (-flat.numel()) % block_size
    padded = torch.nn.functional.pad(flat, (0, padding)) if padding else flat
    blocks = padded.reshape(-1, block_size)
    scales = blocks.abs().amax(dim=1).clamp_min(1e-12)
    scales = _double_quant_scales(scales)
    boundaries = ((NF4[:-1] + NF4[1:]) * 0.5).to(blocks.device)
    output = torch.empty_like(blocks)
    chunk = 4096
    for start in range(0, blocks.shape[0], chunk):
        stop = min(start + chunk, blocks.shape[0])
        normalized = (blocks[start:stop] / scales[start:stop, None]).clamp(-1, 1)
        codes = torch.bucketize(normalized.contiguous(), boundaries)
        output[start:stop] = NF4.to(blocks.device)[codes] * scales[start:stop, None]
    return output.reshape(-1)[: flat.numel()].reshape_as(weight)


def quantize_backbone_in_place(model: torch.nn.Module, mode: str) -> tuple[int, float]:
    """Quantize every backbone Linear matrix; leave embeddings/lm_head untouched."""
    if mode == "fp16":
        return 0, 0.0
    quantizer = fake_int8 if mode == "int8" else fake_nf4
    touched = 0
    absolute_error = 0.0
    elements = 0
    with torch.no_grad():
        for name, module in model.named_modules():
            if not isinstance(module, torch.nn.Linear) or name == "lm_head":
                continue
            original = module.weight.data
            quantized = quantizer(original)
            absolute_error += float((original.float() - quantized).abs().sum().item())
            elements += original.numel()
            module.weight.copy_(quantized.to(module.weight.dtype))
            touched += original.numel()
    return touched, absolute_error / max(elements, 1)


def one_token_values(tokenizer, values: list[str]) -> list[tuple[str, int]]:
    selected = []
    for value in values:
        ids = tokenizer.encode(value, add_special_tokens=False)
        if len(ids) == 1:
            selected.append((value, ids[0]))
    if len(selected) < 10:
        raise RuntimeError(f"too few single-token values: {selected}")
    return selected


def build_examples(tokenizer, task: str, level: int, trials: int, seed: int):
    word_pool = [
        "red", "blue", "green", "white", "black", "orange", "yellow", "purple",
        "cat", "dog", "horse", "tiger", "lion", "eagle", "shark", "whale",
        "Paris", "London", "Berlin", "Tokyo", "Rome", "Madrid", "Boston", "Miami",
    ]
    numeric_pool = [str(i) for i in range(10)]
    pool = one_token_values(tokenizer, word_pool if task == "word" else numeric_pool)
    randomizer = random.Random(seed + level + (0 if task == "word" else 1000))
    examples = []
    for trial in range(trials):
        key = f"slot-{trial % 7}"
        chosen = randomizer.sample(pool, level + 1)
        statements = [f"The value of {key} is {value}." for value, _ in chosen]
        prompt = (
            "Track the latest value after every overwrite.\n"
            + "\n".join(statements)
            + f"\nQuestion: What is the current value of {key}? Answer with exactly one value.\nAnswer: "
        )
        examples.append((prompt, chosen[-1][0], chosen))
    return examples


@torch.inference_mode()
def evaluate(model, tokenizer, task: str, levels: list[int], trials: int, seed: int, batch_size: int):
    results = []
    for level in levels:
        examples = build_examples(tokenizer, task, level, trials, seed)
        correct = 0
        intrusions = 0
        for start in range(0, len(examples), batch_size):
            batch = examples[start : start + batch_size]
            encoded = tokenizer(
                [item[0] for item in batch], return_tensors="pt", padding=True
            )
            logits = model(**encoded, use_cache=False).logits
            last_positions = encoded["attention_mask"].sum(dim=1) - 1
            for row, (_, target, candidates) in enumerate(batch):
                candidate_ids = [token_id for _, token_id in candidates]
                scores = logits[row, last_positions[row], candidate_ids]
                prediction = candidates[int(scores.argmax().item())][0]
                if prediction == target:
                    correct += 1
                elif prediction in {value for value, _ in candidates[:-1]}:
                    intrusions += 1
        results.append(
            Result(
                mode="",
                task=task,
                level=level,
                trials=trials,
                accuracy=correct / trials,
                intrusion_rate=intrusions / trials,
            )
        )
    return results


def self_test() -> None:
    weight = torch.linspace(-3, 3, 5 * 131).reshape(5, 131)
    int8 = fake_int8(weight)
    nf4 = fake_nf4(weight)
    assert int8.shape == weight.shape and nf4.shape == weight.shape
    assert torch.isfinite(int8).all() and torch.isfinite(nf4).all()
    assert float((weight - int8).abs().mean()) < 0.02
    assert float((weight - nf4).abs().mean()) < 0.25
    print("self_test=PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--modes", default="fp16,int8,nf4")
    parser.add_argument("--levels", default="0,1,2,4,8")
    parser.add_argument("--trials", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=12)
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print one concise CSV-like result line instead of the full JSON payload.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    levels = [int(value) for value in args.levels.split(",")]
    all_results = []
    for mode in args.modes.split(","):
        if mode not in {"fp16", "int8", "nf4"}:
            raise ValueError(f"unsupported mode: {mode}")
        started = time.perf_counter()
        model = AutoModelForCausalLM.from_pretrained(
            args.model, local_files_only=True, dtype=torch.float32, low_cpu_mem_usage=True
        ).eval()
        touched, mae = quantize_backbone_in_place(model, mode)
        for task in ("word", "numeric"):
            rows = evaluate(model, tokenizer, task, levels, args.trials, args.seed, args.batch_size)
            for row in rows:
                row.mode = mode
                all_results.append(row)
        elapsed = time.perf_counter() - started
        print(
            f"mode={mode} quantized_elements={touched:,} weight_mae={mae:.8f} "
            f"elapsed_seconds={elapsed:.2f}", flush=True
        )
        del model
        gc.collect()
    if args.compact:
        print("mode,task,level,accuracy,intrusion_rate")
        for row in all_results:
            print(
                f"{row.mode},{row.task},{row.level},"
                f"{row.accuracy:.6f},{row.intrusion_rate:.6f}"
            )
    else:
        print(json.dumps([asdict(row) for row in all_results], indent=2))


if __name__ == "__main__":
    main()
