# ArXiv 量化与模型压缩领域论文日报

**目标日期**: 2026-08-01（周六）
**收集日期范围**: 2026-07-30 补充收录（8 月 1 日为周六，arXiv 无新论文发布）
**检索关键词**: quantization, quantize, low-bit, model compression, pruning, sparsity, knowledge distillation, KV cache compression, mixed precision, GPTQ, AWQ
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV, cs.AI)

---

## 日期说明

2026-08-01 为周六，arXiv 系统周末不发布新论文（周五提交的论文将于周一 8 月 3 日公布）。经 arXiv API `submittedDate:[202608010000 TO 202608012359]` 检索确认当日零新增提交。

本次日报补充收录 4 篇 2026-07-30 提交但在前日流水线中遗漏的模型压缩相关论文，确保覆盖完整。

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 | 分类 |
|:---:|----------|---------|------|:-------:|-----------|------|------|
| 1 | 2607.28405 | QuantWAMs: Calibrating at the Right Granularity for World Action Models | Jiacheng Zhou 等（复旦大学） | 07-30 | PTQ, W4A4, Outlier Calibration, Fisher Saliency, WAM | cs.AI, cs.LG | 量化 |
| 2 | 2607.28341 | Capturing Token Tendencies for Training-Free Token Pruning in MLLMs | Jie Ma 等（厦门大学） | 07-30 | Token Pruning, Training-Free, MLLM, Trend-aware | cs.CV | 剪枝 |
| 3 | 2607.28449 | Lightning OPD 2.0: Mitigating Style Bias in Cross-Teacher OPD | Yecheng Wu, Song Han, Han Cai（MIT/NVIDIA） | 07-30 | On-Policy Distillation, Cross-Teacher, Style Bias | cs.CL | 知识蒸馏 |
| 4 | 2607.28627 | ReToken: One Token to Improve Vision-Language Models for Visual Retrieval | Yao Xiao 等 | 07-30 | Token Selection, KV Cache, VLM, Retrieval | cs.CV, cs.AI, cs.LG | 其他 |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 1 篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| QuantWAMs (2607.28405) | W4A4 PTQ | World Action Models (Fast-WAM, LingBot-VA) | 校准上下文原则：结构/分布/目标三维度对齐量化决策与部署场景 |

### 2.2 剪枝 (Pruning) — 1 篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Trend-aware Pruning (2607.28341) | Visual Token Pruning | MLLMs (LLaVA, Qwen2.5-VL) | 时序轨迹建模+动态纠正，77.8% Token 剪枝率 |

### 2.3 知识蒸馏 (Knowledge Distillation) — 1 篇

| 论文 | 蒸馏类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Lightning OPD 2.0 (2607.28449) | On-Policy Distillation | Large Reasoning Models | 交叉拟合风格残差化，解决跨教师 OPD 风格偏置 |

### 2.4 其他 (Other) — 1 篇

| 论文 | 技术类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| ReToken (2607.28627) | Token Selection | VLMs (Qwen3VL-8B, InternVL3.5) | 单 Token 学习式稀疏视觉 Token 检索 |

---

## 三、评分总览

### 评分标准说明
- **精度效果** (1-10)：量化/压缩后模型性能保持程度
- **压缩倍率** (1-10)：实际压缩比与加速效果
- **创新性** (1-10)：方法的新颖性与理论贡献
- **可复现性** (1-10)：代码可用性与方法描述的完整度

### 3.1 完整评分表

| 序号 | arXiv ID | 论文标题 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合均分 |
|:---:|----------|---------|:-------:|:-------:|:-----:|:-------:|:-------:|
| 1 | 2607.28405 | QuantWAMs | 9 | 8 | 8 | 7 | **8.0** |
| 2 | 2607.28341 | Trend-aware Pruning | 8 | 8 | 8 | 7 | **7.8** |
| 3 | 2607.28449 | Lightning OPD 2.0 | 9 | 5 | 8 | 6 | **7.0** |
| 4 | 2607.28627 | ReToken | 9 | 7 | 8 | 8 | **8.0** |

### 3.2 评分详细说明

#### 1. QuantWAMs (2607.28405)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 9/10 | W4A4 主导设置下仿真均值与 FP16 仅差 0.2-0.7 个百分点，真实机器人任务验证通过 |
| 压缩倍率 | 8/10 | 峰值权重-激活内存降至 FP16 的约 29%，块级加速 1.4-1.6 倍 |
| 创新性 | 8/10 | 首次提出"校准上下文"统一原则，pooling crossover 理论推导严谨，三维度协同设计 |
| 可复现性 | 7/10 | 方法描述详尽含完整公式，但依赖特定 WAM 架构（Fast-WAM、LingBot-VA），代码未公开 |

