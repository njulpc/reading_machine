# RS³-Prune: Read-Sparse, Store-Sparse Token Pruning for Video Object Segmentation

> arXiv: [2608.22526](https://arxiv.org/abs/2608.22526) · v1: 2026-08-23 · 主分类: cs.CV
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：视频分割 memory bank 的训练自由 token 剪枝。
**一句话总结**：RS³-Prune 同时减少跨帧注意力读出的 query 和真正写入 memory bank 的 token，在不改模型训练的情况下最高提升 38.8% FPS、降低 13.1% 峰值显存，并保持有竞争力的 J&F。

## 2. 研究背景与动机

现代 VOS 每帧生成密集 token，历史 token 又持续累积到 memory bank；长视频下计算和内存随 token budget 增长。只在读阶段稀疏仍会存下大量无用 token，只在写阶段裁剪又无法降低当前帧 query 成本。

## 3. 核心方法与创新点

- read-sparse：在 image encoder 与 memory-attention 之间，只保留几何上有信息的 query。
- store-sparse：在 memory encoder 与 bank 之间，只允许目标空间范围内 token 入库。
- 以 inference hook 实现，训练自由，可叠加到现有 memory-bank VOS。
- 将压缩轴明确为 token budget，并同时优化读与存两条路径。

## 4. 实验设计与结果

论文在多个标准 VOS benchmark 和现有网络上评估。最佳配置报告 FPS +38.8%、峰值显存 -13.1%，J&F 与原网络相比仍具竞争力。速度与内存百分比来自不同模型/设置，解读时应结合各表的 token retention。

## 5. 局限性与未来展望

几何约束依赖目标区域质量，遮挡、快速运动和多目标交互可能删掉未来有用背景 token。训练自由意味着模型无法适应新的稀疏分布。未来可研究不确定性驱动的回填和随视频长度动态预算。

## 6. 学术启发

序列模型的 token pruning 应审计 token 的生命周期：生成、读取、写入和长期驻留。只优化其中一段，常会把瓶颈转移到另一段。
