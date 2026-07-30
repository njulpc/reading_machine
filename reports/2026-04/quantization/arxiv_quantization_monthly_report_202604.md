# ArXiv 模型压缩领域论文月报（2026 年 4 月）

**收集日期范围**: 2026-04-01 ~ 2026-04-30（全月）  
**检索范围**: arXiv cs.LG / cs.CL / cs.CV / cs.AI / cs.NE / cs.AR / stat.ML / eess.AS / eess.IV 当月全部 11,110 篇新投稿，经标题初筛（842 篇）→ 主题过滤（365 篇）→ 摘要逐篇审核，最终保留 **216 篇**模型压缩核心论文  
**数据来源**: arXiv.org  
**分析方法**: 每篇论文附六段式中文深度分析（`papers/2026-04/<arxiv_id>/tech_analysis.md`）；核心量化方法附代码复现（`scripts/quantization/<arxiv_id>/`）

---

## 一、论文总览与评分总表

本月共收录 **216** 篇，技术方向分布（一篇可多属）：蒸馏 101 篇、剪枝 62 篇、量化 60 篇、KV cache 压缩 23 篇、低秩 16 篇、混合精度 8 篇。

评分维度（各 1–10 分，规则见附录）：**精**=精度效果，**压**=压缩倍率，**新**=创新性，**复**=可复现性。

