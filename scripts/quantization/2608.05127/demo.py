#!/usr/bin/env python3
"""
SSTQ: Privacy-Preserving Vector Quantization via Subsampled Stochastic TurboQuant
论文: arXiv:2608.05127 | 目标模型: Qwen3-0.6B

三大组件 (MSE 由 O(4^b) 降至 O(2^b)):
1. 过完备紧框架/随机旋转 R (R^T R=(N/d)I): y=Rx 均衡能量
2. 坐标子采样: 抽 s 个坐标, 单坐标 = ceil(log2 N)+b 比特
3. 隐私感知一维量化: 随机无偏一比特符号 E[Q(y)]=y + Flat RR / Laplace (eps-LDP)
单客户端估计无偏高方差, 服务端聚合 K 客户端使噪声以 O(1/K) 衰减。

运行: python3 demo.py
"""

import sys
import math
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from quantization_toolkit import (
    load_model_or_mock,
    quantization_error_metrics,
)

torch.manual_seed(0)


# --- 1. 过完备紧框架 / 随机旋转 ---
def random_tight_frame(d: int, n: int) -> torch.Tensor:
    """生成 N x d 随机紧框架 R (R^T R=(N/d)I); N=d 时为正交随机旋转。"""
    Q, _ = torch.linalg.qr(torch.randn(n, d))  # Q: [N, d], Q^T Q = I_d
    return math.sqrt(n / d) * Q                 # [N, d], R^T R = (N/d) I_d


# --- 2. 坐标子采样 ---
def coordinate_subsample(y: torch.Tensor, s: int):
    """从 N 个坐标中无放回抽取 s 个, 返回 (idx[s], y_sub[s])。"""
    perm = torch.randperm(y.shape[0])
    return perm[:s], y[perm[:s]]


# --- 3. 随机一比特符号量化 (无偏) ---
def stochastic_sign_quantize(y: torch.Tensor) -> torch.Tensor:
    """一比特随机符号量化, |y|<=1, E[Q(y)]=y; Q=+1 以概率 (1+y)/2。"""
    u = torch.rand_like(y)
    return torch.where(u < (1.0 + y) / 2.0, torch.ones_like(y), -torch.ones_like(y))


# --- 4. 隐私机制: Flat RR 与 Metric-Aware Laplace ---
def flat_randomized_response(signs: torch.Tensor, eps: float) -> torch.Tensor:
    """二值随机化响应 (eps-LDP): 以概率 e^eps/(e^eps+1) 上报真值, 否则随机。"""
    p_true = math.exp(eps) / (math.exp(eps) + 1.0)
    u, v = torch.rand_like(signs), torch.rand_like(signs)
    rand_sign = torch.where(v < 0.5, torch.ones_like(signs), -torch.ones_like(signs))
    return torch.where(u < p_true, signs, rand_sign)
def rr_debias_factor(eps: float) -> float:
    """RR 衰减因子 a=(e^eps-1)/(e^eps+1), 去偏时除以 a。"""
    return (math.exp(eps) - 1.0) / (math.exp(eps) + 1.0)
def metric_aware_laplace(y: torch.Tensor, eps: float) -> torch.Tensor:
    """度量感知拉普拉斯: y+Lap(0,2/eps), 敏感度 2, eps-LDP, 无偏。"""
    return y + torch.distributions.Laplace(0.0, 2.0 / max(eps, 1e-6)).sample(y.shape)


