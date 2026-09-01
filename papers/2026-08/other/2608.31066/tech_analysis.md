# 深度技术分析：Every Token Leaves a Ripple in the Stream of Thought: Eliciting Model-Internal Token Saliency for Chain-of-Thought Compression

> arXiv: [2608.31066](https://arxiv.org/abs/2608.31066)
> v1 提交日期：2026-08-31
> 分类：Computation and Language (cs.CL)
> 证据范围：arXiv `/abs` + 官方 HTML 全文；以下数字只保留官方文本中可核对的表述。

## 1. 核心速览

**研究主题**：缓存、Token 与高效推理结构。

**一句话总结**：Building on this view, we propose \textsc{MIST} (Model-Internal Saliency for Token-level CoT compression), which defines token importance along two complementary axes: \emph{necessity}, the drop in answer likelihood when a token's internal contribution is removed, and \emph{sufficiency}, the gain in answer likelihood when that contribution alone is provided.

这篇工作的价值不只在于给出一个更省资源的配置，而在于把质量、资源预算与部署路径放进同一评估框架；是否值得采用，应以论文报告的任务、模型和硬件边界为准。

## 2. 研究背景与动机

- 原文背景证据：Existing methods often rely on external scorers or heuristic signals only indirectly tied to the model's internal answer computation.
- 原文背景证据：We instead adopt a model-internal perspective: as the model forms an answer, each reasoning token leaves a ripple in the residual stream, the model's \emph{stream of thought}, and the magnitude of this ripple reflects the token's contribution to the answer computation.
- 原文背景证据：Combining the two yields a unified importance score for pruning.

从模型压缩视角看，核心矛盾是：减少参数、Token、缓存访问或高精度计算后，模型是否仍保留任务所需的信息。论文选择的切入点是可验证的资源瓶颈，而不是笼统地把“更小”当作“更快”。

## 3. 核心方法与创新点

1. **方法证据 1**：Building on this view, we propose \textsc{MIST} (Model-Internal Saliency for Token-level CoT compression), which defines token importance along two complementary axes: \emph{necessity}, the drop in answer likelihood when a token's internal contribution is removed, and \emph{sufficiency}, the gain in answer likelihood when that contribution alone is provided.

全文结构中与方法和实验相关的章节包括：1 Introduction；2 Related Work；3 MIST : Model-Internal Saliency for Token-level CoT Compression；3.1 Problem Formulation: A Model-Internal Notion of Token Importance；3.2 Quantifying Model-Internal Saliency in Practice；3.3 The Unified MIST Score；4 Experiments；4.1 Experimental Setup；4.2 Main Results；4.3 Generalization Beyond Mathematical Reasoning；4.4 Ablation Study；4.5 Token Type Analysis；4.6 Case Study；5 Conclusion。

分析上需要注意：摘要中的方法名只是入口，真正可复现的对象是数据流、决策粒度、训练/校准信号和推理时额外开销。本文后续复现与评分均按这一口径判断。

## 4. 实验设计与结果

- **可核验结果**：Chain-of-thought (CoT) reasoning improves multi-step problem solving, but long reasoning traces inflate inference cost.
- **可核验结果**：Token-level CoT compression reduces this cost by pruning full reasoning chains into shorter traces for model adaptation, making token selection the central challenge.
- **可核验结果**：Across four reasoning benchmarks and four models, \textsc{MIST} consistently outperforms baseline methods, suggesting that model-internal saliency provides an effective proxy for reasoning-token importance.
- **可核验结果**：improves the multi-step problem-solving ability of large language models (LLMs), but long reasoning traces increase latency, memory use, and serving cost.
- **可核验结果**：1.3-2.4 percentage-point (pp) accuracy drop on GSM8K with Qwen2.5-7B
- **可核验结果**：improves average accuracy by 5.3 pp on Qwen2.5-1.5B and 1.2 pp on Llama-3.1-8B, whereas TokenSkip drops by 4.1 pp and 2.3 pp, respectively. This suggests that the target model’s own internal computations provide a reliable signal for identifying the reasoning tokens it actually relies on.
- **可核验结果**：The remaining baselines use target-model signals such as gradients, perplexity, or attention weights, but map these signals to token importance through heuristic scoring rules.
- **可核验结果**：On GSM8K, GoGI incurs 11.9 and 9.2 pp accuracy drops with Qwen2.5-7B and Mistral-7B, respectively, compared with only 2.4 and 1.3 pp for

结果解读应同时检查比较基线、预算是否匹配、是否为端到端墙钟测试，以及压缩后质量是否在多个任务上稳定。摘要数字能证明作者报告的设置，但不能自动外推到其他模型、硬件或上下文长度。

## 5. 局限性与未来展望

- 本分析只采用 arXiv 官方页面与全文；没有把未公开代码、未报告硬件结果或第三方复现当成论文结论。
- 论文结果受其模型规模、训练数据、任务集与硬件实现约束；跨模型和跨硬件泛化仍需独立验证。
- 对压缩方法而言，平均指标可能掩盖最坏样本退化；未来应增加长上下文、分布外输入和端到端能耗审计。
- 若方法依赖定制 kernel、训练教师或大规模搜索，算法收益与工程成本应分开报告。

## 6. 学术启发

- 高效推理方法应同时报告算法复杂度、端到端延迟、内存占用以及质量退化，避免只用理论 FLOPs 代替部署收益。
- 缓存或 Token 压缩必须检查证据保真、长上下文鲁棒性与不同任务上的最坏情况，而非只看平均准确率。
- 一个可迁移的实验设计是：固定质量阈值后比较资源，或固定资源预算后比较质量，并额外报告端到端墙钟指标。

### 证据链接

- [arXiv 摘要与 Submission history](https://arxiv.org/abs/2608.31066)
- [arXiv 官方全文](https://arxiv.org/html/2608.31066)
- 分类页出现位置：cs.CL new / New submissions (showing 233 of 233 entries)；cs.CL recent / Tue, 1 Sep 2026 (showing 298 of 298 entries )