| 序号 | arXiv ID | 论文标题 | 技术分类 | 精 | 压 | 新 | 复 |
|:---:|---------|---------|---------|:-:|:-:|:-:|:-:|
| 1 | 2604.00004 | LinearARD: Linear-Memory Attention Distillation for RoPE Restoration | 蒸馏 | 8 | 3 | 7 | 9 |
| 2 | 2604.00223 | Diversity-Aware Reverse Kullback-Leibler Divergence for Large Language Model Distillation | 蒸馏 | 8 | 3 | 9 | 3 |
| 3 | 2604.00529 | MF-QAT: Multi-Format Quantization-Aware Training for Elastic Inference | 量化 | 5 | 4 | 6 | 3 |
| 4 | 2604.00586 | More Human, More Efficient: Aligning Annotations with Quantized SLMs | 量化 | 7 | 7 | 5 | 8 |
| 5 | 2604.00626 | A Survey of On-Policy Distillation for Large Language Models | 蒸馏 | 5 | 3 | 5 | 3 |
| 6 | 2604.00757 | IWP: Token Pruning as Implicit Weight Pruning in Large Vision Language Models | 剪枝 | 5 | 4 | 8 | 3 |
| 7 | 2604.00821 | Optimal Brain Decomposition for Accurate LLM Low-Rank Approximation | 低秩 | 7 | 3 | 9 | 3 |
| 8 | 2604.00827 | Video Patch Pruning: Efficient Video Instance Segmentation via Early Token Reduction | 剪枝 | 8 | 5 | 7 | 4 |
| 9 | 2604.01042 | Integer-State Dynamics of Quantized Spiking Neural Networks for Efficient Hardware Acceleration | 量化 | 5 | 4 | 5 | 3 |
| 10 | 2604.01076 | A Hierarchical Importance-Guided Multi-objective Evolutionary Framework for Deep Neural Network Pruning | 剪枝 | 6 | 4 | 8 | 4 |
| 11 | 2604.01167 | AdaLoRA-QAT: Adaptive Low-Rank and Quantization-Aware Segmentation | 量化、低秩、混合精度 | 6 | 4 | 6 | 8 |
| 12 | 2604.01193 | Embarrassingly Simple Self-Distillation Improves Code Generation | 蒸馏 | 6 | 3 | 4 | 9 |
| 13 | 2604.01608 | From Multi-Agent to Single-Agent: When Is Skill Distillation Beneficial? | 蒸馏 | 9 | 5 | 9 | 4 |
| 14 | 2604.01609 | Swift-SVD: Theoretical Optimality Meets Practical Efficiency in Low-Rank LLM Compression | 低秩 | 7 | 6 | 10 | 8 |
| 15 | 2604.01766 | FSKD: Monocular Forest Structure Inference via LiDAR-to-RGBI Knowledge Distillation | 蒸馏 | 9 | 3 | 8 | 4 |
| 16 | 2604.02061 | Diff-KD: Diffusion-based Knowledge Distillation for Collaborative Perception under Corruptions | 蒸馏 | 8 | 3 | 6 | 4 |
| 17 | 2604.02119 | AA-SVD : Anchored and Adaptive SVD for Large Language Model Compression | 低秩 | 6 | 4 | 6 | 3 |
| 18 | 2604.02288 | Unifying Group-Relative and Self-Distillation Policy Optimization via Sample Routing | 蒸馏 | 9 | 3 | 9 | 5 |
| 19 | 2604.02509 | Rapidly deploying on-device eye tracking by distilling visual foundation models | 蒸馏 | 6 | 3 | 8 | 4 |
| 20 | 2604.02556 | Fast NF4 Dequantization Kernels for Large Language Model Inference | 量化 | 5 | 7 | 4 | 9 |
| 21 | 2604.02570 | WSVD: Weighted Low-Rank Approximation for Fast and Efficient Execution of Low-Precision Vision-Language Models | 量化、低秩 | 7 | 4 | 5 | 8 |
| 22 | 2604.02621 | Reinforcement Learning-based Knowledge Distillation with LLM-as-a-Judge | 蒸馏 | 5 | 3 | 6 | 3 |
| 23 | 2604.02638 | AXELRAM: Quantize Once, Never Dequantize | 量化、KV cache | 5 | 5 | 6 | 9 |
| 24 | 2604.02659 | Low-Rank Compression of Pretrained Models via Randomized Subspace Iteration | 低秩 | 7 | 3 | 9 | 3 |
| 25 | 2604.02697 | LieTrunc-QNN: Lie Algebra Truncation and Quantum Expressivity Phase Transition from LiePrune to Provably Stable Quantum Neural Networks | 剪枝 | 4 | 5 | 6 | 3 |
| 26 | 2604.02816 | QAPruner: Quantization-Aware Vision Token Pruning for Multimodal Large Language Models | 量化、剪枝 | 7 | 8 | 8 | 4 |
| 27 | 2604.02819 | Student-in-the-Loop Chain-of-Thought Distillation via Generation-Time Selection | 剪枝、蒸馏 | 7 | 4 | 8 | 3 |
| 28 | 2604.02956 | Collaborative Multi-Mode Pruning for Vision-Language Models | 剪枝 | 6 | 5 | 9 | 8 |
| 29 | 2604.03072 | MI-Pruner: Crossmodal Mutual Information-guided Token Pruner for Efficient MLLMs | 剪枝 | 6 | 5 | 6 | 3 |
| 30 | 2604.03110 | Multi-Aspect Knowledge Distillation for Language Model with Low-rank Factorization | 蒸馏、低秩 | 4 | 3 | 5 | 3 |
| 31 | 2604.03128 | Self-Distilled RLVR | 蒸馏 | 5 | 3 | 5 | 3 |
| 32 | 2604.03154 | DSBD: Dual-Aligned Structural Basis Distillation for Graph Domain Adaptation | 蒸馏 | 6 | 3 | 9 | 3 |
| 33 | 2604.03192 | Reliability Gated Multi-Teacher Distillation for Low Resource Abstractive Summarization | 蒸馏 | 6 | 4 | 4 | 5 |
| 34 | 2604.03258 | SoLA: Leveraging Soft Activation Sparsity and Low-Rank Decomposition for Large Language Model Compression | 低秩 | 7 | 4 | 7 | 4 |
| 35 | 2604.03270 | Knowledge Packs: Zero-Token Knowledge Delivery via KV Cache Injection | KV cache | 7 | 5 | 8 | 5 |
| 36 | 2604.03336 | NativeTernary: A Self-Delimiting Binary Encoding with Unary Run-Length Hierarchy Markers for Ternary Neural Network Weights, Structured Data, and General Computing Infrastructure | 量化 | 6 | 10 | 4 | 4 |
| 37 | 2604.03420 | Zero-Shot Quantization via Weight-Space Arithmetic | 量化 | 5 | 4 | 4 | 3 |
| 38 | 2604.03803 | R\'enyi Attention Entropy for Patch Pruning | 剪枝 | 5 | 4 | 4 | 3 |
| 39 | 2604.03841 | Training a Student Expert via Semi-Supervised Foundation Model Distillation | 蒸馏 | 7 | 3 | 6 | 4 |
| 40 | 2604.03873 | SODA: Semi On-Policy Black-Box Distillation for Large Language Models | 蒸馏 | 8 | 3 | 8 | 5 |
| 41 | 2604.03950 | Diagonal-Tiled Mixed-Precision Attention for Efficient Low-Bit MXFP Inference | 量化、混合精度 | 4 | 4 | 4 | 8 |
| 42 | 2604.03957 | BWTA: Accurate and Efficient Binarized Transformer by Algorithm-Hardware Co-design | 量化 | 6 | 10 | 8 | 4 |
| 43 | 2604.04013 | RUQuant: Towards Refining Uniform Quantization for Large Language Models | 量化 | 6 | 8 | 8 | 4 |
| 44 | 2604.04018 | 1.x-Distill: Breaking the Diversity, Quality, and Efficiency Barrier in Distribution Matching Distillation | 蒸馏 | 8 | 6 | 9 | 4 |
| 45 | 2604.04170 | Incomplete Multi-View Multi-Label Classification via Shared Codebook and Fused-Teacher Self-Distillation | 蒸馏 | 5 | 3 | 5 | 8 |
| 46 | 2604.04356 | REAM: Merging Improves Pruning of Experts in LLMs | 量化、剪枝 | 8 | 5 | 7 | 3 |
| 47 | 2604.04461 | DP-OPD: Differentially Private On-Policy Distillation for Language Models | 蒸馏 | 7 | 3 | 8 | 8 |
| 48 | 2604.04701 | MUXQ: Mixed-to-Uniform Precision MatriX Quantization via Low-Rank Outlier Decomposition | 量化、低秩 | 4 | 4 | 7 | 4 |
| 49 | 2604.04722 | Don't Waste Bits! Adaptive KV-Cache Quantization for Lightweight On-Device LLMs | 量化、KV cache | 7 | 9 | 6 | 4 |
| 50 | 2604.04972 | RCP: Representation Consistency Pruner for Mitigating Distribution Shift in Large Vision-Language Models | 剪枝 | 8 | 5 | 10 | 3 |
| 51 | 2604.04988 | Prune-Quantize-Distill: An Ordered Pipeline for Efficient Neural Network Compression | 量化、剪枝、蒸馏 | 6 | 5 | 5 | 4 |
| 52 | 2604.05012 | Comparative Characterization of KV Cache Management Strategies for LLM Inference | KV cache | 6 | 5 | 5 | 3 |
| 53 | 2604.05171 | Modality-Aware and Anatomical Vector-Quantized Autoencoding for Multimodal Brain MRI | 量化 | 4 | 4 | 7 | 3 |
| 54 | 2604.05303 | Jeffreys Flow: Robust Boltzmann Generators for Rare Event Sampling via Parallel Tempering Distillation | 蒸馏 | 4 | 3 | 4 | 3 |
| 55 | 2604.05366 | 3DTurboQuant: Training-Free Near-Optimal Quantization for 3D Reconstruction Models | 量化、KV cache、剪枝 | 5 | 7 | 5 | 8 |
| 56 | 2604.05524 | Cross-Resolution Diffusion Models via Network Pruning | 剪枝 | 5 | 5 | 7 | 3 |
| 57 | 2604.05584 | Purify-then-Align: Towards Robust Human Sensing under Modality Missing with Knowledge Distillation from Noisy Multimodal Teacher | 蒸馏 | 8 | 3 | 10 | 3 |
| 58 | 2604.05643 | Graph-Based Chain-of-Thought Pruning for Reducing Redundant Reflections in Reasoning LLMs | 剪枝、蒸馏 | 4 | 5 | 5 | 3 |
| 59 | 2604.05656 | SnapFlow: One-Step Action Generation for Flow-Matching VLAs via Progressive Self-Distillation | 剪枝、蒸馏 | 7 | 7 | 6 | 4 |
| 60 | 2604.05887 | HybridKV: Hybrid KV Cache Compression for Efficient Multimodal Large Language Model Inference | KV cache、剪枝 | 5 | 4 | 7 | 4 |
| 61 | 2604.06390 | MorphDistill: Distilling Unified Morphological Knowledge from Pathology Foundation Models for Colorectal Cancer Survival Prediction | 蒸馏 | 9 | 4 | 8 | 4 |
| 62 | 2604.06421 | State-of-the-Art Arabic Language Modeling with Sparse MoE Fine-Tuning and Chain-of-Thought Distillation | 剪枝、蒸馏 | 7 | 4 | 8 | 8 |
| 63 | 2604.06515 | Efficient Quantization of Mixture-of-Experts with Theoretical Generalization Guarantees | 量化、剪枝、混合精度 | 5 | 4 | 7 | 3 |
| 64 | 2604.06542 | Does a Global Perspective Help Prune Sparse MoEs Elegantly? | 剪枝 | 6 | 5 | 6 | 5 |
| 65 | 2604.06650 | A Parameter-Efficient Transfer Learning Approach through Multitask Prompt Distillation and Decomposition for Clinical NLP | 蒸馏 | 8 | 3 | 5 | 5 |
| 66 | 2604.06691 | KD-MARL: Resource-Aware Knowledge Distillation in Multi-Agent Reinforcement Learning | 蒸馏 | 7 | 6 | 6 | 4 |
| 67 | 2604.06732 | Extraction of linearized models from pre-trained networks via knowledge distillation | 蒸馏 | 6 | 3 | 8 | 3 |
| 68 | 2604.06798 | MoBiE: Efficient Inference of Mixture of Binary Experts under Post-Training Quantization | 量化、低秩 | 7 | 8 | 9 | 9 |
| 69 | 2604.06836 | STQuant: Spatio-Temporal Adaptive Framework for Optimizer Quantization in Large Multimodal Model Training | 量化 | 5 | 4 | 8 | 4 |
| 70 | 2604.06916 | FP4 Explore, BF16 Train: Diffusion Reinforcement Learning via Efficient Rollout Scaling | 量化 | 5 | 7 | 8 | 3 |
| 71 | 2604.07329 | Distilling Photon-Counting CT into Routine Chest CT through Clinically Validated Degradation Modeling | 蒸馏 | 8 | 3 | 9 | 8 |
| 72 | 2604.07466 | Cross-Tokenizer LLM Distillation through a Byte-Level Interface | 蒸馏 | 8 | 3 | 7 | 3 |
| 73 | 2604.07674 | Weight Group-wise Post-Training Quantization for Medical Foundation Model | 量化 | 4 | 8 | 6 | 3 |
| 74 | 2604.07716 | Breaking the KV Cache Bottleneck: Fan Duality Model Achieves O(1) Decode Memory with Superior Associative Recall | KV cache | 8 | 6 | 9 | 9 |
| 75 | 2604.07776 | Structured Distillation of Web Agent Capabilities Enables Generalization | 蒸馏 | 8 | 3 | 5 | 8 |
| 76 | 2604.07812 | HAWK: Head Importance-Aware Visual Token Pruning in Multimodal Models | 剪枝 | 7 | 4 | 8 | 9 |
| 77 | 2604.07815 | AsyncTLS: Efficient Generative LLM Inference with Asynchronous Two-level Sparse Attention | KV cache、剪枝 | 7 | 5 | 6 | 5 |
| 78 | 2604.07853 | QaRL: Rollout-Aligned Quantization-Aware RL for Fast and Stable Training under Training--Inference Mismatch | 量化 | 7 | 4 | 8 | 4 |
| 79 | 2604.07894 | TSUBASA: Improving Long-Horizon Personalization via Evolving Memory and Self-Learning with Context Distillation | 蒸馏 | 7 | 3 | 6 | 4 |
| 80 | 2604.07944 | On-Policy Distillation of Language Models for Autonomous Vehicle Motion Planning | 蒸馏 | 6 | 3 | 5 | 3 |
| 81 | 2604.07953 | Pruning Extensions and Efficiency Trade-Offs for Sustainable Time Series Classification | 剪枝 | 7 | 5 | 8 | 4 |
| 82 | 2604.07955 | Rethinking Residual Errors in Compensation-based LLM Quantization | 量化 | 4 | 4 | 4 | 8 |
| 83 | 2604.08266 | Orion-Lite: Distilling LLM Reasoning into Efficient Vision-Only Driving Models | 蒸馏 | 6 | 3 | 5 | 3 |
| 84 | 2604.08426 | KV Cache Offloading for Context-Intensive Tasks | KV cache、低秩 | 6 | 4 | 5 | 4 |
| 85 | 2604.08532 | Self-Improving 4D Perception via Self-Distillation | 蒸馏 | 7 | 3 | 6 | 8 |
| 86 | 2604.08558 | WAND: Windowed Attention and Knowledge Distillation for Efficient Autoregressive Text-to-Speech Models | KV cache、蒸馏 | 6 | 4 | 7 | 4 |
| 87 | 2604.08574 | Distilling Genomic Models for Efficient mRNA Representation Learning via Embedding Matching | 蒸馏 | 8 | 3 | 5 | 3 |
| 88 | 2604.08847 | DeFakeQ: Enabling Real-Time Deepfake Detection on Edge Devices via Adaptive Bidirectional Quantization | 量化 | 7 | 4 | 9 | 3 |
| 89 | 2604.08851 | Cross-Lingual Attention Distillation with Personality-Informed Generative Augmentation for Multilingual Personality Recognition | 蒸馏 | 9 | 3 | 8 | 8 |
| 90 | 2604.08880 | Revisiting the Capacity Gap in Chain-of-Thought Distillation from a Practical Perspective | 蒸馏 | 5 | 3 | 4 | 3 |
| 91 | 2604.08971 | Modality-Aware Zero-Shot Pruning and Sparse Attention for Efficient Multimodal Edge Inference | 剪枝 | 6 | 5 | 7 | 4 |
| 92 | 2604.09076 | Cross-Modal Knowledge Distillation from Spatial Transcriptomics to Histology | 蒸馏 | 6 | 3 | 6 | 3 |
| 93 | 2604.09088 | Memory-Efficient Transfer Learning with Fading Side Networks via Masked Dual Path Distillation | 蒸馏 | 7 | 3 | 7 | 8 |
| 94 | 2604.09220 | TinyNeRV: Compact Neural Video Representations via Capacity Scaling, Distillation, and Low-Precision Inference | 量化、蒸馏 | 4 | 4 | 4 | 8 |
| 95 | 2604.09244 | 2D or 3D: Who Governs Salience in VLA Models? -- Tri-Stage Token Pruning Framework with Modality Salience Awareness | 剪枝 | 6 | 5 | 6 | 4 |
| 96 | 2604.09629 | HumorGen: Cognitive Synergy for Humor Generation in Large Language Models via Persona-Based Distillation | 蒸馏 | 7 | 3 | 6 | 3 |
| 97 | 2604.09850 | Training-Free Object-Background Compositional T2I via Dynamic Spatial Guidance and Multi-Path Pruning | 剪枝 | 5 | 4 | 7 | 3 |
| 98 | 2604.10091 | SEPTQ: A Simple and Effective Post-Training Quantization Paradigm for Large Language Models | 量化 | 7 | 4 | 8 | 3 |
| 99 | 2604.10103 | Long-Horizon Streaming Video Generation via Hybrid Attention with Decoupled Distillation | 量化、剪枝、蒸馏 | 7 | 5 | 10 | 8 |
| 100 | 2604.10235 | CodeComp: Structural KV Cache Compression for Agentic Coding | KV cache | 7 | 4 | 5 | 3 |
| 101 | 2604.10496 | CodeQuant: Unified Clustering and Quantization for Enhanced Outlier Smoothing in Low-Precision Mixture-of-Experts | 量化 | 7 | 4 | 6 | 8 |
| 102 | 2604.10539 | IceCache: Memory-efficient KV-cache Management for Long-Sequence LLMs | KV cache | 6 | 5 | 6 | 9 |
| 103 | 2604.10674 | Skill-SD: Skill-Conditioned Self-Distillation for Multi-turn LLM Agents | 蒸馏 | 7 | 3 | 7 | 8 |
| 104 | 2604.10675 | HiddenObjects: Scalable Diffusion-Distilled Spatial Priors for Object Placement | 蒸馏 | 7 | 3 | 7 | 4 |
| 105 | 2604.10677 | LIDEA: Human-to-Robot Imitation Learning via Implicit Feature Distillation and Explicit Geometry Alignment | 蒸馏 | 5 | 4 | 7 | 4 |
| 106 | 2604.10688 | SCOPE: Signal-Calibrated On-Policy Distillation Enhancement with Dual-Path Adaptive Weighting | 蒸馏 | 6 | 3 | 6 | 4 |
| 107 | 2604.10882 | DIB-OD: Preserving the Invariant Core for Robust Heterogeneous Graph Adaptation via Decoupled Information Bottleneck and Online Distillation | 蒸馏 | 6 | 3 | 9 | 3 |
| 108 | 2604.10912 | TAMISeg: Text-Aligned Multi-scale Medical Image Segmentation with Semantic Encoder Distillation | 蒸馏 | 6 | 3 | 7 | 8 |
| 109 | 2604.10923 | Mem$^2$Evolve: Towards Self-Evolving Agents via Co-Evolutionary Capability Expansion and Experience Distillation | 蒸馏 | 5 | 3 | 6 | 8 |
| 110 | 2604.10950 | Bootstrapping Video Semantic Segmentation Model via Distillation-assisted Test-Time Adaptation | 蒸馏 | 7 | 3 | 8 | 5 |
| 111 | 2604.11080 | ReSpinQuant: Efficient Layer-Wise LLM Quantization via Subspace Residual Rotation Approximation | 量化 | 6 | 7 | 8 | 3 |
| 112 | 2604.11112 | Quantum-Gated Task-interaction Knowledge Distillation for Pre-trained Model-based Class-Incremental Learning | 蒸馏 | 6 | 3 | 8 | 3 |
| 113 | 2604.11240 | Decoupled Similarity for Task-Aware Token Pruning in Large Vision-Language Models | 剪枝 | 7 | 5 | 8 | 5 |
| 114 | 2604.11501 | Quantization Dominates Rank Reduction for KV-Cache Compression | 量化、KV cache | 9 | 9 | 6 | 5 |
| 115 | 2604.11530 | Beyond Attention Scores: SVD-Based Vision Token Pruning for Efficient Vision-Language Models | 剪枝、低秩 | 6 | 5 | 10 | 3 |
| 116 | 2604.11867 | Disposition Distillation at Small Scale: A Three-Arc Negative Result | 蒸馏 | 6 | 4 | 4 | 5 |
| 117 | 2604.12002 | Self-Distillation Zero: Self-Revision Turns Binary Rewards into Dense Supervision | 蒸馏 | 8 | 3 | 7 | 9 |
| 118 | 2604.12035 | When Does Visual Token Pruning Improve Calibration? The Role of Evidence Coverage in MLLMs | 剪枝 | 5 | 5 | 4 | 4 |
| 119 | 2604.12044 | VISTA: Validation-Informed Trajectory Adaptation via Self-Distillation | 蒸馏 | 6 | 4 | 5 | 4 |
| 120 | 2604.12145 | Why Your Tokenizer Fails in Information Fusion: A Timing-Aware Pre-Quantization Fusion for Video-Enhanced Audio Tokenization | 量化 | 5 | 4 | 8 | 3 |
| 121 | 2604.12163 | Nucleus-Image: Sparse MoE for Image Generation | 剪枝 | 7 | 4 | 8 | 8 |
| 122 | 2604.12219 | Ride the Wave: Precision-Allocated Sparse Attention for Smooth Video Generation | 剪枝 | 4 | 5 | 8 | 3 |
| 123 | 2604.12358 | Why and When Visual Token Pruning Fails? A Study on Relevant Visual Information Shift in MLLMs Decoding | 剪枝 | 7 | 4 | 9 | 3 |
| 124 | 2604.12574 | Cross-Modal Knowledge Distillation for PET-Free Amyloid-Beta Detection from MRI | 蒸馏 | 4 | 3 | 4 | 8 |
| 125 | 2604.12767 | CLASP: Class-Adaptive Layer Fusion and Dual-Stage Pruning for Multimodal Large Language Models | 剪枝 | 6 | 4 | 9 | 8 |
| 126 | 2604.12782 | OSC: Hardware Efficient W4A4 Quantization via Outlier Separation in Channel Dimension | 量化 | 5 | 10 | 7 | 5 |
| 127 | 2604.13010 | Lightning OPD: Efficient Post-Training for Large Reasoning Models with Offline On-Policy Distillation | 蒸馏 | 7 | 4 | 8 | 9 |
| 128 | 2604.13016 | Rethinking On-Policy Distillation of Large Language Models: Phenomenology, Mechanism, and Recipe | 蒸馏 | 7 | 4 | 7 | 4 |
| 129 | 2604.13287 | MOONSHOT : A Framework for Multi-Objective Pruning of Vision and Large Language Models | 剪枝 | 8 | 5 | 9 | 5 |
| 130 | 2604.13332 | Selecting Feature Interactions for Generalized Additive Models by Distilling Foundation Models | 蒸馏 | 6 | 3 | 8 | 3 |
| 131 | 2604.13440 | A KL Lens on Quantization: Fast, Forward-Only Sensitivity for Mixed-Precision SSM-Transformer Models | 量化、混合精度 | 7 | 7 | 7 | 8 |
| 132 | 2604.13806 | Robust Ultra Low-Bit Post-Training Quantization via Stable Diagonal Curvature Estimate | 量化 | 7 | 4 | 7 | 4 |
| 133 | 2604.13847 | SparseBalance: Load-Balanced Long Context Training with Dynamic Sparse Attention | 剪枝 | 4 | 5 | 8 | 4 |
| 134 | 2604.14054 | $\pi$-Play: Multi-Agent Self-Play via Privileged Self-Distillation without External Data | 蒸馏 | 7 | 3 | 9 | 8 |
| 135 | 2604.14084 | TIP: Token Importance in On-Policy Distillation | 蒸馏 | 7 | 3 | 9 | 9 |
| 136 | 2604.14186 | HARNESS: Lightweight Distilled Arabic Speech Foundation Models | 蒸馏 | 6 | 3 | 4 | 3 |
| 137 | 2604.14339 | Shuffle the Context: RoPE-Perturbed Self-Distillation for Long-Context Adaptation | 蒸馏 | 6 | 4 | 6 | 5 |
| 138 | 2604.14487 | Quantization of Spiking Neural Networks Beyond Accuracy | 量化 | 4 | 5 | 7 | 4 |
| 139 | 2604.14506 | Co-distilled attention guided masked image modeling with noisy teacher for self-supervised learning on medical images | 蒸馏 | 4 | 3 | 8 | 3 |
| 140 | 2604.14572 | Don't Retrieve, Navigate: Distilling Enterprise Knowledge into Navigable Agent Skills for QA and RAG | 蒸馏 | 6 | 3 | 4 | 8 |
| 141 | 2604.14580 | TurboTalk: Progressive Distillation for One-Step Audio-Driven Talking Avatar Generation | 蒸馏 | 6 | 3 | 8 | 4 |
| 142 | 2604.14629 | Switch-KD: Visual-Switch Knowledge Distillation for Vision-Language Models | 蒸馏 | 5 | 3 | 8 | 4 |
| 143 | 2604.15016 | DLink: Distilling Layer-wise and Dominant Knowledge from EEG Foundation Models | 蒸馏 | 5 | 3 | 5 | 3 |
| 144 | 2604.15167 | When Flat Minima Fail: Characterizing INT4 Quantization Collapse After FP32 Convergence | 量化 | 6 | 7 | 4 | 9 |
| 145 | 2604.15180 | AdaSplash-2: Faster Differentiable Sparse Attention | 剪枝 | 6 | 5 | 7 | 3 |
| 146 | 2604.15188 | VisPCO: Visual Token Pruning Configuration Optimization via Budget-Aware Pareto-Frontier Learning for Vision-Language Models | 剪枝 | 4 | 4 | 6 | 3 |
| 147 | 2604.15196 | Unsupervised Skeleton-Based Action Segmentation via Hierarchical Spatiotemporal Vector Quantization | 量化 | 8 | 4 | 9 | 3 |
| 148 | 2604.15356 | Sequential KV Cache Compression via Probabilistic Language Tries: Beyond the Per-Vector Shannon Limit | 量化、KV cache | 5 | 8 | 8 | 4 |
| 149 | 2604.15408 | Dispatch-Aware Ragged Attention for Pruned Vision Transformers | 剪枝 | 7 | 5 | 5 | 3 |
| 150 | 2604.15409 | The Illusion of Equivalence: Systematic FP16 Divergence in KV-Cached Autoregressive Inference | KV cache | 6 | 4 | 7 | 4 |
| 151 | 2604.15451 | Weak-to-Strong Knowledge Distillation Accelerates Visual Learning | 蒸馏 | 9 | 5 | 7 | 5 |
| 152 | 2604.15482 | Harmonizing Multi-Objective LLM Unlearning via Unified Domain Representation and Bidirectional Logit Distillation | 蒸馏 | 7 | 3 | 9 | 3 |
| 153 | 2604.15780 | Pruning Unsafe Tickets: A Resource-Efficient Framework for Safer and More Robust LLMs | 量化、剪枝 | 5 | 4 | 4 | 4 |
| 154 | 2604.15794 | Self-Distillation as a Performance Recovery Mechanism for LLMs: Counteracting Compression and Catastrophic Forgetting | 量化、剪枝、蒸馏 | 5 | 4 | 5 | 3 |
| 155 | 2604.15871 | UniEditBench: A Unified and Cost-Effective Benchmark for Image and Video Editing via Distilled MLLMs | 蒸馏 | 5 | 3 | 5 | 9 |
| 156 | 2604.16502 | Topology-Aware Layer Pruning for Large Vision-Language Models | 剪枝 | 6 | 5 | 8 | 8 |
| 157 | 2604.16806 | Channel Attention-Guided Cross-Modal Knowledge Distillation for Referring Image Segmentation | 蒸馏 | 5 | 3 | 4 | 3 |
| 158 | 2604.16830 | The Illusion of Certainty: Decoupling Capability and Calibration in On-Policy Distillation | 蒸馏 | 5 | 3 | 7 | 8 |
| 159 | 2604.16854 | CATP: Confidence-Aware Token Pruning for Camouflaged Object Detection | 剪枝 | 6 | 5 | 8 | 8 |
| 160 | 2604.16855 | When W4A4 Breaks Camouflaged Object Detection: Token-Group Dual-Constraint Activation Quantization | 量化 | 7 | 7 | 6 | 8 |
| 161 | 2604.16878 | OC-Distill: Ontology-aware Contrastive Learning with Cross-Modal Distillation for ICU Risk Prediction | 蒸馏 | 7 | 3 | 10 | 3 |
| 162 | 2604.16940 | D-QRELO: Training- and Data-Free Delta Compression for Large Language Models via Quantization and Residual Low-Rank Approximation | 量化、低秩 | 7 | 8 | 8 | 3 |
| 163 | 2604.17224 | LASER: Low-Rank Activation SVD for Efficient Recursion | 低秩 | 5 | 3 | 4 | 3 |
| 164 | 2604.17320 | Towards Joint Quantization and Token Pruning of Vision-Language Models | 量化、KV cache、剪枝 | 6 | 7 | 5 | 8 |
| 165 | 2604.17695 | MoE-nD: Per-Layer Mixture-of-Experts Routing for Multi-Axis KV Cache Compression | 量化、KV cache、低秩 | 7 | 5 | 7 | 5 |
| 166 | 2604.17753 | Evolutionary Negative Module Pruning for Better LoRA Merging | 剪枝、低秩 | 7 | 4 | 7 | 8 |
| 167 | 2604.17789 | DuQuant++: Fine-grained Rotation Enhances Microscaling FP4 Quantization | 量化 | 6 | 7 | 7 | 9 |
| 168 | 2604.17865 | Sharpening Lightweight Models for Generalized Polyp Segmentation: A Boundary Guided Distillation from Foundation Models | 蒸馏 | 6 | 3 | 8 | 8 |
| 169 | 2604.18117 | LoRaQ: Optimized Low Rank Approximation for 4-bit Quantization | 量化、混合精度 | 6 | 7 | 8 | 3 |
| 170 | 2604.18260 | Geometry-Guided 3D Visual Token Pruning for Video-Language Models | 剪枝 | 7 | 5 | 10 | 4 |
| 171 | 2604.18348 | AdaCluster: Adaptive Query-Key Clustering for Sparse Attention in Video Generation | 剪枝 | 6 | 5 | 6 | 4 |
| 172 | 2604.18476 | SemLT3D: Semantic-Guided Expert Distillation for Camera-only Long-Tailed 3D Object Detection | 蒸馏 | 5 | 3 | 5 | 3 |
| 173 | 2604.18831 | Feasibility of Indoor Frame-Wise Lidar Semantic Segmentation via Distillation from Visual Foundation Model | 蒸馏 | 7 | 4 | 4 | 4 |
| 174 | 2604.18963 | Distillation Traps and Guards: A Calibration Knob for LLM Distillability | 蒸馏 | 7 | 3 | 8 | 3 |
| 175 | 2604.19009 | Guiding Distribution Matching Distillation with Gradient-Based Reinforcement Learning | 蒸馏 | 6 | 3 | 8 | 3 |
| 176 | 2604.19145 | ST-Prune: Training-Free Spatio-Temporal Token Pruning for Vision-Language Models in Autonomous Driving | 剪枝 | 7 | 5 | 9 | 3 |
| 177 | 2604.19157 | SAW-INT4: System-Aware 4-Bit KV-Cache Quantization for Real-World LLM Serving | 量化、KV cache | 6 | 8 | 5 | 3 |
| 178 | 2604.19167 | LBLLM: Lightweight Binarization of Large Language Models via Three-Stage Distillation | 量化、蒸馏 | 8 | 8 | 7 | 3 |
| 179 | 2604.19398 | GRASPrune: Global Gating for Budgeted Structured Pruning of Large Language Models | KV cache、剪枝 | 6 | 5 | 5 | 5 |
| 180 | 2604.20079 | On the Quantization Robustness of Diffusion Language Models in Coding Benchmarks | 量化、混合精度 | 5 | 7 | 4 | 4 |
| 181 | 2604.20213 | Weighted Knowledge Distillation for Semi-Supervised Segmentation of Maxillary Sinus in Panoramic X-ray Images | 蒸馏 | 7 | 3 | 9 | 3 |
| 182 | 2604.20333 | Quantization robustness from dense representations of sparse functions in high-capacity kernel associative memory | 量化、剪枝 | 4 | 4 | 4 | 3 |
| 183 | 2604.20470 | DynamicRad: Content-Adaptive Sparse Attention for Long Video Diffusion | 剪枝 | 8 | 5 | 9 | 8 |
| 184 | 2604.20913 | FairyFuse: Multiplication-Free LLM Inference on CPUs via Fused Ternary Kernels | 量化 | 9 | 10 | 5 | 5 |
| 185 | 2604.20920 | Simplified Sparse Attention via Gist Tokens | KV cache、剪枝 | 8 | 8 | 9 | 9 |
| 186 | 2604.20937 | Sink-Token-Aware Pruning for Fine-Grained Video Understanding in Efficient Video LLMs | 剪枝 | 9 | 5 | 8 | 4 |
| 187 | 2604.21231 | SparKV: Overhead-Aware KV Cache Loading for Efficient On-Device LLM Inference | KV cache | 5 | 6 | 7 | 4 |
| 188 | 2604.21335 | Sub-Token Routing for KV Cache Compression | 量化、KV cache | 5 | 5 | 7 | 4 |
| 189 | 2604.21536 | Pre-trained LLMs Meet Sequential Recommenders: Efficient User-Centric Knowledge Distillation | 蒸馏 | 4 | 3 | 6 | 3 |
| 190 | 2604.21649 | GS-Quant: Granular Semantic and Generative Structural Quantization for Knowledge Graph Completion | 量化 | 6 | 4 | 8 | 8 |
| 191 | 2604.21743 | Bridging the Training-Deployment Gap: Gated Encoding and Multi-Scale Refinement for Efficient Quantization-Aware Image Enhancement | 量化 | 4 | 4 | 6 | 8 |
| 192 | 2604.22281 | DocPrune:Efficient Document Question Answering via Background, Question, and Comprehension-aware Token Pruning | 剪枝 | 6 | 6 | 7 | 4 |
| 193 | 2604.22379 | Efficient Diffusion Distillation via Embedding Loss | 蒸馏 | 9 | 4 | 8 | 5 |
| 194 | 2604.22529 | Distilling Vision Transformers for Distortion-Robust Representation Learning | 蒸馏 | 6 | 3 | 7 | 3 |
| 195 | 2604.22839 | From Skeletons to Pixels: Few-Shot Precise Event Spotting via Representation and Prediction Distillation | 蒸馏 | 7 | 3 | 5 | 3 |
| 196 | 2604.23106 | No Test Cases, No Problem: Distillation-Driven Code Generation for Scientific Workflows | 蒸馏 | 5 | 3 | 5 | 3 |
| 197 | 2604.23238 | Hiding in Plain Sight: Detectability-Aware Antidistillation of Reasoning Models | 蒸馏 | 4 | 3 | 5 | 3 |
| 198 | 2604.23314 | Learning from Noisy Prompts: Saliency-Guided Prompt Distillation for Robust Segmentation with SAM | 蒸馏 | 8 | 3 | 8 | 3 |
| 199 | 2604.23632 | Hallo-Live: Real-Time Streaming Joint Audio-Video Avatar Generation with Asynchronous Dual-Stream and Human-Centric Preference Distillation | 蒸馏 | 9 | 6 | 9 | 4 |
| 200 | 2604.23717 | HeadRouter: Dynamic Head-Weight Routing for Task-Adaptive Audio Token Pruning in Large Audio Language Models | 剪枝 | 7 | 5 | 8 | 5 |
| 201 | 2604.23950 | LearnPruner: Rethinking Attention-based Token Pruning in Vision Language Models | 剪枝 | 5 | 5 | 8 | 4 |
| 202 | 2604.25530 | The Surprising Effectiveness of Canonical Knowledge Distillation for Semantic Segmentation | 蒸馏 | 8 | 4 | 5 | 5 |
| 203 | 2604.25570 | Vision SmolMamba: Spike-Guided Token Pruning for Energy-Efficient Spiking State-Space Vision Models | 剪枝 | 6 | 7 | 9 | 5 |
| 204 | 2604.25688 | QB-LIF: Learnable-Scale Quantized Burst Neurons for Efficient SNNs | 量化 | 8 | 8 | 8 | 4 |
| 205 | 2604.26255 | GaitKD: A Universal Decoupled Distillation Framework for Efficient Gait Recognition | 蒸馏 | 5 | 3 | 7 | 8 |
| 206 | 2604.26340 | Adaptive and Fine-grained Module-wise Expert Pruning for Efficient LoRA-MoE Fine-Tuning | 剪枝 | 7 | 5 | 9 | 3 |
| 207 | 2604.26378 | CoQuant: Joint Weight-Activation Subspace Projection for Mixed-Precision LLMs | 量化、混合精度 | 7 | 4 | 10 | 9 |
| 208 | 2604.26573 | PAINT: Partial-Solution Adaptive Interpolated Training for Self-Distilled Reasoners | 蒸馏 | 6 | 3 | 6 | 4 |
| 209 | 2604.26587 | Sparse-on-Dense: Area and Energy-Efficient Computing of Sparse Neural Networks on Dense Matrix Multiplication Accelerators | 剪枝 | 5 | 4 | 4 | 3 |
| 210 | 2604.26837 | Unifying Sparse Attention with Hierarchical Memory for Scalable Long-Context LLM Serving | KV cache、剪枝 | 6 | 7 | 5 | 4 |
| 211 | 2604.26934 | World2VLM: Distilling World Model Imagination into VLMs for Dynamic Spatial Reasoning | 蒸馏 | 8 | 3 | 8 | 3 |
| 212 | 2604.27083 | Co-Evolving Policy Distillation | 蒸馏 | 6 | 3 | 8 | 3 |
| 213 | 2604.27128 | Lightweight Distillation of SAM 3 and DINOv3 for Edge-Deployable Individual-Level Livestock Monitoring and Longitudinal Visual Analytics | 剪枝、蒸馏 | 8 | 5 | 5 | 4 |
| 214 | 2604.27178 | Energy-Efficient Plant Monitoring via Knowledge Distillation | 蒸馏 | 8 | 3 | 5 | 3 |
| 215 | 2604.27396 | VitaLLM: A Versatile, Ultra-Compact Ternary LLM Accelerator with Dependency-Aware Scheduling | 量化、剪枝、混合精度 | 6 | 9 | 8 | 3 |
| 216 | 2604.28123 | Beyond SFT-to-RL: Pre-alignment via Black-Box On-Policy Distillation for Multimodal RL | 蒸馏 | 6 | 3 | 4 | 9 |

