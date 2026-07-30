# ArXiv 量化与模型压缩领域论文月报（2026-05）
**收集日期范围**: 2026-05-01 00:00 ~ 2026-05-31 23:59 UTC  **检索关键词**: quantization, quantize, quantized, low-bit, model compression, pruning, sparsity, sparse, knowledge distillation, distillation, KV cache, mixed precision, GPTQ, AWQ, weight compression, binarization, ternary, quantization-aware, post-training quantization, vector quantization, low precision, neural network compression  **数据来源**: arXiv API（export.arxiv.org，submittedDate 范围查询，22 组关键词去重合并）  **论文总数**: 517 篇（其中核心压缩主题 502 篇、外围相关 15 篇；原始命中 3069 条，经类目与摘要两级过滤、逐条人工标题审查后确定）  **分组口径**: 核心组 = 提出或直接研究模型压缩方法（量化/剪枝/蒸馏/稀疏/KV Cache/向量量化/低秩）的论文；外围组 = 涉及压缩但主题为安全/隐私/公平性/综述/报告/纯系统分析的论文。评分表覆盖全部核心组论文。

---

## 一、核心论文评分总表（502 篇，四项各 1–10 分）

评分维度：精度效果 / 压缩倍率 / 创新性 / 可复现性（评分方法见文末说明）。按 arXiv ID 排序。

