# 2609.00718 — 压缩驾驶策略闭环评估

## 实现范围

在结构兼容的 mock 驾驶 actor 上执行 width-256→64 整单元剪枝、均衡教师蒸馏、静态 W8A8 校准与前向。

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

## 代码审查与验证（2026-09-03，取代上述初始 Qwen 切片结果）

**算法一致性：部分一致。** 论文对象是 MobileNetV3-small 感知加 width-256 MLP 驾驶 actor，不是 LLM。流程是按“入连接 L2 + 出连接 L2 + |bias|”整单元剪枝到 width 64，使用覆盖五个 curriculum 的 62,176 状态和归一化 Smooth-L1 做教师蒸馏，再以 per-channel symmetric weight/per-tensor affine activation 的 eager static INT8 做 PTQ。初始代码对 Qwen q_proj 做行剪枝和 rank-16 SVD，与论文不一致。

本次改为结构兼容的 width-256→64 actor，实际执行整单元剪枝、五阶段均衡 mock 状态上的教师蒸馏、校准、W8A8 fake-quant 和量化后动作前向。参数从 71,170 降至 5,506（92.26%），Smooth-L1 从 0.003353 降至 0.000561，INT8 后为 0.000562，退出码 0。

```bash
python3 scripts/quantization/2609.00718/demo.py --self-test
python3 scripts/quantization/2609.00718/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.00718.json
```

环境为 macOS 26.6.2 arm64 CPU、Python 3.9.6、PyTorch 2.8.0，墙钟 1.08 秒。**真实 Qwen3-0.6B：未跑通/不适用。** 论文模拟器、真实 62,176 状态、MobileNetV3 checkpoint 与 400 个闭环 episode 未在仓库提供；当前结果仅是明确标注的 seeded mock 算法路径。
