# 技术深度分析：Learning to Accelerate Vision-Language-Action Models through Adaptive Visual Token Caching (arXiv:2602.00686)

> **论文**: Learning to Accelerate Vision-Language-Action Models through Adaptive Visual Token Caching
> **作者**: Yujie Wei, Jiahan Fan, Jiyu Guo, Ruichen Zhen, et al.
> **arXiv**: https://arxiv.org/abs/2602.00686 ｜ 提交: 2026-01-31 ｜ 分类: cs.RO

---

## 一、核心速览

### 研究主题

视觉-语言-动作（VLA）机器人模型的自适应视觉 token 缓存加速：把推理加速从启发式规则重构为可学习的策略优化问题。

### 一句话总结

两个轻量协作模块——Cached Token Selector（选哪些 token 复用）与 Cache Ratio Predictor（决定复用多少）——通过可微松弛端到端训练，让缓存策略随任务与场景动态自适应，替代与任务目标脱节的静态规则。

---

## 二、研究背景与动机

VLA 模型在机器人操作上泛化出色，但计算开销阻碍真实部署。现有加速多用规则式 token 缓存/剪枝：固定阈值、固定比例，与任务目标脱节，无法适应动态场景变化（机械臂移动时场景剧变需要重新计算，静止时可大量复用）。

---

## 三、方法与创新点

1. **加速即策略学习**：把 token 缓存决策显式建模为可学习策略，由任务目标端到端优化。
2. **双模块解耦**：Selector 解决"哪些"（离散选择），Ratio Predictor 解决"多少"（连续比例），协作覆盖决策空间。
3. **可微松弛**：离散缓存决策通过松弛技巧纳入梯度训练，避免强化学习式的高方差估计。

---

## 四、实验与结果

摘要未给出具体数字，声明在机器人操作任务上以可学习缓存策略显著降低 VLA 推理开销且保持成功率。

---

## 五、局限与开放问题

两个附加模块引入训练成本与部署复杂度；策略在分布外场景（新物体、新光照）的稳定性未知；与量化/剪枝等其他加速手段叠加时的相互作用未探索。

---

## 六、启示与借鉴

1. "压缩/加速决策可学习化"是本月 VLA 方向的共同趋势（与 EcoVLA 的环境感知剪枝呼应）——静态启发式正在被策略学习取代。
2. Selector + Ratio 的双模块解耦模式可借鉴到 KV cache 管理：逐 token 选择与全局预算宜分开建模。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
