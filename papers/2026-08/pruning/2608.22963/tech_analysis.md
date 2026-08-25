# Buried in Textual Debt: Context Pruning with Visual Evidence Preservation for MLLM Agents

> arXiv: [2608.22963](https://arxiv.org/abs/2608.22963) · v1: 2026-08-24 · 主分类: cs.AI
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：多模态 agent 的视觉证据保持型 reasoning pruning。
**一句话总结**：SPARE 用任务状态摘要作为 privileged diagnostic context，以 original/summary-conditioned replay 的 reverse-KL 判断 reasoning segment 是否可删，并移除 37.89%–64.58% reasoning token，同时取得论文中最高平均准确率。

## 2. 研究背景与动机

多步 MLLM agent 的自生成文本会逐渐压过视觉证据，形成 textual debt；简单长度裁剪可能删掉仍未落地的视觉假设。关键不是删得最短，而是确认摘要已经覆盖该段对未来策略的影响。

## 3. 核心方法与创新点

- 用 compact task-state summary 提供候选段是否冗余的特权参照。
- 对同一模型做原上下文和摘要条件上下文 replay。
- 用 on-policy self-distillation 的 reverse-KL 衡量删除是否改变未来分布。
- 进一步 SFT summarizer，提高覆盖率和可剪比例。

## 4. 实验设计与结果

跨多步视觉工具使用 benchmark，SPARE 删除 37.89%–64.58% reasoning token，同时在所比 pruning 方法中获得最高平均准确率。区间反映任务差异；其贡献是 accuracy-context trade-off，而非保证任意轨迹都能删到 64.58%。

## 5. 局限性与未来展望

每个候选段双 replay 会增加离线/在线判断成本；compact summary 若错，会给 KL 测试提供错误参照。未来需要廉价代理、视觉证据覆盖度度量和流式增量剪枝。

## 6. 学术启发

上下文剪枝可以用“未来行为分布是否稳定”而非词面相似度定义冗余。对多模态系统，还应单独约束不同模态的证据保留率。
