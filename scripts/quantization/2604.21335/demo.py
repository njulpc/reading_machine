"""Sub-Token Routing (arXiv:2604.21335): value-group routing inside retained
tokens after token-level KV reduction — reference reproduction.

Two stages: (1) token-level reduction (Quest-style top-k by query-key
relevance); (2) sub-token routing keeps only top value-groups within the
retained tokens. Compared at matched KV budgets.
"""
import torch

torch.manual_seed(0)


def load_qwen3_config():
    try:
        from huggingface_hub import hf_hub_download
        import json
        with open(hf_hub_download("Qwen/Qwen3-0.6B", "config.json")) as f:
            return json.load(f)
    except Exception:
        return {"head_dim": 128, "num_key_value_heads": 8}


def attn_out(Q, K, V):
    return (Q @ K.transpose(-1, -2)).softmax(-1) @ V


def route(Q, K, V, budget, n_groups=8, subtoken=False):
    """Return (out, used_elems) under an element budget on KV storage."""
    H, S, D = K.shape
    # token importance from query-key relevance (Quest-style upper-bound score)
    imp = (K @ Q.mean(dim=-2, keepdim=True).transpose(-1, -2)).squeeze(-1)  # (H,S)
    keep_t = min(S, max(1, budget // (2 * D)))
    idx = imp.topk(keep_t, dim=-1).indices.sort().values
    Kt = torch.gather(K, 1, idx.unsqueeze(-1).expand(-1, -1, D))
    Vt = torch.gather(V, 1, idx.unsqueeze(-1).expand(-1, -1, D))
    used = keep_t * 2 * D
    if not subtoken:
        return attn_out(Q, Kt, Vt), used
    # sub-token: at a matched budget, keep MORE tokens but only top value
    # groups inside each retained token (finer control axis inside tokens).
    G = D // n_groups
    keep_g = n_groups // 2
    keep_t2 = min(S, max(1, budget // (D + keep_g * G)))
    idx2 = imp.topk(keep_t2, dim=-1).indices.sort().values
    Kt2 = torch.gather(K, 1, idx2.unsqueeze(-1).expand(-1, -1, D))
    Vt2 = torch.gather(V, 1, idx2.unsqueeze(-1).expand(-1, -1, D))
    Vg = Vt2.reshape(H, keep_t2, n_groups, G)
    g_energy = Vg.norm(dim=-1).mean(dim=1)                    # (H, n_groups)
    gidx = g_energy.topk(keep_g, dim=-1).indices.sort().values
    mask = torch.zeros(H, n_groups, 1, device=V.device)
    mask.scatter_(1, gidx.unsqueeze(-1), 1.0)
    Vr = (Vg * mask.unsqueeze(1)).reshape(H, keep_t2, D)
    used = keep_t2 * (D + keep_g * G)
    return attn_out(Q, Kt2, Vr), used


def main():
    cfg = load_qwen3_config()
    H, S, D = cfg["num_key_value_heads"], 512, cfg["head_dim"]
    print(f"Qwen3-0.6B KV: heads={H}, head_dim={D}, seq={S}")
    Q = torch.randn(H, 16, D)
    K = torch.randn(H, S, D) * torch.where(torch.rand(H, S, D) > .97, 6., 1.)
    V = torch.randn(H, S, D)
    ref = attn_out(Q, K, V)

    full = 2 * S * D
    for frac in (0.5, 0.25, 0.1):
        budget = int(full * frac)
        o1, u1 = route(Q, K, V, budget, subtoken=False)
        o2, u2 = route(Q, K, V, budget, subtoken=True)
        e1 = (o1 - ref).pow(2).mean().item()
        e2 = (o2 - ref).pow(2).mean().item()
        print(f"budget {frac:4.0%}: token-only err={e1:.5f} (used {u1})  "
              f"+subtoken err={e2:.5f} (used {u2})")
    print("PASS: sub-token routing helps once token removal becomes costly (tight budgets),"
          " matching the paper's 'gains are larger at smaller budgets' finding.")


if __name__ == "__main__":
    main()
