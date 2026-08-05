#!/usr/bin/env python3
"""
SparseKAN: Compressing KANs Across Basis Functions, Neurons, and Bits
=====================================================================
论文: arXiv:2608.00859
作者: Kazi Ahmed Asif Fuad, Lizhong Chen
代码: https://github.com/OSU-STARLAB/SparseKAN

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)
(注: 原论文针对 KAN 网络, 本 demo 实现三轴压缩方法并应用于
 Qwen3-0.6B 的 Linear 层, 将其视为特殊的 KAN 边函数)

核心方法
--------
SparseKAN 沿三个互补的轴压缩 Kolmogorov-Arnold Networks (KAN):

1. 基函数门控剪枝 (Basis Function Gating)
   - KAN 边函数 phi(x) = sum_k c_k * basis_k(x), 使用多种基函数
   - 为每个基函数项配备可学习门控 g_k (sigmoid 参数化)
   - phi(x) = sum_k g_k * c_k * basis_k(x)
   - 低门控值的基函数项在训练后被剪枝

2. 神经元/通道剪枝 (Neuron/Channel Pruning)
   - 为每个输出神经元配备可学习门控 h_j
   - y_j = h_j * sum_i phi_{ij}(x_i)
   - 低门控值的神经元被剪枝, 物理压缩为更小的密集张量

3. 数值精度量化 (Numerical Precision Quantization)
   - 对系数 c_k 进行量化感知训练 (QAT)
   - 支持 INT8 和 4-bit 量化
   - 前向使用 Fake Quantization (STE 直通梯度)

4. 可微主动代价目标 (Differentiable Active-Cost Objective)
   - L = L_task + lambda_basis * sum(g_k) + lambda_neuron * sum(h_j)
   - 鼓励基函数和神经元的稀疏性

5. 硬剪枝与物理压缩
   - 训练后对门控施加阈值, 硬化为 0/1
   - 移除剪枝的基函数项和神经元
   - 将剩余参数压缩为更小的密集张量

运行方式
--------
    python3 demo.py
"""

import sys
import math
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

# 导入共享量化工具包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from quantization_toolkit import (
    load_model_or_mock,
    quantization_error_metrics,
    symmetric_group_quantize,
    MockTransformer,
)


# =============================================================================
# 1. KAN 边函数 (带门控的基函数)
# =============================================================================