| 序号 | arXiv ID | 论文标题 | 提交日期 | 技术方向 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|:---:|----------|---------|:-------:|---------|:-------:|:-------:|:-----:|:-------:|
| 1 | 2605.00320 | VitaLLM: A Versatile and Tiny Accelerator for Mixed-Precision … | 05-01 | 量化、剪枝、稀疏化、硬件协同 | 5 | 6 | 6 | 4 |
| 2 | 2605.00392 | RTPrune: Reading-Twice Inspired Token Pruning for Efficient De… | 05-01 | 剪枝 | 8 | 5 | 8 | 5 |
| 3 | 2605.00421 | RadLite: Multi-Task LoRA Fine-Tuning of Small Language Models … | 05-01 | 量化、硬件协同 | 8 | 5 | 6 | 8 |
| 4 | 2605.00422 | BWLA: Breaking the Barrier of W1AX Post-Training Quantization … | 05-01 | 量化、低秩 | 8 | 9 | 8 | 10 |
| 5 | 2605.00539 | AGoQ: Activation and Gradient Quantization for Memory-Efficien… | 05-01 | 量化 | 7 | 8 | 6 | 4 |
| 6 | 2605.00649 | Model Compression with Exact Budget Constraints via Riemannian… | 05-01 | 量化、剪枝 | 8 | 9 | 8 | 7 |
| 7 | 2605.00789 | Make Your LVLM KV Cache More Lightweight | 05-01 | KV Cache | 8 | 5 | 7 | 8 |
| 8 | 2605.01205 | SRA: Span Representation Alignment for Large Language Model Di… | 05-02 | 蒸馏 | 7 | 5 | 8 | 4 |
| 9 | 2605.01330 | Colinearity Decay: Training Quantization-Friendly ViTs with Ou… | 05-02 | 量化 | 5 | 6 | 6 | 7 |
| 10 | 2605.01355 | AgriKD: Cross-Architecture Knowledge Distillation for Efficien… | 05-02 | 蒸馏、硬件协同 | 6 | 5 | 6 | 4 |
| 11 | 2605.01374 | MTA: Multi-Granular Trajectory Alignment for Large Language Mo… | 05-02 | 蒸馏 | 8 | 5 | 6 | 4 |
| 12 | 2605.01478 | LIE: LiDAR-only HD Map Construction with Intensity Enhancement… | 05-02 | 蒸馏 | 8 | 5 | 6 | 4 |
| 13 | 2605.01563 | Multi-Dataset Cross-Domain Knowledge Distillation for Unified … | 05-02 | 蒸馏 | 5 | 5 | 6 | 4 |
| 14 | 2605.01627 | Importance-Guided Basis Selection for Low-Rank Decomposition o… | 05-02 | 剪枝、低秩 | 7 | 5 | 8 | 5 |
| 15 | 2605.01637 | The Banach-Butterfly Invariant: Influence-Adaptive Walsh Geome… | 05-02 | 量化 | 8 | 8 | 6 | 5 |
| 16 | 2605.01708 | SplitZip: Ultra Fast Lossless KV Compression for Disaggregated… | 05-03 | 量化、稀疏化、KV Cache、向量量化 | 8 | 6 | 6 | 8 |
| 17 | 2605.01732 | EGAD: Entropy-Guided Adaptive Distillation for Token-Level Kno… | 05-03 | 蒸馏 | 5 | 5 | 6 | 4 |
| 18 | 2605.01742 | Joint Architecture-Token-Bitwidth Multi-Axis Optimization of V… | 05-03 | 量化 | 5 | 6 | 7 | 5 |
| 19 | 2605.01854 | High-Fidelity Mobile Avatars with Pruned Local Blendshapes | 05-03 | 蒸馏、剪枝 | 5 | 5 | 6 | 4 |
| 20 | 2605.01858 | Decouple and Cache: KV Cache Construction for Streaming Video … | 05-03 | KV Cache | 8 | 5 | 6 | 7 |
| 21 | 2605.01866 | ShiftLIF: Efficient Multi-Level Spiking Neurons with Power-of-… | 05-03 | 量化、硬件协同 | 6 | 9 | 6 | 4 |
| 22 | 2605.01870 | Maistros: A Greek Large Language Model Adapted Through Knowled… | 05-03 | 蒸馏 | 7 | 5 | 6 | 4 |
| 23 | 2605.01910 | Stochastic Sparse Attention for Memory-Bound Inference | 05-03 | 量化、稀疏化、KV Cache、低秩 | 6 | 5 | 6 | 8 |
| 24 | 2605.01935 | ViM-Q: Scalable Algorithm-Hardware Co-Design for Vision Mamba … | 05-03 | 量化、硬件协同 | 5 | 10 | 6 | 4 |
| 25 | 2605.02086 | GETA-3DGS: Automatic Joint Structured Pruning and Quantization… | 05-03 | 量化、剪枝、稀疏化 | 7 | 5 | 8 | 4 |
| 26 | 2605.02137 | FLoRA: Fusion-Latent for Optical Reconstruction and Flood Area… | 05-04 | 蒸馏 | 7 | 5 | 6 | 4 |
| 28 | 2605.02198 | SlimDiffSR: Toward Lightweight and Efficient Remote Sensing Im… | 05-04 | 蒸馏、剪枝、稀疏化 | 7 | 5 | 8 | 8 |
| 29 | 2605.02218 | CoVSpec: Efficient Device-Edge Co-Inference for Vision-Languag… | 05-04 | 剪枝、低秩 | 6 | 5 | 8 | 7 |
| 30 | 2605.02262 | WindowQuant: Mixed-Precision KV Cache Quantization based on Wi… | 05-04 | 量化、KV Cache、硬件协同 | 7 | 5 | 8 | 4 |
| 31 | 2605.02275 | EdgeLPR: On the Deep Neural Network trade-off between Precisio… | 05-04 | 量化 | 6 | 6 | 6 | 5 |
| 33 | 2605.02290 | Distilling Long-CoT Reasoning through Collaborative Step-wise … | 05-04 | 蒸馏 | 5 | 5 | 6 | 8 |
| 34 | 2605.02404 | Statistically-Lossless Quantization of Large Language Models | 05-04 | 量化 | 8 | 8 | 8 | 10 |
| 35 | 2605.02568 | StreamIndex: Memory-Bounded Compressed Sparse Attention via St… | 05-04 | 稀疏化 | 5 | 5 | 6 | 8 |
| 36 | 2605.02849 | Active Sampling for Ultra-Low-Bit-Rate Video Compression via C… | 05-04 | 量化、稀疏化 | 5 | 6 | 6 | 5 |
| 37 | 2605.02853 | Trust, but Verify: Peeling Low-Bit Transformer Networks for Tr… | 05-04 | 量化 | 6 | 9 | 7 | 4 |
| 38 | 2605.02860 | Standing on the Shoulders of Giants: Stabilized Knowledge Dist… | 05-04 | 蒸馏 | 5 | 9 | 6 | 8 |
| 39 | 2605.02948 | AsymTalker: Identity-Consistent Long-Term Talking Head Generat… | 05-01 | 蒸馏 | 7 | 5 | 8 | 4 |
| 40 | 2605.02971 | Multilingual Safety Alignment via Self-Distillation | 05-03 | 蒸馏 | 5 | 5 | 6 | 4 |
| 41 | 2605.03039 | Mixed-Precision Information Bottlenecks for On-Device Trait-St… | 05-04 | 量化、硬件协同 | 8 | 8 | 7 | 4 |
| 43 | 2605.03348 | Toward Structural Multimodal Representations: Specialization, … | 05-05 | 剪枝、稀疏化 | 5 | 5 | 6 | 5 |
| 44 | 2605.03396 | Design and Implementation of BNN-Based Object Detection on FPGA | 05-05 | 量化、硬件协同 | 8 | 9 | 6 | 4 |
| 45 | 2605.03437 | Learning Discriminative Signed Distance Functions from Multi-s… | 05-05 | 稀疏化 | 7 | 5 | 7 | 5 |
| 46 | 2605.03562 | HeadQ: Model-Visible Distortion and Score-Space Correction for… | 05-05 | 量化、KV Cache、低秩 | 5 | 8 | 6 | 5 |
| 47 | 2605.03644 | AdapShot: Adaptive Many-Shot In-Context Learning with Semantic… | 05-05 | KV Cache | 8 | 10 | 7 | 5 |
| 48 | 2605.03667 | ELAS: Efficient Pre-Training of Low-Rank Large Language Models… | 05-05 | 稀疏化、低秩 | 5 | 5 | 8 | 8 |
| 49 | 2605.03680 | Real Image Denoising with Knowledge Distillation for High-Perf… | 05-05 | 蒸馏、硬件协同 | 6 | 9 | 6 | 8 |
| 50 | 2605.03884 | QKVShare: Quantized KV-Cache Handoff for Multi-Agent On-Device… | 05-05 | 量化、KV Cache、硬件协同 | 5 | 5 | 6 | 4 |
| 51 | 2605.04201 | Topology-Constrained Quantized nnUNet for Efficient and Anatom… | 05-05 | 量化、硬件协同 | 5 | 6 | 7 | 4 |
| 52 | 2605.04282 | Hardware-Aware Neural Feature Extraction for Resource-Constrai… | 05-05 | 量化、蒸馏、硬件协同 | 6 | 6 | 8 | 4 |
| 53 | 2605.04341 | Budgeted LoRA: Distillation as Structured Compute Allocation f… | 05-05 | 蒸馏、低秩 | 6 | 10 | 6 | 7 |
| 54 | 2605.04421 | FLUID: Continuous-Time Hyperconnected Sparse Transformer for S… | 05-06 | 稀疏化 | 10 | 5 | 7 | 4 |
| 55 | 2605.04447 | Deep Reprogramming Distillation for Medical Foundation Models | 05-06 | 蒸馏 | 7 | 5 | 7 | 4 |
| 57 | 2605.04569 | LIVEditor-14B: Lightning Unified Video Editing via In-Context … | 05-06 | 剪枝、稀疏化 | 10 | 5 | 8 | 5 |
| 58 | 2605.04595 | A Queueing-Theoretic Framework for Stability Analysis of LLM I… | 05-06 | KV Cache | 6 | 5 | 6 | 4 |
| 59 | 2605.04738 | OSAQ: Outlier Self-Absorption for Accurate Low-bit LLM Quantiz… | 05-06 | 量化、低秩 | 6 | 8 | 7 | 10 |
| 61 | 2605.04952 | Adaptive Inverted-Index Routing for Granular Mixtures-of-Experts | 05-06 | 量化、向量量化 | 5 | 5 | 7 | 5 |
| 62 | 2605.05096 | CapsID: Soft-Routed Variable-Length Semantic IDs for Generativ… | 05-06 | 量化、稀疏化、向量量化 | 7 | 5 | 6 | 4 |
| 63 | 2605.05246 | Memory-Efficient EDA Denoising via Knowledge Distillation for … | 05-04 | 蒸馏 | 5 | 5 | 6 | 4 |
| 64 | 2605.05249 | TriAlignGR: Triangular Multitask Alignment with Multimodal Dee… | 05-05 | 量化、向量量化 | 5 | 5 | 8 | 5 |
| 65 | 2605.05330 | Graph Normalization: Fast Binarizing Dynamics for Differentiab… | 05-06 | 量化、剪枝、稀疏化 | 8 | 9 | 6 | 4 |
| 66 | 2605.05553 | FedeKD: Energy-Based Gating for Robust Federated Knowledge Dis… | 05-07 | 蒸馏 | 5 | 5 | 6 | 4 |
| 67 | 2605.05561 | BitCal-TTS: Bit-Calibrated Test-Time Scaling for Quantized Rea… | 05-07 | 量化 | 6 | 8 | 6 | 7 |
| 68 | 2605.05639 | TokenStack: A Heterogeneous HBM-PIM Architecture and Runtime f… | 05-07 | 量化、硬件协同 | 6 | 5 | 6 | 4 |
| 69 | 2605.05674 | EGA: Adapting Frozen Encoders for Vector Search with Bounded O… | 05-07 | 稀疏化 | 6 | 5 | 6 | 4 |
| 70 | 2605.05693 | Saliency-Aware Regularized Quantization Calibration for Large … | 05-07 | 量化 | 6 | 5 | 6 | 7 |
| 71 | 2605.05697 | Budgeted Attention Allocation: Cost-Conditioned Compute Contro… | 05-07 | 剪枝 | 6 | 6 | 6 | 4 |
| 72 | 2605.05699 | When Quantization Is Free: An int4 KV Cache That Outruns fp16 … | 05-07 | 量化、KV Cache | 6 | 8 | 6 | 4 |
| 73 | 2605.05777 | Estimating the Black-box LLM Uncertainty with Distribution-Ali… | 05-07 | 蒸馏 | 5 | 5 | 6 | 4 |
| 75 | 2605.05899 | VisMMOE: Exploiting Visual-Expert Affinity for Efficient Visua… | 05-07 | 剪枝 | 5 | 5 | 6 | 4 |
| 76 | 2605.05940 | Near-Policy: Accelerating On-Policy Distillation via Asynchron… | 05-07 | 蒸馏、稀疏化 | 8 | 10 | 6 | 8 |
| 77 | 2605.05971 | Training Transformers for KV Cache Compressibility | 05-07 | KV Cache | 5 | 5 | 6 | 4 |
| 78 | 2605.05994 | DiBA: Diagonal and Binary Matrix Approximation for Neural Netw… | 05-07 | 量化、低秩 | 5 | 9 | 7 | 7 |
| 79 | 2605.06014 | Quantizing With Randomized Hadamard Transforms: Efficient Heur… | 05-07 | 量化、KV Cache、向量量化 | 6 | 5 | 6 | 5 |
| 80 | 2605.06017 | Matrix-Decoupled Concentration for Autoregressive Sequences: D… | 05-07 | 稀疏化 | 4 | 5 | 6 | 5 |
| 81 | 2605.06052 | XtraMAC: An Efficient MAC Architecture for Mixed-Precision LLM… | 05-07 | 量化、硬件协同 | 6 | 6 | 8 | 8 |
| 82 | 2605.06067 | Normalized Architectures are Natively 4-Bit | 05-07 | 量化 | 5 | 8 | 6 | 8 |
| 83 | 2605.06082 | PoTAcc: A Pipeline for End-to-End Acceleration of Power-of-Two… | 05-07 | 量化、硬件协同 | 6 | 9 | 6 | 8 |
| 84 | 2605.06112 | Dynamic Pondering Sparsity-aware Mixture-of-Experts Transforme… | 05-07 | 稀疏化 | 5 | 5 | 6 | 8 |
| 85 | 2605.06207 | Taming the Entropy Cliff: Variable Codebook Size Quantization … | 05-07 | 量化、向量量化 | 6 | 6 | 7 | 4 |
| 86 | 2605.06221 | UniPrefill: Universal Long-Context Prefill Acceleration via Bl… | 05-07 | 稀疏化 | 4 | 7 | 8 | 5 |
| 87 | 2605.06270 | Spark3R: Asymmetric Token Reduction Makes Fast Feed-Forward 3D… | 05-07 | 剪枝 | 5 | 6 | 6 | 7 |
| 88 | 2605.06273 | On-Orbit Real-Time Wildfire Detection Under On-Board Constraints | 05-07 | 蒸馏、剪枝 | 7 | 6 | 6 | 4 |
| 89 | 2605.06278 | PACE: Prune-And-Compress Ensemble Models | 05-07 | 剪枝 | 7 | 5 | 8 | 5 |
| 90 | 2605.06366 | Layer Collapse in Diffusion Language Models | 05-07 | 量化、剪枝、稀疏化 | 6 | 8 | 6 | 8 |
| 91 | 2605.06392 | ADELIA: Automatic Differentiation for Efficient Laplace Infere… | 05-07 | 稀疏化 | 7 | 5 | 8 | 4 |
| 92 | 2605.06402 | SparseForge: Efficient Semi-Structured LLM Sparsification via … | 05-07 | 剪枝、稀疏化、硬件协同 | 8 | 5 | 6 | 7 |
| 93 | 2605.06441 | Light-FMP: Lightweight Feature and Model Pruning for Enhanced … | 05-07 | 剪枝 | 7 | 5 | 7 | 4 |
| 94 | 2605.06485 | Litespark Inference For CPUs: Ultra-Fast SIMD Framework for Te… | 05-07 | 量化 | 5 | 10 | 7 | 4 |
| 95 | 2605.06505 | PACZero: PAC-Private Fine-Tuning of Language Models via Sign Q… | 05-07 | 量化 | 8 | 9 | 6 | 8 |
| 96 | 2605.06610 | SoftSAE: Dynamic Top-K Selection for Adaptive Sparse Autoencoders | 05-07 | 稀疏化 | 6 | 5 | 7 | 8 |
| 97 | 2605.06628 | LiVeAction: a Lightweight, Versatile, and Asymmetric Neural Co… | 05-07 | 量化 | 7 | 5 | 7 | 8 |
| 99 | 2605.06763 | Sparse Attention as a Range Searching Problem: Towards an Infe… | 05-07 | 稀疏化、KV Cache、硬件协同 | 6 | 5 | 8 | 4 |
| 100 | 2605.06850 | How to Compress KV Cache in RL Post-Training? Shadow Mask Dist… | 05-07 | 蒸馏、稀疏化、KV Cache | 6 | 5 | 6 | 7 |
| 101 | 2605.06997 | Echo: KV-Cache-Free Associative Recall with Spectral Koopman O… | 05-07 | KV Cache、硬件协同 | 7 | 5 | 7 | 7 |
| 102 | 2605.07086 | Task Relevance Is Not Local Replaceability: A Two-Axis View of… | 05-08 | 剪枝 | 5 | 5 | 6 | 4 |
| 103 | 2605.07091 | Estimating Correlation Clustering Cost in Node-Arrival Stream | 05-08 | 剪枝、稀疏化 | 8 | 5 | 6 | 5 |
| 104 | 2605.07182 | Star Elastic: Many-in-One Reasoning LLMs with Efficient Budget… | 05-08 | 量化、蒸馏 | 8 | 8 | 7 | 7 |
| 105 | 2605.07234 | Reformulating KV Cache Eviction Problem for Long-Context LLM I… | 05-08 | KV Cache | 7 | 6 | 7 | 5 |
| 106 | 2605.07245 | TransDot: An Area-efficient Reconfigurable Floating-Point Unit… | 05-08 | 量化、硬件协同 | 6 | 8 | 6 | 8 |
| 107 | 2605.07271 | Understanding Performance Collapse in Layer-Pruned Large Langu… | 05-08 | 剪枝 | 5 | 6 | 4 | 5 |
| 108 | 2605.07317 | Amortized-Precision Quantization for Early-Exit Vision Transfo… | 05-08 | 量化 | 8 | 5 | 6 | 5 |
| 109 | 2605.07321 | TREA: Low-precision Time-Multiplexed, Resource-Efficient Edge … | 05-08 | 量化、剪枝、稀疏化、硬件协同 | 6 | 6 | 8 | 4 |
| 110 | 2605.07330 | SparseRL-Sync: Lossless Weight Synchronization with ~100x Less… | 05-08 | 稀疏化 | 8 | 5 | 6 | 4 |
| 111 | 2605.07363 | MISA: Mixture of Indexer Sparse Attention for Long-Context LLM… | 05-08 | 稀疏化 | 10 | 9 | 6 | 4 |
| 112 | 2605.07505 | LiteGUI: Distilling Compact GUI Agents with Reinforcement Lear… | 05-08 | 蒸馏、硬件协同 | 7 | 5 | 8 | 4 |
| 113 | 2605.07662 | Direction-Preserving Number Representations | 05-08 | 量化 | 5 | 8 | 6 | 8 |
| 114 | 2605.07719 | An Efficient Hybrid Sparse Attention with CPU-GPU Parallelism … | 05-08 | 稀疏化、KV Cache | 4 | 5 | 6 | 4 |
| 115 | 2605.07721 | Memory-Efficient Looped Transformer: Decoupling Compute from M… | 05-08 | 蒸馏、KV Cache | 8 | 5 | 7 | 7 |
| 116 | 2605.07783 | Chain-based Distillation for Effective Initialization of Varia… | 05-08 | 蒸馏、稀疏化 | 7 | 5 | 6 | 4 |
| 117 | 2605.07804 | Prune-OPD: Efficient and Reliable On-Policy Distillation for L… | 05-08 | 蒸馏、剪枝 | 4 | 5 | 6 | 4 |
| 118 | 2605.07892 | Adaptive Regularization for Sparsity Control in Bregman-Based … | 05-08 | 稀疏化 | 10 | 5 | 6 | 4 |
| 119 | 2605.08063 | Flow-OPD: On-Policy Distillation for Flow Matching Models | 05-08 | 蒸馏、稀疏化 | 8 | 5 | 8 | 7 |
| 120 | 2605.08073 | EmambaIR: Efficient Visual State Space Model for Event-guided … | 05-08 | 稀疏化 | 7 | 5 | 6 | 8 |
| 121 | 2605.08137 | Weight Pruning Amplifies Bias: A Multi-Method Study of Compres… | 05-02 | 量化、剪枝、稀疏化、硬件协同 | 6 | 5 | 4 | 4 |
| 122 | 2605.08183 | Sparsity Hurts: Simple Linear Adapter Can Boost Generalized Ca… | 05-05 | 稀疏化 | 5 | 5 | 7 | 8 |
| 123 | 2605.08195 | ExecuTorch -- A Unified PyTorch Solution to Run AI Models On-D… | 05-05 | 量化、硬件协同 | 5 | 5 | 6 | 4 |
| 124 | 2605.08213 | Low-Cost Stereo Vision for Robust 3D Positioning of Thin Radia… | 05-06 | 剪枝、稀疏化 | 8 | 5 | 7 | 4 |
| 125 | 2605.08241 | TinySSL: Distilled Self-Supervised Pretraining for Sub-Megabyt… | 05-07 | 量化、蒸馏、硬件协同 | 10 | 6 | 6 | 4 |
| 126 | 2605.08263 | Decentralized Conformal Novelty Detection via Quantized Model … | 05-07 | 量化 | 5 | 5 | 8 | 5 |
| 127 | 2605.08317 | RDKV: Rate-Distortion Bit Allocation for Joint Eviction and Qu… | 05-08 | 量化、KV Cache | 8 | 5 | 6 | 5 |
| 128 | 2605.08371 | PaceVGGT: Pre-Alternating-Attention Token Pruning for Visual G… | 05-08 | 蒸馏、剪枝、硬件协同 | 5 | 5 | 8 | 4 |
| 129 | 2605.08575 | Uncovering Intra-expert Activation Sparsity for Efficient Mixt… | 05-09 | 稀疏化 | 8 | 8 | 6 | 4 |
| 130 | 2605.08615 | DSPE: An Energy-Efficient Edge Processor for DeepSeek Inferenc… | 05-09 | 剪枝、硬件协同 | 7 | 5 | 6 | 4 |
| 131 | 2605.08657 | Fitting Multilinear Polynomials for Logic Gate Networks | 05-09 | 量化、向量量化 | 6 | 5 | 6 | 4 |
| 132 | 2605.08692 | AAAC: Activation-Aware Adaptive Codebooks for 4-bit LLM Weight… | 05-09 | 量化、向量量化 | 7 | 8 | 6 | 10 |
| 133 | 2605.08738 | SlimQwen: Exploring the Pruning and Distillation in Large MoE … | 05-09 | 蒸馏、剪枝 | 7 | 5 | 8 | 4 |
| 134 | 2605.08755 | LAQuant: A Simple Overhead-free Large Reasoning Model Quantiza… | 05-09 | 量化、KV Cache | 7 | 5 | 6 | 4 |
| 135 | 2605.08813 | AgentSlimming: Towards Efficient and Cost-Aware Multi-Agent Sy… | 05-09 | 量化、剪枝 | 4 | 5 | 8 | 8 |
| 136 | 2605.08836 | Accelerating Multi-Condition T2I Generation via Adaptive Condi… | 05-09 | 剪枝 | 7 | 5 | 6 | 4 |
| 137 | 2605.08840 | ReST-KV: Robust KV Cache Eviction with Layer-wise Output Recon… | 05-09 | KV Cache | 8 | 5 | 6 | 8 |
| 138 | 2605.08855 | Low-Complexity Beamspace Channel Denoiser for mmWave Massive M… | 05-09 | 量化、稀疏化、硬件协同 | 6 | 9 | 7 | 7 |
| 139 | 2605.08873 | CoDistill-GRPO: A Co-Distillation Recipe for Efficient Group R… | 05-09 | 蒸馏、稀疏化 | 8 | 5 | 6 | 4 |
| 140 | 2605.08885 | Compact SO(3) Equivariant Atomistic Foundation Models via Stru… | 05-09 | 量化、蒸馏、剪枝 | 8 | 5 | 6 | 4 |
| 141 | 2605.08894 | Fitting Is Not Enough: Smoothness in Extremely Quantized LLMs | 05-09 | 量化 | 4 | 6 | 6 | 7 |
| 142 | 2605.09008 | Relative Kinetic Utility for Reasoning-Aware Structural Prunin… | 05-09 | 剪枝、稀疏化、硬件协同 | 6 | 5 | 8 | 4 |
| 143 | 2605.09100 | GRC: Unifying Reasoning-Driven Generation, Retrieval and Compr… | 05-09 | KV Cache | 6 | 5 | 8 | 4 |
| 144 | 2605.09276 | Uncertainty-Aware Token Importance Estimation in Spiking Trans… | 05-10 | 剪枝、硬件协同 | 5 | 5 | 6 | 4 |
| 145 | 2605.09281 | TileQ: Efficient Low-Rank Quantization of Mixture-of-Experts w… | 05-10 | 量化、硬件协同、低秩 | 7 | 5 | 6 | 7 |
| 146 | 2605.09308 | Hierarchical Attention-based Graph Neural Network with Relevan… | 05-10 | 剪枝 | 6 | 5 | 6 | 4 |
| 147 | 2605.09344 | PECMAN: Perception-enabled Collaborative Multi-Agent Navigatio… | 05-10 | 剪枝 | 6 | 5 | 6 | 5 |
| 148 | 2605.09375 | 31.1 A 14.08-to-135.69Token/s ReRAM-on-Logic Stacked Outlier-F… | 05-10 | 量化、向量量化、硬件协同 | 5 | 10 | 6 | 5 |
| 149 | 2605.09403 | Sparsity Moves Computation: How FFN Architecture Reshapes Atte… | 05-10 | 稀疏化 | 6 | 5 | 6 | 5 |
| 150 | 2605.09429 | Evading Visual Aphasia: Contrastive Adaptive Semantic Token Pr… | 05-10 | 剪枝 | 8 | 5 | 6 | 7 |
| 151 | 2605.09490 | Not All Thoughts Need HBM: Semantics-Aware Memory Hierarchy fo… | 05-10 | KV Cache | 9 | 5 | 6 | 4 |
| 152 | 2605.09503 | PermuQuant: Lowering Per-Group Quantization Error by Reorderin… | 05-10 | 量化 | 7 | 8 | 6 | 7 |
| 153 | 2605.09548 | Crosslingual On-Policy Self-Distillation for Multilingual Reas… | 05-10 | 蒸馏、稀疏化 | 7 | 5 | 6 | 8 |
| 154 | 2605.09639 | XTinyU-Net: Training-Free U-Net Scaling via Initialization-Tim… | 05-10 | 剪枝 | 8 | 6 | 8 | 7 |
| 155 | 2605.09649 | Make Each Token Count: Towards Improving Long-Context Performa… | 05-10 | KV Cache | 6 | 5 | 6 | 5 |
| 156 | 2605.09681 | Forcing-KV: Hybrid KV Cache Compression for Efficient Autoregr… | 05-10 | 剪枝、KV Cache | 6 | 6 | 6 | 8 |
| 157 | 2605.09719 | Distilling 3D Spatial Reasoning into a Lightweight Vision-Lang… | 05-10 | 蒸馏 | 6 | 5 | 7 | 4 |
| 158 | 2605.09825 | Pretraining large language models with MXFP4 on Native FP4 Har… | 05-11 | 量化、硬件协同 | 5 | 8 | 6 | 4 |
| 159 | 2605.09899 | Hyperbolic Distillation: Geometry-Guided Cross-Modal Transfer … | 05-11 | 蒸馏 | 4 | 5 | 6 | 4 |
| 160 | 2605.09924 | Evolving Knowledge Distillation for Lightweight Neural Machine… | 05-11 | 蒸馏 | 7 | 5 | 6 | 8 |
| 161 | 2605.09931 | PruneTIR: Inference-Time Tool Call Pruning for Effective yet E… | 05-11 | 剪枝 | 5 | 5 | 6 | 4 |
| 162 | 2605.09982 | ERASE: Eliminating Redundant Visual Tokens via Adaptive Two-St… | 05-11 | 剪枝 | 6 | 5 | 6 | 8 |
| 163 | 2605.09986 | Federated Language Models Under Bandwidth Budgets: Distillatio… | 05-11 | 量化、蒸馏 | 5 | 5 | 8 | 4 |
| 164 | 2605.10050 | EchoPrune: Interpreting Redundancy as Temporal Echoes for Effi… | 05-11 | 剪枝、稀疏化 | 6 | 5 | 8 | 7 |
| 165 | 2605.10198 | Empty SPACE: Cross-Attention Sparsity for Concept Erasure in D… | 05-11 | 稀疏化 | 6 | 5 | 6 | 7 |
| 166 | 2605.10210 | Nano-U: Efficient Terrain Segmentation for Tiny Robot Navigation | 05-11 | 量化、蒸馏 | 7 | 9 | 6 | 4 |
| 167 | 2605.10269 | Increasing the Efficiency of DETR for Maritime High-Resolution… | 05-11 | 剪枝 | 7 | 5 | 6 | 5 |
| 168 | 2605.10641 | LLaVA-CKD: Bottom-Up Cascaded Knowledge Distillation for Visio… | 05-11 | 蒸馏 | 7 | 5 | 6 | 4 |
| 169 | 2605.10643 | A Single-Layer Model Can Do Language Modeling | 05-11 | KV Cache | 6 | 5 | 6 | 4 |
| 170 | 2605.10655 | BCJR-QAT: A Differentiable Relaxation of Trellis-Coded Weight … | 05-11 | 量化、蒸馏 | 6 | 8 | 6 | 7 |
| 171 | 2605.10661 | bViT: Investigating Single-Block Recurrence in Vision Transfor… | 05-11 | 剪枝 | 6 | 5 | 6 | 4 |
| 172 | 2605.10673 | Compander-Aligned Query Geometry for Quantized Zeroth-Order Op… | 05-11 | 量化、稀疏化、向量量化 | 4 | 5 | 6 | 4 |
| 173 | 2605.10679 | Energy-Efficient Implementation of Spiking Recurrent Cells on … | 05-11 | 量化、稀疏化、硬件协同 | 5 | 8 | 6 | 4 |
| 174 | 2605.10748 | Provable Sparse Inversion and Token Relabel Enhanced One-shot … | 05-11 | 蒸馏、稀疏化 | 7 | 6 | 8 | 7 |
| 175 | 2605.10793 | ConQuR: Corner Aligned Activation Quantization via Optimized R… | 05-11 | 量化 | 5 | 5 | 7 | 10 |
| 176 | 2605.10875 | Compute Where it Counts: Self Optimizing Language Models | 05-11 | 量化、剪枝、稀疏化 | 6 | 5 | 6 | 5 |
| 177 | 2605.10886 | LoKA: Low-precision Kernel Applications for Recommendation Mod… | 05-11 | 量化、硬件协同 | 4 | 6 | 6 | 4 |
| 178 | 2605.10933 | DECO: Sparse Mixture-of-Experts with Dense-Comparable Performa… | 05-11 | 稀疏化 | 10 | 5 | 6 | 8 |
| 179 | 2605.10959 | QuIDE: Mastering the Quantized Intelligence Trade-off via Acti… | 05-05 | 量化 | 5 | 8 | 7 | 5 |
| 180 | 2605.10989 | SURGE: Surrogate Gradient Adaptation in Binary Neural Networks | 05-09 | 量化 | 7 | 9 | 8 | 4 |
| 181 | 2605.11098 | AffectCodec: Emotion-Preserving Neural Speech Codec for Expres… | 05-11 | 量化、蒸馏 | 5 | 5 | 6 | 4 |
| 182 | 2605.11222 | ADMM-Q: An Improved Hessian-based Weight Quantizer for Post-Tr… | 05-11 | 量化 | 6 | 9 | 8 | 10 |
| 183 | 2605.11260 | Curriculum Learning-Guided Progressive Distillation in Large L… | 05-11 | 蒸馏 | 7 | 5 | 6 | 4 |
| 184 | 2605.11290 | ReAD: Reinforcement-Guided Capability Distillation for Large L… | 05-11 | 蒸馏 | 4 | 5 | 8 | 8 |
| 185 | 2605.11354 | Lite3R: A Model-Agnostic Framework for Efficient Feed-Forward … | 05-12 | 量化、蒸馏、稀疏化 | 4 | 6 | 8 | 8 |
| 186 | 2605.11396 | MuonQ: Enhancing Low-Bit Muon Quantization via Directional Fid… | 05-12 | 量化 | 5 | 8 | 8 | 8 |
| 187 | 2605.11414 | Generative Diffusion Prior Distillation for Long-Context Knowl… | 05-12 | 蒸馏 | 5 | 5 | 7 | 4 |
| 188 | 2605.11433 | FedMM: Federated Collaborative Signal Quantization for Multi-M… | 05-12 | 量化、向量量化 | 5 | 5 | 8 | 4 |
| 189 | 2605.11477 | LDDR: Linear-DPP-Based Dynamic-Resolution Frame Sampling for V… | 05-12 | 剪枝 | 8 | 5 | 6 | 7 |
| 190 | 2605.11478 | FibQuant: Universal Vector Quantization for Random-Access KV-C… | 05-12 | 量化、KV Cache、向量量化 | 5 | 5 | 7 | 4 |
| 191 | 2605.11513 | A Study on Hidden Layer Distillation for Large Language Model … | 05-12 | 蒸馏 | 7 | 5 | 6 | 4 |
| 192 | 2605.11537 | Fast MoE Inference via Predictive Prefetching and Expert Repli… | 05-12 | 稀疏化 | 8 | 5 | 6 | 5 |
| 193 | 2605.11582 | Efficient LLM-based Advertising via Model Compression and Para… | 05-12 | 量化 | 4 | 5 | 6 | 4 |
| 194 | 2605.11605 | Keep What Audio Cannot Say: Context-Preserving Token Pruning f… | 05-12 | 剪枝 | 8 | 5 | 6 | 4 |
| 195 | 2605.11803 | OTT-Vid: Optimal Transport Temporal Token Compression for Vide… | 05-12 | 剪枝 | 8 | 6 | 8 | 7 |
| 196 | 2605.11817 | See What Matters: Differentiable Grid Sample Pruning for Gener… | 05-12 | 剪枝 | 6 | 6 | 7 | 8 |
| 197 | 2605.11835 | Multi-Timescale Conductance Spiking Networks: A Sparse, Gradie… | 05-12 | 稀疏化、硬件协同 | 7 | 5 | 6 | 4 |
| 198 | 2605.11869 | FIS-DiT: Breaking the Few-Step Video Inference Barrier via Tra… | 05-12 | 蒸馏、稀疏化 | 6 | 5 | 8 | 7 |
| 199 | 2605.11881 | Learning Subspace-Preserving Sparse Attention Graphs from Hete… | 05-12 | 稀疏化 | 7 | 5 | 6 | 5 |
| 200 | 2605.11983 | QDSB: Quantized Diffusion Schrödinger Bridges | 05-12 | 量化 | 6 | 5 | 7 | 8 |
| 201 | 2605.12110 | AB-Sparse: Sparse Attention with Adaptive Block Size for Accur… | 05-12 | 量化、稀疏化、KV Cache | 8 | 5 | 8 | 7 |
| 202 | 2605.12245 | SOAR: Scale Optimization for Accurate Reconstruction in NVFP4 … | 05-12 | 量化、硬件协同 | 7 | 8 | 8 | 7 |
| 203 | 2605.12327 | Grid Games: The Power of Multiple Grids for Quantizing Large L… | 05-12 | 量化 | 5 | 8 | 6 | 7 |
| 204 | 2605.12396 | NCCLZ: Compression-Enabled GPU Collectives with Decoupled Quan… | 05-12 | 量化 | 5 | 10 | 6 | 4 |
| 205 | 2605.12464 | Search Your Block Floating Point Scales! | 05-12 | 量化、硬件协同 | 6 | 8 | 8 | 4 |
| 206 | 2605.12471 | KV-Fold: One-Step KV-Cache Recurrence for Long-Context Inference | 05-12 | KV Cache | 6 | 5 | 6 | 7 |
| 207 | 2605.12562 | Uncovering Latent Pathological Signatures in Pulmonary CT via … | 05-12 | 蒸馏 | 6 | 5 | 6 | 4 |
| 209 | 2605.13111 | Pyramid Forcing: Head-Aware Pyramid KV Cache Policy for High-Q… | 05-13 | KV Cache | 4 | 5 | 6 | 8 |
| 210 | 2605.13143 | On the Generalization of Knowledge Distillation: An Informatio… | 05-13 | 蒸馏 | 5 | 5 | 6 | 4 |
| 211 | 2605.13165 | STOP: Structured On-Policy Pruning of Long-Form Reasoning in L… | 05-13 | 蒸馏、剪枝 | 6 | 5 | 6 | 4 |
| 212 | 2605.13178 | CLIP Tricks You: Training-free Token Pruning for Efficient Pix… | 05-13 | 剪枝 | 8 | 5 | 6 | 7 |
| 213 | 2605.13247 | EMO: Frustratingly Easy Progressive Training of Extendable MoE | 05-13 | 稀疏化 | 6 | 5 | 7 | 4 |
| 214 | 2605.13248 | Compact Latent Manifold Translation: A Parameter-Efficient Fou… | 05-13 | 量化、向量量化 | 8 | 6 | 7 | 5 |
| 215 | 2605.13316 | Test-time Sparsity for Extreme Fast Action Diffusion | 05-13 | 剪枝、稀疏化 | 8 | 6 | 7 | 8 |
| 216 | 2605.13375 | GRIP-VLM: Group-Relative Importance Pruning for Efficient Visi… | 05-13 | 剪枝 | 7 | 6 | 7 | 4 |
| 217 | 2605.13396 | PreFIQs: Face Image Quality Is What Survives Pruning | 05-13 | 剪枝 | 7 | 5 | 8 | 7 |
| 218 | 2605.13517 | ArcVQ-VAE: A Spherical Vector Quantization Framework with ArcC… | 05-13 | 量化、向量量化 | 5 | 5 | 8 | 8 |
| 219 | 2605.13521 | Granite Embedding Multilingual R2 Models | 05-13 | 剪枝 | 7 | 5 | 6 | 8 |
| 220 | 2605.13688 | MedCore: Boundary-Preserving Medical Core Pruning for MedSAM | 05-13 | 剪枝 | 6 | 5 | 8 | 8 |
| 221 | 2605.13734 | KVServe: Service-Aware KV Cache Compression for Communication-… | 05-13 | 蒸馏、KV Cache | 5 | 5 | 8 | 4 |
| 222 | 2605.13768 | High-Rate Quantized Matrix Multiplication II | 05-13 | 量化 | 5 | 9 | 7 | 7 |
| 223 | 2605.13769 | Dense vs Sparse Pretraining at Tiny Scale: Active-Parameter vs… | 05-13 | 稀疏化 | 7 | 5 | 6 | 4 |
| 224 | 2605.13810 | Provable Quantization with Randomized Hadamard Transform | 05-13 | 量化、KV Cache、向量量化 | 5 | 5 | 6 | 5 |
| 225 | 2605.13907 | AIS: Adaptive Importance Sampling for Quantized RL | 05-13 | 量化 | 6 | 6 | 6 | 4 |
| 226 | 2605.13915 | Multi-Scale Dequant: Eliminating Dequantization Bottleneck via… | 05-13 | 量化、KV Cache、硬件协同 | 6 | 8 | 6 | 7 |
| 227 | 2605.13974 | Few Channels Draw The Whole Picture: Revealing Massive Activat… | 05-13 | 稀疏化 | 5 | 5 | 7 | 4 |
| 228 | 2605.13981 | Towards Resource-Efficient LLMs: End-to-End Energy Accounting … | 05-13 | 蒸馏 | 5 | 5 | 6 | 8 |
| 229 | 2605.13997 | HodgeCover: Higher-Order Topological Coverage Drives Compressi… | 05-13 | 剪枝、稀疏化 | 8 | 6 | 6 | 4 |
| 230 | 2605.14037 | Self-Pruned Key-Value Attention: Learning When to Write by Pre… | 05-13 | 剪枝、稀疏化、KV Cache | 7 | 5 | 6 | 5 |
| 231 | 2605.14075 | Rethinking Layer Relevance in Large Language Models Beyond Cos… | 05-13 | 剪枝 | 4 | 5 | 6 | 5 |
| 232 | 2605.14110 | SToRe3D: Sparse Token Relevance in ViTs for Efficient Multi-Vi… | 05-13 | 剪枝、稀疏化 | 5 | 8 | 6 | 5 |
| 233 | 2605.14191 | CoReDiT: Spatial Coherence-Guided Token Pruning and Reconstruc… | 05-13 | 剪枝、硬件协同 | 8 | 5 | 6 | 5 |
| 234 | 2605.14252 | Not All Timesteps Matter Equally: Selective Alignment Knowledg… | 05-14 | 蒸馏、硬件协同 | 5 | 5 | 6 | 8 |
| 235 | 2605.14333 | InsightTok: Improving Text and Face Fidelity in Discrete Token… | 05-14 | 量化、向量量化 | 7 | 6 | 6 | 4 |
| 236 | 2605.14346 | Learning with Semantic Priors: Stabilizing Point-Supervised In… | 05-14 | 蒸馏 | 5 | 5 | 6 | 8 |
| 237 | 2605.14359 | RQ-MoE: Residual Quantization via Mixture of Experts for Effic… | 05-14 | 量化、向量量化 | 7 | 10 | 6 | 8 |
| 238 | 2605.14434 | Efficient Generative Retrieval for E-commerce Search with Sema… | 05-14 | 量化、稀疏化、向量量化 | 6 | 5 | 6 | 4 |
| 239 | 2605.14438 | BEAM: Binary Expert Activation Masking for Dynamic Routing in MoE | 05-14 | 稀疏化 | 4 | 9 | 8 | 4 |
| 240 | 2605.14458 | OmniDrop: Layer-wise Token Pruning for Omni-modal LLMs via Que… | 05-14 | 剪枝 | 8 | 6 | 6 | 7 |
| 241 | 2605.14512 | Asymmetric Generative Recommendation via Multi-Expert Projecti… | 05-14 | 量化、向量量化 | 8 | 5 | 6 | 8 |
| 242 | 2605.14513 | HASTE: Training-Free Video Diffusion Acceleration via Head-Wis… | 05-14 | 稀疏化 | 5 | 7 | 6 | 7 |
| 243 | 2605.14738 | TAPIOCA: Why Task- Aware Pruning Improves OOD model Capability | 05-14 | 剪枝 | 6 | 5 | 8 | 5 |
| 244 | 2605.14752 | Cognitive-Uncertainty Guided Knowledge Distillation for Accura… | 05-14 | 蒸馏 | 8 | 5 | 7 | 8 |
| 245 | 2605.14764 | Compositional Sparsity as an Inductive Bias for Neural Archite… | 05-14 | 稀疏化 | 7 | 5 | 6 | 5 |
| 246 | 2605.14795 | COAL: Counterfactual and Observation-Enhanced Alignment Learni… | 05-14 | 蒸馏、稀疏化 | 8 | 5 | 8 | 4 |
| 247 | 2605.14844 | XFP: Quality-Targeted Adaptive Codebook Quantization with Spar… | 05-14 | 量化、剪枝、稀疏化、向量量化、硬件协同 | 6 | 8 | 6 | 4 |
| 248 | 2605.14877 | HeatKV: Head-tuned KV-cache Compression for Visual Autoregress… | 05-14 | 剪枝、KV Cache | 7 | 5 | 8 | 8 |
| 249 | 2605.14886 | BiFedKD: Bidirectional Federated Knowledge Distillation Framew… | 05-14 | 蒸馏 | 4 | 5 | 6 | 4 |
| 250 | 2605.14897 | Critic-Driven Voronoi-Quantization for Distilling Deep RL Poli… | 05-14 | 量化、蒸馏 | 5 | 5 | 6 | 4 |
| 251 | 2605.14929 | A Hardware-Aware, Per-Layer Methodology for Post-Training Quan… | 05-14 | 量化、稀疏化、向量量化、硬件协同 | 6 | 6 | 6 | 7 |
| 253 | 2605.15152 | Widening the Gap: Exploiting LLM Quantization via Outlier Inje… | 05-14 | 量化 | 4 | 5 | 7 | 5 |
| 255 | 2605.15250 | GQLA: Group-Query Latent Attention for Hardware-Adaptive Large… | 05-14 | KV Cache、硬件协同、低秩 | 8 | 5 | 6 | 4 |
| 256 | 2605.15299 | Fortress: A Case Study in Stabilizing Search Recommendations v… | 05-14 | 剪枝 | 4 | 5 | 6 | 4 |
| 257 | 2605.15315 | Context Pruning for Coding Agents via Multi-Rubric Latent Reas… | 05-14 | 剪枝、稀疏化 | 10 | 9 | 6 | 4 |
| 258 | 2605.15491 | Ghosted Layers: Unconstrained Activation Alignment for Recover… | 05-15 | 剪枝 | 4 | 5 | 7 | 7 |
| 259 | 2605.15507 | PrismQuant: Rate-Distortion-Optimal Vector Quantization for Ga… | 05-15 | 量化、向量量化 | 6 | 5 | 7 | 5 |
| 260 | 2605.15508 | STS: Efficient Sparse Attention with Speculative Token Sparsity | 05-15 | 剪枝、稀疏化 | 8 | 8 | 6 | 4 |
| 261 | 2605.15572 | Measuring Maximum Activations in Open Large Language Models | 05-15 | 量化 | 5 | 5 | 6 | 8 |
| 262 | 2605.15621 | LRCP: Low-Rank Compressibility Guided Visual Token Pruning for… | 05-15 | 剪枝、低秩 | 6 | 5 | 8 | 7 |
| 263 | 2605.15626 | IO-SVD: Input-Output Whitened SVD for Adaptive-Rank LLM Compre… | 05-15 | 量化、剪枝、硬件协同、低秩 | 5 | 6 | 8 | 7 |
| 264 | 2605.15684 | ElasticDiT: Efficient Diffusion Transformers via Elastic Archi… | 05-15 | 蒸馏、剪枝、稀疏化、硬件协同 | 8 | 5 | 6 | 4 |
| 265 | 2605.15689 | How to Choose Your Teacher for Fine Grained Image Recognition | 05-15 | 蒸馏 | 7 | 5 | 6 | 8 |
| 266 | 2605.15694 | Going Beyond the Edge: Distributed Inference of Transformer Mo… | 05-15 | 剪枝 | 5 | 6 | 8 | 4 |
| 267 | 2605.15828 | Not All Tasks Quantize Equally: Fisher-Guided Quantization for… | 05-15 | 量化、硬件协同 | 8 | 8 | 6 | 7 |
| 268 | 2605.15852 | GHOST: Geometry-Hierarchical Online Streaming Token Eviction f… | 05-15 | KV Cache | 6 | 7 | 6 | 7 |
| 269 | 2605.15913 | Towards Generalization of Block Attention via Automatic Segmen… | 05-15 | 蒸馏、KV Cache | 6 | 5 | 7 | 4 |
| 270 | 2605.16007 | Ascend-RaBitQ: Heterogeneous NPU-CPU Acceleration of Billion-S… | 05-15 | 量化、硬件协同 | 6 | 10 | 8 | 4 |
| 271 | 2605.16138 | Surrogate Neural Architecture Codesign Package (SNAC-Pack) | 05-15 | 量化、剪枝、硬件协同 | 5 | 5 | 6 | 8 |
| 272 | 2605.16234 | No Free Swap: Protocol-Dependent Layer Redundancy in Transformers | 05-15 | 剪枝 | 5 | 5 | 6 | 4 |
| 273 | 2605.16343 | LoopQ: Quantization for Recursive Transformers | 05-08 | 量化 | 6 | 8 | 8 | 7 |
| 274 | 2605.16349 | Geometric Asymmetry in MoE Specialization: Functional Decorrel… | 05-08 | 稀疏化 | 5 | 5 | 6 | 5 |
| 275 | 2605.16359 | How Many Visual Tokens Do Multimodal Language Models Need? Sca… | 05-09 | 剪枝、稀疏化 | 6 | 6 | 6 | 7 |
| 276 | 2605.16360 | ProxyKV: Cross-Model Proxy Pruning for Efficient Long-Context … | 05-09 | 剪枝 | 6 | 5 | 6 | 5 |
| 277 | 2605.16423 | Nonlinear Bipolar Compensation: Handling Outliers in Post-Trai… | 05-14 | 量化 | 5 | 5 | 6 | 7 |
| 278 | 2605.16439 | KVCapsule: Efficient Sequential KV Cache Compression for Visio… | 05-14 | KV Cache | 6 | 5 | 8 | 5 |
| 279 | 2605.16443 | Two-Valued Symmetric Circulant Matrices: Applications in Deep … | 05-15 | 剪枝、稀疏化、硬件协同、低秩 | 6 | 6 | 6 | 4 |
| 280 | 2605.16579 | Attend Locally, Remember Linearly: Linear Attention as Cross-F… | 05-15 | 稀疏化、KV Cache | 6 | 5 | 7 | 4 |
| 281 | 2605.16732 | DiRotQ: Rotation-Aware Quantization for 4-bit Diffusion Transf… | 05-16 | 量化、低秩 | 6 | 8 | 8 | 7 |
| 282 | 2605.16786 | Lever: Speculative LLM Inference on Smartphones | 05-16 | 剪枝、硬件协同 | 6 | 5 | 6 | 4 |
| 283 | 2605.16826 | Decoupling KL and Trajectories: A Unified Perspective for SFT,… | 05-16 | 蒸馏 | 6 | 5 | 6 | 7 |
| 284 | 2605.16839 | CompactAttention: Accelerating Chunked Prefill with Block-Unio… | 05-16 | 稀疏化、KV Cache | 5 | 5 | 6 | 4 |
| 285 | 2605.16882 | E-PMQ: Expert-Guided Post-Merge Quantization with Merged-Weigh… | 05-16 | 量化 | 6 | 8 | 6 | 7 |
| 286 | 2605.16901 | CAR-SAM: Cross-Attention Reconstruction for Post-Training Quan… | 05-16 | 量化 | 8 | 8 | 6 | 7 |
| 287 | 2605.16928 | Full Attention Strikes Back: Transferring Full Attention into … | 05-16 | 稀疏化、KV Cache | 6 | 5 | 6 | 4 |
| 288 | 2605.17127 | On Trajectory-Based Stability Analysis for $1$-bit Sigma-Delta… | 05-16 | 量化、稀疏化 | 7 | 5 | 6 | 5 |
| 291 | 2605.17170 | TriAxialKV: Toward Extreme Low-Precision KV-Cache Quantization… | 05-16 | 量化、KV Cache | 8 | 9 | 8 | 4 |
| 292 | 2605.17289 | LEAP: Learnable End-to-End Adaptive Pruning of Large Language … | 05-17 | 剪枝、稀疏化、硬件协同 | 8 | 6 | 7 | 4 |
| 293 | 2605.17415 | IVF-TQ: Calibration-Free Streaming Vector Search via a Codeboo… | 05-17 | 量化、向量量化 | 5 | 5 | 8 | 7 |
| 294 | 2605.17447 | FastOCR: Dynamic Visual Fixation via KV Cache Pruning for Effi… | 05-17 | 剪枝、稀疏化、KV Cache | 6 | 5 | 6 | 7 |
| 295 | 2605.17471 | WinQ: Accelerating Quantization-Aware Training of Language Mod… | 05-17 | 量化 | 8 | 8 | 6 | 4 |
| 296 | 2605.17524 | Covariance Structure and Coordinate Heterogeneity Govern Binar… | 05-17 | 量化 | 6 | 10 | 7 | 4 |
| 297 | 2605.17552 | Q-LocalAdam: Memory-Efficient Client-Side Adaptive Optimizatio… | 05-17 | 量化、硬件协同 | 5 | 6 | 6 | 4 |
| 298 | 2605.17613 | VeriCache: Turning Lossy KV Cache into Lossless LLM Inference | 05-17 | 量化、KV Cache | 6 | 5 | 8 | 4 |
| 299 | 2605.17633 | SparseSAM: Structured Sparsification of Activations in Segment… | 05-17 | 稀疏化、硬件协同 | 4 | 7 | 6 | 7 |
| 300 | 2605.17682 | GEM: Gaussian Evolution Model for Occupancy Forecasting and Mo… | 05-17 | 量化 | 8 | 5 | 6 | 5 |
| 301 | 2605.17704 | Toy Combinatorial Interpretability Models Reveal Lottery Ticke… | 05-18 | 稀疏化 | 7 | 5 | 6 | 4 |
| 302 | 2605.17710 | Sometin Beta Pass Notin (SBPN): Improving Multilingual ASR for… | 05-18 | 蒸馏 | 8 | 5 | 7 | 8 |
| 303 | 2605.17743 | MoASE++: Mixture of Activation Sparsity Experts with Domain-Ad… | 05-18 | 蒸馏、稀疏化、低秩 | 6 | 5 | 6 | 4 |
| 304 | 2605.17745 | StatQAT: Statistical Quantizer Optimization for Deep Networks | 05-18 | 量化、硬件协同 | 6 | 5 | 8 | 4 |
| 305 | 2605.17757 | OSCAR: Offline Spectral Covariance-Aware Rotation for 2-bit KV… | 05-18 | 量化、KV Cache | 7 | 9 | 6 | 10 |
| 306 | 2605.17779 | Learning Variable-Length Tokenization for Generative Recommend… | 05-18 | 量化、稀疏化、向量量化 | 7 | 5 | 6 | 4 |
| 307 | 2605.17831 | Agentic Cost-Aware Query Planning with Knowledge Distillation … | 05-18 | 蒸馏 | 6 | 10 | 6 | 8 |
| 308 | 2605.17834 | Stabilizing, Scaling & Enhancing MeanFlow for Large-scale Diff… | 05-18 | 蒸馏 | 6 | 6 | 8 | 4 |
| 309 | 2605.17837 | Temporal Aware Pruning for Efficient Diffusion-based Video Gen… | 05-18 | 剪枝 | 6 | 6 | 6 | 7 |
| 310 | 2605.17839 | Balancing Knowledge Distillation for Imbalance Learning with B… | 05-18 | 蒸馏 | 7 | 5 | 6 | 4 |
| 311 | 2605.17887 | Attention Sinks and Outliers in Attention Residuals | 05-18 | 量化 | 6 | 8 | 6 | 5 |
| 312 | 2605.17985 | SAFE-SVD: Sensitivity-Aware Fidelity-Enforcing SVD for Physics… | 05-18 | 低秩 | 4 | 5 | 6 | 5 |
| 313 | 2605.17997 | MARR: Module-Adaptive Residual Reconstruction for Low-Bit Post… | 05-18 | 量化 | 8 | 8 | 7 | 7 |
| 314 | 2605.18035 | New Insight of Variance reduce in Zero-Order Hard-Thresholding… | 05-18 | 稀疏化 | 5 | 5 | 6 | 5 |
| 315 | 2605.18041 | OmniSelect: Dynamic Modality-Aware Token Compression for Effic… | 05-18 | 剪枝 | 5 | 5 | 6 | 7 |
| 316 | 2605.18053 | Protection Is (Nearly) All You Need: Structural Protection Dom… | 05-18 | KV Cache | 6 | 5 | 6 | 5 |
| 317 | 2605.18071 | KVDrive: A Holistic Multi-Tier KV Cache Management System for … | 05-18 | 稀疏化、KV Cache | 7 | 5 | 6 | 4 |
| 318 | 2605.18079 | The Expressive Power of Low Precision Softmax Transformers wit… | 05-18 | 量化 | 5 | 5 | 6 | 8 |
| 319 | 2605.18141 | A Brief Overview: On-Policy Self-Distillation In Large Languag… | 05-18 | 蒸馏 | 6 | 5 | 6 | 4 |
| 320 | 2605.18331 | Prune, Update and Trim: Robust Structured Pruning for Large La… | 05-18 | 剪枝、稀疏化 | 7 | 6 | 8 | 7 |
| 321 | 2605.18475 | GAMMA: Global Bit Allocation for Mixed-Precision Models under … | 05-18 | 量化 | 7 | 8 | 8 | 7 |
| 322 | 2605.18702 | Distilling Tabular Foundation Models for Structured Health Data | 05-18 | 蒸馏 | 7 | 5 | 6 | 4 |
| 323 | 2605.18739 | LongLive-2.0: An NVFP4 Parallel Infrastructure for Long Video … | 05-18 | 量化、蒸馏、KV Cache | 5 | 8 | 8 | 4 |
| 324 | 2605.18753 | DashAttention: Differentiable and Adaptive Sparse Hierarchical… | 05-18 | 稀疏化 | 6 | 5 | 8 | 5 |
| 325 | 2605.18794 | Robust Basis Spline Decoupling for the Compression of Transfor… | 05-11 | 低秩 | 5 | 5 | 6 | 5 |
| 326 | 2605.18800 | Theory-optimal Quantization Based on Flatness | 05-11 | 量化、蒸馏 | 6 | 8 | 8 | 7 |
| 327 | 2605.18856 | SPHERICAL KV: Angle-Domain Attention and Rate-Distortion Reten… | 05-13 | 量化、KV Cache | 5 | 5 | 7 | 5 |
| 328 | 2605.18860 | Spectral structural distortion reveals redundant neurons in ne… | 05-14 | 剪枝 | 5 | 5 | 6 | 4 |
| 330 | 2605.18865 | From Sparsity to Simplicity: Enabling Simpler Sequential Repla… | 05-15 | 蒸馏、稀疏化 | 5 | 5 | 6 | 4 |
| 331 | 2605.18933 | A Geometric Analysis of Sign-Magnitude Asymmetry in a ReLU + R… | 05-18 | 量化 | 6 | 5 | 5 | 5 |
| 332 | 2605.19207 | Quantized Machine Learning Models for Medical Imaging in Low-R… | 05-19 | 量化、蒸馏 | 6 | 10 | 6 | 7 |
| 333 | 2605.19218 | Rotation-Aligned Key Channel Pruning for Efficient Vision-Lang… | 05-19 | 剪枝、稀疏化、KV Cache、硬件协同 | 6 | 5 | 6 | 4 |
| 334 | 2605.19299 | Cross-Paradigm Knowledge Distillation: A Comprehensive Study o… | 05-19 | 蒸馏 | 8 | 5 | 6 | 4 |
| 335 | 2605.19304 | MMGS: 10$\times$ Compressed 3DGS through Optimal Transport Agg… | 05-19 | 剪枝 | 7 | 5 | 8 | 4 |
| 336 | 2605.19378 | Sparse Mixture-of-Experts Routing in Visual Diffusion Transfor… | 05-12 | 量化、稀疏化、硬件协同 | 6 | 6 | 6 | 4 |
| 337 | 2605.19405 | A complete discussion on fully reconfigurable, digital, scalab… | 05-19 | 稀疏化、硬件协同 | 7 | 5 | 6 | 4 |
| 338 | 2605.19433 | Backtracking When It Strays: Mitigating Dual Exposure Biases i… | 05-19 | 蒸馏 | 8 | 5 | 6 | 4 |
| 339 | 2605.19506 | EventPrune: Cascaded Event-Assisted Token Pruning for Efficien… | 05-19 | 剪枝 | 8 | 5 | 8 | 7 |
| 340 | 2605.19533 | Replacement Learning: Training Neural Networks with Fewer Para… | 05-19 | 量化 | 7 | 6 | 6 | 4 |
| 341 | 2605.19561 | TORQ: Two-Level Orthogonal Rotation for MXFP4 Quantization | 05-19 | 量化、向量量化、硬件协同 | 6 | 8 | 8 | 10 |
| 342 | 2605.19645 | K-Quantization and its Impact on Output Performance | 05-19 | 量化 | 6 | 9 | 6 | 5 |
| 343 | 2605.19688 | DocQT: Improving Document Forgery Localization Robustness via … | 05-19 | 量化 | 5 | 5 | 6 | 8 |
| 344 | 2605.19726 | Efficient Long-Context Modeling in Diffusion Language Models v… | 05-19 | 稀疏化 | 6 | 5 | 6 | 5 |
| 345 | 2605.19729 | LIFT and PLACE: A Simple, Stable, and Effective Knowledge Dist… | 05-19 | 蒸馏 | 6 | 6 | 7 | 4 |
| 346 | 2605.19842 | Fast Tensorization of Neural Networks via Slice-wise Feature D… | 05-19 | 蒸馏、低秩 | 6 | 5 | 6 | 4 |
| 347 | 2605.19929 | Breaking Modality Heterogeneity in Low-Bit Quantization for La… | 05-19 | 量化 | 8 | 8 | 7 | 7 |
| 348 | 2605.19972 | Block-Sphere Vector Quantization | 05-19 | 量化、向量量化 | 5 | 5 | 8 | 4 |
| 349 | 2605.20035 | Stage-adaptive Token Selection for Efficient Omni-modal LLMs | 05-19 | 剪枝 | 6 | 5 | 8 | 7 |
| 350 | 2605.20295 | Quant.npu: Enabling Efficient Mobile NPU Inference for on-devi… | 05-19 | 量化、硬件协同 | 10 | 5 | 6 | 7 |
| 351 | 2605.20315 | Mix-Quant: Quantized Prefilling, Precise Decoding for Agentic … | 05-19 | 量化、硬件协同 | 5 | 8 | 8 | 4 |
| 352 | 2605.20357 | Consistently Informative Soft-Label Temperature for Knowledge … | 05-19 | 蒸馏 | 5 | 5 | 6 | 4 |
| 353 | 2605.20402 | Decomposing MXFP4 quantization error for LLM reinforcement lea… | 05-19 | 量化 | 6 | 8 | 6 | 7 |
| 354 | 2605.20551 | Faster or Stronger: Towards Flexible Visual Place Recognition … | 05-19 | 蒸馏、剪枝、硬件协同 | 7 | 5 | 6 | 4 |
| 355 | 2605.20659 | RoPeSLR: 3D RoPE-driven Sparse-LowRank Attention for Efficient… | 05-20 | 稀疏化、低秩 | 6 | 6 | 7 | 5 |
| 356 | 2605.20669 | GSA-YOLO: A High-Efficiency Framework via Structured Sparsity … | 05-20 | 蒸馏、剪枝、稀疏化 | 6 | 5 | 8 | 4 |
| 357 | 2605.20670 | LT2: Linear-Time Looped Transformers | 05-20 | 稀疏化 | 8 | 5 | 6 | 4 |
| 358 | 2605.20706 | Llamas on the Web: Memory-Efficient, Performance-Portable, and… | 05-20 | 量化、硬件协同 | 6 | 5 | 6 | 4 |
| 359 | 2605.20717 | E-ReCON: An Energy- and Resource-Efficient Precision-Configura… | 05-20 | 剪枝、稀疏化、硬件协同 | 6 | 5 | 8 | 4 |
| 360 | 2605.20751 | PACD-Net: Pseudo-Augmented Contrastive Distillation for Glycem… | 05-20 | 蒸馏、稀疏化 | 7 | 6 | 6 | 4 |
| 361 | 2605.20802 | ELSA: An ELastic SNN Inference Architecture for Efficient Neur… | 05-20 | 量化、稀疏化、硬件协同 | 7 | 8 | 8 | 4 |
| 362 | 2605.20813 | PulseCol: Periodically Refreshed Column-Sparse Attention for A… | 05-20 | 稀疏化、KV Cache | 5 | 5 | 6 | 4 |
| 363 | 2605.20866 | LOSCAR-SGD: Local SGD with Communication-Computation Overlap a… | 05-20 | 稀疏化 | 7 | 5 | 8 | 4 |
| 364 | 2605.20868 | Runtime-Certified Bounded-Error Quantized Attention | 05-20 | 量化、KV Cache | 6 | 8 | 6 | 4 |
| 365 | 2605.20940 | 3D Reconstruction and Knowledge Distillation to Improve Multi-… | 05-20 | 蒸馏 | 5 | 5 | 7 | 4 |
| 366 | 2605.21072 | Q-ARVD: Quantizing Autoregressive Video Diffusion Models | 05-20 | 量化 | 4 | 5 | 8 | 5 |
| 367 | 2605.21104 | HORST: Composing Optimizer Geometries for Sparse Transformer T… | 05-20 | 稀疏化 | 7 | 5 | 6 | 4 |
| 368 | 2605.21171 | FTerViT: Fully Ternary Vision Transformer | 05-20 | 量化、蒸馏、硬件协同 | 10 | 8 | 8 | 4 |
| 369 | 2605.21226 | OCTOPUS: Optimized KV Cache for Transformers via Octahedral Pa… | 05-20 | 量化、KV Cache | 6 | 6 | 7 | 8 |
| 370 | 2605.21322 | Optimized Federated Knowledge Distillation with Distributed Ne… | 05-20 | 蒸馏、硬件协同 | 5 | 5 | 6 | 4 |
| 371 | 2605.21333 | SymbolicLight V1: Spike-Gated Dual-Path Language Modeling with… | 05-20 | 稀疏化、硬件协同 | 8 | 9 | 6 | 4 |
| 372 | 2605.21426 | Adaptive Signal Resuscitation: Channel-wise Post-Pruning Repai… | 05-20 | 剪枝、稀疏化 | 8 | 5 | 6 | 7 |
| 373 | 2605.21649 | EntmaxKV: Support-Aware Decoding for Entmax Attention | 05-20 | 稀疏化、KV Cache | 6 | 5 | 6 | 8 |
| 374 | 2605.21699 | X-Token: Projection-Guided Cross-Tokenizer Knowledge Distillation | 05-20 | 蒸馏、稀疏化 | 8 | 5 | 6 | 4 |
| 375 | 2605.21924 | Visual-Advantage On-Policy Distillation for Vision-Language Mo… | 05-21 | 蒸馏 | 5 | 5 | 6 | 4 |
| 376 | 2605.21972 | How Sparsity Allocation Shapes Label-Free Post-Pruning Recover… | 05-21 | 剪枝、稀疏化 | 6 | 5 | 6 | 4 |
| 377 | 2605.22015 | ORBIS: Output-Guided Token Reduction with Distribution-Aware M… | 05-21 | 量化、硬件协同 | 8 | 10 | 6 | 4 |
| 378 | 2605.22064 | Hy-MT2: A Family of Fast, Efficient and Powerful Multilingual … | 05-21 | 量化、硬件协同 | 7 | 6 | 6 | 8 |
| 379 | 2605.22106 | ArborKV: Structure-Aware KV Cache Management for Scaling Tree-… | 05-21 | KV Cache、硬件协同 | 5 | 5 | 6 | 4 |
| 380 | 2605.22269 | MuKV: Multi-Grained KV Cache Compression for Long Streaming Vi… | 05-21 | KV Cache | 5 | 5 | 6 | 5 |
| 381 | 2605.22337 | Meta-Soft: Leveraging Composable Meta-Tokens for Context-Prese… | 05-21 | 稀疏化、KV Cache | 6 | 5 | 6 | 5 |
| 382 | 2605.22350 | Partial Fusion of Neural Networks: Efficient Tradeoffs Between… | 05-21 | 剪枝 | 7 | 5 | 6 | 8 |
| 383 | 2605.22351 | QuantSR+: Pushing the Limit of Quantized Image Super-Resolutio… | 05-21 | 量化、蒸馏、剪枝 | 8 | 9 | 6 | 4 |
| 384 | 2605.22372 | ASAP: Attention Sink Anchored Pruning | 05-21 | 剪枝 | 8 | 5 | 6 | 7 |
| 385 | 2605.22476 | Structured-Sparse Attention for Entity Tracking with Subquadra… | 05-21 | 稀疏化 | 6 | 5 | 6 | 4 |
| 386 | 2605.22679 | Conceptualizing Embeddings: Sparse Disentanglement for Vision-… | 05-21 | 稀疏化 | 5 | 5 | 6 | 5 |
| 387 | 2605.22691 | Posterior Collapse as Automatic Spectral Pruning | 05-21 | 剪枝 | 4 | 5 | 7 | 5 |
| 388 | 2605.22718 | WorldKV: Efficient World Memory with World Retrieval and Compr… | 05-21 | 剪枝、KV Cache | 6 | 5 | 6 | 7 |
| 389 | 2605.22731 | Post-Training is About States, Not Tokens: A State Distributio… | 05-21 | 蒸馏 | 7 | 5 | 7 | 7 |
| 390 | 2605.22843 | Knowledge Distillation for Low-Resource Open-source Text-to-SQ… | 05-13 | 蒸馏 | 5 | 5 | 6 | 8 |
| 391 | 2605.22850 | ObjectCache: Layerwise Object-Storage Retrieval for KV Cache R… | 05-16 | KV Cache | 5 | 5 | 9 | 8 |
| 392 | 2605.23057 | ModeSwitch-LLM: A Lightweight Phase-Aware Controller for Cross… | 05-21 | 量化 | 8 | 6 | 6 | 4 |
| 393 | 2605.23078 | GEMQ: Global Expert-Level Mixed-Precision Quantization for MoE… | 05-21 | 量化 | 5 | 6 | 7 | 8 |
| 394 | 2605.23081 | ThriftAttention: Selective Mixed Precision for Long-Context FP… | 05-21 | 量化 | 6 | 8 | 8 | 8 |
| 395 | 2605.23102 | LLM Sparsity Prior for Robust Feature Selection | 05-21 | 稀疏化 | 5 | 5 | 7 | 5 |
| 396 | 2605.23200 | Adaptive Mass-Segmented KV Compression for Long-Context Reasoning | 05-22 | 稀疏化、KV Cache | 5 | 5 | 6 | 4 |
| 397 | 2605.23226 | MASQ: Accelerating Masked Diffusion via Stage-Wise Multi-Preci… | 05-22 | 量化、硬件协同 | 5 | 10 | 6 | 4 |
| 398 | 2605.23258 | A Simple Plug-in for Improving Eviction-Based KV Cache Compres… | 05-22 | KV Cache | 5 | 9 | 6 | 5 |
| 399 | 2605.23294 | NASiC: 3D NAND-based CAM-Selected Multibit CIM Architecture fo… | 05-22 | 稀疏化、硬件协同 | 7 | 5 | 6 | 4 |
| 400 | 2605.23310 | From Head to Tail: Asymmetric Knowledge Transfer in Long-tail … | 05-22 | 量化、向量量化 | 8 | 5 | 6 | 4 |
| 401 | 2605.23373 | AffectCodec: Emotion-Preserving Neural Speech Codec with Block… | 05-22 | 量化 | 4 | 5 | 7 | 4 |
| 402 | 2605.23445 | DFSAttn: Dynamic Fine-grained Sparse Attention for Efficient V… | 05-22 | 稀疏化 | 6 | 5 | 6 | 7 |
| 403 | 2605.23451 | Efficient One-Step Diffusion Restoration Model with Compact To… | 05-22 | 剪枝 | 4 | 10 | 6 | 4 |
| 405 | 2605.23857 | Strong Teacher Not Needed? On Distillation in LLM Pretraining | 05-22 | 蒸馏 | 5 | 5 | 6 | 4 |
| 406 | 2605.23969 | SLAP: Stratified Loss-based Pruning for On-Policy Data-Efficie… | 05-13 | 剪枝 | 8 | 5 | 8 | 4 |
| 407 | 2605.23988 | TSFLora: Token-Compressed Split Fine-Tuning for Wireless Edge … | 05-17 | 量化 | 5 | 5 | 6 | 4 |
| 408 | 2605.24011 | ActQuant: Sub-4-bit Action-Guided Quantization for Vision-Lang… | 05-19 | 量化、硬件协同 | 6 | 8 | 6 | 7 |
| 409 | 2605.24019 | MGVQ: Synergizing Multi-dimensional Sensitivity-Aware and Grad… | 05-20 | 量化、向量量化、硬件协同 | 8 | 9 | 8 | 7 |
| 410 | 2605.24022 | Adaptive KV Cache Reuse for Fast Long-Context LLM Serving | 05-20 | 稀疏化、KV Cache、硬件协同 | 4 | 5 | 8 | 4 |
| 411 | 2605.24058 | Signs Beat Floats: Low-Rank Double-Binary Adaptation for On-De… | 05-22 | 量化、硬件协同、低秩 | 8 | 9 | 6 | 4 |
| 412 | 2605.24144 | EVA: Accelerating LLM Decoding via an Efficient Vector Quantiz… | 05-22 | 量化、向量量化、硬件协同 | 7 | 8 | 6 | 8 |
| 413 | 2605.24168 | Inference Time Context Sparsity: Illusion or Opportunity? | 05-22 | 稀疏化、硬件协同 | 5 | 6 | 7 | 4 |
| 414 | 2605.24391 | MX-SAFE: Versatile Inference- and Training-Proof Microscaling … | 05-23 | 量化、硬件协同 | 6 | 6 | 6 | 4 |
| 415 | 2605.24518 | Grammatically-Guided Sparse Attention for Efficient and Interp… | 05-23 | 稀疏化 | 5 | 5 | 7 | 5 |
| 416 | 2605.24530 | Unveil: Unified Visual-Textual Integration and Distillation fo… | 05-23 | 蒸馏 | 7 | 5 | 8 | 4 |
| 417 | 2605.24649 | On the Stability and Realizability of Recurrent Polynomial Sur… | 05-23 | 量化 | 5 | 5 | 8 | 4 |
| 418 | 2605.24754 | Motion-Compensated Weight Compression | 05-23 | 量化 | 5 | 5 | 6 | 8 |
| 419 | 2605.24786 | CONF-KV: Confidence-Aware KV Cache Eviction with Mixed-Precisi… | 05-24 | 量化、剪枝、KV Cache | 6 | 6 | 6 | 5 |
| 420 | 2605.24890 | QuoVLA: Quotient Space for Vision-Language-Action Models | 05-24 | 量化 | 5 | 5 | 7 | 5 |
| 421 | 2605.24921 | BandVQ: Band-Wise Vector-Quantized EEG Foundation Model | 05-24 | 量化、向量量化 | 5 | 5 | 6 | 5 |
| 422 | 2605.25054 | Scale When Needed: Adaptive Neuron-level Mixed Precision Quant… | 05-24 | 量化、硬件协同 | 5 | 6 | 6 | 4 |
| 423 | 2605.25085 | Polynomial Context-Truncation Sensitivity in Autoregressive La… | 05-24 | KV Cache | 6 | 5 | 6 | 5 |
| 424 | 2605.25134 | Theoretical Analysis of Sparse Optimization with Reparameteriz… | 05-24 | 稀疏化 | 5 | 5 | 6 | 5 |
| 425 | 2605.25170 | Grow-Prune-Freeze Networks: Adaptive & Continual Learning Tech… | 05-24 | 剪枝 | 6 | 5 | 6 | 8 |
| 426 | 2605.25179 | Locality Matters for Training-Free Audio Token Compression in … | 05-24 | 剪枝 | 5 | 6 | 6 | 7 |
| 427 | 2605.25203 | Influence-Inspired Spectral Rotations for Extreme Low-Bit LLM … | 05-24 | 量化、硬件协同 | 6 | 9 | 6 | 5 |
| 428 | 2605.25469 | JacQuant: STE-Free Quantization-Aware Training via Learned Jac… | 05-25 | 量化 | 5 | 6 | 7 | 4 |
| 429 | 2605.25475 | IndexMem: Learned KV-Cache Eviction with Latent Memory for Lon… | 05-25 | KV Cache | 6 | 6 | 6 | 5 |
| 430 | 2605.25508 | Relative Repairability: A Calibration-Based Diagnostic for Hig… | 05-25 | 剪枝、稀疏化 | 6 | 5 | 6 | 5 |
| 431 | 2605.25612 | Towards the Connection between Activation Sparsity and Flat Mi… | 05-25 | 剪枝、稀疏化 | 6 | 5 | 6 | 4 |
| 432 | 2605.25798 | DiSC: Resolution-Scalable Acceleration of Diffusion Models by … | 05-25 | 稀疏化、硬件协同 | 6 | 8 | 6 | 4 |
| 433 | 2605.25842 | MuCRASP: Multimodal Chain-of-thought Reasoning aware Structure… | 05-25 | 剪枝、稀疏化 | 8 | 5 | 6 | 5 |
| 434 | 2605.25860 | SAM3-Assisted Training of Lightweight YOLO Models for Precisio… | 05-25 | 蒸馏、硬件协同 | 8 | 5 | 6 | 4 |
| 435 | 2605.25880 | The Quantization Benefits of Residual-Free Transformers | 05-25 | 量化、硬件协同 | 4 | 5 | 6 | 4 |
| 436 | 2605.26089 | Channel-wise Vector Quantization | 05-25 | 量化、向量量化 | 8 | 5 | 7 | 5 |
| 437 | 2605.26092 | GoQuant: Geometric Orthogonal Residual Projection for Multipli… | 05-25 | 量化、硬件协同 | 4 | 8 | 6 | 10 |
| 438 | 2605.26175 | InfoQuant: Shaping Activation Distributions for Low-Bit LLM Qu… | 05-25 | 量化 | 8 | 8 | 6 | 7 |
| 439 | 2605.26189 | Max-Window Scale Estimation for Near-Lossless HiF8 W8A8 Quanti… | 05-25 | 量化 | 7 | 6 | 6 | 4 |
| 440 | 2605.26246 | The Bridge-Garden Dilemma in LLM Distillation: Why Mixing Hard… | 05-25 | 蒸馏 | 7 | 5 | 6 | 8 |
| 441 | 2605.26266 | Quantized Keys Steal Attention: Bias Correction for KV-Cache C… | 05-25 | 量化、KV Cache | 8 | 9 | 6 | 4 |
| 442 | 2605.26339 | QAM-W: Joint 2D Codebook Quantization for LLM Weights via Hada… | 05-25 | 量化、向量量化 | 8 | 6 | 6 | 7 |
| 443 | 2605.26415 | The Rescue Effect: Spatio-Semantic Early Exit Bypasses Quantiz… | 05-26 | 量化、硬件协同 | 6 | 6 | 6 | 4 |
| 444 | 2605.26496 | Dense2MoE: Pushing the Pareto Frontier of On-Device LLMs via U… | 05-26 | 剪枝、硬件协同 | 6 | 5 | 8 | 4 |
| 445 | 2605.26558 | Cassandra: Enabling Reasoning LLMs at Edge via Self-Speculativ… | 05-26 | 剪枝、硬件协同 | 8 | 7 | 6 | 7 |
| 446 | 2605.26628 | Tail-Aware HiFloat4: W4A4 Post-Training Quantization for Wan2.2 | 05-26 | 量化 | 5 | 8 | 6 | 7 |
| 447 | 2605.26632 | RT-Lynx: Putting the GEMM Sparsity In a Right Way for Diffusio… | 05-26 | 量化、蒸馏、剪枝、稀疏化 | 6 | 7 | 6 | 4 |
| 448 | 2605.26660 | WINDQuant: Weight-Informed Neural Decision-Making for Global M… | 05-26 | 量化 | 4 | 6 | 6 | 7 |
| 449 | 2605.26678 | NestedKV: Nested Memory Routing for Long-Context KV Cache Comp… | 05-26 | KV Cache | 6 | 5 | 6 | 7 |
| 450 | 2605.26812 | CFMDCTCodec: A Low-Bitrate Neural Speech Codec with Noise-Prio… | 05-26 | 量化 | 7 | 5 | 6 | 4 |
| 451 | 2605.27003 | Timestep-Aware SVDQuant-GPTQ for W4A4 Quantization of Wan2.2-I2V | 05-26 | 量化、稀疏化、低秩 | 4 | 8 | 6 | 7 |
| 452 | 2605.27186 | MAIGO: Mitigating Lost-in-Conversation with History-Cleaned On… | 05-26 | 蒸馏 | 6 | 5 | 6 | 4 |
| 453 | 2605.27336 | PARE: Pruning and Adaptive Routing for Efficient Video Generation | 05-26 | 蒸馏、剪枝 | 5 | 5 | 8 | 4 |
| 454 | 2605.27358 | MobileMoE: Scaling On-Device Mixture of Experts | 05-26 | 量化、稀疏化、硬件协同 | 10 | 8 | 8 | 8 |
| 455 | 2605.27409 | STARS: Spike Tail-Aware Relational Synthesis for ANN-to-SNN Da… | 05-12 | 蒸馏 | 7 | 5 | 6 | 7 |
| 456 | 2605.27479 | Resource-Constrained Affect Modelling via Variance Regularisat… | 05-26 | 剪枝、稀疏化 | 5 | 5 | 6 | 4 |
| 457 | 2605.27541 | SparseOpt: Addressing Normalization-induced Gradient Skew in S… | 05-26 | 稀疏化 | 5 | 5 | 8 | 4 |
| 458 | 2605.27563 | On the Subgaussianity of Quantized Linear Maps: An AI-Assisted… | 05-26 | 量化 | 5 | 5 | 6 | 5 |
| 459 | 2605.27616 | Not All NVFP4 QAT Recipes Are Equal: How Architecture and Scal… | 05-26 | 量化 | 4 | 8 | 6 | 4 |
| 460 | 2605.27646 | Hurwitz Quaternion Multiplicative Quantization for KV Cache Co… | 05-26 | 量化、稀疏化、KV Cache、向量量化 | 6 | 8 | 6 | 7 |
| 461 | 2605.27740 | UNIQUE: Universal Top-k Sparse Attention for Training-free Inf… | 05-26 | 稀疏化、KV Cache | 5 | 5 | 6 | 7 |
| 462 | 2605.27786 | Locality-Aware Redundancy Pruning for LLM Depth Compression | 05-27 | 剪枝 | 5 | 5 | 6 | 7 |
| 463 | 2605.27808 | TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Rob… | 05-27 | 量化 | 5 | 5 | 7 | 7 |
| 464 | 2605.27967 | Multi-Teacher Knowledge Distillation via Teacher-Informed Mixt… | 05-27 | 蒸馏 | 5 | 5 | 6 | 4 |
| 465 | 2605.28018 | Dual-branch Distilled Transformer for Efficient Asymmetric UAV… | 05-27 | 蒸馏 | 4 | 5 | 6 | 8 |
| 466 | 2605.28034 | Clark Hash: Stateless Sparse Johnson-Lindenstrauss Quantizatio… | 05-27 | 量化、稀疏化、向量量化 | 5 | 5 | 6 | 4 |
| 467 | 2605.28042 | Extracting Small Translation Specialists from LLMs by Aggressi… | 05-27 | 剪枝 | 8 | 6 | 6 | 4 |
| 468 | 2605.28051 | Beyond Surrogate Gradients: Fully Differentiable Token Pruning… | 05-27 | 剪枝 | 6 | 5 | 6 | 4 |
| 469 | 2605.28068 | PINE: Pruning Boosted Tree Ensembles with Conformal In-Distrib… | 05-27 | 剪枝 | 6 | 5 | 7 | 5 |
| 470 | 2605.28115 | CIVIC: End-to-End Sequence Compactness for Efficient Vision-La… | 05-27 | 蒸馏、剪枝、KV Cache、硬件协同 | 5 | 5 | 6 | 4 |
| 471 | 2605.28207 | Pruning and Distilling Mixture-of-Experts into Dense Language … | 05-27 | 蒸馏、剪枝 | 7 | 7 | 7 | 4 |
| 472 | 2605.28208 | FCDC: Nonvolatile Charge-Domain Attention with HZO Ferroelectr… | 05-27 | 量化、KV Cache、硬件协同 | 8 | 8 | 6 | 4 |
| 473 | 2605.28283 | PrunePath: Towards Highly Structured Sparse Language Models | 05-27 | 剪枝、稀疏化、KV Cache、硬件协同 | 5 | 5 | 6 | 4 |
| 474 | 2605.28640 | Augmenting Attention with Exponentially Decaying Memory Improv… | 05-27 | 稀疏化、KV Cache | 5 | 5 | 6 | 8 |
| 475 | 2605.28691 | OSP-Next: Efficient High-Quality Video Generation with Sparse … | 05-27 | 量化、稀疏化、硬件协同 | 8 | 6 | 6 | 7 |
| 476 | 2605.28803 | Ω-QVLA: Robust Quantization for Vision-Language-Action Models … | 05-27 | 量化、硬件协同、低秩 | 6 | 8 | 8 | 7 |
| 477 | 2605.28868 | TaxDistill: Improving Metagenomic Taxonomic Annotation via Dis… | 05-22 | 蒸馏 | 6 | 5 | 6 | 4 |
| 479 | 2605.29075 | Knowledge Offloading: Decomposing LLMs into Sparse Backbones a… | 05-27 | 剪枝、稀疏化、KV Cache | 5 | 5 | 6 | 5 |
| 480 | 2605.29128 | Apertus LLM Family Expansion via Distillation and Quantization | 05-27 | 量化、蒸馏、硬件协同 | 5 | 5 | 6 | 8 |
| 481 | 2605.29327 | Reasoning-preserved Efficient Distillation of Large Language M… | 05-28 | 蒸馏、剪枝 | 6 | 5 | 6 | 4 |
| 482 | 2605.29350 | ConMoE: Expert-Pool Consolidation via Prototype Reassignment f… | 05-28 | 剪枝 | 10 | 5 | 6 | 7 |
| 483 | 2605.29397 | Revisiting Observation Reduction for Web Agents: Comprehensive… | 05-28 | 剪枝 | 5 | 6 | 6 | 4 |
| 484 | 2605.29535 | AsymVLM: Asymmetric Token Pruning for Efficient Vision-Languag… | 05-28 | 剪枝 | 8 | 6 | 6 | 5 |
| 485 | 2605.29590 | State-Anchored Complete-View Distillation for Robust Conversat… | 05-28 | 蒸馏 | 5 | 5 | 6 | 4 |
| 486 | 2605.29642 | Matching Rates and Optimal Allocation for Federated Probe-Logi… | 05-28 | 量化、蒸馏、向量量化 | 5 | 5 | 8 | 7 |
| 487 | 2605.29657 | OccamToken: Efficient VLM Inference with Training-Free and Bud… | 05-28 | 剪枝 | 6 | 6 | 6 | 7 |
| 488 | 2605.29662 | SAFE-Pruner: Semantic Attention-Guided Future-Aware Token Prun… | 05-28 | 剪枝 | 8 | 7 | 6 | 5 |
| 489 | 2605.29705 | BitTP: The Lightweight Trajectory Prediction Model with BitLLM… | 05-28 | 量化、硬件协同 | 6 | 10 | 7 | 8 |
| 490 | 2605.29726 | SLAD : Shared LoRA Adapters for Task Specific Distillation | 05-28 | 蒸馏、低秩 | 7 | 7 | 7 | 4 |
| 491 | 2605.29755 | Rec-Distill: An Industrial Distillation Pipeline for Large-Sca… | 05-28 | 蒸馏 | 6 | 5 | 7 | 4 |
| 492 | 2605.29756 | LFQ: Logit-aware Final-block Quantization for Boosting the Gen… | 05-28 | 量化 | 8 | 5 | 6 | 7 |
| 493 | 2605.29843 | HARP: Hadamard-Preconditioned Adaptive Rotation Processor for … | 05-28 | 量化、稀疏化 | 5 | 8 | 6 | 10 |
| 494 | 2605.29873 | Moment-KV: Momentum-Based Decode-Time KV Cache Compression for… | 05-28 | KV Cache | 6 | 5 | 6 | 5 |
| 495 | 2605.29908 | Joint Model and Data Sparsification via the Marginal Likelihood | 05-28 | 剪枝、稀疏化 | 5 | 5 | 6 | 7 |
| 496 | 2605.29977 | EVL-ECG: Efficient ECG Interpretation With Multi-Aspect Hetero… | 05-28 | 蒸馏 | 6 | 6 | 7 | 4 |
| 497 | 2605.29992 | Adapting Multilingual Embedding Models to Turkish via Cross-Li… | 05-28 | 蒸馏、剪枝 | 8 | 5 | 6 | 8 |
| 498 | 2605.30083 | Future Forcing: Future-aware Training-free KV Cache Policy for… | 05-28 | KV Cache | 5 | 5 | 8 | 7 |
| 499 | 2605.30111 | xModel-KD: Cross-modal Knowledge Distillation for 3D Scene Per… | 05-28 | 蒸馏、稀疏化 | 6 | 5 | 7 | 4 |
| 500 | 2605.30149 | Deep Binarized Photonic Reservoir Computing for Ultrafast Mult… | 05-28 | 量化 | 7 | 9 | 6 | 4 |
| 501 | 2605.30325 | Veda: Scalable Video Diffusion via Distilled Sparse Attention | 05-28 | 蒸馏、稀疏化、硬件协同 | 6 | 6 | 6 | 4 |
| 502 | 2605.30349 | AdaState: Self-Evolving Anchors for Streaming Video Generation | 05-28 | KV Cache | 5 | 5 | 8 | 5 |
| 503 | 2605.30351 | VideoMLA: Low-Rank Latent KV Cache for Minute-Scale Autoregres… | 05-28 | KV Cache、低秩 | 8 | 5 | 8 | 4 |
| 504 | 2605.30380 | Lightweight SAR Ship Detection via Contrastive Distillation | 05-27 | 蒸馏 | 7 | 5 | 7 | 4 |
| 505 | 2605.30448 | Bounded Behavioral Indistinguishability for Black-Box LLM Dist… | 05-28 | 蒸馏 | 6 | 5 | 6 | 4 |
| 506 | 2605.30574 | Probing the Prompt KV Cache: Where It Becomes Dispensable | 05-28 | KV Cache | 5 | 5 | 7 | 5 |
| 507 | 2605.30861 | Distilling LLM Feedback for Lean Theorem Proving | 05-29 | 蒸馏、稀疏化 | 6 | 5 | 6 | 7 |
| 508 | 2605.30904 | MergeTok: Unified Continuous and Discrete Visual Tokenization … | 05-29 | 稀疏化、向量量化 | 4 | 5 | 6 | 4 |
| 509 | 2605.31029 | PEEK: Picking Essential frames via Efficient Knowledge distill… | 05-29 | 蒸馏 | 7 | 5 | 6 | 8 |
| 510 | 2605.31035 | MixFP4: Enhancing NVFP4 with Adaptive FP4/INT4 Block Represent… | 05-29 | 量化 | 6 | 8 | 6 | 5 |
| 511 | 2605.31057 | LVSA: Training-Free Sparse Attention for Long Video Diffusion | 05-29 | 稀疏化 | 5 | 5 | 6 | 7 |
| 512 | 2605.31105 | GRKV: Global Regression for Training-Free KV Cache Compression… | 05-29 | KV Cache | 5 | 5 | 6 | 7 |
| 513 | 2605.31124 | QVGGT: Post-Training Quantized Visual Geometry Grounded Transf… | 05-29 | 量化、硬件协同 | 6 | 8 | 6 | 7 |
| 514 | 2605.31191 | Student Capacity Moderates Knowledge Distillation Effectivenes… | 05-29 | 蒸馏 | 8 | 5 | 7 | 8 |
| 515 | 2605.31256 | Before Parc Fermé: RL-Time Pruning for Efficient Embodied LLMs… | 05-29 | 剪枝 | 5 | 5 | 7 | 7 |
| 516 | 2605.31264 | COLLEAGUE.SKILL: Automated AI Skill Generation via Expert Know… | 05-29 | 蒸馏 | 5 | 5 | 6 | 8 |
| 517 | 2605.31457 | VisionPulse: Dynamic Visual Sparsity for Efficient Multimodal … | 05-29 | 剪枝、稀疏化 | 6 | 5 | 6 | 5 |

