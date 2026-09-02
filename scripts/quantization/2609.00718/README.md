# 2609.00718 — 压缩驾驶策略闭环评估

## 实现范围

在真实 Qwen q_proj 子张量上依次执行 25% 结构化行剪枝、rank-16 教师残差恢复和 INT8，逐阶段测量输出损失。

## 运行

```bash
python3 scripts/quantization/2609.00718/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 `Qwen/Qwen3-0.6B` checkpoint，不下载权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。实际命令：

```bash
python3 scripts/quantization/2609.00718/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.00718.json
```

```json
{
  "paper_id": "2609.00718",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "structured row pruning + rank-16 teacher residual recovery + INT8 transfer proxy",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.019740291999999993,
  "pruned_row_fraction": 0.25,
  "distillation_rank": 16,
  "stages": {
    "pruned": {
      "mse": 0.10835307091474533,
      "cosine": 0.9408593823554481,
      "relative_l2": 0.33879730105400085
    },
    "distilled": {
      "mse": 0.08197833597660065,
      "cosine": 0.9555921805259084,
      "relative_l2": 0.29469239711761475
    },
    "integer_quantized": {
      "mse": 0.08198349177837372,
      "cosine": 0.9555893222513784,
      "relative_l2": 0.29470089077949524
    }
  }
}
```

## 证据边界

Qwen 不是驾驶策略；未复现 Gym-Duckietown 闭环课程，只验证论文强调的阶段化损伤定位。