# --- 5. SSTQ 量化器 (旋转 + 子采样 + 随机符号 + LDP) ---
class SSTQQuantizer:
    """SSTQ: encode 传 idx+priv_signs(+norm), decode 紧框架伪逆重构 (无偏)。"""

    def __init__(self, frame_size: int = None, subsample: int = 8,
                 eps: float = 1.0, mechanism: str = "rr"):
        self.frame_size = frame_size
        self.subsample = subsample
        self.eps = eps
        self.mechanism = mechanism
        self._R_cache = {}      # 缓存旋转矩阵, 避免重复 QR

    def _frame(self, d: int):
        N = self.frame_size if self.frame_size is not None else d
        if (d, N) not in self._R_cache:
            self._R_cache[(d, N)] = (random_tight_frame(d, N), N)
        return self._R_cache[(d, N)]

    def encode(self, x: torch.Tensor):
        """编码权重组 x:[d] -> (idx[s], priv[s], norm, R, N)。"""
        d = x.shape[0]
        R, N = self._frame(d)
        norm = x.norm().clamp_min(1e-8)
        u = x / norm                            # 单位向量
        y = R @ u                               # [N], ||y||^2 = N/d
        yb = y * math.sqrt(d / N)              # 归一化使 |yb_j| <= 1
        idx, yb_sub = coordinate_subsample(yb, self.subsample)
        signs = stochastic_sign_quantize(yb_sub)   # 无偏一比特
        priv = (flat_randomized_response(signs, self.eps) if self.mechanism == "rr"
                else metric_aware_laplace(signs, self.eps))
        return idx, priv, norm, R, N

    def decode(self, idx, priv, norm, R, N) -> torch.Tensor:
        """服务端重构 x_hat:[d] (无偏)。"""
        d, s = R.shape[1], idx.shape[0]
        yb_hat = torch.zeros(N, device=priv.device)
        if self.mechanism == "rr":
            a = rr_debias_factor(self.eps)
            yb_hat[idx] = (N / s) * (1.0 / a if a > 1e-6 else 1.0) * priv
        else:
            yb_hat[idx] = (N / s) * priv           # 拉普拉斯本身无偏
        y_hat = yb_hat * math.sqrt(N / d)          # 还原 y 尺度
        u_hat = (d / N) * (R.t() @ y_hat)          # 紧框架伪逆
        return norm * u_hat

    def bits_per_vector(self, d: int) -> int:
        """每向量通信比特 (不含 1 个共享 norm)。"""
        N = self.frame_size if self.frame_size is not None else d
        return self.subsample * (math.ceil(math.log2(N)) + 1)


# --- 6. 联邦聚合 ---
def federated_aggregate(quantizer: SSTQQuantizer, x: torch.Tensor,
                        k_clients: int) -> torch.Tensor:
    """K 个客户端各自 SSTQ 编码, 服务端平均聚合 -> 无偏, 方差随 K 下降。"""
    acc = torch.zeros_like(x)
    for _ in range(k_clients):
        acc += quantizer.decode(*quantizer.encode(x))
    return acc / k_clients


