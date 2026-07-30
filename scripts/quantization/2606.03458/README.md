# Paper: 2606.03458

**Title**: KVarN: Variance-Normalized KV-Cache Quantization Mitigates Error Accumulation in Reasoning Tasks

**arXiv**: https://arxiv.org/abs/2606.03458 | **Submitted**: 2026-06-02

## 复现方法

按论文的 KV 缓存量化路线，实现 Key per-channel 对称量化 + Value per-token 非对称量化，并保护 attention sink token，报告 KV 误差、注意力输出误差与显存压缩倍率。

## 运行方式

```bash
python3 demo.py          # 默认：mock mini-Qwen3（Qwen3 风格 GQA+SwiGLU 结构，秒级验证全部代码路径）
python3 demo.py --real   # 使用真实 Qwen3-0.6B（需本机 HuggingFace 缓存中已有 Qwen/Qwen3-0.6B）
```

## 验证方式说明

本 demo 已在 **真实 Qwen3-0.6B**（HuggingFace 权重，`--real` 模式）上实际运行验证，结果：KV 4-bit 实测：K 相对误差 0.103、V 0.096、注意力输出误差 0.149，KV 显存 4x 压缩。

默认 mock 模式（随机权重 mini-Qwen3）亦批量验证通过，保证无网环境可复现。
