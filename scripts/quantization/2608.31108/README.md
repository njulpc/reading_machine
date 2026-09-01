# 2608.31108 — 量化评估结论稳健性压力测试

## 实现范围

在 Qwen 权重上同时报告 INT8/INT4 总体误差与四个固定子组误差，检查聚合指标是否掩盖异质性。

## 运行

```bash
python3 scripts/quantization/2608.31108/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

未复现 BBQ/BBQ-V 偏见评估与 GPU 能耗；只验证量化条件和子组审计协议。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.31108/demo.py`

```json
{
  "paper_id": "2608.31108",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "responsible-AI quantization stress test",
  "conditions": [
    "BF16 proxy",
    "INT8",
    "INT4"
  ],
  "results": {
    "8": {
      "overall": {
        "mse": 6.083788406385793e-08,
        "cosine": 0.9999425411224365,
        "relative_l2": 0.007997752529704501
      },
      "subgroup_mse": [
        6.880303260459186e-08,
        5.4051184861236834e-08,
        6.027148913290148e-08,
        6.022582255127418e-08
      ]
    },
    "4": {
      "overall": {
        "mse": 1.992105353565421e-05,
        "cosine": 0.9896743297576904,
        "relative_l2": 0.14472313839121428
      },
      "subgroup_mse": [
        2.2518504920299165e-05,
        1.7732527339830995e-05,
        1.9618970327428542e-05,
        1.9814211555058137e-05
      ]
    }
  }
}
```
