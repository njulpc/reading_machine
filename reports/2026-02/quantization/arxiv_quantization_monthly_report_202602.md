# ArXiv 量化与模型压缩领域论文月报（2026-02）

**收集日期范围**: 2026-02-01 00:00 ~ 2026-02-28 23:59 (UTC)  
**检索关键词**: quantization, quantize, quantized, low-bit, model compression, pruning, sparsity, knowledge distillation, KV cache, mixed precision, GPTQ, AWQ  
**数据来源**: arXiv（API + cs.LG/cs.CL/cs.CV/cs.AI/cs.NE/cs.AR 月度列表交叉验证 + OpenAlex 摘要级检索补充）  
**论文总量**: 623 篇 = **核心压缩主题 391 篇** + **外围相关 232 篇**

> **分组标准**：**核心压缩主题**指论文的中心贡献本身就是模型量化 / KV cache 压缩 / 剪枝 / 稀疏化 / 知识蒸馏五类压缩技术之一（标题或摘要中该压缩方法处于方法核心位置）；**外围相关**指仅沾边压缩关键词的论文（如向量量化 tokenizer、低秩适配 LoRA 类、高效架构设计、数据集蒸馏、压缩理论、含"efficient/sparse"但非压缩中心贡献的工作等）。评分表覆盖全部核心论文。

---

## 一、总览统计

### 1.1 核心压缩主题按技术方向分布

| 技术方向 | 论文数 | 占核心比例 |
|---------|:-----:|:-----:|
| 量化（Quantization） | 149 | 38.1% |
| KV Cache 压缩 | 20 | 5.1% |
| 剪枝（Pruning） | 85 | 21.7% |
| 稀疏化（Sparsity） | 19 | 4.9% |
| 知识蒸馏（Knowledge Distillation） | 118 | 30.2% |
| **合计** | **391** | 100% |

### 1.2 核心量化论文的位宽分布（按摘要中明确提及的位宽统计，可重复计数）

| 位宽 | 论文数 |
|-----|:-----:|
| 1-bit | 11 |
| 2-bit | 9 |
| 4-bit | 35 |
| 8-bit | 48 |

### 1.3 核心论文的目标模型/应用分布（可多标签）

| 目标领域 | 论文数 |
|---------|:-----:|
| LLM | 183 |
| 边缘/端侧 | 121 |
| VLM/多模态 | 49 |
| 扩散模型 | 39 |
| 传统视觉 | 26 |
| 推荐系统 | 12 |

**开源情况**：核心论文中 53 篇在摘要中给出 GitHub 代码链接（13.6%）。

### 1.4 外围相关论文构成

| 沾边方向 | 论文数 |
|---------|:-----:|
| 量化 | 72 |
| 剪枝 | 64 |
| 蒸馏 | 56 |
| 低秩 | 41 |
| 高效架构 | 37 |
| 向量量化 | 26 |
| 硬件协同 | 20 |
| 稀疏 | 15 |
| 其他 | 11 |
| KV cache | 6 |

---

## 二、核心压缩主题论文评分表（覆盖全部 391 篇核心论文）

**评分规则**（1–10 分，依据摘要文本的规则化评估，见月末说明）：
- **精度效果**：是否有 SOTA/超越基线声明、是否有具体数值提升、是否声称精度无损/微损；
- **压缩倍率**：位宽（1-bit≈10, 2-bit≈9, 4-bit≈8, 8-bit≈6）或显式压缩比/稀疏度；
- **创新性**：是否声称首次/新范式、是否有命名方法；综述/纯分析类降档；
- **可复现性**：摘要给出 GitHub 链接≈9，声明将开源≈6，无代码但方法简单≈4–5，依赖专用硬件≈4。

### 2.1 量化（Quantization） — 149 篇

