# Paper: 2606.04115

**Title**: dMX: Differentiable Mixed-Precision Assignment for Low-Precision Floating-Point Formats

**arXiv**: https://arxiv.org/abs/2606.04115 | **Submitted**: 2026-06-02

## 复现方法

按论文的低比特浮点路线，实现 NVFP4/FP4（E2M1，块共享尺度）与 FP8（E4M3）权重量化，对比两种格式的相对误差与压缩倍率。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：FP4(E2M1, block=16) 实测：权重相对误差 0.094，logits MSE 1.191，~7.1x 压缩（含块尺度）。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
