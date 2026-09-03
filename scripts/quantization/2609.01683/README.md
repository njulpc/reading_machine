# 2609.01683 — FORGE 前向统计重校准

## 实现范围

在首层真实激活上注入逐通道 gain/bias 漂移，INT8 投影前按干净统计做 forward-only re-normalization。

## 运行

```bash
python3 scripts/quantization/2609.01683/demo.py --output-json /tmp/2609.01683.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。重校准将输出 MSE 0.0141251→2.96737e-05，cosine 0.944702→0.999886。

```json
{
  "algorithm": "BN-folded forward-only channel renormalization around INT8 projection",
  "tokens": 10,
  "raw_corruption": {
    "mse": 0.014125061221420765,
    "mae": 0.08442076295614243,
    "cosine": 0.944701719521444,
    "relative_l2": 0.32966750860214233
  },
  "forward_only_adapted": {
    "mse": 2.9673654353246093e-05,
    "mae": 0.004129939246922731,
    "cosine": 0.9998859377253096,
    "relative_l2": 0.015110076405107975
  },
  "mse_recovery_fraction": 0.9978992194166036,
  "paper_id": "2609.01683",
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
  "elapsed_seconds": 2.956116125,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

未在 ESP32-S3、卷积网络或真实 corruption 数据集复现；FP32 重校准包围 INT8 数值路径。
