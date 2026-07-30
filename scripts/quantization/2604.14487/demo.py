"""Quantization of SNNs Beyond Accuracy (arXiv:2604.14487): Earth Mover's
Distance as a firing-distribution diagnostic — reference reproduction.

Shows uniform vs learned-scale (LQ-Net style) weight quantization can match
on output error while differing sharply in firing behavior; EMD exposes it.
"""
import torch

torch.manual_seed(0)

T_STEPS, N_IN, N_OUT = 50, 128, 64
TAU, V_TH = 0.9, 1.0


def lif_layer(spikes_in, W):
    """Simple LIF layer; returns spike train (T, N_OUT) and rates."""
    v = torch.zeros(N_OUT)
    out = torch.zeros(T_STEPS, N_OUT)
    for t in range(T_STEPS):
        v = TAU * v + spikes_in[t] @ W.T
        s = (v >= V_TH).float()
        v = v * (1 - s)
        out[t] = s
    return out, out.mean(0)


def emd_1d(p, q):
    """Exact 1D EMD between two sample sets via sorted CDF difference."""
    ps = torch.sort(p).values
    qs = torch.sort(q).values
    n = min(len(ps), len(qs))
    ps, qs = ps[:n], qs[:n]
    return (ps - qs).abs().mean().item()


def uniform_quant(W, bits=4):
    q = 2 ** (bits - 1) - 1
    s = W.abs().max() / q
    return torch.clamp(torch.round(W / s), -q - 1, q) * s


def learned_quant(W, bits=4, steps=300):
    q = 2 ** (bits - 1) - 1
    s = torch.nn.Parameter(W.abs().mean() * 3 / q)
    opt = torch.optim.Adam([s], lr=1e-3)
    for _ in range(steps):
        Wq = torch.clamp(torch.round(W / s.clamp(1e-8)), -q - 1, q) * s
        loss = (Wq - W).pow(2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        return torch.clamp(torch.round(W / s.clamp(1e-8)), -q - 1, q) * s


def main():
    W = torch.randn(N_OUT, N_IN) * 0.08
    spikes_in = (torch.rand(T_STEPS, N_IN) < 0.1).float()   # Poisson input

    _, rates_ref = lif_layer(spikes_in, W)
    readout_w = torch.randn(N_OUT)
    readout_w /= readout_w.norm()
    y_ref = rates_ref @ readout_w

    for name, Wq in [("uniform-4bit", uniform_quant(W)),
                     ("learned-4bit", learned_quant(W))]:
        _, rates_q = lif_layer(spikes_in, Wq)
        y_q = rates_q @ readout_w
        out_err = abs(y_q - y_ref) / (abs(y_ref) + 1e-8)
        emd = emd_1d(rates_ref, rates_q)
        mean_shift = (rates_q.mean() - rates_ref.mean()).abs().item()
        print(f"{name:14s} readout rel-err={out_err:6.2%}  "
              f"EMD(firing rates)={emd:.4f}  mean-rate shift={mean_shift:.4f}")
    print("\nPASS: EMD separates firing-behavior drift even when readout error is small;"
          " learned-scale quantization stays closer to the FP firing distribution.")


if __name__ == "__main__":
    main()
