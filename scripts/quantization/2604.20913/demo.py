"""FairyFuse (arXiv:2604.20913): multiplication-free ternary GEMV —
reference reproduction of the ternary compute path on CPU.

Core idea: with W in {-1,0,+1}*gamma, y = x @ W^T becomes masked adds and
subtracts. We verify numerical equivalence against float matmul and give a
roofline estimate of the bandwidth benefit from 16x weight compression.
"""
import time
import torch

torch.manual_seed(0)


def load_qwen3_config():
    try:
        from huggingface_hub import hf_hub_download
        import json
        with open(hf_hub_download("Qwen/Qwen3-0.6B", "config.json")) as f:
            return json.load(f)
    except Exception:
        return {"hidden_size": 1024, "intermediate_size": 3072}


def ternarize(W, thresh_ratio=0.7):
    """Fairy2i-style ternarization: |w| > thresh -> +/-1 else 0, per-row scale."""
    thresh = thresh_ratio * W.abs().mean(dim=1, keepdim=True)
    T = torch.zeros_like(W)
    T[W > thresh] = 1.0
    T[W < -thresh] = -1.0
    nz = T.abs().sum(dim=1, keepdim=True).clamp(min=1.0)
    gamma = (W * T).sum(dim=1, keepdim=True) / nz
    return T, gamma


def ternary_gemv_mulfree(x, T, gamma):
    """Multiplication-free GEMV: only adds/subs selected by T's sign mask.
    x: (N, I); T: (O, I) in {-1,0,1}; returns (N, O)."""
    pos = T > 0
    neg = T < 0
    # accumulate: for each output row, sum x over +1 cols minus sum over -1 cols.
    # Vectorized equivalent of the masked add/sub loop (zero float multiplies
    # inside the accumulation — masks act as conditional selects).
    s_pos = torch.where(pos.unsqueeze(0), x.unsqueeze(1), torch.zeros(1, device=x.device, dtype=x.dtype)).sum(-1)
    s_neg = torch.where(neg.unsqueeze(0), x.unsqueeze(1), torch.zeros(1, device=x.device, dtype=x.dtype)).sum(-1)
    return (s_pos - s_neg) * gamma.T


def main():
    cfg = load_qwen3_config()
    I, O, N = cfg["hidden_size"], cfg["intermediate_size"], 32
    print(f"Qwen3-0.6B linear layer: {I} -> {O}")
    W = torch.randn(O, I) * 0.05
    x = torch.randn(N, I)

    T, gamma = ternarize(W)
    y_ref = x @ W.T                      # full-precision reference
    y_tern = x @ (T * gamma).T           # float emulation of ternary matmul
    y_free = ternary_gemv_mulfree(x, T, gamma)

    err_exact = (y_free - y_tern).abs().max().item()
    rel = (y_free - y_ref).norm() / y_ref.norm()
    print(f"mul-free vs float-emulated ternary: max abs diff = {err_exact:.2e}")
    print(f"ternary vs FP32 relative error: {rel:.4f}")
    assert err_exact < 1e-4

    # --- illustrative CPU latency comparison (not the paper's fused kernel)
    t0 = time.perf_counter(); _ = x @ W.T; t_fp = time.perf_counter() - t0
    t0 = time.perf_counter(); _ = ternary_gemv_mulfree(x, T, gamma); t_tf = time.perf_counter() - t0
    print(f"latency (illustrative): fp matmul {t_fp*1e3:.2f} ms, "
          f"mul-free path {t_tf*1e3:.2f} ms")

    # --- roofline estimate: 16x weight compression (32->2 bits)
    bytes_fp, bytes_t = W.numel() * 4, W.numel() * 0.25
    print(f"weights: {bytes_fp/1e6:.1f} MB fp32 -> {bytes_t/1e6:.2f} MB ternary "
          f"({bytes_fp/bytes_t:.0f}x smaller; bandwidth-bound decode benefits ~linearly)")
    print("PASS: multiplication-free ternary GEMV matches float emulation.")


if __name__ == "__main__":
    main()
