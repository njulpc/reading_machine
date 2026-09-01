# 2608.30076 — 预算感知联合压缩流水线

## 实现范围

串联 20% 幅值剪枝、逐输出通道 W8 与逐 Token KV8，并计算联合存储倍率和误差。

## 运行

```bash
python3 scripts/quantization/2608.30076/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

单层小规模验证不等价于 70B/A40 的 33GB、57 token/s 端到端结果。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30076/demo.py`

```json
{
  "paper_id": "2608.30076",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "pruning + W8 + KV8 coupled pipeline",
  "prune_fraction": 0.19970321655273438,
  "estimated_compression": 2.4324324324324325,
  "weight": {
    "mse": 2.9194568469392834e-06,
    "cosine": 0.9984380006790161,
    "relative_l2": 0.055402403133965335
  },
  "kv": {
    "mse": 6.885582115501165e-05,
    "cosine": 0.9999300241470337,
    "relative_l2": 0.011886008603401069
  }
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF Figure 2、§4–6 和 Appendix A，结论为**部分一致**。

- 原实现的“20% 幅值剪枝 + W8 + token-wise KV8”与论文最终 `AWQ W4A16 -> ShortGPT 10/80 depth pruning -> PyramidKV + per-head symmetric INT8 KV` 不符。
- 修复：按正确阶段顺序执行 group-128 affine W4 数值代理、基于真实 hidden-state BI 的 3/28 层结构剪枝，并对实际 prefill cache 做逐头对称 INT8 量化后单 token decode；覆盖 196 个 Linear/440,401,920 权重。
- 实际命令：`python3 scripts/quantization/2608.30076/demo.py --tokens 64 --output-json /private/tmp/arxiv_quant_review_20260902/2608.30076.json`；剪除层 `[3,5,4]`，25 个有效 cache 层，logits MSE `4.502982`，生成 `下一个`，退出码 0，2.19 秒。
- **真实 Qwen3-0.6B：已跑通**缩短上下文 CPU 工程迁移；未跑通 activation-calibrated AWQ、1024-window PyramidKV eviction、10k token、70B/A40、吞吐/准确率预算。不得用本结果复述论文 33 GB/57 tok/s。
- 环境同批次公共环境；JSON 导出已验证。
