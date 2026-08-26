# 深度技术分析：On-policy Distillation with Verifiable Reward

> arXiv: [2608.24696](https://arxiv.org/abs/2608.24696)
> v1 提交日期：2026-08-25
> 分类：cs.LG, cs.AI
> 证据：arXiv 官方摘要与官方全文（HTML/PDF）

## 1. 核心速览

**研究主题**：知识蒸馏；On-policy Distillation with Verifiable Reward。

**一句话总结**：OPDVR 用一个无新增超参的 ReLU gate，让 sampled-token 蒸馏的隐式奖励符号与整条轨迹正确性一致，从而自然兼容 RLVR/GRPO。

## 2. 研究背景与动机

这项工作针对的不是抽象的“模型更小”，而是部署链条中的可测瓶颈：模型状态、token/KV、训练监督或实际数据搬运。作者在官方摘要中把问题界定为：Reinforcement Learning with Verifiable Rewards (RLVR) and on-policy distillation (OPD) have become two widely adopted paradigms for post-training large language models。因此，评价重点应同时包含任务质量、资源口径与实现边界，而不能只报告单一压缩率。

## 3. 核心方法与创新点

- 把 OPD 隐式奖励写成教师-学生概率比。
- 依据 verifiable reward 对正确/错误轨迹施加非负/非正约束。
- 作为标准 policy-gradient 奖励接入 GRPO、REINFORCE 或 DAPO。

- 核心创新可概括为：OPDVR 用一个无新增超参的 ReLU gate，让 sampled-token 蒸馏的隐式奖励符号与整条轨迹正确性一致，从而自然兼容 RLVR/GRPO。

## 4. 实验设计与结果

六个推理基准上持续超过标准 OPD；方法无需加权系数或启发式切换，并给出 Group Relative Policy Distillation 实例。

上述数字均来自论文官方全文或摘要；它们是作者在特定模型、数据集、硬件和预算下的报告，不自动构成跨模型普遍结论。复现实验应优先固定基线、质量阈值、真实驻留/读取字节和端到端延迟口径。

## 5. 局限性与未来展望

依赖可验证二值/标量奖励，开放式质量与部分正确轨迹的门控更难；摘要未给统一平均提升和计算成本。

后续最有价值的验证是把方法放进真实服务或训练路径，使用等预算基线、跨模型/跨任务测试和公开可审计的内存—延迟—质量三维记录。

## 6. 学术启发

先修正监督信号的符号一致性，往往比增加复杂的蒸馏-RL 混合权重更稳。

这篇论文也提示：压缩研究应主动公布负结果和失效区间，并区分算法表示压缩、kernel 可利用性与真实端到端收益。
