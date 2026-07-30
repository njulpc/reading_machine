# ArXiv 量化与模型压缩领域论文月报（2026 年 7 月）

**收集日期范围**: 2026-07-01 至 2026-07-29 UTC

**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, sparsity（单词查询 + 提交日期倒序分页 + 客户端过滤）

**数据来源**: arXiv.org API

**论文总数**: 317 篇

---

## 一、范围与方法

- **时间窗**：2026-07-01 00:00 至 2026-07-29 23:59 UTC 提交的新论文（cross-list 以首次提交日期为准）。
- **召回方式**：arXiv API 对复杂布尔查询持续返回 500，故采用 6 个技术关键词（quantization / pruning / knowledge distillation / model compression / sparsity / efficient inference）单词查询，按 submittedDate 倒序全量分页抓取后客户端过滤，关键词取并集去重。摘要级召回，可能漏掉标题/摘要不含上述词根的压缩论文。
- **范围界定**：只收录以**压缩/高效化**为目标的论文。排除三类边界论文：① 纯能力迁移的 on-policy / RL 策略蒸馏（约 30 篇，目标是行为对齐而非压缩）；② 纯 serving 系统优化（无量化/稀疏/蒸馏成分）；③ 压缩感知与图像编解码（compressed sensing / neural codec）。
- **分析深度**：全部 317 篇配有六段结构化技术分析（`papers/2026-07/<id>/tech_analysis.md`），其中 12 篇旗舰论文为人工深度覆写，其余为基于摘要的机器辅助分析（摘要级，未逐篇核对全文）。

---

## 二、月度总览统计

### 2.1 按技术标签分布（论文可有多标签）

| 技术方向 | 论文数 | 占比 |
|---------|:-----:|:---:|
| 知识蒸馏 (Distillation) | 127 | 40.1% |
| 量化 (Quantization) | 112 | 35.3% |
| 剪枝 (Pruning) | 81 | 25.6% |
| 稀疏 (Sparsity) | 36 | 11.4% |
| KV Cache 压缩 | 26 | 8.2% |
| Token/序列压缩 | 20 | 6.3% |
| 低秩分解 | 18 | 5.7% |
| 其他压缩 | 2 | 0.6% |
| 其他 | 1 | 0.3% |

### 2.2 按主标签分布（每篇归入唯一主类，优先级：量化 > KV cache > token 压缩 > 低秩 > 剪枝 > 稀疏 > 蒸馏）

| 主类 | 论文数 |
|------|:-----:|
| 量化 (Quantization) | 112 |
| KV Cache 压缩 | 18 |
| Token/序列压缩 | 18 |
| 低秩分解 | 10 |
| 剪枝 (Pruning) | 45 |
| 稀疏 (Sparsity) | 10 |
| 知识蒸馏 (Distillation) | 94 |
| 其他 | 10 |

### 2.3 按周分布

| 周 | 论文数 |
|---|:-----:|
| 07-01 ~ 07-05 | 55 |
| 07-06 ~ 07-12 | 78 |
| 07-13 ~ 07-19 | 77 |
| 07-20 ~ 07-26 | 63 |
| 07-27 ~ 07-29 | 44 |

07-06 ~ 07-19 两周为稳定高峰（77–78 篇/周）；07-27 ~ 07-29 仅 3 天即收录 44 篇，日均 14.7 篇为全月最高密度，与 ICML 2026 会期结束后的投稿潮一致。FP4 训练、注意力量化、KV cache 压缩三个主题的代表性论文集中在下半月。

---

## 三、量化方向专题（112 篇量化标签论文）

### 3.1 子主题分布

| 子主题 | 代表论文 | 要点 |
|-------|---------|------|
| FP4 端到端训练 | HiFloat4 (2607.26515)、StableFP4 (2607.24953)、FullStackFP4 (2607.04422)、FourTune (2607.05711) | FP4 从纯推理格式走向训练/微调全程格式；核心是层次化缩放与 rollout-training 误差对齐 |
| 注意力机制量化 | RotateAttention (2607.02584)、HiFA4 (2607.04302)、MXAttention (2607.24377)、AVQ-Attention (2607.12789) | P-Reordering/旋转等效化 + MX 格式成为本月共识路线 |
| KV cache 量化/压缩 | KVpop (2607.05061)、GSRQ (2607.01065)、DepthWeave-KV (2607.06523)、Lynx (2607.01831)、JoLT (2607.12550) | 从均匀预算走向 token/层自适应与流式渐进传输 |
| 二阶 PTQ 算法 | GPTQ-2D (2607.27042)、KronQ (2607.07964)、KroQuant (2607.21446) | Kronecker/双侧结构进入主流；复杂度与精度同时推进 |
| 极低比特（≤2 bit） | ExTernD (2607.13511)、Cross-Layer Error Compensation (2607.14630)、BiSCo (2607.02893)、Log_bQuant (2607.08643) | 扩展秩分解、跨层误差补偿让 1–2 bit 从不可用走向可用 |
| 混合精度与敏感度分配 | MXSens (2607.17733)、CONQuER (2607.25884)、C-PTQ (2607.21076) | 列/块级敏感度 + 硬件感知搜索取代均匀位宽 |
| MoE 量化 | MixQuant (2607.23047)、PagedWeight (2607.16184)、QUADS (2607.15810) | 专家级精度分配、运行时动态量化、RL rollout 稳定性 |
| 扩散模型量化 | KroQuant (2607.21446)、OrbitQuant (2607.02461)、RDQ (2607.10137) | 块变换/旋转基 + 数据无关码本，W4A4 甚至 W2A4 可用 |
| 全整数部署 | I-LW-DETR (2607.24981) | Softmax/GELU/LayerNorm 的整数近似，端到端 INT 推理 |
| 旋转/基学习 | GaugeQuant (2607.20757) | 训练中用对称性破缺项学习量化最优基，无需校准数据 |

### 3.2 本月量化复现代码（19 个 demo）

以下 19 篇提出可复现量化算法的论文配有独立可运行 demo（`scripts/quantization/<id>/`，含 README.md 与 demo.py）。验证方式统一为：**优先加载本地缓存的真实 Qwen/Qwen3-0.6B**，对其前若干层线性层/KV cache 实际执行量化并比较 logits 余弦或重建误差；模型不可用时 demo 自动退化为同维度的合成基准，保证任何环境可跑通。全部 19 个 demo 均已在本机实际运行通过。

| # | arXiv ID | 论文 | 核心验证点 |
|--:|----------|------|-----------|
| 1 | 2607.01065 | GSRQ: Gain-Shape Residual Quantization for Sub-1-bit KV Cache | 真实 K cache 增益-形状残差量化，重建余弦 1.0000 |
| 2 | 2607.01127 | $\text{Log}_\text{b}$Quant: Quantizing Language Models in Logarithmic Space | 对数底自适应量化 vs 均匀量化误差对比 |
| 3 | 2607.02584 | RotateAttention: RoPE-Aware Rotation and Range Rectification for INT4 Quantized Attention in Video Generation | RoPE 感知旋转后 INT4 注意力输出误差显著下降 |
| 4 | 2607.02893 | Variable Bit-width Quantization: Learning Per-Group Precision for "Bigger-but-Smaller" Language Models | 逐组可变位宽分配 vs 均匀位宽的等比特误差 |
| 5 | 2607.04302 | HiFA4: Training-Free 4-bit FlashAttention on Ascend HIF4 NPUs for LLM Inference | P-Reordering 行和 std=0（direct 0.0458） |
| 6 | 2607.04422 | Full-Stack FP4: Stable LLM Pretraining with Quantized Projections, Optimizers, and Attention | FP4 全栈（投影/优化器/注意力）缩放链误差验证 |
| 7 | 2607.05711 | FourTune: Towards Fully 4-Bit Efficient Post-Training for Diffusion Models | 扩散模型全 4bit 微调量化-反量化一致性 |
| 8 | 2607.07964 | KronQ: LLM Quantization via Kronecker-Factored Hessian | Kronecker 分解 Hessian 的 GPTQ 舍入误差下降 |
| 9 | 2607.08643 | BiSCo-LLM: Lookup-Free Binary Spherical Coding for Extreme Low-Bit Large Language Model Compression | 1bit/维球面二值编码，logits 余弦 0.9445（符合 1bit 预期） |
| 10 | 2607.10137 | RDQ: Residual Distribution Quantization for Large Language Models | 残差分布量化的分段码本误差验证 |
| 11 | 2607.12550 | A JoLT for the KV Cache: Near-Lossless KV Cache Compression via Joint Tucker and JL-Residual Allocation for LLMs | 真实 K cache Tucker+JL 残差压缩重建余弦 0.9972 |
| 12 | 2607.12789 | AVQ-Attention: Adaptive Vector-Quantized Attention | 注意力集中场景自适应码本细化优于均匀 VQ（0.053 vs 0.062） |
| 13 | 2607.13511 | ExTernD: Expanded-Rank Ternary Decomposition Ternary LLM PTQ with Accuracy Approaching Any Quantization Level | 三值扩展秩分解残差单调下降（any-ε 性质验证） |
| 14 | 2607.14630 | Cross-Layer Error Compensation and Finite-Sample Feature-Statistics Matching for Extreme Low-Bit Quantization of Large Language Models | 跨层补偿使 1.125bit logits 余弦 0.447→0.993 |
| 15 | 2607.23047 | MixQuant: Adaptive Mixed-Precision Quantization for Large Language Models | 敏感度感知混合精度优于均匀 INT4 的等比特误差 |
| 16 | 2607.24377 | MXAttention: Data-Free Optimal Scaling and Pre-Normalization Quantization for MXFP4 Attention | MXFP4 注意力无数据最优缩放 + 预归一化误差对比 |
| 17 | 2607.24953 | Stable FP4 Training via Transposition-Invariant Block Quantization | 转置不变块量化保持前向/反向缩放一致性 |
| 18 | 2607.26515 | HiFloat4 Format for End-To-End Reinforcement Learning Post-Training of Large Language Models | 层次化 FP4 缩放 + Rollout-ResQ 误差修正 |
| 19 | 2607.27042 | GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding | GPTQ-2D 与暴力 O(m⁴) Babai 逐元素一致（diff 7e-9） |

**未配 demo 的量化论文说明**：其余量化标签论文属于以下四类，不做算法 demo——① 硬件/芯片设计（FPGA/ASIC/NPU 加速器，无可复现算法）；② 实证研究与基准（实证结论型，无新算法）；③ 下游应用论文（量化作为工具使用）；④ 纯理论分析。这些论文仍全部收录于评分表与技术分析中。

---

## 四、全部论文四项评分表（317 篇）

评分维度（1–10）：**精度效果**（摘要报告的指标保持/提升幅度与证据充分度）、**压缩倍率**（位宽/稀疏度/压缩率激进程度）、**创新性**（方法新颖性）、**可复现性**（算法清晰度、代码可得性、硬件依赖；本地有已验证 demo 者 +1）。

**评分方式**：12 篇旗舰论文经人工深度分析后人工定分；其余论文由透明确定性启发式生成（主类基准分 + 摘要数字丰富度/极端位宽/方法词/代码链接/硬件依赖调整），分数用于横向粗排，不替代逐篇阅读。

