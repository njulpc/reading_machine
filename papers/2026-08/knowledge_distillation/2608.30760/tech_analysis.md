# 深度技术分析：PRACTICE: From Experience to Expertise in Self-Evolving Embodied Agents

> arXiv: [2608.30760](https://arxiv.org/abs/2608.30760)
> v1 提交日期：2026-08-31
> 分类：Machine Learning (cs.LG)
> 证据范围：arXiv `/abs` + 官方 HTML 全文；以下数字只保留官方文本中可核对的表述。

## 1. 核心速览

**研究主题**：知识蒸馏与能力迁移。

**一句话总结**：We introduce PRACTICE, which trains a skill learner to discover and maintain a persistent skill library from past interaction trajectories while keeping the task executor frozen.

这篇工作的价值不只在于给出一个更省资源的配置，而在于把质量、资源预算与部署路径放进同一评估框架；是否值得采用，应以论文报告的任务、模型和硬件边界为准。

## 2. 研究背景与动机

- 原文背景证据：Recent studies have shown that multimodal large language models (MLLMs) can serve as embodied agents, translating language instructions and visual observations into executable plans.
- 原文背景证据：Summing up experience from past interaction trajectories provides a promising solution, but existing experience-based methods often rely on manually designed prompting workflows to extract and update skills.
- 原文背景证据：Such fixed procedures may struggle to learn updated skills from new and diverse experiences.

从模型压缩视角看，核心矛盾是：减少参数、Token、缓存访问或高精度计算后，模型是否仍保留任务所需的信息。论文选择的切入点是可验证的资源瓶颈，而不是笼统地把“更小”当作“更快”。

## 3. 核心方法与创新点

1. **方法证据 1**：We introduce PRACTICE, which trains a skill learner to discover and maintain a persistent skill library from past interaction trajectories while keeping the task executor frozen.

全文结构中与方法和实验相关的章节包括：1 Introduction；2 Related Works；2.1 Embodied Task Planning；2.2 Experience-Augmented Agents；3 Methodology；3.1 Problem Formulation；3.2 Practice Overview；3.3 Curriculum Training of the Skill Learner；3.4 Skill OPD；4 Experiments；4.1 Experimental Setup；4.2 Main Results；4.3 Ablation；5 Conclusion。

分析上需要注意：摘要中的方法名只是入口，真正可复现的对象是数据流、决策粒度、训练/校准信号和推理时额外开销。本文后续复现与评分均按这一口径判断。

## 4. 实验设计与结果

- **可核验结果**：However, building agents that can continually improve through interaction and rapidly adapt to their environments remains challenging.
- **可核验结果**：Finally, we apply online skill-edit distillation to align the skill learner with a stronger teacher on its current edit distribution to further improves the policy.
- **可核验结果**：Experiments demonstrate that a compact skill learner delivers consistent performance improvements across successive library-update rounds for multiple frozen executors.
- **可核验结果**：On EB-ALFRED and EB-Habitat, PRACTICE further outperforms the strongest experience-based baselines.
- **可核验结果**：It obtains average success rates of 49.7% on EB-ALFRED and 58.3% on EB-Habitat, exceeding the strongest prior experience-augmented baseline.
- **可核验结果**：Stage 0 increases the average from 40.7% to 42.3% by teaching the learner basic skill generation and consolidation from successful
- **可核验结果**：oracle trajectories. Introducing failure-aware skill editing in Stage 1 further raises performance to 45.3%, with a particularly clear improvement on the Long split from 6% to 14%. Finally, Stage 2 achieves the largest incremental gain among the learned stages, improving the average success rate by 4.4 points. At the same time, the number of skill cards in this stage also grows to the greatest one with 29 cards.
- **可核验结果**：, simply adding more successful trajectories provides only a marginal improvement, increasing the average success rate from 42.3% to 42.7%.

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

- [arXiv 摘要与 Submission history](https://arxiv.org/abs/2608.30760)
- [arXiv 官方全文](https://arxiv.org/html/2608.30760)
- 分类页出现位置：cs.LG new / New submissions (showing 185 of 185 entries)；cs.LG recent / Tue, 1 Sep 2026 (showing 336 of 336 entries )