---

## 二、按技术方向分类统计

| 技术方向 | 论文数 | 平均精度效果 | 平均压缩倍率 | 平均创新性 | 平均可复现性 |
|---------|:-----:|:-----:|:-----:|:-----:|:-----:|
| 量化 | 60 | 5.9 | 6.0 | 6.5 | 5.2 |
| 剪枝 | 62 | 6.2 | 5.0 | 7.1 | 4.6 |
| 蒸馏 | 101 | 6.5 | 3.5 | 6.6 | 4.8 |
| KV cache | 23 | 6.3 | 5.9 | 6.3 | 5.3 |
| 低秩 | 16 | 6.2 | 4.5 | 7.1 | 4.9 |
| 混合精度 | 8 | 5.8 | 5.8 | 6.8 | 5.8 |

---

## 三、量化方向重点分析（60 篇）

### 3.1 KV cache 量化（9 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.11501 | Quantization Dominates Rank Reduction for KV-Cache Compression | 9 | 9 | 6 | 5 | 5 个模型（124M–14B，MHA/GQA）等存储预算下量化一致优于降秩 4–364 PPL；LAMBADA 上 INT4 匹配 FP16（Mistral 7 |
| 2604.04722 | Don't Waste Bits! Adaptive KV-Cache Quantization for Lightweight On-Device LLMs | 7 | 9 | 6 | 4 | 用 token 频率、质量分数、注意力方差、熵不确定性等轻量特征训练紧凑控制器，在解码时从 {2/4/8-bit, FP16} 中按 token 重要性动态选择 |
| 2604.17320 | Towards Joint Quantization and Token Pruning of Vision-Language Models | 6 | 7 | 5 | 8 | QUOTA（量化统一离线 token 分配器）把低比特校准信号转化为逐层 token 分配方案并物化为剪枝配方，token 重要性在部署态 W4A4 算子与量化 |
| 2604.02638 | AXELRAM: Quantize Once, Never Dequantize | 5 | 5 | 6 | 9 | AXELRAM 利用设计时固定码本（正交变换使坐标分布集中到 N(0,1/d)，最优量化器只依赖维度 d 与位宽 b）与“写入变换、读时查表”的非对称路径，使每 |
| 2604.05366 | 3DTurboQuant: Training-Free Near-Optimal Quantization for 3D Reconstruction Models | 5 | 7 | 5 | 8 | 作者发现 3DGS 的 45 维球谐与 DUSt3R 的 1024 维 KV 向量所在维度范围内单次随机旋转即可把任意输入变为已知 Beta 分布坐标，使预计算 |
| 2604.15356 | Sequential KV Cache Compression via Probabilistic Language Tries: Beyond the Per-Vector Shannon Limit | 5 | 8 | 8 | 4 | 指出 KV cache 中的 token 不是任意浮点数据而是模型所学语言的样本，提出两层序列压缩架构——概率前缀去重（基于概率语言 trie 的距离度量 d_ |
| 2604.17695 | MoE-nD: Per-Layer Mixture-of-Experts Routing for Multi-Axis KV Cache Compression | 7 | 5 | 7 | 5 | 指出现有方法对所有层套用同一压缩配方的同质性浪费了精度——不同层对各压缩操作的敏感度差异巨大；MoE-nD 用混合专家框架在全局显存预算下为每层路由专属（驱逐率 |
| 2604.19157 | SAW-INT4: System-Aware 4-Bit KV-Cache Quantization for Real-World LLM Serving | 6 | 8 | 5 | 3 | 在分页显存布局、规则访存、融合注意力执行三大真实服务约束下甄别可行的 4 比特 KV 量化方案，核心发现：简单的"token 级 INT4 + 块对角 Hada |
| 2604.21335 | Sub-Token Routing for KV Cache Compression | 5 | 5 | 7 | 4 | 在 token 级削减之后，把每个保留 token 的 value 向量分组、只保留选定组（query/key 不动），为 KV 压缩增加 token 内部的细 |

