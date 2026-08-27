#!/usr/bin/env python3
"""Hydra-style common-schema timing with a Q8_0 numerical proxy on Qwen3-0.6B."""
import argparse
import glob
import json
import os
import statistics
import time

import torch


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits += glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*")
    hits = [x for x in hits if os.path.exists(os.path.join(x, "tokenizer.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir for a local Qwen3-0.6B snapshot")
    return hits[0]


def q8_0_reference_(weight, block_size=32):
    """Block-32 symmetric INT8 fake quant; return GGML-like element/scale payload."""
    x = weight.detach().float().flatten()
    pad = (-x.numel()) % block_size
    padded = torch.nn.functional.pad(x, (0, pad)) if pad else x
    blocks = padded.view(-1, block_size)
    scale = blocks.abs().amax(1, keepdim=True).clamp_min(1e-12) / 127
    restored = (blocks / scale).round().clamp(-127, 127).mul(scale).flatten()[: x.numel()]
    weight.copy_(restored.view_as(weight).to(weight.dtype))
    # Q8_0 stores 32 int8 values plus one fp16 block scale (34 bytes/block).
    return blocks.shape[0] * (block_size + 2)


def synchronize():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def phase_record(model, tokenizer, prompt, decode_steps=4):
    start = time.perf_counter()
    token_start = time.perf_counter()
    input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"]
    tokenization = time.perf_counter() - token_start
    synchronize()
    prefill_start = time.perf_counter()
    with torch.inference_mode():
        out = model(input_ids=input_ids, use_cache=True)
    synchronize()
    prefill_stage = time.perf_counter() - prefill_start
    prefill_logits = out.logits[:, -1].float().cpu()
    cache = out.past_key_values
    token = out.logits[:, -1].argmax(-1, keepdim=True)
    generation, detokenization, pieces = [], [], []
    with torch.inference_mode():
        for _ in range(decode_steps):
            synchronize()
            step_start = time.perf_counter()
            out = model(input_ids=token, past_key_values=cache, use_cache=True)
            synchronize()
            generation.append(time.perf_counter() - step_start)
            cache = out.past_key_values
            token = out.logits[:, -1].argmax(-1, keepdim=True)
            detok_start = time.perf_counter()
            pieces.append(tokenizer.decode(token[0]))
            detokenization.append(time.perf_counter() - detok_start)
    e2e = time.perf_counter() - start
    itl = [a + b for a, b in zip(generation, detokenization)]
    return {
        "prompt_tokens": int(input_ids.numel()),
        "output_tokens": decode_steps,
        "tokenization_s": tokenization,
        "prefill_stage_s": prefill_stage,
        "prefill_phase_s": tokenization + prefill_stage,
        "ttft_s": tokenization + prefill_stage,
        "generation_s": generation,
        "detokenization_s": detokenization,
        "itl_s": itl,
        "decode_phase_s": sum(itl),
        "e2e_s": e2e,
        "decode_median_s": statistics.median(generation),
        "decoded_text": "".join(pieces),
    }, prefill_logits


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--prompt", default="量化部署的性能必须区分预填充和解码阶段。")
    p.add_argument("--decode-steps", type=int, default=4)
    p.add_argument("--metrics-json", help="Optional path for the two common-schema records")
    args = p.parse_args()
    if args.decode_steps < 1:
        p.error("--decode-steps must be positive")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    directory = model_dir(args.model_dir)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32
    ).eval()
    dense_record, dense_logits = phase_record(model, tokenizer, args.prompt, args.decode_steps)
    layers = elements = q8_payload = 0
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head":
                q8_payload += q8_0_reference_(module.weight)
                layers += 1
                elements += module.weight.numel()
    q8_record, q8_logits = phase_record(model, tokenizer, args.prompt, args.decode_steps)
    cosine = torch.nn.functional.cosine_similarity(dense_logits, q8_logits, dim=-1).item()
    result = {
        "model": "Qwen3-0.6B",
        "backend": "transformers-cpu-reference",
        "dense_dtype": "fp32",
        "quant_format": "q8_0_block32_numerical_proxy",
        "linear_layers": layers,
        "quantized_elements": elements,
        "analytical_fp32_bytes": elements * 4,
        "analytical_q8_0_bytes": q8_payload,
        "payload_ratio": elements * 4 / q8_payload,
        "last_token_cosine": cosine,
        "logits_mae": (dense_logits - q8_logits).abs().mean().item(),
        "dense": dense_record,
        "q8_0_proxy": q8_record,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.metrics_json:
        with open(args.metrics_json, "w", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    assert layers == 196 and elements == 440401920
    assert q8_payload == (elements // 32) * 34
    assert cosine > 0.95 and torch.isfinite(q8_logits).all()


if __name__ == "__main__":
    main()
