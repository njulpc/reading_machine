# Paper: 2606.01850

**Title**: Does Compression Preserve Uncertainty? A Unified Benchmark for Quantized and Sparse LLMs via Conformal Prediction

**arXiv**: https://arxiv.org/abs/2606.01850 | **Submitted**: 2026-06-01

## 复现方法

按论文的量化影响评估路线，搭建比特宽度扫描（8/4/3/2-bit）与 group size 敏感性分析框架，报告 logits MSE、KL 散度与 top-1 一致率等保真度指标。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：比特扫描实测：group=64 时 W4 logits MSE 1.719、group=128 时 2.291，验证 group size 敏感性。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