### 3.2 极端低比特（≤2bit / 三值 / FP4）（11 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.06798 | MoBiE: Efficient Inference of Mixture of Binary Experts under Post-Training Quantization | 7 | 8 | 9 | 9 | MoBiE 以联合 SVD 分解消除跨专家冗余、将全局损失梯度融入局部 Hessian 权重重要性估计、用输入零空间引导的误差约束缓解路由失真，且不引入额外存储 |
| 2604.17789 | DuQuant++: Fine-grained Rotation Enhances Microscaling FP4 Quantization | 6 | 7 | 7 | 9 | MXFP4 格式（32 元素共享 E8M0 尺度）下单个激活离群值会撑大整块共享尺度、压缩其余元素动态范围；DuQuant++ 将 DuQuant 的离群值感知 |
| 2604.20913 | FairyFuse: Multiplication-Free LLM Inference on CPUs via Fused Ternary Kernels | 9 | 10 | 5 | 5 | FairyFuse 把每个 widely-linear 层的 8 个实值子 GEMV 融合为单条 AVX-512 循环，用掩码加减替代全部浮点乘法；roofli |
| 2604.03957 | BWTA: Accurate and Efficient Binarized Transformer by Algorithm-Hardware Co-design | 6 | 10 | 8 | 4 | 分析二值化零点失真并提出“微小值投影到零”的 BWTA 方案，配合平滑多阶段量化训练（层级退化策略 + 幅度对齐投影因子）与指令级并行位打包 CUDA kern |
| 2604.25688 | QB-LIF: Learnable-Scale Quantized Burst Neurons for Efficient SNNs | 8 | 8 | 8 | 4 | QB-LIF 把 burst 发放重构为膜电位的饱和均匀量化且尺度可学习——每层自适应调整发放分辨率；可吸收尺度策略推理时把学到的尺度折叠进突触权重、保持纯累加 |
| 2604.12782 | OSC: Hardware Efficient W4A4 Quantization via Outlier Separation in Channel Dimension | 5 | 10 | 7 | 5 | 发现激活离群在固定通道跨 token 持续聚集（token-persistent 结构聚类），OSC 离线组级识别离群通道、在线结构化子张量抽取将其聚合为紧凑稠 |
| 2604.19167 | LBLLM: Lightweight Binarization of Large Language Models via Three-Stage Distillation | 8 | 8 | 7 | 3 | LBLLM 三阶段推进——PTQ 初始化高质量量化模型；逐层蒸馏中同时量化二值权重、组级位图与量化参数（激活保持全精度）；最后训练可学习激活量化因子动态压至 4 |
| 2604.27396 | VitaLLM: A Versatile, Ultra-Compact Ternary LLM Accelerator with Dependency-Aware Scheduling | 6 | 9 | 8 | 3 | 异构双核计算策略（TINT-Cores 处理大规模三值投影 + BoothFlex-Core 统一混合精度注意力），Leading One Prediction |
| 2604.03336 | NativeTernary: A Self-Delimiting Binary Encoding with Unary Run-Length Hierarchy Markers for Ternary Neural Network Weights, Structured Data, and General Computing Infrastructure | 6 | 10 | 4 | 4 | 针对 BitNet b1.58 类 {-1,0,+1} 三值 LLM 缺乏原生二进制 wire format 的问题，NativeTernary 以自分隔编码  |
| 2604.06916 | FP4 Explore, BF16 Train: Diffusion Reinforcement Learning via Efficient Rollout Scaling | 5 | 7 | 8 | 3 | 第一阶段用高吞吐 NVFP4 rollout 生成海量候选池并提取高对比度子集，第二阶段以 BF16 重新生成选中样本并仅在其上优化策略；在 SANA、FLUX |
| 2604.03950 | Diagonal-Tiled Mixed-Precision Attention for Efficient Low-Bit MXFP Inference | 4 | 4 | 4 | 8 | DMA 在 tiling 级别组合两种低比特计算，用 Triton 实现精细融合 kernel，利用下一代 GPU（B200）的硬件并行与显存效率，在生成质量几 |

