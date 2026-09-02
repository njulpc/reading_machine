# 2609.00224 — QTEA 三值量化与半结构残差

## 实现范围

真实 Qwen q_proj 切片执行逐列三值赋值、显著列选择和列内 1:4 残差补偿。

## 运行

```bash
python3 scripts/quantization/2609.00224/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 Qwen3-0.6B 权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。

```json
{
  "paper_id": "2609.00224",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "QTEA-style by-column ternary weights plus salient-column 1:4 residual compensation",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.020958166,
  "tensor_shape": [
    512,
    1024
  ],
  "salient_column_fraction": 0.25,
  "residual_density": 0.0625,
  "estimated_effective_bits_per_weight": 3.125,
  "ternary_metrics": {
    "mse": 0.00031394368852488697,
    "cosine": 0.8690098527387462,
    "relative_l2": 0.5809196829795837
  },
  "compensated_metrics": {
    "mse": 0.00024123876937665045,
    "cosine": 0.8839877088656946,
    "relative_l2": 0.5092340111732483
  }
}
```

## 证据边界

未实现 GPTQ Hessian、误差衰减、论文 1.7 bit 精确存储布局或 LUT GPU 内核。
