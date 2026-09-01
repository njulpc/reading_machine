# 2608.30384 — RSLM 训练自由向量量化

## 实现范围

对 Qwen 权重残差做 FWHT、2-bit Lloyd-Max 和最终向量范数校正。

## 运行

```bash
python3 scripts/quantization/2608.30384/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

论文目标是 ANN embedding；Qwen 权重只用于验证旋转、码本与 norm correction。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30384/demo.py`

```json
{
  "paper_id": "2608.30384",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "RSLM-style FWHT + 2-bit Lloyd-Max + final norm correction",
  "bits": 2,
  "centers": [
    -0.0524252,
    -0.0146392,
    0.0147866,
    0.0531571
  ],
  "mse": 0.0001531571615487337,
  "cosine": 0.9294860363006592,
  "relative_l2": 0.3755305310996975
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF §3.1–3.4、Table 2 和 §4，结论为**部分一致**。

- 原实现只有一次整向量 FWHT、数据拟合 1D Lloyd-Max 和 norm correction；论文 RSLM2 需要 block-128 两级 rotation、两套 sign、block permutation/interleave、标准高斯固定 2D/16 codebook、EVT initial scale、反变换与每向量 2-byte scale。
- 修复：实现上述 RSLM2 核心并在真实 Qwen 最后一层 64×1024 hidden states 上完成 encode/decode 和 MIPS 排名；静态表与 `Emax(D)` 使用 deterministic 工程近似并明确保留边界。
- 实际命令：`python3 scripts/quantization/2608.30384/demo.py --tokens 64 --output-json /private/tmp/arxiv_quant_review_20260902/2608.30384.json`；max norm error `3.0518e-05`、top-10 overlap `1.0`、MSE `1.033460`，退出码 0，1.14 秒。
- **真实 Qwen3-0.6B 模型量化：未跑通/不适用**；已跑通真实 Qwen hidden-state ANN codec。未复现 UE7M9 packing、relative/global codec、百万向量数据集和 AVX/ScaNN/Faiss 性能。
- 环境同批次公共环境；JSON 导出已验证。
