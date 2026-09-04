# CoFiE: Coarse-to-Fine Evidence Selection for Efficient Streaming Video Understanding

- arXiv ID：2609.03675
- 作者：Jing Jiang, Yiran Ling, Ruonan Li, Dimitrios Stamoulis, Jie Liu
- v1实际提交：2026-09-03T11:14:21Z（UTC）；2026-09-03T19:14:21+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV)
- 本次归类：剪枝；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.03675)；[官方HTML全文](https://arxiv.org/html/2609.03675)；[PDF](https://arxiv.org/pdf/2609.03675)

## 1. 核心速览

研究主题：剪枝。CoFiE 在视觉编码前过滤冗余帧，并在预填充时按查询进一步精简。

## 2. 研究背景与动机

仅在视觉编码后删token，仍支付了完整的视觉编码成本，流式视频尤其明显。

## 3. 核心方法与创新点

- Novelty-Guided Frame Filtering基于新颖性保留帧
- Query-Specific Refinement在查询到来后再筛选相关表示，串联两级预算。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.03675)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

StreamingBench 78.86%、OvO 68.72%；最高过滤80%帧，端到端延迟改善2.54倍。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | StreamingBench 78.86%、OvO 68.72%；最高过滤80%帧，端到端延迟改善2.54倍。 |
| 压缩倍率 | 8 | StreamingBench 78.86%、OvO 68.72%；最高过滤80%帧，端到端延迟改善2.54倍。 |
| 创新性 | 8 | Novelty-Guided Frame Filtering基于新颖性保留帧；Query-Specific Refinement在查询到来后再筛选相关表示，串联两级预算。 |
| 可复现性 | 7 | 80%与2.54倍属于各自实验设置，不能视为所有视频固定收益；查询到达方式与缓存状态影响延迟。参数量没有减少。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

80%与2.54倍属于各自实验设置，不能视为所有视频固定收益；查询到达方式与缓存状态影响延迟。参数量没有减少。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

视频压缩应把编码前和编码后开销一起测量，优先消除最早发生的冗余。
