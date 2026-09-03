# 2609.02219 — AVIS 激活方差校准

## 实现范围

在 8 个真实 prompt 的首层激活上，以方差选择 4 个校准样本，比较随机选样并应用 INT8 bias correction。

## 运行

```bash
python3 scripts/quantization/2609.02219/demo.py --output-json /tmp/2609.02219.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。AVIS 与随机校准 MSE 均为 4.17197e-05；bias correction 降至 3.67724e-05。

```json
{
  "algorithm": "activation-variance informative INT8 calibration with output bias correction",
  "variances": [
    0.04610258340835571,
    0.04590262845158577,
    0.04412497580051422,
    0.045350346714258194,
    0.04263787344098091,
    0.0418323315680027,
    0.04410293698310852,
    0.043718013912439346
  ],
  "random_calibration": {
    "indices": [
      0,
      2,
      4,
      6
    ],
    "bound": 2.8125,
    "raw": {
      "mse": 4.171970795141533e-05,
      "mae": 0.004916583187878132,
      "cosine": 0.99984060334109,
      "relative_l2": 0.01796283759176731
    },
    "bias_corrected": {
      "mse": 3.6772449675481766e-05,
      "mae": 0.004637745674699545,
      "cosine": 0.9998578152261071,
      "relative_l2": 0.016864193603396416
    }
  },
  "avis_calibration": {
    "indices": [
      0,
      1,
      3,
      2
    ],
    "bound": 2.8125,
    "raw": {
      "mse": 4.171970795141533e-05,
      "mae": 0.004916583187878132,
      "cosine": 0.99984060334109,
      "relative_l2": 0.01796283759176731
    },
    "bias_corrected": {
      "mse": 3.6772449675481766e-05,
      "mae": 0.004637745674699545,
      "cosine": 0.9998578152261071,
      "relative_l2": 0.016864193603396416
    }
  },
  "paper_id": "2609.02219",
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
  "elapsed_seconds": 1.88014075,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

不是 YOLO/DPU、月球图像或辐射故障实验；本批 prompt 的最大幅值相同，AVIS 未胜随机，结果如实记录。
