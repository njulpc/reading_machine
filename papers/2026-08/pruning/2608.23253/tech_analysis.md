# E2S-Pruner: Progressive Two-Stage Evidence Fusion for Visual Token Pruning in Vision-Language Models

> arXiv: [2608.23253](https://arxiv.org/abs/2608.23253) · v1: 2026-08-24 · 主分类: cs.CV
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：基于证据冲突的训练自由视觉 token 剪枝。
**一句话总结**：E2S-Pruner 把 attention head 当独立证据源，用重要/不重要/不确定三态表达，再以 Dempster–Shafer 跨层融合并加 spatial novelty；LLaVA-1.5-7B 保留 128/64 token 时吞吐提升 1.96×/2.09×。

## 2. 研究背景与动机

VLM 通常为每图保留数百 visual token。直接平均各 head/layer attention 会掩盖证据冲突和不确定性，也容易把 token 集中到少数局部显著区域，损失空间覆盖。

## 3. 核心方法与创新点

- stage 1：每个 head 独立产出三态 evidence，并按 clarity 与 head consistency 估计可靠性。
- stage 2：用 Dempster–Shafer 显式量化层间冲突并融合互补证据。
- spatial novelty 约束鼓励保留不同图像区域。
- 不需辅助模型、可训练参数或微调，可跨 backbone 应用。

## 4. 实验设计与结果

LLaVA-1.5-7B 平均保留 192/128/64 token 时，aggregate performance 为原模型的 98.0%/96.8%/90.6%；128/64 token 吞吐提升 1.96×/2.09×。Qwen2-VL-7B 结果支持跨模型泛化。性能保留率是多任务聚合，不代表每个任务均同幅下降。

## 5. 局限性与未来展望

Dempster–Shafer 规则和 novelty 超参引入手工设计；attention evidence 不一定等价于因果重要性。64-token 时仍有约 9.4% 聚合损失。未来可加入任务自适应预算和不确定性触发的 token 回填。

## 6. 学术启发

多层多头剪枝的核心不只是排序，而是处理证据冲突。显式“不确定”状态能避免过早硬删，并为动态预算提供校准信号。
