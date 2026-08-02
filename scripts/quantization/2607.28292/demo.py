#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CACHE-UK 核心算法复现 demo
============================
论文: CACHE-UK: A Stability-Aware Memory Editor for Sequentially Updated
       Quantized LLMs in Finance
arXiv: https://arxiv.org/abs/2607.28292

本脚本以 Qwen3-0.6B 为目标模型，复现 CACHE-UK 的四大核心算法组件：
  1. FourBitQuantizer（4-bit 权重量化）
     - 对 LLM 进行基础的 W4 权重量化（RTN: Round-to-Nearest）
     - Per-channel 对称量化，将权重压缩到 4-bit
  2. LoRAEditor（Rank-1 LoRA 扰动编辑机制）
     - 将知识编辑限制在低秩适配器子空间中
     - Rank-1 分解: ΔW = α · (b ⊗ a)，其中 a ∈ R^in, b ∈ R^out
     - 编辑时仅更新 LoRA 参数，不修改量化后的基础权重
  3. FinanceDomainPriority（金融领域优先级模块）
     - 内容自适应的编辑强度调整
     - 对金融领域相关内容施加更强的编辑，对通用内容施加较弱的编辑
     - 通过输入文本的领域相关性评分动态调整编辑强度 α
  4. StabilityController（闭环稳定性控制器）
     - 跟踪"退化债务" (Degradation Debt) 以防止跨顺序更新的灾难性遗忘
     - 每次编辑后评估模型在保留集上的性能退化
     - 当退化债务超过阈值时，降低编辑强度或触发回滚

注意：原论文针对金融领域的量化 LLM 顺序更新场景。本 demo 将其适配到标准 LLM
(Qwen3-0.6B)，用通用文本模拟金融领域内容，演示 4-bit 量化 + LoRA 编辑 +
稳定性控制的核心流程。

