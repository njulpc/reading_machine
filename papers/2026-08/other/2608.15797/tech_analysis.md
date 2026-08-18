# KV-Rescue：技术精读

> arXiv: [2608.15797](https://arxiv.org/abs/2608.15797) · submitted 2026-08-16 · Minsoo Cheong 等 · cs.AI / cs.CL

## 1. 核心速览

**研究主题**：激进 KV-cache eviction 后的推理能力恢复。
**一句话总结**：KV-Rescue 不试图猜回被删 KV，而是让小型全上下文 helper 与被 eviction 的大模型交替产生推理步骤，并提前截断退化候选。

## 2. 研究背景与动机

KV eviction 能限制长推理内存，却让大模型只见到残缺历史；预算过小时不仅答案错误，还可能重复/乱码直到长度上限。作者将其解释为信息缺口，并观察被裁剪 7B 与全上下文 1.5B 的错误互补。

## 3. 核心方法与创新点

- 两模型共享一条 stepwise interleaved trajectory：大模型保留能力，小模型补全历史信息。
- 在线检测器结合 entropy 与 compressibility，发现不连贯/重复候选后提前终止。
- training-free，不修改基础模型参数或 eviction 策略。

## 4. 实验设计与结果

oracle 在 eviction 7B 与 full-context 1.5B 的答案间选择，可恢复相对 full-KV 7B 精度差的 **79%**。在 5 个数学基准、Qwen2.5-Math 7B/72B、预算 B=64 下，KV-Rescue 平均恢复 **87%** 的 eviction 精度损失；阻止 runaway degeneration 使大模型生成 token 平均减少 **43%**。

## 5. 局限性与未来展望

需要额外 helper 模型和全上下文存储，系统总内存/吞吐不一定在所有场景更低；检测器和 step 边界也偏数学推理。后续可研究共享权重 helper、动态预算和非推理任务。

## 6. 学术启发

KV 压缩的损失可以通过“能力-信息解耦”补偿；评估应同时报告精度、KV 内存和因退化造成的额外 decode token。

**证据边界**：官方 HTML 全文可用，数字与模型设置均有明确原文证据。
