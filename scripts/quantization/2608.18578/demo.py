#!/usr/bin/env python3
"""Portable Qwen3 reproduction of the Compress-and-Forget PI evaluation.

The paper uses CUDA bitsandbytes FP16, LLM.int8(), and NF4. This CPU-friendly
reference reproduces the released task generator, chat generation, scoring, and
paired evaluation. Its quantizers are explicitly numerical surrogates: INT8 is
weight-only per-output-channel fake quantization (not LLM.int8 activation
outlier decomposition), while NF4 uses the published codebook/block size and a
linear INT8 approximation of double-quantized statistics. Quantized values are
dequantized into FP32 weights, so no storage or kernel-speed claim is made.
"""

from __future__ import annotations

import argparse
import gc
import json
import platform
import random
import re
import sys
import time
from dataclasses import asdict, dataclass

import torch


NF4 = torch.tensor(
    [
        -1.0, -0.6961928009986877, -0.5250730514526367,
        -0.39491748809814453, -0.28444138169288635,
        -0.18477343022823334, -0.09105003625154495, 0.0,
        0.07958029955625534, 0.16093020141124725,
        0.24611230194568634, 0.33791524171829224,
        0.44070982933044434, 0.5626170039176941,
        0.7229568362236023, 1.0,
    ],
    dtype=torch.float32,
)

SUBJECTS = """
Adam Maria Sam Elena Marcus Priya Noah Ines Diego Yuki Omar Hannah Leo Fatima
Chen Nora Victor Amara Felix Sana
""".split()

MOODS = """
happy sad anxious excited calm angry nervous joyful tired confused proud
frustrated relieved curious bored hopeful irritated content worried cheerful
gloomy restless grateful embarrassed eager lonely surprised peaceful jealous
motivated annoyed sleepy optimistic disappointed amused nostalgic grumpy
playful shy confident insecure energetic exhausted hesitant brave timid cautious
carefree stressed relaxed impatient patient determined uncertain satisfied
regretful hurt thrilled terrified delighted puzzled hostile friendly distracted
focused overwhelmed inspired numb vulnerable guilty hopeless wistful serene
tense giddy melancholy spiteful affectionate indifferent suspicious trusting
resentful empowered helpless amazed startled
""".split()

COLORS = """
red blue green yellow purple orange pink teal maroon navy gold silver turquoise
crimson indigo beige lavender olive coral charcoal amber ivory magenta mint rust
azure emerald ruby cyan khaki taupe ochre sienna fuchsia burgundy scarlet cobalt
sapphire jade lilac peach salmon mustard plum rose bronze copper pewter slate
cream tan brown black white gray grey violet cerise denim flax honey walnut
chestnut clay sand moss forest sky wine berry cherry lime lemon apricot grape
""".split()

ANIMALS = """
lion tiger bear wolf fox deer rabbit squirrel otter beaver raccoon badger
hedgehog mole mouse rat hamster ferret weasel skunk sloth koala kangaroo panda
elephant giraffe zebra hippo rhino camel llama horse donkey cow bull pig sheep
goat chicken duck goose turkey swan peacock ostrich penguin eagle hawk falcon owl
crow raven sparrow robin cardinal pigeon parrot toucan flamingo pelican heron
stork dolphin whale shark octopus squid crab lobster shrimp jellyfish starfish
turtle tortoise lizard gecko iguana chameleon snake cobra python crocodile
alligator frog toad bee wasp ant beetle butterfly moth dragonfly cricket spider
scorpion snail worm goldfish salmon trout eel
""".split()

OCCUPATIONS = """
doctor teacher lawyer engineer nurse dentist pilot chef baker farmer plumber
electrician mechanic carpenter painter architect accountant banker journalist
photographer musician actor dancer writer poet scientist professor librarian
translator therapist psychologist surgeon paramedic firefighter soldier sailor
astronaut athlete coach referee tailor florist butcher waiter bartender barista
consultant analyst developer designer editor publisher curator historian biologist
chemist physicist geologist economist linguist zoologist botanist astronomer
cardiologist neurologist radiologist optometrist chiropractor nutritionist welder
surveyor cartoonist sculptor composer conductor
""".split()