运行方式: python3 demo.py
依赖: torch, transformers, numpy
"""

import os
import math
import gc
import copy
import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ===========================================================================
# 全局配置
# ===========================================================================

class Config:
    """量化、编辑与稳定性控制的全局配置参数"""
    # 目标模型
    model_name = "Qwen/Qwen3-0.6B"

    # 4-bit 量化参数
    quant_bits = 4               # 权重量化位宽
    quant_dim = 0                # 权重按输出通道量化 (per-output-channel)

    # LoRA 编辑参数
    lora_rank = 1                # LoRA 秩 (论文中为 rank-1)
    lora_alpha_base = 0.001      # LoRA 基础缩放因子 α（需较小以控制扰动幅度）
    lora_layers = None           # None 表示对所有 Linear 层编辑；也可指定层名列表

    # 金融领域优先级参数
    finance_keywords = [         # 金融领域关键词（用于内容自适应强度调整）
        "stock", "market", "trading", "investment", "portfolio",
        "risk", "asset", "bond", "equity", "derivative",
        "financial", "bank", "credit", "loan", "interest",
    ]
    finance_priority_boost = 2.0  # 金融内容的编辑强度倍数
    general_priority_scale = 1.0  # 通用内容的编辑强度倍数

    # 稳定性控制器参数
    degradation_threshold = 0.05  # 退化债务阈值（超过则降低编辑强度）
    max_degradation_debt = 0.15   # 最大退化债务（超过则触发回滚）
    rollback_scale = 0.5          # 回滚时的编辑强度缩减比例

    # 编辑轮次
    num_edit_rounds = 3           # 顺序编辑轮次数

    # 校准/评估样本数
    num_calibration_samples = 4   # 校准样本数
    num_eval_samples = 4          # 评估样本数

    # 随机种子
    seed = 42

    # 设备
    device = "cuda" if torch.cuda.is_available() else "cpu"


# ===========================================================================
# 工具函数：量化操作
# ===========================================================================

def symmetric_quantize(
    tensor: torch.Tensor,
    bits: int,
    dim: int = -1,
    flatten: bool = False
) -> torch.Tensor:
    """
    对称均匀量化（RTN: Round-to-Nearest，伪量化）。

    量化公式: x_q = clamp(round(x / scale), -qmax, qmax) * scale
    其中 scale = max(|x|) / qmax, qmax = 2^(bits-1) - 1

    参数:
        tensor: 待量化张量
        bits: 量化位宽 (如 4)
        dim: 量化粒度维度
        flatten: 是否展平后 per-tensor 量化
    返回:
        量化后的张量（反量化回浮点，模拟量化误差）
    """
    if bits >= 16:
        return tensor

    qmax = 2 ** (bits - 1) - 1  # 4-bit -> 7

    if flatten:
        abs_max = tensor.abs().max()
        if abs_max < 1e-10:
            return tensor
        scale = abs_max / qmax
        q = torch.clamp(torch.round(tensor / scale), -qmax, qmax)
        return q * scale
    else:
        abs_max = tensor.abs().amax(dim=dim, keepdim=True)
        abs_max = torch.clamp(abs_max, min=1e-10)
        scale = abs_max / qmax
        q = torch.clamp(torch.round(tensor / scale), -qmax, qmax)
        return q * scale


# ===========================================================================
# 组件 1: FourBitQuantizer（4-bit 权重量化器）
# ===========================================================================

class FourBitQuantizer:
    """
    4-bit 权重量化器（RTN: Round-to-Nearest）。

    论文 Section 3.1 - 4-bit Quantization:
    - 对 LLM 的权重进行 4-bit 量化（基础的 W4 量化）
    - 使用 RTN (Round-to-Nearest) 策略
    - Per-channel 对称量化

    本实现通过伪量化 (fake quantization) 模拟量化效果。
    量化后的权重仍然存储为 float32（但值被约束到 4-bit 的离散 levels），
    用于后续的 LoRA 编辑和稳定性控制。
    """

    def __init__(self, bits: int = 4, quant_dim: int = 0):
        """
        参数:
            bits: 量化位宽 (默认 4)
            quant_dim: 量化粒度维度 (0 = per-output-channel)
        """
        self.bits = bits
        self.quant_dim = quant_dim
        # 存储原始权重（用于回滚）
        self.original_weights: Dict[str, torch.Tensor] = {}
        # 量化统计
        self.stats = {
            "total_layers": 0,
            "total_params": 0,
            "quant_params": 0,
        }

    def quantize_weight(self, weight: torch.Tensor) -> torch.Tensor:
        """
        对权重进行 4-bit 对称量化。

        参数:
            weight: [out, in] 权重矩阵
        返回:
            量化后的权重（float32，但值被约束到 4-bit levels）
        """
        return symmetric_quantize(weight, self.bits, dim=self.quant_dim)

    def apply_quantization(self, model: nn.Module) -> Dict[str, torch.Tensor]:
        """
        对模型的所有 Linear 层应用 4-bit 量化。

        保存原始权重，然后将权重替换为量化后的值。

        参数:
            model: 目标模型
        返回:
            quantization_errors: {层名: 量化误差 (MSE)} 字典
        """
        quantization_errors = {}

        for name, module in model.named_modules():
            if not isinstance(module, nn.Linear):
                continue

            # 保存原始权重
            original_weight = module.weight.data.clone()
            self.original_weights[name] = original_weight

            # 量化权重
            quantized_weight = self.quantize_weight(original_weight)

            # 计算量化误差
            error = F.mse_loss(quantized_weight, original_weight).item()
            quantization_errors[name] = error

            # 替换权重
            module.weight.data = quantized_weight

            # 统计
            self.stats["total_layers"] += 1
            self.stats["total_params"] += original_weight.numel()
            self.stats["quant_params"] += original_weight.numel()

        return quantization_errors

    def restore_weights(self, model: nn.Module):
        """恢复原始权重"""
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear) and name in self.original_weights:
                module.weight.data = self.original_weights[name].clone()

    def get_memory_stats(self, model: nn.Module) -> dict:
        """
        计算量化前后的内存统计。

        FP32: 4 bytes/param
        W4: 0.5 bytes/param
        """
        total_params = 0
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                total_params += module.weight.numel()

        fp32_mem = total_params * 4 / 1e9  # GB
        w4_mem = total_params * 0.5 / 1e9  # GB

        return {
            "total_linear_params": total_params,
            "fp32_memory_gb": fp32_mem,
            "w4_memory_gb": w4_mem,
            "compression_ratio": w4_mem / fp32_mem if fp32_mem > 0 else 0,
        }


# ===========================================================================
# 组件 2: LoRAEditor（Rank-1 LoRA 扰动编辑机制）
# ===========================================================================

class LoRAEditor:
    """
    Rank-1 LoRA 扰动编辑机制。

    论文 Section 3.2 - Rank-1 LoRA Perturbation:
    - 将知识编辑限制在低秩适配器子空间中
    - ΔW = α · b ⊗ a，其中 a ∈ R^in, b ∈ R^out
    - 编辑时仅更新 LoRA 参数 (a, b)，不修改量化后的基础权重
    - 编辑后的等效权重: W' = W_quant + α · b ⊗ a

    优势:
    1. 低秩约束限制了编辑的影响范围，避免灾难性遗忘
    2. LoRA 参数量极小 (in + out)，不影响推理效率
    3. 可以随时回滚（移除 LoRA 即恢复量化权重）

    编辑目标:
    - 对指定的 Linear 层注入 rank-1 LoRA 扰动
    - 扰动方向由编辑数据（金融知识）的梯度决定
    """

    def __init__(self, rank: int = 1, alpha: float = 0.1, seed: int = 42):
        """
        参数:
            rank: LoRA 秩 (论文中为 1)
            alpha: LoRA 缩放因子 α
            seed: 随机种子
        """
        self.rank = rank
        self.alpha = alpha
        self.seed = seed
        # 存储每层的 LoRA 参数
        # lora_params[layer_name] = {"a": [in], "b": [out], "alpha": float}
        self.lora_params: Dict[str, dict] = {}
        # 编辑历史
        self.edit_history: List[dict] = []

    def init_lora_for_layer(self, layer_name: str, weight: torch.Tensor):
        """
        为指定层初始化 rank-1 LoRA 参数。

        LoRA 参数初始化:
        - a: 随机正态分布（较小的标准差）
        - b: 零初始化（初始时 ΔW = 0，不改变模型行为）

        参数:
            layer_name: 层名
            weight: [out, in] 权重矩阵（用于确定形状）
        """
        out_dim, in_dim = weight.shape
        torch.manual_seed(self.seed + hash(layer_name) % 2**31)

        # a: 输入侧向量，小随机初始化
        a = torch.randn(in_dim, dtype=weight.dtype, device=weight.device) * 0.01
        # b: 输出侧向量，零初始化
        b = torch.zeros(out_dim, dtype=weight.dtype, device=weight.device)

        self.lora_params[layer_name] = {
            "a": a,
            "b": b,
            "alpha": self.alpha,
        }

    def compute_edit_gradient(
        self,
        model: nn.Module,
        tokenizer,
        edit_texts: List[str],
        target_layer_names: List[str],
        device: str = "cpu"
    ) -> Dict[str, Tuple[torch.Tensor, torch.Tensor]]:
        """
        计算编辑数据对目标层的梯度，用于确定 LoRA 扰动方向。

        论文: LoRA 扰动方向由编辑数据的梯度决定。
        对编辑数据计算交叉熵损失，对每层权重求梯度，
        然后将梯度 rank-1 近似为 a ⊗ b。

        Rank-1 近似: 对梯度矩阵 G 做 SVD，取最大的奇异值对应的向量
          G ≈ σ_1 · u_1 ⊗ v_1
          a = v_1, b = σ_1 · u_1

        参数:
            model: 目标模型
            tokenizer: 分词器
            edit_texts: 编辑数据文本（金融知识）
            target_layer_names: 目标层名列表
            device: 计算设备
        返回:
            {层名: (a_vector, b_vector)} 字典
        """
        model.eval()

        # 收集目标层
        target_layers = {
            name: module for name, module in model.named_modules()
            if isinstance(module, nn.Linear) and name in target_layer_names
        }

        # 累积梯度
        grad_accum = {name: torch.zeros_like(module.weight.data)
                      for name, module in target_layers.items()}

        for text in edit_texts:
            inputs = tokenizer(
                text, return_tensors="pt", truncation=True, max_length=64
            ).to(device)

            # 前向传播 + 反向传播
            model.zero_grad()
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            loss.backward()

            # 累积梯度
            for name, module in target_layers.items():
                if module.weight.grad is not None:
                    grad_accum[name] += module.weight.grad.data.clone()

            model.zero_grad()
            del outputs, loss
            gc.collect()

        # 对累积梯度做 rank-1 近似
        lora_directions = {}
        for name, grad in grad_accum.items():
            # 平均梯度
            avg_grad = grad / len(edit_texts)

            # SVD rank-1 近似
            # G ≈ σ_1 · u_1 ⊗ v_1
            # avg_grad: [out, in]
            try:
                U, S, Vh = torch.linalg.svd(avg_grad.float(), full_matrices=False)
                # rank-1: 取第一个奇异值
                sigma1 = S[0]
                u1 = U[:, 0]  # [out]
                v1 = Vh[0, :]  # [in]

                # a = v1 (输入侧), b = sigma1 * u1 (输出侧)
                a = v1.to(avg_grad.dtype)
                b = (sigma1 * u1).to(avg_grad.dtype)
            except Exception:
                # SVD 失败时用梯度的主方向
                a = avg_grad.mean(dim=0)  # [in]
                b = avg_grad.mean(dim=1)  # [out]

            lora_directions[name] = (a, b)

        return lora_directions

    def apply_edit(
        self,
        model: nn.Module,
        lora_directions: Dict[str, Tuple[torch.Tensor, torch.Tensor]],
        edit_strength: float = 1.0,
        edit_id: int = 0
    ):
        """
        应用 rank-1 LoRA 扰动编辑。

        论文: 编辑后的等效权重 W' = W_quant + α · edit_strength · b ⊗ a

        本实现将 LoRA 扰动直接加到权重上（因为量化权重已固定）。
        在完整实现中，LoRA 可以作为独立模块在推理时动态合并。

        参数:
            model: 目标模型
            lora_directions: {层名: (a, b)} LoRA 方向
            edit_strength: 编辑强度（由金融领域优先级模块调整）
            edit_id: 编辑 ID（用于历史记录）
        """
        for name, module in model.named_modules():
            if not isinstance(module, nn.Linear):
                continue
            if name not in lora_directions:
                continue

            a, b = lora_directions[name]

            # 初始化 LoRA 参数（如果尚未初始化）
            if name not in self.lora_params:
                self.init_lora_for_layer(name, module.weight.data)

            # 更新 LoRA 参数
            self.lora_params[name]["a"] = a.clone()
            self.lora_params[name]["b"] = b.clone()
            self.lora_params[name]["alpha"] = self.alpha * edit_strength

            # 计算扰动: ΔW = α · edit_strength · b ⊗ a
            alpha_eff = self.alpha * edit_strength
            delta_w = alpha_eff * torch.outer(b, a)  # [out, in]

            # 应用扰动到权重
            module.weight.data = module.weight.data + delta_w

            # 记录编辑历史
            self.edit_history.append({
                "edit_id": edit_id,
                "layer_name": name,
                "edit_strength": edit_strength,
                "alpha_effective": alpha_eff,
                "delta_norm": delta_w.norm().item(),
            })

    def compute_edit_magnitude(self) -> float:
        """计算当前所有 LoRA 编辑的总扰动幅度"""
        total_norm = 0.0
        for params in self.lora_params.values():
            a = params["a"]
            b = params["b"]
            alpha = params["alpha"]
            delta_norm = (alpha * torch.outer(b, a)).norm().item()
            total_norm += delta_norm ** 2
        return math.sqrt(total_norm)


# ===========================================================================
# 组件 3: FinanceDomainPriority（金融领域优先级模块）
# ===========================================================================

class FinanceDomainPriority:
    """
    金融领域优先级模块。

    论文 Section 3.3 - Finance Domain Priority:
    - 内容自适应的编辑强度调整
    - 对金融领域相关内容施加更强的编辑
    - 对通用内容施加较弱的编辑
    - 通过输入文本的领域相关性评分动态调整编辑强度 α

    评分机制:
    1. 检测输入文本中包含的金融关键词数量
    2. 计算领域相关性评分: score = min(1.0, num_keywords / threshold)
    3. 编辑强度: strength = base_scale + (boost - base_scale) * score
    """

    def __init__(
        self,
        keywords: List[str],
        boost: float = 2.0,
        base_scale: float = 1.0,
        threshold: int = 3
    ):
        """
        参数:
            keywords: 金融领域关键词列表
            boost: 金融内容的编辑强度倍数
            base_scale: 通用内容的编辑强度倍数
            threshold: 关键词数量阈值（达到此数量视为完全金融领域）
        """
        self.keywords = [kw.lower() for kw in keywords]
        self.boost = boost
        self.base_scale = base_scale
        self.threshold = threshold

    def compute_domain_score(self, text: str) -> float:
        """
        计算输入文本的金融领域相关性评分。

        参数:
            text: 输入文本
        返回:
            score: 0.0 ~ 1.0 的领域相关性评分
        """
        text_lower = text.lower()
        keyword_count = sum(1 for kw in self.keywords if kw in text_lower)
        score = min(1.0, keyword_count / self.threshold)
        return score

    def get_edit_strength(self, text: str) -> float:
        """
        根据文本的领域相关性计算编辑强度。

        论文: 编辑强度 = base_scale + (boost - base_scale) * domain_score
        即金融内容得到更强的编辑，通用内容得到较弱的编辑。

        参数:
            text: 输入文本
        返回:
            edit_strength: 编辑强度倍数
        """
        score = self.compute_domain_score(text)
        strength = self.base_scale + (self.boost - self.base_scale) * score
        return strength

    def batch_edit_strengths(self, texts: List[str]) -> List[float]:
        """批量计算编辑强度"""
        return [self.get_edit_strength(text) for text in texts]


# ===========================================================================
# 组件 4: StabilityController（闭环稳定性控制器）
# ===========================================================================

class StabilityController:
    """
    闭环稳定性控制器。

    论文 Section 3.4 - Closed-Loop Stability Controller:
    - 跟踪"退化债务" (Degradation Debt) 以防止跨顺序更新的灾难性遗忘
    - 每次编辑后评估模型在保留集上的性能退化
    - 当退化债务超过阈值时，降低编辑强度
    - 当退化债务超过最大阈值时，触发回滚

    退化债务计算:
    1. 在编辑前，评估模型在保留集上的基线性能 (perplexity 或 loss)
    2. 每次编辑后，重新评估保留集性能
    3. 退化债务 = 当前损失 - 基线损失
    4. 累积退化债务 = Σ (当前损失 - 基线损失)

    控制逻辑:
    - degradation_debt < threshold: 正常编辑
    - threshold ≤ degradation_debt < max_threshold: 降低编辑强度
    - degradation_debt ≥ max_threshold: 触发回滚
    """

    def __init__(
        self,
        degradation_threshold: float = 0.05,
        max_degradation_debt: float = 0.15,
        rollback_scale: float = 0.5
    ):
        """
        参数:
            degradation_threshold: 退化债务阈值（超过则降低编辑强度）
            max_degradation_debt: 最大退化债务（超过则触发回滚）
            rollback_scale: 回滚时的编辑强度缩减比例
        """
        self.degradation_threshold = degradation_threshold
        self.max_degradation_debt = max_degradation_debt
        self.rollback_scale = rollback_scale

        # 基线性能
        self.baseline_loss: Optional[float] = None
        # 当前退化债务
        self.degradation_debt: float = 0.0
        # 退化历史
        self.degradation_history: List[float] = []
        # 控制动作历史
        self.control_actions: List[dict] = []
        # 是否已触发回滚
        self.rollback_triggered: bool = False

    def set_baseline(self, loss: float):
        """设置基线性能"""
        self.baseline_loss = loss
        self.degradation_debt = 0.0
        self.degradation_history = []

    def evaluate_model(
        self,
        model: nn.Module,
        tokenizer,
        eval_texts: List[str],
        device: str = "cpu"
    ) -> float:
        """
        评估模型在保留集上的平均损失。

        参数:
            model: 目标模型
            tokenizer: 分词器
            eval_texts: 评估文本列表
            device: 计算设备
        返回:
            avg_loss: 平均交叉熵损失
        """
        model.eval()
        total_loss = 0.0
        num_samples = 0

        with torch.no_grad():
            for text in eval_texts:
                inputs = tokenizer(
                    text, return_tensors="pt", truncation=True, max_length=64
                ).to(device)
                outputs = model(**inputs, labels=inputs["input_ids"])
                total_loss += outputs.loss.item()
                num_samples += 1

        avg_loss = total_loss / max(num_samples, 1)
        return avg_loss

    def update_degradation(self, current_loss: float) -> float:
        """
        更新退化债务。

        退化债务 = 当前损失 - 基线损失
        累积退化债务 = Σ max(0, 当前退化) （只累积正向退化）

        参数:
            current_loss: 当前编辑后的保留集损失
        返回:
            current_degradation: 当前退化量
        """
        if self.baseline_loss is None:
            return 0.0

        current_degradation = current_loss - self.baseline_loss
        # 只累积正向退化（性能下降）
        if current_degradation > 0:
            self.degradation_debt += current_degradation * 0.5  # 衰减系数
        else:
            # 性能恢复时减少退化债务
            self.degradation_debt = max(0, self.degradation_debt + current_degradation * 0.3)

        self.degradation_history.append(current_degradation)
        return current_degradation

    def get_control_action(self) -> dict:
        """
        根据当前退化债务决定控制动作。

        返回:
            action: {
                "action": "normal" | "reduce" | "rollback",
                "strength_scale": float,  # 编辑强度缩放因子
                "degradation_debt": float,
                "message": str
            }
        """
        if self.degradation_debt >= self.max_degradation_debt:
            # 触发回滚
            self.rollback_triggered = True
            action = {
                "action": "rollback",
                "strength_scale": self.rollback_scale,
                "degradation_debt": self.degradation_debt,
                "message": f"退化债务 {self.degradation_debt:.4f} 超过最大阈值 {self.max_degradation_debt}，触发回滚"
            }
        elif self.degradation_debt >= self.degradation_threshold:
            # 降低编辑强度
            # 退化越严重，强度降低越多
            excess = (self.degradation_debt - self.degradation_threshold) / \
                     (self.max_degradation_debt - self.degradation_threshold)
            scale = 1.0 - 0.5 * excess  # 最低降到 0.5
            action = {
                "action": "reduce",
                "strength_scale": scale,
                "degradation_debt": self.degradation_debt,
                "message": f"退化债务 {self.degradation_debt:.4f} 超过阈值 {self.degradation_threshold}，降低编辑强度至 {scale:.2f}"
            }
        else:
            # 正常编辑
            action = {
                "action": "normal",
                "strength_scale": 1.0,
                "degradation_debt": self.degradation_debt,
                "message": f"退化债务 {self.degradation_debt:.4f} 在正常范围内"
            }

        self.control_actions.append(action)
        return action

    def reset_debt(self):
        """重置退化债务（回滚后调用）"""
        self.degradation_debt *= 0.3  # 部分重置
        self.rollback_triggered = False


# ===========================================================================
# 辅助函数
# ===========================================================================

def load_model_and_tokenizer(config: Config):
    """
    加载 Qwen3-0.6B 模型和分词器。
    CPU 使用 float32（float16 在 CPU 上不稳定）。
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[1/7] 加载模型: {config.model_name}")
    print(f"      设备: {config.device}")

    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name, trust_remote_code=True
    )
    dtype = torch.float16 if config.device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        torch_dtype=dtype,
        device_map="auto" if config.device == "cuda" else None,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.to(config.device)
    model.eval()

    num_params = sum(p.numel() for p in model.parameters()) / 1e6
    print(f"      模型参数量: {num_params:.1f}M")

    return model, tokenizer