| 排名 | arXiv ID | 论文标题 | 主类 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 总分 |
|:---:|---------|---------|------|:-------:|:-------:|:-----:|:-------:|:---:|
| 1 | 2607.26515 | HiFloat4 Format for End-To-End Reinforcement Learning Post-Training of Large Language Models | 量化 | 8 | 8 | 9 | 7 | **32** |
| 2 | 2607.02584 | RotateAttention: RoPE-Aware Rotation and Range Rectification for INT4 Quantized Attention in Video Generation | 量化 | 8 | 7 | 8 | 8 | **31** |
| 3 | 2607.04302 | HiFA4: Training-Free 4-bit FlashAttention on Ascend HIF4 NPUs for LLM Inference | 量化 | 8 | 8 | 8 | 7 | **31** |
| 4 | 2607.24953 | Stable FP4 Training via Transposition-Invariant Block Quantization | 量化 | 8 | 8 | 8 | 7 | **31** |
| 5 | 2607.27042 | GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding | 量化 | 7 | 7 | 9 | 8 | **31** |
| 6 | 2607.01065 | GSRQ: Gain-Shape Residual Quantization for Sub-1-bit KV Cache | 量化 | 7 | 8 | 7 | 8 | **30** |
| 7 | 2607.02893 | Variable Bit-width Quantization: Learning Per-Group Precision for "Bigger-but-Smaller" Language Models | 量化 | 8 | 8 | 8 | 6 | **30** |
| 8 | 2607.03328 | Beyond Post-Quantization: Native Hash Learning with a Dedicated HASH Token | 量化 | 6 | 8 | 8 | 8 | **30** |
| 9 | 2607.04422 | Full-Stack FP4: Stable LLM Pretraining with Quantized Projections, Optimizers, and Attention | 量化 | 8 | 8 | 8 | 6 | **30** |
| 10 | 2607.05061 | KVpop -- Key-Value Cache Compression with Predictive Online Pruning | KV | 7 | 8 | 7 | 8 | **30** |
| 11 | 2607.05711 | FourTune: Towards Fully 4-Bit Efficient Post-Training for Diffusion Models | 量化 | 7 | 7 | 8 | 8 | **30** |
| 12 | 2607.07964 | KronQ: LLM Quantization via Kronecker-Factored Hessian | 量化 | 8 | 7 | 8 | 7 | **30** |
| 13 | 2607.11359 | Efficient Tuning Before Low-Bit Post-Training Quantization for Stochastic Gradient Descent-optimized Models | 量化 | 6 | 8 | 8 | 8 | **30** |
| 14 | 2607.23193 | OmniScope: Modality-Decoupled Token Compression for Omnimodal Large Language Models | Token/序列压缩 | 7 | 8 | 7 | 8 | **30** |
| 15 | 2607.03652 | ELiTeFormer: An Efficient Transformer for FPGAs | 量化 | 8 | 8 | 7 | 6 | **29** |
| 16 | 2607.03784 | Rethinking Depth Pruning for Vision Transformers: A Heterogeneity-Aware Perspective | 剪枝 | 6 | 7 | 8 | 8 | **29** |
| 17 | 2607.06922 | Latency-Constrained DNN Architecture Learning for Edge Systems using Zerorized Batch Normalization | 量化 | 7 | 7 | 7 | 8 | **29** |
| 18 | 2607.07033 | AnchorPrune: Relevance-Anchored Contextual Expansion for Visual Token Pruning | Token/序列压缩 | 6 | 8 | 7 | 8 | **29** |
| 19 | 2607.10640 | Spectral Heat Flow for Conservative Token Condensation in Vision-Language Models | Token/序列压缩 | 6 | 8 | 7 | 8 | **29** |
| 20 | 2607.13511 | ExTernD: Expanded-Rank Ternary Decomposition Ternary LLM PTQ with Accuracy Approaching Any Quantization Level | 量化 | 6 | 8 | 8 | 7 | **29** |
| 21 | 2607.15563 | Are All Tokens Necessary for Visual Place Recognition? An Empirical Study of Token Reduction for Efficient Inference | Token/序列压缩 | 6 | 8 | 6 | 9 | **29** |
| 22 | 2607.20125 | HeadCast: Casting Attention Heads for Efficient Autoregressive Video Generation | KV | 6 | 8 | 7 | 8 | **29** |
| 23 | 2607.23047 | MixQuant: Adaptive Mixed-Precision Quantization for Large Language Models | 量化 | 7 | 7 | 7 | 8 | **29** |
| 24 | 2607.24377 | MXAttention: Data-Free Optimal Scaling and Pre-Normalization Quantization for MXFP4 Attention | 量化 | 7 | 7 | 8 | 7 | **29** |
| 25 | 2607.00780 | SpiralFovea: Input-Adaptive Foveated Tokenization as a Third Lever of Resource-Adaptive Inference | KV | 7 | 8 | 7 | 6 | **28** |
| 26 | 2607.02237 | When Token Compression Breaks: Structural Pruning vs. Token Reduction for Robust ViT Segmentation under High Compression | Token/序列压缩 | 6 | 8 | 5 | 9 | **28** |
| 27 | 2607.08643 | BiSCo-LLM: Lookup-Free Binary Spherical Coding for Extreme Low-Bit Large Language Model Compression | 量化 | 6 | 8 | 7 | 7 | **28** |
| 28 | 2607.08734 | The Illusion of Equivalency: Statistical Characterization of Quantization Effects in LLMs | 量化 | 6 | 8 | 7 | 7 | **28** |
| 29 | 2607.10086 | WaveNet-Style Guitar Amplifier Model Pruning for Real-Time iOS Deployment | 量化 | 6 | 7 | 7 | 8 | **28** |
| 30 | 2607.10137 | RDQ: Residual Distribution Quantization for Large Language Models | 量化 | 7 | 7 | 7 | 7 | **28** |
| 31 | 2607.11215 | Q-BridgeNet: A Quantization Network for Cross-Lingual Sign Language Translation | 量化 | 6 | 7 | 7 | 8 | **28** |
| 32 | 2607.13205 | Adaptive Filtering of the KV Cache: Diagnosing and Correcting Structural-Role Bias in LLM Inference | KV | 8 | 8 | 6 | 6 | **28** |
| 33 | 2607.14630 | Cross-Layer Error Compensation and Finite-Sample Feature-Statistics Matching for Extreme Low-Bit Quantization of Large Language Models | 量化 | 6 | 8 | 7 | 7 | **28** |
| 34 | 2607.15959 | Multibit Quantized Precoding for MU-mMIMO | 量化 | 6 | 8 | 8 | 6 | **28** |
| 35 | 2607.16973 | TurboVec: A Case Study in Cost-Efficient Private Retrieval for Enterprise RAG via Codebook-Oblivious Quantization | 量化 | 7 | 7 | 5 | 9 | **28** |
| 36 | 2607.19894 | Defense Against LLM Backdoors using Critical Neuron Isolation Pruning | 剪枝 | 7 | 6 | 6 | 9 | **28** |
| 37 | 2607.21075 | VibeVoice-ASR-BitNet Technical Report | 量化 | 6 | 8 | 8 | 6 | **28** |
| 38 | 2607.22038 | Sparse by Command: Task-Conditional Compute Skipping for Multi-Task Inference Accelerators | 量化 | 7 | 8 | 8 | 5 | **28** |
| 39 | 2607.23445 | Omni-Prune: Query-Aware Unified Token Pruning for Efficient Omnimodal Large Language Models | Token/序列压缩 | 7 | 8 | 7 | 6 | **28** |
| 40 | 2607.25669 | OmniDelta: Skill-Driven Budget Allocation for Token Compression in OmniLLMs | Token/序列压缩 | 7 | 8 | 7 | 6 | **28** |
| 41 | 2607.00712 | Towards Memory-Efficient Autoregressive Video Generation via Instance-Specific Parametric Absorption | KV | 6 | 8 | 7 | 6 | **27** |
| 42 | 2607.00760 | MosaicKV: Serving Long-Context LLM with Dynamic Two-D KV Cache Compression | KV | 7 | 8 | 6 | 6 | **27** |
| 43 | 2607.01127 | $\text{Log}_\text{b}$Quant: Quantizing Language Models in Logarithmic Space | 量化 | 6 | 7 | 7 | 7 | **27** |
| 44 | 2607.02484 | Combating Textual Noise and Redundancy: Entropy-Aware Dense Visual Token Pruning | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 45 | 2607.02612 | Fusion: A Framework for Unified Sequential Token AdaptatIon in VisiOn TraNsformers | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 46 | 2607.04079 | Seeing Once is Enough? Online Geometry-Aware Token Pruning for 3D Question Answering | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 47 | 2607.04244 | Quantize the Target, Quantize the Drafter: Efficient Inference with Qwen3.5-4B | 量化 | 6 | 7 | 6 | 8 | **27** |
| 48 | 2607.04605 | Do All Visual Tokens Matter Equally? Object-Evidence Preserving Token Merging for Vision-Language Retrieval | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 49 | 2607.05457 | Empirical Minimal-Realisation Compression of Deep Neural Networks via Controllability-Observability Tests | 量化 | 8 | 7 | 6 | 6 | **27** |
| 50 | 2607.06217 | EeveeDark: A Binary Neural Framework for Low-Light Video Enhancement via Event-Guided Sensor-Level Fusion | 量化 | 6 | 8 | 7 | 6 | **27** |
| 51 | 2607.06519 | FreqDepthKV: Frequency-Guided Depth Sharing for Robust KV Cache Compression in Long-Context LLM Inference | KV | 6 | 8 | 7 | 6 | **27** |
| 52 | 2607.06739 | Hardware-aware Graph Neural Networks prunning for embedded event-based vision | 量化 | 8 | 7 | 7 | 5 | **27** |
| 53 | 2607.06827 | Compress the Cache, Not the Speech Embedding: KV Compression for Efficient Speech LLMs | KV | 6 | 8 | 7 | 6 | **27** |
| 54 | 2607.08484 | Learning LDPC codes with quantized density evolution over relaxed protographs | 量化 | 6 | 8 | 7 | 6 | **27** |
| 55 | 2607.09385 | STEEL: Sparsity-Aware Fused Attention for Energy-Efficient Long-Sequence Inference on AMD's XDNA NPU | 稀疏 | 7 | 6 | 7 | 7 | **27** |
| 56 | 2607.10109 | Adaptive Model Compression (AMC): Saliency-Driven Resource Allocation for Ultra-Low-Power Transformer Inference | 量化 | 7 | 7 | 7 | 6 | **27** |
| 57 | 2607.10582 | MemDecay: Region-Aware KV Cache Eviction for Efficient LLM Agent Inference | KV | 6 | 8 | 7 | 6 | **27** |
| 58 | 2607.10784 | LSTrans: Efficient Knowledge Transfer for Lightweight and Automated ECG Classification | 低秩分解 | 6 | 6 | 6 | 9 | **27** |
| 59 | 2607.11317 | Calibrated e-CUSUM Decoding for Quantized Reasoning Models: Why Token Log-Probability Is the Wrong Observable for Decoding Monitors | 量化 | 7 | 7 | 7 | 6 | **27** |
| 60 | 2607.11473 | Towards Efficient Convolutional Neural Network for Embedded Hardware via Multi-Dimensional Pruning | 剪枝 | 6 | 6 | 7 | 8 | **27** |
| 61 | 2607.11942 | How Query Visibility Changes KV-Cache Compression Rankings: A Matched-Budget Audit | KV | 6 | 8 | 7 | 6 | **27** |
| 62 | 2607.12505 | Realizable N:M Sparse Transformer Inference via Search-Kernel Co-Design | 稀疏 | 6 | 6 | 7 | 8 | **27** |
| 63 | 2607.12550 | A JoLT for the KV Cache: Near-Lossless KV Cache Compression via Joint Tucker and JL-Residual Allocation for LLMs | 量化 | 7 | 7 | 6 | 7 | **27** |
| 64 | 2607.12789 | AVQ-Attention: Adaptive Vector-Quantized Attention | 量化 | 6 | 7 | 7 | 7 | **27** |
| 65 | 2607.13898 | Jack of All Scales: A Versatile FPGA Tensor Block for MXFP Precisions | 量化 | 6 | 7 | 7 | 7 | **27** |
| 66 | 2607.15498 | VarRate: Training-Free Variable-Rate KV Cache Compression for Long-Context LLMs | KV | 6 | 8 | 7 | 6 | **27** |
| 67 | 2607.16184 | PagedWeight: Efficient MoE LLM Serving with Dynamic Quality-Aware Weight Quantization | 量化 | 7 | 7 | 7 | 6 | **27** |
| 68 | 2607.16326 | CRISP: Pre-LLM Yet Text-Driven Visual Token Pruning for Efficient LVLM Inference | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 69 | 2607.16721 | Half the Experts, All the Code: One-Shot Domain Pruning of Mixture-of-Experts LLMs for Coding | 量化 | 6 | 8 | 6 | 7 | **27** |
| 70 | 2607.17486 | SALT: Salience-Aware Lexical Trie for Long-Context Compression | KV | 6 | 8 | 7 | 6 | **27** |
| 71 | 2607.17715 | C$^2$KV: Compressed and Composable KV Cache Reuse for Efficient LLM Inference | KV | 6 | 8 | 7 | 6 | **27** |
| 72 | 2607.20153 | Local Stability and Gaussian Smoothing of Quantized Neural Networks | 量化 | 6 | 8 | 6 | 7 | **27** |
| 73 | 2607.20357 | Look Less, Think Faster: Joint Token-Compute Adaptation for Multimodal LLMs | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 74 | 2607.20757 | GaugeQuant: Online Learning of Quantization-Optimal Bases from LLM Symmetries | 量化 | 6 | 7 | 6 | 8 | **27** |
| 75 | 2607.22389 | HiKV: Hierarchical Importance-Aware KV Cache with Hardware Acceleration for LLM Decoding | KV | 7 | 8 | 7 | 5 | **27** |
| 76 | 2607.22872 | Same Predictions, Different Reasons: The Effect of Quantization on Model Explanations | 量化 | 6 | 8 | 7 | 6 | **27** |
| 77 | 2607.23046 | Structured Redundancy Modeling for Efficient Visual Token Pruning in High-Resolution MLLMs | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 78 | 2607.23265 | WaveZip: Wavelet-Driven Space-Time Decoupling for Video Token Condensation | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 79 | 2607.23373 | UltraViT: Latency-Optimized On-device Vision Encoder for Large Vision-Language Models | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 80 | 2607.24192 | LLM-based Source Code Compression via Thresholded Symbol Ranking | 量化 | 7 | 7 | 6 | 7 | **27** |
| 81 | 2607.24331 | DynaCalKV: Key-Value Cache Compression via Head Grouping and Adaptive Rank Allocation | KV | 6 | 8 | 7 | 6 | **27** |
| 82 | 2607.25504 | At-the-Roofline Sparse Tensor Contractions on Vector Processors for Transformer Inference | 剪枝 | 6 | 6 | 7 | 8 | **27** |
| 83 | 2607.25583 | How Small Can You Go? A Controlled Study of LoRA Rank, Target Modules, and Quantization Trade-offs for Text-to-SQL on a 60M-Parameter Model | 量化 | 8 | 7 | 5 | 7 | **27** |
| 84 | 2607.25818 | SepPrune:A Separator-based Pruning Framework for Efficient Multimodal Large Language Models | Token/序列压缩 | 6 | 8 | 7 | 6 | **27** |
| 85 | 2607.26316 | Route-Block Membership Selects Packed-AWQ Arithmetic: A Controlled Single-Fixture Mechanism Study | 量化 | 6 | 8 | 7 | 6 | **27** |
| 86 | 2607.26648 | The Sparsity Ceiling: Where Spiking Networks Can and Cannot Trade Activity for Energy | KV | 7 | 8 | 6 | 6 | **27** |
| 87 | 2607.00382 | Vitality-Aware Compression for Efficient Image-to-Shape Diffusion Transformers | 量化 | 6 | 7 | 7 | 6 | **26** |
| 88 | 2607.00908 | Beyond Activation Alignment:The Alignment-Diversity Tradeoff in Task-Aware LLM Quantization | 量化 | 6 | 7 | 7 | 6 | **26** |
| 89 | 2607.01520 | The risk of KV cache compression | KV | 6 | 8 | 6 | 6 | **26** |
| 90 | 2607.01789 | EPnG: Adaptive Expert Prune-and-Grow for Parameter-Efficient MoE Fine-tuning | 剪枝 | 7 | 6 | 7 | 6 | **26** |
| 91 | 2607.01831 | Lynx: Progressive Speculative Quantization for accelerating KV Transfer in Long-Context Inference | 量化 | 6 | 7 | 7 | 6 | **26** |
| 92 | 2607.01928 | Sparse-Aware Vector Quantization for Bandwidth-Efficient Collaborative 3D Semantic Occupancy Prediction | 量化 | 6 | 7 | 7 | 6 | **26** |
| 93 | 2607.02461 | OrbitQuant: Data-Agnostic Quantization for Image and Video Diffusion Transformers | 量化 | 6 | 7 | 7 | 6 | **26** |
| 94 | 2607.02721 | Provable Pruning for Efficient 3D Gaussian Splatting via Coresets | 剪枝 | 6 | 6 | 6 | 8 | **26** |
| 95 | 2607.03803 | CineMobile: On-Device Image-to-Video Diffusion for Cinematic Camera Motion Generation | 量化 | 6 | 7 | 7 | 6 | **26** |
| 96 | 2607.04171 | Teaching Tiny VLA Models Where to Look and How to Move | 量化 | 6 | 7 | 7 | 6 | **26** |
| 97 | 2607.04371 | Nemotron-Labs-3-Puzzle-75B-A9B: Compressing Hybrid MoE LLMs | 量化 | 6 | 7 | 7 | 6 | **26** |
| 98 | 2607.04531 | Lyapunov-Guided Training for Hardware-Safe Neural Networks Under Fixed-Point Arithmetic | 量化 | 7 | 7 | 6 | 6 | **26** |
| 99 | 2607.05533 | Multi-Teacher Contrastive Distillation for Edge-Efficient Pathology Foundation Models | 知识蒸馏 | 8 | 3 | 7 | 8 | **26** |
| 100 | 2607.05734 | SCOReD: Student-Aware CoT Optimization for Recommendation Distillation | 剪枝 | 7 | 6 | 7 | 6 | **26** |
| 101 | 2607.06173 | MobileWan: Closing the Quality Gap for Mobile Video Diffusion | 剪枝 | 6 | 7 | 7 | 6 | **26** |
| 102 | 2607.06523 | DepthWeave-KV: Token-Adaptive Cross-Layer Residual Factorization for Long-Context KV Cache Compression | 量化 | 6 | 7 | 7 | 6 | **26** |
| 103 | 2607.06631 | Dynamic-in-Few-Step: Unifying Dynamic Computation and Few-Step Distillation for Efficient Video Generation | 稀疏 | 7 | 6 | 7 | 6 | **26** |
| 104 | 2607.07144 | Fractal KV-Cache Archives: Lossless Symbolic Storage with In-Place Retrieval for Long-Context LLM Inference | 量化 | 7 | 7 | 5 | 7 | **26** |
| 105 | 2607.09029 | MOSAIC: Adaptive Inter-layer Composition for Efficient Heterogeneous Vision-Language Models | 低秩分解 | 7 | 6 | 7 | 6 | **26** |
| 106 | 2607.09999 | Silent Failures in Quantized LLM Reasoning: A Taxonomy-Based Analysis of Hollow Convergence and Failure Mode Shifts | 量化 | 7 | 7 | 5 | 7 | **26** |
| 107 | 2607.10021 | A Symbolic Neural CPU for Quantization-Simulated Writeback and Interpretable Program Execution | 量化 | 6 | 7 | 6 | 7 | **26** |
| 108 | 2607.10611 | M+Adam: Low-Precision Training via Additive-Multiplicative Optimization | 量化 | 6 | 7 | 7 | 6 | **26** |
| 109 | 2607.11368 | Decomposing Runtime, Kernel, and Quantization Speedups via a Matched FP16 Intermediate: A Hardware-Conditioned Case Study on Four NVIDIA RTX A5000 GPUs | 量化 | 6 | 7 | 7 | 6 | **26** |
| 110 | 2607.11883 | Requential Coding: Pushing the Limits of Model Compression with Self-Generated Training Data | 量化 | 6 | 7 | 7 | 6 | **26** |
| 111 | 2607.11933 | Transforming LLMs into Efficient Cross-Encoders via Knowledge Distillation for RAG Reranking | 量化 | 7 | 7 | 5 | 7 | **26** |
| 112 | 2607.12266 | Saturation Makes Quantization Error Additive: A Coverage Model with a Certificate | 量化 | 6 | 7 | 7 | 6 | **26** |
| 113 | 2607.13735 | Constraint-Driven Model Optimization: An Industry Framework for Selecting Compression and Acceleration Techniques in Modern Machine Learning Systems | 量化 | 6 | 7 | 7 | 6 | **26** |
| 114 | 2607.14327 | PReM: Learning What to Preserve and When to Refresh for Context Compression | Token/序列压缩 | 6 | 8 | 6 | 6 | **26** |
| 115 | 2607.14618 | PolyQ: Codesigning End-to-End Quantization Framework for Scalable Edge CPU LLM Inference | 量化 | 6 | 7 | 7 | 6 | **26** |
| 116 | 2607.14622 | ExaGEMM: Exploration Framework for CPU-Driven ML Inference via Associative In-Register Computing for Low-Bit GEMM | 量化 | 6 | 7 | 7 | 6 | **26** |
| 117 | 2607.14834 | Lossy compression of weighted graph adjacency matrices by transform coding | 量化 | 6 | 7 | 7 | 6 | **26** |
| 118 | 2607.15328 | Lazy Arithmetic using Systolic Arrays for Closing the Verification Gap on Embedded Systems | 量化 | 6 | 7 | 7 | 6 | **26** |
| 119 | 2607.15421 | qZACH-ViT: Quantization-Aware Intrinsic Explanations with Recursive Attribution-Stabilized Optimization | 量化 | 6 | 7 | 7 | 6 | **26** |
| 120 | 2607.15810 | QUADS: Stabilizing NVFP4 Reinforcement Learning for MoE via QUantization-error Alignment across Dual Sides | 量化 | 6 | 7 | 7 | 6 | **26** |
| 121 | 2607.15846 | DSTAR: Accelerating Diffusion Transformers via Spatial and Temporal Redundancy Reduction | 量化 | 7 | 7 | 7 | 5 | **26** |
| 122 | 2607.15933 | Distributional Matching for Vector Quantization: A Unified Theoretical and Empirical Framework | 量化 | 6 | 7 | 7 | 6 | **26** |
| 123 | 2607.16316 | Eddy-VL 1.9B: Structural Pruning and Layered Distillation for Edge-Deployable Multimodal Embedding | 剪枝 | 7 | 6 | 7 | 6 | **26** |
| 124 | 2607.16339 | LaCache: Exact Caching and Precision-Adaptive Inference for Diffusion Large Language Models | 量化 | 6 | 7 | 7 | 6 | **26** |
| 125 | 2607.17733 | MXSens: Sensitivity-Aware Mixed-Precision Quantization for Efficient LLM Inference | 量化 | 6 | 7 | 7 | 6 | **26** |
| 126 | 2607.17913 | AutoEncoder-Compressed Parallel Split Learning for Pre-trained Model Fine-Tuning | 量化 | 6 | 7 | 7 | 6 | **26** |
| 127 | 2607.18081 | SelectInfer: Selective Neuron Loading and Computation for On-Device LLMs | 量化 | 6 | 7 | 7 | 6 | **26** |
| 128 | 2607.18540 | Recti-Q: Feature-Space Rectification for Out-of-Distribution-Robust Quantized Perception in Edge Robotics | 量化 | 6 | 7 | 7 | 6 | **26** |
| 129 | 2607.19431 | BRIM: Workload-Balanced Dual-Sided Bit-Serial Sparse Inference Accelerator | 量化 | 7 | 7 | 7 | 5 | **26** |
| 130 | 2607.19575 | VQ-Transplant: Efficient VQ-Module Integration for Pre-trained Visual Tokenizers | 量化 | 6 | 7 | 7 | 6 | **26** |
| 131 | 2607.20981 | Beyond Independent Optimization: Compression, MoE Routing, and Quantization Interactions in Multimodal Edge Intelligence | 量化 | 6 | 7 | 7 | 6 | **26** |
| 132 | 2607.21076 | C-PTQ: Fisher-weighted Channel-wise Sensitivity for Post-training Quantization of MLLMs | 量化 | 6 | 7 | 7 | 6 | **26** |
| 133 | 2607.21446 | KroQuant: Kronecker-Structured Block Transforms for Efficient Post-Training Quantization of Diffusion Transformers | 量化 | 6 | 7 | 7 | 6 | **26** |
| 134 | 2607.21475 | Error Certificates for KV-Cache Eviction via Randomized Design | KV | 6 | 8 | 5 | 7 | **26** |
| 135 | 2607.21591 | Inference-Time Scaling of Diffusion Models via Progressive Seed Pruning | 剪枝 | 6 | 6 | 6 | 8 | **26** |
| 136 | 2607.21692 | Learning What Matters: Supervising Global Context Pruning with Causal Evidence Sets | 剪枝 | 8 | 6 | 6 | 6 | **26** |
| 137 | 2607.22772 | Generative Video Compression with Adaptive Score Distillation | 量化 | 6 | 7 | 7 | 6 | **26** |
| 138 | 2607.24148 | A Motion-Aware Vector Quantization Framework with Centroid Reuse for Efficient VLA Inference | 量化 | 7 | 7 | 7 | 5 | **26** |
| 139 | 2607.25180 | Bekko Embedding: Parameter-Efficient Multilingual Retrieval with Ultra-Compact Encoders | 量化 | 6 | 7 | 7 | 6 | **26** |
| 140 | 2607.25487 | CoTinyVLA: Chain-of-Thought Distillation for a Sub-Billion-Parameter Vision-Language-Action Model | 知识蒸馏 | 8 | 3 | 6 | 9 | **26** |
| 141 | 2607.25527 | Argus-Unified: Towards A Compact and Economical Unified Model for Image Understanding and Generation | 量化 | 6 | 7 | 7 | 6 | **26** |
| 142 | 2607.25870 | VAD to the Bone: Ultra-Tiny Speech Activity Detection for Edge Deployment | 量化 | 6 | 7 | 7 | 6 | **26** |
| 143 | 2607.25884 | CONQuER: Hardware-Aware Mixed-Precision Quantisation with Online-Calibrated Surrogates | 量化 | 6 | 7 | 7 | 6 | **26** |
| 144 | 2607.00927 | Post-Training Pruning for Diffusion Transformers | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 145 | 2607.01478 | Boundary-Aware Quantization: Finite-Scale Decision Geometry of Neural Classifiers | 量化 | 6 | 7 | 5 | 7 | **25** |
| 146 | 2607.01607 | MxGLUT: A Reconfigurable LUT-Centric Broadcast Dataflow Accelerator for Mixed-Precision GEMM | 量化 | 6 | 7 | 7 | 5 | **25** |
| 147 | 2607.01710 | Generic Expert Coverage for Pruning SparseMixture-of-Experts Language Models | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 148 | 2607.03860 | A Unified Framework for Quantized and Continuous Strong Lottery Tickets | 量化 | 6 | 7 | 5 | 7 | **25** |
| 149 | 2607.04179 | CritiqueDriveVLM: From Verifier-Guided Reinforcement Learning to Latent Thought Distillation for Autonomous Driving | 知识蒸馏 | 7 | 3 | 6 | 9 | **25** |
| 150 | 2607.04306 | SAD-LoRA: Spectral Alignment for Low-Rank Knowledge Distillation | 低秩分解 | 6 | 6 | 7 | 6 | **25** |
| 151 | 2607.04599 | Displacement Preserving Relational Distillation for Robust Medical Segmentation | 知识蒸馏 | 7 | 3 | 7 | 8 | **25** |
| 152 | 2607.05116 | Communication-Aware Placement and Pruning for Efficient Mixture-of-Experts Inference | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 153 | 2607.05445 | BitFair: A 12nm Bit-Serial CNN Accelerator with Learnable Early Termination and Adaptive Bit Ordering for Ultra-Low-Power XR Vision | 量化 | 7 | 7 | 6 | 5 | **25** |
| 154 | 2607.06335 | Bridging Diffusion Pruning and Step Distillation with Teacher-Aligned Repair | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 155 | 2607.06841 | Tensor Train Diffusion: Leveraging Low-Rank Structures for High-Dimensional Score-Based Sampling | 低秩分解 | 6 | 6 | 7 | 6 | **25** |
| 156 | 2607.07557 | PALS: Percentile-Aware Layerwise Sparsity for LLM Pruning | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 157 | 2607.08015 | CRIMP: Compact & Reliable DNN Inference on In-Memory Processing via Crossbar-Aligned Compression and Non-ideality Adaptation | 量化 | 6 | 7 | 6 | 6 | **25** |
| 158 | 2607.08027 | Structured Pruning of Large Language Models via Power Transformation and Sign-Preserving Score Aggregation with Adaptive Feature Retention | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 159 | 2607.08029 | Rethinking Small VLM Quantization: From Component-Wise Analysis to Hardware-Aware Edge Deployment | 量化 | 6 | 7 | 6 | 6 | **25** |
| 160 | 2607.08150 | DeepPySR -- A Symbolic Regression Framework with Dynamic Pruning, Pareto Selection, and Hierarchical Composition for Real-World Scientific Discovery | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 161 | 2607.08241 | Closing the Null Space: Guidance-Aware Quantization for Classifier-Free Diffusion | 量化 | 6 | 7 | 6 | 6 | **25** |
| 162 | 2607.08601 | It Takes a MAESTRO To Prune Bad Experts | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 163 | 2607.08754 | SLORR: Simple and Efficient In-Training Low-Rank Regularization | 低秩分解 | 6 | 6 | 7 | 6 | **25** |
| 164 | 2607.08993 | StreamDQ: Near-Memory Weight DeQuantization in Custom HBM for Scalable AI Inference Acceleration | 量化 | 6 | 7 | 7 | 5 | **25** |
| 165 | 2607.09287 | Super-Tuning: From Activation-Aware Pruning to Sparse Fine-Tuning | 低秩分解 | 6 | 6 | 6 | 7 | **25** |
| 166 | 2607.10386 | Structured Thoughts For Improved Reasoning And Context Pruning | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 167 | 2607.10855 | Reliability Scaling Laws for Quantized Large Language Models | 量化 | 6 | 7 | 6 | 6 | **25** |
| 168 | 2607.11089 | OS-Pruner: Pruning Chains-of-Thought of Reasoning Models via Optimal Stopping | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 169 | 2607.11990 | Sparse Inter-Layer Dependencies of Transformer FFN Neurons | 稀疏 | 6 | 6 | 7 | 6 | **25** |
| 170 | 2607.12556 | CGRL: Concept-Guided Pruning and Representation Learning for Whole-Slide Image Classification | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 171 | 2607.12792 | Silent Alarm: A J-Space Protocol for Comparing Danger Recognition Across Models and Quantization Levels | 量化 | 6 | 7 | 5 | 7 | **25** |
| 172 | 2607.13124 | ShortOPD: Recovering Pruned LLMs with Short-to-Long On-Policy Distillation | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 173 | 2607.14181 | Quantize with Confidence? An Empirical Study of Quantization for Code Generation | 量化 | 6 | 7 | 5 | 7 | **25** |
| 174 | 2607.14557 | Seeing the End at Step Zero: Accelerating Diffusion MLLMs via MLP Sparsity-Aware Truncation | 稀疏 | 6 | 6 | 7 | 6 | **25** |
| 175 | 2607.14647 | D-cut: Adaptive Verification Depth Pruning for Batched Speculative Decoding | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 176 | 2607.14897 | Selectivity Drives Efficiency: Dataset Pruning for Visual Place Recognition | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 177 | 2607.16296 | Efficient EEG Seizure Detection Using INT8 Quantization, Channel Pruning, and Spiking Neural Networks | 量化 | 6 | 7 | 6 | 6 | **25** |
| 178 | 2607.16624 | SPARE-GS: Structural Parsimony and Resource Efficiency for 3D Gaussian Splatting | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 179 | 2607.16644 | DARA: Degradation-Aware Low-Rank Residual Adaptation with Original-to-Corrupted Distillation for Corruption-Robust Animal Re-Identification | 低秩分解 | 7 | 6 | 5 | 7 | **25** |
| 180 | 2607.16980 | Efficient Audio-Visual Event Recognition via Knowledge Distillation and Dynamic INT8 Quantization of a Hybrid Cross-Attention Network | 量化 | 6 | 7 | 6 | 6 | **25** |
| 181 | 2607.17019 | Regularize or Localize: When Training-Time KV-Cache Geometry Pays Under Quantization | 量化 | 6 | 7 | 5 | 7 | **25** |
| 182 | 2607.17052 | Searching for Task-Specific Vision Paths: Evolutionary Block Pruning Across Vision-Language Models | 剪枝 | 6 | 6 | 6 | 7 | **25** |
| 183 | 2607.17143 | EdgeCoInfer: Hierarchical Collaborative Inference for On-Device Multimodal Large Models | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 184 | 2607.17200 | Cross-Coordinate Correspondence Pruning for Image-to-Point Cloud Registration | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 185 | 2607.17329 | MIS-HCC: Hierarchical Channel Clustering for Efficient Medical Image Segmentation | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 186 | 2607.17568 | CoCurve: Cross-Module Co-Pruning Curvature for Training-Free Structured LLM Pruning | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 187 | 2607.17668 | Selectivity Matters: Source Node Influence Pruning for Unsupervised Graph Domain Adaptation | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 188 | 2607.18213 | SWE-Pruner Pro: The Coder LLM Already Knows What to Prune | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 189 | 2607.18662 | Staged Depth-Pruning Distillation of a Flow-Matching Text-to-Speech Teacher: A Compact Hindi Speech Synthesizer | 剪枝 | 6 | 6 | 6 | 7 | **25** |
| 190 | 2607.19962 | EvoThink: Evolving Thinking in Large Reasoning Models via Self-Pruning and Aha-Moment Preference Optimization | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 191 | 2607.20048 | Importance-Aware OBS Pruning for Diffusion Models | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 192 | 2607.20129 | CUSUM-Shaped Inference-Time Monitoring and Targeted Re-Decoding for Quantized Small Language Model Reasoning | 量化 | 6 | 7 | 6 | 6 | **25** |
| 193 | 2607.21063 | QuantiBias: Benchmarking Quantization-Induced Bias in LLMs | 量化 | 6 | 7 | 5 | 7 | **25** |
| 194 | 2607.21291 | Adaptive Depth Sparse Framework: Similarity-Driven Resource Allocation for Pre-Trained LLMs | 稀疏 | 6 | 6 | 7 | 6 | **25** |
| 195 | 2607.21366 | Hilbert Operator for Progressive Encoding (HOPE): A Mathematical Framework for Deconstructing Learned Representations in Deep Networks | 低秩分解 | 6 | 6 | 7 | 6 | **25** |
| 196 | 2607.21985 | Unified Static-Dynamic Pruning for Efficient LLM Inference | 剪枝 | 7 | 6 | 6 | 6 | **25** |
| 197 | 2607.22720 | CausalGate: Causal Importance Distillation for Transformer Module Pruning | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 198 | 2607.23015 | Mask2Shield: Strengthening LLM Safety against Neuron-Pruning Attacks | 剪枝 | 6 | 6 | 7 | 6 | **25** |
| 199 | 2607.23227 | INT8 Quantization Makes ARM Edge Inference Dispatch-Invariant | 量化 | 6 | 7 | 6 | 6 | **25** |
| 200 | 2607.23390 | When Can Depth Replace Precision? A Resource Theory of Quantized Neural Computation | 量化 | 6 | 7 | 6 | 6 | **25** |
| 201 | 2607.24027 | Sol-Attn: Accelerating Video Generation Inference via On-the-Fly Attention Sparsification | 稀疏 | 6 | 6 | 7 | 6 | **25** |
| 202 | 2607.24440 | Bigger or Cheaper? Scale and Quantization Effects on Uncertainty Signals in Vision-Language Models Under Image Degradation | 量化 | 6 | 7 | 6 | 6 | **25** |
| 203 | 2607.24981 | Enabling Fully Integer-Only Inference for Lightweight Detection Transformers | 量化 | 6 | 7 | 6 | 6 | **25** |
| 204 | 2607.25182 | TabRank: Chain-of-Thought Distillation for Table Re-Rankers | 知识蒸馏 | 7 | 3 | 6 | 9 | **25** |
| 205 | 2607.25451 | Bits and Memories: Measuring Verbatim Extraction Across LLM Quantization | 量化 | 6 | 7 | 5 | 7 | **25** |
| 206 | 2607.25947 | A Cost-Effective Multimodal LLM Reasoning Framework for Question Answering over Irregular Clinical Time Series | 稀疏 | 6 | 6 | 6 | 7 | **25** |
| 207 | 2607.01444 | On the Utility and Factual Reliability of Pruned Mixture-of-Experts Models in the Biomedical Domain | 剪枝 | 6 | 6 | 5 | 7 | **24** |
| 208 | 2607.03246 | Bridging the Semantic Gap in 6G: Tiny Language Models Under the Latency-Accuracy-Size Trilemma | 低秩分解 | 6 | 6 | 5 | 7 | **24** |
| 209 | 2607.03851 | ContiStain: Cross-Domain Relation-Preserving Distillation for Continual Multi-Domain Virtual IHC Staining | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 210 | 2607.04241 | Hierarchical Multi-to-Single-Modal Knowledge Distillation for Disruption Prediction in EAST | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 211 | 2607.04303 | AquaStereo: Enabling Underwater Stereo Matching via Depth-Conditioned Diffusion and Geometry Self-Distillation | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 212 | 2607.05891 | Few-Medoids: An Embarrassingly Simple Coreset Selection Method for Few-Shot Knowledge Distillation | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 213 | 2607.06611 | Audio Sentiment Analysis via Distillation and Cross-Modal Integration of Generated Multilingual Transcripts | 知识蒸馏 | 6 | 3 | 6 | 9 | **24** |
| 214 | 2607.07626 | Future Confidence Distillation in Large Language Models | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 215 | 2607.11257 | LaGuadia: Language-Guided Adaptive Distillation from Pathology Foundation Models | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 216 | 2607.13330 | Efficient Text-to-Audio Generation via Pruning | 剪枝 | 6 | 6 | 6 | 6 | **24** |
| 217 | 2607.13770 | Kaleido: Algorithm-Hardware Co-Design for Video Diffusion Transformers by Exploiting Latent Space Correlations | 稀疏 | 6 | 6 | 7 | 5 | **24** |
| 218 | 2607.14703 | Pretraining Multiple Instance Learning Networks with Multi-Teacher Distillation from Pathology Slide Foundation Models | 知识蒸馏 | 6 | 3 | 6 | 9 | **24** |
| 219 | 2607.16859 | Dataset Distillation by Influence Matching | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 220 | 2607.17070 | Bridging the Information Gap: Semantic Densification and Hindsight Distillation for Cold-Start Prediction | 知识蒸馏 | 8 | 3 | 7 | 6 | **24** |
| 221 | 2607.17247 | Distilled Reinforcement Learning for LLM Post-training | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 222 | 2607.17828 | When a Name Is Not a Name: A Benchmark Dataset and Distilled Reasoning for Culturally Entangled Bangla Homographs in Low-Resource LLMs | 知识蒸馏 | 6 | 3 | 6 | 9 | **24** |
| 223 | 2607.18342 | PRISM: Sensitivity-Aware PolynoMial PRuning for EffIcient Neural Network Encryption | 剪枝 | 6 | 6 | 6 | 6 | **24** |
| 224 | 2607.18802 | QScheduler: Adaptive Gradient Sampling for Zeroth-Order On-Device Training on INT8 NPUs | 量化 | 6 | 7 | 6 | 5 | **24** |
| 225 | 2607.19248 | A Flexible Sparsity-Aware FPGA Accelerator with Column-Wise Compression for Efficient CNN Inference | 剪枝 | 6 | 6 | 7 | 5 | **24** |
| 226 | 2607.19450 | REGEN: Replay-recycling for Expert-to-Generalist distillation with Offline Reinforcement Learning | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 227 | 2607.22790 | The Sparsity Tax: Weight Sparsity Trade-offs in Event-Driven SIMD and SIMT Neuromorphic Cores | 剪枝 | 6 | 6 | 6 | 6 | **24** |
| 228 | 2607.24013 | AptAvatar: Fast and Vivid Long-Form Audio-Driven Video Generation for Production-Ready Avatars | 知识蒸馏 | 6 | 3 | 7 | 8 | **24** |
| 229 | 2607.24555 | LOCKS: Page-Local Compact Key Summaries for Efficient Long-Context Decoding | 低秩分解 | 6 | 6 | 6 | 6 | **24** |
| 230 | 2607.24568 | Bit-Accurate FPGA Evaluation of Learned Feature Gating in a Fixed-Point Fourier-Feature Automatic Modulation Classifier | 量化 | 6 | 7 | 6 | 5 | **24** |
| 231 | 2607.27031 | Lottery Tickets Are Not Deployment Tickets | 剪枝 | 6 | 6 | 5 | 7 | **24** |
| 232 | 2607.01480 | Procedural Memory Distillation: Online Reflection for Self-Improving Language Models | 知识蒸馏 | 7 | 3 | 7 | 6 | **23** |
| 233 | 2607.06796 | Enhancing deep learning models for time series classification via knowledge distillation | 知识蒸馏 | 6 | 3 | 5 | 9 | **23** |
| 234 | 2607.06982 | EdgeCompress: Coupling Multidimensional Model Compression and Dynamic Inference for EdgeAI | 其他 | 6 | 4 | 6 | 7 | **23** |
| 235 | 2607.07635 | Unlearning to Protect: A Distilled Reinforcement Learning Framework with Privacy-Preserving Feature Unlearning and XAI for IoT Security | 知识蒸馏 | 7 | 3 | 6 | 7 | **23** |
| 236 | 2607.10647 | Knowledge Distillation for Automated AI Tutor Evaluation | 知识蒸馏 | 7 | 3 | 7 | 6 | **23** |
| 237 | 2607.12934 | Domain-Incremental Remote Sensing Change Detection via Difference-Guided Adaptation and Frequency-Decoupled Distillation | 知识蒸馏 | 7 | 3 | 7 | 6 | **23** |
| 238 | 2607.15450 | Prediction-Only Distillation in Linear and Logistic Regression | 知识蒸馏 | 6 | 4 | 6 | 7 | **23** |
| 239 | 2607.17025 | Federated Lightweight Intrusion Detection in Drone Swarms with Knowledge Distillation | 知识蒸馏 | 7 | 3 | 7 | 6 | **23** |
| 240 | 2607.22013 | Visual Saliency Steering Distillation for Multimodal Chain-of-Thought Reasoning | 知识蒸馏 | 6 | 3 | 6 | 8 | **23** |
| 241 | 2607.24611 | Test-Time Adaptation via Dual Distillation for Videos Under Severe Distribution Shifts | 知识蒸馏 | 7 | 3 | 7 | 6 | **23** |
| 242 | 2607.24841 | Neuromorphic Diffusion Language Models: Addressing Compute and Memory Bottlenecks via Sparsity and Block Denoising | 稀疏 | 6 | 6 | 6 | 5 | **23** |
| 243 | 2607.00289 | OnPoint: Offline-to-Online Multi-Level Distillation for Point-Supervised Online Temporal Action Localization | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 244 | 2607.00514 | Cross4D-JEPA: Dense Cross-modal Correspondence Distillation for 4D Point Cloud Representation Learning | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 245 | 2607.01851 | Geometric Foundation Model Distillation for Efficient Lunar 3D Reconstruction | 知识蒸馏 | 6 | 3 | 6 | 7 | **22** |
| 246 | 2607.01906 | SFKD: Spatial--Frequency Joint-Aware Heterogeneous Knowledge Distillation via Multi-Level Wavelet Spectral Interaction | 知识蒸馏 | 6 | 3 | 6 | 7 | **22** |
| 247 | 2607.02593 | Token-level Response-visual Attention Guidance for Multimodal LLMs Knowledge Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 248 | 2607.02966 | Distill Where the Student Goes: Teacher-Regularized RL for English-Evidence Cross-Lingual RAG | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 249 | 2607.03156 | DistillH-Mamba: A Hypergraph-Mamba-Based Knowledge Distillation Model for Efficient Impact Fall Detection | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 250 | 2607.03760 | GeoSAM-Lite: A Lightweight Foundation Model for Onboard Remote Sensing Segmentation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 251 | 2607.03960 | Reward Lightning: Fast Video Generation via Homologous Preference Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 252 | 2607.04619 | CARD: Cross-component Audio Representation Distillation for Encoder-Free Audio Captioning | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 253 | 2607.04809 | Context-Constrained Transfer Learning for Tabular Foundation Models via Data Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 254 | 2607.05339 | TREK: Distill to Explore, Reinforce to Refine | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 255 | 2607.05605 | Patch Knowledge Transfer for Efficient AI-Generated Image Quality Assessment | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 256 | 2607.05721 | SpanUQ: Span-Level Uncertainty Quantification for Large Language Model Generation | 知识蒸馏 | 6 | 3 | 6 | 7 | **22** |
| 257 | 2607.05750 | ArtisanCAD: An Industrial-Level CAD Agent with Expert-Grounded Knowledge Distillation | 知识蒸馏 | 6 | 3 | 6 | 7 | **22** |
| 258 | 2607.07292 | CarbonCLIP: Enhance Carbon Prediction from Satellite Imagery via Integrated Street-View Semantics and Temporal Context Training | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 259 | 2607.08161 | SQuaD-SQL: Efficient Text-to-SQL with Small Language Models via LLM-Guided Knowledge Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 260 | 2607.08771 | ZipDepth: Bringing Lightweight Zero-Shot Monocular Depth Anywhere, on Any Device | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 261 | 2607.09133 | IB-Flow: Information Bottleneck-Guided CFG Distillation for Few-Step Text-to-Image Generation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 262 | 2607.10087 | CVKD-UDA: Cross-View Knowledge Distillation for 3D Unsupervised Domain Adaptive Segmentation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 263 | 2607.10096 | Scaling and Stabilizing Large-Scale Embedding-Based Retrieval | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 264 | 2607.10406 | TVT-PAPD: Pathology-Aware Prototype Distillation for Self-Supervised Whole Slide Image Classification | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 265 | 2607.10565 | BucketKD: A Safety-Aware Bucket-Based Knowledge Distillation Framework for End-to-End Motion Planning | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 266 | 2607.10666 | Answer-Conditioned Chain-of-Thought Distillation for Few-Shot Industrial Vision with Small VLMs | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 267 | 2607.10762 | TOLiD: Bridging the Architecture Gap in Vision Foundation Model to LiDAR Pretraining via Token Lifting for Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 268 | 2607.10998 | Temporal Feature Distillation for Label-Efficient Precise Event Spotting in Sports Videos | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 269 | 2607.11557 | Single-Teacher View Augmentation: Enhancing Knowledge Distillation with Student-Guided Perturbations | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 270 | 2607.12297 | MobileSAM2: Lightweight Segment Anything for Spatial Intelligence | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 271 | 2607.12663 | MAGE: Color-Invariant and Spatial Knowledge Distillation for Gastric Neoplasm Classification | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 272 | 2607.13452 | Symbiosis-Inspired Knowledge Distillation for Incremental Object Detection | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 273 | 2607.14640 | TIDE: Trustworthy and Interpretable Battery Degradation Estimation with Contextual Learning and Symbolic Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 274 | 2607.15736 | Better Starts, Better Ends: Bootstrapped Iterative Self-Reasoning Distillation for Compressed Reasoning | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 275 | 2607.16678 | Pseudo-label distillation for discriminative anomalous sound detection | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 276 | 2607.18152 | jina-reranker-v3.5: An Efficient Listwise Reranker with Hybrid Attention and Self-Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 277 | 2607.18693 | Rationale-Guided Knowledge Distillation for Cross-Lingual Stance Detection | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 278 | 2607.18850 | OPD-IAD: From Language Judgment to Industrial Anomaly Detection via On-Policy Self-Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 279 | 2607.19426 | Making Single-Cell Data Distillation Auditable: Traceable Real-Cell Coresets via Discrete Min-Max Selection | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 280 | 2607.19956 | When Does Knowledge Distillation Hurt? Reliability-Aware Distillation for Low-Resource Language Summarization | 知识蒸馏 | 6 | 3 | 6 | 7 | **22** |
| 281 | 2607.20072 | Factor-Informed Uncertainty Distillation for Gaze Estimation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 282 | 2607.20918 | OPOD: On-Policy Omni Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 283 | 2607.21592 | Unified Video Dense Prediction from Disjoint Data | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 284 | 2607.23346 | SPRKD: Effective Knowledge Distillation for Deep Neural Networks via Saddle Region Approximation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 285 | 2607.24280 | From Proprietary to Open-Source: Bridging the Distribution Gap via Multi-Agent Protocol Distillation in Agentic Search | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 286 | 2607.24720 | The Physics of Multi-Turn Long-Horizon Planning: From Pre-training to Post-training via Single- and Multi-Teacher On-Policy Agentic Distillation | 知识蒸馏 | 6 | 3 | 6 | 7 | **22** |
| 287 | 2607.24731 | Rethinking Classifier-Free Guidance in On-Policy Diffusion Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 288 | 2607.25215 | Leveraging Semantic Maps for City-Scale Cross-View Localization | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 289 | 2607.25289 | AMRD: Adaptive Multi-Teacher Relational Distillation for Lightweight Speech Emotion Recognition | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 290 | 2607.25318 | Beyond Background Bias: Saliency-Driven Prototype Alignment for Dataset Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 291 | 2607.25554 | Distilling Temporal Search and Reasoning: Evolving LLMs for Future Prediction via Harness-Assisted Efficient Data Synthesis | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 292 | 2607.26004 | Parallel Decoding Distillation for Fast Image and Video Generation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 293 | 2607.26238 | Lightweight Image Classification of Raptor Species for Edge Devices: Rare-Species Dataset Expansion via Video Frame Extraction, Knowledge Distillation, and TensorRT Deployment | 知识蒸馏 | 7 | 3 | 6 | 6 | **22** |
| 294 | 2607.26722 | DREvo: Distilling Recalibrated Historical Experience for Harness Self-Evolution | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 295 | 2607.26763 | Long-Tailed 3D Point Cloud Dataset Distillation | 知识蒸馏 | 6 | 3 | 7 | 6 | **22** |
| 296 | 2607.01827 | C2E: Boosting Ego-Only 3D Object Detection via Multi-Teacher Contrastive Knowledge Distillation | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 297 | 2607.04432 | Covert Trait Propagation Is Representation Alignment: Mechanistic Evidence from Hidden-Channel Distillation | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 298 | 2607.08268 | Different Teachers, Different Capabilities: Sub-1B On-Device Distillation for Structured Text Enrichment | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 299 | 2607.09063 | EvoLP: Self-Evolving Latency Predictor for Model Compression in Real-Time Edge Systems | 其他 | 5 | 4 | 5 | 7 | **21** |
| 300 | 2607.11465 | Score-Only Distillation for Compact Dense Retrieval | 知识蒸馏 | 6 | 3 | 5 | 7 | **21** |
| 301 | 2607.11948 | Ontology-Amplified Distillation and Contextuality Auditing for Sovereign Enterprise Language Models: A Combined Proof-of-Mechanism and Negative-Results Method Study | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 302 | 2607.14709 | Gold-Guided Programmatic Distillation for Financial Reasoning over Hybrid Tables and Text | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 303 | 2607.15467 | ADS-C: Antidistillation Sampling for Classification | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 304 | 2607.15919 | On the Failure of Boundary-Seeking Distillation in Bottlenecked Generative Architectures | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 305 | 2607.17099 | DepthART: Scaling Foundation Monocular Depth to Tiny Models | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 306 | 2607.18773 | Privileged Lesion-Context Relational Distillation for Mask-Free Skin Lesion Classification | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 307 | 2607.25545 | OrthKD: Extracting Generalized Clinical Knowledge from Heterogeneous Teachers for Lightweight Deployment | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 308 | 2607.25788 | GeoMFD: Continual Drone-View Geo-Localization with Geometry-Aware Adapter and Margin-Field Distillation | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 309 | 2607.27054 | CoCaRS: Correlation Calibration-Based Redundancy Suppression for Heterogeneous Knowledge Distillation | 知识蒸馏 | 6 | 3 | 6 | 6 | **21** |
| 310 | 2607.10237 | CoSAG: Compact Semantic Anchor Gaussians via Training-Free Rate-Distortion Coding | 其他 | 5 | 4 | 6 | 5 | **20** |
| 311 | 2607.12656 | SpeedyGS: Content-Aware 3D Gaussian Splatting Compression via Two-Stage Optimization | 其他 | 5 | 4 | 6 | 5 | **20** |
| 312 | 2607.15456 | Looped Latent Attention: Cross-Loop KV Compression for Looped Transformers | 其他 | 5 | 4 | 6 | 5 | **20** |
| 313 | 2607.20538 | Codec-Gauge: Learning Compression-Friendly Gauges for Transformer KV Caches | 其他 | 5 | 4 | 6 | 5 | **20** |
| 314 | 2607.08057 | Towards Efficient Large Language Model Serving: A Survey on System-Aware KV Cache Optimization | 其他 | 5 | 4 | 4 | 6 | **19** |
| 315 | 2607.08991 | Sensitivity-Aware Thresholding and Token Routing for Activation Sparsification in Large Language Models | 其他 | 5 | 4 | 4 | 6 | **19** |
| 316 | 2607.22716 | Visual Token Compression Enhances Robustness of MLLMs | 其他 | 5 | 4 | 5 | 5 | **19** |
| 317 | 2607.26835 | A Low-Power Sparse Convolution Accelerator with Idle-First-Task-Assignment for Edge Vision | 其他 | 5 | 4 | 5 | 4 | **18** |

