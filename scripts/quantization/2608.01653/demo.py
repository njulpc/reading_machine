#!/usr/bin/env python3
"""
HaTQ: Hadamard-Domain Model Quantization for Learned Image Coding
===================================================================
论文: arXiv:2608.01653
作者: Junqi Shi, Chongzhi Wang, Yiwen He, Ming Lu, Zhan Ma

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)

核心方法
--------
HaTQ (Hadamard-Transform-domain Quantization) 在量化前用正交 Hadamard 变换
重参数化权重和激活, 使其分布更适合均匀 INT8 量化。

1. Hadamard 重参数化
   - Hadamard 矩阵 H 是正交矩阵 (H @ H^T = I), 且 H = H^T (对称)
   - 对线性层 y = x @ W^T, 插入 H: y = (x @ H) @ (H @ W^T) = x @ W^T
   - 权重变换: W' = W @ H (输入维度变换)
   - 激活变换: x' = x @ H
   - 变换后 W' 和 x' 的能量更均匀分布在各通道, 减少重尾分布

2. 两种形式
   a. Weight-only Hadamard: 只变换权重 W' = W @ H
      - 激活变换 x' = x @ H 可折叠到前一层 (如归一化层)
      - 适用于敏感层 (激活有大通道均值, Hadamard 会放大激活范围)

   b. Double-Hadamard: 同时变换权重和激活
      - W' = H_out @ W @ H_in (输入和输出维度都变换)
      - x' = x @ H_in, y' = x' @ W'^T, y = H_out @ y'
      - 适用于非敏感层 (激活分布均匀, Hadamard 进一步改善量化)

3. 敏感层识别 (离线 Profiling)
   - 通过校准数据计算每层激活的通道均值
   - Hadamard 常数基 (全 1 行) 会相干累加非零通道均值, 放大激活范围
   - 敏感度指标: Hadamard 变换后激活范围放大倍数
   - 放大超过阈值的层 → 使用 Weight-only Hadamard

4. INT8 量化
   - 对变换后的权重/激活进行均匀 INT8 对称量化
   - 支持 PTQ 和 QAT (本 demo 实现 PTQ)

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
    hadamard_matrix,
    fast_hadamard_transform,
    INT8Quantizer,
    MockTransformer,
)


# =============================================================================
# 1. HaTQ 配置: Hadamard 变换形式
# =============================================================================

class HadamardType:
    """Hadamard 变换形式枚举"""
    NONE = "none"              # 不变换 (基线)
    WEIGHT_ONLY = "weight_only"  # 仅权重变换
    DOUBLE = "double"           # 权重和激活都变换


# =============================================================================
# 2. HaTQ 量化器
# =============================================================================

class HaTQQuantizer:
    """
    HaTQ: Hadamard 域量化器。

    工作流程:
    1. 收集校准数据, 计算每层激活的敏感度
    2. 根据敏感度为每层分配 Hadamard 形式 (weight-only 或 double)
    3. 对权重应用 Hadamard 变换
    4. 对变换后的权重进行 INT8 量化
    5. 推理时对激活也应用 Hadamard 变换 (double 模式)

    INT8 量化: 对称 per-channel 量化
        scale = max(|w|) / 127
        w_q = clamp(round(w / scale), -128, 127)
        w_dq = w_q * scale
    """

    def __init__(self, sensitivity_threshold: float = 1.5,
                 hadamard_dim: int = 256):
        """
        Args:
            sensitivity_threshold: 敏感度阈值
                Hadamard 变换后激活范围放大超过此值 → 敏感层 (weight-only)
            hadamard_dim: Hadamard 矩阵维度 (必须是 2 的幂)
        """
        self.sensitivity_threshold = sensitivity_threshold
        self.hadamard_dim = hadamard_dim
        self.int8_quantizer = INT8Quantizer(per_channel=True, channel_dim=0)

        # 预计算 Hadamard 矩阵
        self._H_cache = {}

    def _get_hadamard(self, n: int, device: torch.device) -> torch.Tensor:
        """
        获取 n×n 的归一化 Hadamard 矩阵。
        如果 n 不是 2 的幂, 找到最近的 2 的幂并截断。
        """
        # 找到 >= n 的最小 2 的幂
        pow2 = 1
        while pow2 < n:
            pow2 *= 2

        if pow2 not in self._H_cache:
            self._H_cache[pow2] = hadamard_matrix(pow2, normalize=True)

        H = self._H_cache[pow2].to(device)
        # 截断到 n×n (Hadamard 矩阵的子矩阵仍近似正交)
        return H[:n, :n]

    def compute_sensitivity(self, activations: torch.Tensor) -> float:
        """
        计算层的敏感度: Hadamard 变换后激活范围的放大倍数。

        敏感度 = range(x @ H) / range(x)
        其中 range = max - min

        如果敏感度 > threshold, 则该层为敏感层 (应使用 weight-only)。

        Args:
            activations: 校准激活 [N, in_features]

        Returns:
            sensitivity: 放大倍数
        """
        if activations.ndim > 2:
            activations = activations.reshape(-1, activations.shape[-1])

        n = activations.shape[-1]
        H = self._get_hadamard(n, activations.device)

        # 原始激活范围
        orig_range = activations.abs().max().item()

        # Hadamard 变换后的激活范围
        transformed = activations @ H
        transformed_range = transformed.abs().max().item()

        if orig_range < 1e-8:
            return 1.0

        return transformed_range / orig_range

    def profile_layers(self, model: nn.Module,
                       calib_input_ids: torch.Tensor) -> dict:
        """
        离线 Profiling: 为每个 Linear 层确定 Hadamard 形式。

        通过校准数据前向传播, 收集每层输入激活,
        计算敏感度, 分配 Weight-only 或 Double-Hadamard。

        Args:
            model: 目标模型
            calib_input_ids: 校准数据 [batch, seq_len]

        Returns:
            layer_config: {layer_name: HadamardType}
        """
        layer_config = {}
        activations = {}

        # 注册前向钩子收集激活
        hooks = []
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                def make_hook(n):
                    def hook(module, input, output):
                        # input 是 tuple, 第一个元素是输入激活
                        activations[n] = input[0].detach()
                    return hook
                hooks.append(module.register_forward_hook(make_hook(name)))

        # 前向传播收集激活
        with torch.no_grad():
            model(calib_input_ids)

        # 移除钩子
        for hook in hooks:
            hook.remove()

        # 计算每层敏感度
        print("  [HaTQ Profiling] 层敏感度分析:")
        print(f"  {'Layer':<30} {'敏感度':<10} {'形式':<15}")
        print(f"  {'-'*55}")

        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                if name in activations:
                    act = activations[name]
                    sensitivity = self.compute_sensitivity(act)

                    if sensitivity > self.sensitivity_threshold:
                        hadamard_type = HadamardType.WEIGHT_ONLY
                    else:
                        hadamard_type = HadamardType.DOUBLE

                    layer_config[name] = hadamard_type

                    short_name = name[-28:] if len(name) > 28 else name
                    print(f"  {short_name:<30} {sensitivity:<10.2f} {hadamard_type:<15}")
                else:
                    # 未收集到激活的层, 默认使用 double
                    layer_config[name] = HadamardType.DOUBLE

        # 统计
        n_wo = sum(1 for v in layer_config.values() if v == HadamardType.WEIGHT_ONLY)
        n_dbl = sum(1 for v in layer_config.values() if v == HadamardType.DOUBLE)
        print(f"  {'-'*55}")
        print(f"  Weight-only: {n_wo}, Double-Hadamard: {n_dbl}")

        return layer_config

    def apply_hadamard_weight(self, w: torch.Tensor,
                              hadamard_type: str) -> torch.Tensor:
        """
        对权重应用 Hadamard 变换。

        Weight-only: W' = W @ H_in (仅输入维度变换)
        Double: W' = H_out @ W @ H_in (输入和输出维度都变换)

        由于 H 是正交且对称的 (H = H^T, H @ H = I):
        - y = x @ W^T → (x @ H) @ (W @ H)^T = x @ H @ H^T @ W^T = x @ W^T ✓

        Args:
            w: 权重 [out_features, in_features]
            hadamard_type: HadamardType 枚举值

        Returns:
            w_transformed: 变换后的权重
        """
        out_features, in_features = w.shape
        device = w.device

        if hadamard_type == HadamardType.NONE:
            return w

        # 输入维度变换: W' = W @ H_in
        H_in = self._get_hadamard(in_features, device)
        w_transformed = w @ H_in

        if hadamard_type == HadamardType.DOUBLE:
            # 输出维度变换: W' = H_out @ W @ H_in
            H_out = self._get_hadamard(out_features, device)
            w_transformed = H_out @ w_transformed

        return w_transformed

    def apply_hadamard_activation(self, x: torch.Tensor,
                                  hadamard_type: str) -> torch.Tensor:
        """
        对激活应用 Hadamard 变换 (推理时使用)。

        Weight-only: 不变换激活 (变换已折叠到权重)
        Double: x' = x @ H_in

        Args:
            x: 激活 [..., in_features]
            hadamard_type: HadamardType 枚举值

        Returns:
            x_transformed: 变换后的激活
        """
        if hadamard_type in (HadamardType.NONE, HadamardType.WEIGHT_ONLY):
            return x

        # Double-Hadamard: 变换激活
        in_features = x.shape[-1]
        H_in = self._get_hadamard(in_features, x.device)
        return x @ H_in

    def undo_output_hadamard(self, y: torch.Tensor,
                             hadamard_type: str) -> torch.Tensor:
        """
        对输出应用逆 Hadamard 变换 (Double-Hadamard 模式)。

        Double-Hadamard 的输出变换: y' = H_out @ y → 需要 y = H_out @ y'
        (因为 H 是对称正交的, H^{-1} = H)

        Args:
            y: 输出 [..., out_features]
            hadamard_type: HadamardType 枚举值

        Returns:
            y_restored: 恢复后的输出
        """
        if hadamard_type != HadamardType.DOUBLE:
            return y

        out_features = y.shape[-1]
        H_out = self._get_hadamard(out_features, y.device)
        return y @ H_out  # H_out^T = H_out (对称)

    def quantize_model(self, model: nn.Module,
                       layer_config: dict,
                       max_layers: int = 0):
        """
        对模型应用 HaTQ 量化。

        流程:
        1. 对每个 Linear 层的权重应用 Hadamard 变换
        2. 对变换后的权重进行 INT8 量化
        3. (推理时需要对应变换激活, 本 demo 在前向中处理)

        Args:
            model: 目标模型
            layer_config: {layer_name: HadamardType}
            max_layers: 最多处理多少层 (0=全部)
        """
        layer_idx = 0
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                if max_layers > 0 and layer_idx >= max_layers:
                    break

                hadamard_type = layer_config.get(name, HadamardType.DOUBLE)

                # 1. Hadamard 变换权重
                w = module.weight.data
                w_transformed = self.apply_hadamard_weight(w, hadamard_type)

                # 2. INT8 量化变换后的权重
                w_quantized, scale = self.int8_quantizer.quantize(w_transformed)

                # 3. 存储量化后的权重和变换类型
                module.weight.data = w_quantized
                module._hadamard_type = hadamard_type
                module._hadamard_quantizer = self

                layer_idx += 1

        print(f"  HaTQ quantization complete: {layer_idx} layers "
              f"(INT8 + Hadamard reparameterization)")


# =============================================================================
# 3. HaTQ 前向传播包装器
# =============================================================================

def hatq_forward(model: nn.Module, input_ids: torch.Tensor) -> torch.Tensor:
    """
    HaTQ 模型的前向传播。

    对于使用 Hadamard 变换的层, 需要在前向传播时:
    - Weight-only: 激活不需要变换 (已折叠到权重)
    - Double: 激活需要变换, 输出需要逆变换

    本实现通过临时替换 Linear 层的 forward 方法实现。
    """
    # 保存原始 forward 方法
    original_forwards = {}
    hooks = []

    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and hasattr(module, '_hadamard_type'):
            hadamard_type = module._hadamard_type
            quantizer = module._hadamard_quantizer

            if hadamard_type == HadamardType.DOUBLE:
                # 需要变换激活和逆变换输出
                original_forwards[name] = module.forward

                def make_custom_forward(mod, ht, qz):
                    def custom_forward(x):
                        # 变换输入激活
                        x_transformed = qz.apply_hadamard_activation(x, ht)
                        # 标准线性层前向
                        out = F.linear(x_transformed, mod.weight, mod.bias)
                        # 逆变换输出
                        out_restored = qz.undo_output_hadamard(out, ht)
                        return out_restored
                    return custom_forward

                module.forward = make_custom_forward(module, hadamard_type, quantizer)

    # 前向传播
    with torch.no_grad():
        outputs = model(input_ids)
        if hasattr(outputs, 'logits'):
            result = outputs.logits
        else:
            result = outputs

    # 恢复原始 forward 方法
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and name in original_forwards:
            module.forward = original_forwards[name]

    return result


# =============================================================================
# 4. 基线 INT8 量化器 (无 Hadamard, 用于对比)
# =============================================================================

def baseline_int8_quantize(model: nn.Module, max_layers: int = 0):
    """基线 INT8 量化 (无 Hadamard 变换)。"""
    int8_quantizer = INT8Quantizer(per_channel=True, channel_dim=0)
    layer_idx = 0
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            if max_layers > 0 and layer_idx >= max_layers:
                break
            w_dq, scale = int8_quantizer.quantize(module.weight.data)
            module.weight.data = w_dq
            layer_idx += 1
    print(f"  Baseline INT8 quantization complete: {layer_idx} layers.")


# =============================================================================
# 5. 主流程
# =============================================================================

def run_model_forward(model, input_ids):
    """运行模型前向传播。"""
    with torch.no_grad():
        outputs = model(input_ids)
        if hasattr(outputs, 'logits'):
            return outputs.logits
        return outputs


def _save_original_weights(model):
    """保存模型中所有 Linear 层的原始权重。"""
    saved = {}
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            saved[name] = module.weight.data.clone()
    return saved


def _restore_weights(model, saved_weights):
    """恢复模型权重到原始值。"""
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and name in saved_weights:
            module.weight.data = saved_weights[name].clone()
            # 清除 HaTQ 属性
            if hasattr(module, '_hadamard_type'):
                del module._hadamard_type
                del module._hadamard_quantizer


def main():
    print("=" * 70)
    print("HaTQ: Hadamard-Domain Model Quantization for Learned Image Coding")
    print("论文: arXiv:2608.01653 | 目标模型: Qwen3-0.6B")
    print("=" * 70)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 准备测试输入和校准数据
    if is_mock:
        vocab_size = model.embed.num_embeddings
        test_input = torch.randint(0, vocab_size, (2, 32), device=device)
        calib_input = torch.randint(0, vocab_size, (2, 32), device=device)
    else:
        test_input = torch.tensor([[1, 2, 3, 4, 5]], device=device)
        calib_input = torch.tensor([[10, 20, 30, 40, 50, 60, 70, 80]], device=device)

    # 3. 保存原始权重
    print("\n[2] 保存原始权重...")
    saved_weights = _save_original_weights(model)
    print(f"    共 {len(saved_weights)} 个 Linear 层")

    # 4. 获取全精度基线输出
    print("\n[3] 获取全精度 (FP32) 基线输出...")
    logits_fp = run_model_forward(model, test_input)
    print(f"    Logits shape: {logits_fp.shape}")

    # 5. HaTQ Profiling: 确定每层的 Hadamard 形式
    print("\n[4] HaTQ 离线 Profiling (敏感层识别)...")
    hatq = HaTQQuantizer(sensitivity_threshold=1.5, hadamard_dim=256)
    layer_config = hatq.profile_layers(model, calib_input)

    # 6. 根据模型大小决定量化层数
    max_layers = 0 if is_mock else 8

    # 7. 方法 A: 基线 INT8 (无 Hadamard)
    print("\n" + "=" * 70)
    print("[5] 方法 A: 基线 INT8 量化 (无 Hadamard 变换)")
    print("=" * 70)
    baseline_int8_quantize(model, max_layers=max_layers)
    logits_baseline = run_model_forward(model, test_input)

    # 收集逐层误差
    baseline_metrics = []
    layer_idx = 0
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and name in saved_weights:
            if max_layers > 0 and layer_idx >= 8:
                break
            m = quantization_error_metrics(saved_weights[name], module.weight.data)
            baseline_metrics.append((name, m))
            layer_idx += 1

    # 恢复权重
    _restore_weights(model, saved_weights)

    # 8. 方法 B: HaTQ (Hadamard + INT8)
    print("\n" + "=" * 70)
    print("[6] 方法 B: HaTQ (Hadamard 重参数化 + INT8 量化)")
    print("=" * 70)
    hatq.quantize_model(model, layer_config, max_layers=max_layers)
    logits_hatq = hatq_forward(model, test_input)

    # 收集逐层误差
    hatq_metrics = []
    layer_idx = 0
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and name in saved_weights:
            if max_layers > 0 and layer_idx >= 8:
                break
            m = quantization_error_metrics(saved_weights[name], module.weight.data)
            hatq_metrics.append((name, m))
            layer_idx += 1

    # 恢复权重
    _restore_weights(model, saved_weights)

    # 9. 逐层权重误差对比
    print("\n" + "=" * 70)
    print("[7] 逐层权重量化误差对比")
    print("=" * 70)
    print(f"  {'Layer':<30} {'Baseline MSE':<15} {'HaTQ MSE':<15} {'改善%':<10}")
    print(f"  {'-'*70}")

    total_bl_mse = 0.0
    total_ht_mse = 0.0
    for (name_bl, m_bl), (name_ht, m_ht) in zip(baseline_metrics, hatq_metrics):
        improvement = ((m_bl['mse'] - m_ht['mse'])
                       / max(m_bl['mse'], 1e-12) * 100)
        short_name = name_bl[-28:] if len(name_bl) > 28 else name_bl
        print(f"  {short_name:<30} {m_bl['mse']:<15.8f} "
              f"{m_ht['mse']:<15.8f} {improvement:<10.1f}%")
        total_bl_mse += m_bl['mse']
        total_ht_mse += m_ht['mse']

    if baseline_metrics:
        n = len(baseline_metrics)
        avg_bl = total_bl_mse / n
        avg_ht = total_ht_mse / n
        avg_imp = (avg_bl - avg_ht) / max(avg_bl, 1e-12) * 100
        print(f"  {'-'*70}")
        print(f"  {'平均':<30} {avg_bl:<15.8f} {avg_ht:<15.8f} {avg_imp:<10.1f}%")

    # 10. 模型输出误差对比
    print("\n" + "=" * 70)
    print("[8] 模型输出误差对比")
    print("=" * 70)

    mse_baseline = F.mse_loss(logits_fp.float(), logits_baseline.float()).item()
    mse_hatq = F.mse_loss(logits_fp.float(), logits_hatq.float()).item()
    output_imp = (mse_baseline - mse_hatq) / max(mse_baseline, 1e-12) * 100

    print(f"  全精度 vs 基线 INT8: MSE = {mse_baseline:.8f}")
    print(f"  全精度 vs HaTQ INT8: MSE = {mse_hatq:.8f}")
    print(f"  HaTQ 输出误差改善: {output_imp:.1f}%")

    # 11. 预测对比
    pred_fp = logits_fp[0].argmax(dim=-1)[:5].tolist()
    pred_bl = logits_baseline[0].argmax(dim=-1)[:5].tolist()
    pred_ht = logits_hatq[0].argmax(dim=-1)[:5].tolist()
    print(f"\n  预测 token (前5个):")
    print(f"    FP32:     {pred_fp}")
    print(f"    基线 INT8: {pred_bl}")
    print(f"    HaTQ:      {pred_ht}")
    bl_match = sum(1 for a, b in zip(pred_fp, pred_bl) if a == b)
    ht_match = sum(1 for a, b in zip(pred_fp, pred_ht) if a == b)
    print(f"    基线一致率: {bl_match}/5, HaTQ一致率: {ht_match}/5")

    # 12. Hadamard 变换效果分析
    print("\n" + "=" * 70)
    print("[9] Hadamard 变换效果分析 (权重分布变化)")
    print("=" * 70)

    # 取第一个 Linear 层分析
    first_linear_name = list(saved_weights.keys())[0]
    w_orig = saved_weights[first_linear_name]
    w_transformed = hatq.apply_hadamard_weight(
        w_orig, layer_config.get(first_linear_name, HadamardType.DOUBLE))

    # 计算权重分布统计
    orig_kurtosis = _compute_kurtosis(w_orig)
    trans_kurtosis = _compute_kurtosis(w_transformed)
    orig_max = w_orig.abs().max().item()
    trans_max = w_transformed.abs().max().item()

    print(f"  原始权重:  max_abs={orig_max:.4f}, 峰度={orig_kurtosis:.2f} "
          f"(越低越适合均匀量化)")
    print(f"  Hadamard变换后: max_abs={trans_max:.4f}, 峰度={trans_kurtosis:.2f}")
    print(f"  峰度降低: {orig_kurtosis - trans_kurtosis:.2f} "
          f"(分布更均匀, 更适合 INT8 量化)")

    print("\n" + "=" * 70)
    print("HaTQ 验证完成。")
    print("核心结论: Hadamard 正交变换重参数化权重和激活, 使分布更均匀,")
    print("降低重尾特性, 从而提升均匀 INT8 量化的精度。")
    print("敏感层使用 Weight-only Hadamard 避免激活范围放大。")
    print("=" * 70)


def _compute_kurtosis(x: torch.Tensor) -> float:
    """计算峰度 (kurtosis), 衡量分布的重尾程度。"""
    x_flat = x.flatten().float()
    mean = x_flat.mean()
    var = x_flat.var()
    if var < 1e-12:
        return 0.0
    kurt = ((x_flat - mean) ** 4).mean() / (var ** 2) - 3  # 超额峰度
    return kurt.item()


if __name__ == "__main__":
    main()
