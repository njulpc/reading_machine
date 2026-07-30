"""Paper: M2XFP: A Metadata-Augmented Microscaling Data Format for Efficient
Low-bit Quantization (arXiv:2601.19213)

Core algorithm reproduction: metadata-augmented MXFP4.
  MXFP4: block of 32 elements shares one Power-of-Two (E8M0) scale; elements
  are E2M1 FP4 values {0, +-0.5, +-1, +-1.5, +-2, +-3, +-4, +-6}.
  The 2^k-only scale is a coarse match to the block dynamic range.
  M2XFP adds minimal metadata per block: a 2-bit exponent refinement
  {2^0, 2^-0.25, 2^-0.5, 2^-0.75} multiplying the PoT scale, recovering the
  accuracy lost to the power-of-two constraint (the paper reports ~70%
  accuracy-loss reduction vs MXFP4 on LLM benchmarks).

Validation: real Qwen3-0.6B q_proj weight (HF cache) with mock fallback.
We measure reconstruction MSE: MXFP4 (PoT scale) vs M2XFP (PoT + 2-bit
metadata refinement) and report the error reduction ratio.

Run: python3 demo.py
"""
import glob
import os

import torch

E2M1 = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
REFINE = torch.tensor([1.0, 2 ** -0.25, 2 ** -0.5, 2 ** -0.75])  # 2-bit metadata


def load_weight() -> torch.Tensor:
    try:
        from safetensors import safe_open

        path = glob.glob(
            os.path.expanduser(
                "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
            )
        )[0]
        f = safe_open(path, framework="pt")
        w = f.get_tensor("model.layers.0.self_attn.q_proj.weight").float()
        print(f"[data] loaded real Qwen3-0.6B q_proj weight {tuple(w.shape)}")
        return w
    except Exception as e:  # noqa: BLE001
        print(f"[data] fallback to mock random weight ({type(e).__name__})")
        torch.manual_seed(0)
        return torch.randn(2048, 1024)


def quant_block_e2m1(x: torch.Tensor, scale: float) -> torch.Tensor:
    """Quantize one block to signed E2M1 grid given scale."""
    y = x / scale
    sign = torch.sign(y)
    mag = y.abs()
    # nearest E2M1 magnitude
    idx = (mag.unsqueeze(-1) - E2M1).abs().argmin(-1)
    return sign * E2M1[idx] * scale


def mx_quantize(W: torch.Tensor, block: int = 32, use_metadata: bool = False):
    m, n = W.shape
    n_pad = (block - n % block) % block
    Wp = torch.nn.functional.pad(W, (0, n_pad))
    Wb = Wp.reshape(m, -1, block)
    out = torch.zeros_like(Wb)
    for i in range(Wb.shape[0]):
        for j in range(Wb.shape[1]):
            blk = Wb[i, j]
            amax = blk.abs().max().item()
            if amax == 0:
                continue
            # MXFP4: shared power-of-two scale s.t. max magnitude maps to 6.0
            pot = 2.0 ** torch.round(torch.log2(torch.tensor(amax / 6.0))).item()
            if not use_metadata:
                out[i, j] = quant_block_e2m1(blk, pot)
            else:
                # M2XFP: choose the 2-bit refinement minimizing block MSE
                best, best_err = None, None
                for r in REFINE:
                    q = quant_block_e2m1(blk, pot * r.item())
                    err = torch.mean((blk - q) ** 2).item()
                    if best_err is None or err < best_err:
                        best, best_err = q, err
                out[i, j] = best
    return out.reshape(m, -1)[:, :n]


def main():
    torch.manual_seed(0)
    W = load_weight()
    W_mx = mx_quantize(W, use_metadata=False)
    W_m2 = mx_quantize(W, use_metadata=True)
    mse_mx = torch.mean((W - W_mx) ** 2).item()
    mse_m2 = torch.mean((W - W_m2) ** 2).item()
    red = (mse_mx - mse_m2) / mse_mx * 100
    print(f"[result] recon MSE  MXFP4 (PoT scale):        {mse_mx:.6e}")
    print(f"[result] recon MSE  M2XFP (PoT + 2-bit meta):  {mse_m2:.6e}")
    print(f"[check] metadata reduces quantization error by {red:.1f}% "
          f"({'PASS' if mse_m2 < mse_mx else 'FAIL'})")


if __name__ == "__main__":
    main()