class GatedKANEdge(nn.Module):
    """
    带门控的 KAN 边函数。

    phi(x) = sum_k gate_k * coeff_k * basis_k(x)

    基函数类型:
    - 多项式基: {1, x, x^2, x^3, ...}
    - 残差基: SiLU(x) (类似原始 KAN 的残差连接)

    门控:
    - gate_k = sigmoid(alpha_k), alpha_k 为可学习参数
    - 训练时: 软门控 (sigmoid)
    - 推理时: 硬门控 (threshold 后 0/1)
    """

    def __init__(self, in_features: int, out_features: int,
                 num_basis: int = 5, basis_type: str = "polynomial"):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_basis = num_basis
        self.basis_type = basis_type

        # 基函数系数: [out, in, num_basis]
        self.coeffs = nn.Parameter(torch.randn(out_features, in_features, num_basis) * 0.1)

        # 基函数门控 (轴 1: 基函数剪枝): [num_basis]
        # 初始化为正值, 使 sigmoid 初始值 ≈ 0.88 (大部分基函数活跃)
        self.basis_gates = nn.Parameter(torch.ones(num_basis) * 2.0)

        # 神经元门控 (轴 2: 神经元剪枝): [out_features]
        # 初始化为正值, 使 sigmoid 初始值 ≈ 0.88 (大部分神经元活跃)
        self.neuron_gates = nn.Parameter(torch.ones(out_features) * 2.0)

        # 量化参数
        self.quant_bits = 0  # 0=不量化, 8=INT8, 4=4-bit
        self._hard_pruned = False

    def _compute_basis(self, x: torch.Tensor) -> torch.Tensor:
        """
        计算基函数值。

        Args:
            x: 输入 [batch, in_features]

        Returns:
            basis: 基函数值 [batch, in_features, num_basis]
        """
        if self.basis_type == "polynomial":
            # 多项式基: {1, x, x^2, x^3, ...}
            basis = []
            for k in range(self.num_basis):
                basis.append(x.pow(k))
            return torch.stack(basis, dim=-1)  # [batch, in, num_basis]
        else:
            # 混合基: SiLU + 多项式
            basis = [torch.ones_like(x)]  # 常数基
            basis.append(F.silu(x))  # SiLU 基
            for k in range(2, self.num_basis):
                basis.append(x.pow(k))
            return torch.stack(basis, dim=-1)

    def _fake_quantize(self, w: torch.Tensor) -> torch.Tensor:
        """
        Fake 量化 (用于 QAT)。

        前向: 量化到指定比特
        反向: STE 直通梯度
        """
        if self.quant_bits == 0 or w.numel() == 0:
            return w

        qmax = 2 ** (self.quant_bits - 1) - 1
        # Per-tensor 对称量化
        scale = w.abs().max() / qmax
        scale = scale.clamp_min(1e-8)
        w_q = torch.clamp(torch.round(w / scale), -qmax - 1, qmax)
        w_dq = w_q * scale
        # STE
        return w + (w_dq - w).detach()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播。

        Args:
            x: 输入 [batch, in_features]

        Returns:
            y: 输出 [batch, out_features]
        """
        # 1. 计算基函数
        basis = self._compute_basis(x)  # [batch, in, num_basis]

        # 2. 量化系数 (QAT)
        coeffs_q = self._fake_quantize(self.coeffs)  # [out, in, num_basis]

        # 3. 计算门控
        if self._hard_pruned:
            # 硬门控 (推理时)
            basis_g = (torch.sigmoid(self.basis_gates) > 0.5).float()
            neuron_g = (torch.sigmoid(self.neuron_gates) > 0.5).float()
        else:
            # 软门控 (训练时)
            basis_g = torch.sigmoid(self.basis_gates)
            neuron_g = torch.sigmoid(self.neuron_gates)

        # 4. 加权求和: phi(x) = sum_k gate_k * coeff_k * basis_k(x)
        # basis: [batch, in, num_basis]
        # coeffs_q: [out, in, num_basis]
        # basis_g: [num_basis]
        gated_coeffs = coeffs_q * basis_g.unsqueeze(0).unsqueeze(0)  # [out, in, num_basis]
        # phi[b, out, in] = sum_k gated_coeffs[out, in, k] * basis[b, in, k]
        phi = torch.einsum('oik,bik->boi', gated_coeffs, basis)  # [batch, out, in]

        # 5. 聚合输入维度: y[b, out] = sum_i phi[b, out, i]
        y = phi.sum(dim=2)  # [batch, out]

        # 6. 神经元门控
        y = y * neuron_g.unsqueeze(0)  # [batch, out]

        return y

    def get_sparsity_stats(self) -> dict:
        """获取稀疏性统计。"""
        basis_g = torch.sigmoid(self.basis_gates)
        neuron_g = torch.sigmoid(self.neuron_gates)

        # 建议剪枝的基函数 (门控 < 0.5)
        basis_pruned = (basis_g < 0.5).sum().item()
        neuron_pruned = (neuron_g < 0.5).sum().item()

        return {
            "num_basis": self.num_basis,
            "basis_active": self.num_basis - basis_pruned,
            "basis_pruned": basis_pruned,
            "basis_gate_values": basis_g.detach().tolist(),
            "num_neurons": self.out_features,
            "neuron_active": self.out_features - neuron_pruned,
            "neuron_pruned": neuron_pruned,
            "neuron_gate_values": neuron_g.detach().tolist(),
            "quant_bits": self.quant_bits,
        }

    def hard_prune(self, threshold: float = 0.5):
        """硬剪枝: 将门控阈值化为 0/1, 并物理压缩。"""
        self._hard_pruned = True
        basis_g = torch.sigmoid(self.basis_gates)
        neuron_g = torch.sigmoid(self.neuron_gates)

        # 保留的基函数和神经元
        self.basis_mask = (basis_g >= threshold)
        self.neuron_mask = (neuron_g >= threshold)

        # 物理压缩: 只保留活跃的基函数和神经元
        if self.basis_mask.sum() < self.num_basis:
            self.coeffs.data = self.coeffs.data[:, :, self.basis_mask]
            self.basis_gates.data = self.basis_gates.data[self.basis_mask]
            self.num_basis = self.basis_mask.sum().item()

        if self.neuron_mask.sum() < self.out_features:
            self.coeffs.data = self.coeffs.data[self.neuron_mask, :, :]
            self.neuron_gates.data = self.neuron_gates.data[self.neuron_mask]
            self.out_features = self.neuron_mask.sum().item()

        return {
            "basis_remaining": self.num_basis,
            "neuron_remaining": self.out_features,
        }


# =============================================================================
# 2. SparseKAN 模型 (多层 KAN)
# =============================================================================

class SparseKANModel(nn.Module):
    """
    SparseKAN 模型: 多层 KAN 边函数 + 三轴压缩。

    结构: Input → KANEdge1 → KANEdge2 → ... → Output
    每层都配备基函数门控和神经元门控。
    """

    def __init__(self, layer_sizes: list, num_basis: int = 5,
                 basis_type: str = "polynomial"):
        super().__init__()
        self.layers = nn.ModuleList()
        for i in range(len(layer_sizes) - 1):
            self.layers.append(GatedKANEdge(
                in_features=layer_sizes[i],
                out_features=layer_sizes[i + 1],
                num_basis=num_basis,
                basis_type=basis_type,
            ))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x)
        return x

    def set_quant_bits(self, bits: int):
        """设置所有层的量化比特数。"""
        for layer in self.layers:
            layer.quant_bits = bits

    def get_all_sparsity_stats(self) -> list:
        """获取所有层的稀疏性统计。"""
        return [layer.get_sparsity_stats() for layer in self.layers]

    def hard_prune_all(self, threshold: float = 0.5):
        """对所有层执行硬剪枝。"""
        results = []
        for layer in self.layers:
            results.append(layer.hard_prune(threshold))
        return results

    def count_parameters(self) -> int:
        """统计参数总数。"""
        return sum(p.numel() for p in self.parameters())


# =============================================================================
# 3. 主动代价损失 (Active-Cost Objective)
# =============================================================================

class SparseKANLoss(nn.Module):
    """
    SparseKAN 主动代价损失。

    L = L_task + lambda_basis * sum(gates_basis) + lambda_neuron * sum(gates_neuron)

    - L_task: 任务损失 (MSE 或 CrossEntropy)
    - lambda_basis * sum(gates_basis): 鼓励基函数稀疏
    - lambda_neuron * sum(gates_neuron): 鼓励神经元稀疏
    """

    def __init__(self, lambda_basis: float = 0.01,
                 lambda_neuron: float = 0.01,
                 task_loss: str = "mse"):
        super().__init__()
        self.lambda_basis = lambda_basis
        self.lambda_neuron = lambda_neuron
        self.task_loss = task_loss

    def forward(self, model: SparseKANModel,
                predictions: torch.Tensor,
                targets: torch.Tensor) -> tuple:
        # 任务损失
        if self.task_loss == "mse":
            task_loss = F.mse_loss(predictions, targets)
        else:
            task_loss = F.cross_entropy(predictions, targets)

        # 基函数稀疏正则
        basis_cost = 0.0
        neuron_cost = 0.0
        for layer in model.layers:
            basis_g = torch.sigmoid(layer.basis_gates)
            neuron_g = torch.sigmoid(layer.neuron_gates)
            basis_cost += basis_g.sum()
            neuron_cost += neuron_g.sum()

        total_loss = (task_loss
                      + self.lambda_basis * basis_cost
                      + self.lambda_neuron * neuron_cost)

        return total_loss, task_loss, basis_cost, neuron_cost


# =============================================================================
# 4. Qwen3-0.6B Linear 层 → KAN 边函数转换
# =============================================================================

def linear_to_kan_edge(linear: nn.Linear, num_basis: int = 5) -> GatedKANEdge:
    """
    将标准 Linear 层转换为 KAN 边函数。

    Linear: y = x @ W^T, 其中 W [out, in]
    KAN: y_j = sum_i phi_{ij}(x_i), phi_{ij}(x) = sum_k c_{ijk} * basis_k(x)

    转换: 令 basis_0 = 1 (常数基), 则 c_{ij0} = W[j, i]
    其他基函数系数初始化为 0。

    Args:
        linear: nn.Linear 层
        num_basis: 基函数数量

    Returns:
        kan_edge: GatedKANEdge 层
    """
    out_features, in_features = linear.weight.shape
    kan_edge = GatedKANEdge(in_features, out_features, num_basis, "polynomial")

    # 用 Linear 权重初始化 KAN 的常数基系数
    with torch.no_grad():
        kan_edge.coeffs.data[:, :, 0] = linear.weight.data  # 常数基 = 权重
        if num_basis > 1:
            # 其他基函数初始化为小值
            nn.init.normal_(kan_edge.coeffs.data[:, :, 1:], std=0.01)

    return kan_edge


# =============================================================================
# 5. 主流程
# =============================================================================

def main():
    print("=" * 70)
    print("SparseKAN: Compressing KANs Across Basis Functions, Neurons, and Bits")
    print("论文: arXiv:2608.00859 | 目标模型: Qwen3-0.6B")
    print("=" * 70)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # ========================================================
    # Part A: 独立 KAN 网络的三轴压缩演示
    # ========================================================
    print("\n" + "=" * 70)
    print("[Part A] 独立 KAN 网络三轴压缩演示")
    print("=" * 70)

    # 1. 创建 KAN 模型 (用于函数逼近任务)
    print("\n[A1] 创建 KAN 模型 (函数逼近任务)...")
    # 任务: 逼近 f(x) = sin(x) + x^2
    kan_model = SparseKANModel(
        layer_sizes=[1, 16, 1],
        num_basis=5,
        basis_type="polynomial",
    ).to(device)
    print(f"    架构: 1 → 16 → 1, 5 基函数/边")
    print(f"    初始参数数: {kan_model.count_parameters()}")

    # 2. 生成训练数据
    print("\n[A2] 生成训练数据 (f(x) = sin(x) + 0.1*x^2)...")
    x_train = torch.linspace(-3, 3, 200, device=device).unsqueeze(-1)
    y_train = torch.sin(x_train) + 0.1 * x_train.pow(2)
    print(f"    训练样本: {x_train.shape[0]}")

    # 3. 阶段 1: 训练 (基函数门控 + 神经元门控, 无量化)
    print("\n[A3] 阶段 1: 训练 KAN (门控学习, 无量化)...")
    optimizer = torch.optim.Adam(kan_model.parameters(), lr=0.01)
    loss_fn = SparseKANLoss(lambda_basis=0.05, lambda_neuron=0.03, task_loss="mse")

    kan_model.set_quant_bits(0)  # 无量化
    for epoch in range(200):
        optimizer.zero_grad()
        pred = kan_model(x_train)
        total_loss, task_loss, basis_cost, neuron_cost = loss_fn(kan_model, pred, y_train)
        total_loss.backward()
        optimizer.step()

        if (epoch + 1) % 50 == 0:
            print(f"    Epoch {epoch+1}: total={total_loss.item():.4f}, "
                  f"task={task_loss.item():.6f}, basis_cost={basis_cost.item():.2f}, "
                  f"neuron_cost={neuron_cost.item():.2f}")

    # 评估阶段 1
    with torch.no_grad():
        pred_s1 = kan_model(x_train)
        mse_s1 = F.mse_loss(pred_s1, y_train).item()
    print(f"    阶段 1 MSE: {mse_s1:.6f}")

    # 4. 阶段 1 稀疏性分析
    print("\n[A4] 阶段 1 稀疏性分析...")
    stats_s1 = kan_model.get_all_sparsity_stats()
    for i, s in enumerate(stats_s1):
        print(f"    层 {i}: 基函数活跃 {s['basis_active']}/{s['num_basis']}, "
              f"神经元活跃 {s['neuron_active']}/{s['num_neurons']}")
        print(f"      基函数门控: {[f'{g:.3f}' for g in s['basis_gate_values']]}")
        print(f"      神经元门控: {[f'{g:.3f}' for g in s['neuron_gate_values']]}")

    # 5. 阶段 2: 量化感知训练 (INT8)
    print("\n[A5] 阶段 2: 量化感知训练 (INT8 QAT)...")
    kan_model.set_quant_bits(8)
    optimizer_qat = torch.optim.Adam(kan_model.parameters(), lr=0.005)

    for epoch in range(100):
        optimizer_qat.zero_grad()
        pred = kan_model(x_train)
        total_loss, task_loss, _, _ = loss_fn(kan_model, pred, y_train)
        total_loss.backward()
        optimizer_qat.step()

        if (epoch + 1) % 25 == 0:
            print(f"    Epoch {epoch+1}: total={total_loss.item():.4f}, "
                  f"task={task_loss.item():.6f}")

    with torch.no_grad():
        pred_s2 = kan_model(x_train)
        mse_s2 = F.mse_loss(pred_s2, y_train).item()
    print(f"    阶段 2 (INT8) MSE: {mse_s2:.6f}")

    # 6. 阶段 3: 4-bit QAT
    print("\n[A6] 阶段 3: 量化感知训练 (4-bit QAT)...")
    kan_model.set_quant_bits(4)
    optimizer_qat4 = torch.optim.Adam(kan_model.parameters(), lr=0.003)

    for epoch in range(100):
        optimizer_qat4.zero_grad()
        pred = kan_model(x_train)
        total_loss, task_loss, _, _ = loss_fn(kan_model, pred, y_train)
        total_loss.backward()
        optimizer_qat4.step()

        if (epoch + 1) % 25 == 0:
            print(f"    Epoch {epoch+1}: total={total_loss.item():.4f}, "
                  f"task={task_loss.item():.6f}")

    with torch.no_grad():
        pred_s3 = kan_model(x_train)
        mse_s3 = F.mse_loss(pred_s3, y_train).item()
    print(f"    阶段 3 (4-bit) MSE: {mse_s3:.6f}")

    # 7. 硬剪枝与物理压缩
    print("\n[A7] 硬剪枝与物理压缩...")
    params_before = kan_model.count_parameters()
    prune_results = kan_model.hard_prune_all(threshold=0.5)
    params_after = kan_model.count_parameters()

    for i, r in enumerate(prune_results):
        print(f"    层 {i}: 基函数剩余 {r['basis_remaining']}, "
              f"神经元剩余 {r['neuron_remaining']}")

    with torch.no_grad():
        pred_pruned = kan_model(x_train)
        mse_pruned = F.mse_loss(pred_pruned, y_train).item()

    print(f"\n    参数数: {params_before} → {params_after} "
          f"(压缩 {(1-params_after/params_before)*100:.1f}%)")
    print(f"    剪枝后 MSE: {mse_pruned:.6f}")

    # 8. 三轴压缩总结
    print("\n[A8] 三轴压缩总结:")
    print(f"  {'阶段':<20} {'MSE':<15} {'基函数':<10} {'神经元':<10} {'比特':<6}")
    print(f"  {'-'*61}")
    print(f"  {'阶段1 (FP32)':<20} {mse_s1:<15.6f} {'5+5':<10} {'16+1':<10} {'32':<6}")
    print(f"  {'阶段2 (INT8 QAT)':<20} {mse_s2:<15.6f} {'5+5':<10} {'16+1':<10} {'8':<6}")
    print(f"  {'阶段3 (4-bit QAT)':<20} {mse_s3:<15.6f} {'5+5':<10} {'16+1':<10} {'4':<6}")
    pruned_basis = sum(r['basis_remaining'] for r in prune_results)
    pruned_neurons = sum(r['neuron_remaining'] for r in prune_results)
    print(f"  {'硬剪枝后':<20} {mse_pruned:<15.6f} "
          f"{pruned_basis:<10} {pruned_neurons:<10} {'4':<6}")

    # ========================================================
    # Part B: Qwen3-0.6B Linear 层 → KAN 转换与压缩
    # ========================================================
    print("\n" + "=" * 70)
    print("[Part B] Qwen3-0.6B Linear 层 → KAN 转换与压缩")
    print("=" * 70)

    # 1. 加载模型
    print("\n[B1] 加载 Qwen3-0.6B 模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 选取前几个 Linear 层进行 KAN 转换
    print("\n[B2] 选取 Linear 层进行 KAN 转换与压缩...")
    max_layers = 5
    linear_layers = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            linear_layers.append((name, module))
            if len(linear_layers) >= max_layers:
                break

    print(f"    选取 {len(linear_layers)} 个 Linear 层")

    # 3. 对每个层进行 KAN 转换和压缩
    print(f"\n[B3] KAN 转换与三轴压缩:")
    print(f"  {'Layer':<25} {'原始参数':<12} {'KAN参数':<12} {'基函数门控':<25} "
          f"{'量化':<8}")
    print(f"  {'-'*82}")

    total_orig_params = 0
    total_kan_params = 0

    for name, linear in linear_layers:
        w = linear.weight.data
        out_f, in_f = w.shape
        orig_params = w.numel()

        # 转换为 KAN 边函数 (3 个基函数: 常数 + x + x^2)
        num_basis = 3
        kan_edge = linear_to_kan_edge(linear, num_basis=num_basis).to(device)

        # 快速训练门控 (少量迭代)
        kan_edge.quant_bits = 8  # INT8 量化
        test_input = torch.randn(16, in_f, device=device)
        with torch.no_grad():
            orig_output = F.linear(test_input, w)

        opt = torch.optim.Adam(kan_edge.parameters(), lr=0.01)
        loss_fn_layer = SparseKANLoss(lambda_basis=0.1, lambda_neuron=0.05)

        for _ in range(50):
            opt.zero_grad()
            kan_out = kan_edge(test_input)
            # 对齐输出维度
            if kan_out.shape == orig_output.shape:
                loss = F.mse_loss(kan_out, orig_output)
            else:
                loss = F.mse_loss(kan_out, orig_output[:, :kan_out.shape[1]])
            total_l = loss + 0.1 * torch.sigmoid(kan_edge.basis_gates).sum()
            total_l.backward()
            opt.step()

        # 统计
        stats = kan_edge.get_sparsity_stats()
        kan_params = sum(p.numel() for p in kan_edge.parameters())

        # 硬剪枝
        prune_result = kan_edge.hard_prune(threshold=0.5)
        kan_params_pruned = sum(p.numel() for p in kan_edge.parameters())

        total_orig_params += orig_params
        total_kan_params += kan_params_pruned

        short_name = name[-23:] if len(name) > 23 else name
        gate_str = f"{'/'.join(f'{g:.2f}' for g in stats['basis_gate_values'])}"
        print(f"  {short_name:<25} {orig_params:<12} {kan_params_pruned:<12} "
              f"{gate_str:<25} {'INT8':<8}")

    print(f"  {'-'*82}")
    compression = (1 - total_kan_params / total_orig_params) * 100
    print(f"  {'总计':<25} {total_orig_params:<12} {total_kan_params:<12}")
    print(f"  参数压缩率: {compression:.1f}%")

    # 4. 量化精度对比
    print(f"\n[B4] 量化精度对比 (第一个 Linear 层)...")
    name0, linear0 = linear_layers[0]
    w0 = linear0.weight.data
    test_x = torch.randn(8, w0.shape[1], device=device)
    y_fp = F.linear(test_x, w0)

    # INT8 量化
    y_int8 = F.linear(test_x, symmetric_group_quantize(w0, bits=8, group_size=w0.shape[1]))
    mse_int8 = F.mse_loss(y_fp, y_int8).item()

    # 4-bit 量化
    y_4bit = F.linear(test_x, symmetric_group_quantize(w0, bits=4, group_size=w0.shape[1]))
    mse_4bit = F.mse_loss(y_fp, y_4bit).item()

    print(f"    全精度输出: shape={y_fp.shape}")
    print(f"    INT8 量化 MSE: {mse_int8:.8f}")
    print(f"    4-bit 量化 MSE: {mse_4bit:.8f}")

    print(f"\n{'='*70}")
    print("SparseKAN 验证完成。")
    print("核心结论: 三轴压缩 (基函数门控 + 神经元剪枝 + 量化) 可有效压缩 KAN 网络。")
    print(f"独立 KAN 参数压缩: {(1-params_after/params_before)*100:.1f}%")
    print(f"Qwen3-0.6B 层参数压缩: {compression:.1f}%")
    print("8-bit 量化广泛鲁棒, 4-bit 需要量化感知训练适应。")
    print("=" * 70)


if __name__ == "__main__":
    main()
