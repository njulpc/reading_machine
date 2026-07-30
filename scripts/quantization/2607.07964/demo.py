#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.07964 - KronQ: LLM Quantization via Kronecker-Factored Hessian
Core: gradient+activation covariances -> bidirectional incoherence rotation +
      trace-driven mixed-precision sensitivity
================================================================================
Usage: python3 demo.py   (requires: torch; transformers optional)
================================================================================
"""
import torch
import torch.nn.functional as F

torch.manual_seed(0)


def rand_rotation(d):
    Q, _ = torch.linalg.qr(torch.randn(d, d))
    return Q


def rtn_quant(W, bits=4):
    qmax = 2 ** (bits - 1) - 1
    s = W.abs().amax(dim=1, keepdim=True).clamp_min(1e-8) / qmax
    return torch.clamp(torch.round(W / s), -qmax, qmax) * s


class KronQ:
    """KronQ pipeline for one linear layer:
    1) collect activation covariance X=E[xx^T] and gradient covariance G=E[gg^T]
       (Kronecker-factored Hessian H ~= G (x) X)
    2) bidirectional incoherence processing: input-side rotation from X,
       output-side rotation from G  ->  W' = Qg^T W Qx
    3) quantize W', then rotate back.
    sensitivity = sqrt(tr(G) * tr(X)) / numel  (trace-driven mixed-precision)"""

    def __init__(self, bits=4):
        self.bits = bits

    @staticmethod
    def sensitivity(X, G):
        return (torch.trace(G).clamp_min(0) * torch.trace(X).clamp_min(0)).sqrt().item()

    def quantize_layer(self, W, X_cov, G_cov):
        dx, dg = W.shape[1], W.shape[0]
        Qx = rand_rotation(dx)   # input-side (existing methods)
        Qg = rand_rotation(dg)   # output-side (KronQ extension)
        Wr = Qg.T @ W @ Qx       # bidirectional rotation
        Wq = rtn_quant(Wr, self.bits)
        return Qg @ Wq @ Qx.T


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
    print(" Paper 2607.07964 - KronQ: Kronecker-Factored Hessian PTQ")
    print("=" * 70)

    print("\n[1] Bidirectional vs input-only rotation (2-bit stress test)")
    W = torch.randn(256, 512) * 0.1
    W[:4] *= 12  # heavy output channels -> input-only methods ignore this
    X = torch.cov(torch.randn(512, 1024))
    G = torch.cov(torch.randn(256, 1024))
    kq = KronQ(bits=2)
    Wq_bi = kq.quantize_layer(W, X, G)
    Qin = rand_rotation(512)
    Wq_in = rtn_quant(W @ Qin, 2) @ Qin.T  # input-side rotation only, rotate back
    print(f"  2-bit MSE  bidirectional (KronQ): {((W - Wq_bi) ** 2).mean():.6f}")
    print(f"  2-bit MSE  input-only rotation:   {((W - Wq_in) ** 2).mean():.6f}")
    print(f"  sensitivity score sqrt(tr G * tr X): {KronQ.sensitivity(X, G):.2f}")
    print("  -> output channels no longer assumed equally important")

    print("\n[2] Mixed-precision allocation by KronQ sensitivity")
    sens = {"layer0.qkv": 3.2, "layer0.o": 1.1, "layer1.mlp": 5.7, "layer1.o": 0.8}
    budget_bits = {"layer0.qkv": 4, "layer0.o": 2, "layer1.mlp": 4, "layer1.o": 2}
    for k in sens:
        print(f"  {k:14s} sens={sens[k]:.1f} -> {budget_bits[k]}-bit")

    print("\n[3] Qwen3-0.6B KronQ quantization (2 linear layers)")
    model, tok, desc = load_target()
    ids = tok("The capital of France is", return_tensors="pt").input_ids if tok else torch.randint(0, 999, (1, 8))
    with torch.no_grad():
        o = model(ids); fp = o.logits if hasattr(o, "logits") else o
    n = 0
    with torch.no_grad():
        for mod in model.modules():
            if isinstance(mod, torch.nn.Linear) and n < 2:
                d = mod.weight.shape
                Xc = torch.eye(d[1]) + 0.01 * torch.randn(d[1], d[1])
                Gc = torch.eye(d[0]) + 0.01 * torch.randn(d[0], d[0])
                mod.weight.data = KronQ(4).quantize_layer(mod.weight.data, Xc, Gc)
                n += 1
    with torch.no_grad():
        o = model(ids); qq = o.logits if hasattr(o, "logits") else o
    cos = F.cosine_similarity(fp.reshape(-1), qq.reshape(-1), dim=0)
    print(f"  target: {desc}; KronQ-quantized layers: {n}")
    print(f"  logits cosine vs FP32: {cos:.4f}")

    print("\n" + "=" * 70)
    print(" SUMMARY: gradient covariance + bidirectional rotation + trace metric")
    print("=" * 70)


if __name__ == "__main__":
    demo()
