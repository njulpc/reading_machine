#!/usr/bin/env python3
"""Format-aware Hadamard test plus full-model INT4/MXFP4 reference quantization."""
import argparse
import glob
import os

import torch


E2M1 = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits += glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*")
    hits = [x for x in hits if os.path.exists(os.path.join(x, "tokenizer.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir")
    return hits[0]


def fwht(x):
    y = x.float().clone()
    n = y.shape[-1]
    if n & (n - 1):
        raise ValueError("last dimension must be a power of two")
    h = 1
    while h < n:
        z = y.reshape(y.shape[:-1] + (-1, 2, h))
        a, b = z[..., 0, :].clone(), z[..., 1, :].clone()
        z[..., 0, :], z[..., 1, :] = a + b, a - b
        y = z.reshape_as(y)
        h *= 2
    return y / n**0.5


def blocks(x, group):
    flat = x.float().flatten()
    pad = (-flat.numel()) % group
    padded = torch.nn.functional.pad(flat, (0, pad)) if pad else flat
    return padded.view(-1, group), flat.numel()


def int4_group(x, group=128):
    b, n = blocks(x, group)
    scale = b.abs().amax(1, keepdim=True).clamp_min(1e-12) / 7
    return (b / scale).round().clamp(-7, 7).mul(scale).flatten()[:n].view_as(x)


def fp4_absmax_group(x, group=128):
    """Ideal E2M1 with a real-valued AbsMax scale (grid-only comparison)."""
    b, n = blocks(x, group)
    scale = b.abs().amax(1, keepdim=True).clamp_min(1e-30) / 6
    normalized = b / scale
    idx = (normalized.abs()[..., None] - E2M1).abs().argmin(-1)
    restored = E2M1[idx] * normalized.sign() * scale
    return restored.flatten()[:n].view_as(x)


def mxfp4_group(x, group=32):
    """MXFP4 reference: E2M1 elements and the paper's floor-selected E8M0 scale."""
    b, n = blocks(x, group)
    maximum = b.abs().amax(1, keepdim=True).clamp_min(2.0**-126)
    scale = torch.pow(2.0, torch.floor(torch.log2(maximum)) - 2)
    normalized = b / scale
    idx = (normalized.abs()[..., None] - E2M1).abs().argmin(-1)
    restored = E2M1[idx] * normalized.sign() * scale
    return restored.flatten()[:n].view_as(x)


def randomized_group_hadamard(x, group=128, seed=42):
    b, n = blocks(x, group)
    generator = torch.Generator().manual_seed(seed)
    signs = torch.randint(0, 2, b.shape, generator=generator).mul(2).sub(1)
    rotated = fwht(b * signs)
    recovered = fwht(rotated) * signs
    assert torch.allclose(b, recovered, atol=2e-5, rtol=2e-5)
    return rotated.flatten()[:n].view_as(x)


def metric(label, x, q):
    mse = (x - q).square().mean().item()
    sqnr = 10 * torch.log10(x.square().mean() / (x - q).square().mean().clamp_min(1e-30)).item()
    print(f"{label}_mse={mse:.10e} {label}_sqnr_db={sqnr:.6f}")
    return mse, sqnr


def quantize_model_(model, fmt):
    quantizer = int4_group if fmt == "int4" else mxfp4_group
    count = elements = 0
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head":
                module.weight.copy_(quantizer(module.weight).to(module.weight.dtype))
                count += 1
                elements += module.weight.numel()
    return count, elements


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--prompt", default="变换、分组尺度和数值格式必须共同设计。")
    p.add_argument("--full-model-format", choices=("int4", "mxfp4"), default="mxfp4")
    args = p.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer

    directory = model_dir(args.model_dir)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32
    ).eval()
    encoded = tokenizer(args.prompt, return_tensors="pt")
    ids, attention_mask = encoded["input_ids"], encoded["attention_mask"]
    captured = {}
    handle = model.model.layers[0].register_forward_pre_hook(
        lambda _module, inputs: captured.setdefault("hidden", inputs[0].detach().float())
    )
    with torch.inference_mode():
        reference = model(input_ids=ids, attention_mask=attention_mask, use_cache=False).logits[:, -1].float()
    handle.remove()

    activation = captured["hidden"].reshape(-1, captured["hidden"].shape[-1])
    rotated = randomized_group_hadamard(activation, group=128)
    _, raw_int_sqnr = metric("raw_int4_g128", activation, int4_group(activation, 128))
    _, rot_int_sqnr = metric("rotated_int4_g128", rotated, int4_group(rotated, 128))
    _, raw_fp_sqnr = metric("raw_fp4_real_scale_g128", activation, fp4_absmax_group(activation, 128))
    _, rot_fp_sqnr = metric("rotated_fp4_real_scale_g128", rotated, fp4_absmax_group(rotated, 128))
    _, raw_mx_sqnr = metric("raw_mxfp4_g32", activation, mxfp4_group(activation, 32))
    _, rot_mx_sqnr = metric("rotated_mxfp4_g32", rotated, mxfp4_group(rotated, 32))
    print(
        f"rotation_gain_db int4={rot_int_sqnr-raw_int_sqnr:.6f} "
        f"ideal_fp4={rot_fp_sqnr-raw_fp_sqnr:.6f} mxfp4={rot_mx_sqnr-raw_mx_sqnr:.6f}"
    )

    count, elements = quantize_model_(model, args.full_model_format)
    with torch.inference_mode():
        quantized = model(input_ids=ids, attention_mask=attention_mask, use_cache=False).logits[:, -1].float()
        generated = model.generate(input_ids=ids, attention_mask=attention_mask, max_new_tokens=1, do_sample=False, use_cache=True)
    cosine = torch.nn.functional.cosine_similarity(reference, quantized, dim=-1).item()
    print(
        f"full_model_format={args.full_model_format} layers={count} elements={elements} "
        f"logits_mae={(reference-quantized).abs().mean().item():.8f} cosine={cosine:.8f} "
        f"generated={tokenizer.decode(generated[0, ids.shape[1]:])!r}"
    )
    assert count == 196 and elements == 440401920
    assert torch.isfinite(quantized).all() and torch.isfinite(torch.tensor(cosine))


if __name__ == "__main__":
    main()
