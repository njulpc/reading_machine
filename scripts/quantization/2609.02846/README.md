# 2609.02846 — UE5M3 FP4 block scaling

## 实现范围

以 E2M1 payload、block-16 比较 power-of-two 与 UE5M3 scale，并在真实 Qwen 激活上测输出误差。

## 运行

```bash
python3 scripts/quantization/2609.02846/demo.py --output-json /tmp/2609.02846.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。power-of-two/UE5M3 输出 MSE=0.000621194/0.000414082，UE5M3 cosine=0.998368。

```json
{
  "algorithm": "E2M1 FP4 payload with block-16 UE5M3 scale",
  "pow2_scale": {
    "mse": 0.0006211942527443171,
    "mae": 0.017786245793104172,
    "cosine": 0.9975608091440727,
    "relative_l2": 0.07001686841249466
  },
  "ue5m3_scale": {
    "mse": 0.0004140823148190975,
    "mae": 0.014732175506651402,
    "cosine": 0.9983684975433829,
    "relative_l2": 0.05716527998447418
  },
  "weight_pow2": {
    "mse": 1.2773345588357188e-05,
    "mae": 0.0026193871162831783,
    "cosine": 0.9934815795026009,
    "relative_l2": 0.11400716006755829
  },
  "weight_ue5m3": {
    "mse": 8.815600267553236e-06,
    "mae": 0.0021251984871923923,
    "cosine": 0.9955102303165052,
    "relative_l2": 0.09471075981855392
  },
  "paper_id": "2609.02846",
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
  "elapsed_seconds": 1.255066209,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

未复现 Nemotron-H 8B 的 188.7B-token 预训练、随机梯度舍入和原生 FP4 吞吐。
