# 2609.00665 — SLM 与量化 LLM 可持续性比较

## 实现范围

在真实 Qwen q_proj 上比较 BF16、INT8、NF4 与 group-W4 的估算载荷、MSE 和余弦；迁移论文的多精度比较逻辑。

## 运行

```bash
python3 scripts/quantization/2609.00665/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 `Qwen/Qwen3-0.6B` checkpoint，不下载权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。实际命令：

```bash
python3 scripts/quantization/2609.00665/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.00665.json
```

```json
{
  "paper_id": "2609.00665",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "measured BF16/INT8/NF4/group-W4 sustainability proxy on a real Qwen projection",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.021031750000000016,
  "tensor_shape": [
    2048,
    1024
  ],
  "bf16_bits": 33554432,
  "variants": {
    "int8": {
      "estimated_bits": 17432576,
      "compression_vs_bf16": 1.9248120300751879,
      "mse": 3.749901011929069e-08,
      "cosine": 0.9999809130626459,
      "relative_l2": 0.0061781867407262325
    },
    "nf4": {
      "estimated_bits": 9437184,
      "compression_vs_bf16": 3.5555555555555554,
      "mse": 8.531654202670325e-06,
      "cosine": 0.9956575291982341,
      "relative_l2": 0.0931851863861084
    },
    "group_w4": {
      "estimated_bits": 9043968,
      "compression_vs_bf16": 3.710144927536232,
      "mse": 1.0830535757122561e-05,
      "cosine": 0.994532446577929,
      "relative_l2": 0.10499346256256104
    }
  }
}
```

## 证据边界

未运行论文的 30 个完整模型配置、能耗计量与安全提示评测。
