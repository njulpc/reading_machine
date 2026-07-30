# 深度技术分析：Post-Training is About States, Not Tokens: A State Distribution View of SFT, RL, and On-Policy Distillation

## 1. 核心速览
**研究话题**：知识蒸馏 (Knowledge Distillation)，目标对象为大语言模型

**一句话总结**：Large language model post-training methods such as supervised fine-tuning (SFT), reinforcement learning (RL), and distillation are often analyzed through their loss functions: maximum likelihood, policy gradients, forward KL, reverse KL, or related objective-level variants。

---

## 2. 研究背景与动机 (Background & Motivation)

知识蒸馏（Knowledge Distillation）通过让小型学生模型模仿大型教师模型的输出分布、中间特征或推理轨迹，实现能力的「压缩迁移」。在大模型时代，蒸馏的对象从 logits 扩展到思维链（CoT）轨迹、注意力分布乃至完整的推理行为，成为小模型获取大模型能力的主要途径。核心问题包括：教师-学生容量差距下的迁移效率、蒸馏信号的选择与设计、以及蒸馏过程中的能力保持与偏置传递。

就本文而言，作者的出发点（基于摘要）：Large language model post-training methods such as supervised fine-tuning (SFT), reinforcement learning (RL), and distillation are often analyzed through their loss functions: maximum likelihood, policy gradients, forward KL, reverse KL, or related objective-level variants. We study a complementary factor: the state distribution on which supervision is applied.

---

## 3. 核心方法与创新点 (Methodology & Innovations)
- **要点1**：We study a complementary factor: the state distribution on which supervision is applied.
- **要点2**：For an autoregressive policy, a state is a prompt plus generated prefix.
- **要点3**：SFT trains on fixed dataset states, while RL and on-policy distillation (OPD) train on states induced by the current learner.
- **要点4**：We formalize post-training as state-distribution shaping and run a controlled smallscale study using Qwen3-0.6B-Base on GSM8K, with TruthfulQA and MMLU as retention evaluations.
- **要点5**：Our results show three phenomena.
- **要点6**：First, a mild SFT run improves GSM8K with little forgetting, while a stress SFT run causes substantial retention loss.

**方法要素（从摘要提取）**：
- 涉及模型：Qwen3
- 涉及基准：GSM8K, MMLU, TruthfulQA

---

## 4. 实验设计与结果 (Experiments & Results)

摘要以定性结论为主，未给出可引用的具体数值；关键结论如下：
- Third, a lightweight on-policy RL run improves GSM8K while preserving retention.
- These results support a state-centric view of post-training: the source and locality of training states can be as important as the form of the supervision signal.
评测涉及基准：GSM8K, MMLU, TruthfulQA。

---

## 5. 局限性与未来展望 (Limitations & Future Work)

蒸馏效果受教师-学生容量差距与数据分布匹配程度的制约；蒸馏过程可能同时传递教师的偏置与错误，且对推理类能力（长思维链）的蒸馏往往比知识类任务更不稳定。

（注：本分析基于摘要与可获取信息撰写，论文正文中可能包含更详细的局限性讨论与消融实验。）

---

## 6. 学术启发 (Takeaways for My Research)

蒸馏信号的设计比蒸馏损失的形式更关键。本文对蒸馏对象（logits/特征/轨迹）的选择提供了实证参照；在自己研究中，可借鉴其教师-学生配对与数据构造方式，并关注蒸馏过程中的偏置传递问题。

结合本文的具体设定（大语言模型，知识蒸馏 (Knowledge Distillation)），可进一步思考：该方法的核心机制（如摘要所述）能否与其他压缩手段（量化/剪枝/蒸馏/低秩）组合，在自研模型上形成级联压缩管线；其实验协议（基线选择、评测基准、压缩率口径）也可作为自己实验设计的参照模板。

---

*论文信息：arXiv:2605.22731，Dong Nie，提交于 2026-05-21，分类：cs.LG, cs.AI，https://arxiv.org/abs/2605.22731*
