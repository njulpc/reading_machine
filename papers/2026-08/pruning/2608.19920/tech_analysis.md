# 技术精读：Learning how to Forget

> arXiv: [2608.19920](https://arxiv.org/abs/2608.19920)；v1 提交：2026-08-20；主分类：cs.CL。

## 1. 核心速览

**研究主题**：让 LLM 在微调中适应任意 sparse-attention/KV eviction policy。
**一句话总结**：作者用 replay cache、逐层梯度与 CPU/GPU 分层把长上下文稀疏微调降到单张 A100 40GB，并改进 H2O；策略共适应在多项 64K/128K 任务上优于 sequence-parallel exact-attention 微调。

## 2. 研究背景与动机

KV cache 随上下文线性增长并会超过权重内存。多数 eviction 方法只在推理时硬删 token，模型从未学习“忘掉以后如何工作”；而在 sparse policy 下直接反传又需保存逐层完整 cache 和决策图，显存成本极高。

## 3. 核心方法与创新点（分点）

1. 把 cache policy 抽象为每个 batch/head/token 的选择函数，可适配 last-recent、H2O 及变体。
2. 训练前向记录 policy 决策和少量 delta KV；反向按层重放 cache，只把当前层/头所需梯度放 GPU。
3. nested activation checkpointing 与 CPU/GPU memory reuse 使显存不再随完整序列长度增长。
4. 改进 H2O：移除不必要状态、提出按存活时间归一化的累计 attention score，并提供支持 attention-weight backward 的 SDPA 实现。

## 4. 实验设计与结果

模型为 Qwen3-4B-Instruct-2507，cache 长度 N=32,768，chunk S=1,024/2,048；主训练用 4×A100 40GB，而方法层面可在单张 40GB 上对 4B 模型求梯度。Helmet 64K/128K 覆盖 10 个任务；对额外 6 个 accuracy 型任务，policy-aware 微调明显优于 exact-attention sequence-parallel checkpoint。H2O 计算 attention score 令单步训练比简单策略多约 2–3%，小 chunk 还会增加 10–14% 时间。作者也发现宽松 SubEM 会掩盖超长胡言输出，重新用严格 Accuracy 后结论更可靠。

## 5. 局限性与未来展望

总体 latency 仍高于成熟 dense serving kernel；论文承认 Table 1 的部分任务结果混合且对 H2O 变体排序不确定。训练实验仍使用多卡，单卡论证主要指显存可行性；32K cache 与 128K 输入的配置未覆盖百万 token。未来需 kernel fusion、服务框架集成和更严格生成质量指标。

## 6. 学术启发

“推理时删 cache”与“训练时学会遗忘”是两种不同问题。压缩策略若改变模型可见历史，最好让模型在同一信息约束下适应；同时，评测必须惩罚多余输出，否则稀疏模型的退化可能被 substring 指标隐藏。
