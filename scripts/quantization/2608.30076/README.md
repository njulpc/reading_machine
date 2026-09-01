# 2608.30076 — 预算感知联合压缩流水线

## 实现范围

串联 20% 幅值剪枝、逐输出通道 W8 与逐 Token KV8，并计算联合存储倍率和误差。

## 运行

```bash
python3 scripts/quantization/2608.30076/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

单层小规模验证不等价于 70B/A40 的 33GB、57 token/s 端到端结果。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30076/demo.py`

```json
{
  "paper_id": "2608.30076",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "pruning + W8 + KV8 coupled pipeline",
  "prune_fraction": 0.19970321655273438,
  "estimated_compression": 2.4324324324324325,
  "weight": {
    "mse": 2.9194568469392834e-06,
    "cosine": 0.9984380006790161,
    "relative_l2": 0.055402403133965335
  },
  "kv": {
    "mse": 6.885582115501165e-05,
    "cosine": 0.9999300241470337,
    "relative_l2": 0.011886008603401069
  }
}
```
