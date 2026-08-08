# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-08-07 00:00–23:59 (前一天24小时内)  
**检索分类**: cs.LG, cs.CL, cs.CV  
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, KV cache, sparsity  
**数据来源**: arXiv.org (export.arxiv.org/api)

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 核心关键词 | 领域 | 一句话结论 |
|:---:|----------|---------|------|-----------|------|-----------|
| 1 | 2608.05253 | Beyond Rotations: AuroOFT for Expressive Quantized Orthogonal Fine-Tuning | Yue Han, Dianlin Wang | Quantization, Orthogonal Fine-Tuning, Low-bit | cs.LG | 通过Cayley变换参数化增强型正交旋转，突破传统qOFT线性变换表达能力限制，低比特适配性能提升显著 |
| 2 | 2608.05326 | QEvict: Recoverable Quantized KV Eviction for Attention-Drift-Robust Long-Context Decoding | Ayushman Garg 等 | KV Cache, Quantization, Eviction, Long-context | cs.LG | 首创可恢复量化驱逐机制，三层级KV Cache存储实现8倍压缩且长上下文准确率保持95%+ |
| 3 | 2608.06291 | BaKron: Efficient Quantization with Kronecker-Factored Hessians | Johann Birnick, Rayan Saab | Quantization, GPTQ, Hessian, KFAC | cs.LG | 将KFAC Kronecker分解Hessian引入GPTQ，利用前向后向双重视角指导舍入，W4A16下弥合30%量化-全精度差距 |
| 4 | 2608.02691 | Output-Aware Rotation for INT2 KV-Cache Quantization | Vincent-Daniel Yun 等 | KV Cache, INT2, Rotation, Quantization | cs.CL | 输出感知正交旋转替代输入感知旋转，INT2 KV Cache压缩达16倍且注意力输出分布稳定性大幅提升 |
| 5 | 2608.05240 | One Qubit Can Beat One Bit: Quantum Advantage for Post-Training Quantization | Yuma Ichikawa, Moeto Mishima | Quantum, PTQ, Binary, One-bit | cs.LG | 理论上证明量子比特在一比特PTQ中可利用叠加态编码多模式，某些场景下经典方法1.9倍优势 |
| 6 | 2608.05499 | APQF: Agentic Profiling-Guided Structured Pruning and Mixed-Precision Quantization | Sadegh Jafari 等 | Pruning, Quantization, Agent, Edge | cs.CV | LLM Agent驱动的自动化剪枝+混合精度协同搜索，ResNet-50上8倍压缩精度仅降0.8% |
| 7 | 2608.05464 | Effective pruning of task-trained recurrent neural networks using noisy fluctuations | Sanjith Senthil 等 | Pruning, RNN, Noise, Bio-inspired | cs.AI | 噪声涨落作为重要性探针+连接重标定软剪枝，RNN上80%稀疏度下MSE仅为传统剪枝43% |
| 8 | 2608.06296 | On-Policy Self-Distillation without Any Supervision | Yijiang Li 等 | Distillation, Self-distillation, Unsupervised | cs.CL | 完全无监督的自一致性蒸馏，GSM8K上达有监督SFT的94%性能，无需任何外部信号 |
| 9 | 2608.05739 | LiteKD-Net: Lightweight Knowledge-Distilled Network for Mobile Image Denoising | Zhou Zhiyi | Distillation, Mobile, Image Denoising | cs.CV | 特征级+关系级双重蒸馏，参数量减90%去噪PSNR仅降0.67dB，移动端实现40fps实时推理 |
| 10 | 2608.05604 | SkillZip: Contract-Preserving Graph Compression for Scalable Agent Skill Libraries | Xingyu Tan 等 | Compression, Graph, Agent, Skills | cs.AI | 技能依赖图的契约保持压缩，500个API技能库压缩4.2倍且任务成功率仅降1.4% |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 5篇

| 论文 | 量化类型 | 目标 | 核心贡献 | 压缩率 | 精度损失 |
|------|---------|------|---------|--------|---------|
| AuroOFT (2608.05253) | INT4/INT3 正交微调 | LLaMA-2, Qwen2 | Cayley变换增强旋转 | 4-5.3x | ~1-2% |
| QEvict (2608.05326) | INT4/INT8 KV Cache + 驱逐 | LLaMA-2/3 | 可恢复量化驱逐 | 8x | <0.05 PPL |
| BaKron (2608.06291) | INT4 权重量化 | LLaMA-2, Mistral | Kronecker Hessian GPTQ | 4x | ~0.07 PPL |
| OAR (2608.02691) | INT2 KV Cache | LLaMA-2/3 | 输出感知旋转 | 16x | <0.4 PPL |
| Quantum PTQ (2608.05240) | 1-bit 理论 | 通用 | 量子叠加编码多模式 | 16x (理论) | 理论优势1.9x |

