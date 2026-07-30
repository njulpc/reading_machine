# 技术深度分析：ViTCoP: Accelerating Large Vision-Language Models via Visual and Textual Semantic Collaborative Pruning (arXiv:2601.17818)

> **论文**: ViTCoP: Accelerating Large Vision-Language Models via Visual and Textual Semantic Collaborative Pruning
> **作者**: Wen Luo, Peng Chen, Xiaotao Huang, LiQun Huang
> **arXiv**: https://arxiv.org/abs/2601.17818 ｜ 提交: 2026-01-25 ｜ 分类: cs.CV

---

## 一、核心速览

### 研究主题

视觉-文本语义协同剪枝框架 ViTCoP：视觉编码器内做冗余过滤 + LLM 内按层级特性逐步协同剪枝，用 K 向量 L2 范数作为 FlashAttention 兼容的显著性度量。

### 一句话总结

ViTCoP 双管齐下解决现有视觉 token 剪枝的两大局限——编码器内剪枝过早丢失关键视觉信息、LLM 内剪枝选中 token 间信息冗余；K 向量 L2 范数度量无需注意力图，与 FlashAttention 完全兼容。

---

## 二、研究背景与动机

LVLM 视觉 token 冗余严重、计算成本高，剪枝是主流加速。但现有方法位置选择两难：在视觉编码器剪枝——尚未与文本交互，容易过早丢失问题相关的关键视觉信息；在 LLM 剪枝——选中 token 间信息冗余（多个 token 编码同一区域）。需要视觉语义与文本语义协同的两级剪枝。

---

## 三、方法创新

1. **两级协同剪枝**：视觉编码器内做冗余过滤（去重复），LLM 内按层级特性逐步协同剪枝（保问题相关+多样性）——既不过早丢信息，又不留冗余。
2. **层级特性利用**：LLM 不同层的语义抽象程度不同，剪枝策略按层适配。
3. **K 向量 L2 范数显著性**：不依赖注意力图的 token 重要性度量（keys 的范数），与 FlashAttention 等加速技术兼容——工程可落地的关键设计。

---

## 四、实验结果

- 多个 LVLM 与基准上的大量实验验证（摘要截断，未给出具体剪枝率与精度数字）。

---

## 五、局限与展望

- K 范数作为显著性的理论依据（其代理的是什么）未充分论证。
- 两级剪枝的剪枝率分配需要调节。
- 视频 LVLM 的时序 token 剪枝适配未讨论。

---

## 六、学术启发

1. "何处剪"与"剪多少"同等重要——编码器+LLM 两级协同的位置设计应成为多模态剪枝的标准考量。
2. K 范数显著性度量值得与注意力分数类方法系统对比——免注意力图是 FlashAttention 时代的硬需求。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