WORD_CATEGORIES = {
    "mood": {
        "template": "{subj}'s mood is now {val}.",
        "question": (
            "Based only on the most recent update above, what is {subj}'s mood "
            "right now? Reply with a single word and nothing else."
        ),
        "candidates": MOODS,
    },
    "favorite_color": {
        "template": "{subj}'s favorite color is now {val}.",
        "question": (
            "Based only on the most recent update above, what is {subj}'s "
            "favorite color right now? Reply with a single word and nothing else."
        ),
        "candidates": COLORS,
    },
    "favorite_animal": {
        "template": "{subj}'s favorite animal is now the {val}.",
        "question": (
            "Based only on the most recent update above, what is {subj}'s "
            "favorite animal right now? Reply with a single word and nothing else."
        ),
        "candidates": ANIMALS,
    },
    "occupation": {
        "template": "{subj}'s job is now {val}.",
        "question": (
            "Based only on the most recent update above, what is {subj}'s job "
            "right now? Reply with a single word and nothing else."
        ),
        "candidates": OCCUPATIONS,
    },
}

NUMERIC_CATEGORIES = {
    "temperature": {
        "template": "The temperature reading for {subj}'s greenhouse is now {val} degrees.",
        "question": (
            "Based only on the most recent update above, what is the temperature "
            "reading right now? Reply with only the number and nothing else."
        ),
        "pool": [str(n) for n in range(10, 999)],
    },
    "stock_price": {
        "template": "{subj}'s tracked stock price is now ${val}.",
        "question": (
            "Based only on the most recent update above, what is the tracked stock "
            "price right now? Reply with only the number (no $ sign) and nothing else."
        ),
        "pool": [str(n) for n in range(5, 999)],
    },
    "page_count": {
        "template": "The page count for {subj}'s document is now {val} pages.",
        "question": (
            "Based only on the most recent update above, what is the document's page "
            "count right now? Reply with only the number and nothing else."
        ),
        "pool": [str(n) for n in range(3, 999)],
    },
}

ALL_CATEGORIES = {**WORD_CATEGORIES, **NUMERIC_CATEGORIES}
PAPER_TRIALS = {1: 15, 2: 15, 4: 20, 8: 25, 16: 60, 32: 50, 64: 60, 96: 60}


@dataclass
class Trial:
    attribute: str
    kind: str
    level: int
    trial_index: int
    subject: str
    prompt: str
    gold: str
    old_values: list[str]


@dataclass
class Result:
    mode: str
    attribute: str
    kind: str
    level: int
    trials: int
    accuracy: float
    intrusion_rate: float


def fake_int8(weight: torch.Tensor) -> torch.Tensor:
    """Symmetric per-output-channel W8 surrogate, returned dequantized."""
    if weight.ndim != 2:
        raise ValueError("INT8 reference expects a matrix")
    scale = weight.float().abs().amax(dim=1, keepdim=True).clamp_min(1e-12) / 127.0
    return (weight.float() / scale).round().clamp(-127, 127) * scale


def _double_quant_scales(scales: torch.Tensor, block_size: int = 256) -> torch.Tensor:
    """Linear INT8 engineering approximation of NF4 compressed statistics."""
    result = torch.empty_like(scales)
    offset = scales.mean()
    centered = scales - offset
    for start in range(0, scales.numel(), block_size):
        stop = min(start + block_size, scales.numel())
        block = centered[start:stop]
        quant_scale = block.abs().max().clamp_min(1e-12) / 127.0
        result[start:stop] = (block / quant_scale).round().clamp(-127, 127) * quant_scale + offset
    return result.clamp_min(1e-12)


def fake_nf4(weight: torch.Tensor, block_size: int = 64) -> torch.Tensor:
    """Block-64 NF4 surrogate with double-quantized scales, returned dequantized."""
    if weight.ndim != 2:
        raise ValueError("NF4 reference expects a matrix")
    flat = weight.float().reshape(-1)
    padding = (-flat.numel()) % block_size
    padded = torch.nn.functional.pad(flat, (0, padding)) if padding else flat
    blocks = padded.reshape(-1, block_size)
    scales = _double_quant_scales(blocks.abs().amax(dim=1).clamp_min(1e-12))
    boundaries = ((NF4[:-1] + NF4[1:]) * 0.5).to(blocks.device)
    output = torch.empty_like(blocks)
    for start in range(0, blocks.shape[0], 4096):
        stop = min(start + 4096, blocks.shape[0])
        normalized = (blocks[start:stop] / scales[start:stop, None]).clamp(-1, 1)
        codes = torch.bucketize(normalized.contiguous(), boundaries)
        output[start:stop] = NF4.to(blocks.device)[codes] * scales[start:stop, None]
    return output.reshape(-1)[: flat.numel()].reshape_as(weight)


