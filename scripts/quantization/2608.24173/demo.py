#!/usr/bin/env python3
"""SandwichQuant two-stage affine correction on a full Qwen3 W3A16 graph."""
import argparse
import gc
import glob
import os
import time

import torch
import torch.nn.functional as F


def model_dir(path=None):
    if path:
        return path if os.path.isdir(path) else os.path.dirname(path)
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
    ))
    if not hits:
        raise FileNotFoundError("Qwen3-0.6B checkpoint missing")
    return os.path.dirname(hits[0])


def q3_groupwise(weight, group=128):
    shape = weight.shape
    rows = weight.float().reshape(-1, shape[-1])
    pad = (-rows.shape[1]) % group
    if pad:
        rows = F.pad(rows, (0, pad))
    blocks = rows.view(rows.shape[0], -1, group)
    scale = blocks.abs().amax(-1, keepdim=True).clamp_min(1e-12) / 3
    output = torch.round(blocks / scale).clamp(-3, 3) * scale
    return output.view(rows.shape)[:, :shape[-1]].reshape(shape)


def quantize_model_(model):
    count = elements = 0
    with torch.no_grad():
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear) and name != "lm_head":
                module.weight.copy_(q3_groupwise(module.weight).to(module.weight.dtype))
                count += 1
                elements += module.weight.numel()
    return count, elements


def affine_parameters(model):
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    selected = []
    for name, parameter in model.named_parameters():
        if name.endswith("norm.weight") or "layernorm.weight" in name:
            parameter.requires_grad_(True)
            selected.append((name, parameter))
    return selected


def objective(student, teacher, input_ids):
    shift_logits = student[:, :-1].contiguous()
    shift_labels = input_ids[:, 1:].contiguous()
    ce = F.cross_entropy(shift_logits.view(-1, shift_logits.shape[-1]), shift_labels.view(-1))
    kd = F.kl_div(
        F.log_softmax(student, dim=-1),
        F.softmax(teacher, dim=-1),
        reduction="batchmean",
    ) / student.shape[1]
    return ce + kd, ce.detach(), kd.detach()


def fit_affine(model, input_ids, teacher, steps, lr):
    selected = affine_parameters(model)
    optimizer = torch.optim.AdamW(
        [parameter for _, parameter in selected], lr=lr, weight_decay=0.0
    )
    losses = []
    model.train()
    for _ in range(steps):
        optimizer.zero_grad()
        student = model(input_ids=input_ids, use_cache=False).logits.float()
        loss, ce, kd = objective(student, teacher, input_ids)
        loss.backward()
        torch.nn.utils.clip_grad_norm_([parameter for _, parameter in selected], 1.0)
        optimizer.step()
        losses.append((float(loss.detach()), float(ce), float(kd)))
    model.eval()
    state = {name: parameter.detach().clone() for name, parameter in selected}
    return state, losses, sum(parameter.numel() for _, parameter in selected)


def load_model(directory):
    from transformers import AutoModelForCausalLM
    return AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32,
    )


def self_test():
    w = torch.tensor([[0.0, -1.0, 0.5, 2.0, -2.0]])
    q = q3_groupwise(w, group=4)
    assert q.shape == w.shape and torch.isfinite(q).all()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--tokens", type=int, default=32)
    args = parser.parse_args()
    self_test()
    directory = model_dir(args.checkpoint)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    seed = tokenizer(
        "量化模型需要在固定校准文本上保留下一词预测结构。",
        add_special_tokens=False,
    )["input_ids"]
    ids = (seed * ((args.tokens + len(seed) - 1) // len(seed)))[:args.tokens]
    input_ids = torch.tensor([ids])
    started = time.perf_counter()

    dense = load_model(directory).eval()
    with torch.inference_mode():
        teacher = dense(input_ids=input_ids, use_cache=False).logits.float()
    del dense
    gc.collect()

    # Disposable G1: PTQ from S0, train Phi_pre, then discard every quantized
    # weight and optimizer state as required by Algorithm 1.
    probe = load_model(directory)
    layers, elements = quantize_model_(probe)
    with torch.inference_mode():
        baseline = probe(input_ids=input_ids, use_cache=False).logits.float()
    pre_state, pre_losses, affine_count = fit_affine(
        probe, input_ids, teacher, args.steps, args.lr
    )
    del probe
    gc.collect()

    # Restore immutable S0, transfer only Phi_pre, and rebuild PTQ from scratch.
    deploy = load_model(directory)
    with torch.no_grad():
        named = dict(deploy.named_parameters())
        for name, value in pre_state.items():
            named[name].copy_(value)
    rebuilt_layers, rebuilt_elements = quantize_model_(deploy)
    post_state, post_losses, post_affine_count = fit_affine(
        deploy, input_ids, teacher, args.steps, args.lr
    )
    with torch.inference_mode():
        final_logits = deploy(input_ids=input_ids, use_cache=False).logits.float()
        generated = deploy.generate(input_ids=input_ids, max_new_tokens=1, do_sample=False, use_cache=True)

    baseline_error = float((baseline - teacher).square().mean())
    final_error = float((final_logits - teacher).square().mean())
    suffix = tokenizer.decode(generated[0, input_ids.shape[1]:])
    print(
        f"mode=W3A16-RTN group=128 linear_layers={layers} weight_elements={elements} "
        f"affine_parameters={affine_count} steps={args.steps}+{args.steps}"
    )
    print(f"pre_losses={pre_losses} post_losses={post_losses}")
    print(
        f"baseline_logits_mse={baseline_error:.8e} final_logits_mse={final_error:.8e} "
        f"closure={(baseline_error-final_error)/baseline_error:.4%} "
        f"generated={suffix!r} elapsed_seconds={time.perf_counter()-started:.3f}"
    )
    assert layers == rebuilt_layers == 196
    assert elements == rebuilt_elements == 440401920
    assert affine_count == post_affine_count and affine_count > 0
    assert torch.isfinite(final_logits).all() and generated.shape[1] > input_ids.shape[1]


if __name__ == "__main__":
    main()
