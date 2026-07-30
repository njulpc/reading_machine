# 深度技术分析：Sparsity Moves Computation: How FFN Architecture Reshapes Attention in Small Transformers

## 1. 核心速览
**研究话题**：稀疏化 (Sparsity)，目标对象为MoE模型

**一句话总结**：Architectural choices inside the Transformer feedforward network (FFN) block do not merely affect the block itself; they reshape the computations learned by the rest of the model。

---

## 2. 研究背景与动机 (Background & Motivation)

稀疏性（Sparsity）是神经网络中普遍存在的结构性质——无论是权重稀疏、激活稀疏还是注意力稀疏，都意味着大量计算可以被跳过。利用稀疏性压缩模型面临的核心挑战在于：稀疏模式的不规则性往往抵消理论上的计算节省，因此稀疏化方法必须与硬件执行特性（如 2:4 半结构化稀疏、块稀疏）协同设计，才能转化为真实加速。

就本文而言，作者的出发点（基于摘要）：Architectural choices inside the Transformer feedforward network (FFN) block do not merely affect the block itself; they reshape the computations learned by the rest of the model. We study this effect in one-layer Transformers trained on digit addition with carry, modular arithmetic, and histogram counting.

---

## 3. 核心方法与创新点 (Methodology & Innovations)
- **要点1**：We study this effect in one-layer Transformers trained on digit addition with carry, modular arithmetic, and histogram counting.
- **要点2**：Comparing dense FFNs, gated linear units (GLUs), mixture-of-experts (MoE), and MoE-GLUs, we find that sparse MoE routing can shift computation from FFN to attention, with the strongest ablation-visible effect on carry-based addition.
- **要点3**：We decompose this redistribution into reduced per-token FFN capacity and sparse partitioning across experts.
- **要点4**：Critically, frozen random routing nearly matches learned routing, suggesting that redistribution is driven largely by architectural sparsity rather than router-learned specialization.
- **要点5**：As a secondary finding, GLU-style multiplicative gating rotates task-relevant Fourier structure out of the per-neuron basis and into distributed subspaces, making neuron-level interpretability less informative while preserving structured computation.
- **要点6**：We validate these conclusions with random-routing, narrow-FFN, and top-2 MoE controls, plus parameter-matching, activation-function, and width-scaling analyses.

---

## 4. 实验设计与结果 (Experiments & Results)

摘要以定性结论为主，未给出可引用的具体数值；关键结论如下：
- We validate these conclusions with random-routing, narrow-FFN, and top-2 MoE controls, plus parameter-matching, activation-function, and width-scaling analyses.
- Together, these results show that local FFN design choices can have nonlocal consequences for Transformer computation.

---

## 5. 局限性与未来展望 (Limitations & Future Work)

稀疏化方法的实际收益高度依赖硬件对稀疏模式的支持程度；训练期稀疏与推理期稀疏的动机和约束不同，跨场景迁移需谨慎。

（注：本分析基于摘要与可获取信息撰写，论文正文中可能包含更详细的局限性讨论与消融实验。）

---

## 6. 学术启发 (Takeaways for My Research)

稀疏性的利用必须「算法-硬件闭环」：理论稀疏率只有匹配硬件粒度才能兑现为加速。本文的稀疏模式设计为评估其他稀疏方案提供了对照基准。

结合本文的具体设定（MoE模型，稀疏化 (Sparsity)），可进一步思考：该方法的核心机制（如摘要所述）能否与其他压缩手段（量化/剪枝/蒸馏/低秩）组合，在自研模型上形成级联压缩管线；其实验协议（基线选择、评测基准、压缩率口径）也可作为自己实验设计的参照模板。

---

*论文信息：arXiv:2605.09403，Gabriel Smithline, Chris Mascioli，提交于 2026-05-10，分类：cs.LG, cs.AI, cs.NE，https://arxiv.org/abs/2605.09403*