### 3.3 旋转/变换类方法（3 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.04013 | RUQuant: Towards Refining Uniform Quantization for Large Language Models | 6 | 8 | 8 | 4 | 作者指出激活在量化区间内非均匀分布使 Lloyd-Max 最优量化点偏离区间中点，提出 RUQuant：先用 Householder 反射与 Givens 旋转 |
| 2604.10496 | CodeQuant: Unified Clustering and Quantization for Enhanced Outlier Smoothing in Low-Precision Mixture-of-Experts | 7 | 4 | 6 | 8 | CodeQuant 用可学习旋转平滑激活离群、将权重离群吸收进微调聚类质心（极值拟合进质心降低量化误差且保持表达能力），配 GPU/CPU 专用 kernel  |
| 2604.11080 | ReSpinQuant: Efficient Layer-Wise LLM Quantization via Subspace Residual Rotation Approximation | 6 | 7 | 8 | 3 | 全局旋转可融合进权重但表达力受限（所有层共享一个旋转矩阵），逐层变换精度高但无法融合需在线计算；ReSpinQuant 以高效残差子空间旋转近似实现离线激活旋转 |

### 3.4 混合精度与子空间（6 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.26378 | CoQuant: Joint Weight-Activation Subspace Projection for Mixed-Precision LLMs | 7 | 4 | 10 | 9 | 现有混合精度方法仅靠激活统计选择高精度保留的子空间，忽视输出扰动由激活与权重量化噪声联合驱动的本质；CoQuant 理论建模期望输出误差，导出闭式加权 PCA  |
| 2604.13440 | A KL Lens on Quantization: Fast, Forward-Only Sensitivity for Mixed-Precision SSM-Transformer Models | 7 | 7 | 7 | 8 | 面向 SSM-Transformer 混合架构，用仅前向代理指标识别量化敏感组件；形式分析表明 KL 散度比 MSE/SQNR 更好刻画语言模型量化敏感度；In |
| 2604.01167 | AdaLoRA-QAT: Adaptive Low-Rank and Quantization-Aware Segmentation | 6 | 4 | 6 | 8 | AdaLoRA-QAT 将自适应秩分配的 LoRA 编码器适配与选择性混合精度 INT8 QAT 结合，在大规模 CXR 数据集上达到 95.6% Dice（持 |
| 2604.18117 | LoRaQ: Optimized Low Rank Approximation for 4-bit Quantization | 6 | 7 | 8 | 3 | LoRaQ 挑战现有低秩补偿方法"分支必须保持 W16A16 高精度"与"依赖重校准数据"两条假设，提出简单免数据的量化误差补偿优化，使低秩分支本身也可量化，实 |
| 2604.20079 | On the Quantization Robustness of Diffusion Language Models in Coding Benchmarks | 5 | 7 | 4 | 4 | 在扩散式代码 LLM（CoDA）上应用 GPTQ 与改进的 Hessian 感知量化（HAWQ），标准化评测下 CoDA 在 2–4 比特低比特档的量化鲁棒性显 |
| 2604.06515 | Efficient Quantization of Mixture-of-Experts with Theoretical Generalization Guarantees | 5 | 4 | 7 | 3 | 以训练中路由器 l2 范数变化量为主信号分配专家位宽——变化小的专家捕捉低频但关键特征、其量化对性能更敏感需高精度；同时对神经元内方差大的专家也分配高精度避免注 |

