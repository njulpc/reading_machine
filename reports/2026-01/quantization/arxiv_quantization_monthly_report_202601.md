# arXiv 模型压缩月度报告：2026 年 1 月（量化专题）

> **数据来源**: arXiv API 19 组关键词查询（1099 篇候选）+ arxiv.org 12 个类目 2026-01 全量列表（9456 条）交叉过滤
> **收录标准**: v1 提交于 2026-01-01 至 2026-01-31；主题严格限于模型压缩核心方向（量化/剪枝/稀疏/蒸馏/KV cache/token 压缩）
> **论文总数**: 246 篇 ｜ **量化相关**: 80 篇（含 mixed_precision 去重）
> **生成时间**: 2026-01 回填 ｜ 仓库: reading_machine feature/arxiv-monthly-2026-01

---

## 一、本月概览

2026 年 1 月 arXiv 模型压缩方向共产出 246 篇相关论文。主题分布（一篇可多标签，按主标签归类）：

| 方向 | 数量 | 占比 |
| --- | --- | --- |
| 量化 (Quantization) | 74 | 30.1% |
| 知识蒸馏 (Distillation) | 53 | 21.5% |
| 剪枝 (Pruning) | 31 | 12.6% |
| KV Cache 压缩 | 28 | 11.4% |
| 稀疏化 (Sparsity) | 26 | 10.6% |
| 通用/其他压缩 | 19 | 7.7% |
| Token 压缩 | 9 | 3.7% |
| 混合精度/数值格式 | 6 | 2.4% |

量化方向 80 篇中：训练后量化（PTQ）与量化感知训练（QAT）并重，4-bit/FP4 数值格式（MXFP4/NVFP4/M2XFP）成为预训练与推理双场景焦点；量化研究的安全、公平、多语言维度明显升温；算法-硬件协同设计（NPU/FPGA/CAM/加速器）占比显著。

## 二、全部论文总览表（246 篇）

