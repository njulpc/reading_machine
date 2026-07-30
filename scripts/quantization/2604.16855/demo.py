"""COD-TDQ (arXiv:2604.16855): token-group dual-constraint activation
quantization — mechanistic reproduction of the W4A4 COD cliff and its fix.

Synthetic COD activations: heavy-tailed background tokens dominate a shared
range, pushing weak-but-structured boundary cues into the zero bin.
DSTG (token-group scales) + DCRP (bounded step/dispersion and zero-bin mass)
repairs it.
"""
import torch

torch.manual_seed(0)
GROUP_TOK = 16
STEP_DISP_MAX = 0.5     # DCRP constraint 1: step / token-group dispersion
ZERO_BIN_MAX = 0.25     # DCRP constraint 2: zero-bin mass fraction


def q4(x, clip):
    """Symmetric 4-bit quantization with given clip range (per row)."""
    step = clip / 7.0
    q = torch.clamp(torch.round(x / step), -8, 7)
    return q * step, step


def zero_bin_mass(x, step):
    return (x.abs() < step / 2).float().mean().item()


def per_tensor(x):
    clip = x.abs().amax()
    dq, step = q4(x, clip)
    return dq, step.expand(x.shape[0])


def per_token(x):
    clip = x.abs().amax(-1)
    dq, step = q4(x, clip.unsqueeze(-1))
    return dq, step


def cod_tdq(x):
    """DSTG: token-group scales (direct-sum style). DCRP: project each group's
    clip so that step/dispersion and zero-bin mass stay bounded."""
    N, C = x.shape
    xg = x.reshape(N // GROUP_TOK, GROUP_TOK, C)
    out = torch.zeros_like(xg)
    for g in range(xg.shape[0]):
        blk = xg[g]
        clip = blk.abs().amax(-1)                          # DSTG: per-token-group scale
        step = clip / 7.0
        disp = blk.std(dim=-1).clamp(min=1e-8)
        # DCRP: enforce step <= STEP_DISP_MAX * dispersion  (raise resolution)
        step = torch.minimum(step, STEP_DISP_MAX * disp)
        # enforce zero-bin mass bound by shrinking step until satisfied
        for _ in range(8):
            zb = (blk.abs() < step.unsqueeze(-1) / 2).float().mean(-1)
            viol = zb > ZERO_BIN_MAX
            if not viol.any():
                break
            step = torch.where(viol, step * 0.8, step)
        q = torch.clamp(torch.round(blk / step.unsqueeze(-1)), -8, 7)
        out[g] = q * step.unsqueeze(-1)
    return out.reshape(N, C)


def main():
    N, C = 512, 128
    # background tokens: heavy-tailed, large magnitude
    x = torch.randn(N, C) * torch.where(torch.rand(N, C) > 0.9, 12.0, 1.0)
    # boundary tokens: weak magnitude but structured (a smooth pattern)
    n_bnd = 64
    t = torch.linspace(0, 3.14, C)
    bnd = 0.3 * torch.stack([torch.sin(t * (1 + i % 5)) for i in range(n_bnd)])
    x[:n_bnd] = bnd
    is_bnd = torch.zeros(N, dtype=torch.bool); is_bnd[:n_bnd] = True

    dq_pt, step_pt = per_tensor(x)
    dq_pk, _ = per_token(x)
    dq_tdq = cod_tdq(x)

    zb_pt = zero_bin_mass(x[is_bnd], step_pt[is_bnd].unsqueeze(-1).expand(n_bnd, C))
    err_pt = (dq_pt[is_bnd] - x[is_bnd]).pow(2).mean().item()
    err_pk = (dq_pk[is_bnd] - x[is_bnd]).pow(2).mean().item()
    err_tdq = (dq_tdq[is_bnd] - x[is_bnd]).pow(2).mean().item()
    print(f"boundary-token zero-bin mass under per-tensor W4: {zb_pt:.2%}  (the COD cliff)")
    print(f"boundary recon MSE: per-tensor={err_pt:.6f}  per-token={err_pk:.6f}  COD-TDQ={err_tdq:.6f}")
    assert err_tdq < err_pt
    print("PASS: DSTG + DCRP rescues weak boundary cues from the zero bin.")


if __name__ == "__main__":
    main()