---

## 五、本月 Top 亮点

1. **[2607.26515] HiFloat4 Format for End-To-End Reinforcement Learning Post-Training of Large Language Models**：首次端到端 FP4 RL 后训练：三级层次化缩放格式 + Rollout-ResQ 稀疏残差修正 rollout-training 失配，BF16 差距从 4.9% 缩至 1.1%。FP4 训练从'能跑'走向'对齐'。
2. **[2607.27042] GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding**：把自适应舍入推广到双侧基矩阵（Kronecker 度量），利用反对角线独立性把朴素 O(m⁴) 降到 O(m³)，输出与精确算法逐元素一致。本月最优雅的理论结果。
3. **[2607.04422] Full-Stack FP4: Stable LLM Pretraining with Quantized Projections, Optimizers, and Attention**：FP4 全栈训练框架，系统梳理权重/激活/梯度全链路的缩放设计，是 FP4 训练三篇中的系统性代表。
4. **[2607.24953] Stable FP4 Training via Transposition-Invariant Block Quantization**：FP4 训练稳定性分析 + 稳定化配方，与 HiFloat4/FullStackFP4 共同构成本月'FP4 训练'小高潮。
5. **[2607.04302] HiFA4: Training-Free 4-bit FlashAttention on Ascend HIF4 NPUs for LLM Inference**：层次化 FP4 注意力 + P-Reordering：把 KV 通道按重要性重排使量化误差结构化，与 RotateAttention 的旋转路线相互印证。
6. **[2607.02584] RotateAttention: RoPE-Aware Rotation and Range Rectification for INT4 Quantized Attention in Video Generation**：对 Q/K 施加旋转使注意力输出对量化不变，注意力量化的'免费午餐'路线。
7. **[2607.07964] KronQ: LLM Quantization via Kronecker-Factored Hessian**：Kronecker 结构双侧变换 PTQ，把旋转类方法的变换矩阵压到可存储可计算的结构化形式。
8. **[2607.05061] KVpop -- Key-Value Cache Compression with Predictive Online Pruning**：按注意力动态驱逐/保留 KV 对的缓存量化，token 级自适应预算的代表。
9. **[2607.13511] ExTernD: Expanded-Rank Ternary Decomposition Ternary LLM PTQ with Accuracy Approaching Any Quantization Level**：扩展秩三值分解：满秩之后的分量持续修正误差，理论上任意逼近 bf16 精度，给出单调性证明。
10. **[2607.14630] Cross-Layer Error Compensation and Finite-Sample Feature-Statistics Matching for Extreme Low-Bit Quantization of Large Language Models**：把逐层 PTQ 误差累积写成递归 e_{l+1}=A_l e_l+q_l 并用前向差分补偿，1.125-bit 分组二值下大幅回血（本地验证 logits 余弦 0.447→0.993）。
11. **[2607.01831] Lynx: Progressive Speculative Quantization for accelerating KV Transfer in Long-Context Inference**：渐进投机 KV 传输：Anchor 流（高位）先到先解码、Residual 流（低位）并发补齐，把 KV 传输从'全到齐'变成'边传边算'。
12. **[2607.02461] OrbitQuant: Data-Agnostic Quantization for Image and Video Diffusion Transformers**：数据无关扩散量化：随机置换块 Hadamard 旋转把任意输入的坐标边际压到同一已知分布，单一 Lloyd-Max 码本通吃所有时间步/prompt，推到 W2A4。

