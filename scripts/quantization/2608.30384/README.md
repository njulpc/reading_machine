# 2608.30384 — RSLM 训练自由向量量化

## 实现范围

对 Qwen 权重残差做 FWHT、2-bit Lloyd-Max 和最终向量范数校正。

## 运行

```bash
python3 scripts/quantization/2608.30384/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

论文目标是 ANN embedding；Qwen 权重只用于验证旋转、码本与 norm correction。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30384/demo.py`

```json
{
  "paper_id": "2608.30384",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "RSLM-style FWHT + 2-bit Lloyd-Max + final norm correction",
  "bits": 2,
  "centers": [
    -0.0524252,
    -0.0146392,
    0.0147866,
    0.0531571
  ],
  "mse": 0.0001531571615487337,
  "cosine": 0.9294860363006592,
  "relative_l2": 0.3755305310996975
}
```
