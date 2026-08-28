#!/usr/bin/env python3
"""Ankhdjet-style Qwen3-0.6B ternary IR and mask-program reference."""
import argparse
import glob
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import torch


def model_dir(arg=None):
    if arg:
        return arg
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*"))
    hits = [p for p in hits if os.path.exists(os.path.join(p, "config.json"))]
    if not hits:
        raise FileNotFoundError("Pass --model-dir for a local Qwen3-0.6B snapshot")
    return hits[0]


def absmean_ternarize(weight):
    """Explicit b1.58 QAT-master transform; never silently applied."""
    x = weight.detach().float()
    scale = x.abs().mean().clamp_min(1e-12)
    return (x / scale).round().clamp(-1, 1).to(torch.int8), scale


def _wmat_bytes(chunk):
    table = {-1: "-", 0: "0", 1: "+"}
    return ("\n".join("".join(table[int(v)] for v in row) for row in chunk.tolist())
            + "\n").encode("ascii")


def _parse_wmat(data):
    table = {45: -1, 48: 0, 43: 1}
    return torch.tensor([[table[c] for c in line]
                         for line in data.splitlines() if line], dtype=torch.int8)


def emit_mask_grid(q_out_in, out_dir, macro_rows=64, macro_cols=256):
    """Emit upstream-compatible W[input, output] +/-/0 mask chunks."""
    w = q_out_in.t().contiguous().cpu()
    rows, cols = w.shape
    grid_r, grid_c = math.ceil(rows / macro_rows), math.ceil(cols / macro_cols)
    layer_dir = Path(out_dir) / "model.layers.0.self_attn.q_proj"
    layer_dir.mkdir(parents=True, exist_ok=True)
    digests = {}
    restored = torch.zeros(grid_r * macro_rows, grid_c * macro_cols,
                           dtype=torch.int8)
    total_bytes = 0
    for i in range(grid_r):
        for j in range(grid_c):
            chunk = torch.zeros(macro_rows, macro_cols, dtype=torch.int8)
            r0, c0 = i * macro_rows, j * macro_cols
            rr, cc = min(macro_rows, rows-r0), min(macro_cols, cols-c0)
            chunk[:rr, :cc] = w[r0:r0+rr, c0:c0+cc]
            data = _wmat_bytes(chunk)
            path = layer_dir / f"r{i}_c{j}.wmat"
            path.write_bytes(data)
            readback = _parse_wmat(path.read_bytes())
            assert torch.equal(readback, chunk)
            restored[r0:r0+macro_rows, c0:c0+macro_cols] = readback
            digests[f"r{i}_c{j}"] = hashlib.sha256(data).hexdigest()[:16]
            total_bytes += len(data)
    assert torch.equal(restored[:rows, :cols], w)
    assert not torch.count_nonzero(restored[rows:, :])
    assert not torch.count_nonzero(restored[:, cols:])
    manifest = {
        "layer": "model.layers.0.self_attn.q_proj", "rows": rows, "cols": cols,
        "macro_rows": macro_rows, "macro_cols": macro_cols,
        "grid_r": grid_r, "grid_c": grid_c, "n_macros": grid_r * grid_c,
        "weights": rows * cols,
        "padded_positions": restored.numel() - rows * cols,
        "wmat_bytes": total_bytes, "chunks_sha256_16": digests,
    }
    (layer_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest, w


def nor_bitserial_mvm(w_in_out, activation, bits=8, subcol_rows=64):
    """Paper/upstream row-sequential one-hot, bit-serial NOR-array oracle."""
    acc = torch.zeros(w_in_out.shape[1], dtype=torch.int64)
    for start in range(0, w_in_out.shape[0], subcol_rows):
        for r in range(start, min(start + subcol_rows, w_in_out.shape[0])):
            row = w_in_out[r].to(torch.int64)
            for bit in range(bits):
                if (int(activation[r]) >> bit) & 1:
                    acc += row << bit
    return acc


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir")
    p.add_argument("--output-dir", help="persist q_proj .wmat chunks and manifest")
    p.add_argument("--macro-rows", type=int, default=64)
    p.add_argument("--macro-cols", type=int, default=256)
    p.add_argument("--no-full-model", action="store_true",
                   help="skip full-transformer fake-quant forward/generation")
    args = p.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    directory = model_dir(args.model_dir)
    tok = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, dtype=torch.float32).eval()
    prompt = "掩膜可编程三值计算需要逐级验证。"
    inputs = tok(prompt, return_tensors="pt")
    with torch.inference_mode():
        reference_logits = model(**inputs).logits.detach().float()

    name, module = next((n, m) for n, m in model.named_modules()
                        if isinstance(m, torch.nn.Linear) and n.endswith("q_proj"))
    q, scale = absmean_ternarize(module.weight)
    tmp = None
    if args.output_dir:
        output_dir = args.output_dir
    else:
        tmp = tempfile.TemporaryDirectory(prefix="ankhdjet_masks_")
        output_dir = tmp.name
    manifest, w_in_out = emit_mask_grid(
        q, output_dir, args.macro_rows, args.macro_cols)
    generator = torch.Generator().manual_seed(260826206)
    activation = torch.randint(0, 256, (w_in_out.shape[0],), generator=generator,
                               dtype=torch.uint8)
    oracle = nor_bitserial_mvm(w_in_out, activation)
    dense = w_in_out.to(torch.int64).t() @ activation.to(torch.int64)
    assert torch.equal(oracle, dense)

    linear_count = weight_count = 0
    if not args.no_full_model:
        with torch.no_grad():
            for n, m in model.named_modules():
                if not isinstance(m, torch.nn.Linear) or n == "lm_head":
                    continue
                tq, ts = absmean_ternarize(m.weight)
                m.weight.copy_(tq.to(m.weight.dtype) * ts.to(m.weight.dtype))
                linear_count += 1
                weight_count += tq.numel()
        with torch.inference_mode():
            quant_logits = model(**inputs).logits.detach().float()
            generated = model.generate(**inputs, max_new_tokens=1, do_sample=False,
                                       use_cache=False)
        assert torch.isfinite(quant_logits).all()
        logits_mae = (reference_logits - quant_logits).abs().mean().item()
        generated_text = tok.decode(generated[0], skip_special_tokens=True)
    else:
        logits_mae = None
        generated_text = None

    result = {
        "model": "Qwen3-0.6B", "source_checkpoint_storage": "FP32/BF16 non-ternary",
        "conversion": "explicit absmean QAT-master engineering transform",
        "compiled_tensor": name + ".weight", "tensor_shape_out_in": list(q.shape),
        "ternary_scale": scale.item(), "zero_fraction": (q == 0).float().mean().item(),
        "mask_encoding": "+/-/0 .wmat; W[input,output]",
        "macro_grid": manifest, "mask_roundtrip_exact": True,
        "nor_bitserial_mvm_exact": bool(torch.equal(oracle, dense)),
        "mask_output_persisted": bool(args.output_dir),
        "full_model": {"transformer_linears": linear_count, "weights": weight_count,
                       "lm_head_off_fabric": True, "finite_logits": logits_mae is not None,
                       "logits_mae": logits_mae, "one_token_generation": generated_text},
        "silicon_flow_executed": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert set(q.unique().tolist()) <= {-1, 0, 1}
    if tmp:
        tmp.cleanup()


if __name__ == "__main__":
    main()
