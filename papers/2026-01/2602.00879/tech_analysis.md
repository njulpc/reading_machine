# 技术深度分析：Dynamic Expert Sharing: Decoupling Memory from Parallelism in Mixture-of-Experts Diffusion LLMs (arXiv:2602.00879)

> **论文**: Dynamic Expert Sharing: Decoupling Memory from Parallelism in Mixture-of-Experts Diffusion LLMs
> **作者**: Hao Mark Chen, Zhiwen Mo, Royson Lee, Qianzhou Wang, et al.
> **arXiv**: https://arxiv.org/abs/2602.00879 ｜ 提交: 2026-01-31 ｜ 分类: cs.LG

---

## 一、核心速览

### 研究主题

MoE 扩散 LLM 并行解码的专家共享优化：并行生成 token 数增加导致激活专家数近线性膨胀（专家爆炸），把推理推回访存受限——DES 以序列级 coreset 选择最大化专家复用。

### 一句话总结

DES 把 MoE 优化从 token 中心剪枝/专家跳过转向序列级核心集选择：为一个并行解码块挑选紧凑高效用的专家集合满足整块需求；DES-Seq（序列内共享最优分配）与 DES-Vote（显著性感知投票）两策略，解耦显存占用与并行度。

---

## 二、研究背景与动机

扩散 LLM 并行解码在质量与吞吐间取得平衡，但与 MoE 结合时出现专家爆炸：并行 token 越多，被激活的不同专家近线性增长，显存流量把推理推入访存受限区，抵消 MoE 与并行解码的双重效率收益。传统 token 级专家剪枝各自为政，未利用"同一块内 token 可共享专家"的结构。

---

## 三、方法与创新点

1. **问题重构**：从 token 中心转向序列级 coreset 选择——为整个并行块选一组高复用专家。
2. **DES-Seq**：序列内共享，把最优分配适配到序列粒度。
3. **DES-Vote**：显著性感知投票，聚合各 token 的专家偏好选出共识集合。
4. **显存-并行解耦**：块内专家数受控，并行度提升不再线性放大访存。

---

## 四、实验与结果

摘要未给出具体数字，声明 DES 在 MoE 扩散 LLM 上有效控制显存流量、恢复并行解码的效率收益，并保持生成质量。

---

## 五、局限与开放问题

coreset 选择引入每块一次性的决策开销；投票机制可能牺牲个别 token 的最优专家（质量-效率权衡的尾部风险）；对自回归 MoE 的迁移性未验证。

---

## 六、启示与借鉴

1. "块级共享预算"思想可推广：并行/批量推理场景下，任何 per-token 资源（专家、KV、注意力头）都应考虑块级统筹。
2. 投票聚合是离散资源分配的轻量近似——与可学习选择器（VLA token caching）相比各有成本-精度定位。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