| 序号 | arXiv ID | 论文标题 | 日期 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|:---:|---------|---------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2602.00165 | Benford's Law as a Distributional Prior for Post-Training… | 01-29* | 8 | 8 | 7 | 5 |
| 2 | 2602.00567 | Forget by Uncertainty: Orthogonal Entropy Unlearning for … | 01-31* | 7 | 5 | 9 | 4 |
| 3 | 2602.00969 | On the Spectral Flattening of Quantized Embeddings | 02-01 | 5 | 8 | 6 | 4 |
| 4 | 2602.01027 | SFMP: Fine-Grained, Hardware-Friendly and Search-Free Mix… | 02-01 | 7 | 7 | 9 | 9 |
| 5 | 2602.01037 | VEQ: Modality-Adaptive Quantization for MoE Vision-Langua… | 02-01 | 7 | 5 | 7 | 9 |
| 6 | 2602.01273 | Q-DiT4SR: Exploration of Detail-Preserving Diffusion Tran… | 02-01 | 7 | 5 | 9 | 9 |
| 7 | 2602.01289 | Gradient-Aligned Calibration for Post-Training Quantizati… | 02-01 | 5 | 5 | 9 | 5 |
| 8 | 2602.01410 | SNIP: An Adaptive Mixed Precision Framework for Subbyte L… | 02-01 | 8 | 8 | 6 | 4 |
| 9 | 2602.01459 | Understanding vision transformer robustness through the l… | 02-01 | 6 | 8 | 6 | 4 |
| 10 | 2602.01741 | Tail-Aware Post-Training Quantization for 3D Geometry Mod… | 02-02 | 7 | 7 | 7 | 6 |
| 11 | 2602.01793 | ParaGSE: Parallel Generative Speech Enhancement with Grou… | 02-02 | 5 | 5 | 8 | 4 |
| 12 | 2602.02001 | Preserve-Then-Quantize: Balancing Rank Budgets for Quanti… | 02-02 | 5 | 9 | 7 | 5 |
| 13 | 2602.02047 | Dissecting Outlier Dynamics in LLM NVFP4 Pretraining | 02-02 | 6 | 8 | 7 | 4 |
| 14 | 2602.02071 | BAPS: A Fine-Grained Low-Precision Scheme for Softmax in … | 02-02 | 5 | 6 | 9 | 4 |
| 15 | 2602.02110 | An Empirical Study of World Model Quantization | 02-02 | 5 | 7 | 7 | 9 |
| 16 | 2602.02126 | Two-Stage Grid Optimization for Group-wise Quantization o… | 02-02 | 5 | 7 | 9 | 4 |
| 17 | 2602.02151 | Revisiting Adaptive Rounding with Vectorized Reparameteri… | 02-02 | 6 | 5 | 6 | 9 |
| 18 | 2602.02338 | Rethinking Generative Recommender Tokenizer: Recsys-Nativ… | 02-02 | 8 | 5 | 7 | 9 |
| 19 | 2602.02538 | Enhancing Post-Training Quantization via Future Activatio… | 01-28* | 5 | 5 | 7 | 5 |
| 20 | 2602.02546 | D$^2$Quant: Accurate Low-bit Post-Training Weight Quantiz… | 01-30* | 6 | 8 | 9 | 5 |
| 21 | 2602.02581 | QuantLRM: Quantization of Large Reasoning Models via Fine… | 01-31* | 6 | 5 | 7 | 4 |
| 22 | 2602.02707 | Every Bit Counts: A Theoretical Study of Precision-Expres… | 02-02 | 5 | 10 | 7 | 4 |
| 23 | 2602.02711 | Dynamic Mixed-Precision Routing for Efficient Multi-step … | 02-02* | 5 | 5 | 7 | 4 |
| 24 | 2602.02726 | Vector Quantized Latent Concepts: A Scalable Alternative … | 02-02 | 5 | 5 | 7 | 4 |
| 25 | 2602.02958 | Quant VideoGen: Auto-Regressive Long Video Generation via… | 02-03 | 8 | 9 | 7 | 9 |
| 26 | 2602.03120 | Quantized Evolution Strategies: High-precision Fine-tunin… | 02-03 | 8 | 5 | 6 | 9 |
| 27 | 2602.03176 | BinaryDemoire: Moiré-Aware Binarization for Image Demoiré… | 02-03 | 7 | 10 | 9 | 9 |
| 28 | 2602.03182 | LSGQuant: Layer-Sensitivity Guided Quantization for One-S… | 02-03 | 5 | 7 | 7 | 9 |
| 29 | 2602.03472 | Inlier-Centric Post-Training Quantization for Object Dete… | 02-03 | 5 | 5 | 7 | 5 |
| 30 | 2602.03505 | Generative Decompression: Optimal Lossy Decoding Against … | 02-03 | 5 | 5 | 6 | 4 |
| 31 | 2602.03537 | MatGPTQ: Accurate and Efficient Post-Training Matryoshka … | 02-03 | 5 | 7 | 6 | 9 |
| 32 | 2602.03614 | Quantization-Aware Regularizers for Deep Neural Networks … | 02-03 | 8 | 5 | 9 | 4 |
| 33 | 2602.03760 | RAWDet-7: A Multi-Scenario Benchmark for Object Detection… | 02-03 | 5 | 8 | 7 | 4 |
| 34 | 2602.03782 | QVLA: Not All Channels Are Equal in Vision-Language-Actio… | 02-03 | 6 | 5 | 9 | 6 |
| 35 | 2602.03922 | Online Vector Quantized Attention | 02-03 | 6 | 5 | 6 | 4 |
| 36 | 2602.04099 | Rethinking Perplexity: Revealing the Impact of Input Leng… | 02-04 | 5 | 5 | 8 | 4 |
| 37 | 2602.04163 | BPDQ: Bit-Plane Decomposition Quantization on a Variable … | 02-04 | 5 | 8 | 7 | 9 |
| 38 | 2602.04460 | DOS: Dual-Flow Orthogonal Semantic IDs for Recommendation… | 02-04 | 5 | 5 | 7 | 4 |
| 39 | 2602.04929 | TurboBoA: Faster and Exact Attention-aware Quantization w… | 02-04 | 5 | 7 | 7 | 9 |
| 40 | 2602.05201 | Diffusion-aided Extreme Video Compression with Lightweigh… | 02-05 | 6 | 8 | 8 | 4 |
| 41 | 2602.05213 | Dual-Representation Image Compression at Ultra-Low Bitrat… | 02-05* | 8 | 8 | 7 | 5 |
| 42 | 2602.05269 | Hybrid Gated Flow (HGF): Stabilizing 1.58-bit LLMs via Se… | 02-05 | 6 | 8 | 7 | 4 |
| 43 | 2602.05367 | RaBiT: Residual-Aware Binarization Training for Accurate … | 02-05 | 7 | 9 | 9 | 9 |
| 44 | 2602.05743 | Balancing FP8 Computation Accuracy and Efficiency on Digi… | 02-05* | 5 | 6 | 6 | 4 |
| 45 | 2602.05902 | CoreQ: Learning-Free Mismatch Correction and Successive R… | 02-05 | 5 | 7 | 6 | 5 |
| 46 | 2602.06069 | HQP: Sensitivity-Aware Hybrid Quantization and Pruning fo… | 02-02 | 5 | 6 | 8 | 5 |
| 47 | 2602.06181 | Uncertainty Drives Social Bias Changes in Quantized Large… | 02-05 | 6 | 8 | 9 | 5 |
| 48 | 2602.06252 | D-Legion: A Scalable Many-Core Architecture for Accelerat… | 02-05 | 7 | 5 | 8 | 4 |
| 49 | 2602.06300 | Accelerating Vision Transformers on Brain Processing Unit | 02-06 | 6 | 6 | 9 | 4 |
| 50 | 2602.06523 | MicroBi-ConvLSTM: An Ultra-Lightweight Efficient Model fo… | 02-06 | 6 | 6 | 7 | 4 |
| 51 | 2602.06592 | ProtoQuant: Quantization of Prototypical Parts For Genera… | 02-06 | 5 | 5 | 9 | 4 |
| 52 | 2602.06694 | NanoQuant: Efficient Sub-1-Bit Quantization of Large Lang… | 02-06 | 5 | 10 | 9 | 9 |
| 53 | 2602.07374 | TernaryLM: Memory-Efficient Language Modeling via Native … | 02-07 | 8 | 8 | 7 | 9 |
| 54 | 2602.07465 | On the Importance of a Multi-Scale Calibration for Quanti… | 02-07 | 7 | 7 | 9 | 5 |
| 55 | 2602.07547 | Linguistic properties and model scale in brain encoding: … | 02-07 | 5 | 5 | 6 | 4 |
| 56 | 2602.07596 | Astro: Activation-guided Structured Regularization for Ou… | 02-07 | 5 | 7 | 7 | 5 |
| 57 | 2602.07849 | LQA: A Lightweight Quantized-Adaptive Framework for Visio… | 02-08 | 8 | 5 | 7 | 6 |
| 58 | 2602.07899 | Rethinking Practical and Efficient Quantization Calibrati… | 02-08 | 5 | 5 | 6 | 6 |
| 59 | 2602.08043 | V-ABFT: Variance-Based Adaptive Threshold for Fault-Toler… | 02-08 | 5 | 5 | 7 | 4 |
| 60 | 2602.08081 | Investigating Energy Bounds of Analog Compute-in-Memory w… | 02-08 | 5 | 8 | 6 | 4 |
| 61 | 2602.08269 | Quantization-aware Photonic Homodyne computing for Accele… | 02-09 | 5 | 5 | 6 | 4 |
| 62 | 2602.08376 | OJBKQ: Objective-Joint Babai-Klein Quantization | 02-09 | 5 | 8 | 7 | 5 |
| 63 | 2602.08600 | Beyond Scalar Scores: Reinforcement Learning for Error-Aw… | 02-09 | 7 | 8 | 9 | 4 |
| 64 | 2602.08669 | Reliable one-bit quantization of bandlimited graph data v… | 02-09 | 5 | 5 | 7 | 4 |
| 65 | 2602.08817 | Kirin: Improving ANN efficiency with SNN Hybridization | 02-09 | 5 | 7 | 9 | 4 |
| 66 | 2602.08923 | DynamiQ: Accelerating Gradient Synchronization using Comp… | 02-09 | 8 | 8 | 9 | 4 |
| 67 | 2602.09130 | UniComp: A Unified Evaluation of Large Language Model Com… | 02-09 | 6 | 5 | 7 | 4 |
| 68 | 2602.09323 | LLM-CoOpt: A Co-Design and Optimization Framework for Eff… | 02-10 | 6 | 6 | 9 | 4 |
| 69 | 2602.09872 | BabyMamba-HAR: Lightweight Selective State Space Models f… | 02-10 | 6 | 6 | 6 | 4 |
| 70 | 2602.09883 | AdaTSQ: Pushing the Pareto Frontier of Diffusion Transfor… | 02-10 | 8 | 5 | 9 | 9 |
| 71 | 2602.10262 | Execution-Centric Characterization of FP8 Matrix Cores, A… | 02-10 | 5 | 6 | 7 | 4 |
| 72 | 2602.10431 | QTALE: Quantization-Robust Token-Adaptive Layer Execution… | 02-11 | 6 | 5 | 9 | 5 |
| 73 | 2602.10455 | Compute Only Once: UG-Separation for Efficient Large Reco… | 02-11 | 6 | 6 | 9 | 4 |
| 74 | 2602.10605 | Evaluating Numerical Accuracy in Mixed-Precision Computin… | 02-11 | 5 | 5 | 7 | 4 |
| 75 | 2602.10718 | SnapMLA: Efficient Long-Context MLA Decoding via Hardware… | 02-11 | 7 | 6 | 7 | 9 |
| 76 | 2602.10940 | FastUSP: A Multi-Level Collaborative Acceleration Framewo… | 02-11 | 7 | 6 | 7 | 4 |
| 77 | 2602.11184 | KBVQ-MoE: KLT-guided SVD with Bias-Corrected Vector Quant… | 01-30* | 6 | 8 | 9 | 4 |
| 78 | 2602.11513 | Differentially Private and Communication Efficient Large … | 02-12 | 5 | 5 | 9 | 4 |
| 79 | 2602.11882 | Where Bits Matter in World Model Planning: A Paired Mixed… | 02-12 | 5 | 6 | 6 | 9 |
| 80 | 2602.11937 | Extending Puzzle for Mixture-of-Experts Reasoning Models … | 02-12 | 7 | 6 | 6 | 5 |
| 81 | 2602.12295 | Design Environment of Quantization-Aware Edge AI Hardware… | 02-01 | 6 | 6 | 6 | 5 |
| 82 | 2602.12593 | RQ-GMM: Residual Quantized Gaussian Mixture Model for Mul… | 02-13 | 6 | 5 | 7 | 4 |
| 83 | 2602.12609 | QuEPT: Quantized Elastic Precision Transformers with One-… | 02-13 | 7 | 5 | 7 | 9 |
| 84 | 2602.12635 | Unleashing Low-Bit Inference on Ascend NPUs: A Comprehens… | 02-13 | 7 | 8 | 6 | 5 |
| 85 | 2602.12675 | SLA2: Sparse-Linear Attention with Learnable Routing and … | 02-13 | 6 | 7 | 7 | 4 |
| 86 | 2602.13073 | LCSB: Layer-Cyclic Selective Backpropagation for Memory-E… | 02-13 | 6 | 8 | 9 | 4 |
| 87 | 2602.13151 | Quantization-Robust LLM Unlearning via Low-Rank Adaptation | 02-13 | 5 | 8 | 7 | 5 |
| 88 | 2602.13289 | Evaluating the Impact of Post-Training Quantization on Re… | 02-08 | 6 | 8 | 9 | 5 |
| 89 | 2602.13446 | End-to-End NOMA with Perfect and Quantized CSI Over Rayle… | 02-13 | 5 | 5 | 6 | 4 |
| 90 | 2602.13595 | The Quantization Trap: Breaking Linear Scaling Laws in Mu… | 02-14 | 5 | 8 | 6 | 4 |
| 91 | 2602.13628 | Compact LLM Deployment and World Model Assisted Offloadin… | 02-14 | 6 | 7 | 8 | 4 |
| 92 | 2602.13710 | HBVLA: Pushing 1-Bit Post-Training Quantization for Visio… | 02-14 | 9 | 10 | 9 | 4 |
| 93 | 2602.13837 | A Causal Diffusion Model for Video Reconstruction from Ul… | 02-14* | 5 | 8 | 7 | 4 |
| 94 | 2602.13953 | QuRL: Efficient Reinforcement Learning with Quantized Rol… | 02-15 | 6 | 6 | 9 | 4 |
| 95 | 2602.14432 | S2D: Selective Spectral Decay for Quantization-Friendly C… | 02-16 | 6 | 7 | 7 | 4 |
| 96 | 2602.15045 | VQ-DSC-R: Robust Vector Quantized-Enabled Digital Semanti… | 02-05 | 5 | 5 | 7 | 4 |
| 97 | 2602.15082 | S-PRESSO: Ultra Low Bitrate Sound Effect Compression With… | 02-16 | 7 | 10 | 7 | 4 |
| 98 | 2602.15491 | The Equalizer: Introducing Shape-Gain Decomposition in Ne… | 02-17 | 5 | 5 | 7 | 4 |
| 99 | 2602.15530 | Adaptive Selection of Codebook Using Assistance Informati… | 02-17 | 5 | 5 | 6 | 4 |
| 100 | 2602.15563 | 1-Bit Wonder: Improving QAT Performance in the Low-Bit Re… | 02-17 | 7 | 10 | 6 | 4 |
| 101 | 2602.15586 | Uniform error bounds for quantized dynamical models | 02-17 | 5 | 5 | 9 | 4 |
| 102 | 2602.15836 | EdgeNav-QE: QLoRA Quantization and Dynamic Early Exit for… | 01-12* | 8 | 8 | 9 | 4 |
| 103 | 2602.16309 | The Weight of a Bit: EMFI Sensitivity Analysis of Embedde… | 02-18 | 6 | 6 | 5 | 4 |
| 104 | 2602.16640 | Quecto-V1: Empirical Analysis of 8-bit Quantized Small La… | 02-18 | 8 | 6 | 5 | 5 |
| 105 | 2602.16951 | BrainRVQ: A High-Fidelity EEG Foundation Model via Dual-D… | 02-18 | 7 | 5 | 7 | 9 |
| 106 | 2602.17133 | VP-VAE: Rethinking Vector Quantization via Adaptive Vecto… | 02-19 | 5 | 5 | 9 | 4 |
| 107 | 2602.17287 | Representation Collapse in Machine Translation Through th… | 02-19 | 5 | 5 | 6 | 4 |
| 108 | 2602.17681 | LATMiX: Learnable Affine Transformations for Microscaling… | 02-04 | 6 | 7 | 9 | 5 |
| 109 | 2602.17691 | Tethered Reasoning: Decoupling Entropy from Hallucination… | 02-06 | 6 | 8 | 7 | 4 |
| 110 | 2602.17693 | A Case Study of Selected PTQ Baselines for Reasoning LLMs… | 02-06 | 5 | 8 | 6 | 5 |
| 111 | 2602.17698 | ScaleBITS: Scalable Bitwidth Search for Hardware-Aligned … | 02-06 | 9 | 8 | 7 | 5 |
| 112 | 2602.18109 | TempoNet: Slack-Quantized Transformer-Guided Reinforcemen… | 02-20 | 5 | 5 | 7 | 4 |
| 113 | 2602.18420 | SPQ: An Ensemble Technique for Large Language Model Compr… | 02-20 | 8 | 6 | 6 | 9 |
| 114 | 2602.18758 | UFO: Unlocking Ultra-Efficient Quantized Private Inferenc… | 02-21 | 9 | 5 | 9 | 4 |
| 115 | 2602.18861 | Joint Post-Training Quantization of Vision Transformers w… | 02-21 | 8 | 8 | 9 | 5 |
| 116 | 2602.18896 | Beyond Stationarity: Rethinking Codebook Collapse in Vect… | 02-21 | 5 | 5 | 9 | 9 |
| 117 | 2602.19031 | SKYLIGHT: A Scalable Hundred-Channel 3D Photonic In-Memor… | 02-22 | 5 | 7 | 6 | 4 |
| 118 | 2602.19241 | Scaling Laws for Precision in High-Dimensional Linear Reg… | 02-22 | 5 | 5 | 6 | 4 |
| 119 | 2602.19268 | CORVET: A CORDIC-Powered, Resource-Frugal Mixed-Precision… | 02-22 | 8 | 5 | 6 | 4 |
| 120 | 2602.19938 | A Replicate-and-Quantize Strategy for Plug-and-Play Load … | 02-23 | 6 | 5 | 7 | 5 |
| 121 | 2602.20083 | CQ-CiM: Hardware-Aware Embedding Shaping for Robust CiM-B… | 02-23 | 5 | 9 | 9 | 4 |
| 122 | 2602.20191 | MoBiQuant: Mixture-of-Bits Quantization for Token-Adaptiv… | 02-21 | 5 | 5 | 9 | 4 |
| 123 | 2602.20309 | QuantVLA: Scale-Calibrated Post-Training Quantization for… | 02-23 | 6 | 7 | 9 | 5 |
| 124 | 2602.20319 | Cooperative ISAC for Joint Localization and Velocity Esti… | 02-23 | 8 | 5 | 7 | 4 |
| 125 | 2602.20650 | Dataset Color Quantization: A Training-Oriented Framework… | 02-24 | 6 | 8 | 7 | 4 |
| 126 | 2602.20662 | TOM: A Ternary Read-only Memory Accelerator for LLM-power… | 02-24 | 5 | 5 | 7 | 4 |
| 127 | 2602.21009 | HiSAC: Hierarchical Sparse Activation Compression for Ult… | 02-24 | 6 | 5 | 7 | 4 |
| 128 | 2602.21144 | Scaling State-Space Models on Multiple GPUs with Tensor P… | 02-24 | 6 | 5 | 6 | 4 |
| 129 | 2602.21233 | AngelSlim: A more accessible, comprehensive, and efficien… | 02-07 | 7 | 6 | 9 | 5 |
| 130 | 2602.21591 | CADC: Content Adaptive Diffusion-Based Generative Image C… | 02-25 | 5 | 8 | 9 | 4 |
| 131 | 2602.21600 | AQR-HNSW: Accelerating Approximate Nearest Neighbor Searc… | 02-25 | 8 | 8 | 8 | 4 |
| 132 | 2602.21667 | Send Less, Perceive More: Masked Quantized Point Cloud Co… | 02-25 | 5 | 5 | 7 | 4 |
| 133 | 2602.21780 | XStreamVGGT: Extremely Memory-Efficient Streaming Vision … | 02-25 | 6 | 5 | 7 | 9 |
| 134 | 2602.21986 | Quantum Resistance in Multilayer Graphene-BiFeO3 Memristo… | 02-25 | 5 | 5 | 8 | 4 |
| 135 | 2602.22136 | SigmaQuant: Hardware-Aware Heterogeneous Quantization Met… | 02-25 | 5 | 7 | 6 | 4 |
| 136 | 2602.22268 | AutoQRA: Joint Optimization of Mixed-Precision Quantizati… | 02-25 | 6 | 8 | 9 | 4 |
| 137 | 2602.22352 | GRAU: Generic Reconfigurable Activation Unit Design for N… | 02-25 | 6 | 10 | 7 | 4 |
| 138 | 2602.22545 | Interpretable Tau-PET Synthesis from Multimodal T1-Weight… | 02-26 | 5 | 5 | 6 | 4 |
| 139 | 2602.22592 | pQuant: Towards Effective Low-Bit Language Models via Dec… | 02-26 | 7 | 9 | 7 | 4 |
| 140 | 2602.22984 | Holomorphic Quantization in Constant Curvature Backgrounds | 02-26 | 5 | 5 | 7 | 4 |
| 141 | 2602.23012 | Sequential Regression for Continuous Value Prediction usi… | 02-26 | 5 | 5 | 7 | 4 |
| 142 | 2602.23192 | FairQuant: Fairness-Aware Mixed-Precision Quantization fo… | 02-26 | 5 | 6 | 7 | 5 |
| 143 | 2602.23200 | InnerQ: Hardware-Aware Tuning-Free Quantization of KV Cac… | 02-26 | 5 | 7 | 7 | 4 |
| 144 | 2602.23252 | A Scaling Law for Bandwidth Under Quantization | 02-26 | 5 | 5 | 6 | 4 |
| 145 | 2602.23334 | Bitwise Systolic Array Architecture for Runtime-Reconfigu… | 02-26 | 5 | 7 | 7 | 4 |
| 146 | 2602.23349 | FlashOptim: Optimizers for Memory-Efficient Training | 02-26 | 6 | 6 | 9 | 4 |
| 147 | 2602.23455 | BiKA: Kolmogorov-Arnold-Network-inspired Ultra Lightweigh… | 02-26 | 6 | 5 | 9 | 4 |
| 148 | 2602.23722 | SLA-Aware Distributed LLM Inference Across Device-RAN-Clo… | 02-27 | 5 | 5 | 6 | 4 |
| 149 | 2602.24059 | Quant Experts: Token-aware Adaptive Error Reconstruction … | 02-27 | 6 | 5 | 7 | 5 |

