# 2608.30034 — 输入自适应 UINT8 门控

## 实现范围

用真实 Qwen 线性层和固定输入，按激活强度阈值决定是否走 per-output-channel UINT8 路径。

## 运行

```bash
python3 scripts/quantization/2608.30034/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

未复现烟雾图像、Raspberry Pi 和 TFLite 内核；仅验证门控与 UINT8 数据流。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30034/demo.py`

```json
{
  "paper_id": "2608.30034",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "input-adaptive UINT8 front-end gating",
  "weight_granularity": "per-output-channel",
  "gate_threshold_q75": 0.8131343126296997,
  "gate_rate": 0.25,
  "mse": 8.148403139784932e-06,
  "cosine": 0.9999918937683105,
  "relative_l2": 0.004113812602232673
}
```
