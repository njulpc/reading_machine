# 2608.30034 — 输入自适应 UINT8 门控

## 实现范围

用真实 Qwen 线性层和固定输入，按激活强度阈值决定是否走 per-output-channel UINT8 路径。

## 运行

```bash
python3 scripts/quantization/2608.30034/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

未复现烟雾图像、Raspberry Pi 和 TFLite 内核；仅验证门控与 UINT8 数据流。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30034/demo.py`

```json
{
  "paper_id": "2608.30034",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "input-adaptive UINT8 front-end gating",
  "weight_granularity": "per-output-channel",
  "gate_threshold_q75": 0.8131343126296997,
  "gate_rate": 0.25,
  "mse": 8.148403139784932e-06,
  "cosine": 0.9999918937683105,
  "relative_l2": 0.004113812602232673
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF §3.1、§5.2 与 Appendix D，结论为**部分一致**。

- 原实现错误地用随机 Qwen activation mean 的 q75 作为门控；论文实际使用 15×15 dark-channel prior mean 和训练集拟合的固定阈值 `τ=0.585`，门控决定是否运行 dehazer，而不是是否量化。
- 修复：实现 15×15 dark-channel gate，并验证两幅 deterministic clear/dense-smoke 图像得到 `0.000760/0.750396`、门控 `false/true`；补 UINT8 affine scale/zero-point round-trip，MSE `1.1702e-06`。
- 实际命令：`python3 scripts/quantization/2608.30034/demo.py --output-json /private/tmp/arxiv_quant_review_20260902/2608.30034.json`，退出码 0。
- **真实 Qwen3-0.6B：未跑通/不适用**。论文对象是两套 UINT8 TFLite CNN 和 Raspberry Pi 4；未复现其 dehazer/edge 权重、60-image calibration、ODS/PSNR 或设备 latency。
- 环境同批次公共环境；JSON 导出已验证。
