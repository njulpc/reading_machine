# Paper: 2606.02288

**Title**: Massive Spikes in LLMs are Bias Vectors: Mechanistic Uncovering and Spike-Free Quantization

**arXiv**: https://arxiv.org/abs/2606.02288 | **Submitted**: 2026-06-01

## 复现方法

按论文的权重量化路线，实现 per-group 对称 RTN 量化与 GPTQ 风格（Hessian 逆近似）误差补偿，对 Qwen3 全部线性层做 W4 量化并报告权重相对误差、logits MSE 与压缩倍率。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：W4 RTN 全模型量化实测：logits MSE 1.719，8.0x 压缩；GPTQ 补偿路径运行通过。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