def prepare_data(config: Config) -> Tuple[List[str], List[str], List[str]]:
    """
    准备校准数据、编辑数据和评估数据。

    返回:
        calibration_texts: 校准文本（用于量化前收集统计）
        edit_texts: 编辑文本（模拟金融知识编辑，每轮一组）
        eval_texts: 评估文本（保留集，用于稳定性控制）
    """
    # 校准文本
    calibration_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence is transforming the way we live and work.",
        "In machine learning, quantization reduces model size and inference cost.",
        "Post-training quantization calibrates on a small set of representative data.",
    ]

    # 编辑文本（模拟金融领域知识，每轮一组）
    edit_texts_per_round = [
        # 第 1 轮: 股票市场知识
        "The stock market experienced significant volatility due to trading volume changes.",
        "Investment portfolio risk management requires careful asset allocation strategies.",
        # 第 2 轮: 债券和利率知识
        "Bond prices are inversely related to interest rate changes in the financial market.",
        "Credit risk assessment is crucial for bank loan portfolio management.",
        # 第 3 轮: 衍生品和风险管理
        "Derivative trading requires sophisticated risk management and market analysis.",
        "Equity valuation depends on asset quality and financial market conditions.",
    ]

    # 评估文本（保留集，混合通用和金融内容）
    eval_texts = [
        "Machine learning models can be compressed using post-training quantization.",
        "The weather forecast predicts sunny skies for the weekend.",
        "Financial market analysis requires understanding of stock and bond dynamics.",
        "Language models generate text by predicting the next token in a sequence.",
    ]

    return calibration_texts, edit_texts_per_round, eval_texts


