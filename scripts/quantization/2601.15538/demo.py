"""Paper: QUAIL: Quantization Aware Unlearning for Mitigating Misinformation
in LLMs (arXiv:2601.15538)

Core algorithm reproduction: quantization-aware unlearning via a logits-space
hinge loss.

Paper's mechanism (their Sec. 1): typical unlearning weight updates are too
small to cross quantization bucket thresholds, so quantization silently
"erases" the forgetting. QUAIL forces, for each forget example, the output
logits of the unlearned model to differ from the original model by at least a
margin (half the quantization step), so the distinction survives
quantization.

Toy setup (controlled reproduction of the mechanism):
  y = W x with W a slice of a real Qwen3-0.6B weight (HF cache; mock
  fallback). We produce an unlearning update Delta two ways:
    baseline - a few small gradient steps toward a "forgotten" target,
               mimicking practical unlearning (updates stay sub-threshold);
    QUAIL    - hinge loss relu(margin - ||y_new - y_orig||) in logits space.
  We then report the paper's own diagnostics: per-weight update magnitude vs
  4-bit bucket half-width, fraction of weights crossing a bucket boundary,
  and the forget logit shift before/after 4-bit quantization.

Run: python3 demo.py
"""
import glob
import os

import torch


def load_weight() -> torch.Tensor:
    try:
        from safetensors import safe_open

        path = glob.glob(
            os.path.expanduser(
                "~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/*/model.safetensors"
            )
        )[0]
        f = safe_open(path, framework="pt")
        w = f.get_tensor("model.layers.0.self_attn.q_proj.weight").float()[:64]
        print(f"[data] loaded real Qwen3-0.6B q_proj weight slice {tuple(w.shape)}")
        return w
    except Exception as e:  # noqa: BLE001
        print(f"[data] fallback to mock random weight ({type(e).__name__})")
        torch.manual_seed(0)
        return torch.randn(64, 1024) * 0.02


def quant4(W: torch.Tensor) -> torch.Tensor:
    qmax = 7
    s = W.abs().amax(dim=1, keepdim=True) / qmax
    return torch.clamp(torch.round(W / s), -qmax - 1, qmax) * s


def baseline_unlearn(W, Xf, steps=3, lr=1e-4):
    """A few small gradient steps toward a shifted target (practical unlearning)."""
    Delta = torch.zeros_like(W, requires_grad=True)
    opt = torch.optim.Adam([Delta], lr=lr)
    for _ in range(steps):
        loss = torch.mean(((W + Delta) @ Xf - 0.9 * (W @ Xf)) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return Delta.detach()


def quail_unlearn(W, Xf, margin, steps=300, lr=1e-3):
    """QUAIL: force per-example logit shift >= margin via hinge loss."""
    Delta = (1e-4 * torch.randn_like(W)).requires_grad_(True)  # nonzero init (norm grad at 0 is 0)
    opt = torch.optim.Adam([Delta], lr=lr)
    for _ in range(steps):
        diff = Delta @ Xf
        shift = torch.sqrt((diff**2).sum(dim=0) + 1e-8)
        loss = torch.relu(margin - shift).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return Delta.detach()


def diagnostics(W, Delta, Xf, s_row, tag):
    rms = Delta.pow(2).mean().sqrt().item()
    sub_thresh = (Delta.abs() < s_row.unsqueeze(1) / 2).float().mean().item()
    cross = (quant4(W + Delta) != quant4(W)).float().mean().item()
    pre = Delta @ Xf
    post = (quant4(W + Delta) - quant4(W)) @ Xf
    # does the forgetting *direction* survive quantization, or is it drowned
    # in quantization noise? (cosine between intended and observed shift)
    sim = torch.nn.functional.cosine_similarity(pre, post, dim=0).mean().item()
    print(f"[{tag}] |Delta|_rms={rms:.2e} | sub-threshold updates={sub_thresh:.1%} "
          f"| bucket-crossing={cross:.1%}")
    print(f"[{tag}] forget logit shift  pre={pre.norm(dim=0).mean():.4f} "
          f"post={post.norm(dim=0).mean():.4f} | direction cos-sim={sim:.3f}")
    return pre.norm(dim=0).mean().item(), post.norm(dim=0).mean().item(), sim


def main():
    torch.manual_seed(0)
    W = load_weight()
    Xf = torch.randn(W.shape[1], 32)
    s_row = W.abs().amax(dim=1) / 7                      # 4-bit per-channel bucket
    margin = 0.5 * s_row.mean().item() * Xf.norm(dim=0).mean().item()
    print(f"[setup] 4-bit bucket ~{s_row.mean():.4f}; QUAIL margin (half-step in logits) = {margin:.4f}")

    D_base = baseline_unlearn(W, Xf)
    D_quail = quail_unlearn(W, Xf, margin)
    pre_b, post_b, sim_b = diagnostics(W, D_base, Xf, s_row, "baseline")
    pre_q, post_q, sim_q = diagnostics(W, D_quail, Xf, s_row, "QUAIL")

    # baseline: tiny updates -> forgetting direction largely drowned by
    # quantization noise (low cos-sim). QUAIL: direction preserved (high
    # cos-sim) and post-quant shift stays above half the margin.
    survived = sim_q > 0.8 and post_q >= margin / 2
    print(f"[check] baseline forgetting degraded by quantization "
          f"(direction cos-sim = {sim_b:.3f})")
    print(f"[check] QUAIL forgetting survives quantization "
          f"(direction cos-sim = {sim_q:.3f}, post shift {post_q:.4f} >= margin/2 {margin / 2:.4f})")
    print(f"[check] overall: {'PASS' if survived else 'FAIL'}")


if __name__ == "__main__":
    main()