def quantize_backbone_in_place(model: torch.nn.Module, mode: str) -> tuple[int, int, float]:
    """Quantize backbone Linear matrices; preserve the paper's default FP lm_head."""
    if mode == "fp32":
        return 0, 0, 0.0
    quantizer = fake_int8 if mode == "int8" else fake_nf4
    layers = elements = 0
    absolute_error = 0.0
    with torch.no_grad():
        for name, module in model.named_modules():
            if not isinstance(module, torch.nn.Linear) or name == "lm_head":
                continue
            original = module.weight.data
            quantized = quantizer(original)
            absolute_error += float((original.float() - quantized).abs().sum().item())
            elements += original.numel()
            module.weight.copy_(quantized.to(module.weight.dtype))
            layers += 1
    return layers, elements, absolute_error / max(elements, 1)


def is_single_token_in_context(tokenizer, template: str, subject: str, word: str) -> bool:
    """Use real character offsets, matching the corrected released implementation."""
    prefix_template, suffix_template = template.split("{val}")
    prefix = prefix_template.format(subj=subject)
    suffix = suffix_template.format(subj=subject)
    text = prefix + word + suffix
    word_start, word_end = len(prefix), len(prefix) + len(word)
    encoding = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    overlaps = [
        1 for start, end in encoding["offset_mapping"]
        if not (end <= word_start or start >= word_end)
    ]
    return len(overlaps) == 1


def build_filtered_vocab(tokenizer) -> dict[str, list[str]]:
    filtered = {}
    for attribute, spec in WORD_CATEGORIES.items():
        unique_candidates = list(dict.fromkeys(spec["candidates"]))
        filtered[attribute] = [
            word for word in unique_candidates
            if is_single_token_in_context(tokenizer, spec["template"], "Sam", word)
        ]
        print(
            f"vocab attribute={attribute} kept={len(filtered[attribute])} "
            f"total={len(unique_candidates)}",
            flush=True,
        )
    return filtered


def build_trials(
    attributes: list[str],
    levels: list[int],
    trials_override: int | None,
    seed: int,
    filtered_word_pools: dict[str, list[str]],
) -> list[Trial]:
    """Build trials once so every precision receives byte-identical prompts."""
    rng = random.Random(seed)
    trials = []
    for attribute in attributes:
        spec = ALL_CATEGORIES[attribute]
        kind = "word" if attribute in WORD_CATEGORIES else "numeric"
        pool = filtered_word_pools[attribute] if kind == "word" else spec["pool"]
        for level in levels:
            if level > len(pool):
                print(f"skip attribute={attribute} level={level} pool_size={len(pool)}", flush=True)
                continue
            count = trials_override if trials_override is not None else PAPER_TRIALS[level]
            for trial_index in range(count):
                subject = rng.choice(SUBJECTS)
                values = rng.sample(pool, level)
                updates = [spec["template"].format(subj=subject, val=value) for value in values]
                question = spec["question"].format(subj=subject)
                trials.append(
                    Trial(
                        attribute=attribute,
                        kind=kind,
                        level=level,
                        trial_index=trial_index,
                        subject=subject,
                        prompt="\n".join(updates) + "\n\n" + question,
                        gold=values[-1],
                        old_values=values[:-1],
                    )
                )
    return trials


def score_response(response: str, gold: str, kind: str) -> tuple[bool, str | None]:
    cleaned = response.strip().lower().strip(".").strip()
    pattern = r"-?\d+" if kind == "numeric" else r"[a-zA-Z]+"
    match = re.search(pattern, cleaned)
    extracted = match.group(0) if match else None
    return extracted == gold.lower(), extracted


def encode_chat_batch(tokenizer, prompts: list[str]):
    rendered = []
    for prompt in prompts:
        messages = [{"role": "user", "content": prompt}]
        rendered.append(
            tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        )
    return tokenizer(rendered, return_tensors="pt", padding=True)