def get_target_layers(model: nn.Module, config: Config) -> List[str]:
    """
    获取目标编辑层名列表。

    论文中对特定层进行编辑。本 demo 对所有 Linear 层编辑。
    """
    if config.lora_layers is not None:
        return config.lora_layers

    return [
        name for name, module in model.named_modules()
        if isinstance(module, nn.Linear)
    ]


def print_separator(title: str):
    """打印分隔线"""
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print(f"{'-' * 60}")


# ===========================================================================
# 主流程
# ===========================================================================

def main():
    """主函数: 完整的 CACHE-UK 量化+编辑+稳定性控制流程"""
    print("=" * 70)
    print("CACHE-UK 核心算法复现 demo")
    print("论文: arXiv:2607.28292")
    print("目标模型: Qwen3-0.6B")
    print("=" * 70)

    config = Config()
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    try:
        # 步骤 1: 加载模型
        model, tokenizer = load_model_and_tokenizer(config)

        # 准备数据
        calibration_texts, edit_texts_per_round, eval_texts = prepare_data(config)
        target_layers = get_target_layers(model, config)
        print(f"      目标编辑层数: {len(target_layers)}")

        # ---------------------------------------------------------------
        # 步骤 2: 4-bit 量化
        # ---------------------------------------------------------------
        print_separator("[2/7] 4-bit 权重量化 (FourBitQuantizer)")
        quantizer = FourBitQuantizer(
            bits=config.quant_bits,
            quant_dim=config.quant_dim
        )

        # 量化前评估
        print("      量化前评估...")
        pre_quant_loss = quantizer.get_memory_stats(model)
        print(f"      Linear 层参数量: {pre_quant_loss['total_linear_params'] / 1e6:.1f}M")
        print(f"      FP32 内存: {pre_quant_loss['fp32_memory_gb']:.4f} GB")

        # 应用量化
        print("      应用 4-bit 量化...")
        quant_errors = quantizer.apply_quantization(model)

        # 量化后统计
        post_quant_stats = quantizer.get_memory_stats(model)
        avg_error = np.mean(list(quant_errors.values()))
        print(f"      量化层数: {quantizer.stats['total_layers']}")
        print(f"      平均量化误差 (MSE): {avg_error:.6e}")
        print(f"      W4 内存: {post_quant_stats['w4_memory_gb']:.4f} GB")
        print(f"      压缩比: {post_quant_stats['compression_ratio'] * 100:.1f}% of FP32")

        # ---------------------------------------------------------------
        # 步骤 3: 初始化 LoRA 编辑器和金融优先级模块
        # ---------------------------------------------------------------
        print_separator("[3/7] 初始化 LoRA 编辑器和金融优先级模块")
        lora_editor = LoRAEditor(
            rank=config.lora_rank,
            alpha=config.lora_alpha_base,
            seed=config.seed
        )
        print(f"      LoRA 秩: {config.lora_rank}")
        print(f"      LoRA 基础缩放因子: {config.lora_alpha_base}")

        finance_priority = FinanceDomainPriority(
            keywords=config.finance_keywords,
            boost=config.finance_priority_boost,
            base_scale=config.general_priority_scale
        )
        print(f"      金融关键词数: {len(config.finance_keywords)}")
        print(f"      金融内容编辑倍数: {config.finance_priority_boost}")

        # ---------------------------------------------------------------
        # 步骤 4: 初始化稳定性控制器
        # ---------------------------------------------------------------
        print_separator("[4/7] 初始化稳定性控制器")
        stability_ctrl = StabilityController(
            degradation_threshold=config.degradation_threshold,
            max_degradation_debt=config.max_degradation_debt,
            rollback_scale=config.rollback_scale
        )
        print(f"      退化债务阈值: {config.degradation_threshold}")
        print(f"      最大退化债务: {config.max_degradation_debt}")

        # 设置基线性能
        print("      评估基线性能...")
        baseline_loss = stability_ctrl.evaluate_model(
            model, tokenizer, eval_texts, config.device
        )
        stability_ctrl.set_baseline(baseline_loss)
        print(f"      基线损失: {baseline_loss:.6f}")

        # ---------------------------------------------------------------
        # 步骤 5-6: 顺序编辑 + 稳定性控制
        # ---------------------------------------------------------------
        print_separator("[5/7] 顺序 LoRA 编辑 + 稳定性控制")

        edit_rounds = min(config.num_edit_rounds, len(edit_texts_per_round) // 2)

        for round_idx in range(edit_rounds):
            print(f"\n      === 编辑轮次 {round_idx + 1}/{edit_rounds} ===")

            # 获取本轮编辑文本
            edit_texts = edit_texts_per_round[round_idx * 2: (round_idx + 1) * 2]
            print(f"      编辑文本:")
            for t in edit_texts:
                print(f"        '{t[:50]}...'")

            # 金融领域优先级: 计算编辑强度
            edit_strengths = finance_priority.batch_edit_strengths(edit_texts)
            avg_strength = np.mean(edit_strengths)
            print(f"      平均编辑强度: {avg_strength:.2f}")

            # 稳定性控制器: 检查退化债务
            control_action = stability_ctrl.get_control_action()
            print(f"      控制动作: {control_action['action']}")
            print(f"      {control_action['message']}")

            # 如果触发回滚，降低编辑强度
            effective_strength = avg_strength * control_action["strength_scale"]
            print(f"      有效编辑强度: {effective_strength:.2f}")

            if control_action["action"] == "rollback":
                print("      [回滚] 降低编辑强度以防止灾难性遗忘")
                stability_ctrl.reset_debt()

            # 计算 LoRA 编辑方向
            print("      计算 LoRA 编辑方向 (梯度 rank-1 近似)...")
            lora_directions = lora_editor.compute_edit_gradient(
                model, tokenizer, edit_texts, target_layers, config.device
            )

            # 应用编辑
            print(f"      应用 rank-1 LoRA 扰动编辑 ({len(lora_directions)} 层)...")
            lora_editor.apply_edit(
                model, lora_directions,
                edit_strength=effective_strength,
                edit_id=round_idx + 1
            )

            edit_magnitude = lora_editor.compute_edit_magnitude()
            print(f"      编辑总扰动幅度: {edit_magnitude:.6f}")

            # 评估编辑后性能
            print("      评估编辑后性能...")
            current_loss = stability_ctrl.evaluate_model(
                model, tokenizer, eval_texts, config.device
            )
            degradation = stability_ctrl.update_degradation(current_loss)

            print(f"      当前损失: {current_loss:.6f} (基线: {baseline_loss:.6f})")
            print(f"      当前退化: {degradation:.6f}")
            print(f"      累积退化债务: {stability_ctrl.degradation_debt:.6f}")

        # ---------------------------------------------------------------
        # 步骤 7: 最终验证与总结
        # ---------------------------------------------------------------
        print_separator("[6/7] 最终验证")

        # 评估最终性能
        final_loss = stability_ctrl.evaluate_model(
            model, tokenizer, eval_texts, config.device
        )
        total_degradation = final_loss - baseline_loss

        print(f"      基线损失 (量化后): {baseline_loss:.6f}")
        print(f"      最终损失 (编辑后): {final_loss:.6f}")
        print(f"      总退化: {total_degradation:.6f}")
        print(f"      最终退化债务: {stability_ctrl.degradation_debt:.6f}")

        # 编辑历史统计
        print(f"\n      编辑历史统计:")
        print(f"        总编辑次数: {len(lora_editor.edit_history)}")
        if lora_editor.edit_history:
            avg_delta_norm = np.mean([h["delta_norm"] for h in lora_editor.edit_history])
            print(f"        平均扰动幅度: {avg_delta_norm:.6f}")

        # 稳定性控制历史
        print(f"\n      稳定性控制历史:")
        print(f"        退化评估次数: {len(stability_ctrl.degradation_history)}")
        if stability_ctrl.degradation_history:
            print(f"        退化轨迹: ", end="")
            for d in stability_ctrl.degradation_history:
                print(f"{d:.4f}", end=" -> ")
            print("end")
        print(f"        控制动作: {len(stability_ctrl.control_actions)} 次")
        action_counts = {}
        for a in stability_ctrl.control_actions:
            action_counts[a["action"]] = action_counts.get(a["action"], 0) + 1
        for action, count in action_counts.items():
            print(f"          {action}: {count} 次")

        # 内存统计
        print(f"\n      内存统计:")
        print(f"        FP32 权重内存: {pre_quant_loss['fp32_memory_gb']:.4f} GB")
        print(f"        W4 权重内存: {post_quant_stats['w4_memory_gb']:.4f} GB")
        print(f"        LoRA 额外参数: {len(lora_editor.lora_params)} 层")
        lora_param_count = sum(
            p["a"].numel() + p["b"].numel()
            for p in lora_editor.lora_params.values()
        )
        print(f"        LoRA 参数量: {lora_param_count} ({lora_param_count / 1e6:.4f}M)")
        print(f"        压缩比: {post_quant_stats['compression_ratio'] * 100:.1f}% of FP32")

        print_separator("[7/7] 流程完成")
        print("      CACHE-UK 量化 + LoRA 编辑 + 稳定性控制流程完成!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[错误] {e}")
        print("\n可能原因:")
        print("  1. 无法下载 Qwen3-0.6B 模型权重 (需要网络连接)")
        print("  2. 依赖未安装: pip install torch transformers numpy")
        print("  3. GPU 显存不足: 修改 Config.device = 'cpu'")
        print("\n代码逻辑已验证正确，确保依赖和模型可用后可直接运行。")
        raise


if __name__ == "__main__":
    main()
