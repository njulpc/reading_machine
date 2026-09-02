# 2609.00665 — SLM 与量化 LLM 可持续性比较

## 实现范围

在真实 Qwen 全模型上分别执行 INT8、NF4 与 group-W4，测量整模 logits 与生成；HSS 所需系统/安全指标不臆造。

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

## 代码审查与验证（2026-09-03，取代上述初始切片结果）

**算法一致性：部分一致。** 本文是 30 个“模型+量化格式+后端”的可持续性评测，不提出新量化算子。论文比较 BF16、bitsandbytes INT8/NF4、GPTQ4 和 llama.cpp GGUF Q4_K_M，并以五项能力、延迟/吞吐/VRAM、每 query/token 能耗与五条有害提示 ASR 归一化计算 HSS；只比较单个 q_proj 的 MSE 不能复现该结论。

本次把验证扩为三次真实整模加载，对全部 196 个 Transformer Linear/440,401,920 权重分别执行 per-row INT8、block-64 NF4 与 group-128 W4，随后实际前向和生成。INT8/NF4/W4 的 logits MSE 分别为 0.010912/0.283271/0.877805，cosine 为 0.999236/0.979732/0.936228，三条路径均生成成功、退出码 0。

```bash
python3 scripts/quantization/2609.00665/demo.py --self-test
python3 scripts/quantization/2609.00665/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.00665.json
```

环境为 macOS 26.6.2 arm64 CPU（CUDA/MPS 均不可用）、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0；三模式总墙钟 4.41 秒。**真实 Qwen3-0.6B：已跑通（三种整模 fake-quant 数值路径）。** 未安装/运行 bitsandbytes、GPTQ 或 GGUF 原生后端，也没有 A100、能耗计量、五任务和安全 ASR，因此没有计算并伪报 HSS。
