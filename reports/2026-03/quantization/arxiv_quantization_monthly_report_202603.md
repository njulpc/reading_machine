# ArXiv 量化与模型压缩领域论文月报（2026 年 3 月）

**收集日期范围**: 2026-03-01 ~ 2026-03-31（按 submittedDate）  
**检索关键词**: quantization / pruning / distillation（三组 OR 主查）+ 标题关键词分段补查召回（ti: quant / prune / distill / compress / KV cache）  
**数据来源**: arXiv.org API  
**检索漏斗**: 原始命中 **983** 篇 → 强关键词过滤候选 **362** 篇 → 深度技术分析 **101** 篇（周分段标题补查 592 条核对，确认清单无大遗漏）  
**深度分析**: 每篇含六段结构（核心速览/背景动机/方法创新/实验结果/局限展望/学术启发），见 `papers/2026-03/<arxiv_id>/tech_analysis.md`  
**代码复现**: 8 个量化方向 demo，见 `scripts/quantization/<arxiv_id>/`（第 7 节）

---

## 一、检索方法与边界

### 1.1 检索漏斗

| 阶段 | 数量 | 说明 |
|------|:----:|------|
| 原始命中 | 983 | quantization / pruning / distillation 三组 OR × 目标分类 × submittedDate:[20260301 TO 20260331] |
| 强关键词候选 | 362 | 标题/摘要强关键词过滤（量化、剪枝、蒸馏、压缩、KV cache 等） |
| 深度分析 | 101 | 编辑筛选：压缩核心相关、方法或实证贡献明确 |
| 召回核对 | 592 | 按周分段 × 标题关键词补查，确认无大遗漏 |

### 1.2 排除标准（边界类论文不纳入深度分析）

- **纯投机解码**（speculative decoding，无压缩组件）
- **纯稀疏注意力**（注意力模式稀疏化，非模型压缩）
- **纯 PEFT/LoRA**（参数高效微调本身，无量化/剪枝/蒸馏耦合）
- **统计稀疏**（数据集/特征稀疏现象描述，非压缩方法）
- **数据/编解码压缩**（图像、视频、比特流编解码）
- **数据集级蒸馏**（dataset distillation，非模型权重蒸馏）

---

## 二、论文总览表（101 篇）

