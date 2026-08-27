# 深度技术分析：Beam Search, Self-Consistency, and the Limits of Inference-Time Scaling for Grammar-Constrained Text-to-SQL in Small Language Models

> arXiv: [2608.25761](https://arxiv.org/abs/2608.25761)
> v1 提交日期：2026-08-26
> 分类：cs.CL, cs.AI
> 作者：Ty Chermsirivatana, John MacCormick
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：其他压缩与高效推理；Beam Search, Self-Consistency, and the Limits of Inference-Time Scaling for Grammar-Constrained Text-to-SQL in Small Language Models。

**一句话总结**：该研究发现语法约束 Text-to-SQL 中，用更小 4-bit 模型换更宽搜索通常不如直接换大模型，beam search 又比等预算 sample-and-vote 更有效。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：One common trade-off in the use of large language models involves reducing the size of the model while increasing the amount of computation at inference time, for example by using a wider beam search. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- 在 Qwen2.5-Instruct 0.5B–7B、统一 4-bit 精度下控制模型尺度。
- 分别增加 beam width 与 sample-and-vote 数量。
- 在严格 SQL grammar 与匹配 inference budget 下比较准确率。

- 方法的核心区别是：该研究发现语法约束 Text-to-SQL 中，用更小 4-bit 模型换更宽搜索通常不如直接换大模型，beam search 又比等预算 sample-and-vote 更有效。

## 4. 实验设计与结果

Spider 1,034 个开发样本上，两种 test-time scaling 都更帮助小模型，但“模型变小、搜索变宽”的折中总体不占优；等预算 beam search 胜过 sample-and-vote。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

只有 Text-to-SQL、一个模型家族和一个量化精度；未对 4-bit 与全精度做消融，结果主要评价模型尺寸—推理算力而非量化算法。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

压缩后的额外 test-time compute 不应默认可补偿容量；必须在任务约束和等成本下验证。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
