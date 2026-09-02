# 2609.01587 — 量化损伤预算分配

## 实现范围

在八层真实 Qwen q_proj 切片上比较“最损伤层升 W8”和“所有层 group-32 W4”，并显式报告预算差。

## 运行

```bash
python3 scripts/quantization/2609.01587/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 `Qwen/Qwen3-0.6B` checkpoint，不下载权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。实际命令：

```bash
python3 scripts/quantization/2609.01587/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01587.json
```

```json
{
  "paper_id": "2609.01587",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "matched-near-budget causal local W8 repair versus globally finer group-W4 allocation",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.04238274999999997,
  "layers": 8,
  "worst_layer": 6,
  "local_estimated_bits": 10092544,
  "global_estimated_bits": 11010048,
  "global_to_local_budget_ratio": 1.0909090909090908,
  "summed_mse": {
    "local_repair": 6.501083391086127e-05,
    "global_granularity": 4.8273417860400514e-05
  },
  "global_better": true
}
```

## 证据边界

全局方案预算比局部方案高 9.09%，因此仅是近预算机制验证，不能替代论文九模型因果干预。
