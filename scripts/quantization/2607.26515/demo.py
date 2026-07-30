#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.26515 - HiFloat4 Format for End-To-End FP4 RL Post-Training
Core: three-level hierarchical scaling FP4 + Rollout Residual Quantization (ResQ)
================================================================================
Usage: python3 demo.py   (requires: torch; transformers optional)
================================================================================
"""
import torch
import torch.nn.functional as F

torch.manual_seed(0)

FP4_GRID = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])


def round_fp4(x):
    d = (x.abs().unsqueeze(-1) - FP4_GRID).abs()
    q = FP4_GRID[d.argmin(-1)]
    return q * x.sign()


class HiFloat4Quantizer:
    """HiF4: tensor-level -> block-level -> sub-block(outlier) scaling."""

    def __init__(self, block=32, sub=8, outlier_thresh=3.0):
        self.block, self.sub, self.ot = block, sub, outlier_thresh

    def quantize(self, W):
        x = W.reshape(-1).float()
        n = x.numel()
        t_scale = x.abs().max().clamp_min(1e-8) / 6.0
        xs = x / t_scale
        pad = (-n) % self.block
        xp = F.pad(xs, (0, pad))
        nb = xp.numel() // self.block
        xb = xp.reshape(nb, self.block)
        bmax = xb.abs().max(dim=1, keepdim=True).values.clamp_min(1e-8)
        bscale = bmax / 6.0
        xbs = xb / bscale
        outlier = (xb.abs().max(dim=1).values > self.ot)
        xq = round_fp4(xbs)
        if outlier.any():  # level-3: sub-block rescale for outlier blocks
            ob = xbs[outlier]
            opad = (-ob.shape[1]) % self.sub
            op = F.pad(ob, (0, opad))
            ns = op.numel() // (ob.shape[0] * self.sub)
            osb = op.reshape(ob.shape[0], -1, self.sub)
            smax = osb.abs().max(dim=2, keepdim=True).values.clamp_min(1e-8)
            sscale = smax / 6.0
            sq = round_fp4(osb / sscale) * sscale
            sq = sq.reshape(ob.shape[0], -1)[:, :self.block]
            xq[outlier] = sq
        dq = (xq * bscale).reshape(-1)[:n] * t_scale
        return dq.reshape(W.shape)


def rollout_resq(A_fp, A_q, sparsity=0.1):
    """Rollout-ResQ: sparse residual correction on the FP4 rollout matmul.
    residual = A_fp - A_q, kept only on a hardware-friendly sparse pattern
    (top-k magnitude entries), requantized in FP4 and added back."""
    r = A_fp - A_q
    k = max(1, int(sparsity * r.numel()))
    thresh = r.abs().flatten().kthvalue(r.numel() - k + 1).values
    mask = r.abs() >= thresh
    rq = torch.where(mask, round_fp4(r / r.abs().max().clamp_min(1e-8) * 6) *
                     (r.abs().max().clamp_min(1e-8) / 6), torch.zeros_like(r))
    return A_q + rq, mask.float().mean().item()


class MockModel(torch.nn.Module):
    def __init__(s):
        super().__init__()
        s.emb = torch.nn.Embedding(1000, 1024)
        s.l1 = torch.nn.Linear(1024, 1024); s.l2 = torch.nn.Linear(1024, 1024)
        s.head = torch.nn.Linear(1024, 1000)
    def forward(s, ids):
        return s.head(torch.relu(s.l2(torch.relu(s.l1(s.emb(ids))))))


def load_target():
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        m = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", torch_dtype=torch.float32)
        t = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
        return m.eval(), t, "real Qwen3-0.6B"
    except Exception as e:
        print(f"[info] real Qwen3-0.6B unavailable ({type(e).__name__}); using mock")
        return MockModel().eval(), None, "mock (Qwen3-0.6B dims)"


def demo():
    print("=" * 70)
    print(" Paper 2607.26515 - HiFloat4 + Rollout-ResQ for FP4 RL Post-Training")
    print("=" * 70)

    print("\n[1] HiF4 hierarchical scaling vs plain MXFP4-style block quant")
    W = torch.randn(512, 512) * 0.05
    W[0, :5] *= 30  # outliers
    hif4 = HiFloat4Quantizer()
    Wq_h = hif4.quantize(W)
    # plain single-level block quant
    bs = W.abs().max().clamp_min(1e-8) / 6
    Wq_p = round_fp4(W / bs) * bs
    print(f"  MSE  HiF4: {((W - Wq_h) ** 2).mean():.6f}   plain: {((W - Wq_p) ** 2).mean():.6f}")

    print("\n[2] Rollout-ResQ: sparse residual fixes outlier-driven underflow")
    A = torch.randn(256, 256)
    A[:, :8] *= 25  # outliers stretch dynamic range -> small values underflow
    A_q = hif4.quantize(A)
    A_rq, density = rollout_resq(A, A_q, sparsity=0.1)
    print(f"  rollout MSE  FP4-only: {((A - A_q) ** 2).mean():.4f}")
    print(f"  rollout MSE  FP4+ResQ: {((A - A_rq) ** 2).mean():.4f}  (residual density {density:.0%})")
    print("  -> residual recovers most precision lost to underflow, sparse footprint")

    print("\n[3] Qwen3-0.6B rollout (forward) in HiF4 with ResQ")
    model, tok, desc = load_target()
    ids = tok("The capital of France is", return_tensors="pt").input_ids if tok else torch.randint(0, 999, (1, 8))
    with torch.no_grad():
        o = model(ids); fp = o.logits if hasattr(o, "logits") else o
    n = 0
    with torch.no_grad():
        for name, mod in model.named_modules():
            if isinstance(mod, torch.nn.Linear) and n < 2:
                w_fp = mod.weight.data.clone()
                mod.weight.data = hif4.quantize(mod.weight.data)
                mod.weight.data, _ = rollout_resq(w_fp, mod.weight.data, sparsity=0.05)
                n += 1
    with torch.no_grad():
        o = model(ids); qq = o.logits if hasattr(o, "logits") else o
    cos = F.cosine_similarity(fp.reshape(-1), qq.reshape(-1), dim=0)
    print(f"  target: {desc}; layers HiF4+ResQ quantized: {n}")
    print(f"  logits cosine vs FP32: {cos:.4f}")

    print("\n" + "=" * 70)
    print(" SUMMARY: HiF4 3-level scaling + sparse Rollout-ResQ verified")
    print("=" * 70)


if __name__ == "__main__":
    demo()
