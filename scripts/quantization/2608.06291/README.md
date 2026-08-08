# Paper: 2608.06291 - BaKron: Efficient Quantization with Kronecker-Factored Hessians

## 概述

本目录包含 BaKron 方法在 Qwen3-0.6B 上的复现代码。BaKron 将 KFAC 的 Kronecker 分解 Hessian 近似引入 GPTQ 风格的量化框架，利用输入激活和输出梯度的双重视角信息来指导量化舍入决策。

## 运行方式

```bash
pip install torch transformers accelerate
python3 demo.py
```

## 文件说明

- `demo.py`: 主复现代码，包含 BaKron 核心算法和 Qwen3-0.6B 量化实现

## 方法说明

BaKron 的核心改进在于使用 Kronecker 分解的 Hessian 近似来替代 GPTQ 中的对角近似：
1. 输入激活协方差矩阵 A
2. 输出梯度协方差矩阵 B
3. Kronecker 积 H ≈ A ⊗ B
4. 基于完整 Hessian 信息的舍入决策

## 注意事项

- 代码设计为可在 CPU 上运行
- 需要校准数据进行 Hessian 估计（脚本使用随机数据演示）
- 若无法下载模型权重，代码逻辑仍可展示方法原理
