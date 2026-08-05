#!/usr/bin/env python3
"""
DeVIT: Low-Power ViT Acceleration Using Delta Computation
==========================================================
论文: arXiv:2608.01343
作者: Reyhaneh Hosseinzadeh, Parham Zilouchian Moghaddam, Mehdi Modarressi

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)
(注: 原论文针对 ViT, 本 demo 将其差分计算方法应用于 LLM 的 Linear 层)

核心方法
--------
DeVIT 利用量化后权重的值局部性 (value locality), 通过差分计算实现
无乘法 (multiplier-less) 矩阵乘法。

1. 低比特权重量化
   - 将权重量化到 k-bit (如 4-bit, 16 个离散值)
   - 量化后权重来自有限值域: w_q ∈ {-7, -6, ..., 0, ..., 6, 7}

2. 值局部性 (Value Locality)
   - 量化后, 相邻位置的权重值往往相同或接近
   - 差分编码: delta[i] = w_q[i] - w_q[i-1]
   - 大部分 delta 为 0 (相邻权重相同), 非零 delta 取值有限

3. 无乘法矩阵乘法 (Multiplier-less MatMul)
   标准计算: y = sum(x[i] * w[i])  — 需要 N 次乘法

   差分计算:
   - 将权重表示为前缀和: w[i] = w[0] + sum(delta[j] for j=1..i)
   - 代入: y = sum(x[i] * (w[0] + sum(delta[j] for j<=i)))
         = w[0] * sum(x[i]) + sum(delta[j] * suffix_sum(x, j))
   - 其中 suffix_sum(x, j) = sum(x[i] for i >= j)
   - 简化: y = sum(delta[i] * S[i]),  S[i] = sum(x[j] for j >= i)

   优势:
   - 大部分 delta[i] = 0, 对应项可跳过 (零值跳过)
   - 非零 delta 来自小值域, 可用查找表 (LUT) 实现移位-加法替代乘法
   - 总操作: N 次后缀和累加 + 非零 delta 数量的移位-加法

4. 移位-加法查找表
   对于 4-bit 量化, delta ∈ [-14, 14]:
   - delta = 0: 跳过
   - delta = ±1: 加/减 S[i]
   - delta = ±2: 加/减 (S[i] << 1)
   - delta = ±3: 加/减 (S[i] + (S[i] << 1))
   - delta = ±4: 加/减 (S[i] << 2)
   - ... 以此类推, 所有乘法替换为移位和加法

运行方式
--------
    python3 demo.py
"""

import sys
import math
import time
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
# 1. 低比特权重量化
# =============================================================================

