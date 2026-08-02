# ArXiv 量化与模型压缩领域论文日报

**目标日期**: 2026-08-02（周日）
**收集日期范围**: 2026-07-30 补充收录（8 月 2 日为周日，arXiv 无新论文发布）
**检索关键词**: quantization, quantize, low-bit, model compression, pruning, sparsity, knowledge distillation, KV cache compression, mixed precision, GPTQ, AWQ
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV, cs.AI)

---

## 日期说明

2026-08-02 为周日，arXiv 系统周末不发布新论文。经 arXiv API `submittedDate:[202608020000 TO 202608022359]` 检索确认当日零新增提交。arXiv API 最新可用论文截止于 2026-07-30T17:43:46Z。

本次日报补充收录 8 篇 2026-07-30 提交但在前日流水线中遗漏的模型压缩相关论文，确保覆盖完整。此前 2026-08-02 流水线已收录 4 篇同日论文（2607.28405 QuantWAMs、2607.28341 Trend-aware Pruning、2607.28449 Lightning OPD 2.0、2607.28627 ReToken），本次新增 8 篇，合计 2026-07-30 共 12 篇模型压缩相关论文。

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 | 分类 |
|:---:|----------|---------|------|:-------:|-----------|------|------|
| 1 | 2607.28589 | MixFrag: Fragility-Guided Mixed-Precision PTQ for Vision Transformers | Md. Mehrab Hossain Opi 等 | 07-30 | PTQ, Mixed-Precision, KL Divergence, MCKP, ViT | cs.CV, cs.LG | 量化 |
| 2 | 2607.28292 | CACHE-UK: A Stability-Aware Memory Editor for Sequentially Updated Quantized LLMs | Anubhav Lakra, Yue Feng | 07-30 | 4-bit Quantization, Memory Editing, LoRA, Stability | cs.CL, cs.AI, cs.LG | 量化 |
| 3 | 2607.28418 | WIDE: Boosting Adaptive LLM Inference via Token-level Dynamic Width Pruning | Haozhe Hu 等 | 07-30 | Dynamic Pruning, Width Pruning, Token-level, LLM | cs.AI, cs.CL, cs.LG | 剪枝 |
| 4 | 2607.28319 | Fairness Pruning: Locating Demographic Bias in GLU-MLP Layers | Pere Martra 等 | 07-30 | Structural Pruning, Bias Mitigation, GLU-MLP, LLM | cs.CL, cs.CY, cs.LG | 剪枝 |
| 5 | 2607.28263 | Understanding Is Done Early: Depth Division of Labor in LLMs (CoMem) | Hanzuo Liu 等 | 07-30 | KV Cache Compression, Layer-axis Memory, Self-distillation | cs.CL | 其他 |
| 6 | 2607.28069 | SemPIC: Learning Semantic Position-Independent KV Caches | Hui Xie 等 | 07-30 | KV Cache, Position-Independent, LoRA Writer, Distillation | cs.AI | 其他 |
| 7 | 2607.28196 | Fidelity Is Not Safety: Gently-Compressed LLMs Pass Quality Guards Yet Invent Steps | I. Kennedy, T. Kennedy | 07-30 | Compression Safety, Low-rank, SVD, Pruning, Agent | cs.CL | 其他 |
| 8 | 2607.28097 | From Expert Reduction to Behavioral Divergence in Sparse MoE | Tianyang Zhu | 07-30 | Sparse MoE, Expert Reduction, Numerical Precision | cs.LG | 其他 |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 2 篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| MixFrag (2607.28589) | 混合精度 PTQ | Vision Transformers (ViT) | KL 散度脆弱性度量 + MCKP 比特分配优化，COCO MP3/MP3 提升 9.6 AP |
| CACHE-UK (2607.28292) | 4-bit 量化 + 记忆编辑 | OpenLLaMA-3B (金融领域) | Rank-1 LoRA 扰动 + 稳定性控制器，4-bit 量化下知识退化降低 11-17% |

