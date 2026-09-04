# CORE: Improving Compositional Reasoning in MLLM Embedding via Reranker Distillation

- arXiv ID：2609.04083
- 作者：Tingyu Song, Mingxin Li, Yanzhao Zhang, Dingkun Long, Chu Liu, Pengjun Xie, Yilun Zhao, Shu Wu
- v1实际提交：2026-09-03T16:50:29Z（UTC）；2026-09-04T00:50:29+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI); Computation and Language (cs.CL); Information Retrieval (cs.IR)
- 本次归类：知识蒸馏；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.04083)；[官方HTML全文](https://arxiv.org/html/2609.04083)；[PDF](https://arxiv.org/pdf/2609.04083)

## 1. 核心速览

研究主题：知识蒸馏。CORE 将跨模态重排序器的组合关系判断迁移给可预计算的嵌入模型。

## 2. 研究背景与动机

相同对象不同属性绑定易让双塔嵌入混淆，交叉注意力重排更准但检索成本高。

## 3. 核心方法与创新点

- 生成五级组合匹配候选列表
- 以Rank-KL传递细粒度排序，统一数据与调参预算比较对比学习、CoSENT和列表损失。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.04083)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

CORE-RERANKER-8B总平均0.827，Jina0.720；CORE-EMBED-8B为0.666，在COCO/Flickr30K保持检索能力。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | CORE-RERANKER-8B总平均0.827，Jina0.720；CORE-EMBED-8B为0.666，在COCO/Flickr30K保持检索能力。 |
| 压缩倍率 | 5 | 重排器和嵌入器的两种汇总指标不同，不可直接计算保真比例；没有给出统一权重压缩倍数。 |
| 创新性 | 7 | 生成五级组合匹配候选列表；以Rank-KL传递细粒度排序，统一数据与调参预算比较对比学习、CoSENT和列表损失。 |
| 可复现性 | 8 | 重排器和嵌入器的两种汇总指标不同，不可直接计算保真比例；没有给出统一权重压缩倍数。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

重排器和嵌入器的两种汇总指标不同，不可直接计算保真比例；没有给出统一权重压缩倍数。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

把昂贵交叉编码器的关系知识摊销到离线嵌入，是检索场景的计算压缩。
