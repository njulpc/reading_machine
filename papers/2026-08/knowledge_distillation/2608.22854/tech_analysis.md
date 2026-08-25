# Thinking at the Right Size: Amortized Distillation Across Post-Trained LLMs

> arXiv: [2608.22854](https://arxiv.org/abs/2608.22854) · v1: 2026-08-24 · 主分类: cs.LG
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：跨模型尺寸与 post-training 变体的摊销蒸馏。
**一句话总结**：ADAPT 用一次蒸馏同时覆盖尺寸轴和 instruction/reasoning/chat 变体轴，可生成 L 个插值尺寸 × K 个 post-trained variant，并用连续模型族支持推理时按难度选尺寸。

## 2. 研究背景与动机

部署需要多个大小和多个对齐变体，逐个训练 L×K 组合代价高。Boomerang 只在 base model 的尺寸轴摊销，仍把每个 post-training variant 当成独立问题。

## 3. 核心方法与创新点

- 两阶段蒸馏：先做 pre-training alignment，再做 SFT distillation，构造可平滑插值的 student。
- 把 base teacher-student 的 distillation-induced weight delta 转移到其他 post-trained 初始化。
- 一次训练近似覆盖两维模型族，而不是每一对独立优化。
- 连续尺寸插值允许推理时动态选择 compute-accuracy 点。

## 4. 实验设计与结果

全文在生成与推理任务上比较独立蒸馏、尺寸插值和 delta transfer，结果支持跨变体保持平滑的 size-performance 曲线，并改善长推理任务的自适应 compute-accuracy trade-off。摘要没有给出可脱离表格配置的单一加速或精度数字，因此不虚构统一倍率。

## 5. 局限性与未来展望

weight delta 可转移性依赖模型同源和变体间几何一致；不同 tokenizer、架构或激进对齐可能失效。一次训练并不等于零成本生成所有模型，仍需存储和验证 L×K artifacts。

## 6. 学术启发

模型压缩可以把“单个 student”提升为“可查询的模型族”。未来评价应同时报告训练摊销成本、插值稳定性和动态路由收益，而不仅是某个固定尺寸。
