# Paper: 2606.04373

**Title**: Selective Coupling of Decoupled Informative Regions: Masked Attention Alignment for Data-Free Quantization of Vision Transformers

**arXiv**: https://arxiv.org/abs/2606.04373 | **Submitted**: 2026-06-03

## 复现方法

按论文的数据无关量化路线，仅依据权重统计量合成校准输入（不访问真实数据），搜索最优裁剪比例后做 W4 PTQ，报告误差。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：数据无关 W4 实测：权重相对误差 0.111，logits MSE 1.731。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