### 3.5 量化机理与评估（7 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.15167 | When Flat Minima Fail: Characterizing INT4 Quantization Collapse After FP32 Convergence | 6 | 7 | 4 | 9 | 对全部 154 个公开 Pythia-160m 训练检查点做免校准分组 INT4 探测，发现量化鲁棒性呈三相结构：共同改进期→约 7 万步亚稳平台期→爆炸性发散 |
| 2604.04988 | Prune-Quantize-Distill: An Ordered Pipeline for Efficient Neural Network Compression | 6 | 5 | 5 | 4 | 在 CIFAR-10/100 + ResNet-18/WRN-28-10/VGG-16-BN 上系统比较发现：INT8 QAT 贡献主要运行时收益，剪枝主要作为 |
| 2604.09220 | TinyNeRV: Compact Neural Video Representations via Capacity Scaling, Distillation, and Low-Precision Inference | 4 | 4 | 4 | 8 | 提出 NeRV-T/NeRV-T+ 两种轻量配置，系统分析激进容量削减对重建质量、计算复杂度与解码吞吐的影响；以频率感知焦点监督的蒸馏提升低保真网络，并考察 P |
| 2604.14487 | Quantization of Spiking Neural Networks Beyond Accuracy | 4 | 5 | 7 | 4 | 作者证明在同等准确率下，不同量化方法、裁剪范围与位宽会产生迥异的发放分布（影响实际稀疏度、状态存储与事件处理负载），并提出用 Earth Mover's Dis |
| 2604.15780 | Pruning Unsafe Tickets: A Resource-Efficient Framework for Safer and More Robust LLMs | 5 | 4 | 4 | 4 | 提出免梯度归因的剪枝框架，直接识别并移除与不安全行为关联的参数，同时保持模型效用；在 Mistral、LLaVA 等模型上大幅降低不安全生成并增强抗越狱鲁棒性， |
| 2604.03420 | Zero-Shot Quantization via Weight-Space Arithmetic | 5 | 4 | 4 | 3 | PTQ 鲁棒性可用“量化向量”刻画——从供体任务经简单权重空间算术提取后修补受体模型，3-bit 设置下无受体侧 QAT 即提升 post-PTQ Top-1  |
| 2604.20333 | Quantization robustness from dense representations of sparse functions in high-capacity kernel associative memory | 4 | 4 | 4 | 3 | 通过量化与剪枝压缩实验发现明显不对称性——KLR Hopfield 网络对低精度量化鲁棒、对剪枝高度敏感；用"稀疏函数、稠密表示"原理解释：稀疏输入映射通过稠密 |

