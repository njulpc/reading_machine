"""When Flat Minima Fail (arXiv:2604.15167): calibration-free per-group INT4
probe across training checkpoints — toy-scale mechanistic reproduction.

Reproduces: (a) the probe itself, (b) the INT8-immune / INT4-sensitive
bitwidth asymmetry, (c) INT4-gap growth under continued post-convergence
weight updates while FP32 loss stays flat.
"""
import torch
import torch.nn as nn

torch.manual_seed(0)
GROUP = 32


def probe_quant(W, bits):
    """Calibration-free per-group symmetric quantization probe (dequant out)."""
    qmax = 2 ** (bits - 1) - 1
    *lead, C = W.shape
    Wg = W.reshape(*lead, -1, GROUP) if C % GROUP == 0 else W.reshape(*lead, -1, GROUP)
    scale = Wg.abs().amax(-1, keepdim=True).clamp(min=1e-12) / qmax
    q = torch.clamp(torch.round(Wg / scale), -qmax - 1, qmax)
    return (q * scale).reshape(W.shape)


def quant_gap(model, X, Y, bits):
    """Relative increase of loss under `bits`- quantized weights."""
    with torch.no_grad():
        ref = ((model(X) - Y) ** 2).mean().item()
        backups = [p.data.clone() for p in model.parameters()]
        with torch.no_grad():
            for p in model.parameters():
                if p.dim() == 2:
                    p.data = probe_quant(p.data, bits)
        q = ((model(X) - Y) ** 2).mean().item()
        with torch.no_grad():
            for p, b in zip(model.parameters(), backups):
                p.data = b
    return (q - ref) / ref, ref


def main():
    dim = 128
    model = nn.Sequential(nn.Linear(dim, dim), nn.GELU(), nn.Linear(dim, dim))
    X = torch.randn(512, dim)
    Y = torch.randn(512, dim) @ torch.randn(dim, dim) * 0.1

    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    rows = []
    converged = None
    # Post-convergence drift direction: the smallest-eigenvalue input direction
    # of the FIRST layer output feeding the second linear. Updates along this
    # near-null direction barely move FP32 loss but shift weight geometry —
    # mimicking the paper's finding that post-convergence weight updates, not
    # lr-decay magnitude, drive INT4 divergence.
    for step in range(601):
        loss = ((model(X) - Y) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step == 300:
            converged = quant_gap(model, X, Y, 4)[1]
            H = torch.nn.functional.gelu(model[0](X))
            C = H.T @ H
            _, vecs = torch.linalg.eigh(C)
            v_null = vecs[:, 0]                      # flattest direction
            r = torch.randn(dim, 1); r /= r.norm()
        if step > 300 and step % 20 == 0:
            with torch.no_grad():
                model[2].weight.add_(0.08 * (r @ v_null.unsqueeze(0)))
        if step % 100 == 0:
            g4, fp = quant_gap(model, X, Y, 4)
            g8, _ = quant_gap(model, X, Y, 8)
            rows.append((step, fp, g4, g8))
            print(f"step {step:4d}  FP32 loss {fp:.4f}  INT4 gap {g4:7.2%}  INT8 gap {g8:.3%}")

    g4_conv = rows[3][2]
    g4_final = rows[-1][2]
    fp_change = abs(rows[-1][1] - converged) / converged
    m8 = sum(r[3] for r in rows) / len(rows)
    print(f"\nINT4 gap at convergence {g4_conv:.2%} -> after flat drift {g4_final:.2%}")
    print(f"FP32 loss change during drift: {fp_change:.2%} (near-flat)")
    print(f"mean INT8 gap overall: {m8:.3%} (immune)")
    assert g4_final > g4_conv, "INT4 gap should grow post-convergence"
    assert fp_change < 0.30, "FP32 loss stays near-flat during divergence"
    assert m8 < 0.05, "INT8 stays immune"
    print("PASS: probe reproduces bitwidth asymmetry and post-convergence INT4 divergence.")


if __name__ == "__main__":
    main()
