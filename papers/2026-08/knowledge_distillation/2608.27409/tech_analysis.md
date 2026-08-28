# 深度技术分析：Consolidating RLVR Capabilities Across Domains: A Deep Dive into Fusion Paradigms

> arXiv: [2608.27409](https://arxiv.org/abs/2608.27409)
> v1 提交日期：2026-08-27
> 主分类：Computation and Language (cs.CL)
> 分类：cs.CL
> 作者：Siye Wu, Kai Yang, Yuchen Cai, Xin Xu, Peng-Yuan Wang, Jiaxuan Wang, Jiashun Liu, Jiafei Lyu 等
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：知识蒸馏。

**一句话总结**：该研究在共享专家和数据下统一比较 task-vector merge、混合 RL 与多教师 OPD，给出多域能力整合的成本选择规则。

## 2. 研究背景与动机

论文直接针对的瓶颈是：Reinforcement learning with verifiable rewards (RLVR) improves specific capabilities of large language models, but covering multiple capabilities often involves training separate domain experts and subsequently consolidating them. 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- Merge 直接组合专家 task vectors。
- Mix RL 混合各域数据继续可验证奖励训练。
- MOPD 同时复用教师和数据，在学生自身轨迹上蒸馏。

- 核心区别：该研究在共享专家和数据下统一比较 task-vector merge、混合 RL 与多教师 OPD，给出多域能力整合的成本选择规则。

## 4. 实验设计与结果

跨模型尺度和多域套件，三范式平均差距不超过 1.4 点，但单个 benchmark 可达 8.6 点；都提高 single-sample accuracy，却未测到 solution coverage 增益或 held-out capability 损失。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

结论依共享专家与数据设置；MOPD 受教师上限、Mix RL 受比例、Merge 受 task-vector 几何，训练和存储总成本仍需统一计价。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

多专家压缩不存在全局最优融合范式；应按已有资产、是否需超越教师和部署成本选择。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