| # | arXiv | 标题 | 作者(前2) | 提交日期 | 主方向 |
| --- | --- | --- | --- | --- | --- |
| 1 | [2601.00202](https://arxiv.org/abs/2601.00202) | Knowledge Distillation for Temporal Knowledge Graph Reasoning with Large Lang... | Wang Xing, Wei Song 等 | 2026-01-01 | 知识蒸馏 (Distillation) |
| 2 | [2601.00222](https://arxiv.org/abs/2601.00222) | LooC: Effective Low-Dimensional Codebook for Compositional Vector Quantization | Jie Li, Kwan-Yee K. Wong 等 | 2026-01-01 | 量化 (Quantization) |
| 3 | [2601.00282](https://arxiv.org/abs/2601.00282) | Can Large Language Models Still Explain Themselves? Investigating the Impact ... | Qianli Wang, Nils Feldhus 等 | 2026-01-01 | 量化 (Quantization) |
| 4 | [2601.00359](https://arxiv.org/abs/2601.00359) | Efficient Prediction of Dense Visual Embeddings via Distillation and RGB-D Tr... | Söhnke Benedikt Fischedick, Daniel Seichter 等 | 2026-01-01 | 知识蒸馏 (Distillation) |
| 5 | [2601.00426](https://arxiv.org/abs/2601.00426) | RMAAT: Astrocyte-Inspired Memory Compression and Replay for Efficient Long-Co... | Md Zesun Ahmed Mia, Malyaban Bal 等 | 2026-01-01 | KV Cache 压缩 |
| 6 | [2601.00434](https://arxiv.org/abs/2601.00434) | Time--to--Digital Converter (TDC)--Based Resonant Compute--in--Memory for INT... | Dhandeep Challagundla, Ignatius Bezzam 等 | 2026-01-01 | 量化 (Quantization) |
| 7 | [2601.00679](https://arxiv.org/abs/2601.00679) | QSLM: A Performance- and Memory-aware Quantization Framework with Tiered Sear... | Rachmad Vidya Wicaksana Putra, Pasindu Wickramasinghe 等 | 2026-01-02 | 量化 (Quantization) |
| 8 | [2601.00714](https://arxiv.org/abs/2601.00714) | KDPhys: An Attention Guided 3D to 2D Knowledge Distillation for Real-time Vid... | Nicky Nirlipta Sahoo, VS Sachidanand 等 | 2026-01-02 | 知识蒸馏 (Distillation) |
| 9 | [2601.00913](https://arxiv.org/abs/2601.00913) | Clean-GS: Semantic Mask-Guided Pruning for 3D Gaussian Splatting | Subhankar Mishra | 2026-01-01 | 剪枝 (Pruning) |
| 10 | [2601.00926](https://arxiv.org/abs/2601.00926) | MACA: A Framework for Distilling Trustworthy LLMs into Efficient Retrievers | Satya Swaroop Gudipudi, Sahil Girhepuje 等 | 2026-01-01 | 知识蒸馏 (Distillation) |
| 11 | [2601.00942](https://arxiv.org/abs/2601.00942) | Reliability Under Randomness: An Empirical Analysis of Sparse and Dense Langu... | Kabir Grover | 2026-01-02 | 稀疏化 (Sparsity) |
| 12 | [2601.01204](https://arxiv.org/abs/2601.01204) | XStreamVGGT: Extremely Memory-Efficient Streaming Vision Geometry Grounded Tr... | Zunhai Su, Weihao Ye 等 | 2026-01-03 | KV Cache 压缩 |
| 13 | [2601.01296](https://arxiv.org/abs/2601.01296) | Aggressive Compression Enables LLM Weight Theft | Davis Brown, Juan-Pablo Rivera 等 | 2026-01-03 | 通用/其他压缩 |
| 14 | [2601.01608](https://arxiv.org/abs/2601.01608) | Guiding Token-Sparse Diffusion Models | Felix Krause, Stefan Andreas Baumann 等 | 2026-01-04 | 稀疏化 (Sparsity) |
| 15 | [2601.02213](https://arxiv.org/abs/2601.02213) | Quantized SO(3)-Equivariant Graph Neural Networks for Efficient Molecular Pro... | Haoyu Zhou, Ping Xue 等 | 2026-01-05 | 量化 (Quantization) |
| 16 | [2601.02298](https://arxiv.org/abs/2601.02298) | Power-of-Two Quantization-Aware-Training (PoT-QAT) in Large Language Models (... | Mahmoud Elgenedy | 2026-01-05 | 量化 (Quantization) |
| 17 | [2601.02353](https://arxiv.org/abs/2601.02353) | Meta-Learning Guided Pruning for Few-Shot Plant Pathology on Edge Devices | Mohammed Mudassir Uddin, Shahnawaz Alam 等 | 2026-01-05 | 剪枝 (Pruning) |
| 18 | [2601.02437](https://arxiv.org/abs/2601.02437) | TAP-ViTs: Task-Adaptive Pruning for On-Device Deployment of Vision Transformers | Zhibo Wang, Zuoyuan Zhang 等 | 2026-01-05 | 剪枝 (Pruning) |
| 19 | [2601.02455](https://arxiv.org/abs/2601.02455) | Diagnostic-Driven Layer-Wise Compensation for Post-Training Quantization of E... | Xinyu Wang, Ziyu Zhao 等 | 2026-01-05 | 量化 (Quantization) |
| 20 | [2601.02563](https://arxiv.org/abs/2601.02563) | Compressed code: the hidden effects of quantization and distillation on progr... | Viacheslav Siniaev, Iaroslav Chelombitko 等 | 2026-01-05 | 量化 (Quantization) |
| 21 | [2601.02613](https://arxiv.org/abs/2601.02613) | Sparsity-Aware Streaming SNN Accelerator with Output-Channel Dataflow for Aut... | Kuilian Yang, Li Zhang 等 | 2026-01-06 | 稀疏化 (Sparsity) |
| 22 | [2601.02674](https://arxiv.org/abs/2601.02674) | Iterative Structured Pruning for Large Language Models with Multi-Domain Cali... | Guangxin Wu, Hao Zhang 等 | 2026-01-06 | 剪枝 (Pruning) |
| 23 | [2601.02680](https://arxiv.org/abs/2601.02680) | Adversarial Contrastive Learning for LLM Quantization Attacks | Dinghong Song, Zhiwei Xu 等 | 2026-01-06 | 量化 (Quantization) |
| 24 | [2601.02819](https://arxiv.org/abs/2601.02819) | Punctuation-aware Hybrid Trainable Sparse Attention for Large Language Models | Junxiang Qiu, Shuo Wang 等 | 2026-01-06 | 稀疏化 (Sparsity) |
| 25 | [2601.02888](https://arxiv.org/abs/2601.02888) | RPIQ: Residual-Projected Multi-Collaboration Closed-Loop and Single Instance ... | Xuanyu Wang, Haisen Su 等 | 2026-01-06 | 量化 (Quantization) |
| 26 | [2601.03043](https://arxiv.org/abs/2601.03043) | Lil: Less is Less When Applying Post-Training Sparse-Attention Algorithms in ... | Junhao Hu, Fangze Li 等 | 2026-01-06 | 稀疏化 (Sparsity) |
| 27 | [2601.03067](https://arxiv.org/abs/2601.03067) | Joint Encoding of KV-Cache Blocks for Scalable LLM Serving | Joseph Kampeas, Emir Haleva | 2026-01-06 | KV Cache 压缩 |
| 28 | [2601.03195](https://arxiv.org/abs/2601.03195) | Sparse Knowledge Distillation: A Mathematical Framework for Probability-Domai... | Aaron R. Flouro, Shawn P. Chadwick | 2026-01-06 | 稀疏化 (Sparsity) |
| 29 | [2601.03332](https://arxiv.org/abs/2601.03332) | LUT-KAN: Segment-wise LUT Quantization for Fast KAN Inference | Oleksandr Kuznetsov | 2026-01-06 | 量化 (Quantization) |
| 30 | [2601.03484](https://arxiv.org/abs/2601.03484) | From Bits to Chips: An LLM-based Hardware-Aware Quantization Agent for Stream... | Kaiyuan Deng, Hangyu Zheng 等 | 2026-01-07 | 量化 (Quantization) |
| 31 | [2601.04264](https://arxiv.org/abs/2601.04264) | MemKD: Memory-Discrepancy Knowledge Distillation for Efficient Time Series Cl... | Nilushika Udayangani, Kishor Nandakishor 等 | 2026-01-07 | 知识蒸馏 (Distillation) |
| 32 | [2601.04348](https://arxiv.org/abs/2601.04348) | SCAR-GS: Spatial Context Attention for Residuals in Progressive Gaussian Spla... | Diego Revilla, Pooja Suresh 等 | 2026-01-07 | 通用/其他压缩 |
| 33 | [2601.04359](https://arxiv.org/abs/2601.04359) | PackCache: A Training-Free Acceleration Method for Unified Autoregressive Vid... | Kunyang Li, Mubarak Shah 等 | 2026-01-07 | KV Cache 压缩 |
| 34 | [2601.04519](https://arxiv.org/abs/2601.04519) | TokenSeg: Efficient 3D Medical Image Segmentation via Hierarchical Visual Tok... | Sen Zeng, Hong Zhou 等 | 2026-01-08 | Token 压缩 |
| 35 | [2601.04719](https://arxiv.org/abs/2601.04719) | GPU-Accelerated INT8 Quantization for KV Cache Compression in Large Language ... | Maanas Taneja, Purab Shingvi | 2026-01-08 | 量化 (Quantization) |
| 36 | [2601.05379](https://arxiv.org/abs/2601.05379) | EdgeLDR: Quaternion Low-Displacement Rank Neural Networks for Edge-Efficient ... | Vladimir Frants, Sos Agaian 等 | 2026-01-08 | 通用/其他压缩 |
| 37 | [2601.05388](https://arxiv.org/abs/2601.05388) | Knowledge Distillation of a Protein Language Model Yields a Foundational Impl... | Justin Airas, Bin Zhang | 2026-01-08 | 知识蒸馏 (Distillation) |
| 38 | [2601.05394](https://arxiv.org/abs/2601.05394) | Sketch&Patch++: Efficient Structure-Aware 3D Gaussian Representation | Yuang Shi, Géraldine Morin 等 | 2026-01-08 | 通用/其他压缩 |
| 39 | [2601.05639](https://arxiv.org/abs/2601.05639) | Efficient training for compact compression models via sequential distillation | Caroline Mazini Rodrigues, Nicolas Keriven 等 | 2026-01-09 | 知识蒸馏 (Distillation) |
| 40 | [2601.05684](https://arxiv.org/abs/2601.05684) | FLRQ: Faster LLM Quantization with Flexible Low-Rank Matrix Sketching | Hongyaoxing Gul, Lijuan Hu 等 | 2026-01-09 | 量化 (Quantization) |
| 41 | [2601.05913](https://arxiv.org/abs/2601.05913) | Distilling Lightweight Domain Experts from Large ML Models by Identifying Rel... | Pattarawat Chormai, Ali Hashemi 等 | 2026-01-09 | 知识蒸馏 (Distillation) |
| 42 | [2601.06227](https://arxiv.org/abs/2601.06227) | When Smaller Wins: Dual-Stage Distillation and Pareto-Guided Compression of L... | Dhivya Dharshini Kannan, Wei Li 等 | 2026-01-09 | 知识蒸馏 (Distillation) |
| 43 | [2601.06702](https://arxiv.org/abs/2601.06702) | GRASP LoRA: GRPO Guided Adapter Sparsity Policy for Cross Lingual Transfer | Besher Hassan, Xiuying Chen | 2026-01-10 | 稀疏化 (Sparsity) |
| 44 | [2601.06787](https://arxiv.org/abs/2601.06787) | Garbage Attention in Large Language Models: BOS Sink Heads and Sink-aware Pru... | Jaewon Sok, Jewon Yeom 等 | 2026-01-11 | 剪枝 (Pruning) |
| 45 | [2601.06959](https://arxiv.org/abs/2601.06959) | HAS-VQ: Hessian-Adaptive Sparse Vector Quantization for High-Fidelity LLM Com... | Vladimer Khasia | 2026-01-11 | 量化 (Quantization) |
| 46 | [2601.07048](https://arxiv.org/abs/2601.07048) | GPU-Accelerated ANNS: Quantized for Speed, Built for Change | Hunter McCoy, Zikun Wang 等 | 2026-01-11 | 量化 (Quantization) |
| 47 | [2601.07197](https://arxiv.org/abs/2601.07197) | Beyond Variance: Knowledge-Aware LLM Compression via Fisher-Aligned Subspace ... | Ibne Farabi Shihab, Sanjeda Akter 等 | 2026-01-12 | 通用/其他压缩 |
| 48 | [2601.07212](https://arxiv.org/abs/2601.07212) | MI-PRUN: Optimize Large Language Model Pruning via Mutual Information | Hao Zhang, Zhibin Zhang 等 | 2026-01-12 | 剪枝 (Pruning) |
| 49 | [2601.07372](https://arxiv.org/abs/2601.07372) | Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Lang... | Xin Cheng, Rui Tian 等 | 2026-01-12 | 稀疏化 (Sparsity) |
| 50 | [2601.07396](https://arxiv.org/abs/2601.07396) | Forecast the Principal, Stabilize the Residual: Subspace-Aware Feature Cachin... | Guantao Chen, Shikang Zheng 等 | 2026-01-12 | 通用/其他压缩 |
| 51 | [2601.07475](https://arxiv.org/abs/2601.07475) | ARCQuant: Boosting NVFP4 Quantization with Augmented Residual Channels for LLMs | Haoqian Meng, Yilun Luo 等 | 2026-01-12 | 量化 (Quantization) |
| 52 | [2601.07568](https://arxiv.org/abs/2601.07568) | d3LLM: Ultra-Fast Diffusion LLM using Pseudo-Trajectory Distillation | Yu-Yang Qian, Junda Su 等 | 2026-01-12 | 知识蒸馏 (Distillation) |
| 53 | [2601.07667](https://arxiv.org/abs/2601.07667) | Adaptive Layer Selection for Layer-Wise Token Pruning in LLM Inference | Rei Taniguchi, Yuyang Dong 等 | 2026-01-12 | 剪枝 (Pruning) |
| 54 | [2601.07878](https://arxiv.org/abs/2601.07878) | Sliced-Wasserstein Distribution Alignment Loss Improves the Ultra-Low-Bit Qua... | Deyu Cao, Yixin Yin 等 | 2026-01-11 | 量化 (Quantization) |
| 55 | [2601.07891](https://arxiv.org/abs/2601.07891) | KVzap: Fast, Adaptive, and Faithful KV Cache Pruning | Simon Jegou, Maximilian Jeblick | 2026-01-12 | KV Cache 压缩 |
| 56 | [2601.07892](https://arxiv.org/abs/2601.07892) | Sherry: Hardware-Efficient 1.25-Bit Ternary Quantization via Fine-grained Spa... | Hong Huang, Decheng Wu 等 | 2026-01-12 | 量化 (Quantization) |
| 57 | [2601.08033](https://arxiv.org/abs/2601.08033) | InfGraND: An Influence-Guided GNN-to-MLP Knowledge Distillation | Amir Eskandari, Aman Anand 等 | 2026-01-12 | 知识蒸馏 (Distillation) |
| 58 | [2601.08089](https://arxiv.org/abs/2601.08089) | Q-realign: Piggybacking Realignment on Quantization for Safe and Efficient LL... | Qitao Tan, Xiaoying Song 等 | 2026-01-13 | 量化 (Quantization) |
| 59 | [2601.08169](https://arxiv.org/abs/2601.08169) | Relational Knowledge Distillation Using Fine-tuned Function Vectors | Andrea Kang, Yingnian Wu 等 | 2026-01-13 | 知识蒸馏 (Distillation) |
| 60 | [2601.08301](https://arxiv.org/abs/2601.08301) | ReCo-KD: Region- and Context-Aware Knowledge Distillation for Efficient 3D Me... | Qizhen Lan, Yu-Chun Hsu 等 | 2026-01-13 | 知识蒸馏 (Distillation) |
| 61 | [2601.08343](https://arxiv.org/abs/2601.08343) | When KV Cache Reuse Fails in Multi-Agent Systems: Cross-Candidate Interaction... | Sichu Liang, Zhenglin Wang 等 | 2026-01-13 | KV Cache 压缩 |
| 62 | [2601.08412](https://arxiv.org/abs/2601.08412) | Hybrid Distillation with CoT Guidance for Edge-Drone Control Code Generation | Yizhan Feng, Hichem Snoussi 等 | 2026-01-13 | 知识蒸馏 (Distillation) |
| 63 | [2601.08743](https://arxiv.org/abs/2601.08743) | TableCache: Primary Foreign Key Guided KV Cache Precomputation for Low Latenc... | Jinbo Su, Yuxuan Hu 等 | 2026-01-13 | KV Cache 压缩 |
| 64 | [2601.08764](https://arxiv.org/abs/2601.08764) | FusID: Modality-Fused Semantic IDs for Generative Music Recommendation | Haven Kim, Yupeng Hou 等 | 2026-01-13 | 量化 (Quantization) |
| 65 | [2601.08882](https://arxiv.org/abs/2601.08882) | Compressing Vision Transformers in Geospatial Transfer Learning with Manifold... | Thomas Snyder, H. Lexie Yang 等 | 2026-01-12 | 通用/其他压缩 |
| 66 | [2601.09059](https://arxiv.org/abs/2601.09059) | Efficient Multilingual Dialogue Processing via Translation Pipelines and Dist... | Santiago Martínez Novoa, Nicolás Rozo Fajardo 等 | 2026-01-14 | 知识蒸馏 (Distillation) |
| 67 | [2601.09165](https://arxiv.org/abs/2601.09165) | Multi-Teacher Ensemble Distillation: A Mathematical Framework for Probability... | Aaron R. Flouro, Shawn P. Chadwick | 2026-01-14 | 知识蒸馏 (Distillation) |
| 68 | [2601.09176](https://arxiv.org/abs/2601.09176) | $D^2Prune$: Sparsifying Large Language Models via Dual Taylor Expansion and A... | Lang Xiong, Ning Liu 等 | 2026-01-14 | 剪枝 (Pruning) |
| 69 | [2601.09191](https://arxiv.org/abs/2601.09191) | From Performance to Practice: Knowledge-Distilled Segmentator for On-Premises... | Qizhen Lan, Aaron Choi 等 | 2026-01-14 | 知识蒸馏 (Distillation) |
| 70 | [2601.09306](https://arxiv.org/abs/2601.09306) | On-Device Large Language Models for Sequential Recommendation | Xin Xia, Hongzhi Yin 等 | 2026-01-14 | 通用/其他压缩 |
| 71 | [2601.09352](https://arxiv.org/abs/2601.09352) | Spectral Complex Autoencoder Pruning: A Fidelity-Guided Criterion for Extreme... | Wei Liu, Xing Deng 等 | 2026-01-14 | 剪枝 (Pruning) |
| 72 | [2601.09451](https://arxiv.org/abs/2601.09451) | Late Breaking Results: Quamba-SE: Soft-edge Quantizer for Activations in Stat... | Yizhi Chen, Ahmed Hemani | 2026-01-14 | 量化 (Quantization) |
| 73 | [2601.09555](https://arxiv.org/abs/2601.09555) | Benchmarking Post-Training Quantization of Large Language Models under Micros... | Manyi Zhang, Ji-Fu Li 等 | 2026-01-14 | 量化 (Quantization) |
| 74 | [2601.09694](https://arxiv.org/abs/2601.09694) | LLMs can Compress LLMs: Adaptive Pruning by Agents | Sai Varun Kodathala, Rakesh Vunnam | 2026-01-14 | 剪枝 (Pruning) |
| 75 | [2601.09773](https://arxiv.org/abs/2601.09773) | Enhancing LUT-based Deep Neural Networks Inference through Architecture and C... | Binglei Lou, Ruilin Wu 等 | 2026-01-14 | 量化 (Quantization) |
| 76 | [2601.09865](https://arxiv.org/abs/2601.09865) | Advancing Model Refinement: Muon-Optimized Distillation and Quantization for ... | Jacob Sander, Brian Jalaian 等 | 2026-01-14 | 量化 (Quantization) |
| 77 | [2601.09881](https://arxiv.org/abs/2601.09881) | Transition Matching Distillation for Fast Video Generation | Weili Nie, Julius Berner 等 | 2026-01-14 | 知识蒸馏 (Distillation) |
| 78 | [2601.09985](https://arxiv.org/abs/2601.09985) | FaTRQ: Tiered Residual Quantization for LLM Vector Search in Far-Memory-Aware... | Tianqi Zhang, Flavio Ponzina 等 | 2026-01-15 | 量化 (Quantization) |
| 79 | [2601.10015](https://arxiv.org/abs/2601.10015) | CAFEDistill: Learning Personalized and Dynamic Models through Federated Early... | Boyi Liu, Zimu Zhou 等 | 2026-01-15 | 知识蒸馏 (Distillation) |
| 80 | [2601.10114](https://arxiv.org/abs/2601.10114) | Following the Teacher's Footsteps: Scheduled Checkpoint Distillation for Doma... | Cheng Feng, Chaoliang Zhong 等 | 2026-01-15 | 知识蒸馏 (Distillation) |
| 81 | [2601.10155](https://arxiv.org/abs/2601.10155) | LOOKAT: Lookup-Optimized Key-Attention for Memory-Efficient Transformers | Aryan Karmore | 2026-01-15 | KV Cache 压缩 |
| 82 | [2601.10321](https://arxiv.org/abs/2601.10321) | An Efficient Long-Context Ranking Architecture With Calibrated LLM Distillati... | Warren Jouanneau, Emma Jouffroy 等 | 2026-01-15 | 知识蒸馏 (Distillation) |
| 83 | [2601.10729](https://arxiv.org/abs/2601.10729) | OrbitFlow: SLO-Aware Long-Context LLM Serving with Fine-Grained KV Cache Reco... | Xinyue Ma, Heelim Hong 等 | 2026-01-05 | KV Cache 压缩 |
| 84 | [2601.10765](https://arxiv.org/abs/2601.10765) | Pruning as Evolution: Emergent Sparsity Through Selection Dynamics in Neural ... | Zubair Shah, Noaman Khan | 2026-01-14 | 剪枝 (Pruning) |
| 85 | [2601.10801](https://arxiv.org/abs/2601.10801) | Towards Tensor Network Models for Low-Latency Jet Tagging on FPGAs | Alberto Coppi, Ema Puljak 等 | 2026-01-15 | 通用/其他压缩 |
| 86 | [2601.10953](https://arxiv.org/abs/2601.10953) | SwiftKV: An Edge-Oriented Attention Algorithm and Multi-Head Accelerator for ... | Junming Zhang, Qinyan Zhang 等 | 2026-01-16 | KV Cache 压缩 |
| 87 | [2601.10987](https://arxiv.org/abs/2601.10987) | Reasoning Distillation for Lightweight Automated Program Repair | Aanand Balasubramanian, Sashank Silwal | 2026-01-16 | 知识蒸馏 (Distillation) |
| 88 | [2601.11200](https://arxiv.org/abs/2601.11200) | FAQ: Mitigating Quantization Error via Regenerating Calibration Data with Fam... | Haiyang Xiao, Weiqing Li 等 | 2026-01-16 | 量化 (Quantization) |
| 89 | [2601.11269](https://arxiv.org/abs/2601.11269) | X-Distill: Cross-Architecture Vision Distillation for Visuomotor Learning | Maanping Shao, Feihong Zhang 等 | 2026-01-16 | 知识蒸馏 (Distillation) |
| 90 | [2601.11471](https://arxiv.org/abs/2601.11471) | Low-Rank Key Value Attention | James O'Neill, Robert Clancy 等 | 2026-01-16 | KV Cache 压缩 |
| 91 | [2601.11630](https://arxiv.org/abs/2601.11630) | A one-step generation model with a Single-Layer Transformer: Layer number re-... | Haonan Wei, Linyuan Wang 等 | 2026-01-14 | 知识蒸馏 (Distillation) |
| 92 | [2601.11641](https://arxiv.org/abs/2601.11641) | Mixture of Distributions Matters: Dynamic Sparse Attention for Efficient Vide... | Yuxi Liu, Yipeng Hu 等 | 2026-01-14 | 稀疏化 (Sparsity) |
| 93 | [2601.11660](https://arxiv.org/abs/2601.11660) | Zeros can be Informative: Masked Binary U-Net for Image Segmentation on Tenso... | Chunshu Wu, Ruibing Song 等 | 2026-01-15 | 量化 (Quantization) |
| 94 | [2601.11663](https://arxiv.org/abs/2601.11663) | Activation Sensitivity as a Unifying Principle for Post-Training Quantization | Bruce Changlong Xu | 2026-01-15 | 量化 (Quantization) |
| 95 | [2601.11667](https://arxiv.org/abs/2601.11667) | Distill-then-Replace: Efficient Task-Specific Hybrid Attention Model Construc... | Xiaojie Xia, Huigang Zhang 等 | 2026-01-16 | 知识蒸馏 (Distillation) |
| 96 | [2601.11865](https://arxiv.org/abs/2601.11865) | CTPD: Cross Tokenizer Preference Distillation | Truong Nguyen, Phi Van Dat 等 | 2026-01-17 | 知识蒸馏 (Distillation) |
| 97 | [2601.12033](https://arxiv.org/abs/2601.12033) | Preserving Fairness and Safety in Quantized LLMs Through Critical Weight Prot... | Muhammad Alif Al Hakim, Alfan Farizki Wicaksono 等 | 2026-01-17 | 量化 (Quantization) |
| 98 | [2601.12042](https://arxiv.org/abs/2601.12042) | Less Is More -- Until It Breaks: Security Pitfalls of Vision Token Compressio... | Xiaomei Zhang, Zhaoxi Zhang 等 | 2026-01-17 | Token 压缩 |
| 99 | [2601.12272](https://arxiv.org/abs/2601.12272) | AgenticPruner: MAC-Constrained Neural Network Compression via LLM-Driven Stra... | Shahrzad Esmat, Mahdi Banisharif 等 | 2026-01-18 | 剪枝 (Pruning) |
| 100 | [2601.12638](https://arxiv.org/abs/2601.12638) | Mixed Precision PointPillars for Efficient 3D Object Detection with TensorRT | Ninnart Fuengfusin, Keisuke Yoneda 等 | 2026-01-19 | 混合精度/数值格式 |
| 101 | [2601.12785](https://arxiv.org/abs/2601.12785) | Distilling Time Series Foundation Models for Efficient Forecasting | Yuqi Li, Kuiye Ding 等 | 2026-01-19 | 知识蒸馏 (Distillation) |
| 102 | [2601.12814](https://arxiv.org/abs/2601.12814) | CSGaussian: Progressive Rate-Distortion Compression and Segmentation for 3D G... | Yu-Jen Tseng, Chia-Hao Kao 等 | 2026-01-19 | 通用/其他压缩 |
| 103 | [2601.12894](https://arxiv.org/abs/2601.12894) | Sparse ActionGen: Accelerating Diffusion Policy with Real-time Pruning | Kangye Ji, Jianbo Zhou 等 | 2026-01-19 | 剪枝 (Pruning) |
| 104 | [2601.12904](https://arxiv.org/abs/2601.12904) | From Prefix Cache to Fusion RAG Cache: Accelerating LLM Inference in Retrieva... | Jiahao Wang, Weiyu Xie 等 | 2026-01-19 | KV Cache 压缩 |
| 105 | [2601.13100](https://arxiv.org/abs/2601.13100) | Recursive Meta-Distillation: An Axiomatic Framework for Iterative Knowledge R... | Aaron R. Flouro, Shawn P. Chadwick | 2026-01-19 | 知识蒸馏 (Distillation) |
| 106 | [2601.13143](https://arxiv.org/abs/2601.13143) | FastAV: Efficient Token Pruning for Audio-Visual Large Language Model Inference | Chaeyoung Jung, Youngjoon Jang 等 | 2026-01-19 | 剪枝 (Pruning) |
| 107 | [2601.13155](https://arxiv.org/abs/2601.13155) | Probe and Skip: Self-Predictive Token Skipping for Efficient Long-Context LLM... | Zimeng Wu, Donghao Wang 等 | 2026-01-19 | 剪枝 (Pruning) |
| 108 | [2601.13563](https://arxiv.org/abs/2601.13563) | ButterflyMoE: Compression-Scalable Ternary Experts via Structured Butterfly O... | Aryan Karmore | 2026-01-20 | 量化 (Quantization) |
| 109 | [2601.13631](https://arxiv.org/abs/2601.13631) | ContiguousKV: Accelerating LLM Prefill with Granularity-Aligned KV Cache Mana... | Jing Zou, Shangyu Wu 等 | 2026-01-20 | KV Cache 压缩 |
| 110 | [2601.13684](https://arxiv.org/abs/2601.13684) | HeteroCache: A Dynamic Retrieval Approach to Heterogeneous KV Cache Compressi... | Zhiyuan Shi, Qibo Qiu 等 | 2026-01-20 | KV Cache 压缩 |
| 111 | [2601.13992](https://arxiv.org/abs/2601.13992) | "The Whole Is Greater Than the Sum of Its Parts": A Compatibility-Aware Multi... | Jin Cui, Jiaqi Guo 等 | 2026-01-20 | 知识蒸馏 (Distillation) |
| 112 | [2601.14032](https://arxiv.org/abs/2601.14032) | RM-Distiller: Exploiting Generative LLM for Reward Model Distillation | Hongli Zhou, Hui Huang 等 | 2026-01-20 | 知识蒸馏 (Distillation) |
| 113 | [2601.14051](https://arxiv.org/abs/2601.14051) | Kakugo: Distillation of Low-Resource Languages into Small Language Models | Peter Devine, Mardhiyah Sanni 等 | 2026-01-20 | 知识蒸馏 (Distillation) |
| 114 | [2601.14243](https://arxiv.org/abs/2601.14243) | Jet-RL: Enabling On-Policy FP8 Reinforcement Learning with Unified Training a... | Haocheng Xi, Charlie Ruan 等 | 2026-01-20 | 量化 (Quantization) |
| 115 | [2601.14277](https://arxiv.org/abs/2601.14277) | Which Quantization Should I Use? A Unified Evaluation of llama.cpp Quantizati... | Uygar Kurt | 2026-01-11 | 量化 (Quantization) |
| 116 | [2601.14279](https://arxiv.org/abs/2601.14279) | On the Limits of Learned Importance Scoring for KV Cache Compression | Brady Steele | 2026-01-13 | KV Cache 压缩 |
| 117 | [2601.14290](https://arxiv.org/abs/2601.14290) | Project Aletheia: Verifier-Guided Distillation of Backtracking for Small Lang... | Aradhya Dixit, Tianxi Liang 等 | 2026-01-14 | 知识蒸馏 (Distillation) |
| 118 | [2601.14549](https://arxiv.org/abs/2601.14549) | QMC: Efficient SLM Edge Inference via Outlier-Aware Quantization and Emergent... | Nilesh Prasad Pandey, Jangseon Park 等 | 2026-01-21 | 量化 (Quantization) |
| 119 | [2601.14699](https://arxiv.org/abs/2601.14699) | Triage knowledge distillation for speaker verification | Ju-ho Kim, Youngmoon Jung 等 | 2026-01-21 | 知识蒸馏 (Distillation) |
| 120 | [2601.14724](https://arxiv.org/abs/2601.14724) | HERMES: KV Cache as Hierarchical Memory for Efficient Streaming Video Underst... | Haowei Zhang, Shudong Yang 等 | 2026-01-21 | KV Cache 压缩 |
| 121 | [2601.14821](https://arxiv.org/abs/2601.14821) | POTR: Post-Training 3DGS Compression | Bert Ramlot, Martijn Courteaux 等 | 2026-01-21 | 通用/其他压缩 |
| 122 | [2601.14888](https://arxiv.org/abs/2601.14888) | What Makes Low-Bit Quantization-Aware Training Work for Reasoning LLMs? A Sys... | Keyu Lv, Manyi Zhang 等 | 2026-01-21 | 量化 (Quantization) |
| 123 | [2601.15079](https://arxiv.org/abs/2601.15079) | LoRAP: Low-Rank Aggregation Prompting for Quantized Graph Neural Networks Tra... | Chenyu Liu, Haige Li 等 | 2026-01-21 | 量化 (Quantization) |
| 124 | [2601.15287](https://arxiv.org/abs/2601.15287) | Towards Understanding Best Practices for Quantization of Vision-Language Models | Gautom Das, Vincent La 等 | 2026-01-21 | 量化 (Quantization) |
| 125 | [2601.15305](https://arxiv.org/abs/2601.15305) | Gated Sparse Attention: Combining Computational Efficiency with Training Stab... | Alfred Shen, Aaron Shen | 2026-01-12 | 稀疏化 (Sparsity) |
| 126 | [2601.15370](https://arxiv.org/abs/2601.15370) | Improving MoE Compute Efficiency by Composing Weight and Data Sparsity | Maciej Kilian, Oleg Mkrtchyan 等 | 2026-01-21 | 稀疏化 (Sparsity) |
| 127 | [2601.15394](https://arxiv.org/abs/2601.15394) | Memorization Dynamics in Knowledge Distillation for Language Models | Jaydeep Borkar, Karan Chadha 等 | 2026-01-21 | 知识蒸馏 (Distillation) |
| 128 | [2601.15538](https://arxiv.org/abs/2601.15538) | QUAIL: Quantization Aware Unlearning for Mitigating Misinformation in LLMs | Himanshu Mishra, Kanwal Mehreen | 2026-01-21 | 量化 (Quantization) |
| 129 | [2601.15598](https://arxiv.org/abs/2601.15598) | Ternary Spiking Neural Networks Enhanced by Complemented Neurons and Membrane... | Boxuan Zhang, Jiaxin Wang 等 | 2026-01-22 | 量化 (Quantization) |
| 130 | [2601.15657](https://arxiv.org/abs/2601.15657) | Integrating Knowledge Distillation Methods: A Sequential Multi-Stage Framework | Yinxi Tian, Changwu Huang 等 | 2026-01-22 | 知识蒸馏 (Distillation) |
| 131 | [2601.16073](https://arxiv.org/abs/2601.16073) | DSFedMed: Dual-Scale Federated Medical Image Segmentation via Mutual Distilla... | Hanwen Zhang, Qiaojin Shen 等 | 2026-01-22 | 知识蒸馏 (Distillation) |
| 132 | [2601.16093](https://arxiv.org/abs/2601.16093) | SAMTok: Representing Any Mask with Two Words | Yikang Zhou, Tao Zhang 等 | 2026-01-22 | Token 压缩 |
| 133 | [2601.16210](https://arxiv.org/abs/2601.16210) | PyraTok: Language-Aligned Pyramidal Tokenizer for Video Understanding and Gen... | Onkar Susladkar, Tushar Prakash 等 | 2026-01-22 | Token 压缩 |
| 134 | [2601.16219](https://arxiv.org/abs/2601.16219) | Domain Specific Specialization in Low-Resource Settings: The Efficacy of Offl... | Erdem Aslan, Pakize Erdoğmuş | 2026-01-05 | 知识蒸馏 (Distillation) |
| 135 | [2601.16235](https://arxiv.org/abs/2601.16235) | Contrastive Knowledge Distillation for Embedding Refinement in Personalized S... | Thomas Serre, Mathieu Fontaine 等 | 2026-01-21 | 知识蒸馏 (Distillation) |
| 136 | [2601.16366](https://arxiv.org/abs/2601.16366) | Post-Training Neural Network Pruning using Graph Curvature | Shuhang Tan, Jayson Sia 等 | 2026-01-22 | 剪枝 (Pruning) |
| 137 | [2601.16515](https://arxiv.org/abs/2601.16515) | SALAD: Achieve High-Sparsity Attention via Efficient Linear Attention Tuning ... | Tongcheng Fang, Hanling Zhang 等 | 2026-01-23 | 稀疏化 (Sparsity) |
| 138 | [2601.16536](https://arxiv.org/abs/2601.16536) | W4A16 Mixed-Precision Matrix Multiplication on Decoupled Architecture: Kernel... | Yuanhong He, Peiyu Niu 等 | 2026-01-23 | 混合精度/数值格式 |
| 139 | [2601.16547](https://arxiv.org/abs/2601.16547) | CORD: Bridging the Audio-Text Reasoning Gap via Weighted On-policy Cross-moda... | Jing Hu, Danxiang Zhu 等 | 2026-01-23 | 知识蒸馏 (Distillation) |
| 140 | [2601.16986](https://arxiv.org/abs/2601.16986) | Crystal-KV: Efficient KV Cache Management for Chain-of-Thought LLMs via Answe... | Zihan Wang, Cheng Tang 等 | 2026-01-05 | KV Cache 压缩 |
| 141 | [2601.16991](https://arxiv.org/abs/2601.16991) | Sparsity-Aware Low-Rank Representation for Efficient Fine-Tuning of Large Lan... | Longteng Zhang, Sen Wu 等 | 2026-01-08 | 稀疏化 (Sparsity) |
| 142 | [2601.17042](https://arxiv.org/abs/2601.17042) | Interpretable and Sparse Linear Attention with Decoupled Membership-Subspace ... | Tianyuan Liu, Libin Hou 等 | 2026-01-20 | 稀疏化 (Sparsity) |
| 143 | [2601.17112](https://arxiv.org/abs/2601.17112) | Low-Rank Tensor Approximation of Weights in Large Language Models via Cosine ... | A. El Ichi, K. Jbilou | 2026-01-23 | 通用/其他压缩 |
| 144 | [2601.17187](https://arxiv.org/abs/2601.17187) | High-Rate Quantized Matrix Multiplication I | Or Ordentlich, Yury Polyanskiy | 2026-01-23 | 量化 (Quantization) |
| 145 | [2601.17279](https://arxiv.org/abs/2601.17279) | SPADE: A SIMD Posit-enabled compute engine for Accelerating DNN Efficiency | Sonu Kumar, Lavanya Vinnakota 等 | 2026-01-24 | 混合精度/数值格式 |
| 146 | [2601.17357](https://arxiv.org/abs/2601.17357) | Spectral Geometry for Deep Learning: Compression and Hallucination Detection ... | Davide Ettori | 2026-01-24 | 知识蒸馏 (Distillation) |
| 147 | [2601.17367](https://arxiv.org/abs/2601.17367) | Elastic Attention: Test-time Adaptive Sparsity Ratios for Efficient Transformers | Zecheng Tang, Quantong Qiu 等 | 2026-01-24 | 稀疏化 (Sparsity) |
| 148 | [2601.17438](https://arxiv.org/abs/2601.17438) | UniGRec: Unified Generative Recommendation with Soft Identifiers for End-to-E... | Jialei Li, Yang Zhang 等 | 2026-01-24 | 量化 (Quantization) |
| 149 | [2601.17443](https://arxiv.org/abs/2601.17443) | Clustering-driven Memory Compression for On-device Large Language Models | Ondrej Bohdal, Pramit Saha 等 | 2026-01-24 | 通用/其他压缩 |
| 150 | [2601.17668](https://arxiv.org/abs/2601.17668) | Fast KVzip: Efficient and Accurate LLM Inference with Gated KV Eviction | Jang-Hyun Kim, Dongyoon Han 等 | 2026-01-25 | KV Cache 压缩 |
| 151 | [2601.17818](https://arxiv.org/abs/2601.17818) | ViTCoP: Accelerating Large Vision-Language Models via Visual and Textual Sema... | Wen Luo, Peng Chen 等 | 2026-01-25 | 剪枝 (Pruning) |
| 152 | [2601.17836](https://arxiv.org/abs/2601.17836) | Unleashing the Potential of Sparse Attention on Long-term Behaviors for CTR P... | Weijiang Lai, Beihong Jin 等 | 2026-01-25 | 稀疏化 (Sparsity) |
| 153 | [2601.17910](https://arxiv.org/abs/2601.17910) | Adaptive Weighting in Knowledge Distillation: An Axiomatic Framework for Mult... | Aaron R. Flouro, Shawn P. Chadwick | 2026-01-25 | 知识蒸馏 (Distillation) |
| 154 | [2601.17917](https://arxiv.org/abs/2601.17917) | Streaming-dLLM: Accelerating Diffusion LLMs via Suffix Pruning and Dynamic De... | Zhongyu Xiao, Zhiwei Hao 等 | 2026-01-25 | 剪枝 (Pruning) |
| 155 | [2601.17987](https://arxiv.org/abs/2601.17987) | Systematic Characterization of Minimal Deep Learning Architectures: A Unified... | Ziwei Zheng, Huizhi Liang 等 | 2026-01-25 | 量化 (Quantization) |
| 156 | [2601.18091](https://arxiv.org/abs/2601.18091) | From LLMs to LRMs: Rethinking Pruning for Reasoning-Centric Models | Longwei Ding, Anhao Zhao 等 | 2026-01-26 | 剪枝 (Pruning) |
| 157 | [2601.18150](https://arxiv.org/abs/2601.18150) | FP8-RL: A Practical and Stable Low-Precision Stack for LLM Reinforcement Lear... | Zhaopeng Qiu, Shuang Yu 等 | 2026-01-26 | 量化 (Quantization) |
| 158 | [2601.18306](https://arxiv.org/abs/2601.18306) | Calibrating Beyond English: Language Diversity for Better Quantized Multiling... | Everlyn Asiko Chimoto, Mostafa Elhoushi 等 | 2026-01-26 | 量化 (Quantization) |
| 159 | [2601.18527](https://arxiv.org/abs/2601.18527) | Exploring Fine-Tuning for In-Context Retrieval and Efficient KV-Caching in Lo... | Francesco Maria Molfese, Momchil Hardalov 等 | 2026-01-26 | KV Cache 压缩 |
| 160 | [2601.18570](https://arxiv.org/abs/2601.18570) | Feature-Indexed Federated Recommendation with Residual-Quantized Codebooks | Mingzhe Han, Jiahao Liu 等 | 2026-01-26 | 量化 (Quantization) |
| 161 | [2601.18909](https://arxiv.org/abs/2601.18909) | How Is Uncertainty Propagated in Knowledge Distillation? | Ziyao Cui, Jian Pei | 2026-01-26 | 知识蒸馏 (Distillation) |
| 162 | [2601.18999](https://arxiv.org/abs/2601.18999) | Randomization Boosts KV Caching, Learning Balances Query Load: A Joint Perspe... | Fangzhou Wu, Sandeep Silwal 等 | 2026-01-26 | KV Cache 压缩 |
| 163 | [2601.19026](https://arxiv.org/abs/2601.19026) | Is Finer Better? The Limits of Microscaling Formats in Large Language Models | Andrea Fasoli, Monodeep Kar 等 | 2026-01-26 | 量化 (Quantization) |
| 164 | [2601.19178](https://arxiv.org/abs/2601.19178) | CollectiveKV: Decoupling and Sharing Collaborative Information in Sequential ... | Jingyu Li, Zhaocheng Du 等 | 2026-01-27 | KV Cache 压缩 |
| 165 | [2601.19213](https://arxiv.org/abs/2601.19213) | M2XFP: A Metadata-Augmented Microscaling Data Format for Efficient Low-bit Qu... | Weiming Hu, Zihan Zhang 等 | 2026-01-27 | 量化 (Quantization) |
| 166 | [2601.19320](https://arxiv.org/abs/2601.19320) | StableQAT: Stable Quantization-Aware Training at Ultra-Low Bitwidths | Tianyi Chen, Sihan Chen 等 | 2026-01-27 | 量化 (Quantization) |
| 167 | [2601.19503](https://arxiv.org/abs/2601.19503) | GradPruner: Gradient-Guided Layer Pruning Enabling Efficient Fine-Tuning and ... | Wei Huang, Anda Cheng 等 | 2026-01-27 | 剪枝 (Pruning) |
| 168 | [2601.19675](https://arxiv.org/abs/2601.19675) | LoPRo: Enhancing Low-Rank Quantization via Permuted Block-Wise Rotation | Hongyaoxing Gu, Lijuan Hu 等 | 2026-01-27 | 量化 (Quantization) |
| 169 | [2601.19794](https://arxiv.org/abs/2601.19794) | Component-Aware Pruning Framework for Neural Network Controllers via Gradient... | Ganesh Sundaram, Jonas Ulmen 等 | 2026-01-27 | 剪枝 (Pruning) |
| 170 | [2601.19919](https://arxiv.org/abs/2601.19919) | ASKD-Whisper: Adaptive Self-knowledge Distillation for Efficient and Low-Late... | Junseok Lee, Nahun Kim 等 | 2026-01-08 | 知识蒸馏 (Distillation) |
| 171 | [2601.19920](https://arxiv.org/abs/2601.19920) | PiC-BNN: A 128-kbit 65 nm Processing-in-CAM-Based End-to-End Binary Neural Ne... | Yuval Harary, Almog Sharoni 等 | 2026-01-08 | 量化 (Quantization) |
| 172 | [2601.20088](https://arxiv.org/abs/2601.20088) | Quantization-Aware Distillation for NVFP4 Inference Accuracy Recovery | Meng Xin, Sweta Priyadarshi 等 | 2026-01-27 | 量化 (Quantization) |
| 173 | [2601.20107](https://arxiv.org/abs/2601.20107) | Structural Anchor Pruning: Training-Free Multi-Vector Compression for Visual ... | Zhuchenyang Liu, Ziyu Hu 等 | 2026-01-27 | 剪枝 (Pruning) |
| 174 | [2601.20168](https://arxiv.org/abs/2601.20168) | Efficient Token Pruning for LLaDA-V | Zhewen Wan, Tianchen Song 等 | 2026-01-28 | 剪枝 (Pruning) |
| 175 | [2601.20262](https://arxiv.org/abs/2601.20262) | Shallow-π: Knowledge Distillation for Flow-based VLAs | Boseong Jeon, Yunho Choi 等 | 2026-01-28 | 知识蒸馏 (Distillation) |
| 176 | [2601.20267](https://arxiv.org/abs/2601.20267) | SATA: Sparsity-Aware Scheduling for Selective Token Attention | Zhenkun Fan, Zishen Wan 等 | 2026-01-28 | 稀疏化 (Sparsity) |
| 177 | [2601.20301](https://arxiv.org/abs/2601.20301) | Towards Compact and Robust DNNs via Compression-aware Sharpness Minimization | Jialuo He, Huangxun Chen | 2026-01-28 | 通用/其他压缩 |
| 178 | [2601.20317](https://arxiv.org/abs/2601.20317) | VersaQ-3D: Architecture Support for Visual Geometry Grounded Transformers via... | Yipu Zhang, Jintao Cheng 等 | 2026-01-28 | 量化 (Quantization) |
| 179 | [2601.20326](https://arxiv.org/abs/2601.20326) | Beyond Speedup -- Utilizing KV Cache for Sampling and Reasoning | Zeyu Xing, Xing Li 等 | 2026-01-28 | KV Cache 压缩 |
| 180 | [2601.20499](https://arxiv.org/abs/2601.20499) | Efficient Autoregressive Video Diffusion with Dummy Head | Hang Guo, Zhaoyang Jia 等 | 2026-01-28 | KV Cache 压缩 |
| 181 | [2601.20745](https://arxiv.org/abs/2601.20745) | HESTIA: A Hessian-Guided Differentiable Quantization-Aware Training Framework... | Guoan Wang, Feiyu Wang 等 | 2026-01-28 | 量化 (Quantization) |
| 182 | [2601.21069](https://arxiv.org/abs/2601.21069) | CompSRT: Quantization and Pruning for Image Super Resolution Transformers | Dorsa Zeinali, Hailing Wang 等 | 2026-01-28 | 量化 (Quantization) |
| 183 | [2601.21193](https://arxiv.org/abs/2601.21193) | Generative Recall, Dense Reranking: Learning Multi-View Semantic IDs for Effi... | Zecheng Zhao, Zhi Chen 等 | 2026-01-29 | 量化 (Quantization) |
| 184 | [2601.21198](https://arxiv.org/abs/2601.21198) | ZipMoE: Efficient On-Device MoE Serving via Lossless Compression and Cache-Af... | Yuchen Yang, Yaru Zhao 等 | 2026-01-29 | 通用/其他压缩 |
| 185 | [2601.21219](https://arxiv.org/abs/2601.21219) | Soft Quantization: Model Compression Via Weight Coupling | Daniel T. Bernstein, Luca Di Carlo 等 | 2026-01-29 | 量化 (Quantization) |
| 186 | [2601.21238](https://arxiv.org/abs/2601.21238) | PTQ4ARVG: Post-Training Quantization for AutoRegressive Visual Generation Models | Xuewen Liu, Zhikai Li 等 | 2026-01-29 | 量化 (Quantization) |
| 187 | [2601.21279](https://arxiv.org/abs/2601.21279) | NEXUS: Bit-Exact ANN-to-SNN Equivalence via Neuromorphic Gate Circuits with S... | Zhengzheng Tang | 2026-01-29 | 量化 (Quantization) |
| 188 | [2601.21288](https://arxiv.org/abs/2601.21288) | Drive-KD: Multi-Teacher Distillation for VLMs in Autonomous Driving | Weitong Lian, Zecong Tang 等 | 2026-01-29 | 知识蒸馏 (Distillation) |
| 189 | [2601.21345](https://arxiv.org/abs/2601.21345) | Semantic-Guided Dynamic Sparsification for Pre-Trained Model-based Class-Incr... | Ruiqi Liu, Boyu Diao 等 | 2026-01-29 | 稀疏化 (Sparsity) |
| 190 | [2601.21420](https://arxiv.org/abs/2601.21420) | ConceptMoE: Adaptive Token-to-Concept Compression for Implicit Compute Alloca... | Zihao Huang, Jundong Zhou 等 | 2026-01-29 | 通用/其他压缩 |
| 191 | [2601.21531](https://arxiv.org/abs/2601.21531) | On the Adversarial Robustness of Large Vision-Language Models under Visual To... | Xinwei Zhang, Hangcheng Liu 等 | 2026-01-29 | Token 压缩 |
| 192 | [2601.21611](https://arxiv.org/abs/2601.21611) | Thinking Broad, Acting Fast: Latent Reasoning Distillation from Multi-Perspec... | Baopu Qiu, Hao Chen 等 | 2026-01-29 | 知识蒸馏 (Distillation) |
| 193 | [2601.21623](https://arxiv.org/abs/2601.21623) | LAMP: Look-Ahead Mixed-Precision Inference of Large Language Models | Stanislav Budzinskiy, Marian Gloser 等 | 2026-01-29 | 混合精度/数值格式 |
| 194 | [2601.21626](https://arxiv.org/abs/2601.21626) | HeRo-Q: A General Framework for Stable Low Bit Quantization via Hessian Condi... | Jinhao Zhang, Yunquan Zhang 等 | 2026-01-29 | 量化 (Quantization) |
| 195 | [2601.21686](https://arxiv.org/abs/2601.21686) | Don't be so Stief! Learning KV Cache low-rank approximation over the Stiefel ... | Luca Benfenati, Matteo Risso 等 | 2026-01-29 | KV Cache 压缩 |
| 196 | [2601.21737](https://arxiv.org/abs/2601.21737) | Mixed-Precision Training and Compilation for RRAM-based Computing-in-Memory A... | Rebecca Pelke, Joel Klein 等 | 2026-01-29 | 混合精度/数值格式 |
| 197 | [2601.21896](https://arxiv.org/abs/2601.21896) | Past- and Future-Informed KV Cache Policy with Salience Estimation in Autoreg... | Hanmo Chen, Chenghao Xu 等 | 2026-01-29 | KV Cache 压缩 |
| 198 | [2601.21927](https://arxiv.org/abs/2601.21927) | SONIC: Segmented Optimized Nexus for Information Compression in Key-Value Cac... | Hong Chen, Xiang Liu 等 | 2026-01-29 | KV Cache 压缩 |
| 199 | [2601.21968](https://arxiv.org/abs/2601.21968) | OVD: On-policy Verbal Distillation | Jing Xiong, Hui Shen 等 | 2026-01-29 | 知识蒸馏 (Distillation) |
| 200 | [2601.22069](https://arxiv.org/abs/2601.22069) | VTC-R1: Vision-Text Compression for Efficient Long-Context Reasoning | Yibo Wang, Yongcheng Jing 等 | 2026-01-29 | Token 压缩 |
| 201 | [2601.22101](https://arxiv.org/abs/2601.22101) | ECO: Quantized Training without Full-Precision Master Weights | Mahdi Nikdan, Amir Zandieh 等 | 2026-01-29 | 量化 (Quantization) |
| 202 | [2601.22141](https://arxiv.org/abs/2601.22141) | Routing the Lottery: Adaptive Subnetworks for Heterogeneous Data | Grzegorz Stefanski, Alberto Presta 等 | 2026-01-29 | 剪枝 (Pruning) |
| 203 | [2601.22244](https://arxiv.org/abs/2601.22244) | Is Hierarchical Quantization Essential for Optimal Reconstruction? | Shirin Reyhanian, Laurenz Wiskott | 2026-01-29 | 量化 (Quantization) |
| 204 | [2601.22275](https://arxiv.org/abs/2601.22275) | VMonarch: Efficient Video Diffusion Transformers with Structured Attention | Cheng Liang, Haoxian Chen 等 | 2026-01-29 | 稀疏化 (Sparsity) |
| 205 | [2601.22347](https://arxiv.org/abs/2601.22347) | Pushing the Limits of Block Rotations in Post-Training Quantization | Sai Sanjeet, Ian Colbert 等 | 2026-01-29 | 量化 (Quantization) |
| 206 | [2601.22362](https://arxiv.org/abs/2601.22362) | Understanding Efficiency: Quantization, Batching, and Serving Strategies in L... | Julien Delavande, Regis Pierrard 等 | 2026-01-29 | 量化 (Quantization) |
| 207 | [2601.22379](https://arxiv.org/abs/2601.22379) | SPLA: Block Sparse Plus Linear Attention for Long Context Modeling | Bailin Wang, Dan Friedman 等 | 2026-01-29 | 稀疏化 (Sparsity) |
| 208 | [2601.22475](https://arxiv.org/abs/2601.22475) | Continual Policy Distillation from Distributed Reinforcement Learning Teachers | Yuxuan Li, Qijun He 等 | 2026-01-30 | 知识蒸馏 (Distillation) |
| 209 | [2601.22488](https://arxiv.org/abs/2601.22488) | Elastic Spectral State Space Models for Budgeted Inference | Dachuan Song, Xuan Wang | 2026-01-30 | 通用/其他压缩 |
| 210 | [2601.22531](https://arxiv.org/abs/2601.22531) | Learn from A Rationalist: Distilling Intermediate Interpretable Rationales | Jiayi Dai, Randy Goebel | 2026-01-30 | 知识蒸馏 (Distillation) |
| 211 | [2601.22594](https://arxiv.org/abs/2601.22594) | Language Model Circuits Are Sparse in the Neuron Basis | Aryaman Arora, Zhengxuan Wu 等 | 2026-01-30 | 稀疏化 (Sparsity) |
| 212 | [2601.22632](https://arxiv.org/abs/2601.22632) | DART-ing Through the Drift: Dynamic Tracing of Knowledge Neurons for Adaptive... | Abhishek Tyagi, Yunuo Cen 等 | 2026-01-30 | 剪枝 (Pruning) |
| 213 | [2601.22660](https://arxiv.org/abs/2601.22660) | Layerwise Progressive Freezing Enables STE-Free Training of Deep Binary Neura... | Evan Gibson Smith, Bashima Islam | 2026-01-30 | 量化 (Quantization) |
| 214 | [2601.22674](https://arxiv.org/abs/2601.22674) | VisionTrim: Unified Vision Token Compression for Training-Free MLLM Acceleration | Hanxun Yu, Wentong Li 等 | 2026-01-30 | Token 压缩 |
| 215 | [2601.22709](https://arxiv.org/abs/2601.22709) | Gated Relational Alignment via Confidence-based Distillation for Efficient VLMs | Yanlong Chen, Amirhossein Habibian 等 | 2026-01-30 | 知识蒸馏 (Distillation) |
| 216 | [2601.22716](https://arxiv.org/abs/2601.22716) | Breaking the Blocks: Continuous Low-Rank Decomposed Scaling for Unified LLM Q... | Pingzhi Tang, Ruijie Zhou 等 | 2026-01-30 | 量化 (Quantization) |
| 217 | [2601.22766](https://arxiv.org/abs/2601.22766) | Sparse Attention as Compact Kernel Regression | Saul Santos, Nuno Gonçalves 等 | 2026-01-30 | 稀疏化 (Sparsity) |
| 218 | [2601.22787](https://arxiv.org/abs/2601.22787) | Float8@2bits: Entropy Coding Enables Data-Free Model Compression | Patrick Putzky, Martin Genzel 等 | 2026-01-30 | 量化 (Quantization) |
| 219 | [2601.22795](https://arxiv.org/abs/2601.22795) | Sparse or Dense? A Mechanistic Estimation of Computation Density in Transform... | Corentin Kervadec, Iuliia Lysova 等 | 2026-01-30 | 稀疏化 (Sparsity) |
| 220 | [2601.22813](https://arxiv.org/abs/2601.22813) | Quartet II: Accurate LLM Pre-Training in NVFP4 by Improved Unbiased Gradient ... | Andrei Panferov, Erik Schultheis 等 | 2026-01-30 | 量化 (Quantization) |
| 221 | [2601.22841](https://arxiv.org/abs/2601.22841) | How Much of a Model Do We Need? Redundancy and Slimmability in Remote Sensing... | Leonard Hackel, Tom Burgert 等 | 2026-01-30 | 剪枝 (Pruning) |
| 222 | [2601.22876](https://arxiv.org/abs/2601.22876) | Matterhorn: Efficient Analog Sparse Spiking Transformer Architecture with Mas... | Zhanglu Yan, Kaiwen Tang 等 | 2026-01-30 | 稀疏化 (Sparsity) |
| 223 | [2601.22980](https://arxiv.org/abs/2601.22980) | Learnable Permutation for Structured Sparsity on Transformer Models | Zekai Li, Ji Liu 等 | 2026-01-30 | 剪枝 (Pruning) |
| 224 | [2601.22996](https://arxiv.org/abs/2601.22996) | Competitive Non-Clairvoyant KV-Cache Scheduling for LLM Inference | Yiding Feng, Zonghan Yang 等 | 2026-01-30 | KV Cache 压缩 |
| 225 | [2601.23148](https://arxiv.org/abs/2601.23148) | Compressed BC-LISTA via Low-Rank Convolutional Decomposition | Han Wang, Yhonatan Kvich 等 | 2026-01-30 | 通用/其他压缩 |
| 226 | [2602.00165](https://arxiv.org/abs/2602.00165) | Benford's Law as a Distributional Prior for Post-Training Quantization of Lar... | Arthur Negrão, Pedro Silva 等 | 2026-01-29 | 量化 (Quantization) |
| 227 | [2602.00247](https://arxiv.org/abs/2602.00247) | CAPA: Contribution-Aware Pruning and FFN Approximation for Efficient Large Vi... | Samyak Jha, Junho Kim | 2026-01-30 | 剪枝 (Pruning) |
| 228 | [2602.00268](https://arxiv.org/abs/2602.00268) | TokenTrim: Inference-Time Token Pruning for Autoregressive Long Video Generation | Ariel Shaulov, Eitan Shaar 等 | 2026-01-30 | Token 压缩 |
| 229 | [2602.00372](https://arxiv.org/abs/2602.00372) | Post-Training Probability Manifold Correction via Structured SVD Pruning and ... | Aaron R. Flouro, Shawn P. Chadwick | 2026-01-30 | 剪枝 (Pruning) |
| 230 | [2602.00397](https://arxiv.org/abs/2602.00397) | Fast Forward: Accelerating LLM Prefill with Predictive FFN Sparsity | Aayush Gautam, Mukul Gagrani 等 | 2026-01-30 | 稀疏化 (Sparsity) |
| 231 | [2602.00450](https://arxiv.org/abs/2602.00450) | Model Optimization for Multi-Camera 3D Detection and Tracking | Ethan Anderson, Justin Silva 等 | 2026-01-31 | 量化 (Quantization) |
| 232 | [2602.00534](https://arxiv.org/abs/2602.00534) | AIRE-Prune: Asymptotic Impulse-Response Energy for State Pruning in State Spa... | Apurba Prasad Padhy, Fernando Camacho 等 | 2026-01-31 | 剪枝 (Pruning) |
| 233 | [2602.00686](https://arxiv.org/abs/2602.00686) | Learning to Accelerate Vision-Language-Action Models through Adaptive Visual ... | Yujie Wei, Jiahan Fan 等 | 2026-01-31 | Token 压缩 |
| 234 | [2602.00777](https://arxiv.org/abs/2602.00777) | HyLRA: Hybrid Layer Reuse Attention for Efficient Long-Context Inference | Xuan Ai, Qingqing Yang 等 | 2026-01-31 | 通用/其他压缩 |
| 235 | [2602.00780](https://arxiv.org/abs/2602.00780) | Environment-Aware Adaptive Pruning with Interleaved Inference Orchestration f... | Yuting Huang, Leilei Ding 等 | 2026-01-31 | 剪枝 (Pruning) |
| 236 | [2602.00838](https://arxiv.org/abs/2602.00838) | Exploration of Unary Arithmetic-Based Matrix Multiply Units for Low Precision... | Prabhu Vellaisamy, Harideep Nair 等 | 2026-01-31 | 混合精度/数值格式 |
| 237 | [2602.00852](https://arxiv.org/abs/2602.00852) | Investigating the Robustness of Subtask Distillation under Spurious Correlation | Pattarawat Chormai, Klaus-Robert Müller 等 | 2026-01-31 | 知识蒸馏 (Distillation) |
| 238 | [2602.00879](https://arxiv.org/abs/2602.00879) | Dynamic Expert Sharing: Decoupling Memory from Parallelism in Mixture-of-Expe... | Hao Mark Chen, Zhiwen Mo 等 | 2026-01-31 | 稀疏化 (Sparsity) |
| 239 | [2602.02538](https://arxiv.org/abs/2602.02538) | Enhancing Post-Training Quantization via Future Activation Awareness | Zheqi Lv, Zhenxuan Fan 等 | 2026-01-28 | 量化 (Quantization) |
| 240 | [2602.02579](https://arxiv.org/abs/2602.02579) | ProphetKV: User-Query-Driven Selective Recomputation for Efficient KV Cache R... | Shihao Wang, Jiahao Chen 等 | 2026-01-31 | KV Cache 压缩 |
| 241 | [2602.02581](https://arxiv.org/abs/2602.02581) | QuantLRM: Quantization of Large Reasoning Models via Fine-Tuning Signals | Nan Zhang, Eugene Kwek 等 | 2026-01-31 | 量化 (Quantization) |
| 242 | [2602.11184](https://arxiv.org/abs/2602.11184) | KBVQ-MoE: KLT-guided SVD with Bias-Corrected Vector Quantization for MoE Larg... | Zukang Xu, Zhixiong Zhao 等 | 2026-01-30 | 量化 (Quantization) |
| 243 | [2602.15836](https://arxiv.org/abs/2602.15836) | EdgeNav-QE: QLoRA Quantization and Dynamic Early Exit for LAM-based Navigatio... | Mengyun Liu, Shanshan Huang 等 | 2026-01-12 | 量化 (Quantization) |
| 244 | [2602.15845](https://arxiv.org/abs/2602.15845) | KD4MT: A Survey of Knowledge Distillation for Machine Translation | Ona de Gibert, Joseph Attieh 等 | 2026-01-22 | 知识蒸馏 (Distillation) |
| 245 | [2602.20164](https://arxiv.org/abs/2602.20164) | Benchmarking Distilled Language Models: Performance and Efficiency in Resourc... | Sachin Gopal Wani, Eric Page 等 | 2026-01-28 | 知识蒸馏 (Distillation) |
| 246 | [2603.08713](https://arxiv.org/abs/2603.08713) | Unveiling the Potential of Quantization with MXFP4: Strategies for Quantizati... | Jatin Chhugani, Geonhwa Jeong 等 | 2026-01-30 | 量化 (Quantization) |

## 三、分类论文清单

### 量化 (Quantization)（74 篇）

- [2601.00222](https://arxiv.org/abs/2601.00222) LooC: Effective Low-Dimensional Codebook for Compositional Vector Quantization
- [2601.00282](https://arxiv.org/abs/2601.00282) Can Large Language Models Still Explain Themselves? Investigating the Impact of Quantization on Self-Explanations
- [2601.00434](https://arxiv.org/abs/2601.00434) Time--to--Digital Converter (TDC)--Based Resonant Compute--in--Memory for INT8 CNNs with Layer--Optimized SRAM Mapping
- [2601.00679](https://arxiv.org/abs/2601.00679) QSLM: A Performance- and Memory-aware Quantization Framework with Tiered Search Strategy for Spike-driven Language Models
- [2601.02213](https://arxiv.org/abs/2601.02213) Quantized SO(3)-Equivariant Graph Neural Networks for Efficient Molecular Property Prediction
- [2601.02298](https://arxiv.org/abs/2601.02298) Power-of-Two Quantization-Aware-Training (PoT-QAT) in Large Language Models (LLMs)
- [2601.02455](https://arxiv.org/abs/2601.02455) Diagnostic-Driven Layer-Wise Compensation for Post-Training Quantization of Encoder-Decoder ASR Models
- [2601.02563](https://arxiv.org/abs/2601.02563) Compressed code: the hidden effects of quantization and distillation on programming tokens
- [2601.02680](https://arxiv.org/abs/2601.02680) Adversarial Contrastive Learning for LLM Quantization Attacks
- [2601.02888](https://arxiv.org/abs/2601.02888) RPIQ: Residual-Projected Multi-Collaboration Closed-Loop and Single Instance Quantization for Visually Impaired Assistance
- [2601.03332](https://arxiv.org/abs/2601.03332) LUT-KAN: Segment-wise LUT Quantization for Fast KAN Inference
- [2601.03484](https://arxiv.org/abs/2601.03484) From Bits to Chips: An LLM-based Hardware-Aware Quantization Agent for Streamlined Deployment of LLMs
- [2601.04719](https://arxiv.org/abs/2601.04719) GPU-Accelerated INT8 Quantization for KV Cache Compression in Large Language Models
- [2601.05684](https://arxiv.org/abs/2601.05684) FLRQ: Faster LLM Quantization with Flexible Low-Rank Matrix Sketching
- [2601.06959](https://arxiv.org/abs/2601.06959) HAS-VQ: Hessian-Adaptive Sparse Vector Quantization for High-Fidelity LLM Compression
- [2601.07048](https://arxiv.org/abs/2601.07048) GPU-Accelerated ANNS: Quantized for Speed, Built for Change
- [2601.07475](https://arxiv.org/abs/2601.07475) ARCQuant: Boosting NVFP4 Quantization with Augmented Residual Channels for LLMs
- [2601.07878](https://arxiv.org/abs/2601.07878) Sliced-Wasserstein Distribution Alignment Loss Improves the Ultra-Low-Bit Quantization of Large Language Models
- [2601.07892](https://arxiv.org/abs/2601.07892) Sherry: Hardware-Efficient 1.25-Bit Ternary Quantization via Fine-grained Sparsification
- [2601.08089](https://arxiv.org/abs/2601.08089) Q-realign: Piggybacking Realignment on Quantization for Safe and Efficient LLM Deployment
- [2601.08764](https://arxiv.org/abs/2601.08764) FusID: Modality-Fused Semantic IDs for Generative Music Recommendation
- [2601.09451](https://arxiv.org/abs/2601.09451) Late Breaking Results: Quamba-SE: Soft-edge Quantizer for Activations in State Space Models
- [2601.09555](https://arxiv.org/abs/2601.09555) Benchmarking Post-Training Quantization of Large Language Models under Microscaling Floating Point Formats
- [2601.09773](https://arxiv.org/abs/2601.09773) Enhancing LUT-based Deep Neural Networks Inference through Architecture and Connectivity Optimization
- [2601.09865](https://arxiv.org/abs/2601.09865) Advancing Model Refinement: Muon-Optimized Distillation and Quantization for LLM Deployment
- [2601.09985](https://arxiv.org/abs/2601.09985) FaTRQ: Tiered Residual Quantization for LLM Vector Search in Far-Memory-Aware ANNS Systems
- [2601.11200](https://arxiv.org/abs/2601.11200) FAQ: Mitigating Quantization Error via Regenerating Calibration Data with Family-Aware Quantization
- [2601.11660](https://arxiv.org/abs/2601.11660) Zeros can be Informative: Masked Binary U-Net for Image Segmentation on Tensor Cores
- [2601.11663](https://arxiv.org/abs/2601.11663) Activation Sensitivity as a Unifying Principle for Post-Training Quantization
- [2601.12033](https://arxiv.org/abs/2601.12033) Preserving Fairness and Safety in Quantized LLMs Through Critical Weight Protection
- [2601.13563](https://arxiv.org/abs/2601.13563) ButterflyMoE: Compression-Scalable Ternary Experts via Structured Butterfly Orbits
- [2601.14243](https://arxiv.org/abs/2601.14243) Jet-RL: Enabling On-Policy FP8 Reinforcement Learning with Unified Training and Rollout Precision Flow
- [2601.14277](https://arxiv.org/abs/2601.14277) Which Quantization Should I Use? A Unified Evaluation of llama.cpp Quantization on Llama-3.1-8B-Instruct
- [2601.14549](https://arxiv.org/abs/2601.14549) QMC: Efficient SLM Edge Inference via Outlier-Aware Quantization and Emergent Memories Co-Design
- [2601.14888](https://arxiv.org/abs/2601.14888) What Makes Low-Bit Quantization-Aware Training Work for Reasoning LLMs? A Systematic Study
- [2601.15079](https://arxiv.org/abs/2601.15079) LoRAP: Low-Rank Aggregation Prompting for Quantized Graph Neural Networks Training
- [2601.15287](https://arxiv.org/abs/2601.15287) Towards Understanding Best Practices for Quantization of Vision-Language Models
- [2601.15538](https://arxiv.org/abs/2601.15538) QUAIL: Quantization Aware Unlearning for Mitigating Misinformation in LLMs
- [2601.15598](https://arxiv.org/abs/2601.15598) Ternary Spiking Neural Networks Enhanced by Complemented Neurons and Membrane Potential Aggregation
- [2601.17187](https://arxiv.org/abs/2601.17187) High-Rate Quantized Matrix Multiplication I
- [2601.17438](https://arxiv.org/abs/2601.17438) UniGRec: Unified Generative Recommendation with Soft Identifiers for End-to-End Optimization
- [2601.17987](https://arxiv.org/abs/2601.17987) Systematic Characterization of Minimal Deep Learning Architectures: A Unified Analysis of Convergence, Pruning, and Quantization
- [2601.18150](https://arxiv.org/abs/2601.18150) FP8-RL: A Practical and Stable Low-Precision Stack for LLM Reinforcement Learning
- [2601.18306](https://arxiv.org/abs/2601.18306) Calibrating Beyond English: Language Diversity for Better Quantized Multilingual LLM
- [2601.18570](https://arxiv.org/abs/2601.18570) Feature-Indexed Federated Recommendation with Residual-Quantized Codebooks
- [2601.19026](https://arxiv.org/abs/2601.19026) Is Finer Better? The Limits of Microscaling Formats in Large Language Models
- [2601.19213](https://arxiv.org/abs/2601.19213) M2XFP: A Metadata-Augmented Microscaling Data Format for Efficient Low-bit Quantization
- [2601.19320](https://arxiv.org/abs/2601.19320) StableQAT: Stable Quantization-Aware Training at Ultra-Low Bitwidths
- [2601.19675](https://arxiv.org/abs/2601.19675) LoPRo: Enhancing Low-Rank Quantization via Permuted Block-Wise Rotation
- [2601.19920](https://arxiv.org/abs/2601.19920) PiC-BNN: A 128-kbit 65 nm Processing-in-CAM-Based End-to-End Binary Neural Network Accelerator
- [2601.20088](https://arxiv.org/abs/2601.20088) Quantization-Aware Distillation for NVFP4 Inference Accuracy Recovery
- [2601.20317](https://arxiv.org/abs/2601.20317) VersaQ-3D: Architecture Support for Visual Geometry Grounded Transformers via Versatile Quantization
- [2601.20745](https://arxiv.org/abs/2601.20745) HESTIA: A Hessian-Guided Differentiable Quantization-Aware Training Framework for Extremely Low-Bit LLMs
- [2601.21069](https://arxiv.org/abs/2601.21069) CompSRT: Quantization and Pruning for Image Super Resolution Transformers
- [2601.21193](https://arxiv.org/abs/2601.21193) Generative Recall, Dense Reranking: Learning Multi-View Semantic IDs for Efficient Text-to-Video Retrieval
- [2601.21219](https://arxiv.org/abs/2601.21219) Soft Quantization: Model Compression Via Weight Coupling
- [2601.21238](https://arxiv.org/abs/2601.21238) PTQ4ARVG: Post-Training Quantization for AutoRegressive Visual Generation Models
- [2601.21279](https://arxiv.org/abs/2601.21279) NEXUS: Bit-Exact ANN-to-SNN Equivalence via Neuromorphic Gate Circuits with Surrogate-Free Training
- [2601.21626](https://arxiv.org/abs/2601.21626) HeRo-Q: A General Framework for Stable Low Bit Quantization via Hessian Conditioning
- [2601.22101](https://arxiv.org/abs/2601.22101) ECO: Quantized Training without Full-Precision Master Weights
- [2601.22244](https://arxiv.org/abs/2601.22244) Is Hierarchical Quantization Essential for Optimal Reconstruction?
- [2601.22347](https://arxiv.org/abs/2601.22347) Pushing the Limits of Block Rotations in Post-Training Quantization
- [2601.22362](https://arxiv.org/abs/2601.22362) Understanding Efficiency: Quantization, Batching, and Serving Strategies in LLM Energy Use
- [2601.22660](https://arxiv.org/abs/2601.22660) Layerwise Progressive Freezing Enables STE-Free Training of Deep Binary Neural Networks
- [2601.22716](https://arxiv.org/abs/2601.22716) Breaking the Blocks: Continuous Low-Rank Decomposed Scaling for Unified LLM Quantization and Adaptation
- [2601.22787](https://arxiv.org/abs/2601.22787) Float8@2bits: Entropy Coding Enables Data-Free Model Compression
- [2601.22813](https://arxiv.org/abs/2601.22813) Quartet II: Accurate LLM Pre-Training in NVFP4 by Improved Unbiased Gradient Estimation
- [2602.00165](https://arxiv.org/abs/2602.00165) Benford's Law as a Distributional Prior for Post-Training Quantization of Large Language Models
- [2602.00450](https://arxiv.org/abs/2602.00450) Model Optimization for Multi-Camera 3D Detection and Tracking
- [2602.02538](https://arxiv.org/abs/2602.02538) Enhancing Post-Training Quantization via Future Activation Awareness
- [2602.02581](https://arxiv.org/abs/2602.02581) QuantLRM: Quantization of Large Reasoning Models via Fine-Tuning Signals
- [2602.11184](https://arxiv.org/abs/2602.11184) KBVQ-MoE: KLT-guided SVD with Bias-Corrected Vector Quantization for MoE Large Language Models
- [2602.15836](https://arxiv.org/abs/2602.15836) EdgeNav-QE: QLoRA Quantization and Dynamic Early Exit for LAM-based Navigation on Edge Devices
- [2603.08713](https://arxiv.org/abs/2603.08713) Unveiling the Potential of Quantization with MXFP4: Strategies for Quantization Error Reduction

### 知识蒸馏 (Distillation)（53 篇）

- [2601.00202](https://arxiv.org/abs/2601.00202) Knowledge Distillation for Temporal Knowledge Graph Reasoning with Large Language Models
- [2601.00359](https://arxiv.org/abs/2601.00359) Efficient Prediction of Dense Visual Embeddings via Distillation and RGB-D Transformers
- [2601.00714](https://arxiv.org/abs/2601.00714) KDPhys: An Attention Guided 3D to 2D Knowledge Distillation for Real-time Video-Based Physiological Measurement
- [2601.00926](https://arxiv.org/abs/2601.00926) MACA: A Framework for Distilling Trustworthy LLMs into Efficient Retrievers
- [2601.04264](https://arxiv.org/abs/2601.04264) MemKD: Memory-Discrepancy Knowledge Distillation for Efficient Time Series Classification
- [2601.05388](https://arxiv.org/abs/2601.05388) Knowledge Distillation of a Protein Language Model Yields a Foundational Implicit Solvent Model
- [2601.05639](https://arxiv.org/abs/2601.05639) Efficient training for compact compression models via sequential distillation
- [2601.05913](https://arxiv.org/abs/2601.05913) Distilling Lightweight Domain Experts from Large ML Models by Identifying Relevant Subspaces
- [2601.06227](https://arxiv.org/abs/2601.06227) When Smaller Wins: Dual-Stage Distillation and Pareto-Guided Compression of Liquid Neural Networks for Edge Battery Prognostics
- [2601.07568](https://arxiv.org/abs/2601.07568) d3LLM: Ultra-Fast Diffusion LLM using Pseudo-Trajectory Distillation
- [2601.08033](https://arxiv.org/abs/2601.08033) InfGraND: An Influence-Guided GNN-to-MLP Knowledge Distillation
- [2601.08169](https://arxiv.org/abs/2601.08169) Relational Knowledge Distillation Using Fine-tuned Function Vectors
- [2601.08301](https://arxiv.org/abs/2601.08301) ReCo-KD: Region- and Context-Aware Knowledge Distillation for Efficient 3D Medical Image Segmentation
- [2601.08412](https://arxiv.org/abs/2601.08412) Hybrid Distillation with CoT Guidance for Edge-Drone Control Code Generation
- [2601.09059](https://arxiv.org/abs/2601.09059) Efficient Multilingual Dialogue Processing via Translation Pipelines and Distilled Language Models
- [2601.09165](https://arxiv.org/abs/2601.09165) Multi-Teacher Ensemble Distillation: A Mathematical Framework for Probability-Domain Knowledge Aggregation
- [2601.09191](https://arxiv.org/abs/2601.09191) From Performance to Practice: Knowledge-Distilled Segmentator for On-Premises Clinical Workflows
- [2601.09881](https://arxiv.org/abs/2601.09881) Transition Matching Distillation for Fast Video Generation
- [2601.10015](https://arxiv.org/abs/2601.10015) CAFEDistill: Learning Personalized and Dynamic Models through Federated Early-Exit Network Distillation
- [2601.10114](https://arxiv.org/abs/2601.10114) Following the Teacher's Footsteps: Scheduled Checkpoint Distillation for Domain-Specific LLMs
- [2601.10321](https://arxiv.org/abs/2601.10321) An Efficient Long-Context Ranking Architecture With Calibrated LLM Distillation: Application to Person-Job Fit
- [2601.10987](https://arxiv.org/abs/2601.10987) Reasoning Distillation for Lightweight Automated Program Repair
- [2601.11269](https://arxiv.org/abs/2601.11269) X-Distill: Cross-Architecture Vision Distillation for Visuomotor Learning
- [2601.11630](https://arxiv.org/abs/2601.11630) A one-step generation model with a Single-Layer Transformer: Layer number re-distillation of FreeFlow
- [2601.11667](https://arxiv.org/abs/2601.11667) Distill-then-Replace: Efficient Task-Specific Hybrid Attention Model Construction
- [2601.11865](https://arxiv.org/abs/2601.11865) CTPD: Cross Tokenizer Preference Distillation
- [2601.12785](https://arxiv.org/abs/2601.12785) Distilling Time Series Foundation Models for Efficient Forecasting
- [2601.13100](https://arxiv.org/abs/2601.13100) Recursive Meta-Distillation: An Axiomatic Framework for Iterative Knowledge Refinement
- [2601.13992](https://arxiv.org/abs/2601.13992) "The Whole Is Greater Than the Sum of Its Parts": A Compatibility-Aware Multi-Teacher CoT Distillation Framework
- [2601.14032](https://arxiv.org/abs/2601.14032) RM-Distiller: Exploiting Generative LLM for Reward Model Distillation
- [2601.14051](https://arxiv.org/abs/2601.14051) Kakugo: Distillation of Low-Resource Languages into Small Language Models
- [2601.14290](https://arxiv.org/abs/2601.14290) Project Aletheia: Verifier-Guided Distillation of Backtracking for Small Language Models
- [2601.14699](https://arxiv.org/abs/2601.14699) Triage knowledge distillation for speaker verification
- [2601.15394](https://arxiv.org/abs/2601.15394) Memorization Dynamics in Knowledge Distillation for Language Models
- [2601.15657](https://arxiv.org/abs/2601.15657) Integrating Knowledge Distillation Methods: A Sequential Multi-Stage Framework
- [2601.16073](https://arxiv.org/abs/2601.16073) DSFedMed: Dual-Scale Federated Medical Image Segmentation via Mutual Distillation Between Foundation and Lightweight Models
- [2601.16219](https://arxiv.org/abs/2601.16219) Domain Specific Specialization in Low-Resource Settings: The Efficacy of Offline Response-Based Knowledge Distillation in Large Language Models
- [2601.16235](https://arxiv.org/abs/2601.16235) Contrastive Knowledge Distillation for Embedding Refinement in Personalized Speech Enhancement
- [2601.16547](https://arxiv.org/abs/2601.16547) CORD: Bridging the Audio-Text Reasoning Gap via Weighted On-policy Cross-modal Distillation
- [2601.17357](https://arxiv.org/abs/2601.17357) Spectral Geometry for Deep Learning: Compression and Hallucination Detection via Random Matrix Theory
- [2601.17910](https://arxiv.org/abs/2601.17910) Adaptive Weighting in Knowledge Distillation: An Axiomatic Framework for Multi-Scale Teacher Ensemble Optimization
- [2601.18909](https://arxiv.org/abs/2601.18909) How Is Uncertainty Propagated in Knowledge Distillation?
- [2601.19919](https://arxiv.org/abs/2601.19919) ASKD-Whisper: Adaptive Self-knowledge Distillation for Efficient and Low-Latency Automatic Speech Recognition
- [2601.20262](https://arxiv.org/abs/2601.20262) Shallow-π: Knowledge Distillation for Flow-based VLAs
- [2601.21288](https://arxiv.org/abs/2601.21288) Drive-KD: Multi-Teacher Distillation for VLMs in Autonomous Driving
- [2601.21611](https://arxiv.org/abs/2601.21611) Thinking Broad, Acting Fast: Latent Reasoning Distillation from Multi-Perspective Chain-of-Thought for E-Commerce Relevance
- [2601.21968](https://arxiv.org/abs/2601.21968) OVD: On-policy Verbal Distillation
- [2601.22475](https://arxiv.org/abs/2601.22475) Continual Policy Distillation from Distributed Reinforcement Learning Teachers
- [2601.22531](https://arxiv.org/abs/2601.22531) Learn from A Rationalist: Distilling Intermediate Interpretable Rationales
- [2601.22709](https://arxiv.org/abs/2601.22709) Gated Relational Alignment via Confidence-based Distillation for Efficient VLMs
- [2602.00852](https://arxiv.org/abs/2602.00852) Investigating the Robustness of Subtask Distillation under Spurious Correlation
- [2602.15845](https://arxiv.org/abs/2602.15845) KD4MT: A Survey of Knowledge Distillation for Machine Translation
- [2602.20164](https://arxiv.org/abs/2602.20164) Benchmarking Distilled Language Models: Performance and Efficiency in Resource-Constrained Settings

### 剪枝 (Pruning)（31 篇）

- [2601.00913](https://arxiv.org/abs/2601.00913) Clean-GS: Semantic Mask-Guided Pruning for 3D Gaussian Splatting
- [2601.02353](https://arxiv.org/abs/2601.02353) Meta-Learning Guided Pruning for Few-Shot Plant Pathology on Edge Devices
- [2601.02437](https://arxiv.org/abs/2601.02437) TAP-ViTs: Task-Adaptive Pruning for On-Device Deployment of Vision Transformers
- [2601.02674](https://arxiv.org/abs/2601.02674) Iterative Structured Pruning for Large Language Models with Multi-Domain Calibration
- [2601.06787](https://arxiv.org/abs/2601.06787) Garbage Attention in Large Language Models: BOS Sink Heads and Sink-aware Pruning
- [2601.07212](https://arxiv.org/abs/2601.07212) MI-PRUN: Optimize Large Language Model Pruning via Mutual Information
- [2601.07667](https://arxiv.org/abs/2601.07667) Adaptive Layer Selection for Layer-Wise Token Pruning in LLM Inference
- [2601.09176](https://arxiv.org/abs/2601.09176) $D^2Prune$: Sparsifying Large Language Models via Dual Taylor Expansion and Attention Distribution Awareness
- [2601.09352](https://arxiv.org/abs/2601.09352) Spectral Complex Autoencoder Pruning: A Fidelity-Guided Criterion for Extreme Structured Channel Compression
- [2601.09694](https://arxiv.org/abs/2601.09694) LLMs can Compress LLMs: Adaptive Pruning by Agents
- [2601.10765](https://arxiv.org/abs/2601.10765) Pruning as Evolution: Emergent Sparsity Through Selection Dynamics in Neural Networks
- [2601.12272](https://arxiv.org/abs/2601.12272) AgenticPruner: MAC-Constrained Neural Network Compression via LLM-Driven Strategy Search
- [2601.12894](https://arxiv.org/abs/2601.12894) Sparse ActionGen: Accelerating Diffusion Policy with Real-time Pruning
- [2601.13143](https://arxiv.org/abs/2601.13143) FastAV: Efficient Token Pruning for Audio-Visual Large Language Model Inference
- [2601.13155](https://arxiv.org/abs/2601.13155) Probe and Skip: Self-Predictive Token Skipping for Efficient Long-Context LLM Inference
- [2601.16366](https://arxiv.org/abs/2601.16366) Post-Training Neural Network Pruning using Graph Curvature
- [2601.17818](https://arxiv.org/abs/2601.17818) ViTCoP: Accelerating Large Vision-Language Models via Visual and Textual Semantic Collaborative Pruning
- [2601.17917](https://arxiv.org/abs/2601.17917) Streaming-dLLM: Accelerating Diffusion LLMs via Suffix Pruning and Dynamic Decoding
- [2601.18091](https://arxiv.org/abs/2601.18091) From LLMs to LRMs: Rethinking Pruning for Reasoning-Centric Models
- [2601.19503](https://arxiv.org/abs/2601.19503) GradPruner: Gradient-Guided Layer Pruning Enabling Efficient Fine-Tuning and Inference for LLMs
- [2601.19794](https://arxiv.org/abs/2601.19794) Component-Aware Pruning Framework for Neural Network Controllers via Gradient-Based Importance Estimation
- [2601.20107](https://arxiv.org/abs/2601.20107) Structural Anchor Pruning: Training-Free Multi-Vector Compression for Visual Document Retrieval
- [2601.20168](https://arxiv.org/abs/2601.20168) Efficient Token Pruning for LLaDA-V
- [2601.22141](https://arxiv.org/abs/2601.22141) Routing the Lottery: Adaptive Subnetworks for Heterogeneous Data
- [2601.22632](https://arxiv.org/abs/2601.22632) DART-ing Through the Drift: Dynamic Tracing of Knowledge Neurons for Adaptive Inference-Time Pruning
- [2601.22841](https://arxiv.org/abs/2601.22841) How Much of a Model Do We Need? Redundancy and Slimmability in Remote Sensing Foundation Models
- [2601.22980](https://arxiv.org/abs/2601.22980) Learnable Permutation for Structured Sparsity on Transformer Models
- [2602.00247](https://arxiv.org/abs/2602.00247) CAPA: Contribution-Aware Pruning and FFN Approximation for Efficient Large Vision-Language Models
- [2602.00372](https://arxiv.org/abs/2602.00372) Post-Training Probability Manifold Correction via Structured SVD Pruning and Self-Referential Distillation
- [2602.00534](https://arxiv.org/abs/2602.00534) AIRE-Prune: Asymptotic Impulse-Response Energy for State Pruning in State Space Models
- [2602.00780](https://arxiv.org/abs/2602.00780) Environment-Aware Adaptive Pruning with Interleaved Inference Orchestration for Vision-Language-Action Models

### KV Cache 压缩（28 篇）

- [2601.00426](https://arxiv.org/abs/2601.00426) RMAAT: Astrocyte-Inspired Memory Compression and Replay for Efficient Long-Context Transformers
- [2601.01204](https://arxiv.org/abs/2601.01204) XStreamVGGT: Extremely Memory-Efficient Streaming Vision Geometry Grounded Transformer with KV Cache Compression
- [2601.03067](https://arxiv.org/abs/2601.03067) Joint Encoding of KV-Cache Blocks for Scalable LLM Serving
- [2601.04359](https://arxiv.org/abs/2601.04359) PackCache: A Training-Free Acceleration Method for Unified Autoregressive Video Generation via Compact KV-Cache
- [2601.07891](https://arxiv.org/abs/2601.07891) KVzap: Fast, Adaptive, and Faithful KV Cache Pruning
- [2601.08343](https://arxiv.org/abs/2601.08343) When KV Cache Reuse Fails in Multi-Agent Systems: Cross-Candidate Interaction is Crucial for LLM Judges
- [2601.08743](https://arxiv.org/abs/2601.08743) TableCache: Primary Foreign Key Guided KV Cache Precomputation for Low Latency Text-to-SQL
- [2601.10155](https://arxiv.org/abs/2601.10155) LOOKAT: Lookup-Optimized Key-Attention for Memory-Efficient Transformers
- [2601.10729](https://arxiv.org/abs/2601.10729) OrbitFlow: SLO-Aware Long-Context LLM Serving with Fine-Grained KV Cache Reconfiguration
- [2601.10953](https://arxiv.org/abs/2601.10953) SwiftKV: An Edge-Oriented Attention Algorithm and Multi-Head Accelerator for Fast, Efficient LLM Decoding
- [2601.11471](https://arxiv.org/abs/2601.11471) Low-Rank Key Value Attention
- [2601.12904](https://arxiv.org/abs/2601.12904) From Prefix Cache to Fusion RAG Cache: Accelerating LLM Inference in Retrieval-Augmented Generation
- [2601.13631](https://arxiv.org/abs/2601.13631) ContiguousKV: Accelerating LLM Prefill with Granularity-Aligned KV Cache Management
- [2601.13684](https://arxiv.org/abs/2601.13684) HeteroCache: A Dynamic Retrieval Approach to Heterogeneous KV Cache Compression for Long-Context LLM Inference
- [2601.14279](https://arxiv.org/abs/2601.14279) On the Limits of Learned Importance Scoring for KV Cache Compression
- [2601.14724](https://arxiv.org/abs/2601.14724) HERMES: KV Cache as Hierarchical Memory for Efficient Streaming Video Understanding
- [2601.16986](https://arxiv.org/abs/2601.16986) Crystal-KV: Efficient KV Cache Management for Chain-of-Thought LLMs via Answer-First Principle
- [2601.17668](https://arxiv.org/abs/2601.17668) Fast KVzip: Efficient and Accurate LLM Inference with Gated KV Eviction
- [2601.18527](https://arxiv.org/abs/2601.18527) Exploring Fine-Tuning for In-Context Retrieval and Efficient KV-Caching in Long-Context Language Models
- [2601.18999](https://arxiv.org/abs/2601.18999) Randomization Boosts KV Caching, Learning Balances Query Load: A Joint Perspective
- [2601.19178](https://arxiv.org/abs/2601.19178) CollectiveKV: Decoupling and Sharing Collaborative Information in Sequential Recommendation
- [2601.20326](https://arxiv.org/abs/2601.20326) Beyond Speedup -- Utilizing KV Cache for Sampling and Reasoning
- [2601.20499](https://arxiv.org/abs/2601.20499) Efficient Autoregressive Video Diffusion with Dummy Head
- [2601.21686](https://arxiv.org/abs/2601.21686) Don't be so Stief! Learning KV Cache low-rank approximation over the Stiefel manifold
- [2601.21896](https://arxiv.org/abs/2601.21896) Past- and Future-Informed KV Cache Policy with Salience Estimation in Autoregressive Video Diffusion
- [2601.21927](https://arxiv.org/abs/2601.21927) SONIC: Segmented Optimized Nexus for Information Compression in Key-Value Caching
- [2601.22996](https://arxiv.org/abs/2601.22996) Competitive Non-Clairvoyant KV-Cache Scheduling for LLM Inference
- [2602.02579](https://arxiv.org/abs/2602.02579) ProphetKV: User-Query-Driven Selective Recomputation for Efficient KV Cache Reuse in Retrieval-Augmented Generation

### 稀疏化 (Sparsity)（26 篇）

- [2601.00942](https://arxiv.org/abs/2601.00942) Reliability Under Randomness: An Empirical Analysis of Sparse and Dense Language Models Across Decoding Temperatures
- [2601.01608](https://arxiv.org/abs/2601.01608) Guiding Token-Sparse Diffusion Models
- [2601.02613](https://arxiv.org/abs/2601.02613) Sparsity-Aware Streaming SNN Accelerator with Output-Channel Dataflow for Automatic Modulation Classification
- [2601.02819](https://arxiv.org/abs/2601.02819) Punctuation-aware Hybrid Trainable Sparse Attention for Large Language Models
- [2601.03043](https://arxiv.org/abs/2601.03043) Lil: Less is Less When Applying Post-Training Sparse-Attention Algorithms in Long-Decode Stage
- [2601.03195](https://arxiv.org/abs/2601.03195) Sparse Knowledge Distillation: A Mathematical Framework for Probability-Domain Temperature Scaling and Multi-Stage Compression
- [2601.06702](https://arxiv.org/abs/2601.06702) GRASP LoRA: GRPO Guided Adapter Sparsity Policy for Cross Lingual Transfer
- [2601.07372](https://arxiv.org/abs/2601.07372) Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models
- [2601.11641](https://arxiv.org/abs/2601.11641) Mixture of Distributions Matters: Dynamic Sparse Attention for Efficient Video Diffusion Transformers
- [2601.15305](https://arxiv.org/abs/2601.15305) Gated Sparse Attention: Combining Computational Efficiency with Training Stability for Long-Context Language Models
- [2601.15370](https://arxiv.org/abs/2601.15370) Improving MoE Compute Efficiency by Composing Weight and Data Sparsity
- [2601.16515](https://arxiv.org/abs/2601.16515) SALAD: Achieve High-Sparsity Attention via Efficient Linear Attention Tuning for Video Diffusion Transformer
- [2601.16991](https://arxiv.org/abs/2601.16991) Sparsity-Aware Low-Rank Representation for Efficient Fine-Tuning of Large Language Models
- [2601.17042](https://arxiv.org/abs/2601.17042) Interpretable and Sparse Linear Attention with Decoupled Membership-Subspace Modeling via MCR2 Objective
- [2601.17367](https://arxiv.org/abs/2601.17367) Elastic Attention: Test-time Adaptive Sparsity Ratios for Efficient Transformers
- [2601.17836](https://arxiv.org/abs/2601.17836) Unleashing the Potential of Sparse Attention on Long-term Behaviors for CTR Prediction
- [2601.20267](https://arxiv.org/abs/2601.20267) SATA: Sparsity-Aware Scheduling for Selective Token Attention
- [2601.21345](https://arxiv.org/abs/2601.21345) Semantic-Guided Dynamic Sparsification for Pre-Trained Model-based Class-Incremental Learning
- [2601.22275](https://arxiv.org/abs/2601.22275) VMonarch: Efficient Video Diffusion Transformers with Structured Attention
- [2601.22379](https://arxiv.org/abs/2601.22379) SPLA: Block Sparse Plus Linear Attention for Long Context Modeling
- [2601.22594](https://arxiv.org/abs/2601.22594) Language Model Circuits Are Sparse in the Neuron Basis
- [2601.22766](https://arxiv.org/abs/2601.22766) Sparse Attention as Compact Kernel Regression
- [2601.22795](https://arxiv.org/abs/2601.22795) Sparse or Dense? A Mechanistic Estimation of Computation Density in Transformer-based LLMs
- [2601.22876](https://arxiv.org/abs/2601.22876) Matterhorn: Efficient Analog Sparse Spiking Transformer Architecture with Masked Time-To-First-Spike Encoding
- [2602.00397](https://arxiv.org/abs/2602.00397) Fast Forward: Accelerating LLM Prefill with Predictive FFN Sparsity
- [2602.00879](https://arxiv.org/abs/2602.00879) Dynamic Expert Sharing: Decoupling Memory from Parallelism in Mixture-of-Experts Diffusion LLMs

### 通用/其他压缩（19 篇）

- [2601.01296](https://arxiv.org/abs/2601.01296) Aggressive Compression Enables LLM Weight Theft
- [2601.04348](https://arxiv.org/abs/2601.04348) SCAR-GS: Spatial Context Attention for Residuals in Progressive Gaussian Splatting
- [2601.05379](https://arxiv.org/abs/2601.05379) EdgeLDR: Quaternion Low-Displacement Rank Neural Networks for Edge-Efficient Deep Learning
- [2601.05394](https://arxiv.org/abs/2601.05394) Sketch&Patch++: Efficient Structure-Aware 3D Gaussian Representation
- [2601.07197](https://arxiv.org/abs/2601.07197) Beyond Variance: Knowledge-Aware LLM Compression via Fisher-Aligned Subspace Diagnostics
- [2601.07396](https://arxiv.org/abs/2601.07396) Forecast the Principal, Stabilize the Residual: Subspace-Aware Feature Caching for Efficient Diffusion Transformers
- [2601.08882](https://arxiv.org/abs/2601.08882) Compressing Vision Transformers in Geospatial Transfer Learning with Manifold-Constrained Optimization
- [2601.09306](https://arxiv.org/abs/2601.09306) On-Device Large Language Models for Sequential Recommendation
- [2601.10801](https://arxiv.org/abs/2601.10801) Towards Tensor Network Models for Low-Latency Jet Tagging on FPGAs
- [2601.12814](https://arxiv.org/abs/2601.12814) CSGaussian: Progressive Rate-Distortion Compression and Segmentation for 3D Gaussian Splatting
- [2601.14821](https://arxiv.org/abs/2601.14821) POTR: Post-Training 3DGS Compression
- [2601.17112](https://arxiv.org/abs/2601.17112) Low-Rank Tensor Approximation of Weights in Large Language Models via Cosine Lanczos Bidiagonalization
- [2601.17443](https://arxiv.org/abs/2601.17443) Clustering-driven Memory Compression for On-device Large Language Models
- [2601.20301](https://arxiv.org/abs/2601.20301) Towards Compact and Robust DNNs via Compression-aware Sharpness Minimization
- [2601.21198](https://arxiv.org/abs/2601.21198) ZipMoE: Efficient On-Device MoE Serving via Lossless Compression and Cache-Affinity Scheduling
- [2601.21420](https://arxiv.org/abs/2601.21420) ConceptMoE: Adaptive Token-to-Concept Compression for Implicit Compute Allocation
- [2601.22488](https://arxiv.org/abs/2601.22488) Elastic Spectral State Space Models for Budgeted Inference
- [2601.23148](https://arxiv.org/abs/2601.23148) Compressed BC-LISTA via Low-Rank Convolutional Decomposition
- [2602.00777](https://arxiv.org/abs/2602.00777) HyLRA: Hybrid Layer Reuse Attention for Efficient Long-Context Inference

### Token 压缩（9 篇）

- [2601.04519](https://arxiv.org/abs/2601.04519) TokenSeg: Efficient 3D Medical Image Segmentation via Hierarchical Visual Token Compression
- [2601.12042](https://arxiv.org/abs/2601.12042) Less Is More -- Until It Breaks: Security Pitfalls of Vision Token Compression in Large Vision-Language Models
- [2601.16093](https://arxiv.org/abs/2601.16093) SAMTok: Representing Any Mask with Two Words
- [2601.16210](https://arxiv.org/abs/2601.16210) PyraTok: Language-Aligned Pyramidal Tokenizer for Video Understanding and Generation
- [2601.21531](https://arxiv.org/abs/2601.21531) On the Adversarial Robustness of Large Vision-Language Models under Visual Token Compression
- [2601.22069](https://arxiv.org/abs/2601.22069) VTC-R1: Vision-Text Compression for Efficient Long-Context Reasoning
- [2601.22674](https://arxiv.org/abs/2601.22674) VisionTrim: Unified Vision Token Compression for Training-Free MLLM Acceleration
- [2602.00268](https://arxiv.org/abs/2602.00268) TokenTrim: Inference-Time Token Pruning for Autoregressive Long Video Generation
- [2602.00686](https://arxiv.org/abs/2602.00686) Learning to Accelerate Vision-Language-Action Models through Adaptive Visual Token Caching

### 混合精度/数值格式（6 篇）

- [2601.12638](https://arxiv.org/abs/2601.12638) Mixed Precision PointPillars for Efficient 3D Object Detection with TensorRT
- [2601.16536](https://arxiv.org/abs/2601.16536) W4A16 Mixed-Precision Matrix Multiplication on Decoupled Architecture: Kernel Design and Memory Bottleneck Analysis for Ascend NPUs
- [2601.17279](https://arxiv.org/abs/2601.17279) SPADE: A SIMD Posit-enabled compute engine for Accelerating DNN Efficiency
- [2601.21623](https://arxiv.org/abs/2601.21623) LAMP: Look-Ahead Mixed-Precision Inference of Large Language Models
- [2601.21737](https://arxiv.org/abs/2601.21737) Mixed-Precision Training and Compilation for RRAM-based Computing-in-Memory Accelerators
- [2602.00838](https://arxiv.org/abs/2602.00838) Exploration of Unary Arithmetic-Based Matrix Multiply Units for Low Precision DL Accelerators

## 四、量化论文四项评分表（80 篇）

评分维度（各 1-10 分）：**精度效果**（量化后精度保持/恢复水平，依据摘要报告的指标）、**压缩倍率**（比特宽度/压缩率激进程度）、**创新性**（方法/理论/格式新颖度）、**可复现性**（代码、标准工具链、方法细节可得性）。启发式规则打分+重点论文人工校准，仅供横向参考。

| # | arXiv | 标题(截断) | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [2601.07878](https://arxiv.org/abs/2601.07878) | Sliced-Wasserstein Distribution Alignment Loss Impro... | 8 | 9 | 7 | 9 | **8.2** |
| 2 | [2601.19213](https://arxiv.org/abs/2601.19213) | M2XFP: A Metadata-Augmented Microscaling Data Format... | 9 | 8 | 9 | 7 | **8.2** |
| 3 | [2601.19320](https://arxiv.org/abs/2601.19320) | StableQAT: Stable Quantization-Aware Training at Ult... | 8 | 9 | 8 | 8 | **8.2** |
| 4 | [2601.06959](https://arxiv.org/abs/2601.06959) | HAS-VQ: Hessian-Adaptive Sparse Vector Quantization ... | 7 | 8 | 8 | 9 | **8.0** |
| 5 | [2601.07892](https://arxiv.org/abs/2601.07892) | Sherry: Hardware-Efficient 1.25-Bit Ternary Quantiza... | 7 | 9 | 7 | 9 | **8.0** |
| 6 | [2601.09985](https://arxiv.org/abs/2601.09985) | FaTRQ: Tiered Residual Quantization for LLM Vector S... | 7 | 9 | 7 | 9 | **8.0** |
| 7 | [2601.14243](https://arxiv.org/abs/2601.14243) | Jet-RL: Enabling On-Policy FP8 Reinforcement Learnin... | 9 | 7 | 8 | 8 | **8.0** |
| 8 | [2601.14888](https://arxiv.org/abs/2601.14888) | What Makes Low-Bit Quantization-Aware Training Work ... | 9 | 8 | 7 | 8 | **8.0** |
| 9 | [2601.15538](https://arxiv.org/abs/2601.15538) | QUAIL: Quantization Aware Unlearning for Mitigating ... | 8 | 7 | 9 | 8 | **8.0** |
| 10 | [2601.19026](https://arxiv.org/abs/2601.19026) | Is Finer Better? The Limits of Microscaling Formats ... | 9 | 7 | 8 | 8 | **8.0** |
| 11 | [2601.19675](https://arxiv.org/abs/2601.19675) | LoPRo: Enhancing Low-Rank Quantization via Permuted ... | 8 | 9 | 7 | 8 | **8.0** |
| 12 | [2601.20088](https://arxiv.org/abs/2601.20088) | Quantization-Aware Distillation for NVFP4 Inference ... | 9 | 8 | 7 | 8 | **8.0** |
| 13 | [2601.20745](https://arxiv.org/abs/2601.20745) | HESTIA: A Hessian-Guided Differentiable Quantization... | 8 | 9 | 8 | 7 | **8.0** |
| 14 | [2601.21279](https://arxiv.org/abs/2601.21279) | NEXUS: Bit-Exact ANN-to-SNN Equivalence via Neuromor... | 9 | 8 | 9 | 6 | **8.0** |
| 15 | [2602.00165](https://arxiv.org/abs/2602.00165) | Benford's Law as a Distributional Prior for Post-Tra... | 8 | 8 | 7 | 9 | **8.0** |
| 16 | [2601.07475](https://arxiv.org/abs/2601.07475) | ARCQuant: Boosting NVFP4 Quantization with Augmented... | 7 | 8 | 7 | 9 | **7.8** |
| 17 | [2601.17187](https://arxiv.org/abs/2601.17187) | High-Rate Quantized Matrix Multiplication I | 9 | 7 | 9 | 6 | **7.8** |
| 18 | [2601.18150](https://arxiv.org/abs/2601.18150) | FP8-RL: A Practical and Stable Low-Precision Stack f... | 8 | 7 | 7 | 9 | **7.8** |
| 19 | [2602.11184](https://arxiv.org/abs/2602.11184) | KBVQ-MoE: KLT-guided SVD with Bias-Corrected Vector ... | 6 | 9 | 7 | 9 | **7.8** |
| 20 | [2601.02455](https://arxiv.org/abs/2601.02455) | Diagnostic-Driven Layer-Wise Compensation for Post-T... | 6 | 8 | 7 | 9 | **7.5** |
| 21 | [2601.09555](https://arxiv.org/abs/2601.09555) | Benchmarking Post-Training Quantization of Large Lan... | 7 | 8 | 6 | 9 | **7.5** |
| 22 | [2601.18306](https://arxiv.org/abs/2601.18306) | Calibrating Beyond English: Language Diversity for B... | 8 | 6 | 7 | 9 | **7.5** |
| 23 | [2601.21626](https://arxiv.org/abs/2601.21626) | HeRo-Q: A General Framework for Stable Low Bit Quant... | 7 | 8 | 8 | 7 | **7.5** |
| 24 | [2601.22347](https://arxiv.org/abs/2601.22347) | Pushing the Limits of Block Rotations in Post-Traini... | 8 | 8 | 7 | 7 | **7.5** |
| 25 | [2601.22716](https://arxiv.org/abs/2601.22716) | Breaking the Blocks: Continuous Low-Rank Decomposed ... | 8 | 8 | 7 | 7 | **7.5** |
| 26 | [2601.22813](https://arxiv.org/abs/2601.22813) | Quartet II: Accurate LLM Pre-Training in NVFP4 by Im... | 6 | 8 | 7 | 9 | **7.5** |
| 27 | [2602.15836](https://arxiv.org/abs/2602.15836) | EdgeNav-QE: QLoRA Quantization and Dynamic Early Exi... | 8 | 8 | 8 | 6 | **7.5** |
| 28 | [2601.02888](https://arxiv.org/abs/2601.02888) | RPIQ: Residual-Projected Multi-Collaboration Closed-... | 7 | 8 | 7 | 7 | **7.2** |
| 29 | [2601.03332](https://arxiv.org/abs/2601.03332) | LUT-KAN: Segment-wise LUT Quantization for Fast KAN ... | 6 | 6 | 8 | 9 | **7.2** |
| 30 | [2601.12033](https://arxiv.org/abs/2601.12033) | Preserving Fairness and Safety in Quantized LLMs Thr... | 8 | 6 | 8 | 7 | **7.2** |
| 31 | [2601.17279](https://arxiv.org/abs/2601.17279) | SPADE: A SIMD Posit-enabled compute engine for Accel... | 8 | 9 | 7 | 5 | **7.2** |
| 32 | [2601.19920](https://arxiv.org/abs/2601.19920) | PiC-BNN: A 128-kbit 65 nm Processing-in-CAM-Based En... | 8 | 9 | 7 | 5 | **7.2** |
| 33 | [2601.22787](https://arxiv.org/abs/2601.22787) | Float8@2bits: Entropy Coding Enables Data-Free Model... | 7 | 9 | 7 | 6 | **7.2** |
| 34 | [2602.00838](https://arxiv.org/abs/2602.00838) | Exploration of Unary Arithmetic-Based Matrix Multipl... | 6 | 9 | 7 | 7 | **7.2** |
| 35 | [2601.00222](https://arxiv.org/abs/2601.00222) | LooC: Effective Low-Dimensional Codebook for Composi... | 7 | 5 | 7 | 9 | **7.0** |
| 36 | [2601.08764](https://arxiv.org/abs/2601.08764) | FusID: Modality-Fused Semantic IDs for Generative Mu... | 7 | 5 | 7 | 9 | **7.0** |
| 37 | [2601.11660](https://arxiv.org/abs/2601.11660) | Zeros can be Informative: Masked Binary U-Net for Im... | 7 | 9 | 7 | 5 | **7.0** |
| 38 | [2601.14277](https://arxiv.org/abs/2601.14277) | Which Quantization Should I Use? A Unified Evaluatio... | 8 | 6 | 5 | 9 | **7.0** |
| 39 | [2601.16536](https://arxiv.org/abs/2601.16536) | W4A16 Mixed-Precision Matrix Multiplication on Decou... | 7 | 9 | 7 | 5 | **7.0** |
| 40 | [2601.17438](https://arxiv.org/abs/2601.17438) | UniGRec: Unified Generative Recommendation with Soft... | 7 | 5 | 7 | 9 | **7.0** |
| 41 | [2601.20317](https://arxiv.org/abs/2601.20317) | VersaQ-3D: Architecture Support for Visual Geometry ... | 8 | 8 | 7 | 5 | **7.0** |
| 42 | [2601.21238](https://arxiv.org/abs/2601.21238) | PTQ4ARVG: Post-Training Quantization for AutoRegress... | 6 | 6 | 7 | 9 | **7.0** |
| 43 | [2603.08713](https://arxiv.org/abs/2603.08713) | Unveiling the Potential of Quantization with MXFP4: ... | 7 | 8 | 7 | 6 | **7.0** |
| 44 | [2601.02563](https://arxiv.org/abs/2601.02563) | Compressed code: the hidden effects of quantization ... | 6 | 5 | 7 | 9 | **6.8** |
| 45 | [2601.03484](https://arxiv.org/abs/2601.03484) | From Bits to Chips: An LLM-based Hardware-Aware Quan... | 6 | 5 | 7 | 9 | **6.8** |
| 46 | [2601.07048](https://arxiv.org/abs/2601.07048) | GPU-Accelerated ANNS: Quantized for Speed, Built for... | 8 | 5 | 7 | 7 | **6.8** |
| 47 | [2601.13563](https://arxiv.org/abs/2601.13563) | ButterflyMoE: Compression-Scalable Ternary Experts v... | 7 | 9 | 6 | 5 | **6.8** |
| 48 | [2601.15287](https://arxiv.org/abs/2601.15287) | Towards Understanding Best Practices for Quantizatio... | 7 | 5 | 6 | 9 | **6.8** |
| 49 | [2601.15598](https://arxiv.org/abs/2601.15598) | Ternary Spiking Neural Networks Enhanced by Compleme... | 6 | 9 | 7 | 5 | **6.8** |
| 50 | [2601.18570](https://arxiv.org/abs/2601.18570) | Feature-Indexed Federated Recommendation with Residu... | 7 | 5 | 6 | 9 | **6.8** |
| 51 | [2601.21193](https://arxiv.org/abs/2601.21193) | Generative Recall, Dense Reranking: Learning Multi-V... | 6 | 5 | 7 | 9 | **6.8** |
| 52 | [2601.22101](https://arxiv.org/abs/2601.22101) | ECO: Quantized Training without Full-Precision Maste... | 7 | 8 | 6 | 6 | **6.8** |
| 53 | [2601.22660](https://arxiv.org/abs/2601.22660) | Layerwise Progressive Freezing Enables STE-Free Trai... | 6 | 9 | 6 | 6 | **6.8** |
| 54 | [2601.00434](https://arxiv.org/abs/2601.00434) | Time--to--Digital Converter (TDC)--Based Resonant Co... | 6 | 8 | 7 | 5 | **6.5** |
| 55 | [2601.02298](https://arxiv.org/abs/2601.02298) | Power-of-Two Quantization-Aware-Training (PoT-QAT) i... | 8 | 5 | 7 | 6 | **6.5** |
| 56 | [2601.02680](https://arxiv.org/abs/2601.02680) | Adversarial Contrastive Learning for LLM Quantizatio... | 7 | 5 | 8 | 6 | **6.5** |
| 57 | [2601.11663](https://arxiv.org/abs/2601.11663) | Activation Sensitivity as a Unifying Principle for P... | 6 | 5 | 8 | 7 | **6.5** |
| 58 | [2601.21737](https://arxiv.org/abs/2601.21737) | Mixed-Precision Training and Compilation for RRAM-ba... | 8 | 6 | 7 | 5 | **6.5** |
| 59 | [2601.22244](https://arxiv.org/abs/2601.22244) | Is Hierarchical Quantization Essential for Optimal R... | 6 | 5 | 6 | 9 | **6.5** |
| 60 | [2601.00679](https://arxiv.org/abs/2601.00679) | QSLM: A Performance- and Memory-aware Quantization F... | 8 | 5 | 7 | 5 | **6.2** |
| 61 | [2601.04719](https://arxiv.org/abs/2601.04719) | GPU-Accelerated INT8 Quantization for KV Cache Compr... | 6 | 6 | 7 | 6 | **6.2** |
| 62 | [2601.05684](https://arxiv.org/abs/2601.05684) | FLRQ: Faster LLM Quantization with Flexible Low-Rank... | 7 | 5 | 7 | 6 | **6.2** |
| 63 | [2601.08089](https://arxiv.org/abs/2601.08089) | Q-realign: Piggybacking Realignment on Quantization ... | 6 | 5 | 8 | 6 | **6.2** |
| 64 | [2601.09451](https://arxiv.org/abs/2601.09451) | Late Breaking Results: Quamba-SE: Soft-edge Quantize... | 7 | 6 | 6 | 6 | **6.2** |
| 65 | [2601.09865](https://arxiv.org/abs/2601.09865) | Advancing Model Refinement: Muon-Optimized Distillat... | 6 | 5 | 7 | 7 | **6.2** |
| 66 | [2601.11200](https://arxiv.org/abs/2601.11200) | FAQ: Mitigating Quantization Error via Regenerating ... | 6 | 5 | 7 | 7 | **6.2** |
| 67 | [2601.12638](https://arxiv.org/abs/2601.12638) | Mixed Precision PointPillars for Efficient 3D Object... | 6 | 6 | 7 | 6 | **6.2** |
| 68 | [2601.14549](https://arxiv.org/abs/2601.14549) | QMC: Efficient SLM Edge Inference via Outlier-Aware ... | 7 | 5 | 7 | 6 | **6.2** |
| 69 | [2601.17987](https://arxiv.org/abs/2601.17987) | Systematic Characterization of Minimal Deep Learning... | 7 | 5 | 7 | 6 | **6.2** |
| 70 | [2601.21069](https://arxiv.org/abs/2601.21069) | CompSRT: Quantization and Pruning for Image Super Re... | 7 | 5 | 7 | 6 | **6.2** |
| 71 | [2601.21219](https://arxiv.org/abs/2601.21219) | Soft Quantization: Model Compression Via Weight Coup... | 7 | 5 | 7 | 6 | **6.2** |
| 72 | [2601.02213](https://arxiv.org/abs/2601.02213) | Quantized SO(3)-Equivariant Graph Neural Networks fo... | 6 | 6 | 6 | 6 | **6.0** |
| 73 | [2601.09773](https://arxiv.org/abs/2601.09773) | Enhancing LUT-based Deep Neural Networks Inference t... | 7 | 5 | 7 | 5 | **6.0** |
| 74 | [2602.00450](https://arxiv.org/abs/2602.00450) | Model Optimization for Multi-Camera 3D Detection and... | 6 | 6 | 7 | 5 | **6.0** |
| 75 | [2602.02538](https://arxiv.org/abs/2602.02538) | Enhancing Post-Training Quantization via Future Acti... | 7 | 5 | 6 | 6 | **6.0** |
| 76 | [2602.02581](https://arxiv.org/abs/2602.02581) | QuantLRM: Quantization of Large Reasoning Models via... | 7 | 5 | 6 | 6 | **6.0** |
| 77 | [2601.00282](https://arxiv.org/abs/2601.00282) | Can Large Language Models Still Explain Themselves? ... | 6 | 5 | 6 | 6 | **5.8** |
| 78 | [2601.15079](https://arxiv.org/abs/2601.15079) | LoRAP: Low-Rank Aggregation Prompting for Quantized ... | 6 | 5 | 7 | 5 | **5.8** |
| 79 | [2601.21623](https://arxiv.org/abs/2601.21623) | LAMP: Look-Ahead Mixed-Precision Inference of Large ... | 6 | 5 | 6 | 6 | **5.8** |
| 80 | [2601.22362](https://arxiv.org/abs/2601.22362) | Understanding Efficiency: Quantization, Batching, an... | 6 | 5 | 6 | 6 | **5.8** |

## 五、本月亮点论文

- **[2601.19213](https://arxiv.org/abs/2601.19213)** M2XFP：元数据增强微缩放格式，精度损失较 MXFP4 平均降低 70.63%、较 NVFP4 降低 37.30%，配套硬件单元实现 1.91× 加速、1.75× 能效——FP4 格式军备赛的最新一击。
- **[2601.19320](https://arxiv.org/abs/2601.19320)** StableQAT：从舍入算子的离散傅里叶分析推导 QAT 代理梯度族，证明 STE 只是其特例，2-4bit 训练稳定性显著提升——代理梯度设计从艺术变为有谱系的科学。
- **[2601.20088](https://arxiv.org/abs/2601.20088)** NVIDIA QAD 技术报告：量化感知蒸馏恢复 NVFP4 精度，对 SFT+RL+合并的多阶段后训练模型比 QAT 更稳定、对数据覆盖鲁棒——FP4 时代的事实标准配方。
- **[2601.14243](https://arxiv.org/abs/2601.14243)** Jet-RL：首个 FP8 RL 系统研究，揭示"BF16 训练+FP8 rollout"的数值失配使 on-policy 退化为 off-policy 导致崩溃——量化 RL 的诊断框架。
- **[2601.19026](https://arxiv.org/abs/2601.19026)** IBM 微缩放极限研究：块大小低于阈值后精度反而退化，证伪"块越小越好"——MX 格式存在最优粒度甜蜜点。
- **[2601.17187](https://arxiv.org/abs/2601.17187)** Ordentlich & Polyanskiy：量化矩阵乘的信息论高率理论，为 absmax INT 与 FP 格式建立率-失真基准——量化研究有了理论锚点。
- **[2601.18306](https://arxiv.org/abs/2601.18306)** 多语言校准研究：非英语/多语言校准集使多语言 LLM 量化困惑度最高降 3.52 点——零成本高收益的最佳实践修正。
- **[2601.12033](https://arxiv.org/abs/2601.12033)** 量化公平与安全：量化一致损害公平性/安全性且非英语更严重，关键权重保护（CWP）把混合精度从"保精度"扩展到"保对齐"。
- **[2601.15538](https://arxiv.org/abs/2601.15538)** QUAIL：发现低比特量化会"复活"已遗忘知识（遗忘更新跨不过量化桶阈值），logits 空间 hinge 损失让遗忘在量化后存活。
- **[2601.21279](https://arxiv.org/abs/2601.21279)** NEXUS：用 IF 神经元逻辑门实现 IEEE-754 浮点算术，ANN→SNN 比特级精确等价（LLaMA-2 70B 精度 0.00% 退化，ULP 误差 6.19）。
- **[2601.11660](https://arxiv.org/abs/2601.11660)** MBU：显式零掩码训练让二值 U-Net 获得有信息量的稀疏第三态，Tensor Core 端到端实现——"零是有信息量的"。
- **[2601.13563](https://arxiv.org/abs/2601.13563)** ButterflyMoE：专家=共享三值基底+蝴蝶旋转，单专家存储 O(d²)→O(d·log d)——MoE 内存扩展瓶颈的结构性解法。

## 六、趋势分析

### 1. FP4/微缩放格式的军备竞赛
MXFP4→NVFP4→M2XFP 的演进线是"少量元数据换大幅精度"的持续加码；IBM 的块粒度极限研究与 Polyanskiy 团队的信息论基准标志着 4-bit 格式从工程竞争进入科学分析阶段。算法-硬件协同（M2XFP 的轻量解码单元、VersaQ-3D 的可重构加速器、昇腾 W4A16 kernel）成为硬门槛——纯软件格式创新空间在收窄。

### 2. 蒸馏与量化深度融合
QAD（NVIDIA）、推理模型 QAT 系统研究（蒸馏是稳健目标）、StableQAT/Hestia 的代理梯度改进共同表明："量化即训练"时代的核心问题是如何在不可微量化下优化——蒸馏目标与代理梯度是两大支柱。

### 3. 校准集成为一阶研究对象
FAQ（同家族大模型再生校准数据）、多语言校准研究、推理模型 QAT 的域对齐发现一致指出：校准数据分布是 PTQ 被低估的一阶变量，"按需合成校准集"正在取代"随手取 WikiText"。

### 4. 量化的安全/公平/隐私维度成型
QUAIL（量化复活遗忘）、公平安全关键权重保护、多语言退化测量、蒸馏记忆动态（记忆降 50%+）——量化评估正从"困惑度+准确率"扩展到对齐保持维度，公平/安全应进入量化方法的标准评测包。

### 5. 理论化与统一化
激活敏感度统一 AWQ/GPTQ、量化 MatMul 高率理论、StableQAT 的傅里叶代理族（STE 为特例）、蒸馏的公理化框架——工程积累进入原理整合期。

### 6. 硬件落地的最后一公里
昇腾 NPU W4A16 kernel、PiC-BNN 65nm 流片、SPADE Posit SIMD、SATA 稀疏调度、QMC 存算协同——量化收益的最终兑现依赖 kernel/芯片级实现，"论文压缩率≠实际加速"的系统鸿沟被反复正视。

## 七、复现资产

本仓库为以下 5 篇核心量化论文提供可运行复现 demo（`scripts/quantization/<id>/`，均优先加载真实 Qwen3-0.6B 权重验证，加载失败回退 mock 权重）：

| arXiv | 论文 | demo 验证内容 |
| --- | --- | --- |
| [2601.19320](https://arxiv.org/abs/2601.19320) | StableQAT | 傅里叶代理 vs STE 的 2/3-bit QAT 重建 MSE（2-bit 下 K=3 降低 46.7%） |
| [2601.19675](https://arxiv.org/abs/2601.19675) | LoPRo | 置换+Hadamard 旋转+显著列保护 vs 朴素 2-bit 残差量化（误差降低 19.4%） |
| [2601.19213](https://arxiv.org/abs/2601.19213) | M2XFP | 2-bit 元数据细化 vs MXFP4 2 的幂 scale（误差降低 14.9%） |
| [2601.15538](https://arxiv.org/abs/2601.15538) | QUAIL | logits 空间 hinge 损失使遗忘方向在 4-bit 量化后存活（cos-sim 0.54→0.97） |
| [2601.20745](https://arxiv.org/abs/2601.20745) | Hestia | 温控软量化退火 vs 硬 STE（2-bit MSE 降低约 50%） |

---
*报告由 reading_machine 自动生成（检索管线+人工二审+启发式评分）；每篇论文的深度技术分析见 `papers/2026-01/<id>/tech_analysis.md`。*
