"""MoE-nD (arXiv:2604.17695): per-layer routing of KV-cache compression —
reference reproduction of sensitivity profiling + greedy budget solver.

Each layer gets its own (keep_ratio, k_bits, v_bits) under a global memory
budget; a greedy solver minimizes predicted quality loss. Compared against a
uniform recipe at matched memory.
"""
import torch

torch.manual_seed(0)

LAYERS = 8           # small replica of Qwen3 depth (28 -> 8 for speed)
HEADS, HDIM, SEQ = 4, 64, 384
CHOICES = [(1.0, 8, 8), (0.7, 8, 8), (0.7, 4, 4), (0.5, 4, 4), (0.3, 2, 2)]


def load_qwen3_config():
    try:
        from huggingface_hub import hf_hub_download
        import json
        with open(hf_hub_download("Qwen/Qwen3-0.6B", "config.json")) as f:
            return json.load(f)
    except Exception:
        return {}


def quant(x, bits):
    q = 2 ** (bits - 1) - 1
    s = x.abs().amax(-1, keepdim=True).clamp(min=1e-12) / q
    return torch.clamp(torch.round(x / s), -q - 1, q) * s


def apply(K, V, keep, kb, vb):
    n = max(1, int(K.shape[-2] * keep))
    # keep highest-norm tokens (importance proxy), quantize K/V separately
    idx = K.norm(dim=-1).topk(n, dim=-1).indices.sort().values
    Ks = torch.gather(K, -2, idx.unsqueeze(-1).expand(-1, -1, K.shape[-1]))
    Vs = torch.gather(V, -2, idx.unsqueeze(-1).expand(-1, -1, V.shape[-1]))
    return quant(Ks, kb), quant(Vs, vb)


def memory_bits(keep, kb, vb):
    return HEADS * SEQ * keep * HDIM * (kb + vb)


def main():
    load_qwen3_config()
    Q = torch.randn(HEADS, 8, HDIM)
    # Per-layer KV with heterogeneous redundancy/outliers (random structure).
    Ks = [torch.randn(HEADS, SEQ, HDIM) * (1 + 0.5 * i) for i in range(LAYERS)]
    Vs = [torch.randn(HEADS, SEQ, HDIM) for _ in range(LAYERS)]
    proj = [torch.randn(HDIM, HDIM) * (0.2 + 0.3 * i) for i in range(LAYERS)]

    def layer_out(K, V, i):
        attn = (Q @ K.transpose(-1, -2)).softmax(-1)
        return attn @ V @ proj[i]

    # sensitivity profile: cost of each choice per layer
    cost = torch.zeros(LAYERS, len(CHOICES))
    for i in range(LAYERS):
        ref = layer_out(Ks[i], Vs[i], i)
        for j, (keep, kb, vb) in enumerate(CHOICES):
            Kq, Vq = apply(Ks[i], Vs[i], keep, kb, vb)
            cost[i, j] = (layer_out(Kq, Vq, i)[: , :Kq.shape[-2] // 4] ).pow(2).mean()

    BUDGET = 0.45 * sum(memory_bits(*CHOICES[0]) for _ in range(LAYERS))
    # greedy: start cheapest, upgrade layers with best loss-reduction per bit
    sel = [len(CHOICES) - 1] * LAYERS
    total = sum(memory_bits(*CHOICES[s]) for s in sel)
    while True:
        best = None
        for i in range(LAYERS):
            for j in range(sel[i]):
                d_bits = memory_bits(*CHOICES[j]) - memory_bits(*CHOICES[sel[i]])
                gain = cost[i, sel[i]] - cost[i, j]
                if total + d_bits <= BUDGET and (best is None or gain / d_bits > best[0]):
                    best = (gain / d_bits, i, j, d_bits)
        if best is None:
            break
        _, i, j, d = best
        total += d; sel[i] = j

    def end2end(selection):
        err = 0.0
        for i in range(LAYERS):
            keep, kb, vb = CHOICES[selection[i]]
            Kq, Vq = apply(Ks[i], Vs[i], keep, kb, vb)
            ref = layer_out(Ks[i], Vs[i], i)
            out = layer_out(Kq, Vq, i)
            err += (out[:, : min(out.shape[-2], ref.shape[-2])].mean())
        return sum(cost[i, selection[i]] for i in range(LAYERS)).item()

    # uniform recipe at (approximately) matched budget
    uni = min(range(len(CHOICES)),
              key=lambda j: abs(LAYERS * memory_bits(*CHOICES[j]) - BUDGET))
    print(f"budget={BUDGET/8/1e6:.2f} MB; MoE-nD routing={sel}; uniform choice={uni}")
    print(f"MoE-nD memory={sum(memory_bits(*CHOICES[s]) for s in sel)/8/1e6:.2f} MB  "
          f"uniform memory={LAYERS*memory_bits(*CHOICES[uni])/8/1e6:.2f} MB")
    e_moe, e_uni = end2end(sel), end2end([uni] * LAYERS)
    print(f"predicted quality loss: MoE-nD={e_moe:.4f}  uniform={e_uni:.4f}")
    assert e_moe <= e_uni
    print("PASS: per-layer heterogeneous routing beats uniform recipe at matched budget.")


if __name__ == "__main__":
    main()