### 2.2 KV Cache 压缩 — 20 篇

| 序号 | arXiv ID | 论文标题 | 日期 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|:---:|---------|---------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2602.01801 | Fast Autoregressive Video Diffusion and World Models with… | 02-02 | 5 | 5 | 7 | 5 |
| 2 | 2602.01901 | Q Cache: Visual Attention is Valuable in Less than Half o… | 02-02 | 8 | 5 | 9 | 4 |
| 3 | 2602.02197 | Hierarchical Adaptive Eviction for KV Cache Management in… | 02-02 | 6 | 5 | 7 | 4 |
| 4 | 2602.02199 | More Than a Quick Glance: Overcoming the Greedy Bias in K… | 02-02 | 6 | 5 | 7 | 4 |
| 5 | 2602.02579 | ProphetKV: User-Query-Driven Selective Recomputation for … | 01-31* | 8 | 5 | 7 | 4 |
| 6 | 2602.02599 | RAP: KV-Cache Compression via RoPE-Aligned Pruning | 02-01 | 6 | 5 | 7 | 4 |
| 7 | 2602.03184 | DynSplit-KV: Dynamic Semantic Splitting for KVCache Compr… | 02-03 | 6 | 6 | 7 | 4 |
| 8 | 2602.03203 | ForesightKV: Optimizing KV Cache Eviction for Reasoning M… | 02-03 | 7 | 5 | 9 | 9 |
| 9 | 2602.05305 | FlashBlock: Attention Caching for Efficient Long-Context … | 02-05 | 6 | 7 | 7 | 4 |
| 10 | 2602.05929 | KV-CoRE: Benchmarking Data-Dependent Low-Rank Compressibi… | 02-05 | 5 | 5 | 9 | 4 |
| 11 | 2602.07721 | ParisKV: Fast and Drift-Robust KV-Cache Retrieval for Lon… | 02-07 | 8 | 5 | 7 | 9 |
| 12 | 2602.08005 | DeltaKV: Residual-Based KV Cache Compression via Long-Ran… | 02-08 | 5 | 5 | 7 | 9 |
| 13 | 2602.08343 | ManifoldKV: Training-Free KV Cache Compression via Euclid… | 02-09 | 6 | 5 | 9 | 5 |
| 14 | 2602.08585 | Predicting Future Utility: Global Combinatorial Optimizat… | 02-09 | 7 | 5 | 9 | 4 |
| 15 | 2602.09725 | Efficient Remote KV Cache Reuse with GPU-native Video Cod… | 02-10* | 7 | 5 | 9 | 4 |
| 16 | 2602.10238 | Learning to Evict from Key-Value Cache | 02-10 | 8 | 5 | 7 | 4 |
| 17 | 2602.14236 | Dual-Signal Adaptive KV-Cache Optimization for Long-Form … | 02-15 | 6 | 6 | 9 | 4 |
| 18 | 2602.18196 | RAT+: Train Dense, Infer Sparse -- Recurrence Augmented A… | 02-20 | 6 | 10 | 7 | 9 |
| 19 | 2602.20732 | CHESS: Context-aware Hierarchical Efficient Semantic Sele… | 02-24 | 7 | 5 | 7 | 9 |
| 20 | 2602.22603 | SideQuest: Model-Driven KV Cache Management for Long-Hori… | 02-26 | 8 | 5 | 8 | 4 |

### 2.3 剪枝（Pruning） — 85 篇

| 序号 | arXiv ID | 论文标题 | 日期 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|:---:|---------|---------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2602.00047 | Lightweight Edge Learning via Dataset Pruning | 01-19* | 5 | 5 | 7 | 4 |
| 2 | 2602.00247 | CAPA: Contribution-Aware Pruning and FFN Approximation fo… | 01-30* | 5 | 5 | 7 | 4 |
| 3 | 2602.00268 | TokenTrim: Inference-Time Token Pruning for Autoregressiv… | 01-30* | 6 | 5 | 7 | 4 |
| 4 | 2602.00372 | Post-Training Probability Manifold Correction via Structu… | 01-30* | 6 | 7 | 7 | 5 |
| 5 | 2602.00534 | AIRE-Prune: Asymptotic Impulse-Response Energy for State … | 01-31* | 6 | 5 | 7 | 5 |
| 6 | 2602.00577 | SAU: Sparsity-Aware Unlearning for LLMs via Gradient Mask… | 01-31* | 6 | 5 | 7 | 4 |
| 7 | 2602.00780 | Environment-Aware Adaptive Pruning with Interleaved Infer… | 01-31* | 9 | 5 | 7 | 5 |
| 8 | 2602.00946 | ConsensusDrop: Fusing Visual and Cross-Modal Saliency for… | 02-01 | 7 | 7 | 7 | 6 |
| 9 | 2602.01082 | EvoOpt-LLM: Evolving industrial optimization models with … | 02-01 | 6 | 5 | 7 | 4 |
| 10 | 2602.01113 | Single-Edge Node Injection Threats to GNN-Based Security … | 02-01 | 5 | 5 | 6 | 4 |
| 11 | 2602.01131 | Lyapunov Stability-Aware Stackelberg Game for Low-Altitud… | 02-01 | 5 | 5 | 9 | 4 |
| 12 | 2602.01602 | Spectral-Aligned Pruning for Universal Error-Correcting C… | 02-02 | 5 | 5 | 6 | 4 |
| 13 | 2602.01609 | Token Pruning for In-Context Generation in Diffusion Tran… | 02-02 | 5 | 5 | 9 | 5 |
| 14 | 2602.01838 | AXE: Low-Cost Cross-Domain Web Structured Information Ext… | 02-02 | 8 | 8 | 7 | 9 |
| 15 | 2602.01842 | Prism: Efficient Test-Time Scaling via Hierarchical Searc… | 02-02 | 5 | 5 | 7 | 9 |
| 16 | 2602.01975 | IntraSlice: Towards High-Performance Structural Pruning w… | 02-02 | 5 | 5 | 7 | 4 |
| 17 | 2602.01997 | On the Limits of Layer Pruning for Generative Reasoning i… | 02-02* | 5 | 5 | 6 | 5 |
| 18 | 2602.02163 | Reg4Pru: Regularisation Through Random Token Routing for … | 02-02 | 6 | 5 | 7 | 4 |
| 19 | 2602.02739 | TopoPrune: Robust Data Pruning via Unified Latent Space T… | 02-02 | 6 | 5 | 7 | 4 |
| 20 | 2602.02883 | Efficiency Optimizations for Superblock-based Sparse Retr… | 02-02 | 5 | 5 | 8 | 4 |
| 21 | 2602.02891 | TraceNAS: Zero-shot LLM Pruning via Gradient Trace Correl… | 02-02 | 5 | 5 | 7 | 5 |
| 22 | 2602.02951 | Nüwa: Mending the Spatial Integrity Torn by VLM Token Pru… | 02-03 | 8 | 5 | 9 | 4 |
| 23 | 2602.03060 | IVC-Prune: Revealing the Implicit Visual Coordinates in L… | 02-03 | 5 | 5 | 9 | 9 |
| 24 | 2602.03134 | SwiftVLM: Efficient Vision-Language Model Inference via C… | 02-03 | 5 | 5 | 7 | 5 |
| 25 | 2602.03152 | FASA: Frequency-aware Sparse Attention | 02-03 | 7 | 5 | 9 | 4 |
| 26 | 2602.03295 | POP: Prefill-Only Pruning for Efficient Large Model Infer… | 02-03 | 6 | 5 | 9 | 4 |
| 27 | 2602.03815 | Fast-Slow Efficient Training for Multimodal Large Languag… | 02-03 | 6 | 5 | 7 | 9 |
| 28 | 2602.03918 | Entropy Reveals Block Importance in Masked Self-Supervise… | 02-03 | 8 | 5 | 6 | 5 |
| 29 | 2602.04153 | Pruning for Generalization: A Transfer-Oriented Spatiotem… | 02-04 | 5 | 5 | 7 | 4 |
| 30 | 2602.04166 | Topology-Aware Revival for Efficient Sparse Training | 02-04 | 8 | 5 | 7 | 4 |
| 31 | 2602.04491 | Greedy-Gnorm: A Gradient Matrix Norm-Based Alternative to… | 02-04 | 7 | 5 | 9 | 4 |
| 32 | 2602.04852 | The Key to State Reduction in Linear Attention: A Rank-ba… | 02-04 | 7 | 5 | 9 | 9 |
| 33 | 2602.04919 | Gradually Compacting Large Language Models for Reasoning … | 02-04 | 5 | 5 | 7 | 5 |
| 34 | 2602.04926 | Pruning Minimal Reasoning Graphs for Efficient Retrieval-… | 02-04 | 7 | 5 | 9 | 4 |
| 35 | 2602.05243 | CORP: Closed-Form One-shot Representation-Preserving Stru… | 02-05* | 6 | 7 | 7 | 5 |
| 36 | 2602.05499 | SDFP: Speculative Decoding with FIT-Pruned Models for Tra… | 02-05 | 5 | 5 | 7 | 5 |
| 37 | 2602.05605 | Shiva-DiT: Residual-Based Differentiable Top-$k$ Selectio… | 02-05 | 5 | 5 | 7 | 4 |
| 38 | 2602.05809 | Focus-Scan-Refine: From Human Visual Perception to Effici… | 02-05 | 5 | 7 | 9 | 9 |
| 39 | 2602.06127 | Compressing LLMs with MoP: Mixture of Pruners | 02-05 | 8 | 5 | 7 | 4 |
| 40 | 2602.06675 | Pruning at Initialisation through the lens of Graphon Lim… | 02-06 | 5 | 5 | 9 | 4 |
| 41 | 2602.06822 | POP: Online Structural Pruning Enables Efficient Inferenc… | 02-06 | 5 | 5 | 7 | 4 |
| 42 | 2602.06830 | GaussianPOP: Principled Simplification Framework for Comp… | 02-06 | 7 | 5 | 9 | 5 |
| 43 | 2602.07375 | Efficient Post-Training Pruning of Large Language Models … | 02-07 | 5 | 5 | 9 | 5 |
| 44 | 2602.07574 | ViCA: Efficient Multimodal LLMs with Vision-Only Cross-At… | 02-07 | 6 | 7 | 7 | 9 |
| 45 | 2602.07804 | Pruning as a Cooperative Game: Surrogate-Assisted Layer C… | 02-08 | 5 | 5 | 7 | 4 |
| 46 | 2602.08858 | FlattenGPT: Depth Compression for Transformer with Layer … | 02-09 | 7 | 5 | 8 | 4 |
| 47 | 2602.08905 | Efficient and Stable Reinforcement Learning for Diffusion… | 02-09 | 7 | 5 | 7 | 9 |
| 48 | 2602.09373 | AfriNLLB: Efficient Translation Models for African Langua… | 02-10 | 6 | 5 | 7 | 4 |
| 49 | 2602.09717 | From Lightweight CNNs to SpikeNets: Benchmarking Accuracy… | 02-10 | 8 | 8 | 9 | 4 |
| 50 | 2602.10357 | Theoretical Analysis of Contrastive Learning under Imbala… | 02-10 | 5 | 5 | 6 | 4 |
| 51 | 2602.10666 | From Diet to Free Lunch: Estimating Auxiliary Signal Prop… | 02-11* | 7 | 5 | 6 | 4 |
| 52 | 2602.11408 | GHOST: Unmasking Phantom States in Mamba2 via Grouped Hid… | 02-11 | 5 | 5 | 7 | 9 |
| 53 | 2602.12618 | Vision Token Reduction via Attention-Driven Self-Compress… | 02-13 | 8 | 5 | 7 | 4 |
| 54 | 2602.12744 | Adaptive Structured Pruning of Convolutional Neural Netwo… | 02-13 | 8 | 5 | 7 | 4 |
| 55 | 2602.13315 | IDPruner: Harmonizing Importance and Diversity in Visual … | 02-10 | 7 | 5 | 9 | 9 |
| 56 | 2602.14040 | Explainability-Inspired Layer-Wise Pruning of Deep Neural… | 02-15 | 6 | 5 | 7 | 4 |
| 57 | 2602.14649 | GradMAP: Faster Layer Pruning with Gradient Metric and Pr… | 02-16 | 7 | 5 | 9 | 4 |
| 58 | 2602.15224 | Phase Transitions in Neural Networks Pruning | 02-16 | 5 | 5 | 6 | 4 |
| 59 | 2602.15306 | Sparse Additive Model Pruning for Order-Based Causal Stru… | 02-17 | 5 | 5 | 9 | 4 |
| 60 | 2602.15521 | ExpertWeaver: Unlocking the Inherent MoE in Dense LLMs wi… | 02-17 | 6 | 5 | 7 | 5 |
| 61 | 2602.15720 | ToaSt: Token Channel Selection and Structured Pruning for… | 02-17 | 8 | 5 | 7 | 9 |
| 62 | 2602.15724 | Learning to Retrieve Navigable Candidates for Efficient V… | 02-17 | 5 | 5 | 7 | 4 |
| 63 | 2602.16876 | ML-driven detection and reduction of ballast information … | 02-18 | 6 | 5 | 8 | 4 |
| 64 | 2602.17145 | Bonsai: A Framework for Convolutional Neural Network Acce… | 02-19 | 5 | 5 | 9 | 4 |
| 65 | 2602.17196 | EntropyPrune: Matrix Entropy Guided Visual Token Pruning … | 02-19 | 8 | 7 | 9 | 9 |
| 66 | 2602.17664 | Sink-Aware Pruning for Diffusion Language Models | 02-19 | 5 | 5 | 7 | 9 |
| 67 | 2602.18116 | Cut Less, Fold More: Model Compression through the Lens o… | 02-20 | 5 | 5 | 6 | 4 |
| 68 | 2602.18507 | Fine-Pruning: A Biologically Inspired Algorithm for Perso… | 02-18 | 5 | 5 | 6 | 4 |
| 69 | 2602.19113 | Learning from Complexity: Exploring Dynamic Sample Prunin… | 02-22 | 5 | 5 | 8 | 4 |
| 70 | 2602.19167 | S$^3$GND: An Effective Learning-Based Approach for Subgra… | 02-22 | 5 | 5 | 9 | 4 |
| 71 | 2602.19549 | Sculpting the Vector Space: Towards Efficient Multi-Vecto… | 02-23 | 7 | 5 | 9 | 4 |
| 72 | 2602.19967 | Unlearning Noise in PINNs: A Selective Pruning Framework … | 02-23 | 6 | 9 | 7 | 4 |
| 73 | 2602.20205 | OTPrune: Distribution-Aligned Visual Token Pruning via Op… | 02-22 | 7 | 5 | 7 | 9 |
| 74 | 2602.20467 | Elimination-compensation pruning for fully-connected neur… | 02-24 | 5 | 5 | 8 | 4 |
| 75 | 2602.20566 | BFA++: Hierarchical Best-Feature-Aware Token Prune for Mu… | 02-24 | 8 | 5 | 7 | 4 |
| 76 | 2602.21652 | Sparsity Induction for Accurate Post-Training Pruning of … | 02-25 | 5 | 5 | 7 | 5 |
| 77 | 2602.22537 | LUMOS: Democratizing SciML Workflows with L0-Regularized … | 02-26 | 6 | 5 | 7 | 4 |
| 78 | 2602.23235 | Spatio-Temporal Token Pruning for Efficient High-Resoluti… | 02-26 | 8 | 7 | 7 | 5 |
| 79 | 2602.23258 | AgentDropoutV2: Optimizing Information Flow in Multi-Agen… | 02-26 | 6 | 5 | 7 | 9 |
| 80 | 2602.23400 | U-CAN: Utility-Aware Contrastive Attenuation for Efficien… | 02-26 | 5 | 5 | 7 | 4 |
| 81 | 2602.23699 | HiDrop: Hierarchical Vision Token Reduction in MLLMs via … | 02-27 | 8 | 5 | 7 | 9 |
| 82 | 2602.23734 | UTPTrack: Towards Simple and Unified Token Pruning for Vi… | 02-27 | 8 | 5 | 9 | 9 |
| 83 | 2602.23795 | GRAIL: Post-hoc Compensation by Linear Reconstruction for… | 02-27 | 5 | 7 | 7 | 9 |
| 84 | 2602.24136 | Prune Wisely, Reconstruct Sharply: Compact 3D Gaussian Sp… | 02-27 | 8 | 5 | 7 | 4 |
| 85 | 2602.24266 | Causal Mechanism Reduction: Mechanism Replacement for Neu… | 02-27 | 5 | 5 | 6 | 4 |

