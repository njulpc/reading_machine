# 2608.30181 — A.X K2 的 NVFP4 服务路径

## 实现范围

在真实 Qwen 权重上做 group-16 NVFP4 码本量化，并保留超阈值离群点。

## 运行

```bash
python3 scripts/quantization/2608.30181/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

没有 NVIDIA NVFP4 kernel，软件码本仅验证数值路径，不报告硬件吞吐。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30181/demo.py`

```json
{
  "paper_id": "2608.30181",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "NVFP4 group-16 with outlier guard",
  "group_size": 16,
  "outlier_rate": 0.08275604248046875,
  "mse": 8.17081490822602e-06,
  "cosine": 0.9956570863723755,
  "relative_l2": 0.09268416083882929
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF §2.2、§6.1 和 Table 14，结论为**部分一致**。

- 原实现只量化权重并人为保留 >5.5×scale 的 outlier；论文依靠 GN/SGA gate 抑制 outlier，报告的是 experts-only W4A4 NVFP4，block 示例为 16 元素，不存在该保留分支。
- 修复：全部 196 个 Qwen Linear 使用 block-16 E2M1，block scale 以 E4M3FN 编码；所有 Linear 输入通过 pre-hook 做 A4。首次实跑发现 E4M3FN scale 溢出导致非有限 logits，现已按格式最大有限值裁剪并复测。
- 实际命令：`python3 scripts/quantization/2608.30181/demo.py --output-json /private/tmp/arxiv_quant_review_20260902/2608.30181.json`；392 次 activation quant 调用，logits MSE `0.801791`、cosine `0.954884`，生成 `这`，退出码 0，2.00 秒。
- **真实 Qwen3-0.6B：已跑通** dense W4A4 数值迁移；未跑通 A.X K2 experts-only scope、GN/SGA architecture、NVIDIA NVFP4 kernel、688B/B200/NPU 实验。
- 环境同批次公共环境；JSON 导出已验证。
