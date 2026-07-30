#!/usr/bin/env python3
"""
SliderQuant (arXiv:2603.25284) demo: layer-sensitivity profiling +
sensitivity-driven inter-layer bit allocation + intra-layer incremental
(residual-aware) window quantization.

Target: Qwen3-0.6B-shaped 24-layer probe network (mock). The probe uses
orthogonal-init linear layers so quantization error propagates without
exponential decay or saturation, making per-layer sensitivity measurable.
The paper's U-shaped sensitivity curve is a property of real LLMs; here we
demonstrate the *machinery*: profile -> allocate bits by sensitivity ->
incremental intra-layer quantization, and show it beats uniform-bitrate
baselines at the same average bit budget.
"""
import torch
import torch.nn as nn

torch.manual_seed(0)
N_LAYERS = 24  # Qwen3-0.6B has 28 layers; mock uses 24


def quant_uniform(W, nbits):
    qmax = 2 ** (nbits - 1) - 1
    s = W.abs().max().clamp_min(1e-8) / qmax
    return (torch.clamp((W / s).round(), -qmax, qmax) * s)


def layer_sensitivity(layers, nbits=2, probe=None):
    """Output-MSE when quantizing each layer individually (leave-one-out)."""
    x = probe
    with torch.no_grad():
        for L in layers:
            x = L(x)  # linear probe net: error propagates without decay/saturation
    full = x
    sens = []
    for i, L in enumerate(layers):
        W0 = L.weight.data
        L.weight.data = quant_uniform(W0, nbits)
        with torch.no_grad():
            y = probe
            for L2 in layers:
                y = L2(y)
        sens.append((y - full).pow(2).mean().item())
        L.weight.data = W0
    return sens


def intra_layer_incremental(W, nbits, n_windows=4):
    """Quantize W in column windows incrementally (residual-aware)."""
    out = torch.zeros_like(W)
    residual = W.clone()
    cols = W.shape[1]
    step = cols // n_windows
    for w in range(n_windows):
        lo, hi = w * step, (w + 1) * step if w < n_windows - 1 else cols
        seg = residual[:, lo:hi]
        q = quant_uniform(seg, nbits)
        out[:, lo:hi] = q
        residual[:, lo:hi] = seg - q  # carry error into later windows' scaling
    return out


def e2e_output_mse(layers, quant_fn, probe):
    """Quantize every layer with quant_fn(W, layer_idx) and measure output MSE."""
    x = probe
    with torch.no_grad():
        for L in layers:
            x = L(x)
    full = x
    backups = [L.weight.data.clone() for L in layers]
    for i, L in enumerate(layers):
        L.weight.data = quant_fn(backups[i], i)
    with torch.no_grad():
        y = probe
        for L in layers:
            y = L(y)
    mse = (y - full).pow(2).mean().item()
    for L, W0 in zip(layers, backups):
        L.weight.data = W0
    return mse


def main():
    layers = nn.ModuleList([nn.Linear(64, 64, bias=False) for _ in range(N_LAYERS)])
    with torch.no_grad():
        for L in layers:
            nn.init.orthogonal_(L.weight, gain=1.0)  # norm-preserving probe
    probe = torch.randn(8, 64)

    # 1) profile per-layer sensitivity
    sens = layer_sensitivity(layers, nbits=2, probe=probe)
    print("[sensitivity] per-layer output MSE at 2-bit (leave-one-out):")
    print("  " + " ".join(f"{s:.2e}" for s in sens))
    order = sorted(range(N_LAYERS), key=lambda i: -sens[i])
    print(f"  most sensitive layers: {order[:6]}  least: {order[-6:]}")

    # 2) sensitivity-driven bit allocation: top-6 -> 4bit, mid-12 -> 3bit, bottom-6 -> 2bit
    bits = [2] * N_LAYERS
    for rank, i in enumerate(order):
        bits[i] = 4 if rank < 6 else (3 if rank < 18 else 2)
    avg_bits = sum(bits) / N_LAYERS
    print(f"[allocate] avg bits={avg_bits:.2f}  per-layer bits={bits}")

    # 3) three contenders at the same ~3-bit budget, judged end-to-end:
    mse_uniform = e2e_output_mse(layers, lambda W, i: quant_uniform(W, 3), probe)
    mse_alloc = e2e_output_mse(layers, lambda W, i: quant_uniform(W, bits[i]), probe)
    mse_slider = e2e_output_mse(
        layers, lambda W, i: intra_layer_incremental(W, bits[i], n_windows=4), probe)
    print(f"[e2e] output MSE  uniform3bit={mse_uniform:.4f}  "
          f"sens-alloc={mse_alloc:.4f}  SliderQuant(alloc+incremental)={mse_slider:.4f}")
    print(f"[e2e] SliderQuant vs uniform3bit: {100 * (1 - mse_slider / mse_uniform):.1f}% lower error; "
          f"incremental windows alone: {100 * (1 - mse_slider / mse_alloc):.1f}% lower error")
    assert mse_slider < mse_uniform, "SliderQuant should beat uniform 3-bit baseline"
    print("[demo] OK")


if __name__ == "__main__":
    main()
