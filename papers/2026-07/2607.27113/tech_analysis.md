# 深度技术分析：Veritas++: Value-aware On-Policy Distillation for Perception-Enhanced AIGI Detection

## 1. 核心速览

**研究话题**：面向 AI 生成图像（AIGI）检测的感知增强多模态大模型

**一句话总结**：本文提出 VERITAS++，通过感知导向学习（PoRL）增强 MLLM 在 AIGI 检测中的细粒度视觉感知能力，并引入 Value-aware On-Policy Distillation（VaOPD）自适应蒸馏机制优先高价值信号，在多个基准上实现了优异的泛化性能。

---

## 2. 研究背景与动机

### 2.1 AIGI 检测的挑战

生成模型能力的快速增长使合成图像在开放媒体中日益普遍，AIGI 检测变得越来越重要。

现有 MLLM-based 检测器的问题：
- **感知瓶颈**：在捕捉细粒度异常方面存在不足
- 主要关注视觉证据如何组织和合成
- 内在感知能力优化不足

---

## 3. 核心方法与创新点

### 3.1 方法概述

**基础洞察**：将 AIGI 检测建立在三个基本感知能力上：
1. 捕捉细粒度视觉细节
2. 识别语义异常
3. 检测像素级差异

**模块一：Perception-oriented Learning (PoRL)**
- 用可验证奖励替代开放式描述监督
- 显式强化上述三种感知能力

**模块二：Value-aware On-Policy Distillation (VaOPD)**
- 自适应蒸馏机制，优先高价值蒸馏信号
- 通过 privileged self-teacher 内化感知感知推理

### 3.2 实验结果

在标准、in-the-wild 和新兴基准上均展现出良好的泛化性。

---

## 4. 学术启发

**感知-推理分离**：在需要细粒度判断的任务中，显式增强感知能力比直接优化最终推理更有效。

---

*论文信息：arXiv:2607.27113，Hao Tan 等，CASIA/UCAS*
