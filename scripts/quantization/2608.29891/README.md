# 2608.29891 — MASQ 掩码感知时空量化

## 实现范围

把真实 Qwen 权重行构造成时间片，按 25% 结构掩码做 8 码字 VQ，并只在可见维度统计误差。

## 运行

```bash
python3 scripts/quantization/2608.29891/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

骨架关节语义无法映射到 LLM；验证的是掩码感知量化和 code switching 机制。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.29891/demo.py`

```json
{
  "paper_id": "2608.29891",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "mask-aware spatiotemporal vector quantization",
  "codebook_size": 8,
  "masked_feature_fraction": 0.25,
  "visible_mse": 7.825104209283988e-05,
  "code_switch_rate": 0.782608687877655
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF 的 Methodology、JLSD、Temporal Patch Quantization 和式（2）–（5），结论为**部分一致**。

- 原实现把 Qwen 权重行平均后做普通 masked k-means；它没有整条 joint trajectory 的 JLSD、temporal patch、EMA codebook/inactive reset、commitment loss 或 visible-only velocity loss，不能称为 MASQ。
- 修复：使用 skeleton-shaped deterministic 输入执行 25% full-trajectory JLSD、patch=4、8-entry EMA VQ、inactive entry 恢复、commitment 与仅可见关节的一阶 velocity loss。
- 实际命令：`python3 scripts/quantization/2608.29891/demo.py --output-json /private/tmp/arxiv_quant_review_20260902/2608.29891.json`；commitment `0.0569451`、visible velocity loss `1.916567`、code-switch rate `0.90`，退出码 0。
- **真实 Qwen3-0.6B：未跑通/不适用**。论文量化的是骨架动作 latent token，不是 LLM 权重；未复现 TCN encoder/decoder、HuGaDB/LARa/BABEL 训练及分割指标。
- 环境同批次公共环境；该路径是原任务结构兼容 synthetic 核心验证，JSON 导出已验证。
