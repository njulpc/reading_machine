# 2609.01743 — SCULPT 的 PTQ-ready 激活裁剪

## 实现范围

对真实首层 Qwen 激活和 W4 权重比较 max-range A8 与 99.5% percentile 裁剪。

## 运行

```bash
python3 scripts/quantization/2609.01743/demo.py --output-json /tmp/2609.01743.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。max-range/裁剪 MSE 为 0.00120821/0.00570164；裸裁剪在此迁移上失败。

```json
{
  "algorithm": "W4A8 PTQ with exported percentile activation clipping",
  "tokens": 96,
  "clip_percentile": 0.995,
  "clip_bound": 0.96875,
  "max_range_ptq": {
    "mse": 0.0012082072207704186,
    "mae": 0.025680124759674072,
    "cosine": 0.9952521967473835,
    "relative_l2": 0.09843631088733673
  },
  "sculpt_clipped_ptq": {
    "mse": 0.005701637361198664,
    "mae": 0.04286693409085274,
    "cosine": 0.9829436119152885,
    "relative_l2": 0.21383735537528992
  },
  "paper_id": "2609.01743",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "transformers": "4.57.6",
    "platform": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false,
    "mps": false
  },
  "elapsed_seconds": 2.016145167,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

没有重新训练 Qwen 的拓扑正则；本次直接迁移使误差变差，是必须保留的负结果。
