# 深度技术分析：From Proprietary to Open-Source: Bridging the Distribution Gap via Multi-Agent Protocol Distillation in Agentic Search

> 本分析基于 arXiv 摘要与论文公开信息撰写，所有数字均引自摘要。

## 1. 核心速览

**研究主题**：知识蒸馏方向（技术标签：知识蒸馏）；论文分类：cs.AI

**一句话总结**：本文提出 Multi-Agent Protocol Distillation (MAPD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。

---

## 2. 研究背景与动机

知识蒸馏（Knowledge Distillation）将大模型（教师）的能力迁移到小模型（学生），是获得紧凑高性能模型的经典路径。研究问题包括蒸馏信号的设计、教师-学生架构差异的处理、以及蒸馏与其他压缩手段（剪枝、量化）的组合。

论文摘要中给出的动机如下：

- Agentic search enables large language models to solve knowledge-intensive tasks by interleaving multi-step reasoning with retrieval, yet optimizing this with outcome-based reinforcement learning (RL) provides only sparse supervision.
- Knowledge distillation can supply denser guidance, and advanced proprietary models with their strong reasoning capabilities are promising teachers.
- While distilling from proprietary models can densify this supervisory signal, conventional logit-matching is precluded by hidden logits and mismatched tokenizers, whereas raw natural language trajectory imitation transfers superficial stylistic artifacts rather than core reasoning competence.

---

## 3. 核心方法与创新点

方法要点（摘自摘要）：

- To address the heterogeneous distillation problem and bridge the distribution gap, we propose Multi-Agent Protocol Distillation (MAPD), a joint distillation and RL framework uses a structured, style-normalized protocol as an intermediate representation.
- An offline multi-agent system (MAS) decomposes each query, retrieves supporting evidence, repairs failed searches, and converts the resulting exploration trace into a JSON protocol containing the task type, reasoning plan, and extractive grounding facts.
- During training, the protocol is provided only to a privileged branch of the student policy, whose token distributions furnish a dense distillation signal alongside the sparse RL objective.
- Extensive evaluations across seven QA benchmarks demonstrate that MAPD consistently outperforms competitive distillation and RL, achieving average success rates of 39.4\% on Qwen3-1.7B and 44.4\% on Qwen3-4B.

**创新点归纳**：
1. 将知识蒸馏技术应用于该论文针对的具体场景，形成了完整的方法管线；
2. 通过量化指标验证了方法有效性（摘要报告的关键数字包括：1.7, 1.7B, 39.4, 44.4, 4B 等）；
3. 与已有方法相比，论文强调其设计在精度-成本权衡上的优势（详见摘要方法描述）。

---

## 4. 实验设计与结果

**实验模型**：Qwen3-1.7B, Qwen3-4B

摘要中报告的主要结果：

- Extensive evaluations across seven QA benchmarks demonstrate that MAPD consistently outperforms competitive distillation and RL, achieving average success rates of 39.4\% on Qwen3-1.7B and 44.4\% on Qwen3-4B.

**关键数字**：1.7, 1.7B, 39.4, 44.4, 4B

---

## 5. 局限性与未来展望

蒸馏方法的常见局限包括：学生容量上限导致的性能天花板、教师-学生架构/分词器差异带来的迁移损耗，以及蒸馏过程本身额外的训练成本。

针对本文的具体情况，值得进一步关注的问题包括：方法的超参数敏感性、在更大规模模型上的可扩展性、以及论文未覆盖的硬件后端上的实测表现。未来工作可考虑将该方法与互补的压缩技术（如量化+剪枝+蒸馏组合）结合，并在真实部署负载下端到端验证。

---

## 6. 学术启发 (Takeaways for My Research)

对蒸馏研究的启发：(1) 蒸馏信号可以超越 logits，扩展到中间特征、注意力图与生成轨迹；(2) 自蒸馏避免了教师模型的成本，是小模型场景的可行替代；(3) 蒸馏目标应与下游评测指标显式对齐。

本文值得借鉴的具体点：从摘要可见，作者围绕知识蒸馏的核心瓶颈设计了针对性的解决方案，其问题定义方式（先明确部署约束再设计方法）与评估组织方式（围绕任务指标展开）对设计压缩实验有直接参考价值。

---

*论文信息：arXiv:2607.24280，Junlin Liu, Jiangwang Chen, Zixin Song, Shuaiyu Zhou, Chunji Lv 等，提交日期 2026-07-27，链接 https://arxiv.org/abs/2607.24280*