### 3.6 特定模态/任务量化（11 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.10103 | Long-Horizon Streaming Video Generation via Hybrid Attention with Decoupled Distillation | 7 | 5 | 10 | 8 | 轻量线性时间注意力以紧凑 KV 状态增量吸收滑窗驱逐的 token 保持长程依赖，块稀疏注意力削减局部冗余计算，配合“先稠密注意力少步蒸馏、再激活混合注意力蒸馏 |
| 2604.16855 | When W4A4 Breaks Camouflaged Object Detection: Token-Group Dual-Constraint Activation Quantization | 7 | 7 | 6 | 8 | 发现 COD 的任务特异性量化悬崖：重尾背景 token 主导共享激活范围、撑大量化步长，把微弱但有结构的边界线索压进零仓；COD-TDQ 用直接求和 toke |
| 2604.21649 | GS-Quant: Granular Semantic and Generative Structural Quantization for Knowledge Graph Completion | 6 | 4 | 8 | 8 | GS-Quant 为 KG 实体生成语义连贯、结构分层的离散码：粒度语义增强模块向码本注入层级知识使靠前的码捕获全局语义类别、靠后的码精修具体属性；生成式结构重 |
| 2604.02570 | WSVD: Weighted Low-Rank Approximation for Fast and Efficient Execution of Low-Precision Vision-Language Models | 7 | 4 | 5 | 8 | WSVD 引入更细粒度的 SVD 计算模式以真正实现延迟下降，并在分解过程中按权重元素相对重要性自适应加权，再结合权重与激活量化，在 VLM 上取得超过 1.8 |
| 2604.15196 | Unsupervised Skeleton-Based Action Segmentation via Hierarchical Spatiotemporal Vector Quantization | 8 | 4 | 9 | 3 | 提出两级向量量化框架——底层将骨架帧关联到细粒度子动作、高层聚合子动作为动作级表征，并扩展为同时重建骨架与时间戳的时空方案，在 HuGaDB、LARa、BABE |
| 2604.04356 | REAM: Merging Improves Pruning of Experts in LLMs | 8 | 5 | 7 | 3 | REAM 按路由器权重与激活对专家分组并合并权重（而非 REAP 式直接删除），在多个 MoE LLM 的选择题与生成基准上常优于基线、多数情况下与原模型相当， |
| 2604.07853 | QaRL: Rollout-Aligned Quantization-Aware RL for Fast and Stable Training under Training--Inference Mismatch | 7 | 4 | 8 | 4 | QaRL 让训练侧前向与量化 rollout 对齐以消除失配；并发现量化 rollout 在长回复中产生重复乱码 error token 的失效模式，提出 TB |
| 2604.21743 | Bridging the Training-Deployment Gap: Gated Encoding and Multi-Scale Refinement for Efficient Quantization-Aware Image Enhancement | 4 | 4 | 6 | 8 | 层级架构（门控编码块 + 多尺度精修）保持细粒度视觉特征，训练中用 QAT 模拟低精度表示，使网络提前适应量化、避免标准 PTQ 的质量骤降，在标准移动设备上兼 |
| 2604.07955 | Rethinking Residual Errors in Compensation-based LLM Quantization | 4 | 4 | 4 | 8 | 指出现有方法层内校准时对齐的是“补偿权重输出”而非“原始全精度输出”这一次优目标，并揭示残差误差除来自前层输出差异外还来自本层补偿权重与原始权重之差（compe |
| 2604.05171 | Modality-Aware and Anatomical Vector-Quantized Autoencoding for Multimodal Brain MRI | 4 | 4 | 7 | 3 | NeuroQuant 用分解式多轴注意力学习跨模态共享潜在表示，双流 3D 编码器显式分离模态不变解剖结构与模态依赖外观，解剖编码经共享码本离散化并以 FiLM |
| 2604.01042 | Integer-State Dynamics of Quantized Spiking Neural Networks for Efficient Hardware Acceleration | 5 | 4 | 5 | 3 | 将硬件导向 SNN 建模为有界整数格点上的确定性映射，提出整数值状态 + 移位泄漏的轻量更新规则，通过 N=30–130、连接密度 0.1–0.9、位宽 4/8 |

### 3.7 其他量化工作（13 篇）

| arXiv ID | 标题 | 精 | 压 | 新 | 复 | 一句话结论 |
|---------|-----|:-:|:-:|:-:|:-:|---------|
| 2604.00586 | More Human, More Efficient: Aligning Annotations with Quantized SLMs | 7 | 7 | 5 | 8 | 在有限人工标注数据上微调 4-bit 量化的 1.7B SLM，配合多维评分 rubric 与简单正则化，标注一致性（Krippendorff α）比最强专有  |
| 2604.02816 | QAPruner: Quantization-Aware Vision Token Pruning for Multimodal Large Language Models | 7 | 8 | 8 | 4 | 作者发现语义驱动的 token 剪枝会丢弃对量化数值稳定性至关重要的激活离群 token、在 W4A4 等低比特下加剧量化误差，提出结合组级量化模拟误差与离群强 |
| 2604.16940 | D-QRELO: Training- and Data-Free Delta Compression for Large Language Models via Quantization and Residual Low-Rank Approximation | 7 | 8 | 8 | 3 | 发现大规模 SFT 数据会放大 delta 参数的幅值、奇异值与熵，加剧压缩误差；D-QRELO 先用粗粒度一比特量化捕获 delta 主导结构，再用补偿性残差 |
| 2604.02556 | Fast NF4 Dequantization Kernels for Large Language Model Inference | 5 | 7 | 4 | 9 | 通过仅 64 字节/线程块的共享内存优化与简化索引逻辑，利用共享内存相对全局内存 12–15 倍的延迟优势，NF4 反量化 kernel 在 Gemma 27B |
| 2604.08847 | DeFakeQ: Enabling Real-Time Deepfake Detection on Edge Devices via Adaptive Bidirectional Quantization | 7 | 4 | 9 | 3 | 针对深伪检测依赖极易被量化破坏的细粒度伪造痕迹这一特性，DeFakeQ 提出自适应双向压缩策略同时利用特征相关性并消除冗余，在 5 个基准数据集、11 个 SO |
| 2604.10091 | SEPTQ: A Simple and Effective Post-Training Quantization Paradigm for Large Language Models | 7 | 4 | 8 | 3 | SEPTQ 先全局静态计算权重元素重要性分数并确定量化位置，再依据重要位置掩码逐列量化并更新关联权重，将 PTQ 流程简化为两步；从百万到十亿参数模型、多位宽设 |
| 2604.13806 | Robust Ultra Low-Bit Post-Training Quantization via Stable Diagonal Curvature Estimate | 7 | 4 | 7 | 4 | Hessian 类 PTQ 在低比特下因小校准集曲率估计噪声而退化；DASH-Q 丢弃噪声敏感的跨通道依赖，仅保留对角曲率并迭代加权最小二乘，过滤采样噪声同时优 |
| 2604.06836 | STQuant: Spatio-Temporal Adaptive Framework for Optimizer Quantization in Large Multimodal Model Training | 5 | 4 | 8 | 4 | STQuant 跨层、跨状态变量、跨训练步动态分配优化器状态精度，以可证近最优因子选择策略定位最有影响的精度适配因子，动态转移决策算法把搜索从指数降到线性；GP |
| 2604.07674 | Weight Group-wise Post-Training Quantization for Medical Foundation Model | 4 | 8 | 6 | 3 | Permutation-COMQ 仅用点积与舍入操作（无反向传播、无超参调优）完成 PTQ，并以权重感知重排在层内重组织权重以缓解通道级缩放引起的精度退化，在  |
| 2604.12145 | Why Your Tokenizer Fails in Information Fusion: A Timing-Aware Pre-Quantization Fusion for Video-Enhanced Audio Tokenization | 5 | 4 | 8 | 3 | 系统研究发现：融合位置对重建质量至关重要；对比学习不适合离散分词器；沿时间轴（以区别性特征概念引导）融合显著优于特征维融合；据此提出首个将视觉信息融入音频分词器 |
| 2604.04701 | MUXQ: Mixed-to-Uniform Precision MatriX Quantization via Low-Rank Outlier Decomposition | 4 | 4 | 7 | 4 | MUXQ 检测输入激活离群通道并引入小型辅助矩阵将离群幅度跨通道重分配，使激活离群也能以低精度 INT 量化且保持硬件友好计算结构；GPT-2 0.1B/0.3 |
| 2604.00529 | MF-QAT: Multi-Format Quantization-Aware Training for Elastic Inference | 5 | 4 | 6 | 3 | MF-QAT 让一个模型在多格式 QAT 下对每个目标精度都达到单格式 QAT 的水平，配合 Slice-and-Scale 转换程序，只需保存一份 MXINT |
| 2604.15794 | Self-Distillation as a Performance Recovery Mechanism for LLMs: Counteracting Compression and Catastrophic Forgetting | 5 | 4 | 5 | 3 | 提出以自蒸馏微调恢复受损模型能力的框架，并用 Centered Kernel Alignment（CKA）量化师生激活轨迹的对齐度，实验证明性能恢复与高维流形对 |

---

## 四、亮点论文 TOP 10（按四项总分排序）