---

## 六、月度趋势分析

1. **FP4 从推理格式升级为训练格式。** HiFloat4、StableFP4、FullStackFP4、FourTune 四篇同月出现，共同结论是：FP4 的敌人不是权重量化而是**训练-推理两侧的量化误差失配**，层次化/细粒度缩放 + 残差修正是通用解法。QUADS（MoE RL rollout）在强化学习场景得到同一结论——激活误差而非权重误差主导不稳定。

2. **注意力量化路线收敛。** RotateAttention（旋转等效）、HiFA4（P-Reordering + 层次化 FP4）、MXAttention（MX 格式）、AVQ-Attention（自适应码本）四篇共享同一思想：**先把注意力的数值结构变换到量化友好的基底，再量化**。单纯的逐 tensor RTN 注意力已无人使用。

3. **KV cache 压缩走向 token/层自适应与流式化。** KVpop（动态驱逐）、DepthWeave-KV（跨层共享基 + token 路由秩）、Lynx（位平面分流渐进传输）、JoLT（联合低秩-量化）、GSRQ（分组残差）——均匀预算彻底过时，'重要性在 token、层、位平面三个维度上都极不均匀'成为共识前提。

4. **残差范式贯穿极低比特量化。** Rollout-ResQ（HiFloat4）、Residual Activation Compensation（QUADS）、GSRQ、DepthWeave-KV、ExTernD 都把'主量化 + 低秩/稀疏残差修正'作为标准构件；Cross-Layer Error Compensation 进一步把残差思想提升到**跨层**维度（e_{l+1}=A_l e_l+q_l）。

