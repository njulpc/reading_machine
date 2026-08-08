# Paper: 2608.02691 - Output-Aware Rotation for INT2 KV-Cache Quantization

## 概述

本目录包含 Output-Aware Rotation (OAR) 方法在 Qwen3-0.6B 上的复现代码。OAR 是一种输出感知的正交旋转方法，用于 INT2 KV Cache 量化，通过保持注意力输出分布的稳定性来最小化精度损失。

## 运行方式

```bash
pip install torch transformers accelerate
python3 demo.py
```

## 文件说明

- `demo.py`: 主复现代码，包含 OAR 核心算法和 INT2 KV Cache 量化实现

## 方法说明

OAR 的核心洞察是：KV Cache 量化的目标不是保持 KV 自身的高精度，而是保持注意力输出的高精度。本实现包含：
1. 输出感知的正交旋转矩阵计算
2. INT2 KV Cache 量化
3. 三层级 KV Cache 存储架构（Hot/Warm/Cold）
4. Qwen3-0.6B 的注意力层适配

## 注意事项

- 代码设计为可在 CPU 上运行
- 若无法下载模型权重，代码逻辑仍可展示方法原理
- INT2 量化极度敏感，实际部署需仔细调参
