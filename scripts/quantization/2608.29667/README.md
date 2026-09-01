# 2608.29667 — QAT 综述的目标中心复现

## 实现范围

以 W4 对称 fake-quant、可学习 scale 和 STE 在真实 Qwen 权重切片上做 20 步校准。

## 运行

```bash
python3 scripts/quantization/2608.29667/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

综述没有单一新算法；这里复现其共同的 target-centric QAT 核心，不声称复现所有综述方法。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.29667/demo.py`

```json
{
  "paper_id": "2608.29667",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "target-centric symmetric W4 QAT/STE",
  "bits": 4,
  "granularity": "tensor slice",
  "steps": 20,
  "initial_mse": 0.0002069493057206273,
  "final_mse": 3.178762926836498e-05,
  "scale": 0.015030944719910622
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF 的 UAQ（式 1–2）、fake quant（式 3）、STE（式 4）及最小报告清单后，结论为**部分一致**：论文是综述，没有可称为“论文算法”的单一 W4 配方。

- 修复：由 256×256 权重切片改为真实加载 tokenizer/model；第一层逐输出通道 W4 scale 经 STE 校准，随后量化全部 196 个 Transformer Linear（440,401,920 个权重），执行量化后前向和 1-token greedy 生成。
- 实际命令：`python3 scripts/quantization/2608.29667/demo.py --steps 3 --output-json /private/tmp/arxiv_quant_review_20260902/2608.29667.json`。
- 结果：首层 MSE `2.7347e-05 -> 2.5035e-05`；整模 logits MSE `1.419209`、cosine `0.918308`，生成 token `这`，退出码 0，约 4.7 秒。
- **真实 Qwen3-0.6B：已跑通**，但仅代表 target-centric W4 fake-quant/STE 工程迁移，不代表综述中任一方法的完整训练、任务评测或整数 kernel。
- 环境：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；Apple arm64 CPU，CUDA/MPS 均不可用。JSON 导出已验证。
