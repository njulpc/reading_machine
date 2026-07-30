# 深度技术分析：Knowledge Distillation from Large Reasoning Models to Compact Student Models: A Case Study on the John O Bryan Mathematics Competition

> **arXiv ID**: [2606.31048](https://arxiv.org/abs/2606.31048)  |  **提交日期**: 2026-06-30  |  **分类**: cs.LG, cs.AI  |  **作者**: Gaurab Baral, Aaditya Khanal, Yangyang Tao 等
> **备注**: 15 pages, 3 figures, 7 tables. Code and data available at https://github.com/TempGaurab/Distillation.John-O-Bryan

> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。


---

## 一、核心速览

**研究主题**：Token 缩减（知识蒸馏、硬件部署、低秩分解、Token 缩减）—— 面向Qwen 系列 LLM的模型压缩

**一句话总结**：本文研究了面向Qwen 系列 LLM的Token 缩减方法/研究「Knowledge Distillation from Large Reasoning Models to Compact Student Models」，关键结果包括：64.67%。（基于摘要）

**技术标签**: distillation / hardware-deployment / low-rank / token-reduction


---

## 二、研究背景与动机 (Background & Motivation)

视觉 token 剪枝/合并与 token 选择技术针对多模态模型中视觉 token 数量庞大导致的计算瓶颈，在保持语义完整性的前提下动态缩减序列长度。核心问题包括重要性度量（注意力、相似度、谱性质）、空间结构保持与不同层级的渐进式缩减策略。

### 2.1 本文切入点

摘要开篇指出：

> This paper investigates knowledge distillation from a large reasoning model (DeepSeek-R1) to a compact student model (Qwen2.5-7B).


并进一步阐述了问题设定：

> Using historical problems from the John O'Bryan Mathematics Competition at Northern Kentucky University (2011-2025), we build a Chain-of-Thought (CoT) training corpus through a dual-agent framework.


从问题陈述看，作者针对的是Qwen 系列 LLM在Token 缩减场景下的具体瓶颈，属于 token-reduction 技术路线。


---

## 三、核心方法与创新点 (Methodology & Innovations)

根据摘要可识别的核心方法组件：

- **方法要点 1**：Using historical problems from the John O'Bryan Mathematics Competition at Northern Kentucky University (2011-2025), we build a Chain-of-Thought (CoT) training corpus through a dual-agent framework.
- **方法要点 2**：The dataset is used to fine-tune the student model with Low-Rank Adaptation (LoRA) on Apple Silicon hardware using the MLX framework.
- **方法要点 3**：The base Qwen2.5-7B model achieves 64.67% accuracy on competition problems, while the DeepSeek-R1 teacher achieves 91.40%.
- **方法要点 4**：An initial 1,000-iteration training run revealed severe overfitting, with validation loss reaching a minimum at iteration 200 before rising steadily.
- **方法要点 5**：Based on this finding, we ran five independent training runs each limited to 200 iterations with varied random seeds to assess result stability.

**方法学点评**：Token 缩减方法的关键评估点是：在不同缩减率下的精度-速度帕累托前沿，以及对空间/时序结构的保持。


---

## 四、实验设计与结果 (Experiments & Results)

摘要中报告的关键定量结果（原文句子摘录）：

- This paper investigates knowledge distillation from a large reasoning model (DeepSeek-R1) to a compact student model (Qwen2.5-7B).
- Using historical problems from the John O'Bryan Mathematics Competition at Northern Kentucky University (2011-2025), we build a Chain-of-Thought (CoT) training corpus through a dual-agent framework.
- The base Qwen2.5-7B model achieves 64.67% accuracy on competition problems, while the DeepSeek-R1 teacher achieves 91.40%.
- An initial 1,000-iteration training run revealed severe overfitting, with validation loss reaching a minimum at iteration 200 before rising steadily.
- Based on this finding, we ran five independent training runs each limited to 200 iterations with varied random seeds to assess result stability.
- Across these five runs, the fine-tuned student model achieves a mean accuracy of 69.43% (std dev 0.17%) on the competition dataset, a 4.76 percentage-point improvement over the base model, and generalizes to 73.1% (std dev 0.18%) on the MATH-500 benchmark.

**结果解读**：以上数字均直接引自摘要原文。评估该类工作时建议对照同月同方向工作（见月度报告横向比较表）判断其增益幅度。


---

## 五、局限性与未来展望 (Limitations & Future Work)

Token 缩减的风险是对细粒度视觉信息（小目标、文本区域）的破坏，以及在视频时序一致性上的影响。

此外，本文档基于摘要与 arXiv 元数据撰写，未获取全文，方法细节、实验设置与更完整的局限讨论以原文为准。


**未来展望**：未来方向：可学习缩减率、时序一致的视频 token 缩减。


---

## 六、学术启发 (Takeaways for My Research)

- token 重要性具有层级动态性：浅层重空间覆盖、深层重语义聚合
- 保持空间结构的缩减策略对检测/定位类任务至关重要
- 结合本文：可将「Knowledge Distillation from Large Reasoning Models to Compact Student Models」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。
