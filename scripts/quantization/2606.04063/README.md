# Paper: 2606.04063

**Title**: LLM Compression with Jointly Optimizing Architectural and Quantization choices

**arXiv**: https://arxiv.org/abs/2606.04063 | **Submitted**: 2026-06-02

## 复现方法

按论文的混合精度路线，先逐层测量 2/4/8-bit 量化敏感度（logits MSE），再在平均 4-bit 预算下做贪心比特分配，报告分配结果与精度。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：敏感度驱动比特分配实测：平均 4-bit 下 logits MSE 0.256（对比均匀 W4 基线 1.719）。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
