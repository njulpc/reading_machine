# 深度技术分析：W4A4 Quantization for Inference on Wan2.2-I2V-A14B

> **arXiv ID**: [2606.29337](https://arxiv.org/abs/2606.29337)  |  **提交日期**: 2026-06-28  |  **分类**: cs.CV, cs.DC  |  **作者**: Yidong Chen, Chengyu Shi, Jiahao Liu
> **备注**: 4 pages, 8 figures; ICME 2026 Low-Bit-width Large-Model Quantization Challenge submission

> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。


---

## 一、核心速览

**研究主题**：量化硬件部署（量化、稀疏化）—— 面向大语言模型（LLM）的模型压缩

**一句话总结**：本文研究了面向大语言模型（LLM）的量化硬件部署方法/研究「W4A4 Quantization for Inference on Wan2.2-I2V-A14B」。（基于摘要）

**技术标签**: quantization / sparsity


---

## 二、研究背景与动机 (Background & Motivation)

量化算法的最终价值取决于硬件落地：FPGA、NPU、消费级 GPU 与嵌入式平台上的量化推理涉及整数-only 数据通路、混合精度 kernel、DSP 打包与内存层次优化等系统问题。算法-硬件协同设计（如面向特定数据通路的量化格式与融合算子）是实现真实加速比与能效收益的关键。

### 2.1 本文切入点

摘要开篇指出：

> We summarize our submission to Sub-Challenge 1: W4A4 Quantization for Inference (HiF4 / MXFP4) of the ICME 2026 Low-Bit-width Large-Model Quantization Challenge.


并进一步阐述了问题设定：

> The sub-challenge targets 4-bit weight and 4-bit activation inference on Wan-AI/Wan2.2-I2V-A14B under HiF4 or MXFP4 numerical formats.


从问题陈述看，作者针对的是大语言模型（LLM）在量化硬件部署场景下的具体瓶颈，属于 quant-hardware 技术路线。


---

## 三、核心方法与创新点 (Methodology & Innovations)

根据摘要可识别的核心方法组件：

- **方法要点 1**：The sub-challenge targets 4-bit weight and 4-bit activation inference on Wan-AI/Wan2.2-I2V-A14B under HiF4 or MXFP4 numerical formats.
- **方法要点 2**：We adapt two complementary ideas from LLM quantization, MixQ-style mixed precision for sparse activation outliers and SmoothQuant-style per-channel smoothing, together with block-wise HiF4 packing for Wan2.2 feed-forward linear layers.

**方法学点评**：硬件导向量化工作的评估应关注：报告的是峰值算力利用率还是端到端加速、是否包含量化/反量化开销、以及与现有推理框架（TensorRT-LLM、vLLM 等）的对比。


---

## 四、实验设计与结果 (Experiments & Results)

摘要中报告的关键定量结果（原文句子摘录）：

- We summarize our submission to Sub-Challenge 1: W4A4 Quantization for Inference (HiF4 / MXFP4) of the ICME 2026 Low-Bit-width Large-Model Quantization Challenge.
- The sub-challenge targets 4-bit weight and 4-bit activation inference on Wan-AI/Wan2.2-I2V-A14B under HiF4 or MXFP4 numerical formats.
- We adapt two complementary ideas from LLM quantization, MixQ-style mixed precision for sparse activation outliers and SmoothQuant-style per-channel smoothing, together with block-wise HiF4 packing for Wan2.2 feed-forward linear layers.
- Calibration on representative OpenS2V-5M batches identifies heavy-tailed activation channels; smoothing rebalances dynamic range before W4A4 rounding; and a dual-branch GEMM preserves outlier columns in higher precision while the bulk of channels use strict W4A4.
- On official VBench I2V metrics, our pipeline stays within 2-3.5 percent of FP16 on most quality axes and improves motion smoothness, outperforming a native HiFloat4 baseline that degrades roughly 5 percent relative to FP16 across all reported scores.

**结果解读**：以上数字均直接引自摘要原文。评估该类工作时建议对照同月同方向工作（见月度报告横向比较表）判断其增益幅度。


---

## 五、局限性与未来展望 (Limitations & Future Work)

硬件类工作的结论与特定平台绑定，跨平台可迁移性有限；报告的加速比也可能依赖特定的 batch/序列配置。

此外，本文档基于摘要与 arXiv 元数据撰写，未获取全文，方法细节、实验设置与更完整的局限讨论以原文为准。


**未来展望**：未来方向：编译器级量化 lowering、跨平台统一中间表示。


---

## 六、学术启发 (Takeaways for My Research)

- 算法-硬件协同设计的收益往往大于纯算法改进：为数据通路定制量化格式是实用捷径
- 端到端评测（含量化/反量化开销）是硬件论文的诚信底线
- 结合本文：可将「W4A4 Quantization for Inference on Wan2.2-I2V-A14B」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。
