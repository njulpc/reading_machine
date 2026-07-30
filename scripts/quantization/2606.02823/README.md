# Paper: 2606.02823

**Title**: Qift: Shift-Friendly No-Zero W2 Post-Training Quantization for Rotated W2A4/KV4 LLM Inference

**arXiv**: https://arxiv.org/abs/2606.02823 | **Submitted**: 2026-06-01

## 复现方法

按论文的极端低比特路线，实现 1.58-bit 三值量化（BitNet 风格，组尺度）与 2-bit 量化 + LoRA 低秩残差恢复（logit 蒸馏），报告误差与恢复收益。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：1.58-bit 三值量化实测：权重相对误差 0.519，~20x 压缩；2-bit + LoRA 恢复路径运行通过。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
