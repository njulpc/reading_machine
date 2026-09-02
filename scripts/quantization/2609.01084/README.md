# 2609.01084 — 块扩散 LLM 的 KV/FFN 混合压缩

## 实现范围

真实 Qwen 全 28 层执行分 head rank-2 BRQ-KV 四级 residual view，并对全部 MLP 权重执行 DAT q8→q4 工程迁移。

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

## 代码审查与验证（2026-09-03，取代上述初始切片结果）

**算法一致性：部分一致。** 原论文针对 Fast-dLLM v2 块扩散：BRQ-KV 在每层/每 KV head 上保存 pre-RoPE rank-2 基座和 signed-INT8 residual master，根据 block query 将条目映射到 q8/q4/q2/q0；DAT-FFN 从 GPTQ q8 master 派生 q4/q2 view、拟合相邻低秩 correction，并按激活 drift 动态划分 replacement/delta/carry。初始代码误用 rank 8、统一 INT8 残差和普通中心化 INT4。

本次修正 rank=2、q8 master 与四级 residual view，对真实 Qwen 全 28 层 K/V 输出执行分 head 重建，并对全部 84 个 MLP Linear（264,241,152 权重）执行 q8→q4 view；带 cache 前向和生成共触发 112 次 KV hook，各 tier 3,584 条目。logits MSE 10.411431、cosine 0.628009，生成 token 为“正”，负面迁移如实保留。

```bash
python3 scripts/quantization/2609.01084/demo.py --self-test
python3 scripts/quantization/2609.01084/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01084.json
```

环境为 macOS 26.6.2 arm64 CPU（CUDA/MPS 均不可用）、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0，墙钟 2.09 秒。**真实 Qwen3-0.6B：已跑通（AR 工程迁移）。** 这不等于论文 Fast-dLLM v2 块扩散路径；query-dependent map 复用、DAT recurrent carry、GPTQ/低秩 correction、WIFiV-LPDDR 与 Jetson 周期/能耗模型未跑通。
