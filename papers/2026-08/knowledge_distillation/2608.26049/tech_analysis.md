# 深度技术分析：RTLGuard: A Lightweight Teacher-Student Defense for Poisoned RTL Code Generation Models

> arXiv: [2608.26049](https://arxiv.org/abs/2608.26049)
> v1 提交日期：2026-08-26
> 分类：cs.CR, cs.AR
> 作者：Mahshid Rezakhani, Kimia Azar, Hadi Kamali
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：知识蒸馏；RTLGuard: A Lightweight Teacher-Student Defense for Poisoned RTL Code Generation Models。

**一句话总结**：RTLGuard 用少量可信 RTL 训练小型 clean teacher，再以特征与知识蒸馏清洗被投毒的代码生成目标模型，避免全参数重训。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：The rapid advancement of large language models (LLMs) is driving a shift toward automated register transfer level (RTL) code generation, enabling designers to translate high-level specs. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- 在可信 RTL 子集上微调小 teacher。
- 对可疑目标模型联合使用 teacher-student output objective 与 feature alignment。
- 同时评价攻击成功率、功能正确性和可综合性。

- 方法的核心区别是：RTLGuard 用少量可信 RTL 训练小型 clean teacher，再以特征与知识蒸馏清洗被投毒的代码生成目标模型，避免全参数重训。

## 4. 实验设计与结果

全文跨多种 LLM 架构报告显著降低 Attack Success Rate，并保持生成 RTL 的功能与 synthesis；摘要未给可跨架构汇总的单一百分比，因此不补写不存在的统一数字。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

小 teacher 可能能力不足且可信数据覆盖有限；适应性触发器、不同 Trojan 类型和 teacher 本身供应链风险仍可能绕过清洗。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

蒸馏不仅能压缩能力，也可作为“受信任小模型约束大模型”的供应链净化机制。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
