# 深度技术分析：Does On-Policy Distillation Really Distill? From Noisy Teacher to Self-Improvement

> arXiv: [2608.31046](https://arxiv.org/abs/2608.31046)
> v1 提交日期：2026-08-31
> 分类：Machine Learning (cs.LG) ; Computation and Language (cs.CL)
> 证据范围：arXiv `/abs` + 官方 HTML 全文；以下数字只保留官方文本中可核对的表述。

## 1. 核心速览

**研究主题**：知识蒸馏与能力迁移。

**一句话总结**：However, the teacher scores student-generated trajectories that are inherently off-policy for it, so the reliability of its supervision, and hence the source of the student's improvement, remains unclear.

这篇工作的价值不只在于给出一个更省资源的配置，而在于把质量、资源预算与部署路径放进同一评估框架；是否值得采用，应以论文报告的任务、模型和硬件边界为准。

## 2. 研究背景与动机

- 原文背景证据：On-policy distillation (OPD) offers dense token-level supervision as an alternative to the sparse outcome-level advantages of reinforcement learning with verifiable rewards (RLVR).
- 原文背景证据：We quantitatively analyze teacher supervision during OPD training and find substantial noise whose prevalence increases with teacher scale.
- 原文背景证据：Surprisingly, the student policy is insensitive to such noise, converging to comparable performance regardless of whether noisy supervision is retained or removed.

从模型压缩视角看，核心矛盾是：减少参数、Token、缓存访问或高精度计算后，模型是否仍保留任务所需的信息。论文选择的切入点是可验证的资源瓶颈，而不是笼统地把“更小”当作“更快”。

## 3. 核心方法与创新点

1. **方法证据 1**：However, the teacher scores student-generated trajectories that are inherently off-policy for it, so the reliability of its supervision, and hence the source of the student's improvement, remains unclear.
2. **方法证据 2**：We quantitatively analyze teacher supervision during OPD training and find substantial noise whose prevalence increases with teacher scale.
3. **方法证据 3**：Surprisingly, the student policy is insensitive to such noise, converging to comparable performance regardless of whether noisy supervision is retained or removed.

全文结构中与方法和实验相关的章节包括：1 Introduction；2 Teacher Supervision in OPD Is Highly Noisy, but Students Improve Regardless；2.1 Preliminary；2.2 Noisy Teacher Signals in OPD；2.3 Students Are Insensitive to Noise in Teacher Supervision；3 Where Does Student Improvement Come From?；3.1 Which Tokens Contribute to OPD Training?；3.2 Which Learning Signals Drive Policy Improvement?；4 Methodology；4.1 Entropy Determines the Amount of Negative Signals；4.2 On-Policy Self-Adaptation；4.3 Why Does OPSA Work?；5 Experiments；5.1 Experimental Setup。

分析上需要注意：摘要中的方法名只是入口，真正可复现的对象是数据流、决策粒度、训练/校准信号和推理时额外开销。本文后续复现与评分均按这一口径判断。

## 4. 实验设计与结果

- **可核验结果**：However, the teacher scores student-generated trajectories that are inherently off-policy for it, so the reliability of its supervision, and hence the source of the student's improvement, remains unclear.
- **可核验结果**：Compared with the base \texttt{Qwen3-1.7B}, OPSA improves Avg@32 by 35.41 points on AIME24, corresponding to a 263\% relative gain, and more than doubles Pass@32 across all three benchmarks.
- **可核验结果**：It also outperforms OPD by 16.77 points in Avg@32 on AIME24.
- **可核验结果**：, OPSA improves Avg@32 by 35.41 points on AIME24, corresponding to a 263% relative gain, and more than doubles Pass@32 across all three benchmarks. It also outperforms OPD by 16.77 points in Avg@32 on AIME24.
- **可核验结果**：Training dynamics and performance of OPSA. OPSA eliminates the teacher supervision used in OPD, and further outperforms OPD by 12% in Avg@4. On
- **可核验结果**：, OPSA improves Avg@32 by 263-307% across mathematical reasoning benchmarks and more than doubles Pass@32.
- **可核验结果**：We find that teacher supervision in OPD is highly noisy and uncover a surprising insensitivity of the student policy to such noise. Training exclusively with noisy supervision, excluding noisy supervision, and standard OPD all converge to comparable accuracy after similar numbers of training steps.
- **可核验结果**：, OPSA improves Avg@32 by 263%–307% relative to the base model across the three benchmarks and more than doubles Pass@32 on each benchmark.

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

- [arXiv 摘要与 Submission history](https://arxiv.org/abs/2608.31046)
- [arXiv 官方全文](https://arxiv.org/html/2608.31046)
- 分类页出现位置：cs.LG new / New submissions (showing 185 of 185 entries)；cs.LG recent / Tue, 1 Sep 2026 (showing 336 of 336 entries )；cs.CL new / Cross submissions (showing 65 of 65 entries)；cs.CL recent / Tue, 1 Sep 2026 (showing 298 of 298 entries )
