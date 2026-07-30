# 深度技术分析：Distilling LLM Feedback for Lean Theorem Proving

## 1. 核心速览
**研究话题**：知识蒸馏 (Knowledge Distillation)、稀疏化 (Sparsity)，目标对象为大语言模型

**一句话总结**：Building upon recent works on self-distillation, we propose Feedback Distillation, a training method where the model is trained to match, at the token level, its own distribution conditioned on privileged feedback produced by a language model。

---

## 2. 研究背景与动机 (Background & Motivation)

知识蒸馏（Knowledge Distillation）通过让小型学生模型模仿大型教师模型的输出分布、中间特征或推理轨迹，实现能力的「压缩迁移」。在大模型时代，蒸馏的对象从 logits 扩展到思维链（CoT）轨迹、注意力分布乃至完整的推理行为，成为小模型获取大模型能力的主要途径。核心问题包括：教师-学生容量差距下的迁移效率、蒸馏信号的选择与设计、以及蒸馏过程中的能力保持与偏置传递。

就本文而言，作者的出发点（基于摘要）：Post-training for reasoning models typically combines supervised fine-tuning with reinforcement learning from verifiable rewards, most commonly with GRPO. However, this algorithm suffers from sparse rewards, limited exploration, and mode collapse.

---

## 3. 核心方法与创新点 (Methodology & Innovations)
- **要点1**：Building upon recent works on self-distillation, we propose Feedback Distillation, a training method where the model is trained to match, at the token level, its own distribution conditioned on privileged feedback produced by a language model.
- **要点2**：Evaluating our method for Lean4 theorem-proving, we find that Feedback Distillation maintains greater diversity in generated trajectories than GRPO, yielding higher policy entropy and better pass@k scaling.

---

## 4. 实验设计与结果 (Experiments & Results)

摘要以定性结论为主，未给出可引用的具体数值；关键结论如下：
- The two methods are complementary: initializing GRPO from a Feedback Distillation checkpoint outperforms either method alone.
- All in all, our results suggest a promising avenue to improve post-training for complex reasoning.

---

## 5. 局限性与未来展望 (Limitations & Future Work)

蒸馏效果受教师-学生容量差距与数据分布匹配程度的制约；蒸馏过程可能同时传递教师的偏置与错误，且对推理类能力（长思维链）的蒸馏往往比知识类任务更不稳定。

（注：本分析基于摘要与可获取信息撰写，论文正文中可能包含更详细的局限性讨论与消融实验。）

---

## 6. 学术启发 (Takeaways for My Research)

蒸馏信号的设计比蒸馏损失的形式更关键。本文对蒸馏对象（logits/特征/轨迹）的选择提供了实证参照；在自己研究中，可借鉴其教师-学生配对与数据构造方式，并关注蒸馏过程中的偏置传递问题。

结合本文的具体设定（大语言模型，知识蒸馏 (Knowledge Distillation)、稀疏化 (Sparsity)），可进一步思考：该方法的核心机制（如摘要所述）能否与其他压缩手段（量化/剪枝/蒸馏/低秩）组合，在自研模型上形成级联压缩管线；其实验协议（基线选择、评测基准、压缩率口径）也可作为自己实验设计的参照模板。

---

*论文信息：arXiv:2605.30861，Gaetan Narozniak, Gérard Biau, Rémi Munos, Ahmad Rammal, Pierre Marion，提交于 2026-05-29，分类：cs.AI，https://arxiv.org/abs/2605.30861*
