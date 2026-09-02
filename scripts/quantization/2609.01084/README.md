# 2609.01084 — 块扩散 LLM 的 KV/FFN 混合压缩

## 实现范围

真实 Qwen k_proj 生成 KV 代理，执行 rank-8+INT8 残差；真实投影权重执行中心化 INT4 delta。

## 运行

```bash
python3 scripts/quantization/2609.01084/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 `Qwen/Qwen3-0.6B` checkpoint，不下载权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。实际命令：

```bash
python3 scripts/quantization/2609.01084/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01084.json
```

```json
{
  "paper_id": "2609.01084",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "BRQ-KV rank-8 + INT8 residual and DAT-style centered INT4 delta proxy",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.019735332999999966,
  "kv_shape": [
    48,
    1024
  ],
  "kv_rank": 8,
  "kv_compression_vs_fp16": 1.4409005628517824,
  "kv_metrics": {
    "mse": 2.4620903786853887e-05,
    "cosine": 0.9999871819297508,
    "relative_l2": 0.0050632101483643055
  },
  "ffn_proxy_shape": [
    256,
    1024
  ],
  "ffn_delta_metrics": {
    "mse": 1.0982153980876319e-05,
    "cosine": 0.9947539999351883,
    "relative_l2": 0.10283062607049942
  },
  "ffn_compression_vs_fp16": 3.696750902527076
}
```

## 证据边界

未复现 WIFiV-LPDDR、专用脉动阵列和 Jetson 性能模型。
