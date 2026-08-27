# 深度技术分析：One Symptom, Three Levers: A Critical Review of On-Policy Self-Distillation

> arXiv: [2608.25936](https://arxiv.org/abs/2608.25936)
> v1 提交日期：2026-08-26
> 分类：cs.LG, cs.AI, cs.CL
> 作者：Justin Robert, Raheel Qader
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：知识蒸馏；One Symptom, Three Levers: A Critical Review of On-Policy Self-Distillation。

**一句话总结**：该综述把 on-policy self-distillation 的 collapse 统一为三个可控杠杆：信号施加位置、教师可见的特权信息、以及教师随训练变化的时机。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：On-policy distillation trains a language model on its own generations while a teacher scores them token by token. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- 限制在数学推理 OPSD 文献并统一术语。
- 把 token weighting、privileged context 和 teacher dynamics 分开。
- 区分已有证据、命名不一致现象与仍有争议的因果解释。

- 方法的核心区别是：该综述把 on-policy self-distillation 的 collapse 统一为三个可控杠杆：信号施加位置、教师可见的特权信息、以及教师随训练变化的时机。

## 4. 实验设计与结果

论文不报告新实验；核心产出是把“collapse”从单一故障名拆成 3 个设计轴，并指出 OPSD 省去第二个更大教师但不自动消除分布收缩。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

范围集中于数学推理且是结构性评论；不同工作实验预算与 collapse 指标不统一，不能从综述直接推得最佳超参数。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

综述也可成为复现实验矩阵：对三条轴做正交消融，比继续堆新损失名更能解释失败。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