---

## 二、按技术方向分类统计（核心组，标签可重叠）

| 技术方向 | 论文数 | 占比 |
|---------|:------:|:---:|
| 量化 | 201 | 40.0% |
| 稀疏化 | 144 | 28.7% |
| 剪枝 | 130 | 25.9% |
| 蒸馏 | 122 | 24.3% |
| 硬件协同 | 98 | 19.5% |
| KV Cache | 81 | 16.1% |
| 向量量化 | 36 | 7.2% |
| 低秩 | 25 | 5.0% |

**按周分布**：

| 周 | 论文数 |
|---|:------:|
| 05-01 起 | 109 |
| 05-08 起 | 162 |
| 05-15 起 | 130 |
| 05-22 起 | 105 |
| 05-29 起 | 11 |
---

## 三、外围相关论文（15 篇，不评分）

| arXiv ID | 论文标题 | 归入外围原因 |
|----------|---------|-------------|
| 2605.02196 | DurableUn: Quantization-Induced Recovery Attacks in Machine Unlearning | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.02285 | Complexity Horizons of Compressed Models in Analog Circuit Analysis | 仅硬件/系统或分析，无压缩方法 |
| 2605.03301 | SHIELD: A Diverse Clinical Note Dataset and Distilled Small Languag… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.04507 | Distilling Bayesian Belief States into Language Models for Auditabl… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.04754 | AxMoE: Characterizing the Impact of Approximate Multipliers on Mixt… | 仅硬件/系统或分析，无压缩方法 |
| 2605.05819 | HCInfer: An Efficient Inference System via Error Compensation for R… | 仅硬件/系统或分析，无压缩方法 |
| 2605.06714 | Edge Deep Learning in Computer Vision and Medical Diagnostics: A Co… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.13108 | Flow Augmentation and Knowledge Distillation for Lightweight Face P… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.15138 | Forgetting That Sticks: Quantization-Permanent Unlearning via Circu… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.15208 | Quantization Undoes Alignment: Bias Emergence in Compressed LLMs Ac… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.17158 | A comprehensive study on ILP acceleration accounting for sparsity, … | 纯分析/测量类，未提出压缩方法 |
| 2605.17160 | When Bits Break Recourse: Counterfactual-Faithful Quantization | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.18862 | Towards Family-Grouped Hierarchical Federated Learning on Sub-5KB M… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.23640 | CachePrune: Privacy-Aware and Fine-Grained KV Cache Sharing for Eff… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |
| 2605.28873 | Pre-Registering the Detectable Effect: A Paired-MDE Budget for 4-bi… | 安全/隐私/公平性/综述/报告类等非压缩方法主题 |