class LowBitWeightQuantizer:
    """
    低比特权重量化器 (对称均匀量化)。

    将权重量化到 k-bit: w_q ∈ {-(2^(k-1)-1), ..., 0, ..., 2^(k-1)-1}
    每行 (输出通道) 独立计算尺度: scale = max(|w|) / (2^(k-1) - 1)
    反量化: w_dq = w_q * scale
    """

    def __init__(self, bits: int = 4, per_channel: bool = True):
        self.bits = bits
        self.per_channel = per_channel
        self.qmax = 2 ** (bits - 1) - 1
        self.qmin = -(2 ** (bits - 1))

    def quantize(self, w: torch.Tensor):
        """
        量化权重并返回整数权重和尺度。

        Args:
            w: 权重 [out_features, in_features]

        Returns:
            w_int: 整数量化权重 [out_features, in_features] (值为整数)
            scale: 尺度因子 [out_features, 1] 或标量
        """
        if self.per_channel:
            scale = w.abs().amax(dim=1, keepdim=True) / self.qmax
        else:
            scale = w.abs().max() / self.qmax
        scale = scale.clamp_min(1e-8)

        w_int = torch.clamp(torch.round(w / scale), self.qmin, self.qmax)
        return w_int, scale

    def dequantize(self, w_int: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        """反量化。"""
        return w_int * scale


# =============================================================================
# 2. 差分编码 (Delta Encoding)
# =============================================================================

class DeltaEncoder:
    """
    差分编码器: 将量化权重序列编码为差分序列。

    对于权重行 w[0], w[1], ..., w[n-1]:
    - delta[0] = w[0]  (初始值)
    - delta[i] = w[i] - w[i-1]  (一阶差分)

    值局部性: 量化后相邻权重往往相同, 大部分 delta = 0。
    非零 delta 的数量远小于权重总数, 可用于加速计算。
    """

    @staticmethod
    def encode(w_int: torch.Tensor) -> torch.Tensor:
        """
        对整数权重进行差分编码。

        Args:
            w_int: 整数权重 [out_features, in_features]

        Returns:
            delta: 差分序列 [out_features, in_features]
                   delta[:, 0] = w_int[:, 0]
                   delta[:, i] = w_int[:, i] - w_int[:, i-1]
        """
        delta = torch.zeros_like(w_int)
        delta[:, 0] = w_int[:, 0]
        delta[:, 1:] = w_int[:, 1:] - w_int[:, :-1]
        return delta

    @staticmethod
    def decode(delta: torch.Tensor) -> torch.Tensor:
        """
        从差分序列恢复原始权重 (前缀和)。

        Args:
            delta: 差分序列 [out_features, in_features]

        Returns:
            w_int: 恢复的整数权重
        """
        return torch.cumsum(delta, dim=1)

    @staticmethod
    def analyze_locality(delta: torch.Tensor) -> dict:
        """
        分析值局部性: 差分序列中零值和非零值的统计。

        Args:
            delta: 差分序列 [out_features, in_features]

        Returns:
            统计信息: 零值比例, 非零 delta 数量, 唯一 delta 值数等
        """
        total = delta.numel()
        zero_count = (delta == 0).sum().item()
        nonzero_count = total - zero_count
        unique_values = delta.unique()

        return {
            "total_elements": total,
            "zero_count": zero_count,
            "zero_ratio": zero_count / total,
            "nonzero_count": nonzero_count,
            "nonzero_ratio": nonzero_count / total,
            "unique_delta_values": len(unique_values),
            "unique_delta_list": unique_values.tolist(),
        }


# =============================================================================
# 3. 无乘法矩阵乘法 (Multiplier-less MatMul)
# =============================================================================

class MultiplierFreeLinear(nn.Module):
    """
    无乘法线性层: 使用差分计算实现无乘法矩阵乘法。

    计算 y = x @ W^T:
    1. 量化权重 W 到 k-bit 整数
    2. 对每行权重进行差分编码
    3. 计算输入的后缀和: S[i] = sum(x[j] for j >= i)
    4. y = sum(delta[i] * S[i]) — 使用移位-加法替代乘法

    移位-加法查找表:
    - delta = 0: 跳过 (零值跳过, 节省计算)
    - delta != 0: 将 |delta| 分解为 2 的幂次之和, 用移位和加法实现乘法
      例如: delta=5 = 4+1 = 2^2 + 2^0
            delta * S = (S << 2) + S
    """

    def __init__(self, weight: torch.Tensor, bits: int = 4):
        super().__init__()
        self.bits = bits
        self.quantizer = LowBitWeightQuantizer(bits=bits, per_channel=True)

        # 量化权重
        w_int, scale = self.quantizer.quantize(weight)
        self.register_buffer('w_int', w_int)          # 整数权重
        self.register_buffer('scale', scale)            # 尺度因子
        self.register_buffer('delta', DeltaEncoder.encode(w_int))  # 差分序列

        # 分析值局部性
        self.locality_stats = DeltaEncoder.analyze_locality(self.delta)

        # 预计算移位-加法分解 (对每个可能的 delta 值)
        self._build_shift_add_lut()

    def _build_shift_add_lut(self):
        """
        构建移位-加法查找表。

        对于每个可能的 delta 值, 分解为 2 的幂次之和。
        例如: 5 = 4 + 1 → shifts = [2, 0], sign = +1
              -3 = -(2 + 1) → shifts = [1, 0], sign = -1
        """
        qmax = 2 ** (self.bits - 1) - 1
        delta_range = range(-2 * qmax, 2 * qmax + 1)

        self.shift_lut = {}
        for d in delta_range:
            if d == 0:
                self.shift_lut[d] = ([], 0)  # 无操作
            else:
                sign = 1 if d > 0 else -1
                abs_d = abs(d)
                # 分解为 2 的幂次: 找到所有为 1 的位
                shifts = []
                for bit in range(int(math.log2(abs_d)) + 1 if abs_d > 0 else 1):
                    if abs_d & (1 << bit):
                        shifts.append(bit)
                self.shift_lut[d] = (shifts, sign)

    def _shift_add_multiply(self, s: torch.Tensor, delta_val: int) -> torch.Tensor:
        """
        使用移位-加法计算 s * delta_val。

        Args:
            s: 后缀和值 (标量或张量)
            delta_val: 整数 delta 值

        Returns:
            result: s * delta_val (通过移位和加法计算)
        """
        shifts, sign = self.shift_lut[delta_val]
        if not shifts:
            return torch.zeros_like(s)

        # 使用乘以 2^shift 替代位移操作 (硬件中为移位, 软件模拟用乘法)
        # 对于浮点张量, PyTorch 不支持 << 运算符, 因此用 s * (2 ** shift) 等价实现
        result = torch.zeros_like(s)
        for shift in shifts:
            result = result + (s * float(2 ** shift))  # 等价于 s << shift

        if sign < 0:
            result = -result
        return result

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        无乘法前向传播。

        Args:
            x: 输入 [..., in_features]

        Returns:
            y: 输出 [..., out_features]
        """
        orig_shape = x.shape
        in_features = x.shape[-1]
        out_features = self.w_int.shape[0]

        # 展平输入为 [batch, in_features]
        x_flat = x.reshape(-1, in_features)
        batch_size = x_flat.shape[0]

        # 1. 计算输入的后缀和: S[i] = sum(x[j] for j >= i)
        # S = cumsum from right to left
        suffix_sum = torch.zeros_like(x_flat)
        suffix_sum[:, -1] = x_flat[:, -1]
        for i in range(in_features - 2, -1, -1):
            suffix_sum[:, i] = suffix_sum[:, i + 1] + x_flat[:, i]

        # 2. 差分计算: y = sum(delta[i] * S[i])
        # 使用移位-加法替代乘法, 跳过零值 delta
        y = torch.zeros(batch_size, out_features, device=x.device, dtype=x.dtype)

        delta = self.delta  # [out_features, in_features]

        # 对每个输出通道, 使用差分计算
        for out_idx in range(out_features):
            delta_row = delta[out_idx]  # [in_features]

            # 零值跳过: 只处理非零 delta
            nonzero_mask = delta_row != 0
            nonzero_indices = torch.where(nonzero_mask)[0]

            for idx in nonzero_indices:
                d_val = delta_row[idx].item()
                s_val = suffix_sum[:, idx]  # [batch]
                # 移位-加法乘法
                y[:, out_idx] += self._shift_add_multiply(s_val, d_val)

        # 3. 乘以尺度因子
        y = y * self.scale.squeeze(1).unsqueeze(0)  # [batch, out_features]

        # 重塑回原始形状
        y = y.reshape(*orig_shape[:-1], out_features)
        return y

    def forward_standard(self, x: torch.Tensor) -> torch.Tensor:
        """
        标准前向传播 (使用反量化权重 + 标准矩阵乘法)。
        用于验证差分计算的正确性。
        """
        w_dq = self.quantizer.dequantize(self.w_int, self.scale)
        return F.linear(x, w_dq)


# =============================================================================
# 4. 移位-加法统计
# =============================================================================

def count_operations(delta: torch.Tensor, bits: int = 4) -> dict:
    """
    统计无乘法计算的操作数。

    对比标准矩阵乘法:
    - 标准: N 次乘法 + N 次加法
    - DeVIT: N 次后缀和加法 + (非零 delta 数) × (平均移位次数) 次移位-加法

    Args:
        delta: 差分序列 [out_features, in_features]
        bits: 量化比特数

    Returns:
        操作统计
    """
    total_elements = delta.numel()
    zero_count = (delta == 0).sum().item()
    nonzero_count = total_elements - zero_count

    # 计算非零 delta 的平均移位次数 (popcount of |delta|)
    # 使用查找表向量化计算, 避免逐元素 Python 循环
    qmax = 2 ** (bits - 1) - 1
    max_abs_delta = 2 * qmax
    # 预计算 0..max_abs_delta 的 popcount
    popcount_lut = torch.zeros(max_abs_delta + 1, dtype=torch.long)
    for v in range(max_abs_delta + 1):
        popcount_lut[v] = bin(v).count('1')

    abs_delta = delta.abs().long().clamp(0, max_abs_delta)
    total_shifts = popcount_lut[abs_delta].sum().item()

    avg_shifts = total_shifts / max(nonzero_count, 1)

    # 标准方法: total_elements 次乘法
    # DeVIT: total_elements 次后缀和加法 + total_shifts 次移位 + total_shifts 次加法
    standard_mults = total_elements
    devit_adds = total_elements  # 后缀和
    devit_shifts = total_shifts
    devit_extra_adds = total_shifts  # 移位后的加法

    return {
        "total_elements": total_elements,
        "standard_multiplications": standard_mults,
        "devit_nonzero_deltas": nonzero_count,
        "devit_zero_skipped": zero_count,
        "zero_skip_ratio": zero_count / total_elements,
        "devit_total_shifts": total_shifts,
        "devit_avg_shifts_per_nonzero": avg_shifts,
        "devit_total_adds": devit_adds + devit_extra_adds,
        "devit_total_shifts_ops": devit_shifts,
        "mult_reduction": 1 - (total_shifts + devit_adds + devit_extra_adds) / (2 * standard_mults),
    }


# =============================================================================
# 5. 主流程
# =============================================================================

def main():
    print("=" * 70)
    print("DeVIT: Low-Power ViT Acceleration Using Delta Computation")
    print("论文: arXiv:2608.01343 | 目标模型: Qwen3-0.6B")
    print("=" * 70)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 选取一个 Linear 层进行演示
    print("\n[2] 选取 Linear 层进行 DeVIT 差分计算演示...")
    target_layer = None
    target_name = None
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            target_layer = module
            target_name = name
            break

    if target_layer is None:
        print("    未找到 Linear 层!")
        return

    w = target_layer.weight.data
    out_features, in_features = w.shape
    print(f"    目标层: {target_name}")
    print(f"    权重 shape: {w.shape} (out={out_features}, in={in_features})")

    # 3. 低比特量化
    bits = 4
    print(f"\n[3] {bits}-bit 权重量化...")
    quantizer = LowBitWeightQuantizer(bits=bits, per_channel=True)
    w_int, scale = quantizer.quantize(w)
    w_dq = quantizer.dequantize(w_int, scale)
    quant_metrics = quantization_error_metrics(w, w_dq)
    print(f"    量化误差: MSE={quant_metrics['mse']:.8f}, "
          f"cosine_sim={quant_metrics['cosine_similarity']:.6f}")
    print(f"    整数权重值域: [{w_int.min().item()}, {w_int.max().item()}]")

    # 4. 差分编码与值局部性分析
    print(f"\n[4] 差分编码与值局部性分析...")
    delta = DeltaEncoder.encode(w_int)
    locality = DeltaEncoder.analyze_locality(delta)

    print(f"    总元素数: {locality['total_elements']}")
    print(f"    零值 delta 数: {locality['zero_count']} "
          f"({locality['zero_ratio']*100:.1f}%)")
    print(f"    非零 delta 数: {locality['nonzero_count']} "
          f"({locality['nonzero_ratio']*100:.1f}%)")
    print(f"    唯一 delta 值数: {locality['unique_delta_values']}")
    print(f"    值局部性: {locality['zero_ratio']*100:.1f}% 的相邻权重相同 (delta=0)")

    # 5. 验证差分编码正确性
    print(f"\n[5] 验证差分编码正确性...")
    w_decoded = DeltaEncoder.decode(delta)
    encode_error = (w_int - w_decoded).abs().max().item()
    print(f"    编码-解码误差: {encode_error} (应为 0)")

    # 6. 操作数统计
    print(f"\n[6] 操作数统计 (乘法消除分析)...")
    ops = count_operations(delta, bits)
    print(f"    标准方法: {ops['standard_multiplications']} 次乘法")
    print(f"    DeVIT 方法:")
    print(f"      零值跳过: {ops['devit_zero_skipped']} ({ops['zero_skip_ratio']*100:.1f}%)")
    print(f"      非零 delta: {ops['devit_nonzero_deltas']}")
    print(f"      总移位操作: {ops['devit_total_shifts']}")
    print(f"      非零 delta 平均移位次数: {ops['devit_avg_shifts_per_nonzero']:.2f}")
    print(f"      总加法操作: {ops['devit_total_adds']}")
    mult_saved = (1 - ops['devit_nonzero_deltas'] / ops['standard_multiplications']) * 100
    print(f"    乘法消除率: {mult_saved:.1f}% "
          f"(非零 delta / 总元素)")

    # 7. 无乘法矩阵乘法验证
    # 注: 无乘法前向使用 Python 逐通道循环, 对大维度权重过慢
    # 因此取权重的子集 (前 32 个输出通道, 前 128 个输入特征) 进行演示
    print(f"\n[7] 无乘法矩阵乘法验证...")
    demo_out = min(out_features, 32)
    demo_in = min(in_features, 128)
    w_demo = w[:demo_out, :demo_in].contiguous()
    print(f"    演示子集: out={demo_out}, in={demo_in} (从 {out_features}x{in_features} 截取)")
    test_input = torch.randn(4, demo_in, device=device)

    # 创建 DeVIT 层 (使用子集权重)
    devit_layer = MultiplierFreeLinear(w_demo, bits=bits).to(device)

    # 标准量化前向
    y_standard = devit_layer.forward_standard(test_input)

    # DeVIT 差分前向 (无乘法)
    y_devit = devit_layer.forward(test_input)

    # 对比
    mae = (y_standard - y_devit).abs().mean().item()
    max_err = (y_standard - y_devit).abs().max().item()
    cos_sim = F.cosine_similarity(
        y_standard.flatten().unsqueeze(0),
        y_devit.flatten().unsqueeze(0)
    ).item()

    print(f"    输入 shape: {test_input.shape}")
    print(f"    标准量化输出 shape: {y_standard.shape}")
    print(f"    DeVIT 差分输出 shape: {y_devit.shape}")
    print(f"    标准 vs DeVIT MAE: {mae:.10f} (应接近 0)")
    print(f"    标准 vs DeVIT 最大误差: {max_err:.10f}")
    print(f"    余弦相似度: {cos_sim:.10f}")

    # 8. 全精度 vs 量化对比
    print(f"\n[8] 全精度 vs 量化对比...")
    y_fp = F.linear(test_input, w_demo)
    mse_fp_quant = F.mse_loss(y_fp, y_standard).item()
    print(f"    全精度 vs 4-bit 量化: MSE = {mse_fp_quant:.8f}")

    # 9. 对多个 Linear 层的统计
    print(f"\n[9] 全模型层值局部性统计...")
    print(f"  {'Layer':<30} {'零值比例%':<12} {'非零delta':<12} {'乘法消除%':<12}")
    print(f"  {'-'*66}")

    total_mults = 0
    total_nonzero = 0
    layer_count = 0
    max_layers = 10 if not is_mock else 0

    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            if max_layers > 0 and layer_count >= max_layers:
                break
            w_layer = module.weight.data
            q = LowBitWeightQuantizer(bits=bits, per_channel=True)
            w_int_layer, _ = q.quantize(w_layer)
            delta_layer = DeltaEncoder.encode(w_int_layer)
            ops_layer = count_operations(delta_layer, bits)

            total_mults += ops_layer['standard_multiplications']
            total_nonzero += ops_layer['devit_nonzero_deltas']

            short_name = name[-28:] if len(name) > 28 else name
            print(f"  {short_name:<30} {ops_layer['zero_skip_ratio']*100:<12.1f} "
                  f"{ops_layer['devit_nonzero_deltas']:<12} "
                  f"{(1-ops_layer['devit_nonzero_deltas']/ops_layer['standard_multiplications'])*100:<12.1f}")
            layer_count += 1

    if total_mults > 0:
        overall_elimination = (1 - total_nonzero / total_mults) * 100
        print(f"  {'-'*66}")
        print(f"  {'总体':<30} {'':>12} {total_nonzero:<12} {overall_elimination:<12.1f}")

    # 10. 移位-加法 LUT 示例
    print(f"\n[10] 移位-加法查找表示例 (4-bit 量化)...")
    print(f"  {'delta':<8} {'二进制':<12} {'分解':<20} {'操作':<30}")
    print(f"  {'-'*70}")
    example_deltas = [0, 1, -1, 2, -2, 3, -3, 5, -5, 7, -7, 10, -10, 14, -14]
    for d in example_deltas:
        if d == 0:
            print(f"  {d:<8} {'0':<12} {'—':<20} {'跳过':<30}")
        else:
            sign = '+' if d > 0 else '-'
            abs_d = abs(d)
            binary = bin(abs_d)
            # 分解为 2 的幂
            powers = []
            for bit in range(abs_d.bit_length()):
                if abs_d & (1 << bit):
                    powers.append(f"2^{bit}")
            decomp = f"{sign}({' + '.join(powers)})"
            ops_str = f"{sign} " + " + ".join([f"(S<<{p})" for p in range(abs_d.bit_length()) if abs_d & (1 << p)])
            print(f"  {d:<8} {binary:<12} {decomp:<20} {ops_str:<30}")

    print(f"\n{'='*70}")
    print("DeVIT 验证完成。")
    print("核心结论: 低比特量化引入值局部性, 差分编码使大部分 delta=0。")
    print(f"乘法消除率: {mult_saved:.1f}%, 非零 delta 用移位-加法替代乘法。")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
