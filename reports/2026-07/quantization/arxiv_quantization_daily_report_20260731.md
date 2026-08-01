# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-07-31 (当日 00:00–23:59 UTC)  
**检索关键词**: quantization, pruning, distillation, sparsity, efficient inference, kv cache, low-bit, mixed precision  
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV, cs.AI)

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 核心关键词 | 领域 |
|:---:|----------|---------|------|-----------|------|
| 1 | 2607.27275 | Flat Score, Amplified Failures: How the Error Budget Masks Damage in Quantized LLM Agents | Jiwon Jang 等 | PTQ, 4-bit, Agent, Error Budget | cs.LG |
| 2 | 2607.27581 | MUGEN: A Unified Framework for Efficient Motion Understanding and Generation | Zhankai Ye 等 | Codebook Quantization, Motion, Unified | cs.LG |
| 3 | 2607.27591 | Prox: Training-Free FFN Activation Sparsity via Approximate Intermediate-Channel Salience | Jinyi Liu 等 | Activation Sparsity, FFN, Training-Free | cs.LG |
| 4 | 2607.27536 | GyRot: Leveraging Hidden Synergy between Rotation and Fine-grained Group Quantization | Sangjin Kim 等 | INT4, Rotation, Group Quantization, Hardware | cs.LG |
| 5 | 2607.28191 | CACHE-UK: A Stability-Aware Memory Editor for Sequentially Updated Quantized LLMs | Anubhav Lakra 等 | 4-bit, Memory Editing, Finance, Sequential | cs.LG |
| 6 | 2607.28423 | MixFrag: Fragility-Guided Mixed-Precision PTQ for Vision Transformers | Md. Mehrab Hossain Opi 等 | Mixed-Precision, PTQ, ViT | cs.LG |
| 7 | 2607.27600 | Back from the Future: Key-Value Cache Management by Counter-Causal Surprise | Stephen Gould 等 | KV Cache, Eviction, Counter-Causal | cs.LG |
| 8 | 2607.28135 | Beyond Geometric Complementarity: Coherent Overlap in Sparse MoE Routing | Huiyuan Tian 等 | Sparse MoE, Routing, Geometric | cs.LG |
| 9 | 2607.28248 | Fairness Pruning: Locating Demographic Bias in GLU-MLP Layers | Pere Martra 等 | Pruning, Fairness, Bias, GLU-MLP | cs.LG |
| 10 | 2607.28306 | WIDE: Boosting Adaptive LLM Inference via Token-level Dynamic Width Pruning | Haozhe Hu 等 | Dynamic Pruning, Token-level, Width | cs.LG |
| 11 | 2607.28591 | Efficient LLMs with AMP: Attention Heads and MLP Pruning | Leandro Giusti Mugnaini 等 | Structured Pruning, Attention, MLP | cs.LG |
| 12 | 2607.27700 | Calibrate Before Reason: Robust Visual Token Reduction against Semantic Drift | Jiasheng Li 等 | Visual Token Pruning, VLM, Calibration | cs.CV |
| 13 | 2607.27952 | LAST: The Last Query Token Guides Visual Token Pruning | Feng Yang 等 | Token Pruning, Edge-Cloud, MLLM | cs.CV |
| 14 | 2607.28196 | Fidelity Is Not Safety: Gently-Compressed LLMs Pass Quality Guard Yet Invent Steps | I. Kennedy 等 | Pruning, Safety, Agentic Execution | cs.CL |
| 15 | 2607.27712 | Beyond the Best Teacher: Expanding and Compressing the Reasoning Solution Manifold | Songshuo Lu 等 | Distillation, Reasoning, Multi-Teacher | cs.LG |
| 16 | 2607.27953 | Flux-OPD: On-Policy Distillation with Evolving Contexts | Yuran Wang 等 | OPD, Evolving Contexts, Open-Ended | cs.LG |
| 17 | 2607.27966 | Contrastive Reinforced Policy Optimization via Privileged Self-Distillation | Xingjian Wu 等 | CRPO, OPSD, Contrastive | cs.LG |
| 18 | 2607.28428 | β-OPSD: Deriving with Policy Optimization, Training with Self-Distillation | Jiawei Xu 等 | β-OPSD, Mathematical Reasoning | cs.LG |
| 19 | 2607.27891 | Group-Reflective Self-Distillation for Agentic Reinforcement Learning | Binbin Zheng 等 | Group-Reflective, Self-Distillation, RL | cs.LG |
| 20 | 2607.28498 | VAD: Attributing Visual Evidence for Multimodal On-Policy Distillation | Kangning Zhang 等 | Multimodal OPD, Visual Attribution | cs.CV |
| 21 | 2607.28154 | OPLD: On-Policy Latent Distillation for Multimodal Reasoning | Shoutai Zhu 等 | Latent Distillation, Multimodal Reasoning | cs.CV |
| 22 | 2607.28269 | Theia: Large-Scale Multimodal Captioning for Data-Free Distillation | Simone Giano 等 | Data-Free Distillation, Multimodal | cs.CV |
| 23 | 2607.27937 | From Scoring to Acting: Outcome-Verified Comparative Self-Distillation | Xu Xia 等 | Comparative Distillation, LLM Agents | cs.CL |
| 24 | 2607.28048 | SKILL-KD: Contrastive Skill Distillation for LLM Agents | Qiming Shi 等 | Skill Distillation, Contrastive, Agents | cs.CL |
| 25 | 2607.28069 | SemPIC: Learning Semantic Position-Independent KV Caches | Hui Xie 等 | KV Cache, Position-Independent, LoRA | cs.CL |
| 26 | 2607.28336 | Correcting What You Cannot See: Credit Assignment for Perception Distillation | Feng Xiong 等 | Perception Distillation, Credit Assignment | cs.CV |
| 27 | 2607.28399 | Stage-Replay Divergence Follows the KV Cache | Alexander Boesgaard Lorup 等 | KV Cache, Precision, Transplantation | cs.LG |
| 28 | 2607.27532 | Recall Before You Rank: Similarity-Guided Top-K Reuse for Long-Context | Wenshuai Yao 等 | Top-K Sparse Attention, Long-Context | cs.LG |
| 29 | 2607.27735 | A Sparse Glimpse of the Whole: Train-Free Self-Speculative Decoding | Yuesong Liu 等 | Speculative Decoding, Sparse, Train-Free | cs.CL |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 6 篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Flat Score (2607.27275) | 4-bit PTQ | LLM Agents | 发现4-bit量化在Agent场景中误差被放大 |
| MUGEN (2607.27581) | Codebook Quantization | Motion-Language | 自适应长度运动编码，低解码成本 |
| Prox (2607.27591) | Activation Sparsity | LLM FFN | 训练无关FFN激活稀疏化，70%稀疏度 |
| GyRot (2607.27536) | INT4 Rotation+Group | LLaMA | 粗旋转+细分组协同，3.4x加速 |
| CACHE-UK (2607.28191) | 4-bit + Memory Edit | Finance LLM | 稳定性感知的量化模型记忆编辑 |
| MixFrag (2607.28423) | Mixed-Precision PTQ | ViT | 脆弱性引导的混合精度分配 |

