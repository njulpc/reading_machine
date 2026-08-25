#!/usr/bin/env python3
"""SplitLite low-rank temporal residual compression reference.

Implements arXiv:2608.23018 Algorithm 2: synchronized per-sample cache,
rank-2r activation and rank-4r gradient residual SVD, factor-wise unbiased
stochastic uniform quantization, reconstruction, and cache update.
"""

import argparse
import glob
import os
import time

import torch


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


def stochastic_uniform_qdq(x, bits, generator):
    """Unbiased stochastic rounding on a symmetric, tensor-wise uniform grid."""
    if bits < 2:
        raise ValueError("bits must be >=2")
    qmax = (1 << (bits - 1)) - 1
    scale = x.abs().amax().clamp_min(1e-12) / qmax
    normalized = (x / scale).clamp(-qmax, qmax)
    lower = torch.floor(normalized)
    probability = normalized - lower
    rounded = lower + (
        torch.rand(probability.shape, generator=generator, device=x.device)
        < probability
    ).to(x.dtype)
    rounded = rounded.clamp(-qmax, qmax)
    code_dtype = torch.int8 if bits <= 8 else torch.int16
    codes = rounded.to(code_dtype)
    return codes.float() * scale, codes, scale.float()


def compress_against_cache(current, cache, rank, bits, seed):
    """Algorithm 2 for one direction and one sample."""
    if cache is None:
        return current.clone(), {
            "full": True,
            "transmitted_bits": current.numel() * 32,
            "rank": min(current.shape),
        }
    residual = current - cache
    u, singular, vh = torch.linalg.svd(residual.float(), full_matrices=False)
    kept_rank = min(rank, len(singular))
    left = u[:, :kept_rank] * singular[:kept_rank]
    right = vh[:kept_rank]
    generator = torch.Generator(device=current.device).manual_seed(seed)
    left_hat, left_codes, left_scale = stochastic_uniform_qdq(left, bits, generator)
    right_hat, right_codes, right_scale = stochastic_uniform_qdq(right, bits, generator)
    reconstructed_residual = left_hat @ right_hat
    reconstructed = cache + reconstructed_residual
    packet_bits = (left_codes.numel() + right_codes.numel()) * bits + 64
    packet = {
        "full": False,
        "rank": kept_rank,
        "bits": bits,
        "left_codes": left_codes,
        "right_codes": right_codes,
        "left_scale": left_scale,
        "right_scale": right_scale,
        "transmitted_bits": packet_bits,
    }
    return reconstructed, packet


def rel_l2(reference, actual):
    return float(
        torch.linalg.vector_norm(reference.float() - actual.float())
        / torch.linalg.vector_norm(reference.float()).clamp_min(1e-20)
    )


def self_test():
    generator = torch.Generator().manual_seed(1)
    cache = torch.randn(12, 16, generator=generator)
    left = torch.randn(12, 4, generator=generator)
    right = torch.randn(4, 16, generator=generator)
    current = cache + left @ right
    reconstructed, packet = compress_against_cache(current, cache, 4, 8, 2)
    assert packet["rank"] == 4 and not packet["full"]
    assert torch.isfinite(reconstructed).all()
    first, initial_packet = compress_against_cache(current, None, 4, 8, 2)
    assert initial_packet["full"] and torch.equal(first, current)


def run_operator(sequence, hidden, lora_rank):
    generator = torch.Generator().manual_seed(17)
    activation_cache = torch.randn(sequence, hidden, generator=generator)
    gradient_cache = torch.randn(sequence, hidden, generator=generator)
    activation_residual = torch.randn(sequence, 2 * lora_rank, generator=generator) @ torch.randn(
        2 * lora_rank, hidden, generator=generator
    )
    gradient_residual = torch.randn(sequence, 4 * lora_rank, generator=generator) @ torch.randn(
        4 * lora_rank, hidden, generator=generator
    )
    activation = activation_cache + activation_residual
    gradient = gradient_cache + gradient_residual
    activation_hat, activation_packet = compress_against_cache(
        activation, activation_cache, 2 * lora_rank, 4, 23
    )
    gradient_hat, gradient_packet = compress_against_cache(
        gradient, gradient_cache, 4 * lora_rank, 8, 29
    )
    full_bits = 2 * activation.numel() * 32
    compressed_bits = (
        activation_packet["transmitted_bits"] + gradient_packet["transmitted_bits"]
    )
    print(
        f"operator_shape={sequence}x{hidden} lora_rank={lora_rank} "
        f"activation_rank={activation_packet['rank']} gradient_rank={gradient_packet['rank']}"
    )
    print(
        f"activation_q4_rel_l2={rel_l2(activation, activation_hat):.8f} "
        f"gradient_q8_rel_l2={rel_l2(gradient, gradient_hat):.8f}"
    )
    print(
        f"steady_state_full_bits={full_bits} packet_bits={compressed_bits} "
        f"compression={full_bits / compressed_bits:.3f}x"
    )


def replace_hidden(output, hidden):
    if isinstance(output, tuple):
        return (hidden,) + output[1:]
    return hidden


def extract_hidden(output):
    return output[0] if isinstance(output, tuple) else output