### 2.2 剪枝 (Pruning) — 2 篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| WIDE (2607.28418) | Token 级动态宽度剪枝 | LLMs (注意力头 + FFN 通道) | 首个端到端可微 token 级宽度剪枝，50% 稀疏度下性能提升 55.1%，decode 加速 4.95x |
| Fairness Pruning (2607.28319) | 结构化神经元剪枝 | Llama-3.2, Salamandra-2B | 差分激活定位偏差神经元，仅置零 40 个神经元 (<0.031%) 保持 99.49% 能力 |

### 2.3 其他 (Other) — 4 篇

| 论文 | 技术类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| CoMem (2607.28263) | KV cache 压缩 | Qwen3-8B | 层轴记忆组织，18.26 GB vs 89.36 GB，7.83x prefill 加速 |
| SemPIC (2607.28069) | KV cache 优化 | 多模型 | 语义位置无关 KV 缓存，micro-F1 从 0.53 提升至 0.60 |
| Fidelity Is Not Safety (2607.28196) | 压缩安全评估 | 三模型族 | 发现低秩压缩的安全盲区，提出相干性×速率双轴筛查 |
| Expert Reduction (2607.28097) | MoE 数值分析 | DeepSeek-V4-Flash | 专家归约顺序导致行为发散，建立数值兼容性契约 |

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
| 1 | 2607.28589 | MixFrag | 8 | 7 | 7 | 7 | **7.3** |
| 2 | 2607.28292 | CACHE-UK | 6 | 7 | 7 | 6 | **6.5** |
| 3 | 2607.28418 | WIDE | 8 | 9 | 8 | 9 | **8.5** |
| 4 | 2607.28319 | Fairness Pruning | 8 | 3 | 7 | 8 | **6.5** |
| 5 | 2607.28263 | CoMem | 9 | 9 | 8 | 7 | **8.3** |
| 6 | 2607.28069 | SemPIC | 7 | 7 | 7 | 6 | **6.8** |
| 7 | 2607.28196 | Fidelity Is Not Safety | 7 | 4 | 8 | 7 | **6.5** |
| 8 | 2607.28097 | Expert Reduction | 6 | 3 | 7 | 5 | **5.3** |

### 3.2 评分详细说明

#### 1. MixFrag (2607.28589)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 8/10 | ImageNet-1K 多架构竞争力性能，COCO MP3/MP3 设置下较先前最优提升 9.6 AP |
| 压缩倍率 | 7/10 | 混合精度 PTQ，比特预算约束下自适应分配，实际压缩比取决于预算设置 |
| 创新性 | 7/10 | KL 散度脆弱性度量 + MCKP 组合优化，方法组合新颖但各组件已有先例 |
| 可复现性 | 7/10 | 方法描述清晰，本流水线已用 Qwen3-0.6B 成功复现核心算法 |

#### 2. CACHE-UK (2607.28292)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 6/10 | 知识退化降低 11-17%，但绝对泛化率仅 28%，整体性能仍有限 |
| 压缩倍率 | 7/10 | 4-bit 量化部署，约 4x 权重压缩 |
| 创新性 | 7/10 | 首次系统研究量化 LLM 的记忆编辑稳定性问题，rank-1 LoRA 扰动机制设计巧妙 |
| 可复现性 | 6/10 | 系统复杂（三组件集成），领域特定（UK 金融），复现门槛较高 |

#### 3. WIDE (2607.28418)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 8/10 | 50% 稀疏度下较 SOTA 动态深度剪枝性能提升 55.1%，质量保持显著优于现有方法 |
| 压缩倍率 | 9/10 | prefill 加速 1.98x，decode 加速 4.95x，端到端分别 1.68x/1.55x |
| 创新性 | 8/10 | 首个端到端可微 token 级动态宽度剪枝框架，注意力头+FFN 通道神经元块级粒度 |
| 可复现性 | 9/10 | 代码已开源 (GitHub)，30 页 19 图方法描述详尽 |

