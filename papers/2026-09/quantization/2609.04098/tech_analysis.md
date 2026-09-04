# Why Gated DeltaNet Survives 4-Bit Quantization: NVFP4 W4A4 for the Recurrent Half of a Hybrid 27B LLM

- arXiv ID：2609.04098
- 作者：Sergii Kozyrev, Davyd Maiboroda
- v1实际提交：2026-09-03T17:04:26Z（UTC）；2026-09-04T01:04:26+08:00（Asia/Shanghai）
- 主分类：Artificial Intelligence (cs.AI)；全部分类：Artificial Intelligence (cs.AI)
- 本次归类：量化；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.04098)；[官方HTML全文](https://arxiv.org/html/2609.04098)；[PDF](https://arxiv.org/pdf/2609.04098)

## 1. 核心速览

研究主题：量化。Minima 给出混合GDN/注意力模型可部署的NVFP4校准及融合尺度协调方案。

## 2. 研究背景与动机

混合架构存在不同数值敏感性，离线量化正确也可能在融合算子尺度约定中失效。

## 3. 核心方法与创新点

- Qwen3.8-27B的496个线性层采用16元素块NVFP4，E4M3局部尺度加FP32全局尺度
- 对94组尺度重新协调，以128条32K文本校准，并研究FP8 KV缓存。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.04098)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

权重50.13GiB降至17.53GiB（2.86倍）；五任务均值85.62降至85.10；TTFT 6.90降至4.03秒。32K困惑度BF16 10.35、NVFP4 10.84，加入缓存校准后10.50。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 9 | 权重50.13GiB降至17.53GiB（2.86倍）；五任务均值85.62降至85.10；TTFT 6.90降至4.03秒。32K困惑度BF16 10.35、NVFP4 10.84，加入缓存校准后10.50。 |
| 压缩倍率 | 9 | 权重50.13GiB降至17.53GiB（2.86倍）；五任务均值85.62降至85.10；TTFT 6.90降至4.03秒。32K困惑度BF16 10.35、NVFP4 10.84，加入缓存校准后10.50。 |
| 创新性 | 8 | Qwen3.8-27B的496个线性层采用16元素块NVFP4，E4M3局部尺度加FP32全局尺度；对94组尺度重新协调，以128条32K文本校准，并研究FP8 KV缓存。 |
| 可复现性 | 8 | 依赖Blackwell原生FP4和特定混合架构。Qwen3-0.6B不含GDN；演示验证FP4数值与尺度协调，没有27B、32K、原生GEMM或FP8 KV完整部署。 |

本地验证：以真实Qwen3-0.6B权重运行数值组件，结果状态`executed`，`full_paper_reproduced=false`。详见[README](../../../../scripts/quantization/2609.04098/README.md)及[原始结果](../../../../scripts/quantization/2609.04098/results.json)。

No GDN in Qwen3-0.6B; no 27B/32K experiments or native FP4 GEMM. Static globals calibrated on four local texts, not paper 128x32K. FP8 KV calibration not integrated.

## 5. 局限性与未来展望

依赖Blackwell原生FP4和特定混合架构。Qwen3-0.6B不含GDN；演示验证FP4数值与尺度协调，没有27B、32K、原生GEMM或FP8 KV完整部署。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

校准产物必须匹配运行时融合算子的尺度语义，部署约定本身就是量化算法的一部分。
