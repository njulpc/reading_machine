# Paper: 2606.04349

**Title**: MorphoQuant: Modality-Aware Quantization for Omni-modal Large Language Models

**arXiv**: https://arxiv.org/abs/2606.04349 | **Submitted**: 2026-06-03

## 复现方法

按论文的权重量化路线，实现 per-group 对称 RTN 量化与 GPTQ 风格（Hessian 逆近似）误差补偿，对 Qwen3 全部线性层做 W4 量化并报告权重相对误差、logits MSE 与压缩倍率。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在本机批量验证：默认 mock mini-Qwen3 模式（与 Qwen3-0.6B 同族的 GQA + RMSNorm + SwiGLU 结构、随机权重）完整运行通过，覆盖全部代码路径与指标输出；`--real` 模式已实现并可用（需本机 HF 缓存含 Qwen/Qwen3-0.6B），本论文的 demo 未单独执行真实权重验证（同类代表性 demo 已实测，见月度报告复现清单）。
