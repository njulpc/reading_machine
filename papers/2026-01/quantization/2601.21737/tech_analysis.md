# 技术深度分析：Mixed-Precision Training and Compilation for RRAM-based Computing-in-Memory Accelerators (arXiv:2601.21737)

> **论文**: Mixed-Precision Training and Compilation for RRAM-based Computing-in-Memory Accelerators
> **作者**: Rebecca Pelke, Joel Klein, Jose Cubero-Cascante, Nils Bosbach
> **arXiv**: https://arxiv.org/abs/2601.21737 ｜ 提交: 2026-01-29 ｜ 分类: cs.LG, cs.ET

---

## 一、核心速览

### 研究主题

面向 RRAM 存内计算（CIM）加速器的混合精度训练与编译框架：强化学习搜索量化配置，突破多数 CIM 编译器不支持 8-bit 以下量化的限制。

### 一句话总结

针对 CIM 交叉阵列输入/单元比特宽度有限而编译器仅支持 ≥8-bit 的错配，框架用 RL 策略在巨大搜索空间中找到平衡时延与精度的量化配置：最优情况较 SOTA 方案加速 2.48×，精度损失仅 0.086%。

---

## 二、研究背景与动机

CIM 加速器在交叉阵列上直接做矩阵-向量乘，能效潜力大。但交叉阵列的输入与单元比特宽度天然有限（RRAM 单元多级但精度受限），而多数 CIM 编译器不支持 8-bit 以下量化——一个 MVM 需多个计算周期，权重无法高效存入单单元。训练-编译联合的混合精度是解锁路径，但搜索空间巨大。

---

## 三、方法创新

1. **训练-编译联合框架**：量化配置在训练阶段确定并直接映射到 CIM 编译——算法-硬件闭环。
2. **RL 量化配置搜索**：强化学习策略在庞大搜索空间中找时延-精度平衡点——解决搜索空间爆炸问题。
3. **面向 CIM 约束的量化**：比特分配直接对应交叉阵列的物理约束（单元精度、周期数）。

---

## 四、实验结果

- 最优情况较现有 SOTA 方案**加速 2.48×**，精度损失仅 **0.086%**。

---

## 五、局限与展望

- RL 搜索本身成本未量化。
- RRAM 器件噪声/变异对量化后精度的实际影响（仿真 vs 实测）未说明。
- 网络规模（MLP/CNN 级）向 transformer 的扩展待验证。

---

## 六、学术启发

1. CIM 的量化是"训练-编译一体"问题——比特决策必须看到物理单元约束，纯算法侧 PTQ 不够用。
2. RL 搜索量化配置与 AgenticPruner 的 LLM 智能体剪枝殊途同归——压缩配置搜索的学习化趋势。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
