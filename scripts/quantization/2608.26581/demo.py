#!/usr/bin/env python3
"""RFQ Algorithm 1 software reference on a real Qwen3-0.6B."""
import argparse
import glob
import json
import math
import os

import torch

GRID = torch.tensor([0., 0.5, 1., 1.5, 2., 3., 4., 6.])


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits = [p for p in hits if os.path.exists(os.path.join(p, "tokenizer.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir")
    return hits[0]


def mxfp4(x, block=32):
    """Equation (3)-(4): last-dimension block-32 E2M1 fake quant."""
    original_dtype = x.dtype
    shape = x.shape
    rows = x.detach().float().reshape(-1, shape[-1])
    pad = (-shape[-1]) % block
    padded = torch.nn.functional.pad(rows, (0, pad)) if pad else rows
    blocks = padded.view(rows.shape[0], -1, block)
    maximum = blocks.abs().amax(-1, keepdim=True)
    scale = torch.where(maximum > 0,
                        torch.pow(2, torch.floor(torch.log2(maximum.clamp_min(1e-30)))),
                        torch.ones_like(maximum))
    normalized = blocks.abs() / scale
    grid = GRID.to(normalized.device)
    index = (normalized[..., None] - grid).abs().argmin(-1)
    quant = grid[index] * blocks.sign() * scale
    restored = quant.view(rows.shape[0], -1)[:, :shape[-1]].reshape(shape)
    return restored.to(original_dtype), quant, scale


def rfq_activation(x, fallback_fraction, block=32):
    base, base_blocks, _ = mxfp4(x, block)
    residual = x - base
    _, residual_blocks, _ = mxfp4(residual, block)
    # The paper leaves phi(p,r) construction unspecified. Max magnitude is
    # the stated outlier signal; top-fraction is a transparent engineering rule.
    source_rows = x.detach().float().reshape(-1, x.shape[-1])
    pad = (-x.shape[-1]) % block
    padded = torch.nn.functional.pad(source_rows, (0, pad)) if pad else source_rows
    outlier_score = padded.view_as(base_blocks).abs().amax(-1)
    total = outlier_score.numel()
    k = min(total, max(0, round(total * fallback_fraction)))
    mask = torch.zeros_like(outlier_score, dtype=torch.bool)
    if k:
        mask.flatten()[torch.topk(outlier_score.flatten(), k).indices] = True
    corrected = base_blocks + residual_blocks * mask[..., None]
    corrected = corrected.view(source_rows.shape[0], -1)[:, :x.shape[-1]].reshape_as(x)
    return base, corrected.to(x.dtype), mask


class RFQHooks:
    def __init__(self, fraction):
        self.fraction = fraction
        self.calls = self.blocks = self.fallback_blocks = 0

    def hook(self, _module, inputs):
        _, corrected, mask = rfq_activation(inputs[0], self.fraction)
        self.calls += 1
        self.blocks += mask.numel()
        self.fallback_blocks += int(mask.sum())
        return (corrected,) + tuple(inputs[1:])

    def reset(self, fraction=None):
        if fraction is not None:
            self.fraction = fraction
        self.calls = self.blocks = self.fallback_blocks = 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--fallback-fraction", type=float, default=.10)
    p.add_argument("--prompt", default="极低比特激活量化需要处理异常值。")
    args = p.parse_args()
    if not 0 <= args.fallback_fraction <= 1:
        p.error("--fallback-fraction must be in [0,1]")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_dir(args.model_dir)
    tok = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32).eval()
    inputs = tok(args.prompt, return_tensors="pt")
    with torch.inference_mode():
        clean_logits = model(**inputs).logits.detach().float()

    # Algorithm-1 operator test includes both quantized X and quantized Y.
    generator = torch.Generator().manual_seed(260826581)
    x_test = torch.randn(4, 64, generator=generator)
    w_test = torch.randn(16, 64, generator=generator)
    q_weight_test, _, _ = mxfp4(w_test)
    base_x, rfq_x, test_mask = rfq_activation(x_test, args.fallback_fraction)
    base_z = base_x @ q_weight_test.t()
    rfq_z = rfq_x @ q_weight_test.t()
    assert (x_test - rfq_x).pow(2).mean() <= (x_test - base_x).pow(2).mean()

    quantized_linears = quantized_weights = 0
    hook_state = RFQHooks(0.0)
    handles = []
    with torch.no_grad():
        for name, module in model.named_modules():
            if not isinstance(module, torch.nn.Linear) or name == "lm_head":
                continue
            q_weight, _, _ = mxfp4(module.weight)
            module.weight.copy_(q_weight)
            handles.append(module.register_forward_pre_hook(hook_state.hook))
            quantized_linears += 1
            quantized_weights += module.weight.numel()
    with torch.inference_mode():
        base_logits = model(**inputs).logits.detach().float()
    base_calls = hook_state.calls
    base_blocks = hook_state.blocks
    hook_state.reset(args.fallback_fraction)
    with torch.inference_mode():
        rfq_logits = model(**inputs).logits.detach().float()
    rfq_calls = hook_state.calls
    rfq_blocks = hook_state.blocks
    rfq_fallback_blocks = hook_state.fallback_blocks
    hook_state.reset(args.fallback_fraction)
    with torch.inference_mode():
        generated = model.generate(**inputs, max_new_tokens=1, do_sample=False,
                                   use_cache=False)
    for handle in handles:
        handle.remove()
    assert torch.isfinite(base_logits).all() and torch.isfinite(rfq_logits).all()
    base_mae = (clean_logits - base_logits).abs().mean().item()
    rfq_mae = (clean_logits - rfq_logits).abs().mean().item()
    result = {
        "model": "Qwen3-0.6B", "format": "MXFP4 E2M1 block32 equation-3 power-of-two scale",
        "fallback_indicator": "top block max-abs fraction (engineering rule; paper phi unspecified)",
        "quantized_linears": quantized_linears, "quantized_weights": quantized_weights,
        "lm_head_embedding": "FP32 (paper keeps sensitive endpoints BF16)",
        "operator_test": {"x_shape": list(x_test.shape), "y_shape": list(w_test.t().shape),
                          "fallback_blocks": int(test_mask.sum()),
                          "base_output_mse": (x_test @ w_test.t() - base_z).pow(2).mean().item(),
                          "rfq_output_mse": (x_test @ w_test.t() - rfq_z).pow(2).mean().item()},
        "full_model": {"base_calls": base_calls, "base_activation_blocks": base_blocks,
                       "rfq_calls": rfq_calls, "rfq_activation_blocks": rfq_blocks,
                       "rfq_fallback_blocks": rfq_fallback_blocks,
                       "actual_fallback_fraction": rfq_fallback_blocks / max(1, rfq_blocks),
                       "w4a4_base_logits_mae": base_mae, "w4a4_rfq_logits_mae": rfq_mae,
                       "rfq_mae_change_fraction": 1 - rfq_mae / max(base_mae, 1e-30),
                       "one_token_generation": tok.decode(generated[0], skip_special_tokens=True)},
        "qat_5b_tokens_multimodal_kernel_executed": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
