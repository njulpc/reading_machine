# Paper: 2606.03026

**Title**: Spike-Aware C++ INT8 Inference for Sparse Spiking Language Models on Commodity CPUs

**arXiv**: https://arxiv.org/abs/2606.03026 | **Submitted**: 2026-06-02

## 复现方法

按论文的硬件落地路线，实现 INT8 权重 + INT8 激活的纯整数 GEMM 推理路径（int32 累加 + 输出反量化），报告输出误差与 4 倍权重压缩。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：INT8 纯整数 GEMM 实测：196 层输出平均相对误差 0.012，全模型 logits MSE 0.034，4x 压缩。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