| 序号 | arXiv ID | 论文标题 | 提交日期 | 技术分类 | 核心关键词 |
|:---:|----------|---------|:-------:|---------|-----------|
| 1 | 2603.01236 | AgilePruner: An Empirical Study of Attention and Diversity for Adaptive Visual Token Pruning in Large Vision-Language Models | 03-01 | Token 剪枝（多模态/视频） | pruning、token pruning、LLM、VLM/MLLM |
| 2 | 2603.01376 | 3BASiL: An Algorithmic Framework for Sparse plus Low-Rank Compression of LLMs | 03-02 | 剪枝与稀疏 | sparsity、LLM |
| 3 | 2603.01399 | Quasar: Quantized Self-Speculative Acceleration for Rapid Inference via Memory-Efficient Verification | 03-02 | 通用量化（权重/激活/训练） | quantization、low-bit、pruning、LLM |
| 4 | 2603.01426 | Understanding the Physics of Key-Value Cache Compression for LLMs through Attention Dynamics | 03-02 | KV Cache 压缩（非量化） | KV cache、long-context、sparsity、reasoning |
| 5 | 2603.01599 | Boosting Entropy with Bell Box Quantization | 03-02 | 通用量化（权重/激活/训练） | quantization、QAT、low-bit、rotation/Hadamard |
| 6 | 2603.01776 | FreeAct: Freeing Activations for LLM Quantization | 03-02 | 通用量化（权重/激活/训练） | quantization、KV cache、LLM、VLM/MLLM |
| 7 | 2603.01875 | KDFlow: A User-Friendly and Efficient Knowledge Distillation Framework for Large Language Models | 03-02 | 知识蒸馏 | distillation、LLM |
| 8 | 2603.02170 | SageBwd: A Trainable Low-bit Attention | 03-02 | 通用量化（权重/激活/训练） | quantization、low-bit |
| 9 | 2603.02731 | Practical FP4 Training for Large-Scale MoE Models on Hopper GPUs | 03-03 | 通用量化（权重/激活/训练） | quantization、low-bit、LLM、MoE |
| 10 | 2603.02883 | SemanticDialect: Semantic-Aware Mixed-Format Quantization for Video Diffusion Transformers | 03-03 | 通用量化（权重/激活/训练） | quantization、video、diffusion、edge deployment |
| 11 | 2603.03380 | LiteVLA-Edge: Quantized On-Device Multimodal Control for Embedded Robotics | 03-03 | 通用量化（权重/激活/训练） | quantization、low-bit、LLM、VLM/MLLM |
| 12 | 2603.03681 | EvoPrune: Early-Stage Visual Token Pruning for Efficient MLLMs | 03-04 | Token 剪枝（多模态/视频） | pruning、token pruning、LLM、VLM/MLLM |
| 13 | 2603.04162 | Bielik-Q2-Sharp: A Comparative Study of Extreme 2-bit Quantization Methods for a Polish 11B Language Model | 03-04 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、rotation/Hadamard |
| 14 | 2603.04308 | Activation Outliers in Transformer Quantization: Reproduction, Statistical Analysis, and Deployment Tradeoffs | 03-04 | 通用量化（权重/激活/训练） | quantization、PTQ、mixed-precision、LLM |
| 15 | 2603.04359 | Dissecting Quantization Error: A Concentration-Alignment Perspective | 03-04 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、rotation/Hadamard |
| 16 | 2603.04800 | MASQuant: Modality-Aware Smoothing Quantization for Multimodal Large Language Models | 03-05 | 通用量化（权重/激活/训练） | quantization、PTQ、LLM、VLM/MLLM |
| 17 | 2603.04956 | WaterSIC: Information-Theoretically (Near) Optimal Linear Layer Quantization | 03-05 | 通用量化（权重/激活/训练） | quantization、KV cache、GPTQ |
| 18 | 2603.05105 | Diff-ES: Stage-wise Structural Diffusion Pruning via Evolutionary Search | 03-05 | 剪枝与稀疏 | pruning、structured pruning、sparsity、diffusion |
| 19 | 2603.05168 | Sparse-BitNet: 1.58-bit LLMs are Naturally Friendly to Semi-Structured Sparsity | 03-05 | 通用量化（权重/激活/训练） | quantization、low-bit、sparsity、LLM |
| 20 | 2603.05232 | SlideSparse: Fast and Flexible (2N-2):2N Structured Sparsity | 03-05 | 通用量化（权重/激活/训练） | quantization、low-bit、pruning、sparsity |
| 21 | 2603.05421 | DARK: Diagonal-Anchored Repulsive Knowledge Distillation for Vision-Language Models under Extreme Compression | 03-05 | 知识蒸馏 | distillation、LLM、VLM/MLLM、edge deployment |
| 22 | 2603.05878 | ROSE: Reordered SparseGPT for More Accurate One-Shot Large Language Models Pruning | 03-06 | 剪枝与稀疏 | quantization、pruning、sparsity、LLM |
| 23 | 2603.05950 | Energy-Driven Adaptive Visual Token Pruning for Efficient Vision-Language Models | 03-06 | Token 剪枝（多模态/视频） | pruning、token pruning、VLM/MLLM、reasoning |
| 24 | 2603.06003 | EvoESAP: Non-Uniform Expert Pruning for Sparse MoE | 03-06 | 剪枝与稀疏 | pruning、structured pruning、sparsity、MoE |
| 25 | 2603.06746 | ButterflyViT: 354$\times$ Expert Compression for Edge Vision Transformers | 03-06 | 通用量化（权重/激活/训练） | quantization、low-bit、rotation/Hadamard、pruning |
| 26 | 2603.07904 | DyQ-VLA: Temporal-Dynamic-Aware Quantization for Embodied Vision-Language-Action Models | 03-09 | 通用量化（权重/激活/训练） | quantization、VLM/MLLM、edge deployment |
| 27 | 2603.08065 | Deterministic Differentiable Structured Pruning for Large Language Models | 03-09 | 剪枝与稀疏 | pruning、structured pruning、sparsity、LLM |
| 28 | 2603.08083 | High-Fidelity Pruning for Large Language Models | 03-09 | 知识蒸馏 | pruning、distillation、LLM |
| 29 | 2603.08173 | Evolution Strategy-Based Calibration for Low-Bit Quantization of Speech Models | 03-09 | 通用量化（权重/激活/训练） | quantization、PTQ、QAT、low-bit |
| 30 | 2603.08185 | SERQ: Saliency-Aware Low-Rank Error Reconstruction for LLM Quantization | 03-09 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、rotation/Hadamard |
| 31 | 2603.08258 | WaDi: Weight Direction-aware Distillation for One-step Image Synthesis | 03-09 | 知识蒸馏 | rotation/Hadamard、distillation、diffusion、LoRA/PEFT |
| 32 | 2603.08747 | Diagnosing FP4 inference: a layer-wise and block-wise sensitivity analysis of NVFP4 and MXFP4 | 03-05 | 通用量化（权重/激活/训练） | quantization、low-bit、KV cache、LLM |
| 33 | 2603.09582 | BinaryAttention: One-Bit QK-Attention for Vision and Diffusion Transformers | 03-10 | 通用量化（权重/激活/训练） | quantization、PTQ、QAT、low-bit |
| 34 | 2603.10444 | The Curse and Blessing of Mean Bias in FP4-Quantized LLM Training | 03-11 | 通用量化（权重/激活/训练） | quantization、low-bit、rotation/Hadamard、sparsity |
| 35 | 2603.10899 | LookaheadKV: Fast and Accurate KV Cache Eviction by Glimpsing into the Future without Generation | 03-11 | KV Cache 压缩（非量化） | KV cache、long-context、LLM、LoRA/PEFT |
| 36 | 2603.11021 | Leech Lattice Vector Quantization for Efficient LLM Compression | 03-11 | 通用量化（权重/激活/训练） | quantization、PTQ、rotation/Hadamard、LLM |
| 37 | 2603.11504 | LongFlow: Efficient KV Cache Compression for Reasoning Models | 03-12 | KV Cache 压缩（非量化） | KV cache、reasoning |
| 38 | 2603.11564 | Where Matters More Than What: Decoding-aligned KV Cache Compression via Position-aware Pseudo Queries | 03-12 | KV Cache 压缩（非量化） | KV cache、long-context、LLM |
| 39 | 2603.11881 | Bielik-Minitron-7B: Compressing Large Language Models via Structured Pruning and Knowledge Distillation for the Polish Language | 03-12 | 知识蒸馏 | pruning、structured pruning、distillation、LLM |
| 40 | 2603.13418 | GPrune-LLM: Generalization-Aware Structured Pruning for Large Language Models | 03-12 | 剪枝与稀疏 | pruning、structured pruning、sparsity、LLM |
| 41 | 2603.13765 | Knowledge Distillation for Large Language Models | 03-14 | 通用量化（权重/激活/训练） | quantization、low-bit、distillation、LLM |
| 42 | 2603.13931 | True 4-Bit Quantized Convolutional Neural Network Training on CPU: Achieving Full-Precision Parity | 03-14 | 通用量化（权重/激活/训练） | quantization、PTQ、QAT、low-bit |
| 43 | 2603.14062 | TMPDiff: Temporal Mixed-Precision for Diffusion Models | 03-14 | 通用量化（权重/激活/训练） | quantization、mixed-precision、LLM、diffusion |
| 44 | 2603.14224 | Self-Indexing KVCache: Predicting Sparse Attention from Compressed Keys | 03-15 | KV Cache 量化 | quantization、low-bit、KV cache、long-context |
| 45 | 2603.14303 | SemantiCache: Efficient KV Cache Compression via Semantic Chunking and Clustered Merging | 03-15 | KV Cache 压缩（非量化） | KV cache、LLM |
| 46 | 2603.16435 | VQKV: High-Fidelity and High-Ratio Cache Compression via Vector-Quantization | 03-17 | KV Cache 量化 | quantization、KV cache、LLM |
| 47 | 2603.16590 | BATQuant: Outlier-resilient MXFP4 Quantization via Learnable Block-wise Optimization | 03-17 | 通用量化（权重/激活/训练） | quantization、PTQ、rotation/Hadamard、LLM |
| 48 | 2603.16731 | Understanding Quantization of Optimizer States in LLM Pre-training: Dynamics of State Staleness and Effectiveness of State Resets | 03-17 | 通用量化（权重/激活/训练） | quantization、LLM |
| 49 | 2603.17230 | KANtize: Exploring Low-bit Quantization of Kolmogorov-Arnold Networks for Efficient Inference | 03-18 | 通用量化（权重/激活/训练） | quantization、low-bit、FPGA/hardware |
| 50 | 2603.17354 | Beyond Outliers: A Data-Free Layer-wise Mixed-Precision Quantization Approach Driven by Numerical and Structural Dual-Sensitivity | 03-18 | 通用量化（权重/激活/训练） | quantization、low-bit、mixed-precision、outlier |
| 51 | 2603.17891 | RAMP: Reinforcement Adaptive Mixed Precision Quantization for Efficient On Device LLM Inference | 03-18 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、mixed-precision |
| 52 | 2603.18095 | Q-Drift: Quantization-Aware Drift Correction for Diffusion Model Sampling | 03-18 | 通用量化（权重/激活/训练） | quantization、PTQ、QAT、KV cache |
| 53 | 2603.18423 | SynQ: Accurate Zero-shot Quantization by Synthesis-aware Fine-tuning | 03-19 | 通用量化（权重/激活/训练） | quantization、PTQ、LLM、edge deployment |
| 54 | 2603.18426 | Prune-then-Quantize or Quantize-then-Prune? Understanding the Impact of Compression Order in Joint Model Compression | 03-19 | 通用量化（权重/激活/训练） | quantization、mixed-precision、pruning |
| 55 | 2603.18492 | AIMER: Calibration-Free Task-Agnostic MoE Expert Pruning | 03-19 | 剪枝与稀疏 | pruning、MoE、calibration |
| 56 | 2603.18742 | 6Bit-Diffusion: Inference-Time Mixed-Precision Quantization for Video Diffusion Models | 03-19 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、mixed-precision |
| 57 | 2603.19172 | DyMoE: Dynamic Expert Orchestration with Mixed-Precision Quantization for Efficient MoE Inference on Edge | 03-19 | 通用量化（权重/激活/训练） | quantization、mixed-precision、MoE、edge deployment |
| 58 | 2603.19296 | TTQ: Activation-Aware Test-Time Quantization to Accelerate LLM Inference On The Fly | 03-11 | 通用量化（权重/激活/训练） | quantization、KV cache、LLM、speculative decoding |
| 59 | 2603.19664 | The Residual Stream Is All You Need: On the Redundancy of the KV Cache in Transformer Inference | 03-20 | KV Cache 压缩（非量化） | KV cache |
| 60 | 2603.20280 | Mix-and-Match Pruning: Globally Guided Layer-Wise Sparsification of DNNs | 03-17 | 剪枝与稀疏 | pruning、sparsity、edge deployment |
| 61 | 2603.20616 | Beyond Token Eviction: Mixed-Dimension Budget Allocation for Efficient KV Cache Compression | 03-21 | KV Cache 压缩（非量化） | KV cache、long-context |
| 62 | 2603.20991 | Structural Sensitivity in Compressed Transformers: Relative Error Propagation and Layer Removal | 03-22 | 剪枝与稀疏 | pruning、structured pruning、sparsity、LLM |
| 63 | 2603.21105 | ResPrune: Text-Conditioned Subspace Reconstruction for Visual Token Pruning in Large Vision-Language Models | 03-22 | Token 剪枝（多模态/视频） | pruning、token pruning、VLM/MLLM |
| 64 | 2603.21365 | TIDE: Token-Informed Depth Execution for Per-Token Early Exit in LLM Inference | 03-22 | 早退机制（Early Exit） | distillation、early exit、LLM、MoE |
| 65 | 2603.21426 | Uncertainty-Aware Knowledge Distillation for Multimodal Large Language Models | 03-22 | 知识蒸馏 | distillation、LLM、VLM/MLLM |
| 66 | 2603.22056 | Dual-Space Knowledge Distillation with Key-Query Matching for Large Language Models with Vocabulary Mismatch | 03-23 | 知识蒸馏 | distillation、LLM、MoE |
| 67 | 2603.22324 | DAQ: Delta-Aware Quantization for Post-Training LLM Weight Compression | 03-20 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、LLM |
| 68 | 2603.22355 | Demystifying Low-Rank Knowledge Distillation in Large Language Models: Convergence, Generalization, and Information-Theoretic Guarantees | 03-22 | 知识蒸馏 | distillation、LLM |
| 69 | 2603.22370 | FAAR: Format-Aware Adaptive Rounding for NVFP4 | 03-23 | 通用量化（权重/激活/训练） | quantization、low-bit、LLM、edge deployment |
| 70 | 2603.22910 | EchoKV: Efficient KV Cache Compression via Similarity-Based Reconstruction | 03-24 | KV Cache 压缩（非量化） | KV cache、long-context、LLM |
| 71 | 2603.22911 | ForestPrune: High-ratio Visual Token Compression for Video Multimodal Large Language Models via Spatial-Temporal Forest Modeling | 03-24 | Token 剪枝（多模态/视频） | KV cache、pruning、token pruning、LLM |
| 72 | 2603.22943 | PersonalQ: Select, Quantize, and Serve Personalized Diffusion Models for Efficient Inference | 03-24 | 通用量化（权重/激活/训练） | quantization、PTQ、mixed-precision、LLM |
| 73 | 2603.23575 | APreQEL: Adaptive Mixed Precision Quantization For Edge LLMs | 03-24 | 通用量化（权重/激活/训练） | quantization、mixed-precision、KV cache、LLM |
| 74 | 2603.23701 | The Diminishing Returns of Early-Exit Decoding in Modern LLMs | 03-24 | 早退机制（Early Exit） | early exit、LLM、MoE |
| 75 | 2603.23985 | Diet Your LLM: Dimension-wise Global Pruning of LLMs via Merging Task-specific Importance Score | 03-25 | 剪枝与稀疏 | pruning、structured pruning、sparsity、LLM |
| 76 | 2603.24652 | Demystifying When Pruning Works via Representation Hierarchies | 03-25 | 剪枝与稀疏 | pruning、distillation、embedding |
| 77 | 2603.24680 | ReDiPrune: Relevance-Diversity Pre-Projection Token Pruning for Efficient Multimodal LLMs | 03-25 | Token 剪枝（多模态/视频） | pruning、token pruning、LLM、VLM/MLLM |
| 78 | 2603.25284 | SliderQuant: Accurate Post-Training Quantization for LLMs | 03-26 | 通用量化（权重/激活/训练） | quantization、PTQ、QAT、rotation/Hadamard |
| 79 | 2603.25325 | How Pruning Reshapes Features: Sparse Autoencoder Analysis of Weight-Pruned Language Models | 03-26 | 剪枝与稀疏 | pruning、structured pruning、sparsity、LLM |
| 80 | 2603.25385 | GlowQ: Group-Shared LOw-Rank Approximation for Quantized LLMs | 03-26 | 通用量化（权重/激活/训练） | quantization、low-bit、rotation/Hadamard、KV cache |
| 81 | 2603.25562 | Revisiting On-Policy Distillation: Empirical Failure Modes and Simple Fixes | 03-26 | 知识蒸馏 | distillation、LLM、reasoning、agent |
| 82 | 2603.26556 | When Perplexity Lies: Generation-Focused Distillation of Hybrid Sequence Models | 03-27 | KV Cache 压缩（非量化） | KV cache、distillation |
| 83 | 2603.26778 | TED: Training-Free Experience Distillation for Multimodal Reasoning | 03-25 | 知识蒸馏 | distillation、VLM/MLLM、reasoning、agent |
| 84 | 2603.27467 | TurboAngle: Near-Lossless KV Cache Compression via Uniform Angle Quantization | 03-29 | KV Cache 量化 | quantization、low-bit、rotation/Hadamard、KV cache |
| 85 | 2603.27469 | KV Cache Quantization for Self-Forcing Video Generation: A 33-Method Empirical Study | 03-29 | KV Cache 量化 | quantization、low-bit、KV cache、pruning |
| 86 | 2603.27650 | V-CAST: Video Curvature-Aware Spatio-Temporal Pruning for Efficient Video Large Language Models | 03-29 | Token 剪枝（多模态/视频） | long-context、pruning、token pruning、LLM |
| 87 | 2603.27819 | KVSculpt: KV Cache Compression as Distillation | 03-29 | KV Cache 量化 | quantization、KV cache、long-context、distillation |
| 88 | 2603.27900 | Rényi Entropy: A New Token Pruning Metric for Vision Transformers | 03-29 | Token 剪枝（多模态/视频） | pruning、token pruning、VLM/MLLM |
| 89 | 2603.27914 | ITQ3_S: High-Fidelity 3-bit LLM Inference via Interleaved Ternary Quantization with Rotation-Domain Smoothing | 03-30 | 通用量化（权重/激活/训练） | quantization、low-bit、rotation/Hadamard、KV cache |
| 90 | 2603.28430 | IsoQuant: Hardware-Aligned SO(4) Isoclinic Rotations for LLM KV Cache Compression | 03-30 | KV Cache 量化 | quantization、low-bit、rotation/Hadamard、KV cache |
| 91 | 2603.28845 | OneComp: One-Line Revolution for Generative AI Model Compression | 03-30 | 通用量化（权重/激活/训练） | quantization、mixed-precision、FPGA/hardware、calibration |
| 92 | 2603.29078 | PolarQuant: Optimal Gaussian Weight Quantization via Hadamard Rotation for LLM Compression | 03-30 | 通用量化（权重/激活/训练） | quantization、PTQ、low-bit、rotation/Hadamard |
| 93 | 2603.29535 | Quantization with Unified Adaptive Distillation to enable multi-LoRA based one-for-all Generative Vision Models on edge | 03-31 | 通用量化（权重/激活/训练） | quantization、distillation、LLM、edge deployment |
| 94 | 2603.29768 | Big2Small: A Unifying Neural Network Framework for Model Compression | 03-31 | 通用量化（权重/激活/训练） | quantization、pruning、distillation、LLM |
| 95 | 2604.00223 | Diversity-Aware Reverse Kullback-Leibler Divergence for Large Language Model Distillation | 03-31 | 知识蒸馏 | distillation、LLM |
| 96 | 2604.03258 | SoLA: Leveraging Soft Activation Sparsity and Low-Rank Decomposition for Large Language Model Compression | 03-12 | 剪枝与稀疏 | sparsity、LLM |
| 97 | 2604.03298 | ENEC: A Lossless AI Model Compression Method Enabling Fast Inference on Ascend NPUs | 03-28 | 通用量化（权重/激活/训练） | quantization、LLM、FPGA/hardware |
| 98 | 2604.08558 | WAND: Windowed Attention and Knowledge Distillation for Efficient Autoregressive Text-to-Speech Models | 03-17 | KV Cache 压缩（非量化） | KV cache、distillation、LLM、speech/audio |
| 99 | 2604.09595 | Why Smaller Is Slower? Dimensional Misalignment in Compressed LLMs | 03-05 | 剪枝与稀疏 | pruning、LLM |
| 100 | 2604.18592 | Two-dimensional early exit optimisation of LLM inference | 03-27 | 早退机制（Early Exit） | quantization、pruning、early exit、LLM |
| 101 | 2604.19769 | TTKV: Temporal-Tiered KV Cache for Long-Context LLM Inference | 03-27 | KV Cache 压缩（非量化） | KV cache、long-context、LLM |

