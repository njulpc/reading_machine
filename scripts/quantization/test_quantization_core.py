#!/usr/bin/env python3
"""Small-tensor regression checks for the reviewed quantization demos."""
import importlib.util
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent


def load(arxiv_id):
    spec = importlib.util.spec_from_file_location(f"demo_{arxiv_id.replace('.', '_')}", ROOT / arxiv_id / "demo.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def main():
    bitflip = load("2608.15475")
    code, scale = bitflip.quantize_int8(torch.tensor([[-2.0, 0.0, 1.0]]))
    attacked, chosen = bitflip.attack(code, scale, torch.ones_like(scale * code), 2)
    assert code.min() >= -128 and code.max() <= 127 and chosen[:, 0].unique().numel() == chosen.shape[0]
    assert attacked.shape == code.shape

    flash = load("2608.15531")
    dense, sparse, mask = flash.flashquant_parts(torch.arange(16.0).reshape(2, 8) - 4, .25)
    assert mask.sum().item() == 4 and dense.shape == sparse.shape == (2, 8)

    schur = load("2608.15567")
    w = torch.randn(2, 4); x = torch.randn(12, 4); h = x.T @ x / 12 + 1e-2 * torch.eye(4)
    qw = schur.schur_quantize(w, h, 2)
    assert qw.shape == w.shape and torch.isfinite(qw).all()

    flux = load("2608.15602")
    w = torch.randn(3, 8); approx, bases = flux.fit_bases(w, 2, 2); x = torch.randn(2, 8)
    reconstructed = sum(flux.lut_binary_mm(x, signs, row, col) for signs, row, col in bases)
    assert approx.shape == w.shape and torch.allclose(reconstructed, x @ approx.T, atol=1e-5, rtol=1e-5)

    specvla = load("2608.15636")
    qdelta, counts, tz, th = specvla.quantize_residual(torch.randn(4, 8), 4, .25, .25)
    assert qdelta.shape == (4, 8) and sum(counts) == 8 and tz <= th

    nexus = load("2608.16104")
    q = nexus.ste_asym4(torch.randn(4, 8), torch.tensor(.2), torch.tensor(8.0))
    assert q.shape == (4, 8) and torch.isfinite(q).all()

    binrvr = load("2608.16756")
    scale, adjusted = binrvr.ScaleNet(8)(torch.randn(4, 8))
    assert scale.shape == (1, 8) and adjusted.shape == (4, 8) and (scale > 0).all()
    print("small_tensor_quantization_checks=PASS methods=7")


if __name__ == "__main__":
    main()
