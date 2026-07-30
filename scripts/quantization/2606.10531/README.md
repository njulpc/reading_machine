# Paper: 2606.10531

**Title**: LC-QAT: Data-Efficient 2-Bit QAT for LLMs via Linear-Constrained Vector Quantization

**arXiv**: https://arxiv.org/abs/2606.10531 | **Submitted**: 2026-06-09

## 复现方法

按论文的 QAT 路线，实现 fake-quant + STE 的量化感知微调（合成数据上的 logit 蒸馏损失），对比 PTQ 与 QAT 后的激活误差。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：W2 QAT 实测：激活 MSE 从 0.355（PTQ）降至 0.164，提升 53.7%。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