---

## 三、按技术方向分类

### 3.1 通用量化（权重/激活/训练） — 48 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| SliderQuant: Accurate Post-Training Qua… (2603.25284) | Llama2 | SliderQuant 发现 LLM 浅层/深层比中间层对量化更敏感、且首/末层最敏感，提出层间滑动量化（三种滑动窗口… |
| Quasar: Quantized Self-Speculative Acce… (2603.01399) | Qwen3  | Quasar 指出自投机/前瞻解码把瓶颈转移到验证阶段（全精度前向受显存带宽限制），提出免训练框架——**专对验证阶段… |
| Boosting Entropy with Bell Box Quantiza… (2603.01599) | — | BBQ 提出"量化器输出不必与输入同域"的核心洞察，在输入域做信息论最优（ITO）量化、在输出域映射回计算高效的整数类… |
| ITQ3_S: High-Fidelity 3-bit LLM Inferen… (2603.27914) | — | ITQ3_S 先用快速 Walsh-Hadamard 变换（FWHT）把权重预旋转为近似高斯分布，再做均匀三值编码，并… |
| WaterSIC: Information-Theoretically (Ne… (2603.04956) | Qwen  | 本文从信息论角度分析稠密线性层转低精度时"压缩长度-输出偏差"的权衡，证明流行的 GPTQ 与信息论极限的差距可任意大… |
| SlideSparse: Fast and Flexible (2N-2):2… (2603.05232) | Qwen2.5-7B | SlideSparse 的滑动窗口分解把任意 (2N-2):2N 权重块无损重构为 N-1 个重叠的 2:4 兼容窗口… |
| RAMP: Reinforcement Adaptive Mixed Prec… (2603.17891) | Llama 2 7B | RAMP 用离策略 Soft Actor-Critic 学习逐层比特分配以在全局比特预算下最小化困惑度，策略以 11 … |
| ENEC: A Lossless AI Model Compression M… (2604.03298) | — | ENEC 针对昇腾 NPU 上权重数据传输瓶颈与现有无损压缩算法移植后吞吐极低的问题，提出专为 AI 模型权重定制、为… |
| BinaryAttention: One-Bit QK-Attention f… (2603.09582) | ViT 与 | BinaryAttention 理论论证"二值化注意力保留本质相似性关系"，仅保留 Q/K 符号、用位运算替代浮点点积… |
| True 4-Bit Quantized Convolutional Neur… (2603.13931) | clip | 本文提出 tanh 软权重裁剪 + 对称量化 + 逐层动态缩放 + 直通估计器的组合，在普通 CPU（Google C… |
| PolarQuant: Optimal Gaussian Weight Qua… (2603.29078) | Qwen3.5-9B | PolarQuant 通过"块级归一化到单位超球面 → Walsh-Hadamard 旋转 → 匹配高斯分布质心量化"… |
| FreeAct: Freeing Activations for LLM Qu… (2603.01776) | — | FreeAct 打破变换类量化方法的"静态一对一变换"约束，利用激活的秩亏特性把激活变换与权重变换解耦，为不同 tok… |
| Dissecting Quantization Error: A Concen… (2603.04359) | — | 本文用信号量化噪声比（SQNR）分解线性层量化误差，证明固定比特下 SQNR 由**权重/激活的集中度**（离散度与异… |
| MASQuant: Modality-Aware Smoothing Quan… (2603.04800) | — | MASQuant 以 SmoothQuant 为案例剖析其用于 MLLM 的两大问题——平滑失配（Smoothing … |
| Sparse-BitNet: 1.58-bit LLMs are Natura… (2603.05168) | — | Sparse-BitNet 首次把 1.58-bit 量化与动态 N:M 稀疏统一到一个稳定训练框架，发现 1.58-… |
| ButterflyViT: 354$\times$ Expert Compre… (2603.06746) | ViT | ButterflyViT 不再把专家当作独立权重矩阵，而是把专家视为**统一共享量化基底的几何重定向**——对共享三值… |
| SERQ: Saliency-Aware Low-Rank Error Rec… (2603.08185) | — | SERQ 用**单个低秩补偿矩阵**（而非两个顺序因子）做误差重建，通过静态激活平坦化、显著性感知误差重建、离线权重置… |
| BATQuant: Outlier-resilient MXFP4 Quant… (2603.16590) | Clip | BATQuant 指出为整数格式设计的全局正交旋转与 MXFP4 存在根本性格式失配（旋转把异常值能量跨量化块转移、并… |
| OneComp: One-Line Revolution for Genera… (2603.28845) | — | OneComp 把碎片化的量化算法、精度预算、校准策略与硬件执行细节整合为一个可复现、资源自适应的管线——给定模型标识… |
| SemanticDialect: Semantic-Aware Mixed-F… (2603.02883) | — | SemanticDialect 把块级混合格式量化推进到"语义感知"层面——每个块从扩充了查找表的格式簿（format… |
| The Curse and Blessing of Mean Bias in … (2603.10444) | Qwen3 0.6B | 本文系统分析 FP4 量化 LLM 训练中"均值偏置（mean bias）"现象的双重作用——它既是损伤训练稳定性的"… |
| GlowQ: Group-Shared LOw-Rank Approximat… (2603.25385) | vity | GlowQ 针对低秩校正方法（LQER/QERA/ASER）在每层都插入校正模块带来的延迟与显存开销，提出在每个输入共… |
| Quantization with Unified Adaptive Dist… (2603.29535) | — | QUAD 把 LoRA 权重当作运行时输入（而非编译进模型图），实现单一共享模型动态切换多任务、无需重编译；再通过量化… |
| LiteVLA-Edge: Quantized On-Device Multi… (2603.03380) | — | LiteVLA-Edge 在 Jetson Orin 级硬件上实现完全端侧 VLA 推理——FP32 监督图像到动作微… |
| Evolution Strategy-Based Calibration fo… (2603.08173) | — | ESC 发现音频激活的校准范围大导致标准校准信息损失严重，把激活缩放建模为优化问题并用"两步局部-全局"进化策略求解；… |
| Knowledge Distillation for Large Langua… (2603.13765) | Qwen 3B | 本文用 Qwen 3B（教师）蒸馏 Qwen 0.5B（学生），在英语/西班牙语 Dolly-15k 与代码 BugN… |
| TMPDiff: Temporal Mixed-Precision for D… (2603.14062) | FLUX | TMPDiff 打破"所有去噪步用同一精度"的惯例，提出按时间步分配不同数值精度的框架；基于"量化误差随时间步加性累积… |
| Beyond Outliers: A Data-Free Layer-wise… (2603.17354) | vity | NSDS 指出现有逐层混合精度量化（LMPQ）把层内所有权重模块同质化、且只用单一数值属性估计敏感度，于是把每层机理分… |
| DyMoE: Dynamic Expert Orchestration wit… (2603.19172) | vity | DyMoE 基于"专家重要性高度倾斜且随深度变化"的观察，提出重要性感知动态量化、深度自适应调度、前瞻预取三件套，在商… |
| FAAR: Format-Aware Adaptive Rounding fo… (2603.22370) | Llama3-1B | FAAR 指出传统舍入策略忽视 NVFP4 数值网格的非均匀性导致次优舍入，提出把非均匀网格显式纳入优化、由损失梯度自… |
| Leech Lattice Vector Quantization for E… (2603.11021) | vity | 本文把 24 维 Leech 格（已知最高维的最优球堆积/亲吻构型）引入 LLM 量化，扩展基于扩展 Golay 码构… |
| SynQ: Accurate Zero-shot Quantization b… (2603.18423) | ViT 无显式 | SynQ 针对零样本量化的三大障碍——合成数据噪声、基于偏离目标模式的预测、错误硬标签误导——提出低通滤波去噪、类激活… |
| Prune-then-Quantize or Quantize-then-Pr… (2603.18426) | — | 本文首次系统研究"先剪枝后量化"还是"先量化后剪枝"的顺序问题，形式化压缩顺序优化并提出**渐进强度假说**（较弱扰动… |
| TTQ: Activation-Aware Test-Time Quantiz… (2603.19296) | — | TTQ 把量化校准从离线搬到测试时——通过高效的在线校准，使激活感知量化能适配每一个 prompt、无论下游任务是否见… |
| Big2Small: A Unifying Neural Network Fr… (2603.29768) | — | 本文用测度论构建模型压缩的统一数学框架，证明每种压缩技术在数学上等价于一个带正则化的神经网络；据此提出免数据压缩框架 … |
| Practical FP4 Training for Large-Scale … (2603.02731) | — | 本文面向 Hopper GPU 提出大规模 MoE 模型的实用 FP4 训练方案，解决 MoE 架构在低比特训练下的独… |
| DyQ-VLA: Temporal-Dynamic-Aware Quantiz… (2603.07904) | vity | DyQ-VLA 针对 VLA 模型静态量化的两大挑战——时序动态敏感性（固定精度忽视各阶段误差容忍度差异）与实时分配难… |
| Q-Drift: Quantization-Aware Drift Corre… (2603.18095) | CLIP | Q-Drift 把量化误差视为每个去噪步上的隐式随机扰动，推导出保持边缘分布的漂移校正，仅需 5 组配对的全精度/量化… |
| PersonalQ: Select, Quantize, and Serve … (2603.22943) | — | PersonalQ 用检查点的"触发 token"作为共享信号，把检查点选择（意图对齐混合检索 + LLM 重排 + … |
| APreQEL: Adaptive Mixed Precision Quant… (2603.23575) | — | APreQEL 通过分析逐层贡献并推断不同量化类型在目标硬件上的行为，在内存、延迟、精度的用户自定义优先级下为每层分配… |
| 6Bit-Diffusion: Inference-Time Mixed-Pr… (2603.18742) | vity | 6Bit-Diffusion 发现"块的输入-输出差异"与其内部线性层量化敏感度强线性相关，据此设计轻量预测器动态分配… |
| SageBwd: A Trainable Low-bit Attention (2603.02170) | — | SageBwd 把 SageAttention 从推理扩展到训练——对 7 个注意力矩阵乘中的 6 个做 INT8 量… |
| Bielik-Q2-Sharp: A Comparative Study of… (2603.04162) | Mistral  | Bielik-Q2-Sharp 是首个针对波兰语 LLM 的 2-bit 量化系统评测——以 Bielik-11B-v… |
| Diagnosing FP4 inference: a layer-wise … (2603.08747) | vity | 本文对 NVFP4 与 MXFP4 两种主流 FP4 微缩放格式做了逐层、逐块的敏感度分析，系统诊断 FP4 推理中哪… |
| KANtize: Exploring Low-bit Quantization… (2603.17230) | — | KANtize 系统研究低比特量化对 KAN 的影响——KAN 用可学习 B 样条激活（系数为可学习参数），推理时样条… |
| Understanding Quantization of Optimizer… (2603.16731) | — | 本文研究低精度 EMA 优化器状态，揭示量化使许多名义更新舍入回原值、状态"停滞"而减慢适应；建立单步停滞概率的预测模… |
| DAQ: Delta-Aware Quantization for Post-… (2603.22324) | — | DAQ 指出标准重建式量化目标与基座模型无关，会让量化噪声不成比例地破坏编码后训练行为的小幅度参数增量 ΔW；它用"符… |
| Activation Outliers in Transformer Quan… (2603.04308) | vity | 本文在 BERT-base/QNLI 上复现并扩展了 Bondarenko 等（EMNLP 2021）的激活异常值现象… |

### 3.2 KV Cache 量化 — 6 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| Self-Indexing KVCache: Predicting Spars… (2603.14224) | — | 本文提出把压缩后的 key 表示不仅当存储、更当**自索引结构**直接支持稀疏注意力——设计基于符号的 1-bit 向… |
| KVSculpt: KV Cache Compression as Disti… (2603.27819) | Qwen2.5-1.5B | KVSculpt 跳出"选择或合并原始 KV 对"的范式，直接在连续嵌入空间**优化一组不受约束的更小 KV 对**以… |
| VQKV: High-Fidelity and High-Ratio Cach… (2603.16435) | LLaMA3.1-8B | VQKV 首次把向量量化（VQ）引入免训练 KV cache 压缩，用少量整数索引表示数千浮点值，同时实现高压缩率与高… |
| TurboAngle: Near-Lossless KV Cache Comp… (2603.27467) | Mistral-7B | TurboAngle 在 FWHT 域量化角度——随机对角旋转使相邻元素对在单位圆上近似均匀分布，再配合逐层 earl… |
| IsoQuant: Hardware-Aligned SO(4) Isocli… (2603.28430) | — | IsoQuant 用四元数把每个 4D 块表示为单位四元数并施加闭式变换 T(v)=q_L·v·q̄_R，实现 SO(… |
| KV Cache Quantization for Self-Forcing … (2603.27469) | Wan2.1 | 本文在 Wan2.1 Self-Forcing 堆栈上系统评测 33 种量化与缓存策略变体（610 个 prompt … |

### 3.3 KV Cache 压缩（非量化） — 11 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| LookaheadKV: Fast and Accurate KV Cache… (2603.10899) | — | LookaheadKV 针对 prompt KV 驱逐中"重要性估计无法预见未来需求"的问题，借鉴近期"窥视未来"思路… |
| EchoKV: Efficient KV Cache Compression … (2603.22910) | — | EchoKV 不同于改动模型投影的低秩压缩（无法切回全缓存），用轻量网络从保留的子集**重建被丢弃的 KV 成分**（… |
| LongFlow: Efficient KV Cache Compressio… (2603.11504) | DeepSeek-R1  | LongFlow 针对 OpenAI-o1/DeepSeek-R1 类推理模型"长输出"场景（现有方法多为长输入短输出… |
| SemantiCache: Efficient KV Cache Compre… (2603.14303) | — | SemantiCache 指出现有 KV 压缩作用于离散 token 或非语义块会造成"语义碎片化"（连贯语言单元被打… |
| Understanding the Physics of Key-Value … (2603.01426) | Qwen  | 本文提出把 KV 压缩视为对 token 级路由的受控扰动，区分保留、可及、利用三概念；合成任务实验发现：中等压缩几乎… |
| Beyond Token Eviction: Mixed-Dimension … (2603.20616) | — | MixedDimKV 把 token 驱逐视为"每 token 要么零维要么满维"的粗糙降维，提出在更细粒度上为不同 … |
| TTKV: Temporal-Tiered KV Cache for Long… (2604.19769) | — | TTKV 借鉴人类记忆（清晰度、回忆频率、相关性随时间邻近性变化），把 KV cache 划分为**容量与精度异构的时… |
| Where Matters More Than What: Decoding-… (2603.11564) | — | 本文指出现有 KV 压缩用 prefill 阶段输入侧注意力估计重要性、无法保留未来生成所需的关键 token；发现构… |
| WAND: Windowed Attention and Knowledge … (2604.08558) | — | WAND 把 AR-TTS 的注意力拆分为"条件 token 的持久全局注意力 + 生成 token 的局部滑窗注意力… |
| The Residual Stream Is All You Need: On… (2603.19664) | Gemma 3 | 本文证明 KV cache 这一"必需状态"完全冗余——每层的 key/value 都是残差流的确定性投影，用每 to… |
| When Perplexity Lies: Generation-Focuse… (2603.26556) | Qwen3-0.6B | 本文揭示"困惑度会说谎"——一个 7B 蒸馏模型在对数似然评分下与教师仅差 0.2pp，自回归生成时却落后 20.8p… |

### 3.4 剪枝与稀疏 — 14 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| 3BASiL: An Algorithmic Framework for Sp… (2603.01376) | LLaMA-8B | 3BASiL-TM 用带收敛保证的 3 块 ADMM 最小化逐层重建误差，再用 Transformer 匹配（TM）精… |
| ROSE: Reordered SparseGPT for More Accu… (2603.05878) | LLaMA2-7B | ROSE 发现 SparseGPT 固定的从左到右剪枝顺序在权重呈列状模式时是次优的，于是先做预剪枝识别候选权重并估计… |
| EvoESAP: Non-Uniform Expert Pruning for… (2603.06003) | — | EvoESAP 把专家剪枝解耦为"层内专家排序"与"跨层预算分配"两问，指出现有方法默认均匀层间稀疏度而预算分配强烈影… |
| Deterministic Differentiable Structured… (2603.08065) | Qwen3-32B | DDP 把结构化剪枝视为 L0 稀疏约束下的乘性门控学习，但不用随机 hard-concrete 松弛，而是直接优化离… |
| Structural Sensitivity in Compressed Tr… (2603.20991) | vity | 本文定义 ρ = 层输出误差/输入误差，直接测量 6 个 Transformer（117M–8B）的误差传播，发现：层… |
| Diet Your LLM: Dimension-wise Global Pr… (2603.23985) | Gemma-2 | DIET 只用每任务 100 个样本分析各任务的激活幅度，再以多数投票融合任务特异重要性分数构建单一全局掩码，实现维度… |
| SoLA: Leveraging Soft Activation Sparsi… (2604.03258) | LLaMA-2-7B | SoLA 识别并保留对推理贡献显著的少数成分、用低秩分解压缩其余多数成分，实现免训练、无需特殊硬件、无需昂贵后训练的 … |
| Diff-ES: Stage-wise Structural Diffusio… (2603.05105) | SDXL | Diff-ES 指出扩散模型各去噪步的重要性高度非均匀且依模型而异，现有方法（如 MosaicDiff）靠手工调的阶段… |
| GPrune-LLM: Generalization-Aware Struct… (2603.13418) | vity | GPrune-LLM 发现神经元存在分布敏感性差异——分布鲁棒神经元跨数据集排名稳定、分布敏感神经元排名方差大；据此把… |
| Why Smaller Is Slower? Dimensional Misa… (2604.09595) | Llama-3-8B | 本文揭示后训练压缩产生的不规则张量维度会让 GPU 执行栈效率下降（"维度失配"）——ASVD 压缩 Llama-3-… |
| Mix-and-Match Pruning: Globally Guided … (2603.20280) | vity | Mix-and-Match Pruning 用敏感度分数与简单架构规则生成多样的高质量剪枝配置——推导架构感知的稀疏度… |
| AIMER: Calibration-Free Task-Agnostic M… (2603.18492) | — | AIMER 指出现有任务无关专家剪枝依赖校准集（用路由/激活统计估计重要性），决策对校准数据敏感且预处理成本高；提出基… |
| Demystifying When Pruning Works via Rep… (2603.24652) | — | 本文把语言模型内部计算分解为嵌入（表示）、logit（softmax 前）、概率（softmax 后）三个顺序空间，发… |
| How Pruning Reshapes Features: Sparse A… (2603.25325) | Gemma 3 | 本文首次用稀疏自编码器（SAE）系统研究非结构化剪枝对 LM 内部表示的影响——跨 3 个模型家族（Gemma 3 1… |

### 3.5 Token 剪枝（多模态/视频） — 8 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| V-CAST: Video Curvature-Aware Spatio-Te… (2603.27650) | Qwen3- | V-CAST 指出紧预算下视频 token 压缩的瓶颈是**时空信息覆盖不足**——粗粒度逐帧分配或场景切分造成覆盖不… |
| Rényi Entropy: A New Token Pruning Metr… (2603.27900) | ViT 与大型视觉语言模型上持续超越 | 本文指出依赖 [CLS] token 估计 patch 重要性在浅层不可靠（语义表示尚不成熟），提出源自 Rényi … |
| AgilePruner: An Empirical Study of Atte… (2603.01236) | — | AgilePruner 用有效秩（erank）与注意力分数熵系统对比注意力式与多样性式视觉 token 剪枝，发现：许… |
| ResPrune: Text-Conditioned Subspace Rec… (2603.21105) | LLaVA-1 | ResPrune 把视觉 token 剪枝建模为**子空间重构问题**——用残差能量引导的贪心子空间扩展选择 toke… |
| EvoPrune: Early-Stage Visual Token Prun… (2603.03681) | — | EvoPrune 指出多数视觉 token 剪枝在编码之后才进行，忽视了编码阶段本身的巨大计算成本；EvoPrune … |
| Energy-Driven Adaptive Visual Token Pru… (2603.05950) | LLaVA-1 | E-AdaPrune 指出多数视觉 token 削减方法对所有输入用固定预算、忽视图像信息密度差异，提出从视觉特征空间… |
| ForestPrune: High-ratio Visual Token Co… (2603.22911) | LLaVA-OneVision | ForestPrune 把视频 token 压缩的短板归因于对时序与连续视频内容建模不足，提出免训练的时空森林建模——… |
| ReDiPrune: Relevance-Diversity Pre-Proj… (2603.24680) | LLaVA-NeXT | ReDiPrune 在视觉-语言投影**之前**（视觉特征仍丰富可辨时）做免训练 token 剪枝，用轻量规则联合**… |

### 3.6 知识蒸馏 — 11 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| High-Fidelity Pruning for Large Languag… (2603.08083) | Qwen  | 本文指出用 Taylor 展开 + one-hot 交叉熵估计神经元重要性只关注单个预测 token 的概率、忽视模型… |
| KDFlow: A User-Friendly and Efficient K… (2603.01875) | — | KDFlow 指出学生/教师在 KD 中角色不同却共用同一训练后端（FSDP/DeepSpeed）导致效率次优，于是用… |
| WaDi: Weight Direction-aware Distillati… (2603.08258) | Stable Diffusion | WaDi 分析一步学生与多步教师之间 U-Net/DiT 的权重变化，发现**权重方向变化显著大于范数变化**——方向… |
| Diversity-Aware Reverse Kullback-Leible… (2604.00223) | — | 本文把反向 KL（RKL）的梯度分解为目标与非目标分量，发现**非目标梯度在学生已匹配教师时仍持续推高目标 logit… |
| Uncertainty-Aware Knowledge Distillatio… (2603.21426) | — | Beta-KD 从贝叶斯视角统一师生学习，把教师监督解释为 Gibbs 先验，按样本的教师不确定性与数据噪声自适应调节… |
| TED: Training-Free Experience Distillat… (2603.26778) | Qwen3- | TED 把蒸馏的更新目标从模型参数转移到注入学生提示词的"上下文经验"——学生对每个输入生成多条推理轨迹，教师独立解题… |
| Dual-Space Knowledge Distillation with … (2603.22056) | — | 本文系统分析词表不匹配蒸馏 SOTA 方法 DSKD-CMA 的注意力机制——通过手工 token 对齐探针与热力图可… |
| DARK: Diagonal-Anchored Repulsive Knowl… (2603.05421) | CLIP | DARK 主张在师生容量差达一个数量级时"严格模仿教师是坏目标"，把蒸馏损失分解为对角项（匹配的图文对，全程锚定对齐）… |
| Bielik-Minitron-7B: Compressing Large L… (2603.11881) | — | Bielik-Minitron-7B 借鉴 NVIDIA Minitron 两阶段方法，用结构化混合剪枝 + logi… |
| Demystifying Low-Rank Knowledge Distill… (2603.22355) | — | 本文为低秩知识蒸馏（如 Low-Rank Clone）建立严格理论框架——证明温和假设下低秩投影保留优化动态（收敛率 … |
| Revisiting On-Policy Distillation: Empi… (2603.25562) | — | 本文从理论与实现双面重审 OPD——标准实现把分布匹配简化为采样 token 对数比，在长 rollout（前缀漂移出… |

### 3.7 早退机制（Early Exit） — 3 篇

| 论文 | 目标模型 | 核心贡献（摘自一句话总结） |
|------|---------|--------------------------|
| TIDE: Token-Informed Depth Execution fo… (2603.21365) | DeepSeek R1  | TIDE 在周期性检查点层挂接微型学习路由器，推理时为每个 token 选择隐藏状态已收敛的最早退出层；免重训练、兼容… |
| Two-dimensional early exit optimisation… (2604.18592) | Llama 3.1 | 本文提出二维 early exit——逐句增量处理输入的同时渐进激活更深层，协调"层级退出"与"句级退出"获得超过任一… |
| The Diminishing Returns of Early-Exit D… (2603.23701) | — | 本文重新评估逐层 early-exit（预测足够置信即提前停算），发现随着新模型采用更优预训练配方与架构、层冗余下降，… |

---

## 四、按应用领域分类

| 应用领域 | 论文数量 | 代表性论文 |
|---------|:-------:|-----------|
| 大语言模型（LLM） | 64 | SliderQuant: Accurate P…、Quasar: Quantized Self-…、ITQ3_S: High-Fidelity 3… |
| 多模态/视觉语言（VLM/MLLM） | 15 | FreeAct: Freeing Activa…、MASQuant: Modality-Awar…、BATQuant: Outlier-resil… |
| 视频生成/视频理解 | 7 | SemanticDialect: Semant…、V-CAST: Video Curvature…、EvoPrune: Early-Stage V… |
| 语音/音频 | 2 | Evolution Strategy-Base…、WAND: Windowed Attentio… |
| 扩散模型 | 9 | BinaryAttention: One-Bi…、FreeAct: Freeing Activa…、SemanticDialect: Semant… |
| 推荐/检索/嵌入 | 8 | RAMP: Reinforcement Ada…、Self-Indexing KVCache: …、KVSculpt: KV Cache Comp… |
| 边缘/端侧部署 | 27 | Boosting Entropy with B…、RAMP: Reinforcement Ada…、True 4-Bit Quantized Co… |
| 硬件协同（FPGA/GPU/NPU） | 22 | ITQ3_S: High-Fidelity 3…、SlideSparse: Fast and F…、RAMP: Reinforcement Ada… |
| MoE | 9 | SliderQuant: Accurate P…、EvoESAP: Non-Uniform Ex…、ButterflyViT: 354$\time… |
| 长文本/长上下文 | 9 | LookaheadKV: Fast and A…、Self-Indexing KVCache: …、V-CAST: Video Curvature… |

（一篇论文可属于多个应用领域。）

---

## 五、值得关注的高亮点

1. **[2603.01599] Boosting Entropy with Bell Box Quantization**（本月已附代码复现 demo）：BBQ 提出"量化器输出不必与输入同域"的核心洞察，在输入域做信息论最优（ITO）量化、在输出域映射回计算高效的整数类型，在不牺牲计算效率的前提下，使 4/3/2/1-bit 模型的困惑度分别较此前 SOTA QAPT 方法最多降低 2/4/5/18 个点（ICLR 2026 录用）。

2. **[2603.01776] FreeAct: Freeing Activations for LLM Quantization**（本月已附代码复现 demo）：FreeAct 打破变换类量化方法的"静态一对一变换"约束，利用激活的秩亏特性把激活变换与权重变换解耦，为不同 token 类型（视觉/文本、掩码 token）分配各自的激活变换矩阵、权重侧保持统一静态变换，在 dLLM 与 MLLM 上较基线最高提升 5.3%。

3. **[2603.16590] BATQuant: Outlier-resilient MXFP4 Quantization via Learnable Block-wise Optimization**（本月已附代码复现 demo）：BATQuant 指出为整数格式设计的全局正交旋转与 MXFP4 存在根本性格式失配（旋转把异常值能量跨量化块转移、并制造双峰分布），于是把变换限制到与 MXFP 粒度对齐、放松正交约束做分布整形，配合全局-私有 Kronecker 分解与块级可学习裁剪，在激进 W4A4KV16 下恢复多模态基准 96.43% 的全精度性能，刷新 SOTA。

4. **[2603.17891] RAMP: Reinforcement Adaptive Mixed Precision Quantization for Efficient On Device LLM Inference**（本月已附代码复现 demo）：RAMP 用离策略 Soft Actor-Critic 学习逐层比特分配以在全局比特预算下最小化困惑度，策略以 11 维激活/权重/结构统计嵌入为条件实现零样本跨模型迁移；配合 Scale Folding 预处理把激活异常值迁入权重，在 Llama 2 7B 上以 3.65 有效比特达 5.54 PPL，优于均匀 4-bit AWQ（5.60）与 GPTQ，且仅在 Llama 2 7B 上训练的策略可零样本迁移到 Llama 2 13B 与 Mistral 7B。

5. **[2603.25284] SliderQuant: Accurate Post-Training Quantization for LLMs**（本月已附代码复现 demo）：SliderQuant 发现 LLM 浅层/深层比中间层对量化更敏感、且首/末层最敏感，提出层间滑动量化（三种滑动窗口设计）+ 层内增量滑动量化的两级框架，仅用少量可学习参数即可跨层降低量化误差，在 Llama/Llama2/Llama3/Qwen2.5、DeepSeek-R1 蒸馏模型与大型 MoE 上超越包括旋转变换类最新 PTQ 在内的现有方法（ICLR 2026 录用，代码开源）。

6. **[2603.27467] TurboAngle: Near-Lossless KV Cache Compression via Uniform Angle Quantization**（本月已附代码复现 demo）：TurboAngle 在 FWHT 域量化角度——随机对角旋转使相邻元素对在单位圆上近似均匀分布，再配合逐层 early-boost（每层独立配置 K/V 码本大小、给关键层更高精度），在 7 个 1B–7B 模型上 6 个达近无损（4 个无损）、每元素仅 3.28–3.67 角度比特；配合非对称范数量化（K 8-bit、V 4-bit 对数域），Mistral-7B 总 6.56 bit/元素、PPL 仅退化 +0.0014 且免校准。

7. **[2603.27914] ITQ3_S: High-Fidelity 3-bit LLM Inference via Interleaved Ternary Quantization with Rotation-Domain Smoothing**（本月已附代码复现 demo）：ITQ3_S 先用快速 Walsh-Hadamard 变换（FWHT）把权重预旋转为近似高斯分布，再做均匀三值编码，并将 256 点逆 FWHT 融合进 CUDA 共享内存加载阶段，使重构误差仅由三值网格决定；在 RTX 5090 上达到与 FP16 竞争的困惑度，吞吐超过 4-bit 方案的 1.5 倍。

8. **[2603.29078] PolarQuant: Optimal Gaussian Weight Quantization via Hadamard Rotation for LLM Compression**（本月已附代码复现 demo）：PolarQuant 通过"块级归一化到单位超球面 → Walsh-Hadamard 旋转 → 匹配高斯分布质心量化"三阶段，使 Qwen3.5-9B 的 absmax Q5 困惑度从 6.90 降至 6.40（距 FP16 仅 +0.03），消融显示 Hadamard 旋转贡献 98% 的改进，且无需任何校准数据；作为 INT4 预处理还能把 absmax INT4 的 PPL 从 6.68 降到 6.56。

9. **[2603.01399] Quasar: Quantized Self-Speculative Acceleration for Rapid Inference via Memory-Efficient Verification**：Quasar 指出自投机/前瞻解码把瓶颈转移到验证阶段（全精度前向受显存带宽限制），提出免训练框架——**专对验证阶段用低比特量化**减半显存流量；实证显示激进结构剪枝损害验证精度而量化验证能高保真保留 logit 分布，在 OpenPangu 与 Qwen3 上保持与全精度相当的接受长度并实现 1.28× 端到端吞吐提升。

10. **[2603.01376] 3BASiL: An Algorithmic Framework for Sparse plus Low-Rank Compression of LLMs**：3BASiL-TM 用带收敛保证的 3 块 ADMM 最小化逐层重建误差，再用 Transformer 匹配（TM）精炼步骤跨层联合优化稀疏与低秩成分；在（2:4 稀疏 + 64 低秩）配置下，把 LLaMA-8B 相对稠密的 WikiText2 PPL 差距较此前方法缩小 30% 以上，且压缩运行时在 A100 上比 SOTA S+LR 方法快 2.5×。

11. **[2603.04956] WaterSIC: Information-Theoretically (Near) Optimal Linear Layer Quantization**：本文从信息论角度分析稠密线性层转低精度时"压缩长度-输出偏差"的权衡，证明流行的 GPTQ 与信息论极限的差距可任意大；提出 WaterSIC——模仿经典"注水（waterfilling）"解法为权重矩阵不同列分配不同量化码率，对所有输入激活协方差矩阵一致地把码率差距控制在 0.255 bit 内，在 Llama 与 Qwen 家族上 1–4 bit 全部码率刷新 SOTA。

---

## 六、四维量化评分表（101 篇全量）

**评分口径（1–10 分，编辑评定，规则化初评 + 抽样复核）**：
- **精度效果**：论文报告精度结果的强度（无损/超越基线/显著提升加分；纯实证分析类无新精度结果减分）
- **压缩倍率**：压缩激进程度（≤2bit/三值/二值 +2，3–4bit +1，仅 8bit −2；高倍率数字 +1；分析类封顶 4）
- **创新性**：机制新颖度（首次/新机制 +1，旋转/格/角度/演化/合并等非常规机制 +1，纯 benchmark/综述 −1）
- **可复现性**：代码开源 +2，标准模型/基准 +1，闭源超大模型 −1，本仓库已复现 demo 的论文 +2

| 序号 | arXiv ID | 论文 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 均分 |
|:---:|----------|------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2603.25284 | SliderQuant: Accurate Post-Traini… | 8 | 7 | 8 | 10 | 8.2 |
| 2 | 2603.01399 | Quasar: Quantized Self-Speculativ… | 8 | 8 | 8 | 8 | 8.0 |
| 3 | 2603.01599 | Boosting Entropy with Bell Box Qu… | 7 | 9 | 7 | 9 | 8.0 |
| 4 | 2603.27914 | ITQ3_S: High-Fidelity 3-bit LLM I… | 7 | 10 | 8 | 7 | 8.0 |
| 5 | 2603.01376 | 3BASiL: An Algorithmic Framework … | 8 | 7 | 8 | 8 | 7.8 |
| 6 | 2603.04956 | WaterSIC: Information-Theoretical… | 7 | 8 | 8 | 8 | 7.8 |
| 7 | 2603.05232 | SlideSparse: Fast and Flexible (2… | 7 | 9 | 7 | 8 | 7.8 |
| 8 | 2603.17891 | RAMP: Reinforcement Adaptive Mixe… | 7 | 8 | 8 | 8 | 7.8 |
| 9 | 2604.03298 | ENEC: A Lossless AI Model Compres… | 8 | 8 | 8 | 7 | 7.8 |
| 10 | 2603.09582 | BinaryAttention: One-Bit QK-Atten… | 8 | 9 | 5 | 8 | 7.5 |
| 11 | 2603.13931 | True 4-Bit Quantized Convolutiona… | 7 | 9 | 8 | 6 | 7.5 |
| 12 | 2603.29078 | PolarQuant: Optimal Gaussian Weig… | 7 | 8 | 7 | 8 | 7.5 |
| 13 | 2603.01776 | FreeAct: Freeing Activations for … | 7 | 7 | 8 | 7 | 7.2 |
| 14 | 2603.04359 | Dissecting Quantization Error: A … | 8 | 8 | 8 | 5 | 7.2 |
| 15 | 2603.04800 | MASQuant: Modality-Aware Smoothin… | 8 | 7 | 7 | 7 | 7.2 |
| 16 | 2603.05168 | Sparse-BitNet: 1.58-bit LLMs are … | 7 | 8 | 7 | 7 | 7.2 |
| 17 | 2603.05878 | ROSE: Reordered SparseGPT for Mor… | 8 | 6 | 7 | 8 | 7.2 |
| 18 | 2603.06003 | EvoESAP: Non-Uniform Expert Pruni… | 8 | 6 | 8 | 7 | 7.2 |
| 19 | 2603.06746 | ButterflyViT: 354$\times$ Expert … | 6 | 10 | 8 | 5 | 7.2 |
| 20 | 2603.08185 | SERQ: Saliency-Aware Low-Rank Err… | 8 | 8 | 8 | 5 | 7.2 |
| 21 | 2603.10899 | LookaheadKV: Fast and Accurate KV… | 8 | 8 | 6 | 7 | 7.2 |
| 22 | 2603.16590 | BATQuant: Outlier-resilient MXFP4… | 6 | 8 | 7 | 8 | 7.2 |
| 23 | 2603.28845 | OneComp: One-Line Revolution for … | 8 | 7 | 7 | 7 | 7.2 |
| 24 | 2603.02883 | SemanticDialect: Semantic-Aware M… | 8 | 8 | 7 | 5 | 7.0 |
| 25 | 2603.08065 | Deterministic Differentiable Stru… | 7 | 8 | 7 | 6 | 7.0 |
| 26 | 2603.10444 | The Curse and Blessing of Mean Bi… | 6 | 8 | 6 | 8 | 7.0 |
| 27 | 2603.14224 | Self-Indexing KVCache: Predicting… | 6 | 9 | 8 | 5 | 7.0 |
| 28 | 2603.25385 | GlowQ: Group-Shared LOw-Rank Appr… | 6 | 8 | 6 | 8 | 7.0 |
| 29 | 2603.27650 | V-CAST: Video Curvature-Aware Spa… | 7 | 7 | 8 | 6 | 7.0 |
| 30 | 2603.27819 | KVSculpt: KV Cache Compression as… | 6 | 8 | 8 | 6 | 7.0 |
| 31 | 2603.27900 | Rényi Entropy: A New Token Prunin… | 8 | 7 | 7 | 6 | 7.0 |
| 32 | 2603.29535 | Quantization with Unified Adaptiv… | 6 | 10 | 7 | 5 | 7.0 |
| 33 | 2603.01236 | AgilePruner: An Empirical Study o… | 8 | 7 | 5 | 7 | 6.8 |
| 34 | 2603.03380 | LiteVLA-Edge: Quantized On-Device… | 6 | 8 | 7 | 6 | 6.8 |
| 35 | 2603.08083 | High-Fidelity Pruning for Large L… | 8 | 5 | 6 | 8 | 6.8 |
| 36 | 2603.08173 | Evolution Strategy-Based Calibrat… | 8 | 6 | 8 | 5 | 6.8 |
| 37 | 2603.13765 | Knowledge Distillation for Large … | 7 | 8 | 6 | 6 | 6.8 |
| 38 | 2603.14062 | TMPDiff: Temporal Mixed-Precision… | 8 | 8 | 6 | 5 | 6.8 |
| 39 | 2603.16435 | VQKV: High-Fidelity and High-Rati… | 5 | 8 | 8 | 6 | 6.8 |
| 40 | 2603.17354 | Beyond Outliers: A Data-Free Laye… | 8 | 7 | 7 | 5 | 6.8 |
| 41 | 2603.19172 | DyMoE: Dynamic Expert Orchestrati… | 7 | 8 | 7 | 5 | 6.8 |
| 42 | 2603.20991 | Structural Sensitivity in Compres… | 7 | 7 | 7 | 6 | 6.8 |
| 43 | 2603.22370 | FAAR: Format-Aware Adaptive Round… | 7 | 7 | 7 | 6 | 6.8 |
| 44 | 2603.22910 | EchoKV: Efficient KV Cache Compre… | 8 | 7 | 7 | 5 | 6.8 |
| 45 | 2603.01875 | KDFlow: A User-Friendly and Effic… | 6 | 6 | 7 | 7 | 6.5 |
| 46 | 2603.08258 | WaDi: Weight Direction-aware Dist… | 8 | 5 | 8 | 5 | 6.5 |
| 47 | 2603.11021 | Leech Lattice Vector Quantization… | 7 | 7 | 7 | 5 | 6.5 |
| 48 | 2603.11504 | LongFlow: Efficient KV Cache Comp… | 7 | 7 | 7 | 5 | 6.5 |
| 49 | 2603.14303 | SemantiCache: Efficient KV Cache … | 7 | 7 | 7 | 5 | 6.5 |
| 50 | 2603.18423 | SynQ: Accurate Zero-shot Quantiza… | 8 | 7 | 6 | 5 | 6.5 |
| 51 | 2603.18426 | Prune-then-Quantize or Quantize-t… | 6 | 7 | 8 | 5 | 6.5 |
| 52 | 2603.19296 | TTQ: Activation-Aware Test-Time Q… | 7 | 7 | 7 | 5 | 6.5 |
| 53 | 2603.21105 | ResPrune: Text-Conditioned Subspa… | 8 | 7 | 5 | 6 | 6.5 |
| 54 | 2603.23985 | Diet Your LLM: Dimension-wise Glo… | 8 | 6 | 6 | 6 | 6.5 |
| 55 | 2603.29768 | Big2Small: A Unifying Neural Netw… | 7 | 7 | 7 | 5 | 6.5 |
| 56 | 2604.00223 | Diversity-Aware Reverse Kullback-… | 8 | 5 | 8 | 5 | 6.5 |
| 57 | 2604.03258 | SoLA: Leveraging Soft Activation … | 8 | 6 | 6 | 6 | 6.5 |
| 58 | 2603.01426 | Understanding the Physics of Key-… | 6 | 8 | 5 | 6 | 6.2 |
| 59 | 2603.02731 | Practical FP4 Training for Large-… | 7 | 8 | 6 | 4 | 6.2 |
| 60 | 2603.05105 | Diff-ES: Stage-wise Structural Di… | 6 | 6 | 8 | 5 | 6.2 |
| 61 | 2603.07904 | DyQ-VLA: Temporal-Dynamic-Aware Q… | 6 | 8 | 6 | 5 | 6.2 |
| 62 | 2603.13418 | GPrune-LLM: Generalization-Aware … | 7 | 6 | 7 | 5 | 6.2 |
| 63 | 2603.18095 | Q-Drift: Quantization-Aware Drift… | 6 | 7 | 6 | 6 | 6.2 |
| 64 | 2603.20616 | Beyond Token Eviction: Mixed-Dime… | 8 | 7 | 5 | 5 | 6.2 |
| 65 | 2603.21365 | TIDE: Token-Informed Depth Execut… | 6 | 5 | 6 | 8 | 6.2 |
| 66 | 2603.21426 | Uncertainty-Aware Knowledge Disti… | 8 | 5 | 5 | 7 | 6.2 |
| 67 | 2603.22943 | PersonalQ: Select, Quantize, and … | 7 | 7 | 6 | 5 | 6.2 |
| 68 | 2603.23575 | APreQEL: Adaptive Mixed Precision… | 6 | 7 | 7 | 5 | 6.2 |
| 69 | 2603.26778 | TED: Training-Free Experience Dis… | 7 | 6 | 6 | 6 | 6.2 |
| 70 | 2603.27467 | TurboAngle: Near-Lossless KV Cach… | 6 | 4 | 7 | 8 | 6.2 |
| 71 | 2603.28430 | IsoQuant: Hardware-Aligned SO(4) … | 6 | 7 | 7 | 5 | 6.2 |
| 72 | 2604.09595 | Why Smaller Is Slower? Dimensiona… | 6 | 6 | 7 | 6 | 6.2 |
| 73 | 2604.18592 | Two-dimensional early exit optimi… | 7 | 5 | 7 | 6 | 6.2 |
| 74 | 2604.19769 | TTKV: Temporal-Tiered KV Cache fo… | 6 | 8 | 6 | 5 | 6.2 |
| 75 | 2603.03681 | EvoPrune: Early-Stage Visual Toke… | 7 | 7 | 5 | 5 | 6.0 |
| 76 | 2603.05950 | Energy-Driven Adaptive Visual Tok… | 7 | 7 | 5 | 5 | 6.0 |
| 77 | 2603.11564 | Where Matters More Than What: Dec… | 6 | 7 | 6 | 5 | 6.0 |
| 78 | 2603.18742 | 6Bit-Diffusion: Inference-Time Mi… | 6 | 6 | 7 | 5 | 6.0 |
| 79 | 2603.20280 | Mix-and-Match Pruning: Globally G… | 6 | 6 | 7 | 5 | 6.0 |
| 80 | 2603.22056 | Dual-Space Knowledge Distillation… | 7 | 5 | 7 | 5 | 6.0 |
| 81 | 2603.22911 | ForestPrune: High-ratio Visual To… | 6 | 7 | 6 | 5 | 6.0 |
| 82 | 2604.08558 | WAND: Windowed Attention and Know… | 6 | 7 | 6 | 5 | 6.0 |
| 83 | 2603.05421 | DARK: Diagonal-Anchored Repulsive… | 6 | 6 | 5 | 6 | 5.8 |
| 84 | 2603.18492 | AIMER: Calibration-Free Task-Agno… | 7 | 6 | 5 | 5 | 5.8 |
| 85 | 2603.19664 | The Residual Stream Is All You Ne… | 5 | 4 | 6 | 8 | 5.8 |
| 86 | 2603.24652 | Demystifying When Pruning Works v… | 5 | 4 | 7 | 7 | 5.8 |
| 87 | 2603.27469 | KV Cache Quantization for Self-Fo… | 6 | 4 | 6 | 7 | 5.8 |
| 88 | 2603.02170 | SageBwd: A Trainable Low-bit Atte… | 5 | 4 | 8 | 5 | 5.5 |
| 89 | 2603.04162 | Bielik-Q2-Sharp: A Comparative St… | 5 | 4 | 7 | 6 | 5.5 |
| 90 | 2603.08747 | Diagnosing FP4 inference: a layer… | 6 | 4 | 6 | 6 | 5.5 |
| 91 | 2603.11881 | Bielik-Minitron-7B: Compressing L… | 6 | 5 | 6 | 5 | 5.5 |
| 92 | 2603.17230 | KANtize: Exploring Low-bit Quanti… | 7 | 4 | 6 | 5 | 5.5 |
| 93 | 2603.23701 | The Diminishing Returns of Early-… | 6 | 5 | 6 | 5 | 5.5 |
| 94 | 2603.24680 | ReDiPrune: Relevance-Diversity Pr… | 6 | 4 | 5 | 7 | 5.5 |
| 95 | 2603.25325 | How Pruning Reshapes Features: Sp… | 5 | 4 | 7 | 6 | 5.5 |
| 96 | 2603.26556 | When Perplexity Lies: Generation-… | 6 | 4 | 6 | 6 | 5.5 |
| 97 | 2603.16731 | Understanding Quantization of Opt… | 6 | 4 | 6 | 5 | 5.2 |
| 98 | 2603.22324 | DAQ: Delta-Aware Quantization for… | 5 | 4 | 7 | 5 | 5.2 |
| 99 | 2603.22355 | Demystifying Low-Rank Knowledge D… | 6 | 4 | 6 | 5 | 5.2 |
| 100 | 2603.04308 | Activation Outliers in Transforme… | 4 | 4 | 6 | 6 | 5.0 |
| 101 | 2603.25562 | Revisiting On-Policy Distillation… | 5 | 4 | 5 | 5 | 4.8 |

### 6.1 整体分析

- **全月 101 篇均分 6.53**；均分 ≥7 的论文 32 篇，≤5 的 2 篇。
- **通用量化（权重/激活/训练）（48 篇，均分 6.79）**：最高分 2603.25284（8.2）——SliderQuant 发现 LLM 浅层/深层比中间层对量化更敏感、且首/末层最敏感，提出层间滑动量化（三种滑动窗口设计）+ 层内增量滑…
- **KV Cache 量化（6 篇，均分 6.50）**：最高分 2603.14224（7.0）——本文提出把压缩后的 key 表示不仅当存储、更当**自索引结构**直接支持稀疏注意力——设计基于符号的 1-bit 向量量化方案，把压缩与…
- **KV Cache 压缩（非量化）（11 篇，均分 6.26）**：最高分 2603.10899（7.2）——LookaheadKV 针对 prompt KV 驱逐中"重要性估计无法预见未来需求"的问题，借鉴近期"窥视未来"思路（用草稿生成器产生替…
- **剪枝与稀疏（14 篇，均分 6.48）**：最高分 2603.01376（7.8）——3BASiL-TM 用带收敛保证的 3 块 ADMM 最小化逐层重建误差，再用 Transformer 匹配（TM）精炼步骤跨层联合优化稀…
- **Token 剪枝（多模态/视频）（8 篇，均分 6.35）**：最高分 2603.27650（7.0）——V-CAST 指出紧预算下视频 token 压缩的瓶颈是**时空信息覆盖不足**——粗粒度逐帧分配或场景切分造成覆盖不连续，token 合…
- **知识蒸馏（11 篇，均分 6.00）**：最高分 2603.08083（6.8）——本文指出用 Taylor 展开 + one-hot 交叉熵估计神经元重要性只关注单个预测 token 的概率、忽视模型其他潜在预测；直觉的…
- **早退机制（Early Exit）（3 篇，均分 5.97）**：最高分 2603.21365（6.2）——TIDE 在周期性检查点层挂接微型学习路由器，推理时为每个 token 选择隐藏状态已收敛的最早退出层；免重训练、兼容任意 Hugging…

**均分分布**：4.x 分 1 篇，5.x 分 18 篇，6.x 分 50 篇，7.x 分 28 篇，8+ 分 4 篇。

**趋势观察**：
1. **旋转/正交变换成为低比特量化的主流前处理**（Hadamard/FWHT/SO(4) 相关 15 篇），从权重量化扩散到 KV cache 与 MXFP4 块格式；
2. **KV cache 压缩是最活跃的应用驱动方向**（17 篇），长上下文与视频生成是主要拉力；
3. **混合精度分配走向自动化**（敏感度画像、RL 策略、演化搜索），逐层/逐块预算分配取代统一位宽；
4. **剪枝研究从方法转向理解**（多篇'剪枝何时有效/如何重塑表示'的分析型工作），结构化剪枝与 MoE 专家剪枝仍是工程主力；
5. **蒸馏与压缩合流**：KV 压缩即蒸馏、on-policy 蒸馏失败模式分析等显示两子领域边界正在消融。

---

## 七、量化方法代码复现（8 个 demo）

| arXiv ID | 方法 | 复现内容 | 验证方式 |
|----------|------|---------|---------|
| 2603.29078 | PolarQuant | 块归一化 + Hadamard 旋转 + 高斯质心量化 | 真实 Qwen3-0.6B（本地缓存），失败回退同构 mock |
| 2603.27914 | ITQ3_S | FWHT 旋转域三值量化 + 融合逆变换 | Qwen3-0.6B 同构 mock 重尾权重 |
| 2603.25284 | SliderQuant | 层敏感度画像 + 敏感度驱动比特分配 + 层内增量窗口量化 | 24 层正交探针网络（mock） |
| 2603.01599 | BBQ | ITO 分位学习 + 整数码字映射 | mock 权重 |
| 2603.27467 | TurboAngle | FWHT 域角度量化 KV cache + 早层提升分配 | mock KV cache（GQA 14/2 头） |
| 2603.01776 | FreeAct | 逐 token 类型激活变换 + 统一权重量化 | mock 多模态异质激活 |
| 2603.17891 | RAMP | 11 维层嵌入 + 选择性 Scale Folding + 预算比特分配 + 零样本迁移 | 异质敏感度 mock（64d→96d 迁移） |
| 2603.16590 | BATQuant | MXFP4 量化器 + 全局旋转危害复现 + STE 块级仿射 | 含异常值 mock 张量 |

全部 demo 已在本环境实际运行通过（`python3 demo.py`，输出末行 `[demo] OK`）；目录 `scripts/quantization/<arxiv_id>/{README.md, demo.py}`，README 如实标注验证方式。