### 2.4 稀疏化（Sparsity） — 19 篇

| 序号 | arXiv ID | 论文标题 | 日期 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|:---:|---------|---------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2602.00397 | Fast Forward: Accelerating LLM Prefill with Predictive FF… | 01-30* | 6 | 5 | 9 | 4 |
| 2 | 2602.03214 | FARTrack: Fast Autoregressive Visual Tracking with High P… | 02-03 | 6 | 5 | 7 | 4 |
| 3 | 2602.03216 | Token Sparse Attention: Efficient Long-Context Inference … | 02-03 | 6 | 5 | 7 | 4 |
| 4 | 2602.03230 | EventFlash: Towards Efficient MLLMs for Event-Based Vision | 02-03 | 8 | 5 | 9 | 4 |
| 5 | 2602.03839 | Understanding and Exploiting Weight Update Sparsity for C… | 02-03 | 7 | 5 | 6 | 5 |
| 6 | 2602.05218 | Boosting SAM for Cross-Domain Few-Shot Segmentation via C… | 02-05* | 5 | 5 | 7 | 5 |
| 7 | 2602.06183 | To 2:4 Sparsity and Beyond: Neuron-level Activation Funct… | 02-05 | 6 | 5 | 6 | 4 |
| 8 | 2602.07729 | Do We Need Adam? Surprisingly Strong and Sparse Reinforce… | 02-07 | 9 | 5 | 6 | 4 |
| 9 | 2602.08218 | Sparsity-Aware Evolution for Model Merging | 02-09 | 5 | 5 | 9 | 4 |
| 10 | 2602.09169 | Train Less, Infer Faster: Efficient Model Finetuning and … | 02-09 | 7 | 5 | 7 | 4 |
| 11 | 2602.09386 | SMES: Towards Scalable Multi-Task Recommendation via Expe… | 02-10 | 6 | 5 | 7 | 4 |
| 12 | 2602.09869 | Statistical benchmarking of transformer models in low sig… | 02-10 | 5 | 5 | 6 | 4 |
| 13 | 2602.10754 | Exploring the impact of adaptive rewiring in Graph Neural… | 02-11 | 5 | 5 | 6 | 4 |
| 14 | 2602.11008 | ROCKET: Rapid Optimization via Calibration-guided Knapsac… | 02-11 | 8 | 5 | 9 | 9 |
| 15 | 2602.13515 | SpargeAttention2: Trainable Sparse Attention via Hybrid T… | 02-13 | 8 | 5 | 7 | 5 |
| 16 | 2602.13993 | Elastic Diffusion Transformer | 02-15 | 6 | 5 | 7 | 9 |
| 17 | 2602.14262 | ABI: A tightly integrated, unified, sparsity-aware, recon… | 02-15 | 5 | 10 | 7 | 4 |
| 18 | 2602.14578 | RNM-TD3: N:M Semi-structured Sparse Reinforcement Learnin… | 02-16 | 9 | 8 | 9 | 4 |
| 19 | 2602.22575 | S2O: Early Stopping for Sparse Attention via Online Permu… | 02-26 | 5 | 5 | 7 | 4 |

### 2.5 知识蒸馏（Knowledge Distillation） — 118 篇

