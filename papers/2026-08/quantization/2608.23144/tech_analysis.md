# Activation-Weighted Seeded Residual Coding for Low-Bit LLM Weight Repair

> arXiv: [2608.23144](https://arxiv.org/abs/2608.23144) · v1: 2026-08-24 · 主分类: cs.LG
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：低比特权重量化后的极小 sidecar 修复。
**一句话总结**：AWSRC 用确定性 seed 生成 basis，只存 seed selector、低比特 coefficient 和 scale，并以 activation statistics 加权残差；Qwen2.5-3B-Instruct 上给 INT4 RTN 增加 0.162 bit/weight，分别弥合 88.2% PPL、78.9% KL、71.3% accuracy gap。

## 2. 研究背景与动机

INT4 等 backbone 节省存储，但少量量化误差会显著破坏输出。直接存 residual、低秩矩阵或显式 codebook 会吞掉压缩收益；仅按 weight MSE 修复又忽略 activation 方向的重要性。

## 3. 核心方法与创新点

- 从已有量化重构 W0 出发编码 residual W-W0，不改 backbone quantizer。
- 用 seed 确定性生成候选 basis，编码端只需存 selector 而非 codebook。
- coefficient 低比特量化并配 scale，形成稀小 sidecar。
- activation-weighted objective 优先修复对 layer output 影响大的误差。

## 4. 实验设计与结果

Qwen2.5-3B-Instruct、INT4 RTN 上，0.162 scope-bit/weight 的 sidecar 弥合 BF16 gap：PPL 88.2%、KL 78.9%、accuracy 71.3%。49.25 MB sidecar 约为 BF16 权重 payload 的 0.8%，在匹配预算下优于 sparse、low-rank 和 vector-quantized codec 的 PPL/平均准确率。

## 5. 局限性与未来展望

需要代表性 activation calibration；seed basis 搜索成本和不同模型迁移性仍需评估。弥合比例依赖 backbone 质量与任务集合，不能直接换算成普适精度。未来可研究联合 backbone/sidecar 分配和 fused decode kernel。

## 6. 学术启发

量化不一定要重做 backbone；把压缩模型视为“主码流 + 可选增强层”可提供分级质量。关键是 sidecar bit 必须计入总 bit/weight，而非只报告主干位宽。
