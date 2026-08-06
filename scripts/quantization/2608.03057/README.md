# TASQ: Temporal-Adaptive Bit Sparsification Quantization

## 论文信息
- **标题**: TASQ: Temporal-Adaptive Bit Sparsification Quantization for Diffusion Models
- **arXiv**: 2608.03057
- **作者**: Seokho Han, Dongwei Wang, Jinhee Kim, Yiran Chen, Kang Eun Jeon, Huanrui Yang, Jong Hwan Ko
- **发表日期**: 2026-08-04
- **类别**: cs.CV
- **URL**: https://arxiv.org/abs/2608.03057

## 适配说明

TASQ 原始面向扩散模型 (diffusion) 的去噪轨迹。本实现将其核心思想适配到 LLM 推理：将扩散的 "denoising step" 类比为 LLM 的 "generation step (解码步)"，将 "layer" 作为空间维度，演示 Temporal-Spatial LSB Mask 的位稀疏化量化机制。

## 问题背景

静态量化为每个去噪步骤（时序步）分配同一权重精度。为保留质量，该精度必须满足最敏感的步骤，即使多数步骤本可用更少比特。这导致模型在多数步骤中重复支付最坏情况的算力开销。

## 方法概述

TASQ 分离 "存储成本" 与 "计算成本"，核心包含三个组件：

### 1. 共享最大精度权重缓冲 (Shared Max-Precision Buffer)
- 仅存储一份最高精度（如 INT8）的权重，不为每个 step 复制权重。
- 存储成本由最坏情况决定，固定不变。

### 2. Temporal-Spatial LSB Mask (时序-空间 LSB 掩码)
- 学习一个掩码 `M[layer, step]`，表示该 (层, 步) 要截断多少个最低有效位 (LSB)。
- 有效精度 = `max_bits - M[layer, step]`。
- LSB 截断：对整数权重做算术右移再左移，把 k 个 LSB 置零：
  ```
  x_trunc = round(x_int / 2^k) * 2^k
  ```
  这等价于把权重舍入到 2^k 的倍数，降低有效精度但不改变存储格式。

### 3. Bit-Serial 执行 (Temporal-Precision Engine)
- 位串行算术中，计算周期与有效精度成正比：`cycles ∝ effective_bits`。
- 切换精度无额外周期开销（只需改变处理多少个 bit-plane）。
- `BitOPs = sum_{layer,step} MACs * effective_bits`。

### 核心收益
- 存储不变（一份 INT8 权重）
- BitOPs 相比静态 INT8 位串行下降 25-50%
- 相比朴素静态 8-bit 位串行下降 6.1-7.5x
- 质量与静态量化相当（保留最敏感步骤的全精度）

## 代码使用说明

### 运行
```bash
cd scripts/quantization/2608.03057
python3 demo.py
```

### 核心组件
- `TASQQuantizer`：主量化器，INT8 共享缓冲 + LSB Mask 学习
- `quantize_weight_int8`：per-channel 对称 INT8 量化（共享缓冲）
- `truncate_lsb`：LSB 截断（算术移位置零 k 个最低位）
- `LSBMaskLearner`：贪心学习 Temporal-Spatial LSB Mask（背包问题近似）
- `collect_activation_stats`：收集每层每步激活统计作为敏感度代理
- `compute_bitops`：位串行 BitOPs 计算

### 对比基线
- **Static-8bit (位串行)**：所有层所有步全 8-bit
- **Static-4bit (位串行)**：所有层所有步全 4-bit

脚本会自动尝试加载 Qwen3-0.6B；若无法下载则使用 MockTransformer 保证可运行。运行后输出有效精度调度表、BitOPs 对比、权重量化误差验证。

## 依赖项
- Python >= 3.8
- PyTorch >= 1.10
- transformers (用于加载 Qwen3-0.6B，可选)
- 共享工具包 `quantization_toolkit.py`（上级目录）

## 文件列表
- `demo.py` - TASQ 完整实现与验证脚本
