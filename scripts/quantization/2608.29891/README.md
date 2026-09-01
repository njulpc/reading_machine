# 2608.29891 — MASQ 掩码感知时空量化

## 实现范围

把真实 Qwen 权重行构造成时间片，按 25% 结构掩码做 8 码字 VQ，并只在可见维度统计误差。

## 运行

```bash
python3 scripts/quantization/2608.29891/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

骨架关节语义无法映射到 LLM；验证的是掩码感知量化和 code switching 机制。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.29891/demo.py`

```json
{
  "paper_id": "2608.29891",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "mask-aware spatiotemporal vector quantization",
  "codebook_size": 8,
  "masked_feature_fraction": 0.25,
  "visible_mse": 7.825104209283988e-05,
  "code_switch_rate": 0.782608687877655
}
```
