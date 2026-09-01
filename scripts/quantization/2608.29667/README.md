# 2608.29667 — QAT 综述的目标中心复现

## 实现范围

以 W4 对称 fake-quant、可学习 scale 和 STE 在真实 Qwen 权重切片上做 20 步校准。

## 运行

```bash
python3 scripts/quantization/2608.29667/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

综述没有单一新算法；这里复现其共同的 target-centric QAT 核心，不声称复现所有综述方法。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.29667/demo.py`

```json
{
  "paper_id": "2608.29667",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "target-centric symmetric W4 QAT/STE",
  "bits": 4,
  "granularity": "tensor slice",
  "steps": 20,
  "initial_mse": 0.0002069493057206273,
  "final_mse": 3.178762926836498e-05,
  "scale": 0.015030944719910622
}
```
