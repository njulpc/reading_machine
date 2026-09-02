# 2609.01200 — 分割式 VLM 的视觉 token 编码

## 实现范围

把真实 Qwen token embedding 接口执行均匀量化、字节编码/压缩/解码 round-trip，再继续完整 decoder 前向与生成。

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

## 代码审查与验证（2026-09-03，取代上述初始切片结果）

**算法一致性：部分一致。** 论文不做低秩变换：它截获 Qwen3-VL-8B-Instruct 的完整视觉接口（主 token tensor + 3 路 DeepStack），每路独立执行 ISO/IEC 15938-17 NNC uniform-approximation/dependent-quantization encode/decode，统一扫 QP，并把重建 tensor 放回原位置后继续 VQA。初始 rank-64 SVD+INT8 不是论文 codec。

本次删除该低秩说法，实现可核验的均匀量化、字节序列、zlib payload 与 decode round-trip，并用 hook 把真实 Qwen3-0.6B token embedding 重建值送入完整 decoder 前向和生成。8-bit 代理调用 2 次，BF16 source 65,536 bytes、payload 28,258 bytes，logits MSE 0.001353、cosine 0.999918，生成 token 为“这”，退出码 0。

```bash
python3 scripts/quantization/2609.01200/demo.py --self-test
python3 scripts/quantization/2609.01200/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01200.json
```

环境为 macOS 26.6.2 arm64 CPU（CUDA/MPS 均不可用）、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0，墙钟 3.41 秒。**真实 Qwen3-0.6B：已跑通（文本接口 codec 代理）。** 原论文 Qwen3-VL-8B 的四路视觉 tensor、NNC reference software/合规 bitstream、QP sweep 和 Video-MME 下游评测未跑通，因此不能把 2.32× 代理压缩率与论文结果直接比较。
