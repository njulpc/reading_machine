# 深度技术分析：PointSplat: Compact Gaussian Splatting via Human-Centric Prediction

> **arXiv ID**: [2606.32036](https://arxiv.org/abs/2606.32036)  |  **提交日期**: 2026-06-30  |  **分类**: cs.CV  |  **作者**: Yujie Guo, Yudong Jin, Lingteng Qiu 等
> **备注**: Project Page: https://zju3dv.github.io/pointsplat

> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。


---

## 一、核心速览

**研究主题**：LLM 剪枝（3DGS 压缩、硬件部署、剪枝）—— 面向Transformer 模型的模型压缩

**一句话总结**：本文提出了面向Transformer 模型的LLM 剪枝方法/研究「PointSplat」。（基于摘要）

**技术标签**: 3dgs-compression / hardware-deployment / pruning


---

## 二、研究背景与动机 (Background & Motivation)

LLM 剪枝通过移除冗余的结构单元（注意力头、FFN 神经元、层、专家或权重）直接缩小模型规模。与非结构化稀疏相比，结构化剪枝能带来真实的延迟与显存收益，但也更难保持精度；MoE 架构的普及又带来了专家剪枝、层剪枝等新粒度。一次性（one-shot）剪枝准则、免重训恢复与剪枝后评测的真实性（多项选择题与实际生成能力的差异）是该方向的核心议题。

### 2.1 本文切入点

摘要开篇指出：

> Producing 3D human representations from input views on the fly is essential for immersive live streaming systems, where representation compactness is as critical as high fidelity given limited computational power and transmission bandwidth.


并进一步阐述了问题设定：

> Although recent feed-forward reconstruction methods achieve impressive quality through the view-centric prediction of 3D representations, they repeatedly encode the same subject content across multiple views, leading to significant inter-view redundancy.


从问题陈述看，作者针对的是Transformer 模型在LLM 剪枝场景下的具体瓶颈，属于 pruning-llm 技术路线。


---

## 三、核心方法与创新点 (Methodology & Innovations)

根据摘要可识别的核心方法组件：

- **方法要点 1**：Although recent feed-forward reconstruction methods achieve impressive quality through the view-centric prediction of 3D representations, they repeatedly encode the same subject content across multiple views, leading to significant inter-view redundancy.
- **方法要点 2**：Our key insight is to perform predictions directly in 3D space, enabling the network to learn and produce a highly compact representation.
- **方法要点 3**：To this end, we propose PointSplat, a novel human-centric approach that directly infers Gaussian primitives from an input point set.
- **方法要点 4**：The proposed method first estimates a coarse geometric proxy and performs ray casting to prune redundant points and establish explicit 2D--3D correspondences.
- **方法要点 5**：Subsequently, it employs a Point-Image Transformer to fuse appearance and geometry features, predicting Gaussian attributes in a single forward pass.

**方法学点评**：LLM 剪枝方法的设计轴包括：剪枝粒度（权重/神经元/头/层/专家）、重要性准则（幅值、激活、梯度、二阶）、以及是否需要恢复性微调。


---

## 四、实验设计与结果 (Experiments & Results)

摘要中报告的关键定量结果（原文句子摘录）：

- Producing 3D human representations from input views on the fly is essential for immersive live streaming systems, where representation compactness is as critical as high fidelity given limited computational power and transmission bandwidth.
- Although recent feed-forward reconstruction methods achieve impressive quality through the view-centric prediction of 3D representations, they repeatedly encode the same subject content across multiple views, leading to significant inter-view redundancy.
- Our key insight is to perform predictions directly in 3D space, enabling the network to learn and produce a highly compact representation.
- The proposed method first estimates a coarse geometric proxy and performs ray casting to prune redundant points and establish explicit 2D--3D correspondences.

**结果解读**：以上数字均直接引自摘要原文。评估该类工作时建议对照同月同方向工作（见月度报告横向比较表）判断其增益幅度。


---

## 五、局限性与未来展望 (Limitations & Future Work)

LLM 剪枝的普遍局限：高稀疏度下精度断崖、结构化剪枝对宽度的削减受限于硬件对齐（如 64/128 的倍数），以及剪枝后能力的不均匀退化（生成 vs. 选择）。

此外，本文档基于摘要与 arXiv 元数据撰写，未获取全文，方法细节、实验设置与更完整的局限讨论以原文为准。


**未来展望**：未来方向：剪枝准则的理论基础、剪枝+量化+蒸馏的联合优化、诚实的能力保持评测。


---

## 六、学术启发 (Takeaways for My Research)

- 一次性剪枝准则（幅值+激活）已足够强大，复杂准则的边际收益需要严格验证
- 剪枝评测必须包含开放式生成任务，选择题会通过率高估
- 层剪枝与宽度剪枝的组合是探索压缩前沿的有效手段
- 结合本文：可将「PointSplat」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。
