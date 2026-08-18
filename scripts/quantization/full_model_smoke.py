#!/usr/bin/env python3
"""Real Qwen3-0.6B full-model numerical smoke tests for the daily reproductions."""
import argparse
import math
import time
from pathlib import Path

import torch


def affine(weight, bits):
    qmax = (1 << bits) - 1
    lo = weight.amin(1, keepdim=True); hi = weight.amax(1, keepdim=True)
    scale = ((hi - lo) / qmax).clamp_min(1e-8)
    zero = torch.round(-lo / scale).clamp(0, qmax)
    return scale * (torch.round(weight / scale + zero).clamp(0, qmax) - zero)


def int8(weight):
    scale = weight.abs().amax(1, keepdim=True).clamp_min(1e-8) / 127
    return torch.round(weight / scale).clamp(-128, 127) * scale


def flash(weight):
    k = max(1, math.ceil(weight.shape[1] * .01))
    idx = torch.topk(weight.abs(), k, dim=1).indices
    mask = torch.zeros_like(weight, dtype=torch.bool); mask.scatter_(1, idx, True)
    sparse = torch.where(mask, weight, torch.zeros_like(weight))
    return affine(torch.where(mask, torch.zeros_like(weight), weight), 4) + sparse


def binary(weight):
    scale = weight.abs().mean(1, keepdim=True)
    return weight.sign().masked_fill(weight == 0, 1) * scale


def two_bases(weight):
    first = binary(weight); residual = weight - first
    return first + binary(residual)


def quantize_linears(model, transform):
    count = params = 0
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head":
                module.weight.copy_(transform(module.weight.float()).to(module.weight.dtype))
                count += 1; params += module.weight.numel()
    return count, params


def activation_hook(kind):
    previous = {}
    block = 64

    def hook(name):
        def apply(_module, inputs):
            x = inputs[0]
            if kind == "nexus":
                lo = torch.quantile(x.float(), .0005); hi = torch.quantile(x.float(), .9995)
                scale = ((hi - lo) / 15).clamp_min(1e-8); zero = torch.round(-lo / scale).clamp(0, 15)
                q = scale * (torch.round(x / scale + zero).clamp(0, 15) - zero)
            elif kind == "binrvr":
                dims = tuple(range(x.ndim - 1)); scale = x.abs().mean(dims, keepdim=True).clamp_min(1e-8)
                q = x.sign().masked_fill(x == 0, 1) * scale
            else:
                old = previous.get(name); previous[name] = x.detach()
                if old is None or old.shape != x.shape:
                    return inputs
                delta = x - old; flat = delta.flatten(); chunks = list(flat.split(block))
                scores = torch.tensor([v.abs().sum() for v in chunks]); tz = torch.quantile(scores, .358); th = torch.quantile(scores, .951)
                out = []
                for values, score in zip(chunks, scores):
                    if score < tz: out.append(torch.zeros_like(values))
                    else:
                        bits = 8 if score > th else 4; qmax = (1 << (bits - 1)) - 1
                        scale = values.abs().amax().clamp_min(1e-8) / qmax
                        out.append(torch.round(values / scale).clamp(-qmax, qmax) * scale)
                q = old + torch.cat(out).reshape_as(x)
            return (q.to(x.dtype),) + inputs[1:]
        return apply
    return hook


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--method", choices=["bitflip", "flash", "schur", "flux", "specvla", "nexus", "binrvr"], required=True)
    p.add_argument("--prompt", default="Quantization makes language models")
    a = p.parse_args(); started = time.perf_counter()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(a.model_dir, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model_dir, local_files_only=True, dtype=torch.float32).eval()
    inputs = tokenizer(a.prompt, return_tensors="pt")
    with torch.no_grad(): baseline = model(**inputs).logits[:, -1].float()
    transforms = {"bitflip": int8, "flash": flash, "schur": lambda w: affine(w, 2), "flux": two_bases, "nexus": lambda w: affine(w, 4), "binrvr": binary}
    count = params = 0; handles = []
    if a.method in transforms:
        count, params = quantize_linears(model, transforms[a.method])
    if a.method in {"specvla", "nexus", "binrvr"}:
        factory = activation_hook(a.method)
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head":
                handles.append(module.register_forward_pre_hook(factory(name)))
        if a.method == "specvla":
            prime = {key: value.clone() for key, value in inputs.items()}
            prime["input_ids"][0, 0] = (prime["input_ids"][0, 0] + 1) % model.config.vocab_size
            with torch.no_grad(): model(**prime)
    with torch.no_grad():
        logits = model(**inputs).logits[:, -1].float()
    token = logits.argmax(-1)
    for handle in handles: handle.remove()
    print(f"method={a.method} model=Qwen3-0.6B linears_replaced={count} parameters_replaced={params}")
    print(f"full_forward_finite={bool(torch.isfinite(logits).all())} logits_mse={torch.nn.functional.mse_loss(logits, baseline).item():.8g}")
    print(f"generated_token_id={token.item()} generated_text={tokenizer.decode(token)}")
    print(f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