def cut_forward(model, inputs, cut_layer, need_gradient):
    record = {}

    def capture(_module, _args, output):
        hidden = extract_hidden(output).detach().requires_grad_(need_gradient)
        record["hidden"] = hidden
        return replace_hidden(output, hidden)

    handle = model.model.layers[cut_layer - 1].register_forward_hook(capture)
    if need_gradient:
        output = model(**inputs, labels=inputs["input_ids"], use_cache=False)
        output.loss.backward()
        gradient = record["hidden"].grad.detach().clone()
        logits = output.logits.detach()
        loss = float(output.loss.detach())
    else:
        with torch.no_grad():
            output = model(**inputs, use_cache=False)
        gradient = None
        logits = output.logits.detach()
        loss = float("nan")
    hidden = record["hidden"].detach().clone()
    handle.remove()
    return hidden, gradient, logits, loss


def run_full_model(path, prompt, cut_layer, lora_rank, adapter_scale, save_packet):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started = time.perf_counter()
    model_dir = os.path.dirname(path)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir, local_files_only=True, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    inputs = tokenizer(prompt, return_tensors="pt")
    baseline_hidden, baseline_gradient, _, baseline_loss = cut_forward(
        model, inputs, cut_layer, True
    )

    target = model.model.layers[0].self_attn.q_proj.weight
    generator = torch.Generator().manual_seed(41)
    left = torch.randn(target.shape[0], lora_rank, generator=generator) * adapter_scale
    right = torch.randn(lora_rank, target.shape[1], generator=generator) * adapter_scale
    delta = left @ right
    with torch.no_grad():
        target.add_(delta)
    current_hidden, current_gradient, current_logits, current_loss = cut_forward(
        model, inputs, cut_layer, True
    )

    activation_hat, activation_packet = compress_against_cache(
        current_hidden.squeeze(0), baseline_hidden.squeeze(0), 2 * lora_rank, 4, 43
    )
    gradient_hat, gradient_packet = compress_against_cache(
        current_gradient.squeeze(0), baseline_gradient.squeeze(0), 4 * lora_rank, 8, 47
    )
    activation_hat = activation_hat.unsqueeze(0)

    def inject(_module, _args, output):
        hidden = extract_hidden(output)
        if hidden.shape == activation_hat.shape:
            return replace_hidden(output, activation_hat.to(hidden.dtype))
        return output

    injection = model.model.layers[cut_layer - 1].register_forward_hook(inject)
    with torch.no_grad():
        repaired_logits = model(**inputs, use_cache=False).logits
        generated = model.generate(
            **inputs, max_new_tokens=1, do_sample=False, use_cache=False
        )
    injection.remove()
    with torch.no_grad():
        target.sub_(delta)

    if save_packet:
        torch.save(
            {
                "cut_layer": cut_layer,
                "lora_rank": lora_rank,
                "activation": activation_packet,
                "gradient": gradient_packet,
            },
            save_packet,
        )
        loaded = torch.load(save_packet, map_location="cpu", weights_only=True)
        assert loaded["cut_layer"] == cut_layer
    current_last = current_logits[:, -1].float()
    repaired_last = repaired_logits[:, -1].float()
    cosine = float(
        torch.nn.functional.cosine_similarity(current_last, repaired_last, dim=-1).mean()
    )
    cosine = max(-1.0, min(1.0, cosine))
    print(
        f"full_model=Qwen3-0.6B parameters={sum(p.numel() for p in model.parameters())} "
        f"cut_layer={cut_layer} sequence={inputs['input_ids'].shape[1]} hidden={current_hidden.shape[-1]} "
        f"lora_rank={lora_rank}"
    )
    print(
        f"baseline_loss={baseline_loss:.8f} current_loss={current_loss:.8f} "
        f"activation_reconstruction_rel_l2={rel_l2(current_hidden, activation_hat):.8f} "
        f"gradient_reconstruction_rel_l2={rel_l2(current_gradient.squeeze(0), gradient_hat):.8f}"
    )
    print(
        f"repaired_logits_mae={float((current_logits - repaired_logits).abs().mean()):.8f} "
        f"last_token_cosine={cosine:.8f} "
        f"activation_packet_bits={activation_packet['transmitted_bits']} "
        f"gradient_packet_bits={gradient_packet['transmitted_bits']}"
    )
    print(
        f"saved_packet={save_packet or 'disabled'} generated={tokenizer.decode(generated[0])!r} "
        f"elapsed_seconds={time.perf_counter() - started:.3f}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint")
    parser.add_argument("--sequence", type=int, default=64)
    parser.add_argument("--hidden", type=int, default=256)
    parser.add_argument("--lora-rank", type=int, default=4)
    parser.add_argument("--full-model", action="store_true")
    parser.add_argument("--cut-layer", type=int, default=3)
    parser.add_argument("--adapter-scale", type=float, default=0.02)
    parser.add_argument("--save-packet")
    parser.add_argument(
        "--prompt",
        default="Split learning communicates cached activation and gradient residuals.",
    )
    args = parser.parse_args()
    self_test()
    run_operator(args.sequence, args.hidden, args.lora_rank)
    if args.full_model:
        path = checkpoint(args.checkpoint)
        run_full_model(
            path,
            args.prompt,
            args.cut_layer,
            args.lora_rank,
            args.adapter_scale,
            args.save_packet,
        )


if __name__ == "__main__":
    main()
