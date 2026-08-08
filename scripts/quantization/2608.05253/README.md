# Paper: 2608.05253 - AuroOFT: Augmented Rotational Orthogonal Fine-Tuning

## 概述

本目录包含 AuroOFT 方法在 Qwen3-0.6B 上的复现代码。AuroOFT 是一种量化正交微调方法，通过学习增强型正交旋转来适配低比特语言模型。

## 运行方式

```bash
pip install torch transformers accelerate
python3 demo.py
```

## 文件说明

- `demo.py`: 主复现代码，包含 AuroOFT 核心算法和 Qwen3-0.6B 量化适配

## 方法说明

AuroOFT 的核心是在冻结量化权重的基础上，学习结构化正交旋转矩阵来调整激活分布。本实现包含：
1. 正交旋转矩阵的参数化（Cayley变换）
2. 量化感知的前向传播
3. 低秩近似的高效实现
4. Qwen3-0.6B 模型的逐层适配

## 注意事项

- 代码设计为可在 CPU 上运行（使用 `device_map="cpu"`）
- 若无法下载模型权重，代码逻辑仍可直接理解方法原理
- 实际微调需要额外的训练数据和较长的训练时间