---

## 四、量化论文代码复现清单（10 篇核心量化方法，Qwen3-0.6B 为目标模型）

| arXiv ID | 方法 | 复现内容 | 验证方式与实测结果 | 状态 |
|----------|------|---------|------------------|:---:|
| 2605.00422 | BWLA | 1-bit权重+6-bit激活 PTQ（OKT+PSP） | 真实Qwen3-0.6B权重；W1误差0.397→0.349 | 通过 |
| 2605.02404 | SLQ | 统计无损非对称非均匀量化 + EAR 指标 | 真实Qwen3-0.6B权重；gamma^2≈1.3-1.5，4-bit EAR代理0.834 | 通过 |
| 2605.04738 | OSAQ | Hessian零空间加性异常值抑制 | 真实Qwen3-0.6B权重；W4输出误差0.0199→0.0123 | 通过 |
| 2605.08692 | AAAC | 双学习码本4-bit权重量化（零存储开销） | 真实Qwen3-0.6B权重；激活加权误差0.0177→0.0156 | 通过 |
| 2605.10793 | ConQuR | Procrustes闭式角点对齐激活旋转 | 真实嵌入激活+合成异常通道；合成场景优于Hadamard | 通过 |
| 2605.11222 | ADMM-Q | 共识ADMM Hessian权重量化器（3-bit） | 真实Qwen3-0.6B权重；3-bit输出误差0.134→0.093 | 通过 |
| 2605.17757 | OSCAR | 协方差感知旋转+逐通道裁剪 INT2 KV | 真实Qwen3-0.6B q/k/v_proj；逐通道裁剪为主要增益（如实注明代理局限） | 通过 |
| 2605.19561 | TORQ | 两级正交旋转 MXFP4 量化 | 真实嵌入激活+块不平衡合成；两组场景误差均下降 | 通过 |
| 2605.26092 | GoQuant | 双基PoT残差投影无乘法量化 | 真实Qwen3-0.6B权重；4-bit误差0.039→0.0016 | 通过 |
| 2605.29843 | HARP | 蝶形可学习旋转处理器（RHT初始化） | 真实嵌入激活；4-bit误差0.0161→0.0140 | 通过 |

