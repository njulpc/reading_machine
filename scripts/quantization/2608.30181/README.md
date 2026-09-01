# 2608.30181 — A.X K2 的 NVFP4 服务路径

## 实现范围

在真实 Qwen 权重上做 group-16 NVFP4 码本量化，并保留超阈值离群点。

## 运行

```bash
python3 scripts/quantization/2608.30181/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

没有 NVIDIA NVFP4 kernel，软件码本仅验证数值路径，不报告硬件吞吐。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30181/demo.py`

```json
{
  "paper_id": "2608.30181",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "NVFP4 group-16 with outlier guard",
  "group_size": 16,
  "outlier_rate": 0.08275604248046875,
  "mse": 8.17081490822602e-06,
  "cosine": 0.9956570863723755,
  "relative_l2": 0.09268416083882929
}
```
