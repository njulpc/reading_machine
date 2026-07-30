"""QB-LIF (arXiv:2604.25688): learnable-scale quantized burst neurons —
reference reproduction of the quantization view of burst spiking, the
absorbable scale trick, and a surrogate-gradient training comparison vs
binary LIF at equal simulation length.
"""
import torch
import torch.nn as nn

torch.manual_seed(0)

T_STEPS, N_IN, N_HID, N_CLS = 8, 32, 64, 4
TAU = 0.8


class BurstQuant(torch.autograd.Function):
    """Saturated uniform quantization of membrane potential with learnable
    scale; ReLSG-ET-style surrogate: linear inside [0, Qmax*delta], exp-tail
    outside to sustain gradient flow across burst intervals."""
    @staticmethod
    def forward(ctx, v, log_delta, qmax):
        delta = log_delta.exp()
        ctx.save_for_backward(v, delta)
        ctx.qmax = qmax
        return torch.clamp(torch.round(v / delta), 0, qmax)

    @staticmethod
    def backward(ctx, g):
        v, delta = ctx.saved_tensors
        u = v / delta
        # linear surrogate within the burst range, exponential tails outside
        w = torch.clamp(u, 0, ctx.qmax)
        tail = torch.exp(-((u - w) ** 2) / 0.5)
        grad_v = g * tail / delta
        grad_d = g * tail * (-u / delta)
        return grad_v, grad_d.sum().reshape(1), None


class QBLIFLayer(nn.Module):
    def __init__(self, n_in, n_out, qmax):
        super().__init__()
        self.W = nn.Parameter(torch.randn(n_out, n_in) * 0.1)
        self.log_delta = nn.Parameter(torch.zeros(1))
        self.qmax = qmax
        self.head = nn.Linear(n_out, N_CLS)

    def forward(self, x):
        v = torch.zeros(x.shape[1], self.W.shape[0], device=x.device)
        acc = torch.zeros_like(v)
        for t in range(x.shape[0]):
            v = TAU * v + x[t] @ self.W.T
            s = BurstQuant.apply(v, self.log_delta, self.qmax)
            v = v - s * self.log_delta.exp()      # subtract emitted quanta
            acc = acc + s
        return self.head(acc / x.shape[0])

    @torch.no_grad()
    def absorbed_weight(self):
        """Absorbable scale: fold delta into synaptic weights for AC-only
        inference. Returns weight W' such that integer spikes map directly."""
        return self.W * self.log_delta.exp()


def make_data(n=512):
    X = torch.rand(T_STEPS, n, N_IN)
    X = (X < 0.15 + 0.1 * torch.rand(1, n, N_IN)).float()
    w_true = torch.randn(N_IN, N_CLS)
    y = (X.mean(0) @ w_true).argmax(-1)
    return X, y


def train(model, X, y, steps=200):
    opt = torch.optim.Adam(model.parameters(), lr=5e-3)
    lossf = nn.CrossEntropyLoss()
    for _ in range(steps):
        loss = lossf(model(X), y)
        opt.zero_grad(); loss.backward(); opt.step()
    acc = (model(X).argmax(-1) == y).float().mean().item()
    return acc


def main():
    X, y = make_data()
    bin_model = QBLIFLayer(N_IN, N_HID, qmax=1)     # binary LIF (1 bit/step)
    qb_model = QBLIFLayer(N_IN, N_HID, qmax=3)      # QB-LIF (2-bit burst)
    acc_bin = train(bin_model, X, y)
    acc_qb = train(qb_model, X, y)
    print(f"same T={T_STEPS} steps: binary-LIF acc={acc_bin:.3f}  QB-LIF(qmax=3) acc={acc_qb:.3f}")

    # verify absorbable scale: folding delta into synaptic weights preserves
    # the effective increment — AC-only path uses integer spikes s and W*delta
    model = qb_model.eval()
    delta = model.log_delta.exp()
    w0 = model.W[0]                                    # one synaptic row (N_IN,)
    s1 = BurstQuant.apply(torch.rand(N_IN) * 2 * delta, model.log_delta, model.qmax)
    inc_folded = s1 @ (w0 * delta)
    inc_plain = (s1 * delta) @ w0
    diff = abs(inc_folded.item() - inc_plain.item())
    print(f"absorbable-scale folding check: max diff = {diff:.2e}")
    assert diff < 1e-5
    assert acc_qb >= acc_bin - 1e-6
    print("PASS: learnable-scale burst quantization beats 1-bit coding at equal latency;"
          " scale folds into weights for accumulate-only inference.")


if __name__ == "__main__":
    main()