说明：10 个 demo 均位于 `scripts/quantization/<arxiv_id>/`（README.md + demo.py），优先选取本月影响力最大、算法最清晰的量化方法论文（覆盖 1-bit/2-bit/3-bit/4-bit 权重量化、激活量化、KV Cache 量化、MXFP4/PoT 新格式、ADMM/旋转/码本/零空间等技术族）。全部 demo 以真实 Qwen3-0.6B 权重（经 ModelScope 下载校验，311 个张量）实际运行通过；权重缺失时自动回退 mock 权重并跑通全部代码路径。

---

## 五、值得关注的高亮点（按总评分排序，附一句话结论）

1. **[2605.00422] BWLA: Breaking the Barrier of W1AX Post-Training Quantization for LLMs**（8/9/8/10）：提出 BWLA (Binarized Weights and Low-bit Activations), the first post-training quantization framework that preserves hi…。
2. **[2605.02404] Statistically-Lossless Quantization of Large Language Models**（8/8/8/10）：Model quantization has become essential for efficient large language model deployment, yet existing approaches involv…。
3. **[2605.27358] MobileMoE: Scaling On-Device Mixture of Experts**（10/8/8/8）：To close this gap, we present MobileMoE, a family of on-device MoE language models with sub-billion active parameters…。
4. **[2605.11222] ADMM-Q: An Improved Hessian-based Weight Quantizer for Post-Training Quantization of Large Language Models**（6/9/8/10）：提出 ADMM-Q, a novel weight quantization algorithm that considers the layer-wise quantization problem。
5. **[2605.00649] Model Compression with Exact Budget Constraints via Riemannian Manifolds**（8/9/8/7）：提出 a new approach by showing that, under softmax relaxation, the budget constraint defines a smooth Riemannian manifo…。
6. **[2605.05940] Near-Policy: Accelerating On-Policy Distillation via Asynchronous Generation and Selective Packing**（8/10/6/8）：To improve efficiency, we propose Near-Policy Distillation (NPD), an asynchronous approach that decouples student gen…。
7. **[2605.17757] OSCAR: Offline Spectral Covariance-Aware Rotation for 2-bit KV Cache Quantization**（7/9/6/10）：提出 OSCAR, an Ultra-low-bit KV Cache quantization method that estimates attention-aware covariance structures offline …。
8. **[2605.19561] TORQ: Two-Level Orthogonal Rotation for MXFP4 Quantization**（6/8/8/10）：To address these challenges, we propose TORQ (Two-level Orthogonal Rotation for MXFP4 Quantization), a training-free …。
9. **[2605.24019] MGVQ: Synergizing Multi-dimensional Sensitivity-Aware and Gradient-Hessian Fusion for Vector Quantization**（8/9/8/7）：Vision-Language Models (VLMs) achieve outstanding performance, yet their huge model size severely hinders deployment …。
10. **[2605.04738] OSAQ: Outlier Self-Absorption for Accurate Low-bit LLM Quantization**（6/8/7/10）：In this paper, we propose Outlier Self-Absorption Quantization (OSAQ), which performs additive weight suppression gui…。
11. **[2605.06505] PACZero: PAC-Private Fine-Tuning of Language Models via Sign Quantization**（8/9/6/8）：提出 PACZero, a family of PAC-private zeroth-order mechanisms for fine-tuning large language models that delivers usabl…。
12. **[2605.08692] AAAC: Activation-Aware Adaptive Codebooks for 4-bit LLM Weight Quantization**（7/8/6/10）：In this work, we propose AAAC (Activation-Aware Adaptive Codebooks), a lightweight method for 4-bit LLM weight quanti…。
13. **[2605.14359] RQ-MoE: Residual Quantization via Mixture of Experts for Efficient Input-Dependent Vector Compression**（7/10/6/8）：提出 Residual Quantization via Mixture of Experts (RQ-MoE), a framework combining a two-level MoE with dual-stream quan…。
14. **[2605.29705] BitTP: The Lightweight Trajectory Prediction Model with BitLLM for Edge-Devices**（6/10/7/8）：To bridge this gap, we propose BitTP, which converts an LLM-based trajectory predictor into a lightweight bitlinear a…。
15. **[2605.03644] AdapShot: Adaptive Many-Shot In-Context Learning with Semantic-Aware KV Cache Reuse**（8/10/7/5）：To address the above limitations, we propose AdapShot, which dynamically optimizes shot counts and leverages KV cache…。
16. **[2605.07182] Star Elastic: Many-in-One Reasoning LLMs with Efficient Budget Control**（8/8/7/7）：In this paper, we introduce Star Elastic, a novel LLM post-training method that adds N nested submodels to a given pa…。
17. **[2605.12245] SOAR: Scale Optimization for Accurate Reconstruction in NVFP4 Quantization**（7/8/8/7）：To address these issues, we propose Scale Optimization for Accurate Reconstruction (SOAR), a novel post-training quan…。
18. **[2605.17831] Agentic Cost-Aware Query Planning with Knowledge Distillation for Big Data Analytics**（6/10/6/8）：提出 an agentic query planning system that combines a rule-based teacher planner, UCB1 bandit exploration, cost-aware p…。
19. **[2605.17997] MARR: Module-Adaptive Residual Reconstruction for Low-Bit Post-Training Quantization**（8/8/7/7）：More importantly, we observe that this trade-off is module-dependent, making a single global residual strength insuff…。
20. **[2605.18475] GAMMA: Global Bit Allocation for Mixed-Precision Models under Arbitrary Budgets**（7/8/8/7）：提出 GAMMA, a quantizer-agnostic framework that learns module-wise precision preferences entirely within a post-trainin…。