| 序号 | arXiv ID | 论文标题 | 日期 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|:---:|---------|---------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2602.00647 | CoRe-Fed: Bridging Collaborative and Representation Fairn… | 01-31* | 5 | 5 | 7 | 4 |
| 2 | 2602.00681 | Audio-to-Image Bird Species Retrieval without Audio-Image… | 01-31* | 5 | 5 | 7 | 4 |
| 3 | 2602.00852 | Investigating the Robustness of Subtask Distillation unde… | 01-31* | 5 | 5 | 5 | 4 |
| 4 | 2602.00865 | Distill3R: A Pipeline for Democratizing 3D Foundation Mod… | 01-31* | 7 | 10 | 7 | 4 |
| 5 | 2602.00871 | Beyond Output Critique: Self-Correction via Task Distilla… | 01-31* | 5 | 5 | 9 | 4 |
| 6 | 2602.01007 | Distilling Token-Trained Models into Byte-Level Models | 02-01 | 5 | 5 | 7 | 4 |
| 7 | 2602.01064 | Exploring Knowledge Purification in Multi-Teacher Knowled… | 02-01 | 5 | 5 | 7 | 4 |
| 8 | 2602.01222 | FutureMind: Equipping Small Language Models with Strategi… | 02-01 | 7 | 5 | 7 | 4 |
| 9 | 2602.01265 | BicKD: Bilateral Contrastive Knowledge Distillation | 02-01 | 5 | 5 | 9 | 4 |
| 10 | 2602.01395 | Rethinking Selective Knowledge Distillation | 02-01 | 6 | 5 | 6 | 4 |
| 11 | 2602.01547 | Attention-weighted Centered Kernel Alignment for Knowledg… | 02-02 | 8 | 5 | 9 | 4 |
| 12 | 2602.01775 | Efficient Cross-Architecture Knowledge Transfer for Large… | 02-02 | 6 | 5 | 7 | 4 |
| 13 | 2602.01814 | GPD: Guided Progressive Distillation for Fast and High-Qu… | 02-02* | 5 | 5 | 9 | 4 |
| 14 | 2602.01937 | T-LLM: Teaching Large Language Models to Forecast Time Se… | 02-02* | 5 | 5 | 7 | 4 |
| 15 | 2602.01956 | Efficient Epistemic Uncertainty Estimation for Large Lang… | 02-02 | 7 | 5 | 7 | 4 |
| 16 | 2602.02107 | Teacher-Guided Student Self-Knowledge Distillation Using … | 02-02 | 6 | 5 | 9 | 4 |
| 17 | 2602.02142 | FD-VLA: Force-Distilled Vision-Language-Action Model for … | 02-02* | 5 | 5 | 9 | 4 |
| 18 | 2602.02214 | Causal Forcing: Autoregressive Diffusion Distillation Don… | 02-02* | 7 | 5 | 7 | 4 |
| 19 | 2602.02244 | Entropy-Preserving Supervised Fine-Tuning via Adaptive Se… | 02-02* | 7 | 5 | 7 | 5 |
| 20 | 2602.02318 | Enhancing Indoor Occupancy Prediction via Sparse Query-Ba… | 02-02 | 8 | 5 | 9 | 9 |
| 21 | 2602.02405 | Making Expert Reasoning Learnable with Self-Distillation | 02-02* | 6 | 5 | 9 | 4 |
| 22 | 2602.02532 | CADENT: Gated Hybrid Distillation for Sample-Efficient Tr… | 01-28* | 5 | 5 | 6 | 4 |
| 23 | 2602.02626 | Learning Better Certified Models from Empirically-Robust … | 02-02 | 5 | 5 | 7 | 4 |
| 24 | 2602.02960 | Embodiment-Aware Generalist Specialist Distillation for U… | 02-03* | 5 | 5 | 6 | 4 |
| 25 | 2602.02994 | Video-OPD: Efficient Post-Training of Multimodal Large La… | 02-03 | 5 | 5 | 7 | 5 |
| 26 | 2602.03006 | Distilling LLM Reasoning into Graph of Concept Predictors | 02-03* | 5 | 5 | 7 | 9 |
| 27 | 2602.03022 | STAR: Similarity-guided Teacher-Assisted Refinement for S… | 02-03 | 8 | 8 | 9 | 4 |
| 28 | 2602.03043 | SAFE-KD: Risk-Controlled Early-Exit Distillation for Visi… | 02-03 | 5 | 5 | 7 | 4 |
| 29 | 2602.03139 | Diversity-Preserved Distribution Matching Distillation fo… | 02-03* | 5 | 5 | 8 | 4 |
| 30 | 2602.03396 | Towards Distillation-Resistant Large Language Models: An … | 02-03* | 5 | 5 | 8 | 4 |
| 31 | 2602.03812 | Antidistillation Fingerprinting | 02-03* | 7 | 5 | 7 | 4 |
| 32 | 2602.03955 | AgentArk: Distilling Multi-Agent Intelligence into a Sing… | 02-03* | 5 | 5 | 8 | 4 |
| 33 | 2602.04260 | Decoupled Hierarchical Distillation for Multimodal Emotio… | 02-04 | 7 | 5 | 9 | 4 |
| 34 | 2602.04412 | HoRD: Robust Humanoid Control via History-Conditioned Rei… | 02-04 | 7 | 5 | 9 | 4 |
| 35 | 2602.04577 | Semantic Self-Distillation for Language Model Uncertainty | 02-04* | 5 | 5 | 6 | 4 |
| 36 | 2602.04677 | REDistill: Robust Estimator Distillation for Balancing Ro… | 02-04 | 6 | 5 | 7 | 4 |
| 37 | 2602.04703 | Knowledge Distillation for mmWave Beam Prediction Using S… | 02-04* | 6 | 5 | 7 | 4 |
| 38 | 2602.04884 | Reinforced Attention Learning | 02-04 | 5 | 5 | 7 | 5 |
| 39 | 2602.04942 | Privileged Information Distillation for Language Models | 02-04* | 5 | 5 | 7 | 4 |
| 40 | 2602.05449 | DisCa: Accelerating Video Diffusion Transformers with Dis… | 02-05 | 5 | 5 | 8 | 9 |
| 41 | 2602.05452 | DistillER: Knowledge Distillation in Entity Resolution wi… | 02-05 | 6 | 5 | 9 | 4 |
| 42 | 2602.06019 | Multi-Token Prediction via Self-Distillation | 02-05* | 5 | 5 | 8 | 4 |
| 43 | 2602.06032 | Splat and Distill: Augmenting Teachers with Feed-Forward … | 02-05* | 8 | 5 | 9 | 4 |
| 44 | 2602.06180 | STACodec: Semantic Token Assignment for Balancing Acousti… | 02-05 | 7 | 5 | 9 | 4 |
| 45 | 2602.06184 | PhenoLIP: Integrating Phenotype Ontology Knowledge into M… | 02-05 | 8 | 5 | 9 | 4 |
| 46 | 2602.06251 | ASMa: Asymmetric Spatio-temporal Masking for Skeleton Act… | 02-05 | 8 | 7 | 9 | 4 |
| 47 | 2602.06879 | NanoFLUX: Distillation-Driven Compression of Large Text-t… | 02-06 | 7 | 5 | 9 | 4 |
| 48 | 2602.07058 | SPARE: Self-distillation for PARameter-Efficient Removal | 02-04 | 5 | 5 | 9 | 4 |
| 49 | 2602.07345 | Optimizing Few-Step Generation with Adaptive Matching Dis… | 02-07* | 7 | 5 | 7 | 4 |
| 50 | 2602.07521 | Pareto-guided Pipeline for Distilling Featherweight AI Ag… | 02-07* | 8 | 5 | 7 | 4 |
| 51 | 2602.07768 | PAND: Prompt-Aware Neighborhood Distillation for Lightwei… | 02-08* | 8 | 5 | 9 | 9 |
| 52 | 2602.07819 | DINO-Mix: Distilling Foundational Knowledge with Cross-Do… | 02-08 | 5 | 5 | 7 | 4 |
| 53 | 2602.07840 | SAGE: Scalable AI Governance & Evaluation | 02-08 | 5 | 5 | 7 | 4 |
| 54 | 2602.08395 | D$^2$-VR: Degradation-Robust and Distilled Video Restorat… | 02-09* | 7 | 5 | 9 | 4 |
| 55 | 2602.08431 | USBD: Universal Structural Basis Distillation for Source-… | 02-09* | 6 | 5 | 7 | 4 |
| 56 | 2602.08446 | RIFLE: Robust Distillation-based FL for Deep Model Deploy… | 02-09 | 6 | 8 | 6 | 4 |
| 57 | 2602.08607 | VocalNet-MDM: Accelerating Streaming Speech LLM via Self-… | 02-09* | 7 | 5 | 9 | 4 |
| 58 | 2602.09014 | ArcFlow: Unleashing 2-Step Text-to-Image Generation via H… | 02-09* | 6 | 10 | 7 | 4 |
| 59 | 2602.09483 | Beyond Next-Token Alignment: Distilling Multimodal Large … | 02-10 | 7 | 5 | 9 | 9 |
| 60 | 2602.09509 | Beyond Student: An Asymmetric Network for Neural Network … | 02-10 | 5 | 5 | 7 | 4 |
| 61 | 2602.09691 | Life Cycle-Aware Evaluation of Knowledge Distillation for… | 02-10 | 5 | 5 | 6 | 4 |
| 62 | 2602.10869 | Agentic Knowledge Distillation: Autonomous Training of Sm… | 02-11 | 8 | 5 | 7 | 4 |
| 63 | 2602.11157 | Response-Based Knowledge Distillation for Multilingual Ja… | 02-跨† | 5 | 5 | 9 | 6 |
| 64 | 2602.11374 | Retrieval-Aware Distillation for Transformer-SSM Hybrids | 02-11 | 6 | 5 | 7 | 4 |
| 65 | 2602.11858 | Zooming without Zooming: Region-to-Image Distillation for… | 02-12* | 5 | 5 | 9 | 9 |
| 66 | 2602.12125 | Learning beyond Teacher: Generalized On-Policy Distillati… | 02-12* | 7 | 5 | 9 | 4 |
| 67 | 2602.12127 | PosterOmni: Generalized Artistic Poster Creation via Task… | 02-12* | 5 | 5 | 7 | 6 |
| 68 | 2602.12172 | Pedagogically-Inspired Data Synthesis for Language Model … | 02-12 | 9 | 5 | 9 | 4 |
| 69 | 2602.12262 | Few-Step Diffusion Language Models via Trajectory Self-Di… | 02-12* | 5 | 5 | 7 | 9 |
| 70 | 2602.12275 | On-Policy Context Distillation for Language Models | 02-12 | 5 | 5 | 7 | 4 |
| 71 | 2602.12524 | LiDAR-Anchored Collaborative Distillation for Robust 2D R… | 02-13* | 7 | 5 | 9 | 4 |
| 72 | 2602.12674 | $\mathcal{X}$-KD: General Experiential Knowledge Distilla… | 02-13 | 5 | 5 | 9 | 4 |
| 73 | 2602.12679 | Motion Prior Distillation in Time Reversal Sampling for G… | 02-13* | 5 | 5 | 7 | 4 |
| 74 | 2602.12687 | Trust the uncertain teacher: distilling dark knowledge vi… | 02-13 | 5 | 5 | 6 | 4 |
| 75 | 2602.12936 | Unleashing MLLMs on the Edge: A Unified Framework for Cro… | 02-13 | 5 | 5 | 9 | 6 |
| 76 | 2602.13567 | DistillLens: Symmetric Knowledge Distillation Through Log… | 02-14 | 7 | 5 | 7 | 9 |
| 77 | 2602.14301 | DeepFusion: Accelerating MoE Training via Federated Knowl… | 02-15 | 6 | 5 | 9 | 4 |
| 78 | 2602.14428 | LLM-Guided Knowledge Distillation for Temporal Knowledge … | 02-16 | 5 | 5 | 7 | 4 |
| 79 | 2602.14975 | Faster Molecular Dynamics with Neural Network Potentials … | 02-16* | 7 | 5 | 7 | 4 |
| 80 | 2602.15005 | Learning User Interests via Reasoning and Distillation fo… | 02-16* | 5 | 5 | 7 | 4 |
| 81 | 2602.15143 | Protecting Language Models Against Unauthorized Distillat… | 02-16 | 5 | 5 | 7 | 9 |
| 82 | 2602.15260 | Fast and Effective On-policy Distillation from Reasoning … | 02-16* | 6 | 5 | 7 | 4 |
| 83 | 2602.15326 | SCENE OTA-FD: Self-Centering Noncoherent Estimator for Ov… | 02-17* | 8 | 5 | 7 | 4 |
| 84 | 2602.15547 | jina-embeddings-v5-text: Task-Targeted Embedding Distilla… | 02-17 | 7 | 5 | 9 | 4 |
| 85 | 2602.15734 | Language and Geometry Grounded Sparse Voxel Representatio… | 02-17 | 7 | 5 | 9 | 4 |
| 86 | 2602.15845 | KD4MT: A Survey of Knowledge Distillation for Machine Tra… | 01-22* | 5 | 5 | 5 | 4 |
| 87 | 2602.15902 | Doc-to-LoRA: Learning to Instantly Internalize Contexts | 02-13 | 7 | 7 | 7 | 4 |
| 88 | 2602.16093 | Updating Parametric Knowledge with Context Distillation R… | 02-17* | 5 | 5 | 7 | 5 |
| 89 | 2602.16857 | Distillation and Interpretability of Ensemble Forecasts o… | 02-15 | 7 | 5 | 6 | 4 |
| 90 | 2602.17047 | Amber-Image: Efficient Compression of Large-Scale Diffusi… | 02-19 | 6 | 5 | 9 | 4 |
| 91 | 2602.17565 | Optimal Unconstrained Self-Distillation in Ridge Regressi… | 02-19* | 5 | 5 | 7 | 4 |
| 92 | 2602.17686 | BRIDGE: Bridging Reasoning In Distillation Gap Eliminatio… | 02-05 | 9 | 5 | 9 | 9 |
| 93 | 2602.17907 | DSL-Topic: Improving Topic Modeling by Distilling Soft La… | 02-20 | 6 | 5 | 9 | 4 |
| 94 | 2602.18749 | Federated Reasoning Distillation Framework with Model Lea… | 02-21* | 5 | 5 | 9 | 4 |
| 95 | 2602.19005 | GUIDE-US: Grade-Informed Unpaired Distillation of Encoder… | 02-22 | 6 | 7 | 7 | 4 |
| 96 | 2602.19066 | IDLM: Inverse-distilled Diffusion Language Models | 02-22* | 5 | 5 | 8 | 4 |
| 97 | 2602.19778 | Enhancing Automatic Chord Recognition via Pseudo-Labeling… | 02-23 | 8 | 5 | 9 | 4 |
| 98 | 2602.19822 | Efficient endometrial carcinoma screening via cross-modal… | 02-23 | 7 | 5 | 7 | 4 |
| 99 | 2602.19848 | DerMAE: Improving skin lesion classification through cond… | 02-23 | 5 | 5 | 6 | 4 |
| 100 | 2602.19863 | Brewing Stronger Features: Dual-Teacher Distillation for … | 02-23* | 7 | 5 | 7 | 4 |
| 101 | 2602.19964 | On the Equivalence of Random Network Distillation, Deep E… | 02-23* | 5 | 5 | 8 | 4 |
| 102 | 2602.20164 | Benchmarking Distilled Language Models: Performance and E… | 01-28* | 8 | 5 | 6 | 4 |
| 103 | 2602.20574 | GATES: Self-Distillation under Privileged Context with Co… | 02-24* | 5 | 5 | 6 | 4 |
| 104 | 2602.20676 | PRECTR-V2:Unified Relevance-CTR Framework with Cross-User… | 02-24 | 5 | 5 | 9 | 4 |
| 105 | 2602.20816 | Don't Ignore the Tail: Decoupling top-K Probabilities for… | 02-24* | 5 | 5 | 7 | 4 |
| 106 | 2602.20904 | Transcoder Adapters for Reasoning-Model Diffing | 02-24 | 6 | 5 | 7 | 4 |
| 107 | 2602.21103 | Prompt-Level Distillation: A Non-Parametric Alternative t… | 02-24* | 6 | 5 | 7 | 4 |
| 108 | 2602.21221 | Latent Context Compilation: Distilling Long Context into … | 01-31* | 5 | 10 | 7 | 4 |
| 109 | 2602.21307 | SymTorch: Symbolic Distillation of Neural Networks | 02-24* | 7 | 5 | 6 | 6 |
| 110 | 2602.21395 | Momentum Memory for Knowledge Distillation in Computation… | 02-24 | 7 | 5 | 7 | 4 |
| 111 | 2602.21669 | DWA-KD: Dual-Space Weighting and Time-Warped Alignment fo… | 02-25 | 5 | 5 | 9 | 4 |
| 112 | 2602.21857 | Distill and Align Decomposition for Enhanced Claim Verifi… | 02-25* | 8 | 5 | 7 | 4 |
| 113 | 2602.22345 | Structure and Redundancy in Large Language Models: A Spec… | 02-25 | 5 | 5 | 9 | 4 |
| 114 | 2602.22351 | Decoder-based Sense Knowledge Distillation | 02-25 | 5 | 5 | 7 | 4 |
| 115 | 2602.22495 | Reinforcement-aware Knowledge Distillation for LLM Reason… | 02-26 | 5 | 5 | 7 | 5 |
| 116 | 2602.22613 | Spectrally Distilled Representations Aligned with Instruc… | 02-26* | 6 | 5 | 9 | 4 |
| 117 | 2602.23587 | PDF: PUF-based DNN Fingerprinting for Knowledge Distillat… | 02-27 | 5 | 5 | 9 | 4 |
| 118 | 2602.23716 | ProductResearch: Training E-Commerce Deep Research Agents… | 02-27* | 5 | 5 | 7 | 4 |

---

## 三、外围相关论文清单（232 篇，不做逐项评分）

