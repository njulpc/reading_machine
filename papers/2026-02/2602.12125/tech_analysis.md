# 深度技术分析：Learning beyond Teacher: Generalized On-Policy Distillation with Reward Extrapolation

> **论文信息**
> - **arXiv ID**: 2602.12125
> - **标题**: Learning beyond Teacher: Generalized On-Policy Distillation with Reward Extrapolation
> - **作者**: Wenkai Yang, Weijie Liu, Ruobing Xie, Kai Yang, Saiyong Yang, Yankai Lin
> - **提交日期**: 12 Feb 2026 (v1), last revised 26 Feb 2026 (this version, v2)
> - **分类**: cs.AI, cs.CL, cs.LG
> - **链接**: https://arxiv.org/abs/2602.12125

---

## 1. 核心速览

### 1.1 研究主题

本文属于**知识蒸馏（Knowledge Distillation）**方向的研究，提出了名为 **Generalized** 的方法。

> 论文摘要首句：*"On-policy distillation (OPD), which aligns the student with the teacher's logit distribution on student-generated trajectories, has demonstrated strong empirical gains in improving student performance and often outperforms off-policy distillation and reinforcement learning (RL) paradigms."*

### 1.2 一句话总结

本文提出 Generalized：Then, we propose the Generalized On-Policy Distillation (G-OPD) framework, which extends the standard OPD objective by introducing a flexible reference model and a reward scaling factor that controls the relative weight of the reward term against the KL regularization.（摘要原文）

---

## 2. 研究背景与动机 (Background & Motivation)

### 2.1 领域背景

知识蒸馏将大模型（教师）的能力迁移到小模型（学生）中，是模型压缩与能力压缩的重要手段。核心问题包括蒸馏信号的构造、师生能力差距的弥合、以及在推理能力等复杂行为上的有效迁移。

### 2.2 本文针对的具体问题

以下为摘要中直接陈述研究动机与问题定义的原文句子：

- *"On-policy distillation (OPD), which aligns the student with the teacher's logit distribution on student-generated trajectories, has demonstrated strong empirical gains in improving student performance and often outperforms off-policy distillation and reinforcement learning (RL) paradigms."*
- *"In this work, we first theoretically show that OPD is a special case of dense KL-constrained RL where the reward function and the KL regularization are always weighted equally and the reference model can by any model."*
- *"Then, we propose the Generalized On-Policy Distillation (G-OPD) framework, which extends the standard OPD objective by introducing a flexible reference model and a reward scaling factor that controls the relative weight of the reward term against the KL regularization."*
- *"Through comprehensive experiments on math reasoning and code generation tasks, we derive two novel insights: (1) Setting the reward scaling factor to be greater than 1 (ie, reward extrapolation), which we term ExOPD, consistently improves over standard OPD across a range of teacher-student size pairings."*
- *"However, this choice assumes access to the teacher's pre-RL variant and incurs more computational overhead."*

从上述表述可见，作者关注的核心矛盾是在小模型上尽可能复现大模型的能力。

---

## 3. 核心方法与创新点 (Methodology & Innovations)

### 3.1 方法概述

摘要中关于方法设计的核心陈述如下：

- *"Then, we propose the Generalized On-Policy Distillation (G-OPD) framework, which extends the standard OPD objective by introducing a flexible reference model and a reward scaling factor that controls the relative weight of the reward term against the KL regularization."*
- *"Through comprehensive experiments on math reasoning and code generation tasks, we derive two novel insights: (1) Setting the reward scaling factor to be greater than 1 (ie, reward extrapolation), which we term ExOPD, consistently improves over standard OPD across a range of teacher-student size pairings."*
- *"We hope our work offers new insights for future research on OPD."*

### 3.2 分点创新

摘要中以编号形式列出的技术要点：

1. *"Setting the reward scaling factor to be greater than 1 (i"*
2. *"Building on ExOPD, we further find that in the strong-to-weak distillation setting (i"*

---

## 4. 实验设计与结果 (Experiments & Results)

### 4.2 关键结果（摘要原文数据）

以下为摘要中含具体数值或对比结论的原文句子，所有数字均直接引自摘要：

- *"Through comprehensive experiments on math reasoning and code generation tasks, we derive two novel insights: (1) Setting the reward scaling factor to be greater than 1 (ie, reward extrapolation), which we term ExOPD, consistently improves over standard OPD across a range of teacher-student size pairings."*
- *"(2) Building on ExOPD, we further find that in the strong-to-weak distillation setting (ie, distilling a smaller student from a larger teacher), performing reward correction by choosing the reference model as the teacher's base model before RL yields a more accurate reward signal and further improves distillation performance."*

**摘要中出现的关键数值**（去重后）：1, 2

---

## 5. 局限性与未来展望 (Limitations & Future Work)

摘要未明确讨论局限性。结合该方向的普遍情况，本文方法可能存在以下局限（基于领域常识的一般性分析，非论文原文陈述）：

知识蒸馏的常见局限包括：(1) 学生与教师之间的能力差距限制了蒸馏上限；(2) 蒸馏过程通常需要额外训练数据与算力；(3) 蒸馏后模型在分布外数据上的鲁棒性可能弱于教师。

**未来展望**：可在以下方向继续推进——(1) 将本文方法与正交压缩手段（量化/剪枝/蒸馏/低秩）级联，验证综合压缩率；(2) 在更大规模模型与更多任务上检验泛化性；(3) 面向真实硬件做端到端部署验证。

---

## 6. 学术启发 (Takeaways for My Research)

结合本文工作与该方向的研究脉络，可提炼以下启发：

1. 蒸馏信号的设计（logits/特征/关系/推理轨迹）应与目标能力的类型匹配；
2. 在推理模型时代，长思维链的蒸馏成为小模型获取推理能力的关键路径；
3. 蒸馏过程中的负迁移与能力遗忘需要专门的评估协议；

4. 本文（Generalized）表明知识蒸馏将大模型（教师）的能力迁移到小模型（学生）中，是模型压缩与能力压缩的重要手段——其具体设计（见第 3 节）可作为后续工作的直接参考。

---

*本分析基于论文摘要与可获取信息撰写；所有标注为原文引用的句子与数字均直接摘自论文摘要，未做改写或虚构。*
