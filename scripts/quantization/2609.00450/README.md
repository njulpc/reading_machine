# 2609.00450 — HBQ 分层块尺度

## 实现范围

真实 Qwen q_proj 切片在 block-256 W4 上比较 PoT 尺度与 4-bit significand 二级尺度。

## 运行

```bash
python3 scripts/quantization/2609.00450/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 Qwen3-0.6B 权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。

```json
{
  "paper_id": "2609.00450",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "HBQ-style large-block W4 with power-of-two exponent plus 4-bit significand scale",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.01646724999999999,
  "tensor_shape": [
    512,
    1024
  ],
  "block_size": 256,
  "weight_bits": 4,
  "significand_bits": 4,
  "pot_scale_metrics": {
    "mse": 1.8805934814736247e-05,
    "cosine": 0.989959898165508,
    "relative_l2": 0.1421685367822647
  },
  "hierarchical_sig_metrics": {
    "mse": 1.6037060049711727e-05,
    "cosine": 0.9914771583965905,
    "relative_l2": 0.13129666447639465
  },
  "sig_improves_mse": true
}
```

## 证据边界

未实现 W4A5 激活/KV、28nm ASIC、部分和 BQ 或端到端硬件能耗。
