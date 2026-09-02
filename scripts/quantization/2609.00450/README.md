# 2609.00450 — HBQ 分层块尺度

## 实现范围

真实 Qwen 全部 Transformer Linear、输入激活与 K/V 执行 HBQ-E B128/micro-B32 W4A5/KV4 数值参考。

## 运行

```bash
python3 scripts/quantization/2609.00450/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 Qwen3-0.6B 权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。

```json
{
  "paper_id": "2609.00450",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "HBQ-style large-block W4 with power-of-two exponent plus 4-bit significand scale",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.01646724999999999,
  "tensor_shape": [
    512,
    1024
  ],
  "block_size": 256,
  "weight_bits": 4,
  "significand_bits": 4,
  "pot_scale_metrics": {
    "mse": 1.8805934814736247e-05,
    "cosine": 0.989959898165508,
    "relative_l2": 0.1421685367822647
  },
  "hierarchical_sig_metrics": {
    "mse": 1.6037060049711727e-05,
    "cosine": 0.9914771583965905,
    "relative_l2": 0.13129666447639465
  },
  "sig_improves_mse": true
}
```

## 证据边界

未实现 W4A5 激活/KV、28nm ASIC、部分和 BQ 或端到端硬件能耗。

## 代码审查与验证（2026-09-03，取代上述初始切片结果）

**算法一致性：部分一致。** 论文的 HBQ-E 是 L1 block 128、micro-block 32、无符号 FP8 E5M3 L1 scale、W4(E2M1)/A5(E2M2)，并为权重逐 L1 block 在 2-bit SIG2/SIG3 中离线择优，激活/KV 使用 2-bit SIG1；初始实现的 block-256 PoT scale 加“4-bit significand”不是论文方案。

本次重写了两级 scale 和低比特浮点码本，将 HBQ-E W4 应用于全部 196 个 Transformer Linear，并在真实前向/带 cache 生成中对所有 Linear 输入执行 A5、对 K/V 投影输出执行 KV4。验证覆盖 440,401,920 个权重、392 次激活量化调用和 112 次 KV 调用。

```bash
python3 scripts/quantization/2609.00450/demo.py --self-test
python3 scripts/quantization/2609.00450/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.00450.json
```

环境为 macOS 26.6.2 arm64 CPU（CUDA/MPS 均不可用）、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0。均退出码 0；整模命令墙钟 8.33 秒，量化后 logits MSE 0.513373、cosine 0.963330，生成 token 为“这”。**真实 Qwen3-0.6B：已跑通（整模 W4A5/KV4 稠密参考）；28nm HBQ 加速器、MXINT8 partial-sum、bit packing、真实面积/能耗未跑通。**