5. **变换学习化、校准数据可有可无。** GaugeQuant 在训练中用 LogSumExp 对称性破缺项学习量化最优基（无需校准数据）；OrbitQuant 用随机旋转把输入分布归一化到已知边际（数据无关）；KroQuant 学习 Kronecker 结构块变换（参数少于逐通道缩放）。校准集依赖正在被系统性消除。

6. **量化与其他压缩手段的耦合研究增多。** LoRA 秩 × 量化位宽的受控研究（2607.25583）、PagedWeight 的 MoE 权重 × KV cache 内存权衡、CONQuER 的编译器层混合精度搜索——单一旋钮的优化让位于联合权衡。

7. **蒸馏主战场明显转向数据集蒸馏与生成模型。** 127 篇蒸馏标签论文中数据集蒸馏（图像/点云/图/时间序列）与扩散/自回归生成模型蒸馏占主导；经典 LLM _logits 蒸馏持续减少。剪枝方面，彩票假说的部署兼容性（2607.27031）与 SNN 稀疏上限（2607.26648）两篇理论警示值得注意。

---

## 七、范围与局限

- **召回局限**：关键词并集召回，摘要/标题不含检索词根的压缩论文会漏收；arXiv API 间歇性 500/429，已用分页重试缓解，但不排除个别条目丢失。
- **分析深度**：305 篇为摘要级机器辅助分析，结论性表述以摘要为准，未核对全文与实验细节；12 篇旗舰论文经人工深度分析（含方法细节与实验数字）。
- **评分性质**：四项评分为横向粗排工具；启发式分数依赖摘要文本信号（数字丰富度、方法词、代码链接），对写作风格保守的论文可能系统性偏低。
- **复现范围**：19 个 demo 复现核心算法机制并在真实 Qwen3-0.6B 上验证方向性结论，不复现论文的完整 benchmark 数字与 kernel 级加速比。

---

## 附录 A：分类详表（按主类分组，含一句话结论）

### 量化 (Quantization)（112 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.26515 | 07-29 | HiFloat4 Format for End-To-End Reinforcement Learning Post-Training of Large Language Models | 本文首次实现端到端 FP4 的 LLM 强化学习后训练（rollout 与训练策略的前向、反向全部 4-bit），发现性能退化的主因不是训练侧量化误差而是 rollout 激活量化中的异常值下溢，提出 Rollout 残… | 32 |
| 2607.02584 | 07-01 | RotateAttention: RoPE-Aware Rotation and Range Rectification for INT4 Quantized Attention in Video Generation | 本文发现 3D RoPE 的维度划分强烈影响 Q/K 的异常值分布，提出 RotateAttention——面向 3D RoPE 视频 DiT 的混合精度 INT4 FlashAttention 框架：RoPE 感知旋转… | 31 |
| 2607.04302 | 07-05 | HiFA4: Training-Free 4-bit FlashAttention on Ascend HIF4 NPUs for LLM Inference | HiFA4 把 FlashAttention 的 QK^T 与 PV 两个 GEMM 都执行为 4-bit HIF4 Cube GEMM、softmax 在线状态保持 FP16，包含两个机制：Smooth-QK（RoPE… | 31 |
| 2607.24953 | 07-27 | Stable FP4 Training via Transposition-Invariant Block Quantization | 本文发现现有 1D 块微缩放量化中张量转置导致前向/反向对同一数值分配不同缩放因子，造成有偏且不稳定的梯度更新，提出基于 2D 块 FP4 量化的训练框架强制转置不变缩放，并结合无截断缩放、随机舍入与 Q/K 投影的 M… | 31 |
| 2607.27042 | 07-29 | GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding | 本文将 GPTQ 类自适应舍入从单边二次度量推广到左右两侧均有基矩阵作用的双边版本，提出 GPTQ-2D 算法，按反对角线逐条舍入、同一条反对角线上的元素相互独立可并行，将朴素 Kronecker 向量化实现的四次方复杂… | 31 |
| 2607.01065 | 07-01 | GSRQ: Gain-Shape Residual Quantization for Sub-1-bit KV Cache | 本文指出标准 ℓ₂ K-means 的欧氏质心平均在高维下会引发"质心收缩"，削弱 ℓ₂ 失真中的角度对齐项、损害方向保真，提出 Gain-Shape K-means（GSKM）作为 K-means 的即插替代，并以其加… | 30 |
| 2607.02893 | 07-03 | Variable Bit-width Quantization: Learning Per-Group Precision for "Bigger-but-Smaller" Language Models | 本文提出 Variable Bit-width Quantization (VBQ)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 30 |
| 2607.03328 | 07-03 | Beyond Post-Quantization: Native Hash Learning with a Dedicated HASH Token | 本文提出 HashViT，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 30 |
| 2607.04422 | 07-05 | Full-Stack FP4: Stable LLM Pretraining with Quantized Projections, Optimizers, and Attention | 本文指出已有 NVFP4 预训练只覆盖线性层，优化器状态/运算与注意力仍是 4-bit 空白，提出 Full-Stack FP4：线性投影用 LoRA-SVD 轻量分解把线性层损失差距从 1.40% 压到 0.61%，优… | 30 |
| 2607.05711 | 07-07 | FourTune: Towards Fully 4-Bit Efficient Post-Training for Diffusion Models | FourTune 在标准 LoRA 架构上增加一个冻结的数值稳定分支（隔离量化敏感异常值）构成三分支混合管线，配合硬件高效的块级量化与定制融合 kernel 支持量化反向传播，在定制化、强化学习、蒸馏三类后训练任务上匹配… | 30 |
| 2607.07964 | 07-08 | KronQ: LLM Quantization via Kronecker-Factored Hessian | 本文指出 GPTQ 类二阶 PTQ 只用输入激活统计构造量化目标、隐含"所有输出通道同等重要"的假设，提出 KronQ 把梯度协方差纳入量化管线：在 Kronecker 分解 Hessian 近似下做双向不相干处理（输入… | 30 |
| 2607.11359 | 07-13 | Efficient Tuning Before Low-Bit Post-Training Quantization for Stochastic Gradient Descent-optimized Models | 本文提出 Efficient Tuning Before Quantization (ETBQ)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 30 |
| 2607.03652 | 07-04 | ELiTeFormer: An Efficient Transformer for FPGAs | 本文提出 ELiTeFormer (Efficient Linear Ternary Transformer)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 29 |
| 2607.06922 | 07-08 | Latency-Constrained DNN Architecture Learning for Edge Systems using Zerorized Batch Normalization | 本文提出 a latency-oriented neural network learning method to optimize models for high accuracy while fulfilling t… | 29 |
| 2607.13511 | 07-15 | ExTernD: Expanded-Rank Ternary Decomposition Ternary LLM PTQ with Accuracy Approaching Any Quantization Level | 本文提出 ExTernD (Expanded-rank Ternary Decomposition)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 29 |
| 2607.23047 | 07-25 | MixQuant: Adaptive Mixed-Precision Quantization for Large Language Models | 本文发现层的敏感度强依赖于其上游层的量化比特配置，提出 MixQuant——一个包裹任意基础量化器（AWQ/GPTQ）的自适应框架：对随机上游量化配置做失真边缘化得到预算无关的层评分、在分配器自己产生的方案上校准量化参数… | 29 |
| 2607.24377 | 07-27 | MXAttention: Data-Free Optimal Scaling and Pre-Normalization Quantization for MXFP4 Attention | MXAttention 通过通用最优缩放（UOS）从 E2M1 网格结构解析推导出与数据分布无关的最优缩放边界 Qmax=7.25，并用预归一化量化（PNQ）保持在线 softmax 的行归一化性质，在 Wan2.2 与… | 29 |
| 2607.08643 | 07-09 | BiSCo-LLM: Lookup-Free Binary Spherical Coding for Extreme Low-Bit Large Language Model Compression | Large language models (LLMs) are increasingly constrained by memory capacity, weight bandwidth, and checkpoint… | 28 |
| 2607.08734 | 07-09 | The Illusion of Equivalency: Statistical Characterization of Quantization Effects in LLMs | 本文提出 correctness agreement，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.10086 | 07-11 | WaveNet-Style Guitar Amplifier Model Pruning for Real-Time iOS Deployment | 本文提出 a sparse-enabled WaveNet inference engine for iOS that runs heavily pruned neural guitar amplifier models… | 28 |
| 2607.10137 | 07-11 | RDQ: Residual Distribution Quantization for Large Language Models | 本文提出 RDQ (Residual Distribution Quantization)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.11215 | 07-13 | Q-BridgeNet: A Quantization Network for Cross-Lingual Sign Language Translation | 本文提出 Q-BridgeNet，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.14630 | 07-16 | Cross-Layer Error Compensation and Finite-Sample Feature-Statistics Matching for Extreme Low-Bit Quantization of Large Language Models | Layer-wise post-training quantization of large language models minimizes each layer's reconstruction error in … | 28 |
| 2607.15959 | 07-17 | Multibit Quantized Precoding for MU-mMIMO | 本文提出 a novel multibit quantized precoding method for the downlink of multi-user massive MIMO systems with low-… | 28 |
| 2607.16973 | 07-18 | TurboVec: A Case Study in Cost-Efficient Private Retrieval for Enterprise RAG via Codebook-Oblivious Quantization | Retrieval-Augmented Generation (RAG) systems increasingly power enterprise LLM applications, yet the vector re… | 28 |
| 2607.21075 | 07-23 | VibeVoice-ASR-BitNet Technical Report | 本文提出 VibeVoice-ASR-BitNet，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.22038 | 07-24 | Sparse by Command: Task-Conditional Compute Skipping for Multi-Task Inference Accelerators | 本文提出 a HW/SW co-designed approach in which a lightweight gating network，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.01127 | 07-01 | $\text{Log}_\text{b}$Quant: Quantizing Language Models in Logarithmic Space | 本文提出 Log$_\text{b}$Quant，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.04244 | 07-05 | Quantize the Target, Quantize the Drafter: Efficient Inference with Qwen3.5-4B | This report describes our approach to the Efficient Qwen Competition, where the goal is to enable low-latency … | 27 |
| 2607.05457 | 07-05 | Empirical Minimal-Realisation Compression of Deep Neural Networks via Controllability-Observability Tests | Deep neural networks often contain substantial hidden-state redundancy, but most compression methods operate d… | 27 |
| 2607.06217 | 07-07 | EeveeDark: A Binary Neural Framework for Low-Light Video Enhancement via Event-Guided Sensor-Level Fusion | Enhancing videos under extreme low-light conditions remains challenging due to the difficulty of balancing res… | 27 |
| 2607.06739 | 07-07 | Hardware-aware Graph Neural Networks prunning for embedded event-based vision | 本文提出 an optimization strategy for Graph Convolutional Neural Networks models aimed at adapting their architect… | 27 |
| 2607.08484 | 07-09 | Learning LDPC codes with quantized density evolution over relaxed protographs | We consider the design of low-density parity-check (LDPC) codes for a given iterative decoder. | 27 |
| 2607.10109 | 07-11 | Adaptive Model Compression (AMC): Saliency-Driven Resource Allocation for Ultra-Low-Power Transformer Inference | 本文提出 Adaptive Model Compression (AMC)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.11317 | 07-13 | Calibrated e-CUSUM Decoding for Quantized Reasoning Models: Why Token Log-Probability Is the Wrong Observable for Decoding Monitors | 本文提出 a training-free decoding controller that combines (i) a degeneration-aware alarm score fusing token uncer… | 27 |
| 2607.12550 | 07-14 | A JoLT for the KV Cache: Near-Lossless KV Cache Compression via Joint Tucker and JL-Residual Allocation for LLMs | The key-value (KV) cache has become the dominant memory cost of transformer inference: it grows with batch siz… | 27 |
| 2607.12789 | 07-14 | AVQ-Attention: Adaptive Vector-Quantized Attention | 本文提出 Adaptive Vector-Quantized (AVQ) Attention，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.13898 | 07-15 | Jack of All Scales: A Versatile FPGA Tensor Block for MXFP Precisions | 本文提出 targeted modifications to the DSP block's internal tensor-mode architecture that enable native support fo… | 27 |
| 2607.16184 | 07-17 | PagedWeight: Efficient MoE LLM Serving with Dynamic Quality-Aware Weight Quantization | 本文提出 PagedWeight，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.16721 | 07-18 | Half the Experts, All the Code: One-Shot Domain Pruning of Mixture-of-Experts LLMs for Coding | The strongest open-weight coding models are mixture-of-experts (MoE) networks: most of their size comes from l… | 27 |
| 2607.20153 | 07-22 | Local Stability and Gaussian Smoothing of Quantized Neural Networks | We study Gaussian averaging as a smooth surrogate for quantized neural models. | 27 |
| 2607.20757 | 07-22 | GaugeQuant: Online Learning of Quantization-Optimal Bases from LLM Symmetries | Transformers are known to have internal continuous symmetries that leave outputs invariant, while modifying qu… | 27 |
| 2607.22872 | 07-24 | Same Predictions, Different Reasons: The Effect of Quantization on Model Explanations | Post-training quantization (PTQ) has become a practical solution for deploying deep learning models on resourc… | 27 |
| 2607.24192 | 07-27 | LLM-based Source Code Compression via Thresholded Symbol Ranking | 本文提出 LLM-based compressors deploying two novel symbol-ranking variants that bound predictions to the top-$T$ r… | 27 |
| 2607.25583 | 07-28 | How Small Can You Go? A Controlled Study of LoRA Rank, Target Modules, and Quantization Trade-offs for Text-to-SQL on a 60M-Parameter Model | Parameter-efficient fine-tuning (PEFT) and low-bit quantization are now standard tools for adapting language m… | 27 |
| 2607.26316 | 07-28 | Route-Block Membership Selects Packed-AWQ Arithmetic: A Controlled Single-Fixture Mechanism Study | Mixture-of-experts (MoE) inference first aligns routed tokens into padded expert blocks, then executes packed … | 27 |
| 2607.00382 | 07-01 | Vitality-Aware Compression for Efficient Image-to-Shape Diffusion Transformers | 本文提出 the first compression approach for image-to-shape Diffusion Transformers (DiTs) that substantially reduce… | 26 |
| 2607.00908 | 07-01 | Beyond Activation Alignment:The Alignment-Diversity Tradeoff in Task-Aware LLM Quantization | 本文提出 TASA (Task-Aware Sensitivity Analysis)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.01831 | 07-02 | Lynx: Progressive Speculative Quantization for accelerating KV Transfer in Long-Context Inference | 本文提出 Lynx，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.01928 | 07-02 | Sparse-Aware Vector Quantization for Bandwidth-Efficient Collaborative 3D Semantic Occupancy Prediction | 本文提出 a bandwidth-efficient collaborative Vector Quantization Semantic Occupancy Prediction (VQSOP) framework，面… | 26 |
| 2607.02461 | 07-02 | OrbitQuant: Data-Agnostic Quantization for Image and Video Diffusion Transformers | 本文提出 OrbitQuant，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.03803 | 07-04 | CineMobile: On-Device Image-to-Video Diffusion for Cinematic Camera Motion Generation | 本文提出 CineMobile to bridge the gap，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.04171 | 07-05 | Teaching Tiny VLA Models Where to Look and How to Move | 本文提出 XS-VLA，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.04371 | 07-05 | Nemotron-Labs-3-Puzzle-75B-A9B: Compressing Hybrid MoE LLMs | 本文提出 Nemotron-Labs-3-Puzzle-75B-A9B，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.04531 | 07-05 | Lyapunov-Guided Training for Hardware-Safe Neural Networks Under Fixed-Point Arithmetic | Low-precision neural networks are attractive for resource-constrained hardware, but fixed-point arithmetic int… | 26 |
| 2607.06523 | 07-07 | DepthWeave-KV: Token-Adaptive Cross-Layer Residual Factorization for Long-Context KV Cache Compression | 本文提出 DepthWeave-KV，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.07144 | 07-08 | Fractal KV-Cache Archives: Lossless Symbolic Storage with In-Place Retrieval for Long-Context LLM Inference | The key-value (KV) cache dominates the memory cost of long-context autoregressive inference, and a growing bod… | 26 |
| 2607.09999 | 07-10 | Silent Failures in Quantized LLM Reasoning: A Taxonomy-Based Analysis of Hollow Convergence and Failure Mode Shifts | We show that post-training quantization can silently alter how large language models reason even when task acc… | 26 |
| 2607.10021 | 07-10 | A Symbolic Neural CPU for Quantization-Simulated Writeback and Interpretable Program Execution | 本文提出 a trace-supervised symbolic neural CPU，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.10611 | 07-12 | M+Adam: Low-Precision Training via Additive-Multiplicative Optimization | 本文提出 M+Adam，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.11368 | 07-13 | Decomposing Runtime, Kernel, and Quantization Speedups via a Matched FP16 Intermediate: A Hardware-Conditioned Case Study on Four NVIDIA RTX A5000 GPUs | 本文提出 an attribution study on four NVIDIA RTX A5000 GPUs，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.11883 | 07-13 | Requential Coding: Pushing the Limits of Model Compression with Self-Generated Training Data | 本文提出 requential coding，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.11933 | 07-11 | Transforming LLMs into Efficient Cross-Encoders via Knowledge Distillation for RAG Reranking | Cross-encoders achieve high reranking accuracy in Retrieval-Augmented Generation (RAG) pipelines but impose qu… | 26 |
| 2607.12266 | 07-14 | Saturation Makes Quantization Error Additive: A Coverage Model with a Certificate | 本文提出 the coverage model $f(S)=c\bigl(1-\prod_{i\in S}(1-a_i)\bigr)$，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.13735 | 07-15 | Constraint-Driven Model Optimization: An Industry Framework for Selecting Compression and Acceleration Techniques in Modern Machine Learning Systems | The rapid deployment of machine learning systems across cloud, edge, and enterprise environments has brought m… | 26 |
| 2607.14618 | 07-16 | PolyQ: Codesigning End-to-End Quantization Framework for Scalable Edge CPU LLM Inference | 本文提出 PolyQ，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.14622 | 07-16 | ExaGEMM: Exploration Framework for CPU-Driven ML Inference via Associative In-Register Computing for Low-Bit GEMM | 本文提出 ExaGEMM，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.14834 | 07-16 | Lossy compression of weighted graph adjacency matrices by transform coding | 本文提出 a compression framework for weighted graphs in which the graph topology is transmitted losslessly and edg… | 26 |
| 2607.15328 | 07-16 | Lazy Arithmetic using Systolic Arrays for Closing the Verification Gap on Embedded Systems | 本文提出 a both wholly new approach to real-time，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.15421 | 07-16 | qZACH-ViT: Quantization-Aware Intrinsic Explanations with Recursive Attribution-Stabilized Optimization | 本文提出 qZACH-ViT，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.15810 | 07-17 | QUADS: Stabilizing NVFP4 Reinforcement Learning for MoE via QUantization-error Alignment across Dual Sides | 本文提出 QUantization-error Alignment across Dual Sides (QUADS)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.15846 | 07-17 | DSTAR: Accelerating Diffusion Transformers via Spatial and Temporal Redundancy Reduction | 本文提出 DSTAR，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.15933 | 07-17 | Distributional Matching for Vector Quantization: A Unified Theoretical and Empirical Framework | 本文提出 a distributional matching framework for vector quantization，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.16339 | 07-16 | LaCache: Exact Caching and Precision-Adaptive Inference for Diffusion Large Language Models | 本文提出 LaCache，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.17733 | 07-20 | MXSens: Sensitivity-Aware Mixed-Precision Quantization for Efficient LLM Inference | 本文提出 MXSens，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.17913 | 07-20 | AutoEncoder-Compressed Parallel Split Learning for Pre-trained Model Fine-Tuning | 本文提出 AE-PSL，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.18081 | 07-20 | SelectInfer: Selective Neuron Loading and Computation for On-Device LLMs | 本文提出 SelectInfer，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.18540 | 07-20 | Recti-Q: Feature-Space Rectification for Out-of-Distribution-Robust Quantized Perception in Edge Robotics | 本文提出 Recti-Q，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.19431 | 07-20 | BRIM: Workload-Balanced Dual-Sided Bit-Serial Sparse Inference Accelerator | 本文提出 BRIM，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.19575 | 07-21 | VQ-Transplant: Efficient VQ-Module Integration for Pre-trained Visual Tokenizers | 本文提出 {\bf VQ-Transplant}，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.20981 | 07-23 | Beyond Independent Optimization: Compression, MoE Routing, and Quantization Interactions in Multimodal Edge Intelligence | 本文提出 Temporal Routing Consistency as a diagnostic for video MoE models and highlight open research directions … | 26 |
| 2607.21076 | 07-23 | C-PTQ: Fisher-weighted Channel-wise Sensitivity for Post-training Quantization of MLLMs | 本文提出 C-PTQ，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.21446 | 07-23 | KroQuant: Kronecker-Structured Block Transforms for Efficient Post-Training Quantization of Diffusion Transformers | 本文提出 KroQuant，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.22772 | 07-24 | Generative Video Compression with Adaptive Score Distillation | 本文提出 our Generative Video Codec (GenVC)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.24148 | 07-27 | A Motion-Aware Vector Quantization Framework with Centroid Reuse for Efficient VLA Inference | 本文提出 VQVLA，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.25180 | 07-28 | Bekko Embedding: Parameter-Efficient Multilingual Retrieval with Ultra-Compact Encoders | 本文提出 Bekko Embedding: its smallest model，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.25527 | 07-28 | Argus-Unified: Towards A Compact and Economical Unified Model for Image Understanding and Generation | 本文提出 Argus-Unified，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.25870 | 07-28 | VAD to the Bone: Ultra-Tiny Speech Activity Detection for Edge Deployment | 本文提出 kiloVAD，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.25884 | 07-28 | CONQuER: Hardware-Aware Mixed-Precision Quantisation with Online-Calibrated Surrogates | 本文提出 CONQuER，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.01478 | 07-01 | Boundary-Aware Quantization: Finite-Scale Decision Geometry of Neural Classifiers | We measured quantization-induced decision-boundary changes using local logit-margin radii, first-order boundar… | 25 |
| 2607.01607 | 07-02 | MxGLUT: A Reconfigurable LUT-Centric Broadcast Dataflow Accelerator for Mixed-Precision GEMM | 本文提出 MxGLUT，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.03860 | 07-04 | A Unified Framework for Quantized and Continuous Strong Lottery Tickets | The Strong Lottery Ticket Hypothesis (SLTH) asserts that sufficiently overparameterized, randomly initialized … | 25 |
| 2607.05445 | 07-04 | BitFair: A 12nm Bit-Serial CNN Accelerator with Learnable Early Termination and Adaptive Bit Ordering for Ultra-Low-Power XR Vision | Extended Reality (XR) wearables require always-on perception within tight power envelopes of a few watts and m… | 25 |
| 2607.08015 | 07-09 | CRIMP: Compact & Reliable DNN Inference on In-Memory Processing via Crossbar-Aligned Compression and Non-ideality Adaptation | Crossbar-based In-Memory Processing (IMP) accelerators achieve high-speed, low-power computing for deep neural… | 25 |
| 2607.08029 | 07-09 | Rethinking Small VLM Quantization: From Component-Wise Analysis to Hardware-Aware Edge Deployment | The emergence of vision language models with fewer than 3 billion parameters has accelerated the implementatio… | 25 |
| 2607.08241 | 07-09 | Closing the Null Space: Guidance-Aware Quantization for Classifier-Free Diffusion | Deploying classifier-free guidance (CFG) diffusion models under real-world compute budgets requires quantizati… | 25 |
| 2607.08993 | 07-09 | StreamDQ: Near-Memory Weight DeQuantization in Custom HBM for Scalable AI Inference Acceleration | 本文提出 StreamDQ，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.10855 | 07-12 | Reliability Scaling Laws for Quantized Large Language Models | Quantization is a powerful strategy to build capable and resource-efficient large language models (LLMs) by re… | 25 |
| 2607.12792 | 07-14 | Silent Alarm: A J-Space Protocol for Comparing Danger Recognition Across Models and Quantization Levels | Jailbreak-robustness research typically evaluates safety through generated responses using an LLM-as-judge app… | 25 |
| 2607.14181 | 07-15 | Quantize with Confidence? An Empirical Study of Quantization for Code Generation | The growing adoption of local inference frameworks such as Ollama has made it increasingly common for develope… | 25 |
| 2607.16296 | 07-13 | Efficient EEG Seizure Detection Using INT8 Quantization, Channel Pruning, and Spiking Neural Networks | Continuous EEG monitoring for epilepsy is constrained by the limited power and memory budgets of wearable and … | 25 |
| 2607.16980 | 07-18 | Efficient Audio-Visual Event Recognition via Knowledge Distillation and Dynamic INT8 Quantization of a Hybrid Cross-Attention Network | Audio-visual event recognition (AVER) has achieved significant performance improvements through transformer-ba… | 25 |
| 2607.17019 | 07-19 | Regularize or Localize: When Training-Time KV-Cache Geometry Pays Under Quantization | We study whether \sigreg -- LeJEPA's anti-collapse objective -- can reshape representations during standard au… | 25 |
| 2607.20129 | 07-22 | CUSUM-Shaped Inference-Time Monitoring and Targeted Re-Decoding for Quantized Small Language Model Reasoning | 本文提出 MGT-B (Monitoring-Guided Test-time Backtracking)，面向量化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.21063 | 07-23 | QuantiBias: Benchmarking Quantization-Induced Bias in LLMs | Almost every large language model that reaches a broad audience is quantized: trained in full precision, then … | 25 |
| 2607.23227 | 07-25 | INT8 Quantization Makes ARM Edge Inference Dispatch-Invariant | On x86, kernel dispatch fragments the outputs of the same neural network into many equivalence classes across … | 25 |
| 2607.23390 | 07-25 | When Can Depth Replace Precision? A Resource Theory of Quantized Neural Computation | When can additional low-bit residual computation replace missing numerical precision for a fixed input-output … | 25 |
| 2607.24440 | 07-27 | Bigger or Cheaper? Scale and Quantization Effects on Uncertainty Signals in Vision-Language Models Under Image Degradation | Vision-language models (VLMs) deployed on consumer hardware must decide when to answer and when to defer, and … | 25 |
| 2607.24981 | 07-27 | Enabling Fully Integer-Only Inference for Lightweight Detection Transformers | Vision Transformer detectors now approach the accuracy of CNNs but remain difficult to deploy on NPUs and micr… | 25 |
| 2607.25451 | 07-28 | Bits and Memories: Measuring Verbatim Extraction Across LLM Quantization | Language models are almost always quantized before they are deployed, and a growing line of work asks whether … | 25 |
| 2607.18802 | 07-21 | QScheduler: Adaptive Gradient Sampling for Zeroth-Order On-Device Training on INT8 NPUs | Zeroth-Order (ZO) optimization enables On-Device Learning (ODL) on NPU-equipped microcontrollers by estimating… | 24 |
| 2607.24568 | 07-27 | Bit-Accurate FPGA Evaluation of Learned Feature Gating in a Fixed-Point Fourier-Feature Automatic Modulation Classifier | Learned feature reweighting can improve automatic modulation classification (AMC) in software, but the same op… | 24 |

