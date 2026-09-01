# 深度技术分析：Centering before Pruning: Lightweight Geometry Correction for Diversity-Based Visual Token Pruning in LVLMs

> arXiv: [2608.30263](https://arxiv.org/abs/2608.30263)
> v1 提交日期：2026-08-31
> 分类：Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI)
> 证据范围：arXiv `/abs` + 官方 HTML 全文；以下数字只保留官方文本中可核对的表述。

## 1. 核心速览

**研究主题**：剪枝、稀疏化与动态计算。

**一句话总结**：Based on this analysis, we propose the \textbf{Cen}tered Geometry \textbf{Prune}r (Cen-Prune), which measures subset diversity using centered cosine similarity while retaining raw-space distinctiveness as a complementary token-wise preference.

这篇工作的价值不只在于给出一个更省资源的配置，而在于把质量、资源预算与部署路径放进同一评估框架；是否值得采用，应以论文报告的任务、模型和硬件边界为准。

## 2. 研究背景与动机

- 原文背景证据：Large vision-language models (LVLMs) incur substantial inference costs due to their long and highly redundant visual-token sequences.
- 原文背景证据：Diversity-based pruning mitigates this cost by selecting token subsets based on pairwise cosine similarity.
- 原文背景证据：We find, however, that similarities between raw visual tokens are strongly concentrated in the positive range, limiting their ability to distinguish non-redundant tokens.

从模型压缩视角看，核心矛盾是：减少参数、Token、缓存访问或高精度计算后，模型是否仍保留任务所需的信息。论文选择的切入点是可验证的资源瓶颈，而不是笼统地把“更小”当作“更快”。

## 3. 核心方法与创新点

1. **方法证据 1**：Based on this analysis, we propose the \textbf{Cen}tered Geometry \textbf{Prune}r (Cen-Prune), which measures subset diversity using centered cosine similarity while retaining raw-space distinctiveness as a complementary token-wise preference.

全文结构中与方法和实验相关的章节包括：1 Introduction；2 Related Works；3 Preliminaries；4 Geometry Analysis and Cen-Prune；4.1 Visual Similarity Is Highly Concentrated；4.2 Mean Centering for Pure Diversification；4.3 Method: Cen-Prune；5 Experiments；5.1 Experimental Setups；5.2 Main Results；5.3 Ablation Studies and Further Analysis；6 Conclusion；References；Appendix。

分析上需要注意：摘要中的方法名只是入口，真正可复现的对象是数据流、决策粒度、训练/校准信号和推理时额外开销。本文后续复现与评分均按这一口径判断。

## 4. 实验设计与结果

- **可核验结果**：A natural way to improve this resolution is to center token features before computing cosine similarity.
- **可核验结果**：Extensive experiments across multiple image- and video-understanding benchmarks and LVLM architectures demonstrate that Cen-Prune provides robust improvements in overall performance across existing diversity-based pruners.
- **可核验结果**：. Consequently, visual tokens can occupy a substantial portion of the sequence processed by the language model. As attention cost grows quadratically with sequence length, visual tokens become a major source of latency and memory consumption
- **可核验结果**：As the retention budget tightens, the fraction of selected negative-cosine pairs rises under both matrices but far more steeply for centered selection (lines), while its relative accuracy stays below raw selection and the gap widens (bars).
- **可核验结果**：, centered selection underperforms its raw counterpart on most benchmarks, and its relative accuracy remains lower across token budgets, with the gap widening as the budget becomes more restrictive (Fig.
- **可核验结果**：, Cen-Prune with DivPrune and ZOO-Prune reaches 93.4% and 93.6% performance with only 32 retained tokens, matching the query-aware MMTok (93.4%). Cen-Prune also improves CDPruner across all evaluated budgets. On
- **可核验结果**：, it retains 96.1% performance while removing 88.9% of visual tokens. The gains extend to
- **可核验结果**：with dynamic-resolution inputs: at 90% token reduction, Cen-Prune retains 88.9% performance, versus 85.1% for DivPrune, 83.2% for MMTok, and 79.5% for CDPruner (Tab.

结果解读应同时检查比较基线、预算是否匹配、是否为端到端墙钟测试，以及压缩后质量是否在多个任务上稳定。摘要数字能证明作者报告的设置，但不能自动外推到其他模型、硬件或上下文长度。

## 5. 局限性与未来展望

- 本分析只采用 arXiv 官方页面与全文；没有把未公开代码、未报告硬件结果或第三方复现当成论文结论。
- 论文结果受其模型规模、训练数据、任务集与硬件实现约束；跨模型和跨硬件泛化仍需独立验证。
- 对压缩方法而言，平均指标可能掩盖最坏样本退化；未来应增加长上下文、分布外输入和端到端能耗审计。
- 若方法依赖定制 kernel、训练教师或大规模搜索，算法收益与工程成本应分开报告。

## 6. 学术启发

- 剪枝代理指标必须在最终被选中的 mask 附近验证，而不能只报告全局相关性。
- 参数稀疏、理论 FLOPs 与墙钟加速并不等价，部署内核是否能利用稀疏性是独立变量。
- 一个可迁移的实验设计是：固定质量阈值后比较资源，或固定资源预算后比较质量，并额外报告端到端墙钟指标。

### 证据链接

- [arXiv 摘要与 Submission history](https://arxiv.org/abs/2608.30263)
- [arXiv 官方全文](https://arxiv.org/html/2608.30263)
- 分类页出现位置：cs.CV new / New submissions (showing 260 of 260 entries)；cs.CV recent / Tue, 1 Sep 2026 (showing 316 of 316 entries )；cs.AI new / Cross submissions (showing 243 of 243 entries)；cs.AI recent / Tue, 1 Sep 2026 (showing 424 of 424 entries )
