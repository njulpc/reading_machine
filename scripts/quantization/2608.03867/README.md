# AdaMX: Heterogeneity-Aware Microscaling for Efficient Low-Bit LLM Inference

## 论文信息
- **标题**: Heterogeneity-Aware Microscaling for Efficient Low-Bit LLM Inference
- **arXiv**: 2608.03867
- **作者**: Junyi Luo, Xinting Jiang, Tai-Hao Wen, Ruichen Qi, Minxing Chu, Hongyi Wu, Gregory Kielian, Ben Laurie, Qirui Zhang, Quan Cheng, Dennis Sylvester, Mehdi Saligane
- **发表日期**: 2026-08-04
- **类别**: cs.AR
- **URL**: https://arxiv.org/abs/2608.03867

## 问题背景

Microscaling (MX) 已成为低比特 LLM 推理的标准格式。其 4-bit 形式 MXFP4 仍损失大量精度, 因为现有 MX 格式在所有块上固定元素格式或精度恢复方案 (precision-recovery scheme), 只能捕捉有限的量化异质性。

量化异质性出现在两个层级:
1. **跨块 (across blocks)**: 不同块偏好的元素格式和精度恢复方案不同
2. **跨操作数 (across operands)**: 权重和激活需要不同的编码

## 方法概述

### AdaMX (Adaptive Microscaling)
一种异质性感知的格式和加速器, 核心创新:

#### 1. Per-block 精度恢复方案选择
每个块独立选择最优的精度恢复方案, 适应块间异质性:

- **Scheme 0 (MXFP4)**: 标准 MXFP4, 共享指数 + FP4 元素
- **Scheme 1 (MXFP4+MS)**: MXFP4 + 每块微缩放 (额外 INT4 精细尺度因子), 恢复共享指数的量化损失
- **Scheme 2 (MXFP4+OL)**: MXFP4 + 离群值保持, 最大元素用 FP8 精确存储

每块选择 MSE 最小的方案, 用 2-bit scheme code 标记。

#### 2. Per-operand 编码
权重和激活使用不同的默认编码策略:
- **Weights**: 分布更均匀, 倾向 Scheme 0/1 (微缩放恢复精度)
- **Activations**: 有通道离群值, 倾向 Scheme 2 (离群值保持)

#### 3. EBW 保持不变
通过方案选择平衡开销, 确保不增加等效位宽 (Equivalent Bit Width):
- Block size 32: EBW = 4 + 8/32 = 4.25 bits/element
- Block size 16: EBW = 4 + 8/16 = 4.50 bits/element (低 EBW 工作点)

一个设计覆盖两种 block size, 提供高精度工作点和低 EBW 工作点。

### 论文结果
- AdaMX 在 22nm FD-SOI 加速器上仅增加约 1% 系统能耗
- 跨 3B-70B LLM, 消除 83% 的 MXFP4 在常识推理上的精度损失, 82% 在 MMLU 上
- 在 Gemma-4 12B 上保持最高 96% 的 FP16 精度

## 代码使用说明

### 运行
```bash
cd scripts/quantization/2608.03867
python3 demo.py
```

### 核心组件
- `MXFP4Quantizer`: 标准 MXFP4 量化器 (基线), 共享指数 + FP4 E2M1 元素
- `AdaMXQuantizer`: AdaMX 量化器, 支持 per-block scheme selection 和 per-operand encoding
  - `_scheme_mxfp4`: Scheme 0, 标准 MXFP4
  - `_scheme_mxfp4_ms`: Scheme 1, MXFP4 + INT4 微缩放
  - `_scheme_mxfp4_ol`: Scheme 2, MXFP4 + FP8 离群值保持
  - `quantize_block`: 尝试所有方案, 选 MSE 最小的
- `quantize_to_fp4`: FP4 E2M1 格式量化
- `quantize_model_weights_mxfp4`: 用 MXFP4 量化模型权重
- `quantize_model_weights_adamx`: 用 AdaMX 量化模型权重
- `quantize_activations_adamx`: 用 AdaMX 量化激活 (operand=activation)
- `collect_activations`: 收集各层激活用于评估

### 实验设计
1. **实验1**: 权重量化 MXFP4 vs AdaMX (per-block scheme selection)
2. **实验2**: 激活量化 MXFP4 vs AdaMX (per-operand: activation)
3. **实验3**: 两种 block size (32/16) 的 EBW-精度权衡
4. **实验4**: 端到端输出保真度对比

脚本会自动尝试加载 Qwen3-0.6B; 若无法下载则使用 MockTransformer 保证可运行。

## 依赖项
- Python >= 3.8
- PyTorch >= 1.10
- transformers (用于加载 Qwen3-0.6B, 可选)
- 共享工具包 `quantization_toolkit.py` (上级目录)

## 文件列表
- `demo.py` - AdaMX 量化器实现与验证脚本