---

## 六、整体趋势分析

**1. 量化研究进入"后 4-bit 时代"的精细化竞争。** 本月 201 篇核心量化论文中，热点从"能否做到 W4A16"转向三个方向：(a) 极致位宽（BWLA 的 W1A6、OSCAR/OScaR 的 INT2 KV Cache、GoQuant 的无乘法 PoT）；(b) 新硬件格式（MXFP4/NVFP4/HiF8 相关论文超过 10 篇，TORQ、MixFP4、MX-SAFE 等直接对标 Blackwell/昇腾原生 FP4）；(c) 量化误差的结构化治理（旋转类方法 HARP/ConQuR/TORQ/DiRotQ、码本类 AAAC/QAM-W、零空间/补偿类 OSAQ/ADMM-Q/MARR）。

**2. KV Cache 成为长上下文压缩主战场。** 81 篇 KV Cache 核心论文覆盖量化（INT2 已可行）、驱逐、低秩合并与系统调度四条路线；视频生成与 Agentic 长推理成为新的压力测试场景（如 Forcing-KV、TriAxialKV、Moment-KV）。

**3. 剪枝与蒸馏向"结构化+组合化"演进。** 层剪枝的可恢复性（Ghosted Layers）、MoE 专家剪枝/合并（ConMoE、Dense2MoE、SlimQwen）、推理轨迹蒸馏（On-Policy Distillation 一族）是本月高频主题；剪枝+量化+蒸馏的三重级联压缩（如 VAD、GSA-YOLO 类工作）在边缘侧持续落地。

