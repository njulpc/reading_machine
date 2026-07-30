# 技术深度分析：Jet-RL: Enabling On-Policy FP8 Reinforcement Learning with Unified Training and Rollout Precision Flow (arXiv:2601.14243)

> **论文**: Jet-RL: Enabling On-Policy FP8 Reinforcement Learning with Unified Training and Rollout Precision Flow
> **作者**: Haocheng Xi, Charlie Ruan, Peiyuan Liao, Yujun Lin
> **arXiv**: https://arxiv.org/abs/2601.14243 ｜ 提交: 2026-01-20 ｜ 分类: cs.LG, cs.CL

---

## 一、核心速览

### 研究主题

FP8 强化学习训练的首个系统研究与方案 Jet-RL：揭示广泛使用的"BF16 训练 + FP8 rollout"策略在长时程 rollout 与困难任务下严重不稳定甚至精度崩溃，根因是离策略数值失配，提出统一训练-rollout 精度流。

### 一句话总结

Jet-RL 首次全面研究 FP8 RL 训练，证明训练与推理精度不一致引入的数值失配使 RL 变为事实上的离策略训练从而导致崩溃，通过统一精度流实现真正的 on-policy FP8 强化学习。

---

## 二、研究背景与动机

RL 是增强 LLM 复杂推理的关键阶段，但训练管线低效——rollout 阶段占总训练时间 70% 以上。FP8 量化 rollout 是自然加速手段，业界常用"BF16 训练+FP8 rollout"。本文核心发现：该策略在长 rollout 与难任务下灾难性崩溃，因为训练分布（BF16 策略）与采样分布（FP8 策略）的数值失配使 on-policy 算法实际变成 off-policy。

---

## 三、方法创新

1. **首个 FP8 RL 系统研究**：系统刻画精度混合策略的失效模式——长时程 rollout 与困难任务下训练不稳定与精度崩溃。
2. **根因归因到 off-policy 失配**：训练/推理数值不一致 → 行为策略与目标策略偏离 → on-policy 假设被破坏——为量化 RL 提供理论诊断框架。
3. **统一精度流**：让训练与 rollout 在同一 FP8 精度路径上，恢复 on-policy 性质，同时保住 FP8 的速度收益。

---

## 四、实验结果

- "BF16 训练 + FP8 rollout"在长时程 rollout 和困难任务下出现**严重训练不稳定与灾难性精度崩溃**。
- rollout 阶段占 RL 总训练时间 **70%+**（加速动机）。
- Jet-RL 统一精度后恢复稳定训练（具体加速数字摘要未列出）。

---

## 五、局限与展望

- FP8 训练对算子覆盖与硬件（Hopper 代际以上）有要求，旧卡不适用。
- 统一精度流的实现侵入训练框架，工程落地成本高。
- 对 PPO 之外算法（GRPO、DPO 变体）的覆盖未在摘要中说明。

---

## 六、学术启发

1. "数值失配=隐性 off-policy"是深刻诊断——任何推理期量化（INT8/FP8 serving）与训练精度不一致的 RL 系统都有同样隐患。
2. 量化研究应把"训练-部署精度一致性"作为设计约束，而非事后补丁——精度流统一会成为 RL infra 的标准实践。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