### KV Cache 压缩（18 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.05061 | 07-06 | KVpop -- Key-Value Cache Compression with Predictive Online Pruning | KVpop 不依赖静态启发式或代理分数，而是直接用 keep-or-drop 决策的监督信号训练 KV 驱逐策略：评分器以新颖的"未来注意力"目标训练（无需构造稠密注意力图即可高效计算），并引入延迟记忆评分器（推迟若干步… | 30 |
| 2607.20125 | 07-22 | HeadCast: Casting Attention Heads for Efficient Autoregressive Video Generation | 本文提出 HeadCast，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 29 |
| 2607.00780 | 07-01 | SpiralFovea: Input-Adaptive Foveated Tokenization as a Third Lever of Resource-Adaptive Inference | 本文提出 SpiralFovea，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.13205 | 07-14 | Adaptive Filtering of the KV Cache: Diagnosing and Correcting Structural-Role Bias in LLM Inference | Attention-based KV cache eviction (H2O and its descendants) compresses the memory-constrained state of a long-… | 28 |
| 2607.00712 | 07-01 | Towards Memory-Efficient Autoregressive Video Generation via Instance-Specific Parametric Absorption | 本文提出 Instance-Specific Parametric Absorption (ISPA)，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.00760 | 07-01 | MosaicKV: Serving Long-Context LLM with Dynamic Two-D KV Cache Compression | Long-context LLM services now sustain prompts with hundreds of thousands to millions of tokens, making the key… | 27 |
| 2607.06519 | 07-07 | FreqDepthKV: Frequency-Guided Depth Sharing for Robust KV Cache Compression in Long-Context LLM Inference | 本文提出 FreqDepthKV，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.06827 | 07-07 | Compress the Cache, Not the Speech Embedding: KV Compression for Efficient Speech LLMs | 本文提出 SpeechKV，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.10582 | 07-12 | MemDecay: Region-Aware KV Cache Eviction for Efficient LLM Agent Inference | 本文提出 MemDecay，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.11942 | 07-11 | How Query Visibility Changes KV-Cache Compression Rankings: A Matched-Budget Audit | 本文提出 a matched-budget audit of six published compression methods against three trivial baselines on three open… | 27 |
| 2607.15498 | 07-16 | VarRate: Training-Free Variable-Rate KV Cache Compression for Long-Context LLMs | 本文提出 VarRate，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.17486 | 07-20 | SALT: Salience-Aware Lexical Trie for Long-Context Compression | 本文提出 SALT，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.17715 | 07-20 | C$^2$KV: Compressed and Composable KV Cache Reuse for Efficient LLM Inference | 本文提出 C$^2$KV，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.22389 | 07-24 | HiKV: Hierarchical Importance-Aware KV Cache with Hardware Acceleration for LLM Decoding | 本文提出 HiKV，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.24331 | 07-27 | DynaCalKV: Key-Value Cache Compression via Head Grouping and Adaptive Rank Allocation | 本文提出 an improved low-rank KV cache compression framework，面向KV 缓存压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.26648 | 07-29 | The Sparsity Ceiling: Where Spiking Networks Can and Cannot Trade Activity for Energy | Spiking neural networks (SNNs) are promoted as an energy-efficient substrate because sparse, event-driven acti… | 27 |
| 2607.01520 | 07-01 | The risk of KV cache compression | Transformer inference on long sequences is expensive because softmax attention repeatedly reads from a large K… | 26 |
| 2607.21475 | 07-23 | Error Certificates for KV-Cache Eviction via Randomized Design | Deterministic KV-cache eviction keeps the top-$k$ tokens under an importance score and deletes the rest. | 26 |

### Token/序列压缩（18 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.23193 | 07-25 | OmniScope: Modality-Decoupled Token Compression for Omnimodal Large Language Models | 本文提出 OmniScope，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 30 |
| 2607.07033 | 07-08 | AnchorPrune: Relevance-Anchored Contextual Expansion for Visual Token Pruning | 本文提出 AnchorPrune，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 29 |
| 2607.10640 | 07-12 | Spectral Heat Flow for Conservative Token Condensation in Vision-Language Models | 本文提出 SpecFlow，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 29 |
| 2607.15563 | 07-17 | Are All Tokens Necessary for Visual Place Recognition? An Empirical Study of Token Reduction for Efficient Inference | 本文提出 the first systematic benchmark of token reduction for efficient visual place recognition，面向剪枝场景解决模型存储/计算成… | 29 |
| 2607.02237 | 07-02 | When Token Compression Breaks: Structural Pruning vs. Token Reduction for Robust ViT Segmentation under High Compression | Vision Transformers (ViTs) are strong backbones for semantic segmentation, but their computational cost limits… | 28 |
| 2607.23445 | 07-26 | Omni-Prune: Query-Aware Unified Token Pruning for Efficient Omnimodal Large Language Models | 本文提出 Omni-Prune，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.25669 | 07-28 | OmniDelta: Skill-Driven Budget Allocation for Token Compression in OmniLLMs | 本文提出 OmniDelta，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.02484 | 07-02 | Combating Textual Noise and Redundancy: Entropy-Aware Dense Visual Token Pruning | 本文提出 Entropy-Aware Dense Pruning (EADP)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.02612 | 07-01 | Fusion: A Framework for Unified Sequential Token AdaptatIon in VisiOn TraNsformers | 本文提出 Fusion，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.04079 | 07-05 | Seeing Once is Enough? Online Geometry-Aware Token Pruning for 3D Question Answering | 本文提出 the first online token-pruning method that can be integrated seamlessly with current MLLM models for 3D q… | 27 |
| 2607.04605 | 07-06 | Do All Visual Tokens Matter Equally? Object-Evidence Preserving Token Merging for Vision-Language Retrieval | 本文提出 SaMer，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.16326 | 07-15 | CRISP: Pre-LLM Yet Text-Driven Visual Token Pruning for Efficient LVLM Inference | 本文提出 CRISP，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.20357 | 07-22 | Look Less, Think Faster: Joint Token-Compute Adaptation for Multimodal LLMs | 本文提出 SmartVL，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.23046 | 07-25 | Structured Redundancy Modeling for Efficient Visual Token Pruning in High-Resolution MLLMs | 本文提出 Single-Forward Pruner (SFPruner)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.23265 | 07-25 | WaveZip: Wavelet-Driven Space-Time Decoupling for Video Token Condensation | 本文提出 WaveZip，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.23373 | 07-25 | UltraViT: Latency-Optimized On-device Vision Encoder for Large Vision-Language Models | 本文提出 UltraViT，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.25818 | 07-28 | SepPrune:A Separator-based Pruning Framework for Efficient Multimodal Large Language Models | 本文提出 SepPrune，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.14327 | 07-15 | PReM: Learning What to Preserve and When to Refresh for Context Compression | Efficient long-context inference is not only about reducing memory cost, but also about keeping useful context… | 26 |

