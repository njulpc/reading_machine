# 深度技术分析：TMP: Tree-structured Mixed-policy Pruning for Large-scale Image Generation and Editing

> **arXiv ID**: [2606.27089](https://arxiv.org/abs/2606.27089)  |  **提交日期**: 2026-06-25  |  **分类**: cs.CV  |  **作者**: Peizhen Zhang, Yang Li, Xunsong Li 等
> **备注**: 10 pages, 3 figures, 3 tables, tech report

> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。


---

## 一、核心速览

**研究主题**：LLM 剪枝（知识蒸馏、硬件部署、剪枝）—— 面向扩散模型的模型压缩

**一句话总结**：本文研究了面向扩散模型的LLM 剪枝方法/研究「TMP」，关键结果包括：75%。（基于摘要）

**技术标签**: distillation / hardware-deployment / pruning


---

## 二、研究背景与动机 (Background & Motivation)

LLM 剪枝通过移除冗余的结构单元（注意力头、FFN 神经元、层、专家或权重）直接缩小模型规模。与非结构化稀疏相比，结构化剪枝能带来真实的延迟与显存收益，但也更难保持精度；MoE 架构的普及又带来了专家剪枝、层剪枝等新粒度。一次性（one-shot）剪枝准则、免重训恢复与剪枝后评测的真实性（多项选择题与实际生成能力的差异）是该方向的核心议题。

### 2.1 本文切入点

摘要开篇指出：

> Modern image generation model rapidly grows their sizes to meet high-fidelity image synthesis.


并进一步阐述了问题设定：

> However, they gradually become unaffordable for their enormous parameter consumption and computation budget that lead to massive resources requirement and gpu memory footprint.


从问题陈述看，作者针对的是扩散模型在LLM 剪枝场景下的具体瓶颈，属于 pruning-llm 技术路线。


---

## 三、核心方法与创新点 (Methodology & Innovations)

根据摘要可识别的核心方法组件：

- **方法要点 1**：However, they gradually become unaffordable for their enormous parameter consumption and computation budget that lead to massive resources requirement and gpu memory footprint.
- **方法要点 2**：In this paper, we propose TMP, the first Tree-structured Mixed-policy Pruning framework that generalizes prevalent image tasks (T2I and TI2I) and architectures (Mixture-of-Experts (MoE) and Diffusion transformer (DiT)).
- **方法要点 3**：It could be applied to the step-distilled models and contribute as the last stage.
- **方法要点 4**：We perform experiments upon current open-sourced SOTA HunyuanImage-3.0 instruct and a popular efficient model Z-Image turbo.
- **方法要点 5**：The proposed pruning framework manages to compress HunyuanImage 3.0 from 80B to 20B parameters at 75% reduction ratio, sacrificing limited generation quality.

**方法学点评**：LLM 剪枝方法的设计轴包括：剪枝粒度（权重/神经元/头/层/专家）、重要性准则（幅值、激活、梯度、二阶）、以及是否需要恢复性微调。


---

## 四、实验设计与结果 (Experiments & Results)

摘要中报告的关键定量结果（原文句子摘录）：

- In this paper, we propose TMP, the first Tree-structured Mixed-policy Pruning framework that generalizes prevalent image tasks (T2I and TI2I) and architectures (Mixture-of-Experts (MoE) and Diffusion transformer (DiT)).
- We perform experiments upon current open-sourced SOTA HunyuanImage-3.0 instruct and a popular efficient model Z-Image turbo.
- The proposed pruning framework manages to compress HunyuanImage 3.0 from 80B to 20B parameters at 75% reduction ratio, sacrificing limited generation quality.
- We also optimize to enable the inference of the pruned 20B version of HunyuanImage 3.0 on a single 24GB 4090 GPU by engineering skills.
- The inference script and model weight have been integrated into the existing HunyuanImage3.0 open-source github and huggingface repository.
- Besides, we prove the efficacy of TMP by compressing Z-Image turbo from 6B to 4B (33% reduction) with negligible degradation.

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
- 结合本文：可将「TMP」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。
