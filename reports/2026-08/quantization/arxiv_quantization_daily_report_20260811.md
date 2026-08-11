# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-08-11 (昨天24小时内)  
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, KV cache  
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV, cs.AI)

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2608.09595 | From Sweep to Seam: Interleaved Cross-Block Post-Training Quantization | Achille Jacquemond 等 | 08-11 | Quantization, Cross-Block, PTQ, Kernel Fusion | cs.AI |
| 2 | 2608.08910 | Tied Trit-Planes: Constraining PTQTP to a Uniform Nine-Level Quantizer | Matteo Grella | 08-11 | Quantization, Trit-Planes, MoE Serving, Low-bit | cs.CL |
| 3 | 2608.08624 | Domain-Aware Pruning: Sparsity and Domain Generalization via Regularized Probabilistic Masking | Parham Sazdar 等 | 08-11 | Pruning, Sparsity, Domain Generalization | cs.LG |
| 4 | 2608.08794 | Deferred Audio Pruning with Local Audio-Visual Dynamics for Omni-LLMs | Kyeongyoon Lee 等 | 08-11 | Pruning, Audio, Multimodal, Omni-LLM | cs.LG |
| 5 | 2608.09287 | UniDFKD: A Unified Semantic Prior Framework for Architecture-Agnostic Data-Free Knowledge Distillation | Xuewan He 等 | 08-11 | Knowledge Distillation, Data-Free, Semantic Prior | cs.CV |
| 6 | 2608.09637 | DUET: A Diversity-Quality Duet of Distillation Experts for Two-Step Video Generation | Zian Li 等 | 08-11 | Distillation, Video Generation, Diffusion | cs.CV |
| 7 | 2608.09931 | Perception Before Supervision: Self-Contained Visual Distillation from Counterfactual Blind Spots | Shravan Venkatraman 等 | 08-11 | Distillation, Self-Supervised, MLLM, Counterfactual | cs.CV |
| 8 | 2608.08684 | RippleKV: Cross-Layer KV Cache Allocation via Perturbation Propagation | Dongjie Xu 等 | 08-11 | KV Cache, Cross-Layer, Allocation, Long Context | cs.LG |
| 9 | 2608.09412 | KVDiagnosis: A Diagnostic Benchmark for KV-Cache Compression in Long-Context Language Models | Chen Qiu 等 | 08-11 | KV Cache, Diagnosis, Benchmark, Long Context | cs.AI |
| 10 | 2608.08878 | DistillCache: KL-Guided Adaptive KV-Cache Eviction for Memory-Efficient LLM Inference | Asaad Althoubi | 08-11 | KV Cache, Eviction, KL Divergence, Memory | cs.LG |
| 11 | 2608.09176 | Not All Visual Tokens Are Equally Safe to Remove: Consequence-Sensitive Visual Token Compression | Jingbo Wen 等 | 08-11 | Token Compression, VLM, Consequence-Sensitive | cs.CV |
| 12 | 2608.08960 | Reading is not Reasoning: Bridging the Agentic Policy Gap in Vision-Text Compression | Cheng Fan 等 | 08-11 | Token Compression, Agent, Vision-Text, Policy | cs.AI |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 2篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| ICB-PTQ (2608.09595) | Block-wise PTQ (2-bit) | LLM | 交错执行实现同类型块并行量化，消除顺序依赖，支持内核融合 |
| Tied Trit-Planes (2608.08910) | Trit-Plane (≈3-bit) | LLM / MoE | 固定比例3:1约束双因子为统一九级量化器，设计持久折叠格式支持磁盘流式加载 |

### 2.2 剪枝 (Pruning) — 2篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Domain-Aware Pruning (2608.08624) | Unstructured Probabilistic | CNN | 联合优化稀疏结构与领域泛化，正则化概率掩码 |
| Deferred Audio Pruning (2608.08794) | Structured Temporal | Omni-LLM | 利用局部音视频动态延迟决策音频token剪枝 |

### 2.3 知识蒸馏 (Knowledge Distillation) — 3篇

| 论文 | 蒸馏类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| UniDFKD (2608.09287) | Data-Free, Architecture-Agnostic | 通用 | 统一语义先验框架，支持任意教师-学生架构组合 |
| DUET (2608.09637) | Diversity-Quality Dual Expert | Video Diffusion | 双专家分别负责多样性与质量，两步视频生成 |
| Perception Before Supervision (2608.09931) | Self-Supervised Visual | MLLM | 利用反事实盲点实现无外部监督的自包含视觉蒸馏 |

### 2.4 KV Cache 压缩 — 3篇

| 论文 | 压缩类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| RippleKV (2608.08684) | Cross-Layer Allocation | LLM | 建模扰动层间传播，实现跨层KV Cache最优预算分配 |
| KVDiagnosis (2608.09412) | Diagnostic Benchmark | LLM | 细粒度诊断KV Cache压缩方法的能力边界与失效模式 |
| DistillCache (2608.08878) | Adaptive Eviction | LLM | KL散度引导的自适应KV Cache逐出，保持分布稳定性 |