### 2.2 剪枝 (Pruning) — 8 篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Fairness Pruning (2607.28248) | Structured | LLM GLU-MLP | 通过差分激活定位偏见神经元 |
| WIDE (2607.28306) | Dynamic Width | LLM | Token级动态宽度剪枝，端到端可微 |
| AMP (2607.28591) | Structured | LLaMA/Phi | 统一MHA和MLP结构化剪枝框架 |
| Calibrate Before Reason (2607.27700) | Visual Token | VLM | 训练无关视觉token削减94.4% |
| LAST (2607.27952) | Token Pruning | MLLM | 查询感知的边缘-云协作剪枝 |
| Fidelity Is Not Safety (2607.28196) | Magnitude | LLM Agents | 低秩压缩通过质量检查但不安全 |
| Back from Future (2607.27600) | KV Cache Eviction | LLM | 反因果注意力掩码的KV淘汰 |
| Sparse MoE (2607.28135) | Expert Routing | MoE LLM | 专家子空间重叠的新画像 |

### 2.3 知识蒸馏 (Distillation) — 12 篇

| 论文 | 蒸馏类型 | 应用场景 |
|------|---------|---------|
| Beyond Best Teacher (2607.27712) | Multi-Teacher Ensemble | 推理能力扩展 |
| Flux-OPD (2607.27953) | Evolving Context OPD | 开放式任务 |
| CRPO (2607.27966) | Contrastive OPSD | Agent推理 |
| β-OPSD (2607.28428) | β-Controlled OPSD | 数学推理 |
| Group-Reflective (2607.27891) | Self-Distillation | Agent RL |
| VAD (2607.28498) | Visual Attribution OPD | 多模态 |
| OPLD (2607.28154) | Latent Distillation | 多模态推理 |
| Theia (2607.28269) | Data-Free KD | 灾难管理 |
| From Scoring to Acting (2607.27937) | Comparative Self-Distill | LLM Agents |
| SKILL-KD (2607.28048) | Skill Distillation | LLM Agents |
| SemPIC (2607.28069) | LoRA Writer Distillation | KV Cache |
| Credit Assignment (2607.28336) | Perception Distillation | 多模态推理 |

### 2.4 KV Cache 优化 — 4 篇

