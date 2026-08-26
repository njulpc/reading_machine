# 深度技术分析：HAP: Head-Adaptive Visual Token Pruning via Cross-Modal Alignment

> arXiv: [2608.23921](https://arxiv.org/abs/2608.23921)
> v1 提交日期：2026-08-24
> 分类：cs.CV
> 证据：arXiv 官方摘要与官方全文（HTML/PDF）

## 1. 核心速览

**研究主题**：剪枝/稀疏；HAP: Head-Adaptive Visual Token Pruning via Cross-Modal Alignment。

**一句话总结**：依据各注意力头与文本查询的跨模态对齐质量自适应融合打分，再按层组预算剪除视觉 token，避免坏头淹没细粒度证据。

## 2. 研究背景与动机

这项工作针对的不是抽象的“模型更小”，而是部署链条中的可测瓶颈：模型状态、token/KV、训练监督或实际数据搬运。作者在官方摘要中把问题界定为：Recent Vision-Language Models encode high-resolution images into long visual token sequences, incurring prohibitive prefill costs。因此，评价重点应同时包含任务质量、资源口径与实现边界，而不能只报告单一压缩率。

## 3. 核心方法与创新点

- 提出 PAQ 衡量 head 的 prompt-grounded 对齐质量。
- 以 PAQ-softmax 聚合 head 并分配 layer-group 预算。
- 按组级得分保留 token，全流程无需训练。

- 核心创新可概括为：依据各注意力头与文本查询的跨模态对齐质量自适应融合打分，再按层组预算剪除视觉 token，避免坏头淹没细粒度证据。

## 4. 实验设计与结果

LLaVA-1.5-7B 在 18 个基准中的九项汇总上，仅保留 5.6% token 仍保留 99.1% 原性能，比 AutoPrune 高 4.2 点；576→32 token 时 KV 占用降到 20%、延迟 0.48→0.17s（2.82×）。

上述数字均来自论文官方全文或摘要；它们是作者在特定模型、数据集、硬件和预算下的报告，不自动构成跨模型普遍结论。复现实验应优先固定基线、质量阈值、真实驻留/读取字节和端到端延迟口径。

## 5. 局限性与未来展望

方法主要优化 prefill，未处理生成期视觉 KV；PAQ 是注意力相关代理而非因果重要性证明，且依赖配对文本查询。

后续最有价值的验证是把方法放进真实服务或训练路径，使用等预算基线、跨模型/跨任务测试和公开可审计的内存—延迟—质量三维记录。

## 6. 学术启发

剪枝可靠性可以先评价“谁在打分”，再评价“哪些 token 得分高”。

这篇论文也提示：压缩研究应主动公布负结果和失效区间，并区分算法表示压缩、kernel 可利用性与真实端到端收益。