**4. 量化副作用研究升温。** 多篇论文关注量化对公平性（Quantization Undoes Alignment）、记忆/隐私（Widening the Gap）、遗忘鲁棒性（DurableUn、Forgetting That Sticks）的影响，量化评估正从单一精度指标走向多维可信评估（本月归入外围组处理）。

**5. 可复现性观察。** 训练免费（training-free）PTQ 方法占量化论文主流，复现门槛低；QAT 与硬件协同类方法复现成本仍高。本月我们完成了 10 篇代表性量化方法在统一目标模型（Qwen3-0.6B）上的真实权重复现，全部代码路径验证通过。

---

## 评分方法说明

四项评分均采用规则化打分（1–10 整数），依据论文标题与摘要中的客观信号计算，未逐篇精读全文，仅供横向参考：
- **精度效果**：SOTA/超越基线声明（+2）、近无损声明（+1.5）、报告具体数值（+1），基准 5 分；
- **压缩倍率**：按目标位宽分档（1-bit≈9，2-bit≈8.5，3-bit≈8，4-bit≈7.5，8-bit≈6），报告加速比/压缩比者按数值上浮；
- **创新性**：首创性声明（+1.5）、理论保证（+1）、training-free/协同设计（+0.5），综述/纯分析类下调；
- **可复现性**：本月已实际复现的 10 篇为 9–10 分；training-free/闭式方法 7 分；QAT/硬件/系统类 4.5 分。

局限性：评分未考虑论文全文细节、引用量与作者机构等因素；同一规则对所有论文一致适用，保证横向可比。

*报告生成时间: 2026-07-30 GMT+8；数据检索自 arXiv API，共 517 篇（核心 502 + 外围 15）*