#### 2. Trend-aware Pruning (2607.28341)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 8/10 | 77.8% 剪枝率下保持竞争力性能，OCRBench 从 18.70 提升至 31.00 |
| 压缩倍率 | 8/10 | 视觉 Token 减少 77.8%，最终层仅保留约 23 个 Token |
| 创新性 | 8/10 | 将剪枝从静态快照决策升级为时序轨迹建模，动态纠正"晚熟"Token |
| 可复现性 | 7/10 | 训练无关方法降低复现门槛，但需特定 MLLM 架构，代码未明确公开 |

#### 3. Lightning OPD 2.0 (2607.28449)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 9/10 | AIME 2024 达 82.4%，LiveCodeBench v5 达 63.0%，持续超越 Lightning OPD |
| 压缩倍率 | 5/10 | 蒸馏方法不直接产生压缩比，但通过知识转移间接实现模型能力压缩 |
| 创新性 | 8/10 | 交叉拟合风格残差化首创，将风格偏置与语义证据分离 |
| 可复现性 | 6/10 | 方法涉及 rollout 级交叉拟合，实现复杂度高，代码"即将发布" |

#### 4. ReToken (2607.28627)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 9/10 | Visual Haystacks 上 Qwen3VL-8B 提升 13.4 分（>20% 相对），LVBench 零样本迁移 +8.0 分 |
| 压缩倍率 | 7/10 | 稀疏 Token 选择从 KV cache 中检索，有效减少注意力计算量 |
| 创新性 | 8/10 | 单一可学习 Token 作为检索目标，value 空间检索诊断驱动设计 |
| 可复现性 | 8/10 | 代码已开源 (GitHub)，轻量设计（单 H100 可训练推理） |

---

## 四、整体分析

### 4.1 技术趋势

本日收录的 4 篇论文反映了模型压缩领域的几个重要趋势：

1. **校准上下文意识的觉醒**：QuantWAMs 提出的"校准上下文"原则标志着 PTQ 研究从单纯追求低 bit 向"量化决策与部署场景对齐"的范式转变。这一思想不仅适用于 WAM，对标准 LLM 的量化也有深刻启示——校准数据分布、池化范围和目标函数必须与部署场景一致。

2. **时序动态建模进入 Token 剪枝**：Trend-aware Pruning 将时序轨迹建模引入 Token 剪枝领域，突破了传统静态评估的局限。这一思路与大模型中"深层 Token 重要性演化"的观察高度契合，为 LLM 的 Token 级压缩提供了新范式。

3. **蒸馏中的偏置解耦**：Lightning OPD 2.0 关注的跨教师风格偏置问题在实际工程中极为常见——SFT 数据来源混杂、蒸馏教师与 SFT 教师不一致是常态。交叉拟合风格残差化提供了一种实用的解耦方案。

4. **极简设计的力量**：ReToken 用单一可学习 Token 实现视觉 Token 检索，在多个基准上取得显著提升。这种"最小干预"设计哲学证明了轻量方法在特定任务上的有效性。

### 4.2 量化领域重点

QuantWAMs 是本日唯一的量化论文，也是重点复现对象。其核心贡献在于：

- **理论贡献**：Proposition 1（pooling crossover）给出了跨模块统计量池化的理论条件 N < N* = σ²/τ²，为实践中的池化决策提供了明确指导。
- **工程价值**：W4A4 设置下仅 0.2-0.7 pp 的精度损失和 29% 的内存占用，接近实用部署门槛。
- **方法论启示**：将 PTQ 决策视为"有限样本估计"，并从结构、分布、目标三个维度审查其部署有效性，这一框架可推广到标准 LLM 量化。

### 4.3 代码复现说明

对 QuantWAMs 进行了 Qwen3-0.6B 代码复现（`scripts/quantization/2607.28405/`），实现了三大核心组件：

1. **SharedBasisOutlierCalibration**：Hadamard 旋转 + 对角平滑 + Top-K 通道保留
2. **CoTrainingSaliency**：Empirical-Fisher 分数层级权重精度分配
3. **W4A4Quantizer**：混合精度量化（Top 20% 层升级 W8，Top 2% 离群值通道保留 BF16）

由于原论文针对 WAM 架构，复现中将"视频流目标"和"动作流目标"适配为 LLM 的"下一 Token 预测损失"和"隐藏状态一致性损失"，以演示联合 Fisher 的核心思想。

---

## 五、推荐阅读优先级

| 优先级 | 论文 | 推荐理由 |
|:-----:|------|---------|
| ★★★ | QuantWAMs (2607.28405) | 量化领域必读，校准上下文理论框架具普适性 |
| ★★★ | ReToken (2607.28627) | 代码开源，设计精巧，VLM 推理加速实用方案 |
| ★★☆ | Trend-aware Pruning (2607.28341) | Token 剪枝新范式，时序建模思路可迁移至 LLM |
| ★★☆ | Lightning OPD 2.0 (2607.28449) | 蒸馏工程实践，跨教师场景解决方案 |