### 2.5 Token 压缩 — 2篇

| 论文 | 压缩类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Consequence-Sensitive (2608.09176) | Visual Token Pruning | VLM | 后果敏感性评估，从相关性到因果性的token剪枝 |
| Agentic Policy Gap (2608.08960) | Vision-Text Compression | Agent LLM | 面向代理策略决策的上下文压缩，而非语义完整性 |

---

## 三、按应用领域分类

| 应用领域 | 论文数量 | 代表性论文 |
|---------|:-------:|-----------|
| **大语言模型 (LLM)** | 5 | ICB-PTQ, Tied Trit-Planes, RippleKV, KVDiagnosis, DistillCache |
| **计算机视觉 (CV)** | 3 | UniDFKD, DUET, Perception Before Supervision |
| **多模态 (VLM/MLLM)** | 3 | Deferred Audio Pruning, Consequence-Sensitive, Agentic Policy Gap |
| **视频生成** | 1 | DUET |
| **Agent 系统** | 1 | Agentic Policy Gap |

---

## 四、值得关注的高亮点

1. **ICB-PTQ (2608.09595)**：首次在交叉块PTQ中实现交错执行模式，打破严格的顺序依赖，为低比特LLM推理提供了约2-3倍的量化步骤加速潜力。

2. **Tied Trit-Planes (2608.08910)**：通过简单的固定比例约束，将复杂的双因子三值平面简化为统一九级量化器，同时为MoE模型设计了专用的磁盘流式加载格式。

3. **RippleKV (2608.08684)**：将KV Cache压缩从逐层独立优化提升为跨层联合优化，通过扰动传播模型实现了固定总预算下的全局最优分配。

4. **KVDiagnosis (2608.09412)**：倡导从"比较分数"到"理解机制"的评估范式转变，为KV Cache压缩领域提供了急需的细粒度诊断工具。

---

## 五、Quantization 论文评分

| 论文 | 精度效果 (1-10) | 压缩倍率 (1-10) | 创新性 (1-10) | 可复现性 (1-10) | 综合 |
|------|:-------------:|:-------------:|:-----------:|:-------------:|:----:|
| ICB-PTQ (2608.09595) | 8 | 8 | 9 | 8 | 33/40 |
| Tied Trit-Planes (2608.08910) | 8 | 7 | 8 | 9 | 32/40 |

### 评分说明

**ICB-PTQ (2608.09595)**：
- **精度效果 8/10**：保持交叉块PTQ的精度优势，理论证明交错执行不引入额外误差
- **压缩倍率 8/10**：支持2-bit块级量化，达到8x压缩比
- **创新性 9/10**：首次从系统执行顺序角度优化PTQ实现，算法-系统协同设计
- **可复现性 8/10**：方法清晰，核心思想易于实现，但内核融合需要特定硬件支持

**Tied Trit-Planes (2608.08910)**：
- **精度效果 8/10**：固定比例约束的精度损失在可接受范围内，统一九级量化有硬件友好性
- **压缩倍率 7/10**：有效存储约3-bit，压缩比约4.7x，缩放因子存储减少50%
- **创新性 8/10**：约束即简化的设计哲学，持久折叠格式对MoE服务有实际价值
- **可复现性 9/10**：方法极为简洁，比例3的约束直接明了，实现简单

---

## 六、整体分析

### 6.1 当日趋势

2026-08-11 的模型压缩领域呈现出以下特点：

1. **系统级优化崛起**：ICB-PTQ 代表了从纯算法创新向算法-系统协同设计的转变，执行顺序重排成为新的优化维度。

2. **诊断与评估受重视**：KVDiagnosis 反映了社区对压缩方法细粒度理解的渴望，从"哪个方法更好"转向"为什么好"。

3. **多模态压缩需求增长**：Deferred Audio Pruning 和 Consequence-Sensitive Visual Token Compression 表明，VLM/MLLM 的高效推理已成为重要研究方向。

4. **KV Cache 持续热门**：3篇KV Cache论文涵盖了分配策略、诊断基准和逐出机制，显示该方向仍是活跃前沿。

### 6.2 技术交叉

当日论文体现了多个技术交叉点：
- **量化 + 系统**：ICB-PTQ 的交错执行
- **剪枝 + 领域泛化**：Domain-Aware Pruning 的联合优化
- **蒸馏 + 自监督**：Perception Before Supervision 的反事实学习
- **压缩 + 诊断**：KVDiagnosis 的细粒度评估

### 6.3 未来方向

基于当日论文，可预见以下研究趋势：
- **执行级优化**：更多工作将关注压缩算法的系统实现效率
- **因果感知压缩**：从相关性到因果性的压缩决策
- **自适应资源分配**：根据输入内容和任务动态调整压缩策略
- **多模态统一压缩**：跨模态联合稀疏和量化

---

*报告生成时间: 2026-08-12*  
*分析师: AI Assistant (Auto-generated)*