@torch.inference_mode()
def generate_batch(model, tokenizer, prompts: list[str], max_new_tokens: int) -> list[str]:
    encoded = encode_chat_batch(tokenizer, prompts)
    input_length = encoded["input_ids"].shape[1]
    generated = model.generate(
        **encoded,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=None,
        top_p=None,
        top_k=None,
        use_cache=True,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.batch_decode(generated[:, input_length:], skip_special_tokens=True)


def evaluate(model, tokenizer, trials: list[Trial], batch_size: int, max_new_tokens: int):
    counters: dict[tuple[str, str, int], list[int]] = {}
    raw_examples = []
    for start in range(0, len(trials), batch_size):
        batch = trials[start : start + batch_size]
        responses = generate_batch(model, tokenizer, [trial.prompt for trial in batch], max_new_tokens)
        for trial, response in zip(batch, responses):
            correct, extracted = score_response(response, trial.gold, trial.kind)
            key = (trial.attribute, trial.kind, trial.level)
            count, hits, intrusions = counters.setdefault(key, [0, 0, 0])
            counters[key] = [
                count + 1,
                hits + int(correct),
                intrusions + int(not correct and extracted in {v.lower() for v in trial.old_values}),
            ]
            if len(raw_examples) < 5:
                raw_examples.append(
                    {"attribute": trial.attribute, "level": trial.level, "gold": trial.gold,
                     "response": response.strip(), "extracted": extracted, "correct": correct}
                )
    rows = []
    for (attribute, kind, level), (count, hits, intrusions) in sorted(counters.items()):
        rows.append(
            Result(
                mode="", attribute=attribute, kind=kind, level=level, trials=count,
                accuracy=hits / count, intrusion_rate=intrusions / count,
            )
        )
    return rows, raw_examples


def self_test() -> None:
    weight = torch.linspace(-3, 3, 5 * 131).reshape(5, 131)
    int8 = fake_int8(weight)
    nf4 = fake_nf4(weight)
    assert int8.shape == weight.shape and nf4.shape == weight.shape
    assert torch.isfinite(int8).all() and torch.isfinite(nf4).all()
    assert float((weight - int8).abs().mean()) < 0.02
    assert float((weight - nf4).abs().mean()) < 0.25
    assert score_response(" Blue. ", "blue", "word") == (True, "blue")
    assert score_response("The answer is 317.", "317", "numeric") == (True, "317")
    print("self_test=PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--modes", default="fp32,int8,nf4")
    parser.add_argument("--levels", default="1,2,4,8")
    parser.add_argument(
        "--attributes", default=",".join(ALL_CATEGORIES),
        help="Comma-separated subset of the four word and three numeric attributes.",
    )
    parser.add_argument(
        "--trials", type=int, default=2,
        help="Trials per attribute/level. Use 0 for the paper's level-dependent budget.",
    )
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    modes = [value.strip() for value in args.modes.split(",") if value.strip()]
    if any(mode not in {"fp32", "int8", "nf4"} for mode in modes):
        raise ValueError(f"unsupported modes: {modes}")
    levels = [int(value) for value in args.levels.split(",")]
    if any(level not in PAPER_TRIALS for level in levels):
        raise ValueError(f"levels must be selected from {sorted(PAPER_TRIALS)}")
    attributes = [value.strip() for value in args.attributes.split(",") if value.strip()]
    unknown = set(attributes) - set(ALL_CATEGORIES)
    if unknown:
        raise ValueError(f"unknown attributes: {sorted(unknown)}")
    if args.trials < 0 or args.batch_size < 1 or args.max_new_tokens < 1:
        raise ValueError("trials must be >= 0; batch size and max tokens must be positive")

    from transformers import AutoModelForCausalLM, AutoTokenizer, __version__ as transformers_version

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    filtered_word_pools = build_filtered_vocab(tokenizer)
    paired_trials = build_trials(
        attributes, levels, None if args.trials == 0 else args.trials, args.seed,
        filtered_word_pools,
    )
    if not paired_trials:
        raise RuntimeError("no trials were generated")

    environment = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "torch": torch.__version__,
        "transformers": transformers_version,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": bool(hasattr(torch.backends, "mps") and torch.backends.mps.is_available()),
        "model": args.model,
        "parameters": None,
        "paired_trials": len(paired_trials),
    }
    print("environment=" + json.dumps(environment, sort_keys=True), flush=True)

    all_results = []
    for mode in modes:
        started = time.perf_counter()
        model = AutoModelForCausalLM.from_pretrained(
            args.model, local_files_only=True, dtype=torch.float32, low_cpu_mem_usage=True
        ).eval()
        parameters = sum(parameter.numel() for parameter in model.parameters())
        environment["parameters"] = parameters
        layers, elements, mae = quantize_backbone_in_place(model, mode)
        rows, examples = evaluate(
            model, tokenizer, paired_trials, args.batch_size, args.max_new_tokens
        )
        for row in rows:
            row.mode = mode
            all_results.append(row)
        elapsed = time.perf_counter() - started
        print(
            f"mode={mode} parameters={parameters:,} quantized_layers={layers} "
            f"quantized_elements={elements:,} weight_mae={mae:.8f} "
            f"elapsed_seconds={elapsed:.2f} examples={json.dumps(examples)}",
            flush=True,
        )
        del model
        gc.collect()

    if args.compact:
        print("mode,attribute,kind,level,trials,accuracy,intrusion_rate")
        for row in all_results:
            print(
                f"{row.mode},{row.attribute},{row.kind},{row.level},{row.trials},"
                f"{row.accuracy:.6f},{row.intrusion_rate:.6f}"
            )
    else:
        print(json.dumps([asdict(row) for row in all_results], indent=2))


if __name__ == "__main__":
    main()