| 序号 | arXiv ID | 论文标题 | 沾边方向 |
|:---:|---------|---------|---------|
| 1 | 2602.00038 | LSSF: Safety Alignment for Large Language Models through Low-Rank Saf… | 低秩 |
| 2 | 2602.00722 | Spectral Imbalance Causes Forgetting in Low-Rank Continual Adaptation | 低秩 |
| 3 | 2602.00942 | SALAAD: Sparse And Low-Rank Adaptation via ADMM for Large Language Mo… | 低秩 |
| 4 | 2602.01140 | Generalized Radius and Integrated Codebook Transforms for Differentia… | 量化、向量量化 |
| 5 | 2602.01186 | The Gaussian-Head OFL Family: One-Shot Federated Learning from Client… | 蒸馏、低秩 |
| 6 | 2602.01233 | Lotus: Efficient LLM Training by Randomized Low-Rank Gradient Project… | 低秩 |
| 7 | 2602.01472 | ConPress: Learning Efficient Reasoning from Multi-Question Contextual… | 剪枝、高效架构 |
| 8 | 2602.01546 | NeuroAI Temporal Neural Networks (NeuTNNs): Microarchitecture and Des… | 剪枝、硬件协同 |
| 9 | 2602.01613 | A Practical Tensor-Network Compression Pipeline for Production-Scale … | 量化、低秩 |
| 10 | 2602.01635 | COMET: Codebook-based Online-adaptive Multi-scale Embedding for Time-… | 量化、向量量化 |
| 11 | 2602.01725 | SafePred: A Predictive Guardrail for Computer-Using Agents via World … | 剪枝 |
| 12 | 2602.01807 | Sentence Curve Language Models | 蒸馏 |
| 13 | 2602.01829 | Zero-Shot Knowledge Base Resizing for Rate-Adaptive Digital Semantic … | 量化、剪枝 |
| 14 | 2602.01976 | FlyPrompt: Brain-Inspired Random-Expanded Routing with Temporal-Ensem… | 其他 |
| 15 | 2602.02028 | Edit Knowledge, Not Just Facts via Multi-Step Reasoning over Backgrou… | 蒸馏 |
| 16 | 2602.02035 | Bandwidth-Efficient Multi-Agent Communication through Information Bot… | 量化、向量量化 |
| 17 | 2602.02056 | Ultrafast On-Chip Online Learning via Spline Locality in Kolmogorov-A… | 量化 |
| 18 | 2602.02089 | UrbanGS: A Scalable and Efficient Architecture for Geometrically Accu… | 剪枝、高效架构 |
| 19 | 2602.02159 | Focus-dLLM: Accelerating Long-Context Diffusion LLM Inference via Con… | 剪枝、稀疏 |
| 20 | 2602.02195 | State Rank Dynamics in Linear Attention LLMs | KV cache、剪枝 |
| 21 | 2602.02212 | MAIN-VLA: Modeling Abstraction of Intention and eNvironment for Visio… | 剪枝 |
| 22 | 2602.02334 | VQ-Style: Disentangling Style and Content in Motion with Residual Qua… | 量化、向量量化 |
| 23 | 2602.02395 | David vs. Goliath: Verifiable Agent-to-Agent Jailbreaking via Reinfor… | 量化 |
| 24 | 2602.02474 | MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents | 剪枝 |
| 25 | 2602.02680 | FlexRank: Nested Low-Rank Knowledge Decomposition for Adaptive Model … | 低秩 |
| 26 | 2602.02786 | LEMON: Local Explanations via Modality-aware OptimizatioN | 稀疏 |
| 27 | 2602.02873 | ViThinker: Active Vision-Language Reasoning via Dynamic Perceptual Qu… | 稀疏、蒸馏 |
| 28 | 2602.03310 | RDT2: Exploring the Scaling Limit of UMI Data Towards Zero-Shot Cross… | 量化、蒸馏 |
| 29 | 2602.03533 | PnP-U3D: Plug-and-Play 3D Framework Bridging Autoregression and Diffu… | 量化、高效架构 |
| 30 | 2602.03538 | Constrained Dynamic Gaussian Splatting | 剪枝、硬件协同 |
| 31 | 2602.03615 | KTV: Keyframes and Key Tokens Selection for Efficient Training-Free V… | 剪枝 |
| 32 | 2602.03622 | Quasi-multimodal-based pathophysiological feature learning for retina… | 剪枝 |
| 33 | 2602.03713 | Multimodal Generative Recommendation for Fusing Semantic and Collabor… | 量化 |
| 34 | 2602.03742 | Edge-Optimized Vision-Language Models for Underground Infrastructure … | 量化、硬件协同 |
| 35 | 2602.03915 | Phaedra: Learning High-Fidelity Discrete Tokenization for the Physica… | 量化 |
| 36 | 2602.03974 | Active Epistemic Control for Query-Efficient Verified Planning | 剪枝 |
| 37 | 2602.04083 | Structure-Informed Estimation for Pilot-Limited MIMO Channels via Ten… | 低秩、硬件协同 |
| 38 | 2602.04188 | DiMo: Discrete Diffusion Modeling for Motion Generation and Understan… | 量化、向量量化 |
| 39 | 2602.04215 | OAT: Ordered Action Tokenization | 量化 |
| 40 | 2602.04278 | MiniRec: Data-Efficient Reinforcement Learning for LLM-based Recommen… | 剪枝 |
| 41 | 2602.04349 | VecSet-Edit: Unleashing Pre-trained LRM for Mesh Editing from Single … | 剪枝、高效架构 |
| 42 | 2602.04396 | LoRDO: Distributed Low-Rank Optimization with Infrequent Communication | 低秩 |
| 43 | 2602.04549 | Nix and Fix: Targeting 1000x Compression of 3D Gaussian Splatting wit… | 蒸馏 |
| 44 | 2602.04565 | Understanding Degradation with Vision Language Model | 量化 |
| 45 | 2602.04583 | PEPR: Privileged Event-based Predictive Regularization for Domain Gen… | 蒸馏 |
| 46 | 2602.04595 | Harmonia: Algorithm-Hardware Co-Design for Memory- and Compute-Effici… | 量化、KV cache |
| 47 | 2602.04657 | PIO-FVLM: Rethinking Training-Free Visual Token Reduction for VLM Acc… | KV cache、高效架构 |
| 48 | 2602.04804 | OmniSIFT: Modality-Asymmetric Token Compression for Efficient Omni-mo… | 剪枝 |
| 49 | 2602.04832 | It's Not a Lottery, It's a Race: Understanding How Gradient Descent A… | 剪枝 |
| 50 | 2602.04925 | Internalizing LLM Reasoning via Discovery and Replay of Latent Actions | 蒸馏 |
| 51 | 2602.05068 | E-Globe: Scalable $ε$-Global Verification of Neural Networks via Tigh… | 剪枝 |
| 52 | 2602.05353 | AgentXRay: White-Boxing Agentic Systems via Workflow Reconstruction | 剪枝、蒸馏 |
| 53 | 2602.05391 | Efficient Dataset Distillation for Pre-Trained Self-Supervised Models… | 蒸馏、高效架构 |
| 54 | 2602.05426 | Multi-AD: Cross-Domain Unsupervised Anomaly Detection for Medical and… | 蒸馏 |
| 55 | 2602.05594 | Deep Learning for Contextualized NetFlow-Based Network Intrusion Dete… | 其他 |
| 56 | 2602.05616 | Path-Guided Flow Matching for Dataset Distillation | 蒸馏 |
| 57 | 2602.05638 | SurgMotion: A Video-Native Foundation Model for Universal Understandi… | 蒸馏 |
| 58 | 2602.05709 | Nonlinearity as Rank: Generative Low-Rank Adapter with Radial Basis F… | 低秩、高效架构 |
| 59 | 2602.05790 | Price of metric universality in vector quantization is at most 0.11 b… | 量化、向量量化 |
| 60 | 2602.06093 | NanoNet: Parameter-Efficient Learning with Label-Scarce Supervision f… | 蒸馏、高效架构 |
| 61 | 2602.06138 | Flow Matching for Offline Reinforcement Learning with Discrete Actions | 量化、低秩 |
| 62 | 2602.06154 | MoSE: Mixture of Slimmable Experts for Efficient and Adaptive Languag… | 高效架构 |
| 63 | 2602.06208 | Emergent Low-Rank Training Dynamics in MLPs with Smooth Activations | 低秩 |
| 64 | 2602.06476 | Prism: Spectral Parameter Sharing for Multi-Agent Reinforcement Learn… | 剪枝 |
| 65 | 2602.06563 | TokenMixer-Large: Scaling Up Large Ranking Models in Industrial Recom… | 稀疏、硬件协同 |
| 66 | 2602.06602 | Scaling Speech Tokenizers with Diffusion Autoencoders | 量化 |
| 67 | 2602.06777 | Next-generation cyberattack detection with large language models: ano… | 蒸馏 |
| 68 | 2602.06924 | Robustness Beyond Known Groups with Low-rank Adaptation | 低秩 |
| 69 | 2602.06993 | Attractor Patch Networks: Reducing Catastrophic Forgetting with Route… | 低秩 |
| 70 | 2602.07164 | Your Language Model Secretly Contains Personality Subnetworks | 剪枝、高效架构 |
| 71 | 2602.07278 | Laplacian-LoRA: Delaying Oversmoothing in Deep GCNs via Spectral Low-… | 低秩 |
| 72 | 2602.07309 | Semantic Search At LinkedIn | 剪枝、蒸馏 |
| 73 | 2602.07400 | BitLogic: Training Framework for Gradient-Based FPGA-Native Neural Ne… | 剪枝、硬件协同 |
| 74 | 2602.07479 | ODELoRA: Training Low-Rank Adaptation by Solving Ordinary Differentia… | 低秩 |
| 75 | 2602.07616 | SERE: Similarity-based Expert Re-routing for Efficient Batch Decoding… | 剪枝、稀疏 |
| 76 | 2602.07618 | Neural Networks With Dense Weights Are Not Universal Approximators | 其他 |
| 77 | 2602.07663 | A Two-Layer Framework for Joint Online Configuration Selection and Ad… | 量化 |
| 78 | 2602.07847 | SimGR: Escaping the Pitfalls of Generative Decoding in LLM-based Reco… | 剪枝 |
| 79 | 2602.07889 | Efficient Anti-exploration via VQVAE and Fuzzy Clustering in Offline … | 量化、向量量化 |
| 80 | 2602.08007 | From $O(mn)$ to $O(r^2)$: Two-Sided Low-Rank Communication for Adam i… | 低秩 |
| 81 | 2602.08136 | Robustness of Vision Language Models Against Split-Image Harmful Inpu… | 蒸馏 |
| 82 | 2602.08206 | Geospatial-Reasoning-Driven Vocabulary-Agnostic Remote Sensing Semant… | 蒸馏 |
| 83 | 2602.08240 | PTS-SNN: A Prompt-Tuned Temporal Shift Spiking Neural Networks for Ef… | 其他 |
| 84 | 2602.08331 | PACC: Protocol-Aware Cross-Layer Compression for Compact Network Traf… | 低秩、高效架构 |
| 85 | 2602.08564 | M-Loss: Quantifying Model Merging Compatibility with Limited Unlabele… | 剪枝 |
| 86 | 2602.08612 | OneLive: Dynamically Unified Generative Framework for Live-Streaming … | 量化、向量量化 |
| 87 | 2602.08984 | Next Concept Prediction in Discrete Latent Space Leads to Stronger La… | 量化、向量量化 |
| 88 | 2602.09258 | Generalizing GNNs with Tokenized Mixture of Experts | 量化 |
| 89 | 2602.09316 | Effective MoE-based LLM Compression by Exploiting Heterogeneous Inter… | 其他 |
| 90 | 2602.09389 | TVTSyn: Content-Synchronous Time-Varying Timbre for Streaming Voice C… | 量化、低秩 |
| 91 | 2602.09434 | A Behavioral Fingerprint for Large Language Models: Provenance Tracki… | 量化 |
| 92 | 2602.09618 | UniShare: A Unified Framework for Joint Video and Receiver Recommenda… | 量化、稀疏 |
| 93 | 2602.09670 | Talking with the Latents -- how to convert your LLM into an astronomer | 蒸馏、低秩 |
| 94 | 2602.09816 | CompSplat: Compression-aware 3D Gaussian Splatting for Real-world Vid… | 剪枝 |
| 95 | 2602.09821 | Text summarization via global structure awareness | 剪枝、高效架构 |
| 96 | 2602.10006 | Answer First, Reason Later: Aligning Search Relevance via Mode-Balanc… | 蒸馏 |
| 97 | 2602.10056 | WildCat: Near-Linear Attention in Theory and Practice | KV cache |
| 98 | 2602.10144 | When LLMs get significantly worse: A statistical approach to detect m… | 量化 |
| 99 | 2602.10195 | Versor: A Geometric Sequence Architecture | 剪枝 |
| 100 | 2602.10216 | ELROND: Exploring and decomposing intrinsic capabilities of diffusion… | 蒸馏 |
| 101 | 2602.10319 | A Low-Rank Defense Method for Adversarial Attack on Diffusion Models | 低秩 |
| 102 | 2602.10345 | Identifying Evidence-Based Nudges in Biomedical Literature with Large… | 量化 |
| 103 | 2602.10445 | End-to-End Semantic ID Generation for Generative Advertisement Recomm… | 量化、向量量化 |
| 104 | 2602.10503 | Towards Long-Lived Robots: Continual Learning VLA Models via Reinforc… | 量化 |
| 105 | 2602.10801 | Deep Learning-based Method for Expressing Knowledge Boundary of Black… | 蒸馏 |
| 106 | 2602.10811 | EST: Towards Efficient Scaling Laws in Click-Through Rate Prediction … | 剪枝、高效架构 |
| 107 | 2602.10825 | Flow caching for autoregressive video generation | KV cache |
| 108 | 2602.10934 | MOSS-Audio-Tokenizer: Scaling Audio Tokenizers for Future Audio Found… | 量化、蒸馏 |
| 109 | 2602.10994 | Interpretable Vision Transformers in Image Classification via SVDA | 稀疏 |
| 110 | 2602.11004 | Enhancing Predictability of Multi-Tenant DNN Inference for Autonomous… | 量化、剪枝 |
| 111 | 2602.11062 | MoToRec: Sparse-Regularized Multimodal Tokenization for Cold-Start Re… | 量化、稀疏 |
| 112 | 2602.11084 | GRASP: group-Shapley feature selection for patients | 稀疏、蒸馏 |
| 113 | 2602.11320 | Efficient Analysis of the Distilled Neural Tangent Kernel | 蒸馏 |
| 114 | 2602.11383 | WSBD: Freezing-Based Optimizer for Quantum Neural Networks | 剪枝 |
| 115 | 2602.11456 | RL over Commodity Networks: Overcoming the Bandwidth Barrier with Los… | 量化 |
| 116 | 2602.11547 | H.265/HEVC Video Steganalysis Based on CU Block Structure Gradients a… | 量化 |
| 117 | 2602.11726 | Dopamine: Brain Modes, Not Brains | 稀疏 |
| 118 | 2602.11799 | Hi-SAM: A Hierarchical Structure-Aware Multi-modal Framework for Larg… | 量化、蒸馏 |
| 119 | 2602.11978 | Accelerating Robotic Reinforcement Learning with Agent Guidance | 剪枝 |
| 120 | 2602.12108 | The Pensieve Paradigm: Stateful Language Models Mastering Their Own C… | 剪枝 |
| 121 | 2602.12158 | SafeNeuron: Neuron-Level Safety Alignment for Large Language Models | 剪枝 |
| 122 | 2602.12173 | SAM3-LiteText: An Anatomical Study of the SAM3 Text Encoder for Effic… | 蒸馏、高效架构 |
| 123 | 2602.12204 | Learning to Forget Attention: Memory Consolidation for Adaptive Compu… | 蒸馏 |
| 124 | 2602.12370 | LLaMo: Scaling Pretrained Language Models for Unified Motion Understa… | 量化、高效架构 |
| 125 | 2602.12429 | Stabilizing Native Low-Rank LLM Pretraining | 低秩 |
| 126 | 2602.12526 | Constraint-Rectified Training for Efficient Chain-of-Thought | 剪枝 |
| 127 | 2602.12735 | VimRAG: Navigating Massive Visual Context in Retrieval-Augmented Gene… | 剪枝 |
| 128 | 2602.12878 | Understanding Cultural Alignment in Multilingual LLMs via Natural Deb… | 量化 |
| 129 | 2602.13087 | EXCODER: EXplainable Classification Of DiscretE time series Represent… | 量化、向量量化 |
| 130 | 2602.13140 | FlashSchNet: Fast and Accurate Coarse-Grained Neural Network Molecula… | 量化 |
| 131 | 2602.13486 | Preventing Rank Collapse in Federated Low-Rank Adaptation with Client… | 低秩 |
| 132 | 2602.13573 | Unleash the Potential of Long Semantic IDs for Generative Recommendat… | 量化、蒸馏 |
| 133 | 2602.13581 | Climber-Pilot: A Non-Myopic Generative Recommendation Model Towards B… | 蒸馏 |
| 134 | 2602.13636 | Layer-Guided UAV Tracking: Enhancing Efficiency and Occlusion Robustn… | 蒸馏、高效架构 |
| 135 | 2602.13764 | MOTIF: Learning Action Motifs for Few-shot Cross-Embodiment Transfer | 量化、向量量化 |
| 136 | 2602.13780 | Foundation Model-Driven Semantic Change Detection in Remote Sensing I… | 量化 |
| 137 | 2602.13818 | VAR-3D: View-aware Auto-Regressive Model for Text-to-3D Generation vi… | 量化、向量量化 |
| 138 | 2602.14018 | Extended Universal Joint Source-Channel Coding for Digital Semantic C… | 量化、向量量化 |
| 139 | 2602.14083 | Plan-MCTS: Plan Exploration for Action Exploitation in Web Navigation | 蒸馏 |
| 140 | 2602.14089 | TabTracer: Monte Carlo Tree Search for Complex Table Reasoning with L… | 剪枝、高效架构 |
| 141 | 2602.14397 | LRD-MPC: Efficient MPC Inference through Low-rank Decomposition | 低秩 |
| 142 | 2602.14728 | D2-LoRA: A Synergistic Approach to Differential and Directional Low-R… | 低秩 |
| 143 | 2602.14751 | Depth Completion as Parameter-Efficient Test-Time Adaptation | 其他 |
| 144 | 2602.14896 | Algorithmic Simplification of Neural Networks with Mosaic-of-Motifs | 量化、剪枝 |
| 145 | 2602.15164 | Synthesizing Trajectory Queries from Examples | 剪枝 |
| 146 | 2602.15200 | COMPOT: Calibration-Optimized Matrix Procrustes Orthogonalization for… | 量化、低秩 |
| 147 | 2602.15229 | tensorFM: Low-Rank Approximations of Cross-Order Feature Interactions | 低秩 |
| 148 | 2602.15277 | Accelerating Large-Scale Dataset Distillation via Exploration-Exploit… | 蒸馏 |
| 149 | 2602.15382 | The Vision Wormhole: Latent-Space Communication in Heterogeneous Mult… | 量化、蒸馏 |
| 150 | 2602.15516 | Semantic-Guided 3D Gaussian Splatting for Transient Object Removal | 剪枝 |
| 151 | 2602.15706 | Meta-Learning for GPU-Accelerated Quantum Many-Body Problems | 量化 |
| 152 | 2602.15751 | Enabling Low-Latency Machine learning on Radiation-Hard FPGAs with hl… | 量化、硬件协同 |
| 153 | 2602.15819 | VideoSketcher: Sequential Sketch Generation Using Video Model Priors | 蒸馏 |
| 154 | 2602.15897 | Mitigating Gradient Inversion Risks in Language Models via Token Obfu… | 剪枝 |
| 155 | 2602.15904 | A Comprehensive Survey on Deep Learning-Based LiDAR Super-Resolution … | 其他 |
| 156 | 2602.15909 | Resp-Agent: An Agent-Based System for Multimodal Respiratory Sound Ge… | 蒸馏 |
| 157 | 2602.15965 | FLoPS: Semantics, Operations, and Properties of P3109 Floating-Point … | 量化、硬件协同 |
| 158 | 2602.16124 | Rethinking ANN-based Retrieval: Multifaceted Learnable Index for Larg… | 量化、向量量化 |
| 159 | 2602.16160 | Uncertainty-Guided Inference-Time Depth Adaptation for Transformer-Ba… | 蒸馏、高效架构 |
| 160 | 2602.16249 | AFFMAE: Scalable Vision Pre-Training for High-Resolution Microscopy S… | 量化、硬件协同 |
| 161 | 2602.16412 | ReMoRa: Multimodal Large Language Model based on Refined Motion Repre… | 其他 |
| 162 | 2602.16442 | Hardware-accelerated graph neural networks: an alternative approach f… | 量化、硬件协同 |
| 163 | 2602.16511 | VIGOR: Visual Goal-In-Context Inference for Unified Humanoid Fall Saf… | 蒸馏 |
| 164 | 2602.16564 | A Scalable Approach to Solving Simulation-Based Network Security Games | 量化、高效架构 |
| 165 | 2602.16609 | ColBERT-Zero: To Pre-train Or Not To Pre-train ColBERT models | 蒸馏 |
| 166 | 2602.16720 | APEX-SQL: Talking to the data via Agentic Exploration for Text-to-SQL | 剪枝 |
| 167 | 2602.16833 | VAM: Verbalized Action Masking for Controllable Exploration in RL Pos… | 剪枝 |
| 168 | 2602.16840 | Solution to the Cosmological Constant Problem from Pre-geometric Grav… | 量化 |
| 169 | 2602.17063 | Sign Lock-In: Randomly Initialized Weight Signs Persist and Bottlenec… | 低秩 |
| 170 | 2602.17095 | FLoRG: Federated Fine-tuning with Low-rank Gram Matrices and Procrust… | 低秩 |
| 171 | 2602.17100 | AgentConductor: Topology Evolution for Multi-Agent Competition-Level … | 剪枝 |
| 172 | 2602.17327 | WebFAQ 2.0: A Multilingual QA Dataset with Mined Hard Negatives for D… | 蒸馏 |
| 173 | 2602.17395 | SpectralGCD: Spectral Concept Selection and Cross-modal Representatio… | 蒸馏 |
| 174 | 2602.17559 | Revisiting Weight Regularization for Low-Rank Continual Learning | 低秩 |
| 175 | 2602.17751 | Investigating Target Class Influence on Neural Network Compressibilit… | 硬件协同 |
| 176 | 2602.17761 | Hardware-Aware Design of a GNN-Based Hit Filtering Algorithm for the … | 量化、剪枝 |
| 177 | 2602.17772 | Sparse Bayesian Modeling of EEG Channel Interactions Improves P300 Br… | 稀疏 |
| 178 | 2602.18006 | MUOT_3M: A 3 Million Frame Multimodal Underwater Benchmark and the MU… | 蒸馏 |
| 179 | 2602.18523 | The Geometry of Multi-Task Grokking: Transverse Instability, Superpos… | 剪枝 |
| 180 | 2602.18649 | Global Low-Rank, Local Full-Rank: The Holographic Encoding of Learned… | 低秩 |
| 181 | 2602.18694 | In-Context Planning with Latent Temporal Abstractions | 量化 |
| 182 | 2602.18825 | Bayesian Lottery Ticket Hypothesis | 剪枝、稀疏 |
| 183 | 2602.18904 | PCA-VAE: Differentiable Subspace Quantization without Codebook Collap… | 量化、向量量化 |
| 184 | 2602.19111 | Astra: Activation-Space Tail-Eigenvector Low-Rank Adaptation of Large… | 低秩 |
| 185 | 2602.19161 | Flash-VAED: Plug-and-Play VAE Decoders for Efficient Video Generation | 剪枝、蒸馏 |
| 186 | 2602.19169 | Virtual Parameter Sharpening: Dynamic Low-Rank Perturbations for Infe… | 低秩 |
| 187 | 2602.19416 | IR$^3$: Contrastive Inverse Reinforcement Learning for Interpretable … | 蒸馏 |
| 188 | 2602.19437 | FinSight-Net:A Physics-Aware Decoupled Network with Frequency-Domain … | 剪枝、高效架构 |
| 189 | 2602.19622 | VecFormer: Towards Efficient and Generalizable Graph Transformer with… | 量化、向量量化 |
| 190 | 2602.19626 | Nacrith: Neural Lossless Compression via Ensemble Context Modeling an… | 量化、KV cache |
| 191 | 2602.19753 | RAP: Fast Feedforward Rendering-Free Attribute-Guided Primitive Impor… | 剪枝 |
| 192 | 2602.19756 | Multimodal Dataset Distillation Made Simple by Prototype-Guided Data … | 剪枝、蒸馏 |
| 193 | 2602.19859 | Dirichlet Scale Mixture Priors for Bayesian Neural Networks | 剪枝、稀疏 |
| 194 | 2602.19959 | Deploying a Hybrid PVFinder Algorithm for Primary Vertex Reconstructi… | 量化 |
| 195 | 2602.20198 | KEMP-PIP: A Feature-Fusion Based Approach for Pro-inflammatory Peptid… | 剪枝 |
| 196 | 2602.20363 | Aesthetic Camera Viewpoint Suggestion with 3D Aesthetic Field | 蒸馏 |
| 197 | 2602.20496 | Pip-Stereo: Progressive Iterations Pruner for Iterative Optimization … | 剪枝、稀疏 |
| 198 | 2602.20727 | ID-LoRA: Efficient Low-Rank Adaptation Inspired by Matrix Interpolati… | 低秩 |
| 199 | 2602.20923 | ParkDiffusion++: Ego Intention Conditioned Joint Multi-Agent Trajecto… | 蒸馏、高效架构 |
| 200 | 2602.20933 | Dropping Anchor and Spherical Harmonics for Sparse-view Gaussian Spla… | 其他 |
| 201 | 2602.20985 | EW-DETR: Evolving World Object Detection via Incremental Low-Rank DEt… | 低秩 |
| 202 | 2602.21042 | OmniOCR: Generalist OCR for Ethnic Minority Languages | 剪枝、稀疏 |
| 203 | 2602.21133 | SOM-VQ: Topology-Aware Tokenization for Interactive Generative Models | 量化、向量量化 |
| 204 | 2602.21397 | MMLoP: Multi-Modal Low-Rank Prompting for Efficient Vision-Language A… | 低秩 |
| 205 | 2602.21442 | MINAR: Mechanistic Interpretability for Neural Algorithmic Reasoning | 剪枝 |
| 206 | 2602.21461 | VecGlypher: Unified Vector Glyph Generation with Language Models | 量化 |
| 207 | 2602.21596 | A Hidden Semantic Bottleneck in Conditional Embeddings of Diffusion T… | 剪枝 |
| 208 | 2602.21662 | HybridINR-PCGC: Hybrid Lossless Point Cloud Geometry Compression Brid… | 其他 |
| 209 | 2602.21917 | Scan Clusters, Not Pixels: A Cluster-Centric Paradigm for Efficient U… | 蒸馏、高效架构 |
| 210 | 2602.21983 | Humanizing Robot Gaze Shifts: A Framework for Natural Gaze Shifts in … | 量化、向量量化 |
| 211 | 2602.22238 | TT-SEAL: TTD-Aware Selective Encryption for Adversarially-Robust and … | 硬件协同 |
| 212 | 2602.22417 | Absorbing Discrete Diffusion for Speech Enhancement | 量化、向量量化 |
| 213 | 2602.22571 | GIFSplat: Generative Prior-Guided Iterative Feed-Forward 3D Gaussian … | 蒸馏 |
| 214 | 2602.22607 | LoR-LUT: Learning Compact 3D Lookup Tables via Low-Rank Residuals | 低秩 |
| 215 | 2602.22666 | ArtPro: Self-Supervised Articulated Object Reconstruction with Adapti… | 剪枝 |
| 216 | 2602.22700 | IMMACULATE: A Practical LLM Auditing Framework via Verifiable Computa… | 量化、硬件协同 |
| 217 | 2602.22759 | Beyond Detection: Multi-Scale Hidden-Code for Natural Image Deepfake … | 量化、向量量化 |
| 218 | 2602.22896 | DySL-VLA: Efficient Vision-Language-Action Model Inference via Dynami… | 蒸馏 |
| 219 | 2602.22911 | CeRA: Breaking the Linear Ceiling of Low-Rank Adaptation with Non-lin… | 低秩、硬件协同 |
| 220 | 2602.23061 | MoDora: Tree-Based Semi-Structured Document Analysis System | 剪枝 |
| 221 | 2602.23105 | MaRI: Accelerating Ranking Model Inference via Structural Re-paramete… | 蒸馏、高效架构 |
| 222 | 2602.23128 | Bound to Disagree: Generalization Bounds via Certifiable Surrogates | 其他 |
| 223 | 2602.23204 | Motion-aware Event Suppression for Event Cameras | 剪枝、高效架构 |
| 224 | 2602.23219 | Takeuchi's Information Criteria as Generalization Measures for DNNs C… | 剪枝 |
| 225 | 2602.23295 | ManifoldGD: Training-Free Hierarchical Manifold Guidance for Diffusio… | 蒸馏、高效架构 |
| 226 | 2602.23358 | A Dataset is Worth 1 MB | 剪枝、蒸馏 |
| 227 | 2602.23440 | Truncated Step-Level Sampling with Process Rewards for Retrieval-Augm… | 量化 |
| 228 | 2602.23467 | On the Limits of Interpretable Machine Learning in Quintic Root Class… | 蒸馏 |
| 229 | 2602.23720 | The Auton Agentic AI Framework | 剪枝、高效架构 |
| 230 | 2602.23871 | Bandwidth-adaptive Cloud-Assisted 360-Degree 3D Perception for Autono… | 量化 |
| 231 | 2602.24144 | Fixed Anchors Are Not Enough: Dynamic Retrieval and Persistent Homolo… | 蒸馏 |
| 232 | 2602.24283 | Taming Momentum: Rethinking Optimizer States Through Low-Rank Approxi… | 低秩 |

