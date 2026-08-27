# 深度技术分析：Not All Attention Heads Contribute to Critical Visual Token Selection: Head-Aware Pruning Matters More

> arXiv: [2608.25332](https://arxiv.org/abs/2608.25332)
> v1 提交日期：2026-08-26
> 分类：cs.CV
> 作者：Chaofang Ma, Lin Jiang, Carol Jingyi Li, Xingyu Liu, Zeyu Li, Jiang Xu, Wei Zhang
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：剪枝/稀疏；Not All Attention Heads Contribute to Critical Visual Token Selection: Head-Aware Pruning Matters More。

**一句话总结**：ProViP 先判断哪些注意力头真正擅长定位关键视觉证据，再用这些头逐层剪 token，避免全头平均稀释信号。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：Vision-Language Models (VLMs) have exhibited impressive performance across diverse visual scenarios. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- 输入阶段按 embedding 相似度先去除明显冗余视觉 token。
- 估计头级视觉证据定位能力，只聚合高贡献 head。
- 训练免费、渐进式地在 LLM 推理过程中继续剪 token。

- 方法的核心区别是：ProViP 先判断哪些注意力头真正擅长定位关键视觉证据，再用这些头逐层剪 token，避免全头平均稀释信号。

## 4. 实验设计与结果

LLaVA-1.5-7B 在 88.9% token pruning ratio 下保留原性能的 95.9%，并实现 1.62 倍推理加速。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

注意力 head 的“贡献”仍是相关性代理，可能随问题和层变化；聚合/排序自身有开销，且摘要只给一个模型的代表性速度点。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

token pruning 可以先做 head selection，再做 token selection，把评分器可靠性显式纳入压缩算法。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
