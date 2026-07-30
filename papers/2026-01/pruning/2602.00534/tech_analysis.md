# 技术深度分析：AIRE-Prune: Asymptotic Impulse-Response Energy for State Pruning in State Space Models (arXiv:2602.00534)

> **论文**: AIRE-Prune: Asymptotic Impulse-Response Energy for State Pruning in State Space Models
> **作者**: Apurba Prasad Padhy, Fernando Camacho, Saibal Mukhopadhyay
> **arXiv**: https://arxiv.org/abs/2602.00534 ｜ 提交: 2026-01-31 ｜ 分类: cs.LG, eess.SY

---

## 一、核心速览

### 研究主题

状态空间模型（SSM）的结构化后训练状态剪枝：以闭式"渐近脉冲响应能量"为每个状态打分，直接最小化长程输出能量失真，削减各层状态维度。

### 一句话总结

AIRE-Prune 为每个状态计算无限时域上贡献的总脉冲响应能量（闭式解），层内归一化后跨层全局比较选择——SISO/MIMO SSM 平均剪枝 60.8%，免重训平均精度仅降 0.29%，把经典模态截断从单系统推广到深度堆叠。

---

## 二、研究背景与动机

SSM（Mamba 等）以大状态维度换取长程记忆，但大状态带来显存与计算开销，现有降维手段常牺牲容量、搜索空间或稳定性。控制论中的模态截断（modal truncation）有成熟的能量准则，但只适用于单系统，无法直接用于深度网络逐层剪枝的全局预算分配。

---

## 三、方法与创新点

1. **闭式重要性分数**：每个状态的渐近（无限时域）脉冲响应能量有解析解，无需数据前向即可计算。
2. **逐层归一化 + 全局选择**：分数层内归一化后可跨层比较，实现全局状态预算的最优分配——把单系统模态截断扩展到深度堆叠。
3. **对齐渐近响应能量而非最坏增益**：与 H∞ 准则不同，能量准则更贴合平均性能保持。

---

## 四、实验与结果

多个序列基准上：SISO 与 MIMO SSM 平均剪枝 60.8%，无重训平均精度下降仅 0.29%，同时显著降低计算量。代码已开源（GitHub falcon-arrow/AIRE-Prune）。

---

## 五、局限与开放问题

能量准则基于线性时不变假设，对输入依赖型（selective）SSM 的时变动态是近似；闭式分数忽略层间非线性耦合；对极长序列任务的适用性需更多验证。

---

## 六、启示与借鉴

1. 经典控制理论（模态截断、能量准则）是 SSM 压缩的现成工具箱——跨学科方法迁移的范例。
2. "闭式分数 + 全局预算分配"模式比逐层独立剪枝更优，这一思想同样适用于 Transformer 宽度剪枝。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
