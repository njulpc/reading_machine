#!/usr/bin/env python3
"""Bangla Qwen3 audit under an explicit W8A16 RTN engineering baseline."""
import argparse
import glob
import os
import time

import torch


DEFAULT_TEXT = "বাংলা ভাষায় যুক্তি ও সাধারণ জ্ঞান বোঝার ক্ষমতা গুরুত্বপূর্ণ।"


def model_dir(path=None):
    if path:
        return path if os.path.isdir(path) else os.path.dirname(path)
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
    ))
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B checkpoint missing")
    return os.path.dirname(hits[0])


def quantize_rowwise_(weight):
    source = weight.float().clone()
    scale = source.abs().amax(1, keepdim=True).clamp_min(1e-12) / 127
    quantized = torch.round(source / scale).clamp(-128, 127) * scale
    weight.copy_(quantized.to(weight.dtype))
    return float((quantized - source).abs().mean())


def self_test():
    w = torch.tensor([[0.0, -1.0, 0.5], [2.0, -2.0, 0.0]])
    original = w.clone()
    error = quantize_rowwise_(w)
    assert torch.isfinite(w).all() and error >= 0
    assert torch.equal(w[:, 0] == 0, original[:, 0] == 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--text", default=DEFAULT_TEXT)
    parser.add_argument("--max-new-tokens", type=int, default=1)
    args = parser.parse_args()
    self_test()
    directory = model_dir(args.checkpoint)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32,
    ).eval()
    encoded = tokenizer(args.text, return_tensors="pt")
    with torch.inference_mode():
        reference = model(**encoded, use_cache=False).logits[:, -1].float()

    started = time.perf_counter()
    layers = elements = 0
    mean_errors = []
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head":
                mean_errors.append(quantize_rowwise_(module.weight))
                layers += 1
                elements += module.weight.numel()
    quant_seconds = time.perf_counter() - started

    with torch.inference_mode():
        logits = model(**encoded, use_cache=False).logits[:, -1].float()
        generated = model.generate(
            **encoded, max_new_tokens=args.max_new_tokens, do_sample=False,
            use_cache=True,
        )
    mae = float((logits - reference).abs().mean())
    cosine = float(torch.nn.functional.cosine_similarity(logits, reference, dim=-1))
    suffix = tokenizer.decode(generated[0, encoded["input_ids"].shape[1]:])
    print(f"tokens={encoded['input_ids'].shape[1]} token_ids={encoded['input_ids'][0].tolist()}")
    print(
        f"mode=W8A16-RTN-engineering-transfer linear_layers={layers} "
        f"weight_elements={elements} quant_seconds={quant_seconds:.3f} "
        f"mean_weight_mae={sum(mean_errors)/len(mean_errors):.8e}"
    )
    print(
        f"last_logits_mae={mae:.8f} cosine={cosine:.8f} "
        f"theoretical_weight_compression_vs_fp16=2.00x generated={suffix!r}"
    )
    assert layers == 196 and elements == 440401920
    assert torch.isfinite(logits).all() and generated.shape[1] > encoded["input_ids"].shape[1]


if __name__ == "__main__":
    main()
