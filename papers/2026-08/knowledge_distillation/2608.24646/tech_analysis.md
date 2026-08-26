# 深度技术分析：On-Policy Self-Distillation in Diffusion Models

> arXiv: [2608.24646](https://arxiv.org/abs/2608.24646)
> v1 提交日期：2026-08-25
> 分类：cs.CV
> 证据：arXiv 官方摘要与官方全文（HTML/PDF）

## 1. 核心速览

**研究主题**：知识蒸馏；On-Policy Self-Distillation in Diffusion Models。

**一句话总结**：DiffusionOPSD 把图像级奖励梯度转成同一 query 上的有界正负 clean-output 目标，使扩散 RL 的中间去噪更新变得可监督、可诊断。

## 2. 研究背景与动机

这项工作针对的不是抽象的“模型更小”，而是部署链条中的可测瓶颈：模型状态、token/KV、训练监督或实际数据搬运。作者在官方摘要中把问题界定为：Reinforcement learning can align diffusion models with human preferences and task-specific objectives, but endpoint rewards do not specify how an intermediate denoising prediction should change。因此，评价重点应同时包含任务质量、资源口径与实现边界，而不能只报告单一压缩率。

## 3. 核心方法与创新点

- 冻结 behavior policy 采样轨迹并提供 query/anchor。
- 奖励梯度围绕 anchor 构造有界正负目标。
- 有限步拟合后以 EMA 更新 behavior policy。

- 核心创新可概括为：DiffusionOPSD 把图像级奖励梯度转成同一 query 上的有界正负 clean-output 目标，使扩散 RL 的中间去噪更新变得可监督、可诊断。

## 4. 实验设计与结果

在 SD 3.5-M 与 Z-Image-Turbo、十个 evaluator 的 20 个 reward-matched 设置中 19 个最终最佳，最高超过最强方法 44.0%；相对 DiffusionNFT 的训练 GPU-hour 分别减少 40% 与 63%。

上述数字均来自论文官方全文或摘要；它们是作者在特定模型、数据集、硬件和预算下的报告，不自动构成跨模型普遍结论。复现实验应优先固定基线、质量阈值、真实驻留/读取字节和端到端延迟口径。

## 5. 局限性与未来展望

奖励模型偏差会直接进入目标；同 query 单步拟合增益与最终增益并不单调，长期稳定性和更大生成模型仍需验证。

后续最有价值的验证是把方法放进真实服务或训练路径，使用等预算基线、跨模型/跨任务测试和公开可审计的内存—延迟—质量三维记录。

## 6. 学术启发

把终点奖励转成中间显式目标，可把 RL 的信用分配问题转为可测的目标构造与目标实现两部分。

这篇论文也提示：压缩研究应主动公布负结果和失效区间，并区分算法表示压缩、kernel 可利用性与真实端到端收益。
