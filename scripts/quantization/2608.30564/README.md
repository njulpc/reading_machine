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

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF Algorithm 1/2、Eq.（1）–（3）和 Appendix B/E，结论为**部分一致**。

- 原实现仅在 7 个 q_proj 上按 weight MSE 做一次 DP；论文内层是 MoE block-output proxy 的 MCKP/Pareto cache，外层以完整量化模型 next-token JSD 做 lazy greedy descent；quantizer 为 group-128 asymmetric W1–W4（GPTQ），dense appendix 用 HQQ W2–W4。
- 修复：全部 196 个 Linear 先做 group-128 asymmetric W4，并以 full-precision logits JSD 对 `[0,9,18,27]` 四个 block 的 W3 候选做模型级选择，最终 block `[27,0]` 为 W3，其余 W4，平均 block bit `3.92857`。
- 实际命令：`python3 scripts/quantization/2608.30564/demo.py --output-json /private/tmp/arxiv_quant_review_20260902/2608.30564.json`；W4 baseline JSD `0.0331611`，最终 logits MSE `0.827265`，生成 `这`，退出码 0，2.12 秒。
- **真实 Qwen3-0.6B：已跑通** dense appendix 的缩小外层迁移；未跑通 MoE expert inner frontier、25 budget levels、完整 lazy descent、WikiText2 calibration、GPTQ/HQQ 或 GemLite/H100。
- 环境同批次公共环境；JSON 导出已验证。