### 低秩分解（10 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.10784 | 07-12 | LSTrans: Efficient Knowledge Transfer for Lightweight and Automated ECG Classification | 本文提出 LSTrans，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.09029 | 07-10 | MOSAIC: Adaptive Inter-layer Composition for Efficient Heterogeneous Vision-Language Models | 本文提出 Multi-Objective Search for Adaptive Inter-layer Composition (MOSAIC)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.04306 | 07-05 | SAD-LoRA: Spectral Alignment for Low-Rank Knowledge Distillation | 本文提出 \textbf{SAD-LoRA} (\textbf{S}pectral \textbf{A}lignment \textbf{D}istillation)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权… | 25 |
| 2607.06841 | 07-07 | Tensor Train Diffusion: Leveraging Low-Rank Structures for High-Dimensional Score-Based Sampling | 本文提出 a novel and efficient solver for the underlying HJB equation based on the functional tensor train (FTT) f… | 25 |
| 2607.08754 | 07-09 | SLORR: Simple and Efficient In-Training Low-Rank Regularization | 本文提出 SLORR，面向稀疏化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.09287 | 07-10 | Super-Tuning: From Activation-Aware Pruning to Sparse Fine-Tuning | 本文提出 Super，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.16644 | 07-18 | DARA: Degradation-Aware Low-Rank Residual Adaptation with Original-to-Corrupted Distillation for Corruption-Robust Animal Re-Identification | Animal re-identification (Re-ID) relies on fine-grained identity cues that can be disrupted by blur, noise, co… | 25 |
| 2607.21366 | 07-23 | Hilbert Operator for Progressive Encoding (HOPE): A Mathematical Framework for Deconstructing Learned Representations in Deep Networks | 本文提出 Hilbert Operator for Progressive Encoding (HOPE)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.03246 | 07-03 | Bridging the Semantic Gap in 6G: Tiny Language Models Under the Latency-Accuracy-Size Trilemma | Sixth-generation (6G) wireless networks are expected to serve as AI-native infrastructure, transmitting meanin… | 24 |
| 2607.24555 | 07-27 | LOCKS: Page-Local Compact Key Summaries for Efficient Long-Context Decoding | Serving large language models at long context is bottlenecked by the key-value (KV) cache, which is read in fu… | 24 |

### 剪枝 (Pruning)（45 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.03784 | 07-04 | Rethinking Depth Pruning for Vision Transformers: A Heterogeneity-Aware Perspective | 本文提出 HetDPT，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 29 |
| 2607.19894 | 07-22 | Defense Against LLM Backdoors using Critical Neuron Isolation Pruning | 本文提出 DeCNIP (Defense with Critical Neuron Isolation Pruning)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 28 |
| 2607.11473 | 07-13 | Towards Efficient Convolutional Neural Network for Embedded Hardware via Multi-Dimensional Pruning | 本文提出 TECO，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.25504 | 07-28 | At-the-Roofline Sparse Tensor Contractions on Vector Processors for Transformer Inference | 本文提出 Ventaglio，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.01789 | 07-02 | EPnG: Adaptive Expert Prune-and-Grow for Parameter-Efficient MoE Fine-tuning | 本文提出 EPnG，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.02721 | 07-02 | Provable Pruning for Efficient 3D Gaussian Splatting via Coresets | 3D Gaussian Splatting (3DGS) enables high-quality real-time novel-view synthesis, but practical scenes often c… | 26 |
| 2607.05734 | 07-07 | SCOReD: Student-Aware CoT Optimization for Recommendation Distillation | 本文提出 Student-Aware CoT Optimization for Recommendation Distillation (SCOReD)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.06173 | 07-07 | MobileWan: Closing the Quality Gap for Mobile Video Diffusion | Recent advances in video diffusion have been driven by scaling transformer-based architectures to billions of … | 26 |
| 2607.16316 | 07-15 | Eddy-VL 1.9B: Structural Pruning and Layered Distillation for Edge-Deployable Multimodal Embedding | 本文提出 Eddy-VL 1.9B，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.21591 | 07-23 | Inference-Time Scaling of Diffusion Models via Progressive Seed Pruning | Diffusion and flow-matching models dominate conditional image generation, yet inference-time scaling for these… | 26 |
| 2607.21692 | 07-23 | Learning What Matters: Supervising Global Context Pruning with Causal Evidence Sets | Sparse attention prunes a long context to the blocks a model needs, and the usual selector is distilled from a… | 26 |
| 2607.00927 | 07-01 | Post-Training Pruning for Diffusion Transformers | 本文提出 DiT-Pruning，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.01710 | 07-02 | Generic Expert Coverage for Pruning SparseMixture-of-Experts Language Models | 本文提出 \textbf{Generic TB-Coverage}，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.05116 | 07-06 | Communication-Aware Placement and Pruning for Efficient Mixture-of-Experts Inference | 本文提出 CAP (Communication-Aware Assignment and Pruning)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.06335 | 07-07 | Bridging Diffusion Pruning and Step Distillation with Teacher-Aligned Repair | 本文提出 a short teacher-alignment repair stage as a bridge between pruning and step distillation，面向剪枝场景解决模型存储/计算成… | 25 |
| 2607.07557 | 07-08 | PALS: Percentile-Aware Layerwise Sparsity for LLM Pruning | 本文提出 PALS (Percentile-Aware Layerwise Sparsity)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.08027 | 07-09 | Structured Pruning of Large Language Models via Power Transformation and Sign-Preserving Score Aggregation with Adaptive Feature Retention | 本文提出 a unified approach combining power transformation for nonlinear distribution alignment，面向剪枝场景解决模型存储/计算成本与… | 25 |
| 2607.08150 | 07-09 | DeepPySR -- A Symbolic Regression Framework with Dynamic Pruning, Pareto Selection, and Hierarchical Composition for Real-World Scientific Discovery | 本文提出 DeepPySR，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.08601 | 07-09 | It Takes a MAESTRO To Prune Bad Experts | 本文提出 MAESTRO (Markov-chain Approximated Expert Sparsification via Transition-based ROuting)，面向剪枝场景解决模型存储/计算成本与… | 25 |
| 2607.10386 | 07-11 | Structured Thoughts For Improved Reasoning And Context Pruning | 本文提出 Structured Thoughts，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.11089 | 07-13 | OS-Pruner: Pruning Chains-of-Thought of Reasoning Models via Optimal Stopping | 本文提出 OS-Pruner，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.12556 | 07-14 | CGRL: Concept-Guided Pruning and Representation Learning for Whole-Slide Image Classification | 本文提出 Concept-Guided Pruning and Representation Learning (CGRL)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.13124 | 07-14 | ShortOPD: Recovering Pruned LLMs with Short-to-Long On-Policy Distillation | 本文提出 \textbf{\shortopd}，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.14647 | 07-16 | D-cut: Adaptive Verification Depth Pruning for Batched Speculative Decoding | 本文提出 D-Cut，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.14897 | 07-16 | Selectivity Drives Efficiency: Dataset Pruning for Visual Place Recognition | 本文提出 a place-wise dataset pruning framework tailored for VPR，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.16624 | 07-18 | SPARE-GS: Structural Parsimony and Resource Efficiency for 3D Gaussian Splatting | 本文提出 SPARE-GS，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.17052 | 07-19 | Searching for Task-Specific Vision Paths: Evolutionary Block Pruning Across Vision-Language Models | 本文提出 a source-balanced evolutionary search and compare it with independent ranking，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题… | 25 |
| 2607.17143 | 07-19 | EdgeCoInfer: Hierarchical Collaborative Inference for On-Device Multimodal Large Models | 本文提出 EdgeCoInfer，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.17200 | 07-19 | Cross-Coordinate Correspondence Pruning for Image-to-Point Cloud Registration | 本文提出 a novel Cross-Coordinate Correspondences Pruning (CCP) strategy to acquire sufficient inliers while ensur… | 25 |
| 2607.17329 | 07-19 | MIS-HCC: Hierarchical Channel Clustering for Efficient Medical Image Segmentation | 本文提出 a hierarchical clustering compression method for medical image segmentation models (MIS-HCC)，面向剪枝场景解决模型存储… | 25 |
| 2607.17568 | 07-20 | CoCurve: Cross-Module Co-Pruning Curvature for Training-Free Structured LLM Pruning | 本文提出 CoCurve (Cross-Module Co-Pruning Curvature)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.17668 | 07-20 | Selectivity Matters: Source Node Influence Pruning for Unsupervised Graph Domain Adaptation | 本文提出 Source Node Influence Pruning (SNIP)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.18213 | 07-20 | SWE-Pruner Pro: The Coder LLM Already Knows What to Prune | 本文提出 SWE-Pruner Pro，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.18662 | 07-19 | Staged Depth-Pruning Distillation of a Flow-Matching Text-to-Speech Teacher: A Compact Hindi Speech Synthesizer | 本文提出 a practical recipe for building a compact Hindi text-to-speech (TTS) model by distilling a large flow-mat… | 25 |
| 2607.19962 | 07-22 | EvoThink: Evolving Thinking in Large Reasoning Models via Self-Pruning and Aha-Moment Preference Optimization | 本文提出 EvoThink，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.20048 | 07-22 | Importance-Aware OBS Pruning for Diffusion Models | 本文提出 importance-aware pruning for diffusion models，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.21985 | 07-24 | Unified Static-Dynamic Pruning for Efficient LLM Inference | The increasing deployment of large language models (LLMs) has magnified the computational and memory bottlenec… | 25 |
| 2607.22720 | 07-21 | CausalGate: Causal Importance Distillation for Transformer Module Pruning | 本文提出 CausalGate，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.23015 | 07-25 | Mask2Shield: Strengthening LLM Safety against Neuron-Pruning Attacks | 本文提出 Mask2Shield (M2S)，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.01444 | 07-01 | On the Utility and Factual Reliability of Pruned Mixture-of-Experts Models in the Biomedical Domain | Mixture-of-Experts (MoE) models offer inference speedups via selective activation but impose substantial memor… | 24 |
| 2607.13330 | 07-14 | Efficient Text-to-Audio Generation via Pruning | Diffusion-based text-to-audio generative models such as AudioLDM achieve high perceptual quality and strong se… | 24 |
| 2607.18342 | 07-20 | PRISM: Sensitivity-Aware PolynoMial PRuning for EffIcient Neural Network Encryption | Structured pruning is essential for making neural network inference feasible under homomorphic encryption (HE)… | 24 |
| 2607.19248 | 07-21 | A Flexible Sparsity-Aware FPGA Accelerator with Column-Wise Compression for Efficient CNN Inference | 本文提出 a hardware-algorithm co-design framework，面向剪枝场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.22790 | 07-24 | The Sparsity Tax: Weight Sparsity Trade-offs in Event-Driven SIMD and SIMT Neuromorphic Cores | Event-driven neuromorphic inference exploits activation sparsity by updating neuron state only on spikes. | 24 |
| 2607.27031 | 07-29 | Lottery Tickets Are Not Deployment Tickets | Reports on how sparsification, compression, and lottery tickets change model behavior have been mixed in the p… | 24 |

### 稀疏 (Sparsity)（10 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.09385 | 07-10 | STEEL: Sparsity-Aware Fused Attention for Energy-Efficient Long-Sequence Inference on AMD's XDNA NPU | 本文提出 STEEL，面向稀疏化场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.12505 | 07-14 | Realizable N:M Sparse Transformer Inference via Search-Kernel Co-Design | 本文提出 a hardware-software co-design framework for N:M sparse ViT inference，面向稀疏化场景解决模型存储/计算成本与精度之间的权衡问题。 | 27 |
| 2607.06631 | 07-07 | Dynamic-in-Few-Step: Unifying Dynamic Computation and Few-Step Distillation for Efficient Video Generation | 本文提出 a novel post-training acceleration framework that exploits this redundancy by integrating dynamic structu… | 26 |
| 2607.11990 | 07-13 | Sparse Inter-Layer Dependencies of Transformer FFN Neurons | 本文提出 a training-free attribution method that estimates the relative influence of upstream neurons and attentio… | 25 |
| 2607.14557 | 07-16 | Seeing the End at Step Zero: Accelerating Diffusion MLLMs via MLP Sparsity-Aware Truncation | 本文提出 Seer，面向稀疏化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.21291 | 07-23 | Adaptive Depth Sparse Framework: Similarity-Driven Resource Allocation for Pre-Trained LLMs | 本文提出 an Adaptive Depth Sparse Framework (AdaDSF) that converts off-the-shelf pre-trained LLMs into depth-spars… | 25 |
| 2607.24027 | 07-27 | Sol-Attn: Accelerating Video Generation Inference via On-the-Fly Attention Sparsification | 本文提出 training-free Sol-Attn (Sparsifying online attention)，面向稀疏化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.25947 | 07-28 | A Cost-Effective Multimodal LLM Reasoning Framework for Question Answering over Irregular Clinical Time Series | 本文提出 ClinPRISM，面向稀疏化场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.13770 | 07-15 | Kaleido: Algorithm-Hardware Co-Design for Video Diffusion Transformers by Exploiting Latent Space Correlations | 本文提出 a lightweight channelwise reuse algorithm that skips redundant computations by reusing partial results wh… | 24 |
| 2607.24841 | 07-24 | Neuromorphic Diffusion Language Models: Addressing Compute and Memory Bottlenecks via Sparsity and Block Denoising | 本文提出 a token-level roofline-inspired model that captures the combined impact of block-parallel generation and … | 23 |

