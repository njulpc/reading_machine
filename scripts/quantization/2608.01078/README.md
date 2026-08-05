# ScaleQ-1.58: 1.58-Bit Ternary PTQ for Reasoning LLMs

## 论文信息
- **标题**: Attend to Your Own Thoughts: Breaking the Barrier for Post-Training Quantization of Reasoning LLMs through the Lens of 1.58-Bit Quantization
- **arXiv**: 2608.01078
- **作者**: Shigeng Wang, Chao Li, Yangyuxuan Kang, Jiawei Fan, Anbang Yao
- **代码**: https://github.com/IntelChina-AI/BitTern

## 方法概述

ScaleQ-1.58 是面向推理型 LLM 的三值 (1.58-bit) 训练后量化框架，将权重量化为 {-1, 0, 1}。包含三个核心组件：

1. **三值量化 (Ternary Quantization)**：权重映射到 {-1, 0, 1} × scale，scale = mean(|w|)，阈值 = 0.5 × scale。

2. **AYOT (Attend to Your Own Thoughts) 校准**：使用全精度模型自身生成的推理链 (chain-of-thought) 作为校准上下文，使量化过程能"看到"模型推理时的激活分布。

3. **CAT-Q (可微三值化)**：基于学习的可微三值化方法，前向使用硬三值化 (STE)，反向通过可学习 scale 和 threshold 参数优化量化误差。

## 文件列表
- `demo.py` - ScaleQ-1.58 量化完整实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.01078
python3 demo.py
```

脚本会自动尝试加载 Qwen3-0.6B 模型；若无法下载则使用 Mock Transformer 保证可运行。运行后对比 RTN 三值量化和 ScaleQ-1.58 (AYOT+CAT-Q) 的量化误差和输出误差。
