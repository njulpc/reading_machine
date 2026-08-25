# SplitLite: Low-Rank Residual Compression for Split Learning

> arXiv: [2608.23018](https://arxiv.org/abs/2608.23018) · v1: 2026-08-24 · 主分类: cs.LG
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：split federated LoRA 的低秩残差与量化通信压缩。
**一句话总结**：LoRA rank-r 更新使相邻 epoch activation/gradient residual 呈有效 rank-2r/4r，SplitLite 只传量化 truncated-SVD factor，在 GLUE 与多种 on-device LLM 上把 activation uplink 最多降 93.5%、总通信降 83.7%，且无性能下降。

## 2. 研究背景与动机

Split learning 把主计算移到服务器，却要求客户端与服务器反复交换高维 activation 和 gradient。直接逐轮量化忽略相邻 epoch 更新的结构，低 bit 又可能破坏训练。

## 3. 核心方法与创新点

- 对同一样本跨相邻 epoch 计算 activation/gradient residual，而非重传完整张量。
- 从 LoRA rank-r 推导 activation residual 有效 rank-2r、gradient residual 有效 rank-4r。
- 对 residual 做 truncated SVD，仅传 U/S/V factor。
- factor 再量化，接收端重构并累加到上一 epoch 状态。

## 4. 实验设计与结果

GLUE、多种先进 on-device LLM 的 split federated LoRA 设置中，activation uplink 最多减少 93.5%，总通信最多减少 83.7%，作者报告无性能退化。上界依赖层切分、LoRA rank、SVD rank 与量化 bit，不能视为固定压缩率。

## 5. 局限性与未来展望

需要同一样本跨 epoch 对齐并保存上一状态；SVD 自身有计算和内存开销，非 IID/异步客户端会削弱低秩残差假设。未来可研究 randomized SVD、误差反馈和真实网络端到端时延。

## 6. 学术启发

通信压缩应优先压“变化量”而非绝对量，并把训练算法的结构先验（LoRA rank）转成编码 rank。量化误差应与残差累积误差共同分析。
