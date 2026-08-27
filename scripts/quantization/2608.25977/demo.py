#!/usr/bin/env python3
"""Seven-option layer-wise entropy/gap and UALD on FP32/W4/W2 Qwen3-0.6B."""
import argparse
import gc
import glob
import os

import torch


QUESTIONS = [
    "You regularly make new friends.",
    "You spend a lot of your free time exploring various random topics that pique your interests.",
    "You usually stay calm, even under a lot of pressure.",
    "Seeing other people cry can easily make you feel like you want to cry too.",
    "At social events, you rarely try to introduce yourself to new people and mostly talk to the ones you already know.",
    "You prefer to completely finish one project before starting another.",
    "You are more inclined to follow your head than your heart.",
    "You become bored or lose interest when the discussion gets highly theoretical.",
]

PROMPT = """You are completing a personality traits assessment.
You will be given one statement, Q. Your task is to indicate how well the statement generally describes you.
Select exactly one option:
A = Agree
B = Generally Agree
C = Partially Agree
D = Neither Agree nor Disagree
E = Partially Disagree
F = Generally Disagree
G = Disagree
Respond based on your overall tendency. Do not overthink.
Q: {question}
Return ONLY one letter from: A, B, C, D, E, F, G."""


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits += glob.glob("/private/tmp/hf_arxiv/models--Qwen--Qwen3-0.6B/snapshots/*")
    hits = [x for x in hits if os.path.exists(os.path.join(x, "tokenizer.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir")
    return hits[0]


def quant_weight_(weight, bits, group=128):
    qmax = 2 ** (bits - 1) - 1
    x = weight.detach().float().flatten()
    pad = (-x.numel()) % group
    padded = torch.nn.functional.pad(x, (0, pad)) if pad else x
    blocks = padded.view(-1, group)
    scale = blocks.abs().amax(1, keepdim=True).clamp_min(1e-12) / qmax
    restored = (blocks / scale).round().clamp(-qmax, qmax).mul(scale)
    weight.copy_(restored.flatten()[: x.numel()].view_as(weight).to(weight.dtype))


def option_token_sets(tokenizer):
    sets = []
    for option in "ABCDEFG":
        ids = set()
        for form in (option, " " + option, "\n" + option):
            encoded = tokenizer.encode(form, add_special_tokens=False)
            if encoded:
                ids.add(encoded[-1])
        sets.append(sorted(ids))
    assert all(sets)
    return sets


def option_logits(model, hidden_states, token_sets):
    per_layer = []
    selected = hidden_states[1:]
    for index, hidden in enumerate(selected):
        normalized = hidden if index == len(selected) - 1 else model.model.norm(hidden)
        vocab = model.lm_head(normalized[:, -1]).float()
        per_layer.append(torch.stack([vocab[:, ids].amax(-1) for ids in token_sets], dim=-1).cpu())
    return torch.stack(per_layer)


def entropy_gap(probabilities):
    entropy = -(probabilities * probabilities.clamp_min(1e-30).log()).sum(-1)
    top2 = probabilities.topk(2, dim=-1).values
    return entropy, top2[..., 0] - top2[..., 1]


def uald(probabilities, evolution_scale):
    mature = probabilities[-1]
    premature = probabilities[:-1]
    mean = (premature + mature.unsqueeze(0)) / 2
    jsd = 0.5 * (
        (premature * (premature.clamp_min(1e-30).log() - mean.clamp_min(1e-30).log())).sum(-1)
        + (mature.unsqueeze(0) * (mature.unsqueeze(0).clamp_min(1e-30).log() - mean.clamp_min(1e-30).log())).sum(-1)
    )
    chosen_layers = jsd.argmax(0)
    chosen = torch.stack([premature[chosen_layers[i], i] for i in range(mature.shape[0])])
    adjusted = mature.clamp_min(1e-30).log() + evolution_scale * chosen.clamp_min(1e-30).log()
    return adjusted.softmax(-1), chosen_layers + 1


def run(directory, tokenizer, texts, bits=None, evolution_scale=10.0):
    from transformers import AutoModelForCausalLM

    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32
    ).eval()
    layers = elements = 0
    if bits is not None:
        with torch.no_grad():
            for name, module in model.named_modules():
                if isinstance(module, torch.nn.Linear) and name != "lm_head":
                    quant_weight_(module.weight, bits)
                    layers += 1
                    elements += module.weight.numel()
    rendered = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": PROMPT.format(question=q)}],
            tokenize=False,
            add_generation_prompt=True,
        )
        for q in texts
    ]
    batch = tokenizer(rendered, return_tensors="pt", padding=True)
    with torch.inference_mode():
        output = model(**batch, use_cache=False, output_hidden_states=True, return_dict=True)
    with torch.inference_mode():
        logits = option_logits(model, output.hidden_states, option_token_sets(tokenizer))
        probabilities = logits.softmax(-1)
        entropy, gap = entropy_gap(probabilities)
        adjusted, premature_layers = uald(probabilities, evolution_scale)
    mature_choice = probabilities[-1].argmax(-1)
    uald_choice = adjusted.argmax(-1)
    one = {k: value[:1] for k, value in batch.items()}
    with torch.inference_mode():
        generated = model.generate(**one, max_new_tokens=1, do_sample=False, use_cache=True)
    label = "FP32" if bits is None else f"W{bits}_RTN_PROXY"
    midpoint = probabilities.shape[0] // 2
    print(
        f"{label} layers={layers} elements={elements} questions={len(texts)} "
        f"entropy_first_mid_last={entropy[0].mean().item():.6f}/{entropy[midpoint].mean().item():.6f}/{entropy[-1].mean().item():.6f} "
        f"gap_first_mid_last={gap[0].mean().item():.6f}/{gap[midpoint].mean().item():.6f}/{gap[-1].mean().item():.6f}"
    )
    print(
        f"{label} mature_choices={''.join('ABCDEFG'[x] for x in mature_choice.tolist())} "
        f"uald_lambda={evolution_scale:g} uald_choices={''.join('ABCDEFG'[x] for x in uald_choice.tolist())} "
        f"premature_layers={premature_layers.tolist()} generated={tokenizer.decode(generated[0,one['input_ids'].shape[1]:])!r}"
    )
    assert torch.isfinite(probabilities).all()
    del model, output
    gc.collect()
    return probabilities, mature_choice, uald_choice, layers, elements


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--questions", type=int, default=4, choices=range(1, len(QUESTIONS) + 1))
    p.add_argument("--evolution-scale", type=float, default=10.0)
    args = p.parse_args()
    from transformers import AutoTokenizer

    directory = model_dir(args.model_dir)
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    texts = QUESTIONS[: args.questions]
    _, base_choice, _, _, _ = run(directory, tokenizer, texts, None, args.evolution_scale)
    for bits in (4, 2):
        _, choice, _, layers, elements = run(directory, tokenizer, texts, bits, args.evolution_scale)
        agreement = (choice == base_choice).float().mean().item()
        print(f"W{bits}_choice_agreement_with_fp32={agreement:.6f}")
        assert layers == 196 and elements == 440401920


if __name__ == "__main__":
    main()
