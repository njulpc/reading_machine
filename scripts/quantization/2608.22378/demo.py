#!/usr/bin/env python3
"""Software checks for arXiv:2608.22378 variable-bit approximate PEs.

The operator check models format conversion and least-significant partial-product
column truncation. The paper's eight compressor RTL variants, NSGA-II search,
and synthesis/PPA flow are not specified here and are deliberately not faked.
"""

import argparse
import glob
import os
import time

import torch


FORMATS = {
    "FP32": (24, 23),  # significand bits (hidden bit included), stored mantissa bits
    "TF32": (11, 10),
    "BF16": (8, 7),
}


def checkpoint(explicit=None):
    if explicit:
        if os.path.isdir(explicit):
            explicit = os.path.join(explicit, "model.safetensors")
        if os.path.isfile(explicit):
            return explicit
        raise FileNotFoundError(explicit)
    patterns = [
        os.path.expanduser(
            "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/"
            "snapshots/*/model.safetensors"
        ),
        "/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/"
        "snapshots/*/model.safetensors",
    ]
    hits = sum((glob.glob(pattern) for pattern in patterns), [])
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B not found; pass --checkpoint")
    return hits[0]


def load_matrix(path, size):
    from safetensors import safe_open

    with safe_open(path, framework="pt", device="cpu") as handle:
        key = next(key for key in handle.keys() if key.endswith("q_proj.weight"))
        weight = handle.get_tensor(key).float()[:size, :size].contiguous()
    return key, weight


def truncate_mantissa(x, keep):
    """Truncate stored FP32 mantissa bits; sign and exponent are unchanged."""
    if not 0 <= keep <= 23:
        raise ValueError("keep must be in [0, 23]")
    if keep == 23:
        return x.float().clone()
    values = x.float().contiguous()
    integers = values.view(torch.int32)
    drop = 23 - keep
    mask = ~((1 << drop) - 1)
    return (integers & mask).view(torch.float32)


def ppm_truncated_product(left, right, significand_bits, truncated_columns):
    """Reference the PPM-column operation before compressor reduction.

    Normal finite values are converted to integer significands. Clearing the
    lowest product bits is equivalent to deleting the least-significant PPM
    columns. This does not model the paper's positive/negative compressors.
    """
    left = left.float()
    right = right.float()
    left_m, left_e = torch.frexp(left.abs())
    right_m, right_e = torch.frexp(right.abs())
    multiplier = float(1 << (significand_bits - 1))
    max_significand = (1 << significand_bits) - 1
    left_i = torch.round(left_m * 2.0 * multiplier).clamp(0, max_significand).to(torch.int64)
    right_i = torch.round(right_m * 2.0 * multiplier).clamp(0, max_significand).to(torch.int64)
    product = left_i * right_i
    if truncated_columns:
        product = (product >> truncated_columns) << truncated_columns
    exponent = left_e + right_e - 2 - 2 * (significand_bits - 1)
    output = torch.ldexp(product.float(), exponent)
    output = torch.copysign(output, left * right)
    output[(left == 0) | (right == 0)] = 0
    return output


def approximate_matmul(x, weight, significand_bits, truncated_columns):
    products = ppm_truncated_product(
        x[:, :, None], weight.t()[None, :, :], significand_bits, truncated_columns
    )
    return products.sum(1)


def metric(reference, actual):
    rel = float(
        torch.linalg.vector_norm(reference - actual)
        / torch.linalg.vector_norm(reference).clamp_min(1e-20)
    )
    cosine = float(
        torch.nn.functional.cosine_similarity(
            reference.flatten(), actual.flatten(), dim=0
        )
    )
    return rel, max(-1.0, min(1.0, cosine))


def self_test():
    left = torch.tensor([1.0, -1.5, 0.0, 3.25])
    right = torch.tensor([2.0, 0.5, 7.0, -2.0])
    exact = left * right
    full = ppm_truncated_product(left, right, 24, 0)
    assert torch.allclose(full, exact, rtol=1e-6, atol=1e-6)
    truncated = ppm_truncated_product(left, right, 8, 3)
    assert torch.isfinite(truncated).all() and truncated[2] == 0


def run_operator(path, size, batch, tbits):
    key, weight = load_matrix(path, size)
    generator = torch.Generator().manual_seed(7)
    x = torch.randn(batch, size, generator=generator)
    reference = x @ weight.t()
    print(f"checkpoint={path}\ntensor={key} slice={tuple(weight.shape)}")
    for name, (significand_bits, stored_bits) in FORMATS.items():
        nominal = truncate_mantissa(x, stored_bits) @ truncate_mantissa(
            weight, stored_bits
        ).t()
        ppm = approximate_matmul(x, weight, significand_bits, tbits)
        nominal_rel, nominal_cos = metric(reference, nominal)
        ppm_rel, ppm_cos = metric(reference, ppm)
        print(
            f"{name} significand_bits={significand_bits} nominal_rel_l2={nominal_rel:.8f} "
            f"nominal_cos={nominal_cos:.8f} ppm_truncated_columns={tbits} "
            f"ppm_rel_l2={ppm_rel:.8f} ppm_cos={ppm_cos:.8f}"
        )
        assert torch.isfinite(ppm).all()


def run_full_model(path, prompt, keep_bits):
    """Qwen-wide operand-format stress test, not proposed-compressor emulation."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started = time.perf_counter()
    model_dir = os.path.dirname(path)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir, local_files_only=True, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        reference = model(**inputs, use_cache=False).logits.detach()

    hooks = []
    linear_count = 0
    weight_elements = 0
    for layer in model.model.layers:
        for module in layer.modules():
            if not isinstance(module, torch.nn.Linear):
                continue
            linear_count += 1
            weight_elements += module.weight.numel()
            with torch.no_grad():
                module.weight.copy_(truncate_mantissa(module.weight, keep_bits))

            def pre_hook(_module, args, keep=keep_bits):
                return (truncate_mantissa(args[0], keep),) + tuple(args[1:])

            hooks.append(module.register_forward_pre_hook(pre_hook))
    with torch.no_grad():
        quantized = model(**inputs, use_cache=False).logits
        generated = model.generate(
            **inputs, max_new_tokens=1, do_sample=False, use_cache=False
        )
    for hook in hooks:
        hook.remove()
    rel, cosine = metric(reference, quantized)
    print(
        f"full_model=Qwen3-0.6B parameters={sum(p.numel() for p in model.parameters())} "
        f"linear_modules={linear_count} transformed_weight_elements={weight_elements} "
        f"operand_mantissa_keep={keep_bits}"
    )
    print(
        f"operand_format_logits_rel_l2={rel:.8f} last_token_cosine={cosine:.8f} "
        f"generated={tokenizer.decode(generated[0])!r} "
        f"elapsed_seconds={time.perf_counter() - started:.3f}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--size", type=int, default=64)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--truncated-columns", type=int, default=3)
    parser.add_argument("--full-model", action="store_true")
    parser.add_argument("--full-keep-bits", type=int, default=7)
    parser.add_argument("--prompt", default="Hardware approximation must report its evidence boundary.")
    args = parser.parse_args()
    self_test()
    path = checkpoint(args.checkpoint)
    run_operator(path, args.size, args.batch, args.truncated_columns)
    if args.full_model:
        run_full_model(path, args.prompt, args.full_keep_bits)


if __name__ == "__main__":
    main()