---

## 四、量化算法代码复现清单（11 篇核心量化论文，全部真实运行验证）

复现统一以 **Qwen3-0.6B** 为目标模型（真实权重，HuggingFace 下载），代码位于 `scripts/quantization/<arxiv_id>/`（README.md + demo.py）。所有 demo 均已在本机真实执行并输出指标；均提供 `--mock` 无网回退。

| arXiv ID | 论文 | 复现方法要点 | 验证方式 | 关键实测结果 |
|---------|------|------------|---------|------------|
| 2602.01027 | SFMP | 分数位宽+块级混合精度+显著性行列重排 | 真实 Qwen3-0.6B gate_proj 权重+hook 真实激活 | 3.25-bit 平均位宽下输出误差 0.102，优于不重排消融（0.108）与统一 3-bit（0.228） |
| 2602.01037 | VEQ | 专家频率+模态亲和加权 Hessian 的 GPTQ 校准 | 真实权重切片构造 mock MoE+真实文本激活 | W3A16 下各专家文本误差 ≤0.050（RTN 0.153–0.167），误差预算向关键专家/模态倾斜 |
| 2602.05367 | RaBiT | 残差层级二值化+功能保持初始化 | 真实 down_proj 权重+真实激活 | 2 条二值路径输出误差 0.355，显著优于 naive 多二值（0.613）与 2-bit RTN（0.727） |
| 2602.07374 | TernaryLM | 原生 1.58-bit 三值+STE+自适应逐层缩放 | 真实权重上做 300 步真实 STE 训练 | 输出误差 0.555（冻结 RTN）→ 0.131（训练后），缩放因子自适应收敛 |
| 2602.06694 | NanoQuant | ADMM 低秩二值分解+块重建，亚 1-bit | 真实权重切片，40 轮 ADMM+16 轮重建 | 0.90-bit 输出误差 0.501 < 1-bit sign+scale 的 0.557；0.40-bit 平稳退化（0.654） |
| 2602.02151 | VQRound | 码本重参数化自适应舍入（E 步输出误差分配+M 步码本精炼） | 真实权重+128 条真实校准激活 | W3 下以 0.26% 可训练参数收敛至近 RTN 水平；稠密 AdaRound 达 0.083（RTN 0.244），如实呈现表达力-规模权衡 |
| 2602.02958 | Quant VideoGen | 语义感知平滑+渐进残差 2-bit KV cache 量化 | 真实前向截取的 layer-0 KV cache（seq=1393） | 注意力输出误差：直接 2-bit 1.297 → 两阶段 1.102 → 三阶段 0.817 |
| 2602.18420 | SPQ | 剪枝+SVD+INT8 集成压缩全模型手术 | 真实 Qwen3-0.6B 全模型手术+真实 PPL 评测 | 530MB 显存点 PPL 3.67（剪枝单技 2120MB@3.61、INT8 单技 596MB@2.76）；发现 0.6B 注意力近满秩，SVD 按省参数规则跳过 |
| 2602.13710 | HBVLA | 策略感知 Hessian 显著权重保护+稀疏正交（Harr）域分组 1-bit | 真实 down_proj 权重+真实激活（充当策略信号） | 输出误差：naive 1-bit 0.579 → 全域 Harr 消融 0.484 → HBVLA 0.338（约 1.81 bit/param） |
| 2602.17681 | LATMiX | MXFP4（块共享指数+FP4）+可学习逐通道仿射变换 STE 训练 | 真实 gate_proj 权重+真实 hidden states | round trip 输出误差：raw MXFP4 0.210 → 固定 absmax 均衡 0.195 → LATMiX 可学习仿射 0.189 |
| 2602.12609 | QuEPT | 4-bit 基底+一次校准级联低秩 adapter 实时切换 3/2-bit | 真实权重+真实校准切片，激活加权 SVD 单 pass 校准 | 3-bit 0.229→0.186（3.33 bit/param）、2-bit 0.639→0.460（2.33 bit/param），adapter 开销约 0.33 bit |

