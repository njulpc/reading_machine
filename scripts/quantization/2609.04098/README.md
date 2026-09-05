# 2609.04098 — Qwen3-0.6B 数值验证

论文：[Why Gated DeltaNet Survives 4-Bit Quantization: NVFP4 W4A4 for the Recurrent Half of a Hybrid 27B LLM](https://arxiv.org/abs/2609.04098)。

Minima 给出混合GDN/注意力模型可部署的NVFP4校准及融合尺度协调方案。

## 实现范围

Qwen3.8-27B的496个线性层采用16元素块NVFP4，E4M3局部尺度加FP32全局尺度；对94组尺度重新协调，以128条32K文本校准，并研究FP8 KV缓存。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

No GDN in Qwen3-0.6B; no 27B/32K experiments or native FP4 GEMM. Static globals calibrated on four local texts, not paper 128x32K. FP8 KV calibration not integrated.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.04098/demo.py --output-json /tmp/2609.04098.json
```

可选指定检查点：

```sh
export QWEN_MODEL_PATH=/path/to/Qwen3-0.6B
```

校准文本与独立测试文本在`../numerics.py`明示。涉及全模型前向的验证使用不同的校准/测试文本；算子与码本测试仅检验组件误差，不做泛化声称。

## 实测结果与配置

```json
{
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca",
  "parameters": 596049920,
  "linears": 196,
  "quantized_elements": 440401920,
  "heldout_logits": {
    "mse": 0.5578979253768921,
    "relative_l2": 0.2331867516040802,
    "cosine": 0.974928617477417
  },
  "generation": {"new_token_id": 100678, "new_token_text": "为什么", "use_cache": false},
  "calibration_texts": [
    "量化需要校准激活。",
    "Compression balances quality and storage.",
    "不同层的数值范围并不相同。",
    "The cache grows with sequence length."
  ],
  "quantization": "nvfp4",
  "scale_harmonization": {"groups": 56, "worst_original_global_ratio": 5.13939393939394},
  "storage": "FP32 dequantized reference; no physical memory reduction claimed",
  "full_paper_reproduced": false,
  "weight_block": 16,
  "activation_block": 16,
  "scale_format": "E4M3 plus FP32 global",
  "harmonization_test": "PASS on real Qwen QKV and gate/up groups",
  "boundary": "No GDN in Qwen3-0.6B; no 27B/32K experiments or native FP4 GEMM. Static globals calibrated on four local texts, not paper 128x32K. FP8 KV calibration not integrated.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。

## 代码审查与验证（2026-09-05）

- 一致性结论：**部分一致**。NVFP4 的 16 元素块、E2M1 payload、E4M3 局部 scale、FP32 全局 scale 和融合组尺度协调与官方 v1 一致；但 Qwen3-0.6B 无 Gated DeltaNet，且本地校准只有 4 条短文本而非论文 128×32K。
- 修复：原脚本只对两个标量声称 harmonization PASS；现对真实 Qwen 的 28 个 QKV 组和 28 个 gate/up 组统一全局尺度，实际处理 56 组，原始全局尺度最大比值 5.139394，并补量化后前向与生成。
- 实测命令：`python3 scripts/quantization/2609.04098/demo.py --output-json /private/tmp/2609.04098.review.json`；退出码 0，墙钟 4.04 秒；196 个 Linear、440,401,920 权重，held-out logits cosine 0.974929，单 token 生成为“为什么”。
- 真实 Qwen3-0.6B：**NVFP4 W4A4 工程路径已跑通**；论文的 Qwen3.8-27B、240 个 GDN Linear、94 个实际融合 scale set、FP8 KV 校准、32K 评测和 Blackwell 原生 GEMM 未跑通。
