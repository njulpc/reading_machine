# 深度技术分析：How to Score Experts for One-Shot MoE Expert Pruning: A Unified Formulation and Selection Principle

> **arXiv ID**: [2606.15716](https://arxiv.org/abs/2606.15716)  |  **提交日期**: 2026-06-14  |  **分类**: cs.LG  |  **作者**: Zongfang Liu, Jinghui Zhang, Zijian Ma 等

> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。


---

## 一、核心速览

**研究主题**：MoE 专家剪枝（剪枝、稀疏化）—— 面向MoE 模型的模型压缩

**一句话总结**：本文研究了面向MoE 模型的MoE 专家剪枝方法/研究「How to Score Experts for One-Shot MoE Expert Pruning」，关键结果包括：8.8。（基于摘要）

**技术标签**: pruning / sparsity


---

## 二、研究背景与动机 (Background & Motivation)

MoE 模型以条件计算换取容量，但专家总数带来的显存与通信开销限制了部署。专家剪枝与专家合并通过评估专家重要性（路由频率、输出范数、因果干预等）移除冗余专家，是 MoE 压缩的主要路径；其挑战在于路由一致性与负载均衡的保持。

### 2.1 本文切入点

摘要开篇指出：

> Mixture-of-Experts (MoE) language models reduce per-token computation through sparse expert activation, yet deployment still requires storing the full expert pool, making one-shot expert pruning a practical approach for reducing memory usage.


并进一步阐述了问题设定：

> Although effective, existing criteria are largely heuristic, and no single criterion is universally optimal.


从问题陈述看，作者针对的是MoE 模型在MoE 专家剪枝场景下的具体瓶颈，属于 moe-pruning 技术路线。


---

## 三、核心方法与创新点 (Methodology & Innovations)

根据摘要可识别的核心方法组件：

- **方法要点 1**：Although effective, existing criteria are largely heuristic, and no single criterion is universally optimal.
- **方法要点 2**：Thus, establishing a principle for selecting pruning criteria suited to different deployment objectives remains an important yet largely underexplored problem in one-shot expert pruning.
- **方法要点 3**：To this end, we introduce a unified formulation for one-shot MoE expert pruning organized around three factors: routing frequency, gate weighting, and activation strength.
- **方法要点 4**：The formulation yields a criteria selection principle: task-agnostic pruning should favor routed-token-averaged, gate-free activation-based criteria, whereas task-specific pruning can benefit from retaining routing-frequency and gate-weight information.

**方法学点评**：MoE 剪枝需特别关注剪枝后路由分布的漂移与专家负载均衡的破坏，以及是否需要路由重训练。


---

## 四、实验设计与结果 (Experiments & Results)

摘要中报告的关键定量结果（原文句子摘录）：

- Across four representative MoE models and 16 diverse benchmarks, MAN and MSAN are consistently strong in the task-agnostic setting, obtain the top-two average ranks, and improve average performance by up to 8.8 points over the strongest baseline.

**结果解读**：以上数字均直接引自摘要原文。评估该类工作时建议对照同月同方向工作（见月度报告横向比较表）判断其增益幅度。


---

## 五、局限性与未来展望 (Limitations & Future Work)

MoE 剪枝的局限在于专家冗余度因任务而异，剪枝后罕见路由路径的能力损失难以通过常规基准检测。

此外，本文档基于摘要与 arXiv 元数据撰写，未获取全文，方法细节、实验设置与更完整的局限讨论以原文为准。


**未来展望**：未来方向：路由感知剪枝、专家合并、动态专家预算。


---

## 六、学术启发 (Takeaways for My Research)

- 专家重要性应从因果效应（消融）而非仅路由频率衡量
- MoE 剪枝与专家合并的组合可进一步压缩而保持路由一致性
- 结合本文：可将「How to Score Experts for One-Shot MoE Expert Pruning」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。
