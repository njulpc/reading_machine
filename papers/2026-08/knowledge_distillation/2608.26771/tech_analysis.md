# 深度技术分析：Cross-Architecture Knowledge Distillation from a Vision Foundation Model to a Lightweight Visual State Space Model for Tea Leaf Disease Classification

> arXiv: [2608.26771](https://arxiv.org/abs/2608.26771)
> v1 提交日期：2026-08-27
> 主分类：Computer Vision and Pattern Recognition (cs.CV)
> 分类：cs.CV
> 作者：Zibo Zhou, Zongsen Qiu, Rui Chen, Yujie Yao, Yue Zhou, Jianjun Wang
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：知识蒸馏。

**一句话总结**：该工作把 DINOv2 教师跨架构蒸馏到 4.45M 参数双向视觉状态空间学生，并发现简单 logit KD 胜过特征对齐。

## 2. 研究背景与动机

论文直接针对的瓶颈是：Automated tea leaf disease classification supports precision agriculture, yet deploying accurate models on edge devices remains challenging under tight compute budgets. 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- 用 progressive convolution stem 修复大 patch embedding 对小数据训练的不稳定。
- 以 gated bidirectional selective-scan 保留残差路径。
- 温度缩放 logit distillation 对齐异构 ViT 与 VSSM，单独消融 feature alignment。

- 核心区别：该工作把 DINOv2 教师跨架构蒸馏到 4.45M 参数双向视觉状态空间学生，并发现简单 logit KD 胜过特征对齐。

## 4. 实验设计与结果

三随机种子下，KD 将测试准确率从 92.32±2.14% 提至 95.41±1.17%，最佳 96.20%、macro-F1 94.45%；4.45M 学生比 22M 教师少 5.0× 参数，并保留 98.3% 教师准确率。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

只在一个茶叶病害数据集和简化非官方 SSM 实现上验证；教师预训练成本未计入部署压缩，边缘真实延迟/能耗仍需测量。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

异构师生不必强行对齐中间特征；先修复学生训练动力学，再用输出蒸馏可能更稳。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