| 排名 | arXiv ID | 标题 | 总分 | 亮点 |
|:---:|---------|-----|:---:|-----|
| 1 | 2604.20920 | Simplified Sparse Attention via Gist Tokens | 34 | 持续预训练时在序列中插入 gist token 并用注意力掩码限制其可见上下文，教模型把每块重要信息压进 gist token；推理时只对 gist token 打分选 top-k 块"展开"回原始  |
| 2 | 2604.06798 | MoBiE: Efficient Inference of Mixture of Binary Experts under Post-Training Quantization | 33 | MoBiE 以联合 SVD 分解消除跨专家冗余、将全局损失梯度融入局部 Hessian 权重重要性估计、用输入零空间引导的误差约束缓解路由失真，且不引入额外存储；Qwen3-30B-A3B 上困惑度降 |
| 3 | 2604.07716 | Breaking the KV Cache Bottleneck: Fan Duality Model Achieves O(1) Decode Memory with Superior Associative Recall | 32 | FDM 将序列处理分为波组件（保相 Givens 旋转递归扫描，把长程模式压缩进定长复隐状态）与粒子组件（W+K=272 槽联想寻址缓存），实现严格 O(1) 解码显存（128–8192 提示长均 8 |
| 4 | 2604.01609 | Swift-SVD: Theoretical Optimality Meets Practical Efficiency in Low-Rank LLM Compression | 31 | Swift-SVD 对一批输入增量聚合输出激活协方差并只做一次特征分解，得到免训练、闭式、数值稳定的逐层最优低秩近似；配合基于有效秩与端到端层重要性的动态秩分配，在 6 个 LLM、8 个数据集上精度 |
| 5 | 2604.10103 | Long-Horizon Streaming Video Generation via Hybrid Attention with Decoupled Distillation | 30 | 轻量线性时间注意力以紧凑 KV 状态增量吸收滑窗驱逐的 token 保持长程依赖，块稀疏注意力削减局部冗余计算，配合“先稠密注意力少步蒸馏、再激活混合注意力蒸馏”的解耦策略；单张 H100 上实时无界 |
| 6 | 2604.20470 | DynamicRad: Content-Adaptive Sparse Attention for Long Video Diffusion | 30 | DynamicRad 在径向局部性先验内做自适应选择，双模式（静态比率求速度 / 动态阈值求质量），并用离线贝叶斯优化在物理代理任务上优化注意力重建误差、配合轻量语义运动路由器把 prompt 嵌入映 |
| 7 | 2604.26378 | CoQuant: Joint Weight-Activation Subspace Projection for Mixed-Precision LLMs | 30 | 现有混合精度方法仅靠激活统计选择高精度保留的子空间，忽视输出扰动由激活与权重量化噪声联合驱动的本质；CoQuant 理论建模期望输出误差，导出闭式加权 PCA 解平衡激活与权重协方差以选最优高精度子空 |
| 8 | 2604.11501 | Quantization Dominates Rank Reduction for KV-Cache Compression | 29 | 5 个模型（124M–14B，MHA/GQA）等存储预算下量化一致优于降秩 4–364 PPL；LAMBADA 上 INT4 匹配 FP16（Mistral 7B +0.23 PPL）而同存储 ran |
| 9 | 2604.13440 | A KL Lens on Quantization: Fast, Forward-Only Sensitivity for Mixed-Precision SSM-Transformer Models | 29 | 面向 SSM-Transformer 混合架构，用仅前向代理指标识别量化敏感组件；形式分析表明 KL 散度比 MSE/SQNR 更好刻画语言模型量化敏感度；Intel Lunar Lake 真机验证  |
| 10 | 2604.17789 | DuQuant++: Fine-grained Rotation Enhances Microscaling FP4 Quantization | 29 | MXFP4 格式（32 元素共享 E8M0 尺度）下单个激活离群值会撑大整块共享尺度、压缩其余元素动态范围；DuQuant++ 将 DuQuant 的离群值感知细粒度旋转与微缩放组大小（B=32）对齐 |

---

## 五、量化代码复现清单

本月为 **12** 篇核心量化论文完成代码复现（`scripts/quantization/<arxiv_id>/`，含 README.md 与 demo.py）。统一验证方式：加载真实 Qwen/Qwen3-0.6B 架构配置（hidden=1024、16 Q 头、8 KV 头、head_dim=128；因网络受限未下载 1.4GB 权重，采用同架构随机权重模型，已在各 README 如实注明），在 CPU 上真实运行 `python3 demo.py` 验证全部代码路径，12/12 通过。

| arXiv ID | 论文 | 复现核心算法 | 验证结果 |
|---------|-----|------------|---------|
| 2604.14487 | SNN EMD 评估 | LIF 脉冲层 + EMD 发放分布偏移指标 | EMD 区分均匀/学习型量化的行为漂移，PASS |
| 2604.15167 | INT4 Collapse Probe | 免校准 per-group INT4/INT8 探针 + 三相结构 toy 复现 | 收敛后 INT4 gap 98.9%→182.7% 而 FP32 近平，INT8 免疫，PASS |
| 2604.16855 | COD-TDQ | DSTG token 组尺度 + DCRP 双约束范围投影 | 边界 token 零仓率 100%→修复，重建 MSE 降至 1.4e-4，PASS |
| 2604.17695 | MoE-nD | 逐层（驱逐率,K-bits,V-bits）敏感度画像 + 贪心预算路由 | 同预算预测损失 920.6 < 均匀配方 941.9，PASS |
| 2604.17789 | DuQuant++ | MXFP4 微缩放 + 离群值感知块对齐单旋转 | 层输出 MSE 降 3.71×，PASS |
| 2604.18117 | LoRaQ | 免数据低秩补偿 + 分支自身 W8A8 量化 | W4+分支误差 < 纯 W4，全 sub-16bit 管线成立，PASS |
| 2604.19157 | SAW-INT4 | token 级 INT4 + 块对角 Hadamard 旋转 KV 量化 | 注意力 logits 相对误差 0.168→0.084，PASS |
| 2604.19167 | LBLLM | W(1+1)A4 三阶段解耦蒸馏（PTQ→权重蒸馏→激活尺度） | 训练收敛、误差递减，PASS |
| 2604.20913 | FairyFuse | 三值无乘法 GEMV（掩码加减）+ roofline 估算 | 与浮点三值仿真最大差 6.7e-6，PASS |
| 2604.21335 | Sub-Token Routing | token 削减后 value 组级路由（紧预算档） | 10% 预算误差 0.962→0.847，PASS |
| 2604.25688 | QB-LIF | 可学习尺度 burst 量化神经元 + ReLSG-ET 替代梯度 + 尺度吸收 | 同步数下精度 0.979→0.998，折叠误差 1.2e-7，PASS |
| 2604.26378 | CoQuant | 权重-激活联合加权 PCA 子空间混合精度 | MSE 0.0163 < 激活单边 0.0201 < 全 INT4 0.0229，PASS |

---

## 六、整体趋势分析

1. **系统共设计成主战场**：SAW-INT4（服务约束筛选量化方法）、SPIN（稀疏注意力+层级存储统一框架）、FairyFuse（无乘法 kernel）、Dispatch-Aware Ragged Attention（分发开销修复）共同表明——离线精度与部署收益之间的鸿沟必须靠算法-系统协同弥合，"简单方法+系统优化"反复战胜复杂方法。
2. **压缩的"元问题"独立成方向**：MoE-nD（逐层 KV 压缩路由）、QUOTA（量化-剪枝统一分配）、VisPCO（Pareto 配置搜索）、DynamicRad（离线 BO+在线路由）把"在哪压、压多少"从人工调参变成可学习的调度器问题。
3. **蒸馏精细化**：在策略蒸馏（OPD）生态快速成熟——TIP（token 重要性双轴）、CaOPD（校准失配）、PAINT（特权信息量控制）、CoPD（协同进化），token 级稀疏监督（<20% token 训全量效果）成为降本共识；特权蒸馏攻防一体（可蒸馏性旋钮、反蒸馏投毒）连接模型 IP 保护。
4. **极端低比特走向硬件现实**：三值/二值（FairyFuse CPU 29.6×、VitaLLM ASIC 0.223mm²、LBLLM 免旋转 W(1+1)A4）与 MXFP4 格式（DuQuant++、LoRaQ）沿 Blackwell 等硬件格式对齐，"补偿分支也必须可量化"成为新约束。
5. **评估方法论觉醒**：多篇论文专攻"看不见的失效"——FP16 KV cache 非等价性（100% token 分歧）、SNN 量化 EMD 行为漂移、INT4 训练后崩塌三相结构、sink token 致细粒度崩溃、分割蒸馏的墙钟公平比较；压缩研究正从"刷精度"转向"部署感知评估"。
6. **剪枝反超基线现象频发**：ST-Prune、HeadRouter、DocPrune 等报告剪枝后部分指标反超全模型（降噪效应），"稀疏化即正则化"值得统一理论研究。
7. **应用侧扩散**：医疗（息肉/上颌窦/SAM 提示蒸馏）、农业（牲畜监测、植物识别）、自动驾驶（ST-Prune、SemLT3D）、推荐系统、科学计算——蒸馏成为领域落地的标准搬运工，系统级压缩报告（装进 Jetson 的具体余量）是应用论文范本。

---

## 附录：评分规则

四项评分均为 1–10 分，由摘要以透明规则提取（代码开源情况、是否声明 SOTA/超越基线、量化位宽、加速/压缩数字、基准数量、理论贡献、新颖性声明等信号加权），不引用摘要之外的信息。评分用于横向筛选，精确数字请以原文为准。每篇论文的详细依据见 `papers/2026-04/<arxiv_id>/tech_analysis.md`。
