# 2608.30439 — 稀疏量化事件驱动激活

## 实现范围

在 Qwen 投影激活上按 40% 分位阈值置零，再做逐 Token INT4，并统计有效运算下降。

## 运行

```bash
python3 scripts/quantization/2608.30439/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

未复现神经形态芯片和训练阈值；软件路径不等价于论文 37x/16x 硬件预测。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30439/demo.py`

```json
{
  "paper_id": "2608.30439",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "trainable-threshold proxy + INT4 event-driven activations",
  "threshold_quantile": 0.4,
  "activation_sparsity": 0.399993896484375,
  "effective_op_reduction": 1.6666497126290627,
  "mse": 0.023033909499645233,
  "cosine": 0.9756960868835449,
  "relative_l2": 0.2201398437192899
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF Eq.（1）–（3）、§IV–V 和 Table II/III，结论为**部分一致**。

- 原实现对线性层输出硬置零后做 INT4；论文在每个 projection **输入前**应用 `sign(x)*ReLU(|x|-Δ)`，用 smooth surrogate（C=20）和 L0 proxy（k=10）训练 per-projection Δ；基模是 ternary weight + INT8 activation MMFreeLM。
- 修复：在真实 Qwen calibration prompt 上为 196 个 Linear 估计 per-projection Δ，全部权重工程三值化，输入执行论文前激活并逐 token INT8；量化后前向/生成覆盖 392 次 hook、9,748,480 activation elements。
- 实际命令：`python3 scripts/quantization/2608.30439/demo.py --output-json /private/tmp/arxiv_quant_review_20260902/2608.30439.json`；sparsity `0.330014`，logits MSE `17.778524`、cosine `0.351901`，生成 `hart`，退出码 0，1.91 秒。该明显退化是未经论文训练直接迁移的真实负结果。
- **真实 Qwen3-0.6B：已跑通**工程迁移；未跑通 4B-token continued training、MMFreeLM recurrent state、L0 warmup、Loihi 2 部署或论文 37×/16× 预测。
- 环境同批次公共环境；JSON 导出已验证。
