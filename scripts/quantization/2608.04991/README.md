# RAC: Reference-Aware Activation Compression for Communication-Efficient Split LLM Inference

## 论文信息
- **标题**: RAC: Reference-Aware Activation Compression for Communication-Efficient Split LLM Inference
- **arXiv**: 2608.04991
- **关键词**: Split Inference, Activation Compression, Reference-Based Codec, Residual Quantization

## 方法概述

RAC 是一种面向分割推理 (Split Inference) 的激活压缩编解码器。在分割推理中，LLM
被拆分为设备端和服务器端两部分，中间激活需要通过网络传输，成为通信瓶颈。RAC 通过
利用历史激活中的精确 token 匹配来大幅降低传输比特数，同时保持任务精度。

核心包含三个组件：

1. **参考检索 (Reference Extraction & Retrieval)**：在 KV-Cache 或历史 prefill 中检索
   与当前 token 序列精确匹配的历史激活 span。相同的 token 子序列在不同上下文中会产生
   相似但不完全相同的激活，因此可以直接复用历史激活作为参考。

2. **分组仿射对齐 (Grouped Affine Alignment)**：由于相同 token 在不同上下文中的激活
   存在分布偏移，RAC 对参考 span 施加逐组仿射变换 `ref_aligned = ref * scale + zero`，
   其中 scale 和 zero 通过最小二乘在每个 group 上独立计算，使对齐后的参考尽可能接近
   当前激活，从而最小化残差。

3. **校准残差量化 (Calibrated Residual Quantization)**：对齐后计算残差
   `residual = current - ref_aligned`。残差幅值远小于原始激活，因此可用更少比特量化。
   支持多级残差量化（multi-bit residual），并可选地保留 prefill 阶段的异常通道
   (outlier channels) 全精度传输。

## 关键结果
- **TTFT (首 token 延迟) 比率**: 1.24-2.72x 加速
- **TPOT (每 token 延迟) 比率**: 1.01-2.79x 加速
- **任务分数变化**: -0.40 到 +2.50（多数场景精度无损甚至提升）

## 文件列表
- `demo.py` - RAC 激活压缩编解码器实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.04991
python3 demo.py
```

脚本会自动尝试加载 Qwen3-0.6B 模型；若无法下载则使用 Mock Transformer 保证可运行。
运行后输出参考检索命中率、分组仿射对齐效果、残差量化重建误差及压缩比对比，展示
RAC 相比直接量化的优势。
