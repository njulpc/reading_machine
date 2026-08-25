# Beyond Dense Adam States: Adaptive Log-Space Quantization for Memory-Efficient Optimizers

> arXiv: [2608.22322](https://arxiv.org/abs/2608.22322) · v1: 2026-08-23 · 主分类: cs.LG
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：非稠密 Adam 优化器状态的自适应对数量化。
**一句话总结**：作者针对 factored、confidence-based 和 projected 状态分别选精度，用按块 Adaptive Log-Space（AL）编码保留精确零；TinyLlama-1.1B 上将优化器状态从 8392.7 MiB 降到 2119.2 MiB，AL8 AdamW 困惑度 72.90，接近 FP32 的 72.48。

## 2. 研究背景与动机

现有 8-bit optimizer 多围绕 Adam 的稠密一、二阶矩设计，但 Adafactor、CAME、APOLLO 的状态拓扑和误差传播不同。同一种量化器强行套用会使对数量级很小的非负状态、带符号动量和关键参数发生不同方式的失真。

## 3. 核心方法与创新点

- 对非负状态按块估计非零动态范围，在 log 域均匀编码，同时为零保留独立码点。
- AL8/AL16 与带符号动量编码解耦，让每类状态选择不同位宽。
- topology-aware protection 对敏感参数或状态保留更高精度，而不是全局统一升级。
- 贡献重点不是一个万能 8-bit 格式，而是“状态语义 + 拓扑”共同决定量化策略。

## 4. 实验设计与结果

共 96 次运行、214.7 GPU-hours，覆盖 AdamW、Adafactor、CAME、APOLLO。20K-step TinyLlama-1.1B 中，AL8 二阶矩 + 8-bit uniform momentum 的 PPL 为 72.90，FP32 为 72.48，dynamic 8-bit 基线为 73.54；存储下降约 74.8%。CAME 的 AL16/FP32/all-AL8 PPL 分别 86.16/86.68/90.19，说明不能盲目使用 AL8。100K-step GPT-2 中，拓扑保护把 Adafactor 后期 loss gap 从 +0.1185 压到 +0.0159。

## 5. 局限性与未来展望

端到端比较只有一个训练 seed，论文也明确把数字限定为经验测量；长期稳定性和更大模型外推仍不足。AL 的真实内存带宽收益还依赖 kernel 和状态布局。未来应补多 seed、收敛置信区间，以及 fused optimizer kernel 的实际吞吐。

## 6. 学术启发

优化器压缩应先画出状态拓扑，再分配 bit：数值分布相似不代表训练敏感性相同。复现中应同时检查编码误差、一步更新误差与多步 loss 漂移，避免只报告静态 MSE。
