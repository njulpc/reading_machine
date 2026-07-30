# 技术深度分析：CAPA: Contribution-Aware Pruning and FFN Approximation for Efficient Large Vision-Language Models (arXiv:2602.00247)

> **论文**: CAPA: Contribution-Aware Pruning and FFN Approximation for Efficient Large Vision-Language Models
> **作者**: Samyak Jha, Junho Kim
> **arXiv**: https://arxiv.org/abs/2602.00247 ｜ 提交: 2026-01-30 ｜ 分类: cs.CV, cs.LG

---

## 一、核心速览

### 研究主题

大型视觉语言模型（VLM）的视觉 token 剪枝与 FFN 近似：用"注意力贡献"（注意力概率 × value 向量模长）替代裸注意力分数作为 token 重要性判据，并对视觉 token 的 FFN 冗余做近似。

### 一句话总结

CAPA 发现视觉 attention sink 功能异质——分为可安全剪枝的"概率倾卸（Probability Dumps）"与必须保留的"结构锚点（Structural Anchors）"；中层 FFN 对图像 token 呈近似线性行为，可用低秩/线性近似替代——双策略协同压缩视觉计算。

---

## 二、研究背景与动机

VLM 推理的高成本主要来自数千个视觉 token。主流做法用注意力分数估计 token 重要性，但注意力概率只是"权重分配"，未考虑被加权对象（value 向量）的幅度——高注意力 × 小 value 实际贡献甚微。同时 attention sink 现象在视觉 token 中普遍存在，过去被笼统视为可剪或必须保留，缺乏功能层面的细分。

---

## 三、方法与创新点

1. **注意力贡献准则**：importance = attention 概率 × ||value 向量||，比裸注意力分数更准确刻画 token 对下游表示的真实贡献。
2. **视觉 sink 异质性发现**：将视觉 attention sink 分为两类——Probability Dumps（低贡献，纯概率泄洪口，可剪）与 Structural Anchors（高贡献，维持性能的关键结构，须保留）。
3. **FFN 冗余分析与近似**：识别出视觉 token 在中层 FFN 上的线性行为，提出对这部分计算做近似替代，与 token 剪枝正交叠加。

---

## 四、实验与结果

摘要未给出具体数字，但声明 CAPA 在多个大型 VLM 上以贡献准则剪枝 + FFN 近似显著降低视觉计算成本，同时保持任务性能。

---

## 五、局限与开放问题

贡献准则仍依赖注意力内部信号，对跨层间接影响的刻画有限；FFN 线性近似的适用层范围需逐模型标定；两类 sink 的自动判别阈值是否跨架构稳定未明。

---

## 六、启示与借鉴

1. "概率 × 幅度"的贡献视角可推广到 KV cache 驱逐、专家路由等其他 token 选择场景——选择准则应度量实际影响而非分配权重。
2. attention sink 的功能异质细分（Dumps vs Anchors）提醒我们：现象学标签（"sink 可删/不可删"）必须落到机制层面才有工程指导价值。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
