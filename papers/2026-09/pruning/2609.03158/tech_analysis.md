# Who Speaks for the Pruned? Visual Token Pruning as Coverage Optimization

- arXiv ID：2609.03158
- 作者：Qingchan Zhu, Weihang You, Hanqi Jiang, Changdi Yang, Tianming Liu, Geng Yuan
- v1实际提交：2026-09-02T20:51:02Z（UTC）；2026-09-03T04:51:02+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV) ; Computation and Language (cs.CL); Machine Learning (cs.LG)
- 本次归类：剪枝；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.03158)；[官方HTML全文](https://arxiv.org/html/2609.03158)；[PDF](https://arxiv.org/pdf/2609.03158)

## 1. 核心速览

研究主题：剪枝。CoverPruner 将保留 token 选择改写为对全部视觉证据的代表性覆盖。

## 2. 研究背景与动机

高分 token 可能彼此冗余，留下的 token 未必能代表被删除的信息。

## 3. 核心方法与创新点

- 在视觉投影后的 LLM 输入空间建立相似性
- 用首层注意力估计查询需求
- 求需求加权覆盖最大化，保持选中的原始 token 和顺序，不做特征合并。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.03158)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

LLaVA-1.5-7B 从 576 保留 128 token，平均分 67.9 对完整 69.0，保持 98.4%；LLaVA-NeXT 从 2880 保留 640，69.4 对 69.6，保持 99.7%。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 9 | LLaVA-1.5-7B 从 576 保留 128 token，平均分 67.9 对完整 69.0，保持 98.4%；LLaVA-NeXT 从 2880 保留 640，69.4 对 69.6，保持 99.7%。 |
| 压缩倍率 | 8 | LLaVA-1.5-7B 从 576 保留 128 token，平均分 67.9 对完整 69.0，保持 98.4%；LLaVA-NeXT 从 2880 保留 640，69.4 对 69.6，保持 99.7%。 |
| 创新性 | 8 | 在视觉投影后的 LLM 输入空间建立相似性；用首层注意力估计查询需求；求需求加权覆盖最大化，保持选中的原始 token 和顺序，不做特征合并。 |
| 可复现性 | 8 | 这些是 token 预算和归一化任务分数，不等于整机显存或延迟倍率；相似矩阵与探针有额外开销。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

这些是 token 预算和归一化任务分数，不等于整机显存或延迟倍率；相似矩阵与探针有额外开销。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

评价剪枝应考察每个被删证据是否有代表，而不仅检查保留集内部多样性。
