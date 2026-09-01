# 深度技术分析：Improving Argument Saliency Coverage in Small LLMs for Long Legal Opinion Summarization via Sequence-Level Distillation

> arXiv: [2608.29884](https://arxiv.org/abs/2608.29884)
> v1 提交日期：2026-08-30
> 分类：Computation and Language (cs.CL)
> 证据范围：arXiv `/abs` + 官方 HTML 全文；以下数字只保留官方文本中可核对的表述。

## 1. 核心速览

**研究主题**：知识蒸馏与能力迁移。

**一句话总结**：Across student model sizes, distillation consistently surpasses tuning on expert-written summaries in our legal-opinion setting.

这篇工作的价值不只在于给出一个更省资源的配置，而在于把质量、资源预算与部署路径放进同一评估框架；是否值得采用，应以论文报告的任务、模型和硬件边界为准。

## 2. 研究背景与动机

- 原文背景证据：Across student model sizes, distillation consistently surpasses tuning on expert-written summaries in our legal-opinion setting.

从模型压缩视角看，核心矛盾是：减少参数、Token、缓存访问或高精度计算后，模型是否仍保留任务所需的信息。论文选择的切入点是可验证的资源瓶颈，而不是笼统地把“更小”当作“更快”。

## 3. 核心方法与创新点

1. **方法证据 1**：Across student model sizes, distillation consistently surpasses tuning on expert-written summaries in our legal-opinion setting.
2. **方法证据 2**：We further demonstrate that most gains are achieved with as few as ~10 training summaries, highlighting the strong data efficiency of teacher-generated supervision.
3. **方法证据 3**：Finally, we find that summary distillation is sufficient for improvements: reasoning-chain distillation remains competitive with summary-only distillation, but provides marginal benefit when combined with summary supervision.

全文结构中与方法和实验相关的章节包括：1 Introduction；2 Related Work；3 Distillation Setup；4 Experimental Setup；4.1 Dataset；4.2 Models；4.3 Baselines and Evaluation；5 Results and Discussion；5.1 Distillation Findings；5.2 Effect of Scaling Distillation Samples；6 Conclusion and Future Work；Limitations；Ethical Statement；References。

分析上需要注意：摘要中的方法名只是入口，真正可复现的对象是数据流、决策粒度、训练/校准信号和推理时额外开销。本文后续复现与评分均按这一口径判断。

## 4. 实验设计与结果

- **可核验结果**：We show that sequence-level distillation from a capable long-context teacher model is a simple, annotation-free, and data-efficient strategy for improving argument saliency coverage in long legal opinion summarization, where small LLMs often struggle to retain the most salient argumentative content.
- **可核验结果**：We further demonstrate that most gains are achieved with as few as ~10 training summaries, highlighting the strong data efficiency of teacher-generated supervision.
- **可核验结果**：Finally, we find that summary distillation is sufficient for improvements: reasoning-chain distillation remains competitive with summary-only distillation, but provides marginal benefit when combined with summary supervision.
- **可核验结果**：analyzes teacher and expert-summary perplexity, while Appendix
- **可核验结果**：Perplexity Analysis: Explaining Teacher Impact
- **可核验结果**：Perplexity distributions of teacher-generated and expert-written
- **可核验结果**：summaries, we analyze the perplexity of each summary type under
- **可核验结果**：perplexity under the student are closer to its pretraining

结果解读应同时检查比较基线、预算是否匹配、是否为端到端墙钟测试，以及压缩后质量是否在多个任务上稳定。摘要数字能证明作者报告的设置，但不能自动外推到其他模型、硬件或上下文长度。

## 5. 局限性与未来展望

- 本分析只采用 arXiv 官方页面与全文；没有把未公开代码、未报告硬件结果或第三方复现当成论文结论。
- 论文结果受其模型规模、训练数据、任务集与硬件实现约束；跨模型和跨硬件泛化仍需独立验证。
- 对压缩方法而言，平均指标可能掩盖最坏样本退化；未来应增加长上下文、分布外输入和端到端能耗审计。
- 若方法依赖定制 kernel、训练教师或大规模搜索，算法收益与工程成本应分开报告。

## 6. 学术启发

- 蒸馏信号要同时考虑教师信息量与学生可学习性；教师更强并不自动意味着监督更有效。
- 应分离“能力迁移”“数据增广”和“优化正则化”三种收益来源，并用消融确认真正的教师贡献。
- 一个可迁移的实验设计是：固定质量阈值后比较资源，或固定资源预算后比较质量，并额外报告端到端墙钟指标。

### 证据链接

- [arXiv 摘要与 Submission history](https://arxiv.org/abs/2608.29884)
- [arXiv 官方全文](https://arxiv.org/html/2608.29884)
- 分类页出现位置：cs.CL new / New submissions (showing 233 of 233 entries)；cs.CL recent / Tue, 1 Sep 2026 (showing 298 of 298 entries )