| 论文 | 方法 | 核心贡献 |
|------|------|---------|
| Stage-Replay (2607.28399) | Precision Control | 固定前缀精度控制和双向移植 |
| Recall Before Rank (2607.27532) | Top-K Reuse | Query相似性复用历史检索决策 |
| Sparse Glimpse (2607.27735) | Sparse Speculative | 训练无关的稀疏推测解码 |
| SemPIC (2607.28069) | Position-Independent | 语义位置无关KV缓存 |

---

## 三、按应用领域分类

| 应用领域 | 论文数量 | 代表性论文 |
|---------|:-------:|-----------|
| **大语言模型 (LLM)** | 15 | GyRot, WIDE, AMP, Prox, CACHE-UK, β-OPSD |
| **计算机视觉 (CV)** | 6 | MixFrag, VAD, OPLD, Theia, Calibrate Before Reason, LAST |
| **多模态 (Multimodal)** | 4 | VAD, OPLD, Theia, Credit Assignment |
| **Agent/工具调用** | 5 | Flat Score, Group-Reflective, From Scoring to Acting, SKILL-KD, Fidelity |
| **边缘/嵌入式** | 2 | LAST, GyRot |
| **科学计算** | 1 | Sparse Glimpse |

---

## 四、值得关注的高亮点

1. **旋转+组量化的协同突破**: [2607.27536] GyRot 首次实现旋转与细粒度组量化的无缝协作，通过算法-硬件协同设计在 LLaMA 上达到 4-bit SOTA，3.4× 加速和 3.6× 能效提升。

2. **Agent 场景下的量化风险评估**: [2607.27275] 发现 4-bit PTQ 在标准指标上"无损"，但在多轮工具调用 Agent 中将失败模式放大最多 2.5 倍，提出"错误预算掩盖效应"。

3. **动态宽度剪枝**: [2607.28306] WIDE 实现首个端到端可微分的 token 级动态宽度剪枝，50% 稀疏度下 decode 阶段 4.95× 内核加速。

4. **KV Cache 反因果淘汰**: [2607.27600] 提出基于反因果注意力掩码的 KV Cache 淘汰策略——能被未来 token 准确预测的过去 token 是冗余的。

5. **公平性剪枝**: [2607.28248] 仅干预 <0.031% 的 GLU-MLP 宽度即可改变偏见响应，但会导致双向偏见失稳而非单向消除。

---

## 五、Quantization 论文评分

| 论文 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合 |
|------|:-------:|:-------:|:-----:|:-------:|:----:|
| GyRot (2607.27536) | 9 | 9 | 9 | 7 | **8.5** |
| Flat Score (2607.27275) | 7 | 6 | 8 | 8 | **7.3** |
| Prox (2607.27591) | 8 | 8 | 7 | 8 | **7.8** |
| MixFrag (2607.28423) | 8 | 7 | 8 | 7 | **7.5** |
| CACHE-UK (2607.28191) | 7 | 6 | 8 | 6 | **6.8** |
| MUGEN (2607.27581) | 7 | 7 | 7 | 6 | **6.8** |

**评分说明**:
- **精度效果**: 量化后模型在下游任务上的性能保持程度
- **压缩倍率**: 实际达到的压缩比例和硬件效率
- **创新性**: 方法的新颖性和理论贡献
- **可复现性**: 代码开源程度、实验细节完整性、第三方复现难度

---

## 六、整体分析

### 6.1 当日趋势

**量化与压缩的 Agent 化**: 当日多篇论文关注 LLM Agent 场景下的压缩问题（Flat Score、Fidelity Is Not Safety、SKILL-KD 等），表明随着 Agent 成为主流应用形态，模型压缩研究正在从"通用精度"转向"场景化可靠性"。

**蒸馏的范式转移**: 12 篇蒸馏论文中有 8 篇聚焦于 On-Policy Distillation (OPD) 及其变体，显示 OPD 正在取代传统离线蒸馏成为后训练优化的核心范式。

**硬件协同设计兴起**: GyRot 的算法-硬件协同设计、Prox 的稀疏化与量化兼容性设计，表明压缩研究正从纯算法优化转向"算法-系统"联合优化。

### 6.2 可复现性评估

- **高可复现**: GyRot（算法描述清晰）、Prox（训练无关）、Flat Score（评估框架公开）
- **中等可复现**: MixFrag（PTQ 流程标准）、WIDE（框架明确但需特定内核）
- **低可复现**: CACHE-UK（金融领域专有数据）、MUGEN（运动数据集特定）

### 6.3 推荐关注

**短期可跟进**:
1. GyRot 的旋转粒度与分组粒度最优配比实验
2. Prox 的稀疏度与量化位宽联合优化
3. Flat Score 的"错误预算"指标在其他 Agent 基准上的验证

**中长期方向**:
1. OPD + 量化 + 稀疏的三重压缩协同
2. KV Cache 压缩与注意力稀疏化的联合设计
3. 多模态模型的统一压缩框架

---

*报告生成时间: 2026-08-01*  
*报告人: AI Assistant (Auto-generated)*