# --- 7. 辅助: 收集权重分组与能量分散度诊断 ---
def collect_weight_groups(model: nn.Module, group_size: int = 64,
                          max_groups: int = 256) -> torch.Tensor:
    """从模型 Linear 层权重中收集 group_size 大小的分组, 返回 [G, d]。"""
    chunks, total = [], 0
    for _, module in model.named_modules():
        if isinstance(module, nn.Linear):
            w = module.weight.data.flatten()
            n = (w.numel() // group_size) * group_size
            chunks.append(w[:n].reshape(-1, group_size))
            total += chunks[-1].shape[0]
            if total >= max_groups:
                break
    return torch.cat(chunks, dim=0)[:max_groups]

def energy_spread(groups: torch.Tensor, d: int) -> dict:
    """统计单位向量坐标绝对值的最大值/均值, 评估能量集中度。"""
    u = groups / groups.norm(dim=1, keepdim=True).clamp_min(1e-8)
    abs_u = u.abs()
    mx = abs_u.max(dim=1).values.mean().item()
    mn = abs_u.mean().item()
    return {"max_coord_mean": mx, "coord_mean": mn, "concentration": mx / max(mn, 1e-8)}


# --- 8. 主流程 ---
def main():
    print("=" * 72)
    print("SSTQ: Privacy-Preserving VQ via Subsampled Stochastic TurboQuant")
    print("论文: arXiv:2608.05127 | 目标模型: Qwen3-0.6B")
    print("=" * 72)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型 (真实 Qwen3-0.6B 或 Mock)
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 收集权重分组
    d = 64
    print(f"\n[2] 收集权重分组 (group_size={d})...")
    groups = collect_weight_groups(model, group_size=d, max_groups=256)
    print(f"    分组数: {groups.shape[0]}, 维度: {groups.shape[1]}")

    # 3. 能量分散度诊断: 旋转 (紧框架) 把离群大值能量均匀分散到各坐标
    print("\n[3] 能量分散度诊断 (旋转分散离群大值)...")
    before = energy_spread(groups, d)
    R = random_tight_frame(d, d)
    u = groups / groups.norm(dim=1, keepdim=True).clamp_min(1e-8)
    yb = u @ R.t()                                # 旋转后单位向量坐标
    after_max = yb.abs().max(dim=1).values.mean().item()
    after_mean = yb.abs().mean().item()
    print(f"    旋转前: max|coord|={before['max_coord_mean']:.4f}, "
          f"集中度={before['concentration']:.2f}")
    print(f"    旋转后: max|coord|={after_max:.4f}, "
          f"集中度={after_max / max(after_mean, 1e-8):.2f}")

    # 4. 联邦聚合: K 客户端各自 SSTQ 编码, 服务端平均 -> 噪声以 O(1/K) 衰减
    s, eps = 16, 3.0
    sstq = SSTQQuantizer(frame_size=d, subsample=s, eps=eps, mechanism="rr")
    bits = sstq.bits_per_vector(d)
    print(f"\n[4] 联邦聚合 (K 客户端平均, s={s}, eps={eps}, {bits}/客户端比特)")
    x0 = groups[0]
    print(f"    {'K':<8}{'MSE':<14}{'cosine':<12}{'相对误差':<12}")
    print(f"    {'-' * 46}")
    for k in [1, 5, 20, 100, 500, 2000]:
        xh = federated_aggregate(sstq, x0, k)
        m = quantization_error_metrics(x0, xh)
        rel = (xh - x0).norm().item() / x0.norm().clamp_min(1e-8).item()
        print(f"    {k:<8}{m['mse']:<14.6f}{m['cosine_similarity']:<12.4f}{rel:<12.4f}")
    print("    (K 增大 -> MSE ~ 1/K 下降, cosine -> 1: 单客户端无偏高方差, 聚合去噪)")

    # 5. 无偏性验证: 低维合成向量 + 大 K (高维方差大, 用 d=8 验证 E[x_hat]->x)
    print("\n[5] 无偏性验证 (合成 d=8 向量, K=20000 客户端聚合)...")
    q_small = SSTQQuantizer(frame_size=8, subsample=8, eps=4.0, mechanism="rr")
    x_s = torch.randn(8)
    x_s = x_s / x_s.norm() * 0.5
    xh_s = federated_aggregate(q_small, x_s, 20000)
    rel_bias = (xh_s - x_s).norm().item() / x_s.norm().clamp_min(1e-8).item()
    print(f"    ||x_hat-x||/||x|| = {rel_bias:.4f} (趋近 0 => 无偏估计)")

    # 6. 隐私-效用权衡: K=500, 16 组平均 cosine 随 eps 变化 (RR vs Laplace)
    print("\n[6] 隐私-效用权衡 (K=500 客户端, 16 组平均 cosine, eps 越小越隐私)")
    print(f"    {'eps':<6}{'机制':<10}{'平均 cosine':<14}")
    print(f"    {'-' * 30}")
    nv = min(16, groups.shape[0])
    for eps_v in [4.0, 2.0, 1.0, 0.5]:
        for mech, mech_name in [("rr", "RR"), ("laplace", "Laplace")]:
            q = SSTQQuantizer(frame_size=d, subsample=s, eps=eps_v, mechanism=mech)
            cos_sum = sum(F.cosine_similarity(groups[i].flatten().unsqueeze(0),
                federated_aggregate(q, groups[i], 500).flatten().unsqueeze(0)
                ).item() for i in range(nv))
            print(f"    {eps_v:<6}{mech_name:<10}{cos_sum / nv:<14.4f}")

    # 7. 权重压缩应用: 首层 Linear 逐行分组, 联邦 SSTQ 传输并聚合重构
    print("\n[7] 权重压缩应用 (首层 Linear 前 64 行, K=200 客户端/组)")
    sstq = SSTQQuantizer(frame_size=d, subsample=s, eps=eps, mechanism="rr")
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            w = module.weight.data
            n_rows = min(64, w.shape[0])
            w_sub, w_hat = w[:n_rows], torch.zeros_like(w[:n_rows])
            for r in range(n_rows):
                row = w_sub[r]
                ng = row.numel() // d
                row_hat = row.clone()
                for g in range(ng):
                    seg = row[g * d:(g + 1) * d]
                    row_hat[g * d:(g + 1) * d] = federated_aggregate(sstq, seg, 200)
                w_hat[r] = row_hat
            m = quantization_error_metrics(w_sub, w_hat)
            short = name[-30:] if len(name) > 30 else name
            print(f"    {short:<30} MSE={m['mse']:.6f} cos={m['cosine_similarity']:.4f} "
                  f"bits/client={bits}")
            break

    print("\n" + "=" * 72)
    print("SSTQ 验证完成。核心结论: 随机旋转+子采样+随机无偏一比特量化+LDP,")
    print("每客户端仅 ceil(log2 N)+b 比特即实现 eps-LDP; 单客户端无偏高方差,")
    print("聚合 K 客户端使 MSE 以 O(1/K) 衰减 (论文 O(4^b)->O(2^b) 改进)。")
    print("=" * 72)


if __name__ == "__main__":
    main()
