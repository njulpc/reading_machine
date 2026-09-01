# 2608.30564 — Q-Strata 分层位宽分配

## 实现范围

对 7 个跨层 Qwen q_proj 构造 2/3/4-bit Pareto 代价，在平均 3-bit 全局预算下动态规划。

## 运行

```bash
python3 scripts/quantization/2608.30564/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

Qwen3-0.6B 是 dense 模型；验证 outer allocator，未复现 MoE 专家级内层搜索。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30564/demo.py`

```json
{
  "paper_id": "2608.30564",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "Q-Strata-style hierarchical model-budget allocation",
  "layers": 7,
  "average_bits": 2.857142857142857,
  "allocated_bits": [
    3,
    2,
    3,
    3,
    3,
    3,
    3
  ],
  "summed_reconstruction_mse": 0.0008794675886747427
}
```