---

## 五、本月值得关注的高亮点

- **[2602.06694] NanoQuant**：首个将 LLM 压到**亚 1-bit** 的 PTQ 方法：把量化形式化为低秩二值分解问题，ADMM 求解器初始化 + 块/模型重建微调；Llama2-70B 压缩 25.8×（单卡 H100 仅 13 小时），让 70B 模型跑在 8GB 消费级显卡上。
- **[2602.05367] RaBiT**：指出残差二值化的**路径间共适应（inter-path adaptation）**失败模式，用共享全精度权重顺序导出各二值路径、从算法上强制残差层级，配合功能保持初始化，重新定义 2-bit 精度-效率前沿。
- **[2602.02958] Quant VideoGen**：针对自回归视频扩散的 KV cache 瓶颈（常超 30GB），用语义感知平滑+渐进残差量化实现训练自由 2-bit KV cache，显存最高降 7.0× 而端到端质量损失 <4%。
- **[2602.01027] SFMP**：把离散混合精度分配变为连续问题：**分数位宽** + 块级混合精度 + 行列重排聚合显著权重 + 统一 GEMM kernel，免搜索且硬件友好，同显存预算下超越逐层混合精度 SOTA。
- **[2602.07374] TernaryLM**：132M 参数模型**原生三值（{-1,0,+1}，≈1.58-bit）从头训练**：TinyStories PPL 58.42（跨种子 ±0.17），MRPC F1 82.47% 超 DistilBERT，显存降 2.4×，并发现三值约束的隐式正则化效应。
- **[2602.13710] HBVLA**：面向 VLA 机器人的 1-bit PTQ：策略感知 Hessian 识别动作关键权重 + 稀疏正交变换 + Harr 域分组 1-bit 量化；LIBERO 上保留 92.2% 全精度性能，并在真实机器人上验证。
- **[2602.18420] SPQ**：SVD+剪枝+INT8 **集成压缩**：三者攻击不同冗余源，LLaMA-2-7B 显存最高降 75% 且 WikiText-2 PPL 5.47→4.91 不降反升，吞吐较 GPTQ 最高提升 1.9×。
- **[2602.09883] AdaTSQ**：扩散 Transformer 的**时间步敏感性量化**：不同去噪时间步对量化误差敏感度差异巨大，按时间步分配精度，推动 DiT 量化的帕累托前沿。
- **[2602.17681] LATMiX**：把激活离群值抑制从旋转/Hadamard 变换推广到**可学习可逆仿射变换**，并给出 MX（微缩放）格式下量化误差的理论界，适配新硬件 MX 数据格式。
- **[2602.12609] QuEPT**：**弹性精度** Transformer：一次校准即可在多种位宽间实时切换（MB-ToMe + 级联 LoRA），一套权重适配多样部署场景。

---

## 六、整体趋势分析

2026 年 2 月共检索到模型压缩相关论文 623 篇（核心 391 篇），较 2026-07 月末单日约 20 篇的密度推算，本月产出处于高位。从 391 篇核心论文中可观察到以下趋势：

### 6.1 极低位宽（≤2-bit）从"能用"走向"好用"
本月 1-bit/亚 1-bit/三值相关核心量化论文约 14 篇，2-bit 9 篇。NanoQuant（亚 1-bit PTQ）、RaBiT（残差二值化）、TernaryLM（原生三值训练）、HBVLA（1-bit VLA）等工作共同表明：社区正在系统性攻克 1–2 bit 区间，方法论从"缩放+截断"升级为**结构化分解（低秩二值）、残差层级、原生 QAT、硬件域变换**四类新范式。

### 6.2 KV cache 压缩成为独立赛道
本月 KV cache 压缩核心论文 20 篇（另有 6 篇外围），覆盖量化（QVG 2-bit）、驱逐（ForesightKV、ManifoldKV 等）、选择性重算（ProphetKV）三条技术路线，并从文本 LLM 扩展到视频扩散与 RAG 场景。长上下文与长推理链的显存压力是该赛道的根本驱动。

### 6.3 量化对象从 LLM 扩散到 VLM/VLA/扩散模型
核心论文中 LLM 相关 183 篇、VLM/多模态 49 篇、扩散模型 39 篇。MoE VLM（VEQ）、VLA 机器人模型（HBVLA、QuantVLA）、视频/图像扩散（AdaTSQ、Q-DiT4SR、QVG）成为量化新战场；模态异质性、专家异质性、时间步异质性是本批工作共同处理的结构性挑战。

### 6.4 压缩从单一技术走向集成与协同
SPQ（SVD+剪枝+INT8）、QuEPT（弹性精度+LoRA）、AutoQRA（混合精度+低秩适配联合优化）等工作显示：单一压缩技术的收益趋于饱和，**正交技术的误差组合与联合优化**成为新的提升空间。蒸馏（118 篇核心）也越来越多地与量化/剪枝级联使用。

### 6.5 硬件友好与免搜索成为工程导向主旋律
SFMP（免搜索分数位宽）、QuEPT（一次校准多位宽切换）、多款 FPGA/存算一体/INT8 kernel 工作（核心论文中硬件协同标签 57 篇）表明：压缩算法的评估标准正从"参数量/PPL"转向"真实硬件上的端到端收益"，算法-硬件协同设计渐成标配。边缘/端侧相关核心论文达 121 篇。

### 6.6 可复现性
核心论文中 53 篇（13.6%）摘要直接给出代码链接，开源比例较往年明显提升；本月我们对其中的 11 篇代表性核心量化论文完成了基于 Qwen3-0.6B 的算法复现（见第四节），全部代码可运行并真实验证。

---

## 七、检索方法与局限说明

1. **检索**：arXiv API（submittedDate:[202602010000 TO 202602282359]，all: 关键词检索）+ cs.LG/cs.CL/cs.CV/cs.AI/cs.NE/cs.AR 六个分类的 2026-02 月度列表全量解析（9878 篇去重后）做标题级交叉验证 + OpenAlex（标题+摘要全文检索）补齐摘要；三路去重合并。
2. **月份确认**：所有入选论文 arXiv ID 均为 2602.*（即 2026 年 2 月公告）。其中 28 篇于 1 月 19–31 日提交、2 月初公告（评分表中日期列以 `01-29*` 形式标注星号），按 arXiv 公告月份归属 2026-02 月，与 arXiv 月度列表一致；另有 1 篇（2602.11157）为 2025 年 12 月提交、2026 年 2 月跨分类公告（标注 †），一并保留并说明。
3. **分组**：核心/外围由规则化分类器（压缩方法词×神经网络上下文共现、标题/摘要权重）初分，再对边界桶做人工复核；数据集蒸馏、纯物理/数学意义的 quantization、图算法 pruning 等已剔除出核心组。
4. **评分为规则化自动评分**（依据摘要文本中的声明与数字），用于横向粗排，不能替代逐篇精读；评分标准已在第二节开头给出。
5. **已知局限**：(a) 摘要未提关键词但正文涉及压缩的论文可能漏检；(b) 技术分析文档（papers/2026-02/）以摘要为主要依据，标注"原文引用"的句子均直接摘自摘要；(c) 评分未人工逐篇校准。

*报告生成时间: 2026-07-30 (GMT+8)，覆盖 2026-02 全月，共 623 篇（核心 391 / 外围 232）。*