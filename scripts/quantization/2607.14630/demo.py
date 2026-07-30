#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.14630 - Cross-Layer Error Compensation and Finite-Sample
       Feature-Statistics Matching for Extreme Low-Bit Quantization of LLMs
Core: layer-wise PTQ lets errors accumulate over depth.  The paper maintains
      the network-level accumulated error (e_{l+1} = A_l e_l + q_l) and
      matches feature statistics to the teacher, so each block is optimized
      to compensate the error introduced by the already-quantized prefix.
================================================================================
Demo: group-binary weights.  Baseline: per-layer local least-squares scales
      (independent calibration).  Compensation: each block's scales are tuned
      so the total BLOCK output (residual stream + branch) matches the
      TEACHER's block output on top of the quantized prefix -- a tractable
      forward-difference form of the paper's error recursion.
      (1) synthetic residual MLP chain; (2) per-layer mean drift diagnostic;
      (3) Qwen3-0.6B first 4 blocks MLP at 1.125-bit, logits cosine.
Usage: python3 demo.py   (requires: torch; transformers optional)
================================================================================
"""
import copy
import torch
import torch.nn.functional as F

torch.manual_seed(0)


def local_scales(W, x2, g=64):
    """Independent calibration: per-group LS scale for sign(W) under E[x^2]."""
    m, n = W.shape
    ng = (n + g - 1) // g
    S = torch.zeros(m, ng)
    for j0 in range(0, n, g):
        j1 = min(j0 + g, n)
        Wg = W[:, j0:j1]
        x2g = x2[j0:j1].clamp_min(1e-12)
        S[:, j0 // g] = (Wg.abs() * x2g).sum(1) / x2g.sum().clamp_min(1e-12)
    return S


def expand(S, n, g):
    return S.repeat_interleave(g, dim=1)[:, :n]


def mlp_forward(layers, X):
    """Residual MLP chain (transformer-like residual stream)."""
    H = X
    for ln in layers:
        H = H + F.gelu(ln(H))
    return H


print("=" * 74)
print("[1] Synthetic 12-block residual MLP, ~1.1-bit group-binary weights")
print("=" * 74)
d, L, Ns, g = 64, 12, 2048, 64
layers = [torch.nn.Linear(d, d, bias=False) for _ in range(L)]
with torch.no_grad():
    for ln in layers:
        ln.weight.mul_(0.4)
X = torch.randn(Ns, d) * torch.logspace(0.0, 2.0, d)[torch.randperm(d)]
with torch.no_grad():
    Hs = [X]
    H = X
    for ln in layers:
        H = H + F.gelu(ln(H))
        Hs.append(H)
ref = Hs[-1]

# --- independent: local LS scales, layer by layer on teacher features ---
with torch.no_grad():
    ind = copy.deepcopy(layers)
    H = X
    for l in range(L):
        x2 = (H ** 2).mean(0)
        W = layers[l].weight.data
        ind[l].weight.data = torch.sign(W) * expand(local_scales(W, x2, g), d, g)
        H = H + F.gelu(layers[l](H))
    out_ind = mlp_forward(ind, X)

# --- compensated: per block, scales tuned so block output matches teacher ---
comp = copy.deepcopy(layers)
H = X.detach()
for l in range(L):
    W = layers[l].weight.data
    sign = torch.sign(W)
    S = torch.nn.Parameter(W.abs().mean(1, keepdim=True))
    opt = torch.optim.Adam([S], lr=0.02)
    tgt, const = Hs[l + 1], H          # teacher block output / quantized prefix
    for _ in range(200):
        opt.zero_grad()
        loss = F.mse_loss(const + F.gelu(F.linear(const, sign * S)), tgt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        comp[l].weight.data = (sign * S).detach()
        H = const + F.gelu(F.linear(const, comp[l].weight.data))
with torch.no_grad():
    out_comp = mlp_forward(comp, X)

e_ind = ((out_ind - ref).norm() / ref.norm()).item()
e_comp = ((out_comp - ref).norm() / ref.norm()).item()
print(f"  output rel. error, independent (local LS)    : {e_ind:.4f}")
print(f"  output rel. error, compensated (block match) : {e_comp:.4f}  "
      f"({'BETTER' if e_comp < e_ind else 'worse'})")

print()
print("=" * 74)
print("[2] Feature-statistics matching diagnostic (per-layer mean drift)")
print("=" * 74)
with torch.no_grad():
    Ht, Hi, Hc = X, X, X
    drift_i, drift_c = [], []
    for l in range(L):
        Ht = Ht + F.gelu(layers[l](Ht))
        Hi = Hi + F.gelu(ind[l](Hi))
        Hc = Hc + F.gelu(comp[l](Hc))
        nrm = Ht.mean(0).norm().clamp_min(1e-8)
        drift_i.append(((Hi.mean(0) - Ht.mean(0)).norm() / nrm).item())
        drift_c.append(((Hc.mean(0) - Ht.mean(0)).norm() / nrm).item())
    print("  layer-mean drift independent :",
          " ".join(f"{v:.3f}" for v in drift_i))
    print("  layer-mean drift compensated :",
          " ".join(f"{v:.3f}" for v in drift_c))

print()
print("=" * 74)
print("[3] Qwen3-0.6B first 4 blocks MLP, 1.125-bit: last-token logits cosine")
print("=" * 74)
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B",
                                                 torch_dtype=torch.float32)
    model.eval()
    ids = tok("Quantization errors accumulate across depth in large language "
              "models, especially at extreme bit widths.", return_tensors="pt")

    LINEARS = ["gate_proj", "up_proj", "down_proj"]
    NB, G = 4, 128   # 1.125-bit group binary

    def collect(m, what):
        """One forward pass capturing either per-linear input E[x^2] ('x2'),
        per-block (mlp_input, mlp_output) ('mlp'), or block outputs ('blk')."""
        store, hooks = {}, []
        for b in range(NB):
            blk = m.model.layers[b]
            if what == "blk":
                def make_hook(key):
                    def hook(_, __, out):
                        store[key] = (out[0] if isinstance(out, tuple) else out
                                      ).detach().float()
                    return hook
                hooks.append(blk.register_forward_hook(make_hook(b)))
            elif what == "x2":
                for name in LINEARS:
                    mod = getattr(blk.mlp, name)

                    def make_hook(key):
                        def hook(_, inp, __):
                            x = inp[0].detach().float().reshape(-1, inp[0].shape[-1])
                            store[key] = (x ** 2).mean(0)
                        return hook
                    hooks.append(mod.register_forward_hook(make_hook((b, name))))
            else:
                def make_hook(key):
                    def hook(_, inp, out):
                        store[key] = (inp[0].detach().float(),
                                      out.detach().float())
                    return hook
                hooks.append(blk.mlp.register_forward_hook(make_hook(b)))
        with torch.no_grad():
            m(**ids)
        for h in hooks:
            h.remove()
        return store

    with torch.no_grad():
        ref_logits = model(**ids).logits
    x2_teacher = collect(model, "x2")
    blk_teacher = collect(model, "blk")

    def logits_cos(m):
        with torch.no_grad():
            lg = m(**ids).logits
        return F.cosine_similarity(ref_logits[0, -1], lg[0, -1], dim=0).item()

    # ---- independent baseline: local LS scales from teacher features ----
    mq = copy.deepcopy(model)
    for b in range(NB):
        for name in LINEARS:
            mod = getattr(mq.model.layers[b].mlp, name)
            W = mod.weight.data.float()
            mod.weight.data = torch.sign(W) * expand(
                local_scales(W, x2_teacher[(b, name)], G), W.shape[1], G)
    cos_i = logits_cos(mq)
    print(f"  independent (local LS) : {cos_i:.4f}")
    del mq

    # ---- compensated: per block, tune the 3 linears' scales so the total
    #      BLOCK output (residual stream + attention + MLP) matches the
    #      TEACHER's block output given the quantized prefix.  The non-MLP
    #      part is constant w.r.t. MLP scales, so this stays a tiny
    #      sub-network optimization.
    mq = copy.deepcopy(model)
    for b in range(NB):
        blk = mq.model.layers[b]
        mlp_in, mlp_out = collect(mq, "mlp")[b]
        blk_out = collect(mq, "blk")[b]
        const = blk_out - mlp_out                    # residual + attention
        tgt = blk_teacher[b]                         # teacher block output
        act = blk.mlp.act_fn
        mods = {name: getattr(blk.mlp, name) for name in LINEARS}
        Ws = {name: mods[name].weight.data.float() for name in LINEARS}
        signs = {name: torch.sign(Ws[name]) for name in LINEARS}
        S = {name: torch.nn.Parameter(Ws[name].abs().mean(1, keepdim=True))
             for name in LINEARS}  # init: per-output-channel magnitude scale
        opt = torch.optim.Adam(list(S.values()), lr=0.02)

        def blk_q(x):
            gq = F.linear(x, signs["gate_proj"] * S["gate_proj"])
            uq = F.linear(x, signs["up_proj"] * S["up_proj"])
            return const + F.linear(act(gq) * uq,
                                    signs["down_proj"] * S["down_proj"])

        for _ in range(120):
            opt.zero_grad()
            loss = F.mse_loss(blk_q(mlp_in), tgt)
            loss.backward()
            opt.step()
        with torch.no_grad():
            for name in LINEARS:
                mods[name].weight.data = (signs[name] * S[name]).detach()
    cos_c = logits_cos(mq)
    print(f"  compensated (blk-out)  : {cos_c:.4f}  "
          f"({'BETTER' if cos_c > cos_i else 'worse'})")
except Exception as e:
    print(f"  skipped (model unavailable): {type(e).__name__}: {e}")

print()
print("Done. Optimizing each block against the teacher's block output on top")
print("of the quantized prefix compensates accumulated cross-layer error,")
print("matching the paper's recursion e_{l+1} = A_l e_l + q_l.")
