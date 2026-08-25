# DiD It in 87 Minutes: A Label-Free Softmax-to-Linear Adaptation of Vision Transformers for Object Detection

> arXiv: [2608.22368](https://arxiv.org/abs/2608.22368) · v1: 2026-08-23 · 主分类: cs.CV
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：Softmax ViT 检测器向 linear attention 的无标签架构转换。
**一句话总结**：DiD 不模仿任意隐藏层，而是对齐冻结 detector 真正消费的 backbone interface tensor；4 GPU 约 87 分钟完成适配，在 DOTA-v1.5 上把延迟降约 62%、峰值内存降约 49%。

## 2. 研究背景与动机

高分辨率检测中 Softmax attention 的二次复杂度昂贵；直接替换为 linear attention 会破坏下游 detector 期待的特征分布。分类任务常用的通用 feature distillation 也不保证检测接口兼容。

## 3. 核心方法与创新点

- 冻结原 Softmax teacher 和下游 detector，只训练 linear-attention backbone。
- 蒸馏 target 选 detector-facing interface tensors，而非内部层的泛化表征。
- 全程无标签，目标是复用已有检测器，而不是从头监督训练。
- 把“架构压缩是否成功”定义为固定消费者接口是否保持。

## 4. 实验设计与结果

在 DOTA-v1.5 上，DiD 明显优于既有转换基线，并达到监督训练 linear model 的水平。适配约 87 分钟/4 GPU；线性化 backbone 推理延迟约降 62%，峰值内存约降 49%。这些数字针对论文硬件与检测配置，不能直接解释为所有 ViT 的端到端收益。

## 5. 局限性与未来展望

验证集中于遥感检测与特定 detector 接口；其他密集预测任务、不同分辨率和 kernel 的收益尚待验证。线性 attention 的长程表达上限也可能被 interface loss 掩盖。

## 6. 学术启发

架构替换类蒸馏应围绕“不可修改的下游消费者”选择 target。接口保持比层对层模仿更接近部署约束，也为 CNN→ViT、dense→sparse 等转换提供通用范式。
