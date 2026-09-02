# 2609.01200 — 分割式 VLM 的视觉 token 编码

## 实现范围

把真实 Qwen embedding 行当作机器消费 token 表示，执行 rank-64 变换和 INT8 编码，测量率失真。

## 运行

```bash
python3 scripts/quantization/2609.01200/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 `Qwen/Qwen3-0.6B` checkpoint，不下载权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。实际命令：

```bash
python3 scripts/quantization/2609.01200/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01200.json
```

```json
{
  "paper_id": "2609.01200",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "training-free rank-64 transform plus INT8 entropy-coding proxy for real Qwen token representations",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.08198445900000001,
  "representation_shape": [
    256,
    1024
  ],
  "rank": 64,
  "estimated_compression_vs_fp16": 5.970845481049563,
  "metrics": {
    "mse": 0.00043889484368264675,
    "cosine": 0.7105138219057092,
    "relative_l2": 0.7036625146865845
  }
}
```

## 证据边界

未实现 ISO/IEC 15938-17 合规位流，也不等同论文视觉编码器的中间表示。
