# 2609.01962 — Qwen 后训练三值化

## 实现范围

对首层 q_proj 的 256 行执行正交 Hadamard/KOTMS 风格旋转、group-128 affine ternary 与 rank-8 残差补偿。

## 运行

```bash
python3 scripts/quantization/2609.01962/demo.py --output-json /tmp/2609.01962.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。三值/补偿 MSE 为 0.00914294/0.00801944，补偿后 cosine=0.929254。

```json
{
  "algorithm": "Hadamard/KOTMS-style rotation, group-128 affine ternarization and low-rank error compensation",
  "target_rows": 256,
  "group_size": 128,
  "effective_bpw_estimate": 1.25048828125,
  "ternary": {
    "mse": 0.009142941795289516,
    "mae": 0.07439770549535751,
    "cosine": 0.9185334887533176,
    "relative_l2": 0.395343542098999
  },
  "compensated": {
    "mse": 0.008019444532692432,
    "mae": 0.07074769586324692,
    "cosine": 0.9292540165150659,
    "relative_l2": 0.37025752663612366
  },
  "zero_fraction": 0.43691253662109375,
  "paper_id": "2609.01962",
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
  "elapsed_seconds": 1.221288958,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

不是论文完整 Qwen3-4B、64×2048 校准、精确 TWLA/GPTQ 全模型转换或 Triton 内核。
