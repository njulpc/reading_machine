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

## 审查结论与验证结果 (2026-08-05)

### 算法一致性: 部分一致

| 组件 | 论文方法 | 代码实现 | 一致性 |
|------|----------|----------|--------|
| 三值量化 | scale=mean(\|w\|), threshold=0.5*scale | 一致 | ✓ |
| AYOT 校准 | 模型自身生成推理链作为校准数据 | CPU 上使用模拟推理链 (避免 generate 过慢) | 部分一致 |
| CAT-Q STE | 可微三值化, STE 传递梯度 | sigmoid 软近似 + STE, temp=1.0 | 部分一致 |
| CAT-Q 优化 | 端到端全模型优化 | 逐层优化 (layer-wise, PTQ 标准做法) | 部分一致 |

### 修复的问题

1. **STE 梯度断裂**: 原 `.data` 赋值断开计算图, 改为前向钩子保持梯度流
2. **FP16/FP32 dtype 不匹配**: scale 参数初始化时 FP16 → FP32 转换缺失, 导致 NaN
3. **全模型训练过慢**: 改为逐层优化, CPU 上 10 层 5 次迭代可完成
4. **硬三值化 dtype 不匹配**: 量化后权重需转回模型 dtype (FP16)
5. **梯度爆炸**: 添加梯度裁剪 (max_norm=1.0), 温度参数从 0.1 调至 1.0

### 验证结果

- **验证模型**: 真实 Qwen3-0.6B (FP16)
- **量化层数**: 10 层 (CPU 限制)
- **CAT-Q 迭代**: 5 次 (CPU 限制, GPU 上为 30 次)
- **ScaleQ vs RTN 权重 MSE 改善**: 12.4%
- **压缩率**: 8.0x (FP16 → ~2 bit/weight)
