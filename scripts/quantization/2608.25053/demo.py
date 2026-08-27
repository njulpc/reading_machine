#!/usr/bin/env python3
"""Hydra-style phase-aware dense/W8 characterization on Qwen3-0.6B."""
import argparse
import glob
import os
import statistics
import time

import torch


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*'))
    hits += glob.glob('/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*')
    hits = [x for x in hits if os.path.exists(os.path.join(x, 'tokenizer.json'))]
    if not hits:
        raise FileNotFoundError('Pass --model-dir for a local Qwen3-0.6B snapshot')
    return hits[0]


def w8_per_row_(weight):
    x = weight.detach().float()
    scale = x.abs().amax(dim=1, keepdim=True).clamp_min(1e-12) / 127
    weight.copy_((x / scale).round().clamp(-127, 127).mul(scale).to(weight.dtype))


def phase_measure(model, input_ids, decode_steps=4):
    with torch.inference_mode():
        started = time.perf_counter()
        out = model(input_ids=input_ids, use_cache=True)
        prefill = time.perf_counter() - started
        cache = out.past_key_values
        token = out.logits[:, -1].argmax(-1, keepdim=True)
        decode = []
        for _ in range(decode_steps):
            started = time.perf_counter()
            out = model(input_ids=token, past_key_values=cache, use_cache=True)
            decode.append(time.perf_counter() - started)
            cache = out.past_key_values
            token = out.logits[:, -1].argmax(-1, keepdim=True)
    return prefill, decode, out.logits[:, -1].float()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model-dir')
    p.add_argument('--prompt', default='量化部署的性能必须区分预填充和解码阶段。')
    p.add_argument('--decode-steps', type=int, default=4)
    args = p.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_dir(args.model_dir)
    tok = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(directory, local_files_only=True, dtype=torch.float32).eval()
    ids = tok(args.prompt, return_tensors='pt')['input_ids']
    dense_prefill, dense_decode, dense_logits = phase_measure(model, ids, args.decode_steps)
    layers = elements = 0
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != 'lm_head':
                w8_per_row_(module.weight)
                layers += 1
                elements += module.weight.numel()
    w8_prefill, w8_decode, w8_logits = phase_measure(model, ids, args.decode_steps)
    cosine = torch.nn.functional.cosine_similarity(dense_logits, w8_logits, dim=-1).item()
    print(f'model=Qwen3-0.6B prompt_tokens={ids.numel()} linear_layers={layers} quantized_elements={elements}')
    print(f'dense_prefill_s={dense_prefill:.6f} dense_decode_median_s={statistics.median(dense_decode):.6f}')
    print(f'w8_prefill_s={w8_prefill:.6f} w8_decode_median_s={statistics.median(w8_decode):.6f}')
    print(f'analytical_fp32_bytes={elements*4} analytical_int8_payload_bytes={elements} payload_ratio=4.0000')
    print(f'last_token_cosine={cosine:.8f} logits_mae={(dense_logits-w8_logits).abs().mean().item():.8f}')
    assert layers == 196 and elements == 440401920
    assert cosine > 0.95 and torch.isfinite(w8_logits).all()


if __name__ == '__main__':
    main()
