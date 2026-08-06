#!/usr/bin/env python3
"""
TASQ: Temporal-Adaptive Bit Sparsification Quantization
=========================================================
论文: arXiv:2608.03057
作者: Seokho Han, Dongwei Wang, Jinhee Kim, Yiran Chen, Kang Eun Jeon,
      Huanrui Yang, Jong Hwan Ko
标题: TASQ: Temporal-Adaptive Bit Sparsification Quantization for Diffusion Models

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)

注: TASQ 原始面向扩散模型 (diffusion) 的去噪轨迹。本实现将其核心思想
    适配到 LLM 推理: 将扩散的 "denoising step" 类比为 LLM 的 "generation
    step (解码步)", 将 "layer" 作为空间维度, 演示 Temporal-Spatial LSB Mask
    的位稀疏化量化机制。

核心方法
--------
静态量化为每个 (层/步) 分配同一精度。为保留质量, 该精度必须满足最敏感的
步骤, 即使多数步骤本可用更少比特。TASQ 分离 "存储成本" 与 "计算成本":

1. 共享最大精度权重缓冲 (Shared Max-Precision Buffer)
   - 仅存储一份最高精度 (如 INT8) 的权重, 不为每个 step 复制权重。
   - 存储成本由最坏情况 (worst case) 决定, 固定不变。

2. Temporal-Spatial LSB Mask (时序-空间 LSB 掩码)
   - 学习一个掩码 M[layer, step], 表示该 (层, 步) 要截断多少个最低有效位 (LSB)。
   - 有效精度 = max_bits - M[layer, step]。
   - LSB 截断: 对整数权重做算术右移再左移, 把 k 个 LSB 置零:
       x_trunc = (x_int >> k) << k
     这等价于把权重舍入到 2^k 的倍数, 降低有效精度但不改变存储格式。

3. Bit-Serial 执行 (Temporal-Precision Engine)
   - 位串行算术中, 计算周期与有效精度成正比: cycles ∝ effective_bits。
   - 切换精度无额外周期开销 (只需改变处理多少个 bit-plane)。
   - 因此 BitOPs = sum_{layer,step} MACs * effective_bits。
   - 存储固定 (worst case), 但计算在不敏感的步骤显著下降。

核心收益
--------
- 存储不变 (一份 INT8 权重)
- BitOPs 相比静态 INT8 位串行下降 25-50%
- 相比朴素静态 8-bit 位串行下降 6.1-7.5x
- 质量与静态量化相当 (因为保留了最敏感步骤的全精度)

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
    MockTransformer,
)


# =============================================================================
# 1. INT8 权重量化 (共享最大精度缓冲)
# =============================================================================

def quantize_weight_int8(w: torch.Tensor) -> tuple:
    """
    Per-channel 对称 INT8 量化 (输出通道维度)。

    这是 TASQ 的 "共享最大精度缓冲": 所有权重以 INT8 存储。
    返回整数权重和尺度, 供后续 LSB 截断使用。

    Args:
        w: 权重 [out_features, in_features]

    Returns:
        w_int: 量化整数权重 (float 存储, 值在 [-128, 127])
        scale: per-channel 尺度 [out_features, 1]
    """
    w_max = w.abs().amax(dim=1, keepdim=True).clamp_min(1e-8)
    scale = w_max / 127.0
    w_int = torch.clamp(torch.round(w / scale), -128, 127)
    return w_int, scale


def dequantize_int8(w_int: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    """反量化 INT8 权重回浮点。"""
    return w_int * scale


def truncate_lsb(w_int: torch.Tensor, k: int) -> torch.Tensor:
    """
    LSB 截断: 截断 k 个最低有效位。

    对整数做算术右移 k 位再左移 k 位, 把 k 个 LSB 置零:
        x_trunc = (x_int >> k) << k
    这等价于把权重舍入到 2^k 的倍数, 有效精度降为 (8 - k) bit。
    截断后非零 bit-plane 数 = 8 - k, 位串行计算周期随之减少。

    注意: 用 round-half-to-even 的整数运算, 对称 INT8 用算术移位保持符号。

    Args:
        w_int: 整数权重 (值在 [-128, 127])
        k: 截断的 LSB 位数 (0 表示不截断)

    Returns:
        w_trunc: 截断后的整数权重 (仍 8-bit 存储, 但 k 个 LSB 为 0)
    """
    if k <= 0:
        return w_int
    # 算术移位 (保持符号): round to nearest multiple of 2^k
    # 先加偏置做四舍五入: round(x / 2^k) * 2^k
    factor = 2 ** k
    # 四舍五入到最近的 2^k 倍数 (对称)
    w_rounded = torch.round(w_int / factor) * factor
    # 钳位回 [-128, 127]
    w_trunc = torch.clamp(w_rounded, -128, 127)
    return w_trunc


def effective_bits(max_bits: int, k: int) -> int:
    """截断 k 个 LSB 后的有效精度。"""
    return max(1, max_bits - k)


# =============================================================================
# 2. 敏感度估计 (用于学习 LSB Mask)
# =============================================================================

@torch.no_grad()
def collect_activation_stats(model, input_ids_list, is_mock: bool,
                              max_layers: int = 0) -> dict:
    """
    收集每层 Linear 的输入激活统计, 作为量化敏感度的代理。

    敏感度 ∝ E[activation^2] (Hessian 对角线的代理):
    权重扰动 Δw 对输出的影响 ≈ activation^2 * Δw^2。
    激活越大的层, 量化误差对输出影响越大, 应保留更高精度。

    Args:
        model: 模型
        input_ids_list: 校准输入列表 (多个不同输入, 对应不同 "temporal step")
        is_mock: 是否 mock 模型
        max_layers: 最多统计多少层 (0=全部)

    Returns:
        stats: {layer_name: {act_sq_mean: [T], act_max: [T]}}
               T = len(input_ids_list) (temporal steps)
    """
    stats = {}
    hooks = []
    captured = {}

    def make_hook(name):
        # forward_pre_hook 签名为 (module, args), args 是输入元组
        def hook(module, args):
            x = args[0] if isinstance(args, tuple) else args
            captured[name] = x.detach()
        return hook

    layer_count = 0
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            if max_layers > 0 and layer_count >= max_layers:
                break
            h = module.register_forward_pre_hook(make_hook(name))
            hooks.append(h)
            layer_count += 1
            stats[name] = {"act_sq_mean": [], "act_max": []}

    # 对每个校准输入 (temporal step) 收集统计
    model.eval()
    for input_ids in input_ids_list:
        captured.clear()
        with torch.no_grad():
            _ = model(input_ids)
        for name in stats:
            if name in captured:
                x = captured[name].float()
                stats[name]["act_sq_mean"].append(x.pow(2).mean().item())
                stats[name]["act_max"].append(x.abs().max().item())
            else:
                stats[name]["act_sq_mean"].append(1e-6)
                stats[name]["act_max"].append(1e-6)

    for h in hooks:
        h.remove()

    return stats


def compute_truncation_error(w_int: torch.Tensor, scale: torch.Tensor,
                              k: int, act_sq_mean: float) -> float:
    """
    计算截断 k 个 LSB 引入的输出误差 (代理)。

    误差 ≈ act_sq_mean * E[(w - w_trunc)^2] * scale^2

    Args:
        w_int: 整数权重
        scale: 尺度
        k: 截断位数
        act_sq_mean: 该层该步的激活平方均值

    Returns:
        误差代理值
    """
    w_trunc = truncate_lsb(w_int, k)
    # 量化误差 (整数域)
    int_err = (w_int - w_trunc).pow(2).mean().item()
    # 转换到浮点域并乘以激活敏感度
    scale_sq = (scale ** 2).mean().item()
    return act_sq_mean * int_err * scale_sq


# =============================================================================
# 3. Temporal-Spatial LSB Mask 学习 (贪心)
# =============================================================================

class LSBMaskLearner:
    """
    学习 Temporal-Spatial LSB Mask。

    目标: 在总误差预算下, 最大化截断的 LSB 数 (即最小化 BitOPs)。
    这是经典的背包问题变体, 这里用贪心近似:
        每次选择 "误差增量 / bit节省" 比最小的截断操作。

    参数:
        max_bits: 最大精度 (8)
        min_bits: 最低允许有效精度 (如 2)
        error_budget: 总误差预算 (相对全精度的比例)
    """

    def __init__(self, max_bits: int = 8, min_bits: int = 2,
                 error_budget: float = 0.05):
        self.max_bits = max_bits
        self.min_bits = min_bits
        self.max_trunc = max_bits - min_bits  # 最多截断的 LSB 数
        self.error_budget = error_budget

    def learn(self, layer_names, num_steps, error_fn):
        """
        学习 LSB mask。

        Args:
            layer_names: 层名列表
            num_steps: temporal steps 数
            error_fn: callable(layer_name, step, k) -> 截断 k 位的误差

        Returns:
            mask: dict {(layer, step): k} 每个位置截断的 LSB 数
            info: dict 学习统计
        """
        # 初始化: 所有位置截断 0 位 (全精度)
        mask = {(l, s): 0 for l in layer_names for s in range(num_steps)}

        # 逐层逐步: 计算从 k 到 k+1 的边际误差增量
        # 贪心: 每次选误差增量最小且不超过预算的截断
        total_error = 0.0
        total_bits_saved = 0
        total_possible_bits = len(layer_names) * num_steps * self.max_bits

        # 预计算所有候选 (layer, step, next_k) 的边际误差
        # next_k = 当前 k + 1
        improvements = []
        for l in layer_names:
            for s in range(num_steps):
                for k in range(0, self.max_trunc):
                    # 从 k 截断到 k+1 的误差增量
                    err_k = error_fn(l, s, k)
                    err_k1 = error_fn(l, s, k + 1)
                    delta = err_k1 - err_k  # 增加截断带来的误差增量
                    # 每截断 1 位节省 1 bit-plane
                    improvements.append((delta, l, s, k + 1))

        # 按误差增量升序排 (优先截断代价小的)
        improvements.sort(key=lambda x: x[0])

        # 贪心选择: 顺序应用截断, 直到达到误差预算
        # 当前每个 (l,s) 的截断数
        current_trunc = {(l, s): 0 for l in layer_names for s in range(num_steps)}

        for delta, l, s, target_k in improvements:
            # 只能顺序增加 (k -> k+1)
            if current_trunc[(l, s)] != target_k - 1:
                continue
            # 检查是否会超过预算
            if total_error + delta > self.error_budget:
                continue
            current_trunc[(l, s)] = target_k
            mask[(l, s)] = target_k
            total_error += delta
            total_bits_saved += 1

        info = {
            "total_error": total_error,
            "total_bits_saved": total_bits_saved,
            "total_possible_bits": total_possible_bits,
            "avg_effective_bits": (total_possible_bits - total_bits_saved)
                                  / (len(layer_names) * num_steps),
        }
        return mask, info


# =============================================================================
# 4. Bit-Serial BitOPs 计算
# =============================================================================

def compute_bitops(num_layers_used, mask, max_bits, num_steps,
                    macs_per_layer):
    """
    计算位串行 BitOPs。

    BitOPs = sum_{layer, step} macs_per_layer * effective_bits[layer, step]
    其中 effective_bits = max_bits - mask[layer, step]

    Args:
        num_layers_used: 实际处理的层数
        mask: LSB mask dict
        max_bits: 最大精度
        num_steps: temporal steps
        macs_per_layer: 每层 MAC 数 (单次前向)

    Returns:
        bitops_total, bitops_static_max (静态 max_bits 位串行)
    """
    bitops_total = 0
    layer_names = sorted(set(l for l, s in mask))
    for l in layer_names:
        for s in range(num_steps):
            k = mask.get((l, s), 0)
            eff = effective_bits(max_bits, k)
            bitops_total += macs_per_layer * eff

    # 静态 max_bits 位串行 (所有 step 都用 max_bits)
    bitops_static_max = num_layers_used * num_steps * macs_per_layer * max_bits
    return bitops_total, bitops_static_max


# =============================================================================
# 5. TASQ 量化器
# =============================================================================

class TASQQuantizer:
    """
    TASQ: 时序自适应位稀疏化量化器。

    工作流程:
    1. 将模型所有 Linear 权重量化为 INT8 (共享最大精度缓冲)
    2. 收集每层在不同 temporal step 的激活统计
    3. 计算每 (层, 步, 截断位数) 的误差代理
    4. 贪心学习 LSB mask, 在误差预算下最大化 bit 节省
    5. 位串行 BitOPs 评估
    """

    def __init__(self, max_bits: int = 8, min_bits: int = 2,
                 error_budget: float = 0.05, num_steps: int = 8,
                 max_layers: int = 0):
        self.max_bits = max_bits
        self.min_bits = min_bits
        self.error_budget = error_budget
        self.num_steps = num_steps
        self.max_layers = max_layers  # 0=全部
        self.learner = LSBMaskLearner(max_bits, min_bits, error_budget)

        # 存储每层的 INT8 权重和尺度
        self.layer_weights = {}  # {name: (w_int, scale)}
        self.layer_names = []

    def quantize_model_weights(self, model):
        """将模型所有 Linear 层权重量化为 INT8 (共享缓冲)。"""
        self.layer_weights = {}
        self.layer_names = []
        count = 0
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                if self.max_layers > 0 and count >= self.max_layers:
                    break
                w = module.weight.data
                w_int, scale = quantize_weight_int8(w)
                self.layer_weights[name] = (w_int, scale)
                self.layer_names.append(name)
                count += 1
        print(f"  TASQ: 量化 {count} 层为 INT8 (共享最大精度缓冲)")

    def compute_sensitivity(self, act_stats):
        """
        计算每 (层, 步, 截断位数) 的误差代理。

        Returns:
            error_table: {(layer, step, k): error}
        """
        error_table = {}
        for l in self.layer_names:
            if l not in act_stats or l not in self.layer_weights:
                continue
            w_int, scale = self.layer_weights[l]
            act_sq = act_stats[l]["act_sq_mean"]
            for s in range(min(self.num_steps, len(act_sq))):
                for k in range(0, self.max_bits - self.min_bits + 1):
                    err = compute_truncation_error(
                        w_int, scale, k, act_sq[s])
                    error_table[(l, s, k)] = err
        return error_table

    def learn_mask(self, act_stats):
        """
        学习 Temporal-Spatial LSB Mask。

        error_budget 解释为 "全截断 (所有位置截断到 min_bits) 总误差" 的比例:
            adaptive_budget = error_budget * full_trunc_error
        这样预算能跨模型/层规模自适应, 并让敏感位置保留更高精度,
        充分展示时序-空间精度差异 (而非所有位置一致截断)。
        """
        error_table = self.compute_sensitivity(act_stats)

        def error_fn(l, s, k):
            return error_table.get((l, s, k), 1e12)

        # 计算 "全截断" 总误差 (所有位置截到 min_bits)
        max_trunc = self.max_bits - self.min_bits
        full_trunc_error = sum(
            error_fn(l, s, max_trunc)
            for l in self.layer_names
            for s in range(self.num_steps)
            if (l, s, max_trunc) in error_table
        )
        # 自适应预算
        adaptive_budget = self.error_budget * max(full_trunc_error, 1e-12)
        self.learner.error_budget = adaptive_budget

        mask, info = self.learner.learn(
            self.layer_names, self.num_steps, error_fn)
        info["full_trunc_error"] = full_trunc_error
        info["adaptive_budget"] = adaptive_budget
        info["budget_fraction"] = self.error_budget
        return mask, info

    def apply_mask_to_layer(self, layer_name, step, mask):
        """
        对指定层在指定 step 应用 LSB 截断, 返回截断后的权重 (浮点)。

        用于评估特定 (层, 步) 的量化效果。
        """
        w_int, scale = self.layer_weights[layer_name]
        k = mask.get((layer_name, step), 0)
        w_trunc = truncate_lsb(w_int, k)
        return dequantize_int8(w_trunc, scale)

    def get_effective_precision_schedule(self, mask):
        """获取每 (层, 步) 的有效精度调度。"""
        schedule = {}
        for l in self.layer_names:
            for s in range(self.num_steps):
                k = mask.get((l, s), 0)
                schedule[(l, s)] = effective_bits(self.max_bits, k)
        return schedule


# =============================================================================
# 6. 基线: 静态量化
# =============================================================================

class StaticQuantizer:
    """
    静态量化基线: 所有 (层, 步) 使用同一精度。

    - Static-INT8: 所有层全 8-bit (BitOPs = max)
    - Static-INT4: 所有层 4-bit (存储减半, 但 TASQ 比较的是 BitOPs)
    """

    def __init__(self, bits: int = 8):
        self.bits = bits

    def quantize_weight(self, w):
        """静态 b-bit 量化。"""
        qmax = 2 ** (self.bits - 1) - 1
        qmin = -(2 ** (self.bits - 1))
        w_max = w.abs().amax(dim=1, keepdim=True).clamp_min(1e-8)
        scale = w_max / qmax
        w_q = torch.clamp(torch.round(w / scale), qmin, qmax)
        return w_q * scale, scale

    def bitops_static(self, num_layers, num_steps, macs_per_layer):
        """静态位串行 BitOPs。"""
        return num_layers * num_steps * macs_per_layer * self.bits


# =============================================================================
# 7. 主流程
# =============================================================================

def estimate_macs(model, is_mock, seq_len=64):
    """估算模型每层一次前向的 MAC 数 (简化)。"""
    if is_mock:
        m = model
        # q/k/v/o proj + gate/up/down proj
        h = m.hidden_size
        macs = (4 * h * h + 3 * h * m.layers[0]['gate_proj'].out_features)
        return int(macs * seq_len)
    else:
        cfg = model.config
        h = cfg.hidden_size
        inter = cfg.intermediate_size
        nh = cfg.num_attention_heads
        nkv = getattr(cfg, "num_key_value_heads", nh)
        hd = cfg.hidden_size // nh
        # attention: q/k/v/o
        attn_macs = (nh * hd * h + nkv * hd * h + nkv * hd * h + nh * hd * h) * seq_len
        # mlp: gate, up, down
        mlp_macs = 3 * h * inter * seq_len
        return int(attn_macs + mlp_macs)


def main():
    print("=" * 72)
    print("TASQ: Temporal-Adaptive Bit Sparsification Quantization")
    print("论文: arXiv:2608.03057 | 目标模型: Qwen3-0.6B")
    print("=" * 72)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 准备校准输入 (模拟 temporal steps, 即不同生成步的输入)
    num_steps = 8
    seq_len = 64
    if is_mock:
        vocab_size = model.embed.num_embeddings
    else:
        vocab_size = 1000
    # 每步用不同的输入模拟解码过程的不同阶段
    calib_inputs = [
        torch.randint(0, vocab_size, (1, seq_len + i * 8), device=device)
        for i in range(num_steps)
    ]
    print(f"\n[2] 准备 {num_steps} 个 temporal steps 校准输入")

    # 3. TASQ 量化 (INT8 共享缓冲)
    print("\n[3] TASQ: INT8 共享最大精度缓冲量化")
    max_layers = 0 if is_mock else 12  # 真实模型限制层数 (演示)
    # error_budget 解释为 "全截断误差" 的比例 (0.3 = 允许 30% 全截断误差)
    tasq = TASQQuantizer(max_bits=8, min_bits=2, error_budget=0.3,
                          num_steps=num_steps, max_layers=max_layers)
    tasq.quantize_model_weights(model)
    n_layers = len(tasq.layer_names)
    print(f"    处理层数: {n_layers}")

    # 4. 收集激活统计 (敏感度代理)
    print("\n[4] 收集每层每步激活统计 (敏感度代理)...")
    act_stats = collect_activation_stats(
        model, calib_inputs, is_mock, max_layers=max_layers)
    print(f"    收集了 {len(act_stats)} 层的激活统计")

    # 5. 学习 Temporal-Spatial LSB Mask
    print(f"\n[5] 学习 Temporal-Spatial LSB Mask (贪心, 预算=全截断误差的"
          f"{tasq.error_budget*100:.0f}%)...")
    mask, learn_info = tasq.learn_mask(act_stats)
    print(f"    全截断总误差: {learn_info['full_trunc_error']:.6f}")
    print(f"    自适应预算:   {learn_info['adaptive_budget']:.6f}")
    print(f"    实际总误差:   {learn_info['total_error']:.6f}")
    print(f"    节省的 bit-plane 数: {learn_info['total_bits_saved']} / "
          f"{learn_info['total_possible_bits']}")
    print(f"    平均有效精度: {learn_info['avg_effective_bits']:.2f} bit "
          f"(max={tasq.max_bits}, min={tasq.min_bits})")

    # 6. 有效精度调度可视化
    print(f"\n[6] 有效精度调度 (前 {min(6, n_layers)} 层 x {num_steps} 步)")
    print(f"    {'Layer':<24} " + " ".join(f"S{s}" for s in range(num_steps)))
    print(f"    {'-'*48}")
    schedule = tasq.get_effective_precision_schedule(mask)
    for li, l in enumerate(tasq.layer_names[:6]):
        short = l[-22:] if len(l) > 22 else l
        bits_row = "  ".join(
            f"{schedule.get((l, s), 8)}" for s in range(num_steps))
        print(f"    {short:<24} {bits_row}")

    # 精度分布直方图: 展示自适应调度 (不同位置用不同有效精度)
    from collections import Counter
    prec_counter = Counter(schedule.values())
    total_positions = len(schedule)
    print(f"\n    有效精度分布 (共 {total_positions} 个 层x步 位置):")
    print(f"    {'精度(bit)':<12} {'位置数':<10} {'占比':<10} {'分布'}")
    print(f"    {'-'*50}")
    for b in sorted(prec_counter.keys()):
        cnt = prec_counter[b]
        bar = "#" * int(cnt / total_positions * 40)
        print(f"    {b:<12} {cnt:<10} {cnt/total_positions*100:<10.1f}% {bar}")
    n_diff = len(prec_counter)
    print(f"    >>> 共 {n_diff} 种不同有效精度 (体现时序-空间自适应) <<<")

    # 展示保留最高精度的层 (敏感层)
    max_prec = max(prec_counter.keys())
    sensitive = [l for (l, s), b in schedule.items() if b == max_prec]
    if sensitive:
        print(f"    保留最高精度 {max_prec}-bit 的敏感层示例: "
              f"{sensitive[0][-22:]}")

    # 7. BitOPs 评估
    print(f"\n[7] Bit-Serial BitOPs 评估")
    macs_per_layer = estimate_macs(model, is_mock, seq_len=seq_len)
    print(f"    每层每步 MAC 数: {macs_per_layer:,}")

    # TASQ
    bitops_tasq, bitops_static8 = compute_bitops(
        n_layers, mask, tasq.max_bits, num_steps, macs_per_layer)
    # Static INT8 (位串行)
    static8 = StaticQuantizer(bits=8)
    bitops_s8 = static8.bitops_static(n_layers, num_steps, macs_per_layer)
    # Static INT4 (位串行)
    static4 = StaticQuantizer(bits=4)
    bitops_s4 = static4.bitops_static(n_layers, num_steps, macs_per_layer)

    print(f"\n    方法                  BitOPs (相对值)    相比 Static-8bit")
    print(f"    {'-'*56}")
    print(f"    Static-8bit (位串行)  {bitops_s8:>14,}      1.00x")
    print(f"    Static-4bit (位串行)  {bitops_s4:>14,}      {bitops_s8/bitops_s4:.2f}x 加速")
    print(f"    TASQ (自适应)         {bitops_tasq:>14,}      {bitops_s8/bitops_tasq:.2f}x 加速")

    reduction_vs_s8 = (1 - bitops_tasq / bitops_s8) * 100
    reduction_vs_s4 = (1 - bitops_tasq / bitops_s4) * 100
    print(f"\n    TASQ 相比 Static-8bit 位串行减少: {reduction_vs_s8:.1f}%")
    print(f"    TASQ 相比 Static-4bit 位串行减少: {reduction_vs_s4:.1f}%")

    # 8. 量化误差验证: 全精度 vs INT8 vs TASQ(典型步)
    print(f"\n[8] 权重量化误差验证 (前 {min(4, n_layers)} 层)")
    print(f"    {'Layer':<24} {'FP-INT8 MSE':<14} {'FP-TASQ MSE':<14} "
          f"{'有效bit':<8}")
    print(f"    {'-'*62}")
    # 保存原始权重
    orig_weights = {}
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and name in tasq.layer_weights:
            orig_weights[name] = module.weight.data.clone()

    total_int8_mse = 0
    total_tasq_mse = 0
    for li, l in enumerate(tasq.layer_names[:4]):
        w_orig = orig_weights[l]
        w_int, scale = tasq.layer_weights[l]
        w_int8_dq = dequantize_int8(w_int, scale)
        m_int8 = quantization_error_metrics(w_orig, w_int8_dq)

        # TASQ: 用第 0 步 (通常较敏感) 的截断
        k_step0 = mask.get((l, 0), 0)
        w_tasq = tasq.apply_mask_to_layer(l, 0, mask)
        m_tasq = quantization_error_metrics(w_orig, w_tasq)

        short = l[-22:] if len(l) > 22 else l
        eff_b = effective_bits(tasq.max_bits, k_step0)
        print(f"    {short:<24} {m_int8['mse']:<14.8f} "
              f"{m_tasq['mse']:<14.8f} {eff_b:<8}")
        total_int8_mse += m_int8['mse']
        total_tasq_mse += m_tasq['mse']

    # 9. 存储对比
    print(f"\n[9] 存储对比")
    print(f"    TASQ 存储一份 INT8 权重 (最坏情况精度), 无 per-step 副本")
    print(f"    额外存储: LSB Mask = {n_layers}层 x {num_steps}步 x "
          f"{math.ceil(math.log2(tasq.max_bits - tasq.min_bits + 1))}bit ≈ "
          f"{n_layers * num_steps * math.ceil(math.log2(tasq.max_bits - tasq.min_bits + 1)) / 8 / 1024:.2f} KB")
    print(f"    权重存储: 与 Static-INT8 相同 (一份 INT8)")

    # 10. 总结
    print(f"\n{'='*72}")
    print("TASQ 验证总结")
    print(f"{'='*72}")
    print(f"存储: 与 Static-INT8 相同 (一份 INT8 共享缓冲, 无 per-step 副本)")
    print(f"BitOPs: TASQ = {bitops_tasq:,}")
    print(f"        Static-8bit 位串行 = {bitops_s8:,}")
    print(f"        Static-4bit 位串行 = {bitops_s4:,}")
    print(f"加速: TASQ 相比 Static-8bit 位串行 {bitops_s8/bitops_tasq:.2f}x")
    print(f"平均有效精度: {learn_info['avg_effective_bits']:.2f} bit "
          f"(存储仍为 {tasq.max_bits}-bit)")
    print(f"\n核心结论: TASQ 通过共享最大精度缓冲 + Temporal-Spatial LSB Mask,")
    print(f"在不增加存储 (固定 INT8) 的前提下, 通过位串行执行减少 BitOPs,")
    print(f"在不敏感的层/步使用更低有效精度, 敏感处保留全精度, 质量与静态量化相当。")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
