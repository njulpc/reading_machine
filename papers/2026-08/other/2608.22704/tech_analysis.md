# WnW: Waxing-and-Waning KV Cache for Long-Form Speech LLMs

> arXiv: [2608.22704](https://arxiv.org/abs/2608.22704) · v1: 2026-08-24 · 主分类: cs.CL
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：长音频 LLM 的可召回 KV cache 压缩。
**一句话总结**：WnW 将 head 分成 anchor、tidal、fixed：anchor 在线观察重要性，tidal 从 CPU complement 按块召回，fixed 永久保留子集；两种 3B speech LLM 只把 20% 音频 token 留在 GPU 仍接近 Full-Cache 准确率。

## 2. 研究背景与动机

长音频使 KV 成为主内存项。prefill-only eviction 假设预填注意力可预测解码重要性，但作者发现 prefill 有明显 attention sink，而 decode 注意力更分散，两种排序重合弱，永久删除会使基线甚至无法正常终止。

## 3. 核心方法与创新点

- 离线校准 head 角色，而非所有 head 使用同一淘汰策略。
- anchor head 常驻 GPU，并在 decode 时提供重要性信号。
- tidal head 将补集留在 CPU，可依据 anchor 聚合分数分块召回。
- fixed head 保留 GPU 子集，其余永久删除，以召回灵活性换取更低开销。

## 4. 实验设计与结果

在 LibriSpeech-Long、Voxtral-mini-3B 和 Qwen2.5-Omni-3B 上，GPU 仅保留 20% 音频 token 时保持接近 Full-Cache 准确率，prefill-only 基线在该预算下失败。作者还做语言、任务和域迁移，CPU-GPU recall 的 decode overhead 较小。

## 5. 局限性与未来展望

需要离线 head 校准和 CPU 容量；PCIe/统一内存拓扑变化会改写召回代价。20% 是特定模型与音频任务结果。未来应联合学习 head 角色、带宽感知 chunk 大小，并测真实并发服务。

## 6. 学术启发

KV 压缩不必等同永久丢弃；分层存储允许把“保留/删除”改成“常驻/可召回/删除”三态决策，更适合 prefill 与 decode 重要性不一致的模态。