#### 4. Fairness Pruning (2607.28319)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 8/10 | 置零 ≤40 个神经元保持 99.49% 推理和知识能力，干预极其精准 |
| 压缩倍率 | 3/10 | 非效率导向的剪枝（仅 0.031% MLP 宽度），不产生实质压缩比 |
| 创新性 | 7/10 | 差分激活定位偏差神经元的思路新颖，但发现双向偏差不稳定削弱了实用性 |
| 可复现性 | 8/10 | 代码和数据集公开，方法描述清晰 |

#### 5. CoMem (2607.28263)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 9/10 | RULER 97.05 vs 34.59，LoCoMo 38.27 vs 34.59，显著超越全上下文 KV-Direct |
| 压缩倍率 | 9/10 | 128k 上下文显存 18.26 GB vs 89.36 GB（79.6% 减少），prefill 加速 7.83x |
| 创新性 | 8/10 | "理解在前"的层轴分工发现，将长上下文记忆从 token 轴扩展到层轴 |
| 可复现性 | 7/10 | 基于 Qwen3-8B，方法清晰，但自蒸馏 LoRA 训练细节较多 |

#### 6. SemPIC (2607.28069)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 7/10 | micro-F1 从 0.53 提升至 0.60，逼近全量重计算 0.62，有提升但差距仍存 |
| 压缩倍率 | 7/10 | 位置无关缓存实现文档复用，减少重复 KV 计算 |
| 创新性 | 7/10 | LoRA Writer + 行为蒸馏的 Writer-Reader 分离架构设计合理 |
| 可复现性 | 6/10 | 方法描述较完整但未提及代码开源，KV Gradient Checkpointing 实现细节有限 |

#### 7. Fidelity Is Not Safety (2607.28196)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 7/10 | 发现并表征了压缩模型质量评估的关键盲区，但未提出修复方案 |
| 压缩倍率 | 4/10 | 研究压缩效果的安全评估，非压缩方法本身 |
| 创新性 | 8/10 | "相干性×速率"主控轴的发现和双轴无数据筛查工具设计新颖 |
| 可复现性 | 7/10 | 预注册 canary 实验，跨三架构复制验证，但实验设计复杂 |

#### 8. Expert Reduction (2607.28097)

| 维度 | 评分 | 依据 |
|------|:---:|------|
| 精度效果 | 6/10 | 分析型论文，无直接性能提升，但揭示了重要的数值精度问题 |
| 压缩倍率 | 3/10 | 非压缩方法，研究 MoE 推理中的数值稳定性 |
| 创新性 | 7/10 | 首次系统研究专家归约顺序对 MoE 行为的影响，数值兼容性契约概念有价值 |
| 可复现性 | 5/10 | 依赖 DeepSeek-V4-Flash 特定架构，32 页复杂实验设置，复现门槛高 |

---

## 四、整体分析

### 4.1 技术趋势

本日收录的 8 篇论文反映了模型压缩领域的几个重要趋势：

1. **混合精度量化走向自适应优化**：MixFrag 将比特分配形式化为多选择背包问题（MCKP），标志着混合精度 PTQ 从经验启发式向组合优化的转变。KL 散度脆弱性度量直接关联输出分布而非中间误差，更准确地反映了量化对最终性能的影响。这一思路可推广到 LLM 量化——用输出层面的分布差异指导比特分配，而非仅依赖权重或激活的统计量。

2. **量化模型的全生命周期管理**：CACHE-UK 首次揭示了"量化稳定性危机"——4-bit 量化模型在进行顺序记忆编辑时性能急剧退化。这提示量化不应被视为一次性部署操作，而需要考虑模型后续的动态更新需求。Rank-1 LoRA 扰动机制将编辑限制在低秩子空间内的思路，为量化模型的增量更新提供了新范式。

3. **动态剪枝走向 token 级粒度**：WIDE 将动态剪枝从层级别推进到 token 级别的注意力头组和 FFN 通道组粒度，实现了"每个 token 动态选择计算路径"的细粒度稀疏执行。其 pruning-kernel 协设计框架（掩码重排序 + 硬件无关块跳过 + 硬件相关块内跳过）解决了动态稀疏加速的工程落地问题，对 LLM 推理加速具有重要实践价值。