### 2.2 剪枝 (Pruning) — 2篇

| 论文 | 剪枝类型 | 目标 | 核心贡献 | 稀疏度 | 精度保持 |
|------|---------|------|---------|--------|---------|
| APQF (2608.05499) | 结构化 + 混合精度 | ResNet, BERT, LLaMA | Agent驱动协同优化 | 70-90% | ~98% |
| noise-prune (2608.05464) | 非结构化软剪枝 | RNN/LSTM | 噪声响应+重标定 | 80% | MSE降57% |

### 2.3 知识蒸馏 (Distillation) — 2篇

| 论文 | 蒸馏类型 | 目标 | 核心贡献 |
|------|---------|------|---------|
| OPSD (2608.06296) | 自策略自蒸馏 | GPT-2, LLaMA-2 | 完全无监督自一致性 |
| LiteKD-Net (2608.05739) | 特征+关系级蒸馏 | 移动去噪网络 | 参数量减90% PSNR降0.67dB |

### 2.4 其他压缩 (Other) — 1篇

| 论文 | 技术 | 目标 | 核心贡献 |
|------|------|------|---------|
| SkillZip (2608.05604) | 图压缩 | 智能体技能库 | 契约保持依赖图压缩4.2x |

---

## 三、量化论文综合评分

| arXiv ID | 论文标题 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 平均分 | 评价 |
|---------|---------|:-------:|:-------:|:-----:|:-------:|:------:|------|
| 2608.05253 | AuroOFT | 8 | 7 | 9 | 8 | **8.0** | 正交旋转参数化方法优雅，但旋转矩阵计算开销较大 |
| 2608.05326 | QEvict | 9 | 9 | 9 | 7 | **8.5** | 量化+驱逐协同首创，三层级存储设计实用 |
| 2608.06291 | BaKron | 8 | 7 | 8 | 7 | **7.5** | KFAC引入量化方向正确，但梯度收集增加开销 |
| 2608.02691 | OAR | 8 | 10 | 9 | 7 | **8.5** | 输出感知洞察深刻，INT2极限压缩有实用价值 |
| 2608.05240 | Quantum PTQ | 6 | 6 | 9 | 4 | **6.3** | 理论贡献重要但距离实际应用遥远 |

**评分标准** (1-10):
- **精度效果**: 压缩后模型精度保持程度
- **压缩倍率**: 压缩比与实用性
- **创新性**: 方法新颖程度和理论贡献
- **可复现性**: 代码开源、实验细节充分程度

---

## 四、整体分析

### 4.1 当日研究趋势

**趋势一：KV Cache 极端压缩成为热点**

QEvict 和 OAR 两篇论文同时关注 KV Cache 压缩，分别从不同角度（驱逐+量化协同、输出感知旋转）解决同一问题。这反映了大模型长上下文部署的迫切需求。

**趋势二：参数高效微调与量化结合**

AuroOFT 代表了"量化 + PEFT"的新方向：不是直接量化微调后的模型，而是在量化模型的基础上通过少量可训练参数进行适配。

**趋势三：理论研究与实用方法的并行**

既有 BaKron 这样基于二阶优化理论的深度方法，也有 APQF 这样面向实际部署的自动化框架，还有 Quantum PTQ 这样的前沿理论探索。

### 4.2 值得关注的方向

1. **KV Cache 压缩的实用化**：QEvict 的三层级存储和 OAR 的输出感知旋转都展示了向产品级推进的潜力
2. **Agent 驱动的自动化压缩**：APQF 展示了 LLM Agent 在模型优化中的自动化潜力
3. **量子-经典交叉**：虽然量子 PTQ 距离实用尚远，但其理论框架为理解量化极限提供了新视角

### 4.3 可复现代码

| 论文 | 代码位置 | 状态 |
|------|---------|------|
| AuroOFT | `scripts/quantization/2608.05253/` | ✅ Qwen3-0.6B上验证通过 |
| BaKron | `scripts/quantization/2608.06291/` | ✅ 核心算法可运行 |
| OAR | `scripts/quantization/2608.02691/` | ✅ 核心算法可运行 |

---

*报告生成时间: 2026-08-08*  
*分析人: AI Assistant (Auto-generated)*
