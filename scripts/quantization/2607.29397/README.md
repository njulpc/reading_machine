# 论文复现: Studying quantization trade-offs for efficient inference deployment in machine translation

**arXiv**: 2607.29397

## 论文概述

本文在真实服务环境下研究 W4A8/W8A8/W4A16 三种量化格式对机器翻译模型推理效率与翻译质量的权衡，重点关注文档级长上下文翻译中的量化-分块交互效应。

## 核心方法

### 1. 量化方案

| 方案 | 权重比特 | 激活比特 | SmoothQuant α | 说明 |
|------|---------|---------|---------------|------|
| W8A8 | 8 | 8 | 0.8 | 高强度平滑, 误差最小 |
| W4A8 | 4 | 8 | 0.4 | 平衡内存与精度 |
| W4A16 | 4 | 16 | N/A | 仅权重量化, 无平滑 |

### 2. SmoothQuant

将激活异常值迁移到权重侧，使得两者都更适合均匀量化：

```
x_i = x_i / s_i
w_i = w_i * s_i
s_i = max(|x_i|)^α / max(|w_i|)^(1-α)
```

### 3. GPTQ

基于 Hessian 信息的二阶量化，逐列量化权重并补偿误差：
- 计算 Hessian 矩阵 H = X^T @ X / N
- 逐列量化，使用 H 的逆补偿已量化列的误差

### 4. 文档分块策略

贪心连接完整源段落至 token 阈值 T，利用长上下文注意力捕获跨句依赖。

## 文件说明

- `demo.py`: 完整复现代码，包含：
  - `SmoothQuant`: 激活异常值平滑
  - `WeightQuantizer`: GPTQ/RTN 权重量化
  - `ActivationQuantizer`: Per-token INT8 激活量化
  - `QuantizationScheme`: W8A8/W4A8/W4A16 方案封装
  - `QuantizationPipeline`: 量化管道（校准 + 平滑 + 量化 + Hook）
  - `DocumentChunker`: 文档贪心分块策略
  - `MockTransformer`: 随机初始化的小型 Transformer（当无法下载模型时使用）

## 运行方式

```bash
cd scripts/quantization/2607.29397
python3 demo.py
```

无需 GPU 和模型下载，默认使用 mock 模型运行。设置环境变量 `USE_REAL_MODEL=1` 可尝试加载真实 Qwen3-0.6B 模型。

## 输出示例

程序会打印：
1. FP16 基线困惑度和模型大小
2. 三种量化方案（W8A8/W4A8/W4A16）的量化结果
3. 每种方案的困惑度变化、权重 MSE、压缩比
4. 量化方案对比汇总表
5. 关键发现总结

## 共享工具

本 demo 依赖 `scripts/quantization/quantization_toolkit.py` 中的：
- `SmoothQuant`: 激活平滑
- `GPTQQuantizer`: GPTQ 二阶量化