4. **压缩安全性成为独立研究方向**：Fidelity Is Not Safety 揭示了一个被忽视的盲区——通过所有质量guard的"温和压缩"模型在 agentic 执行中可能虚构操作步骤。更关键的是，这一效应是算子特异性的：低秩（SVD）截断会触发，而幅度剪枝不会。这表明不同压缩方式对模型行为的影响机制截然不同，压缩安全评估需要针对压缩类型定制。

5. **KV cache 压缩沿层轴突破**：CoMem 和 SemPIC 分别从不同角度推进了 KV cache 优化。CoMem 发现 Transformer 深度分工现象（浅中层做语义表示，上层做预测特化），利用中间层缓存实现 7.83x prefill 加速。SemPIC 通过 LoRA Writer 编译位置无关 KV 缓存，解决了前缀缓存无法利用文档复用的局限。

### 4.2 量化领域重点

本日两篇量化论文分别从不同角度推进了量化技术：

**MixFrag** 的核心贡献在于将脆弱性度量与组合优化相结合：
- KL 散度脆弱性直接衡量量化对输出分布的影响，比传统的 MSE 度量更贴近最终任务性能
- MCKP 建模将比特分配从启发式升级为有理论保证的组合优化，动态规划求解保证全局最优
- 在 COCO 检测/分割的 MP3/MP3 设置下提升 9.6 AP，验证了混合精度分配的有效性

**CACHE-UK** 的核心贡献在于揭示了量化模型动态维护的新问题：
- "量化稳定性危机"是一个此前未被研究的实际问题：4-bit 量化使记忆编辑性能急剧退化
- 三组件设计（rank-1 LoRA + 领域优先化 + 稳定性控制器）提供了完整的解决方案框架
- 退化债务跟踪机制将控制论思想引入量化模型的持续维护

### 4.3 代码复现说明

对两篇量化论文均进行了 Qwen3-0.6B 代码复现：

1. **MixFrag** (`scripts/quantization/2607.28589/`)：
   - `FragilityEstimator`：KL 散度脆弱性估计（全精度 vs 量化输出分布）
   - `MCKPSolver`：多选择背包问题动态规划求解
   - `MixedPrecisionQuantizer`：W4A4/W6A6/W8A8 混合精度量化
   - 验证结果：197 层完成分配（W4=61, W6=109, W8=27），加权平均 5.15 bit，内存压缩至 FP16 的 32.2%

2. **CACHE-UK** (`scripts/quantization/2607.28292/`)：
   - `FourBitQuantizer`：4-bit RTN per-channel 对称量化
   - `LoRAEditor`：rank-1 LoRA 扰动编辑（梯度 SVD rank-1 近似）
   - `StabilityController`：退化债务跟踪 + 三级控制（normal/reduce/rollback）
   - 验证结果：3 轮顺序编辑，控制器成功检测退化并触发 2 次回滚

---

## 五、推荐阅读优先级

| 优先级 | 论文 | 推荐理由 |
|:-----:|------|---------|
| ★★★ | WIDE (2607.28418) | 剪枝领域必读，token 级动态宽度剪枝+kernel 协设计，代码开源 |
| ★★★ | CoMem (2607.28263) | KV cache 压缩突破，层轴记忆组织实现 7.83x 加速 |
| ★★☆ | MixFrag (2607.28589) | 量化领域推荐，MCKP 比特分配框架可迁移至 LLM |
| ★★☆ | Fidelity Is Not Safety (2607.28196) | 压缩安全必读，揭示低秩压缩的 agentic 安全盲区 |
| ★★☆ | CACHE-UK (2607.28292) | 量化模型维护新视角，量化稳定性危机值得关注 |
| ★☆☆ | Fairness Pruning (2607.28319) | 偏差剪枝新思路，但非效率导向 |
| ★☆☆ | SemPIC (2607.28069) | KV cache 优化方案，Writer-Reader 架构有参考价值 |
| ★☆☆ | Expert Reduction (2607.28097) | MoE 数值分析，对 MoE 部署有参考意义 |