### 知识蒸馏 (Distillation)（94 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.05533 | 07-06 | Multi-Teacher Contrastive Distillation for Edge-Efficient Pathology Foundation Models | 本文提出 MuCoDi，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.25487 | 07-28 | CoTinyVLA: Chain-of-Thought Distillation for a Sub-Billion-Parameter Vision-Language-Action Model | 本文提出 CoTinyVLA，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 26 |
| 2607.04179 | 07-05 | CritiqueDriveVLM: From Verifier-Guided Reinforcement Learning to Latent Thought Distillation for Autonomous Driving | 本文提出 CritiqueDriveVLM，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.04599 | 07-06 | Displacement Preserving Relational Distillation for Robust Medical Segmentation | 本文提出 Displacement-Preserving Relational Distillation (DPRD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.25182 | 07-28 | TabRank: Chain-of-Thought Distillation for Table Re-Rankers | 本文提出 TabRank，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 25 |
| 2607.03851 | 07-04 | ContiStain: Cross-Domain Relation-Preserving Distillation for Continual Multi-Domain Virtual IHC Staining | 本文提出 ContiStain，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.04241 | 07-05 | Hierarchical Multi-to-Single-Modal Knowledge Distillation for Disruption Prediction in EAST | 本文提出 a hierarchical multi-to-single-modal knowledge distillation framework for disruption prediction on a sync… | 24 |
| 2607.04303 | 07-05 | AquaStereo: Enabling Underwater Stereo Matching via Depth-Conditioned Diffusion and Geometry Self-Distillation | 本文提出 $\textbf{AquaStereo}$，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.05891 | 07-07 | Few-Medoids: An Embarrassingly Simple Coreset Selection Method for Few-Shot Knowledge Distillation | 本文提出 extensive KD experiments on four datasets，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.06611 | 07-07 | Audio Sentiment Analysis via Distillation and Cross-Modal Integration of Generated Multilingual Transcripts | 本文提出 a multimodal solution that integrates audio and text information via cross-modal transformers，面向知识蒸馏场景解决模… | 24 |
| 2607.07626 | 07-08 | Future Confidence Distillation in Large Language Models | 本文提出 future confidence distillation，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.11257 | 07-13 | LaGuadia: Language-Guided Adaptive Distillation from Pathology Foundation Models | 本文提出 LaGuadia (Language-Guided Adaptive DistillAtion)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.14703 | 07-16 | Pretraining Multiple Instance Learning Networks with Multi-Teacher Distillation from Pathology Slide Foundation Models | 本文提出 a distillation-based pretraining framework for MIL，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.16859 | 07-18 | Dataset Distillation by Influence Matching | 本文提出 a fully differentiable，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.17070 | 07-19 | Bridging the Information Gap: Semantic Densification and Hindsight Distillation for Cold-Start Prediction | 本文提出 SemRaD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.17247 | 07-19 | Distilled Reinforcement Learning for LLM Post-training | 本文提出 Distilled Reinforcement Learning (Distilled RL)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.17828 | 07-20 | When a Name Is Not a Name: A Benchmark Dataset and Distilled Reasoning for Culturally Entangled Bangla Homographs in Low-Resource LLMs | 本文提出 Culturally Entangled Homograph (CEH) disambiguation and build a Bangla benchmark of 1,516 expert-verified… | 24 |
| 2607.19450 | 07-21 | REGEN: Replay-recycling for Expert-to-Generalist distillation with Offline Reinforcement Learning | 本文提出 REGEN: Replay-recycling for Expert-to-Generalist Distillation with Offline RL，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡… | 24 |
| 2607.24013 | 07-27 | AptAvatar: Fast and Vivid Long-Form Audio-Driven Video Generation for Production-Ready Avatars | 本文提出 AptAvatar，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 24 |
| 2607.01480 | 07-01 | Procedural Memory Distillation: Online Reflection for Self-Improving Language Models | 本文提出 Procedural Memory Distillation (PMD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 23 |
| 2607.06796 | 07-07 | Enhancing deep learning models for time series classification via knowledge distillation | Deep learning has achieved remarkable success in various domains including time series analysis, computer visi… | 23 |
| 2607.07635 | 07-08 | Unlearning to Protect: A Distilled Reinforcement Learning Framework with Privacy-Preserving Feature Unlearning and XAI for IoT Security | 本文提出 DiRLU，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 23 |
| 2607.10647 | 07-12 | Knowledge Distillation for Automated AI Tutor Evaluation | 本文提出 FATE (FLC AI Tutor Evaluator)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 23 |
| 2607.12934 | 07-14 | Domain-Incremental Remote Sensing Change Detection via Difference-Guided Adaptation and Frequency-Decoupled Distillation | 本文提出 DG-FDD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 23 |
| 2607.15450 | 07-16 | Prediction-Only Distillation in Linear and Logistic Regression | Self-distillation (SD) is typically studied when the student is retrained on the teacher's original training i… | 23 |
| 2607.17025 | 07-19 | Federated Lightweight Intrusion Detection in Drone Swarms with Knowledge Distillation | 本文提出 a lightweight FL-based IDS tailored for drone swarm networks using deep neural networks (DNN) enhanced wi… | 23 |
| 2607.22013 | 07-24 | Visual Saliency Steering Distillation for Multimodal Chain-of-Thought Reasoning | Multimodal chain-of-thought (CoT) reasoning integrates visual and textual cues through step-by-step inference. | 23 |
| 2607.24611 | 07-27 | Test-Time Adaptation via Dual Distillation for Videos Under Severe Distribution Shifts | 本文提出 Test-time Adaptation via Dual Distillation (TADD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 23 |
| 2607.00289 | 07-01 | OnPoint: Offline-to-Online Multi-Level Distillation for Point-Supervised Online Temporal Action Localization | 本文提出 Point-Supervised Online TAL (POTAL)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.00514 | 07-01 | Cross4D-JEPA: Dense Cross-modal Correspondence Distillation for 4D Point Cloud Representation Learning | 本文提出 Cross4D-JEPA，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.01851 | 07-02 | Geometric Foundation Model Distillation for Efficient Lunar 3D Reconstruction | 本文提出 a structured SVD-based initialization that projects the teacher's decoder weights into the student's smal… | 22 |
| 2607.01906 | 07-02 | SFKD: Spatial--Frequency Joint-Aware Heterogeneous Knowledge Distillation via Multi-Level Wavelet Spectral Interaction | 本文提出 a Spatial-Frequency Joint-Aware Heterogeneous Knowledge Distillation framework (SFKD)，面向知识蒸馏场景解决模型存储/计算成本… | 22 |
| 2607.02593 | 07-01 | Token-level Response-visual Attention Guidance for Multimodal LLMs Knowledge Distillation | 本文提出 Token-level Response-visual Attention Guidance (TRAG)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.02966 | 07-03 | Distill Where the Student Goes: Teacher-Regularized RL for English-Evidence Cross-Lingual RAG | 本文提出 TR-RAG，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.03156 | 07-03 | DistillH-Mamba: A Hypergraph-Mamba-Based Knowledge Distillation Model for Efficient Impact Fall Detection | 本文提出 DistillH-Mamba，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.03760 | 07-04 | GeoSAM-Lite: A Lightweight Foundation Model for Onboard Remote Sensing Segmentation | 本文提出 \textit{Geo}spatial \textit{S}egment \textit{A}nything \textit{M}odel-Lite (GeoSAM-Lite)，面向知识蒸馏场景解决模型存储/计… | 22 |
| 2607.03960 | 07-04 | Reward Lightning: Fast Video Generation via Homologous Preference Distillation | 本文提出 Reward Lightning，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.04619 | 07-06 | CARD: Cross-component Audio Representation Distillation for Encoder-Free Audio Captioning | 本文提出 CARD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.04809 | 07-06 | Context-Constrained Transfer Learning for Tabular Foundation Models via Data Distillation | 本文提出 Context-Constrained Transfer Learning via ANchoring and DIstillation (TL-ANDI)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权… | 22 |
| 2607.05339 | 07-06 | TREK: Distill to Explore, Reinforce to Refine | 本文提出 TREK (Teacher-Routed Exploration via Forward KL)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.05605 | 07-06 | Patch Knowledge Transfer for Efficient AI-Generated Image Quality Assessment | 本文提出 Patch Knowledge Transfer (PKT)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.05721 | 07-07 | SpanUQ: Span-Level Uncertainty Quantification for Large Language Model Generation | 本文提出 SPANUQ，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.05750 | 07-07 | ArtisanCAD: An Industrial-Level CAD Agent with Expert-Grounded Knowledge Distillation | 本文提出 ArtisanCAD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.07292 | 07-08 | CarbonCLIP: Enhance Carbon Prediction from Satellite Imagery via Integrated Street-View Semantics and Temporal Context Training | 本文提出 CarbonCLIP，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.08161 | 07-09 | SQuaD-SQL: Efficient Text-to-SQL with Small Language Models via LLM-Guided Knowledge Distillation | 本文提出 SQuaD-SQL (Small-Qualified and Distilled for SQL)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.08771 | 07-09 | ZipDepth: Bringing Lightweight Zero-Shot Monocular Depth Anywhere, on Any Device | 本文提出 ZipDepth，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.09133 | 07-10 | IB-Flow: Information Bottleneck-Guided CFG Distillation for Few-Step Text-to-Image Generation | 本文提出 an instance-aware selection mechanism that transmutes the intractable KL divergence constraint into a zer… | 22 |
| 2607.10087 | 07-11 | CVKD-UDA: Cross-View Knowledge Distillation for 3D Unsupervised Domain Adaptive Segmentation | 本文提出 CVKD-UDA，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.10096 | 07-11 | Scaling and Stabilizing Large-Scale Embedding-Based Retrieval | 本文提出 a unified pipeline deployed at Walmart that addresses both signal quality and model evolution，面向知识蒸馏场景解决模… | 22 |
| 2607.10406 | 07-11 | TVT-PAPD: Pathology-Aware Prototype Distillation for Self-Supervised Whole Slide Image Classification | 本文提出 Tiny Vision Transformer with Pathology-Aware Prototype Distillation (TVT-PAPD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权… | 22 |
| 2607.10565 | 07-12 | BucketKD: A Safety-Aware Bucket-Based Knowledge Distillation Framework for End-to-End Motion Planning | 本文提出 BucketKD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.10666 | 07-12 | Answer-Conditioned Chain-of-Thought Distillation for Few-Shot Industrial Vision with Small VLMs | 本文提出 answer-conditioned chain-of-thought (CoT) distillation for rapidly adapting small vision-language models … | 22 |
| 2607.10762 | 07-12 | TOLiD: Bridging the Architecture Gap in Vision Foundation Model to LiDAR Pretraining via Token Lifting for Distillation | 本文提出 TOLiD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.10998 | 07-13 | Temporal Feature Distillation for Label-Efficient Precise Event Spotting in Sports Videos | 本文提出 Temporal Feature Distillation，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.11557 | 07-13 | Single-Teacher View Augmentation: Enhancing Knowledge Distillation with Student-Guided Perturbations | 本文提出 Shift-Augmented Knowledge Distillation (SAKD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.12297 | 07-14 | MobileSAM2: Lightweight Segment Anything for Spatial Intelligence | 本文提出 Hypergraphical Knowledge Distill (HyperKD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.12663 | 07-14 | MAGE: Color-Invariant and Spatial Knowledge Distillation for Gastric Neoplasm Classification | 本文提出 a novel framework，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.13452 | 07-15 | Symbiosis-Inspired Knowledge Distillation for Incremental Object Detection | 本文提出 Symbiosis-Inspired Knowledge Distillation (SIKD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.14640 | 07-16 | TIDE: Trustworthy and Interpretable Battery Degradation Estimation with Contextual Learning and Symbolic Distillation | 本文提出 TIDE，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.15736 | 07-17 | Better Starts, Better Ends: Bootstrapped Iterative Self-Reasoning Distillation for Compressed Reasoning | 本文提出 BIRD(Bootstrapped Iterative Self-Reasoning Distillation)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.16678 | 07-18 | Pseudo-label distillation for discriminative anomalous sound detection | 本文提出 a simple pseudo-label distillation framework，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.18152 | 07-20 | jina-reranker-v3.5: An Efficient Listwise Reranker with Hybrid Attention and Self-Distillation | 本文提出 jina-reranker-v3.5，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.18693 | 07-21 | Rationale-Guided Knowledge Distillation for Cross-Lingual Stance Detection | 本文提出 a rationale-guided knowledge distillation framework for cross-lingual stance detection，面向知识蒸馏场景解决模型存储/计算成… | 22 |
| 2607.18850 | 07-21 | OPD-IAD: From Language Judgment to Industrial Anomaly Detection via On-Policy Self-Distillation | 本文提出 \textbf{OPD-IAD}，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.19426 | 07-20 | Making Single-Cell Data Distillation Auditable: Traceable Real-Cell Coresets via Discrete Min-Max Selection | 本文提出 two real-cell selectors，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.19956 | 07-22 | When Does Knowledge Distillation Hurt? Reliability-Aware Distillation for Low-Resource Language Summarization | 本文提出 two complementary reliability-aware distillation methods，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.20072 | 07-22 | Factor-Informed Uncertainty Distillation for Gaze Estimation | 本文提出 Factor-Informed Uncertainty Distillation (FIUD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.20918 | 07-23 | OPOD: On-Policy Omni Distillation | 本文提出 On-Policy Omni Distillation (OPOD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.21592 | 07-23 | Unified Video Dense Prediction from Disjoint Data | 本文提出 UniD，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.23346 | 07-25 | SPRKD: Effective Knowledge Distillation for Deep Neural Networks via Saddle Region Approximation | 本文提出 Saddle Point Recruitment for Knowledge Distillation (SPRKD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.24280 | 07-27 | From Proprietary to Open-Source: Bridging the Distribution Gap via Multi-Agent Protocol Distillation in Agentic Search | 本文提出 Multi-Agent Protocol Distillation (MAPD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.24720 | 07-27 | The Physics of Multi-Turn Long-Horizon Planning: From Pre-training to Post-training via Single- and Multi-Teacher On-Policy Agentic Distillation | 本文提出 a unified and controlled multi-turn environment that enables precise control，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问… | 22 |
| 2607.24731 | 07-27 | Rethinking Classifier-Free Guidance in On-Policy Diffusion Distillation | 本文提出 Positive--Direction Matching (PDM)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.25215 | 07-28 | Leveraging Semantic Maps for City-Scale Cross-View Localization | 本文提出 distilling a lightweight matcher from a VLM which computes correspondences for all entities in a map，面向知识… | 22 |
| 2607.25289 | 07-28 | AMRD: Adaptive Multi-Teacher Relational Distillation for Lightweight Speech Emotion Recognition | 本文提出 Adaptive Multi-teacher Relational Distillation (AMRD) to address both，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.25318 | 07-28 | Beyond Background Bias: Saliency-Driven Prototype Alignment for Dataset Distillation | 本文提出 a saliency-driven distillation framework that constructs class-discriminative latent prototypes to enhanc… | 22 |
| 2607.25554 | 07-28 | Distilling Temporal Search and Reasoning: Evolving LLMs for Future Prediction via Harness-Assisted Efficient Data Synthesis | 本文提出 a time-truncation harness that enforces a temporal cut-off at every turn，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.26004 | 07-28 | Parallel Decoding Distillation for Fast Image and Video Generation | 本文提出 Parallel Decoding Distillation (PDD)，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.26238 | 07-28 | Lightweight Image Classification of Raptor Species for Edge Devices: Rare-Species Dataset Expansion via Video Frame Extraction, Knowledge Distillation, and TensorRT Deployment | We investigate lightweight raptor-species classification for real-time edge deployment in wind-turbine collisi… | 22 |
| 2607.26722 | 07-29 | DREvo: Distilling Recalibrated Historical Experience for Harness Self-Evolution | 本文提出 a new harness self-evolution method，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.26763 | 07-29 | Long-Tailed 3D Point Cloud Dataset Distillation | 本文提出 the first study on long-tailed point cloud dataset distillation，面向知识蒸馏场景解决模型存储/计算成本与精度之间的权衡问题。 | 22 |
| 2607.01827 | 07-02 | C2E: Boosting Ego-Only 3D Object Detection via Multi-Teacher Contrastive Knowledge Distillation | LiDAR-based 3D object detection is essential for autonomous driving systems. | 21 |
| 2607.04432 | 07-05 | Covert Trait Propagation Is Representation Alignment: Mechanistic Evidence from Hidden-Channel Distillation | A student model trained on pure uniform noise can still inherit its teacher's digit-classification ability, pr… | 21 |
| 2607.08268 | 07-09 | Different Teachers, Different Capabilities: Sub-1B On-Device Distillation for Structured Text Enrichment | High-volume structured extraction pays a large model's latency on every item, so distilling the task into a sm… | 21 |
| 2607.11465 | 07-13 | Score-Only Distillation for Compact Dense Retrieval | Large embedding models improve retrieval quality, but serving large encoders online is expensive. | 21 |
| 2607.11948 | 07-11 | Ontology-Amplified Distillation and Contextuality Auditing for Sovereign Enterprise Language Models: A Combined Proof-of-Mechanism and Negative-Results Method Study | Regulated financial institutions operating under data-residency rules need tenant-owned language models that c… | 21 |
| 2607.14709 | 07-16 | Gold-Guided Programmatic Distillation for Financial Reasoning over Hybrid Tables and Text | 本文提出 an approach that transfers reliable numerical reasoning from a large teacher model to a compact student u… | 21 |
| 2607.15467 | 07-16 | ADS-C: Antidistillation Sampling for Classification | Knowledge distillation enables an adversary to replicate a proprietary classifier by querying its prediction i… | 21 |
| 2607.15919 | 07-17 | On the Failure of Boundary-Seeking Distillation in Bottlenecked Generative Architectures | Data-free knowledge distillation transfers the knowledge encoded in a teacher model to a student model without… | 21 |
| 2607.17099 | 07-19 | DepthART: Scaling Foundation Monocular Depth to Tiny Models | Recent geometric foundation models (e.g., Metric3D, Depth Anything and UniDepth) have substantially improved m… | 21 |
| 2607.18773 | 07-21 | Privileged Lesion-Context Relational Distillation for Mask-Free Skin Lesion Classification | Accurate skin lesion classification can benefit from lesion segmentation masks, but requiring masks or an auxi… | 21 |
| 2607.25545 | 07-28 | OrthKD: Extracting Generalized Clinical Knowledge from Heterogeneous Teachers for Lightweight Deployment | Deploying diabetic retinopathy (DR) screening models in primary care requires edge-efficient systems that rema… | 21 |
| 2607.25788 | 07-28 | GeoMFD: Continual Drone-View Geo-Localization with Geometry-Aware Adapter and Margin-Field Distillation | Existing drone-view geo-localization (DVGL) methods are mainly developed under a static training paradigm, whe… | 21 |
| 2607.27054 | 07-29 | CoCaRS: Correlation Calibration-Based Redundancy Suppression for Heterogeneous Knowledge Distillation | Knowledge distillation (KD) enables a compact student model to learn from a powerful teacher and has become an… | 21 |

### 其他（10 篇）

| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |
|---------|:-------:|---------|-----------|:---:|
| 2607.06982 | 07-08 | EdgeCompress: Coupling Multidimensional Model Compression and Dynamic Inference for EdgeAI | 本文提出 EdgeCompress，面向模型压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 23 |
| 2607.09063 | 07-10 | EvoLP: Self-Evolving Latency Predictor for Model Compression in Real-Time Edge Systems | Edge devices are increasingly utilized for deploying deep learning applications on embedded systems. | 21 |
| 2607.10237 | 07-11 | CoSAG: Compact Semantic Anchor Gaussians via Training-Free Rate-Distortion Coding | 本文提出 CoSAG，面向模型压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 20 |
| 2607.12656 | 07-14 | SpeedyGS: Content-Aware 3D Gaussian Splatting Compression via Two-Stage Optimization | 本文提出 SpeedyGS，面向模型压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 20 |
| 2607.15456 | 07-16 | Looped Latent Attention: Cross-Loop KV Compression for Looped Transformers | 本文提出 Looped Latent Attention (\lla{})，面向模型压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 20 |
| 2607.20538 | 07-10 | Codec-Gauge: Learning Compression-Friendly Gauges for Transformer KV Caches | 本文提出 Codec-Gauge，面向模型压缩场景解决模型存储/计算成本与精度之间的权衡问题。 | 20 |
| 2607.08057 | 07-09 | Towards Efficient Large Language Model Serving: A Survey on System-Aware KV Cache Optimization | Despite the rapid advancements of large language models (LLMs), LLM serving systems remain memory-intensive an… | 19 |
| 2607.08991 | 07-09 | Sensitivity-Aware Thresholding and Token Routing for Activation Sparsification in Large Language Models | Efficient inference in Large Language Models (LLMs) requires deciding where computation can be reduced while p… | 19 |
| 2607.22716 | 07-21 | Visual Token Compression Enhances Robustness of MLLMs | In this paper, we show for the first time that visual token pruning enhances the robustness of Multimodal Larg… | 19 |
| 2607.26835 | 07-29 | A Low-Power Sparse Convolution Accelerator with Idle-First-Task-Assignment for Edge Vision | In recent years, edge-vision monitoring systems for applications such as smart animal husbandry have faced str… | 18 |

---

*报告生成方式：`scripts/retrieval/_gen_report.py` 基于 `_arxiv_raw/final.json`（317 篇）与 `papers/2026-07/*/tech_analysis.md` 自动生成统计与表格；趋势分析与亮点评述为人工撰写。*
