# arXiv 模型压缩论文三日精读日报（2026-09-03）

> 运行日：2026-09-04（Asia/Shanghai）  
> 固定检索窗口：2026-09-01 00:00 至 2026-09-03 23:59  
> 日期口径：arXiv `/abs` Submission history 中 v1 的 UTC 日历日期；公告日期只用于页面覆盖审计。

## 1. 结论

- 三日窗口相关论文原始数：**66**（09-01：45，09-02：21，09-03：0）。
- 历史真实精读重复：**35**，全部已有真实 `tech_analysis.md`；metadata 不单独作为完成依据。
- 本次新增：**31**（09-01 晚公告 10，09-02 新增 21，09-03 截至运行时 0）。
- 最终新增集合与 453 个历史已分析规范 ID 的交集为 **0**。

09-03 的“0”只表示截至 2026-09-04 本次扫描时，官方分类页中尚无 `/abs` v1 归入该日的相关论文；并非断言后续公告仍为零。下一次三日窗口会自动回查。

## 2. 官方分类页覆盖证据

10 个页面均使用 `show=2000`，声明数与实际 `<dt>/<dd>` 条目逐页一致，且单页均小于 2,000；new 页同时覆盖 new submissions、cross submissions、replacements，recent 页覆盖 09-03/02/01，并以 08-31、08-28 作为窗口外阳性对照。跨分类/页面合并为 **3,178** 个唯一 ID。

| 分类 | 入口 | URL | 页面声明数 | 实际解析数 | 日期/提交分组 |
|---|---|---|---:|---:|---|
| cs.LG | new | [https://arxiv.org/list/cs.LG/new?show=2000](https://arxiv.org/list/cs.LG/new?show=2000) | 278 | 278 | Showing new listings for Thursday, 3 September 2026；New submissions (showing 83 of 83 entries)；Cross submissions (showing 76 of 76 entries)；Replacement submissions (showing 119 of 119 entries) |
| cs.LG | recent | [https://arxiv.org/list/cs.LG/recent?show=2000](https://arxiv.org/list/cs.LG/recent?show=2000) | 974 | 974 | Thu, 3 Sep 2026 (showing 159 of 159 entries )；Wed, 2 Sep 2026 (showing 202 of 202 entries )；Tue, 1 Sep 2026 (showing 336 of 336 entries )；Mon, 31 Aug 2026 (showing 120 of 120 entries )；Fri, 28 Aug 2026 (showing 157 of 157 entries ) |
| cs.CL | new | [https://arxiv.org/list/cs.CL/new?show=2000](https://arxiv.org/list/cs.CL/new?show=2000) | 200 | 200 | Showing new listings for Thursday, 3 September 2026；New submissions (showing 61 of 61 entries)；Cross submissions (showing 40 of 40 entries)；Replacement submissions (showing 99 of 99 entries) |
| cs.CL | recent | [https://arxiv.org/list/cs.CL/recent?show=2000](https://arxiv.org/list/cs.CL/recent?show=2000) | 820 | 820 | Thu, 3 Sep 2026 (showing 101 of 101 entries )；Wed, 2 Sep 2026 (showing 185 of 185 entries )；Tue, 1 Sep 2026 (showing 298 of 298 entries )；Mon, 31 Aug 2026 (showing 82 of 82 entries )；Fri, 28 Aug 2026 (showing 154 of 154 entries ) |
| cs.CV | new | [https://arxiv.org/list/cs.CV/new?show=2000](https://arxiv.org/list/cs.CV/new?show=2000) | 208 | 208 | Showing new listings for Thursday, 3 September 2026；New submissions (showing 118 of 118 entries)；Cross submissions (showing 18 of 18 entries)；Replacement submissions (showing 72 of 72 entries) |
| cs.CV | recent | [https://arxiv.org/list/cs.CV/recent?show=2000](https://arxiv.org/list/cs.CV/recent?show=2000) | 811 | 811 | Thu, 3 Sep 2026 (showing 136 of 136 entries )；Wed, 2 Sep 2026 (showing 152 of 152 entries )；Tue, 1 Sep 2026 (showing 316 of 316 entries )；Mon, 31 Aug 2026 (showing 93 of 93 entries )；Fri, 28 Aug 2026 (showing 114 of 114 entries ) |
| cs.AI | new | [https://arxiv.org/list/cs.AI/new?show=2000](https://arxiv.org/list/cs.AI/new?show=2000) | 288 | 288 | Showing new listings for Thursday, 3 September 2026；New submissions (showing 58 of 58 entries)；Cross submissions (showing 104 of 104 entries)；Replacement submissions (showing 126 of 126 entries) |
| cs.AI | recent | [https://arxiv.org/list/cs.AI/recent?show=2000](https://arxiv.org/list/cs.AI/recent?show=2000) | 1281 | 1281 | Thu, 3 Sep 2026 (showing 162 of 162 entries )；Wed, 2 Sep 2026 (showing 309 of 309 entries )；Tue, 1 Sep 2026 (showing 424 of 424 entries )；Mon, 31 Aug 2026 (showing 190 of 190 entries )；Fri, 28 Aug 2026 (showing 196 of 196 entries ) |
| cs.AR | new | [https://arxiv.org/list/cs.AR/new?show=2000](https://arxiv.org/list/cs.AR/new?show=2000) | 12 | 12 | Showing new listings for Thursday, 3 September 2026；New submissions (showing 4 of 4 entries)；Cross submissions (showing 6 of 6 entries)；Replacement submissions (showing 2 of 2 entries) |
| cs.AR | recent | [https://arxiv.org/list/cs.AR/recent?show=2000](https://arxiv.org/list/cs.AR/recent?show=2000) | 46 | 46 | Thu, 3 Sep 2026 (showing 10 of 10 entries )；Wed, 2 Sep 2026 (showing 12 of 12 entries )；Tue, 1 Sep 2026 (showing 10 of 10 entries )；Mon, 31 Aug 2026 (showing 5 of 5 entries )；Fri, 28 Aug 2026 (showing 9 of 9 entries ) |

检索后对候选逐篇核对官方 `/abs` 的标题、摘要、主/交叉分类和 v1 history；31 篇新增中 30 篇读取官方 HTML 全文，`2609.02036` 读取官方 17 页 PDF。quantization、low-bit、compression、pruning、sparsity、distillation、teacher/student、KV cache、mixed precision、GPTQ、AWQ 等只用于排序和复核，不作为唯一召回门槛。

## 3. 历史去重审计

- 扫描远端 `origin/feature/arxiv-daily-*`：**34 个分支**。
- 从 `papers/**/<id>/tech_analysis.md` 得到历史规范 ID：**453**。
- 历史 metadata 唯一 ID：**456**；metadata-only：**3**。
- 规范化规则：去掉 `v1/v2/...` 后缀；跨日期、分类、关键词和分支合并。

### 被排除的 35 篇历史重复

| arXiv | 标题 | v1 日期 | 来源分支 |
|---|---|---|---|
| [2609.00575](https://arxiv.org/abs/2609.00575) | Residual Sparsification via Output Importance for Compressing Mixture-of-Experts LLMs | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00588](https://arxiv.org/abs/2609.00588) | Quit While You're Ahead: Quit for Efficient Candidate Generation in Machine Translation Reranking | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00611](https://arxiv.org/abs/2609.00611) | Panda Diplomacy: Foundation Model Pre-training across Particle Imaging Detectors for High Energy and Nuclear Physics | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00624](https://arxiv.org/abs/2609.00624) | Trust Your Guide Only When Certain: Uncertainty-Aware Sparse Alignment at Inference Time | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00665](https://arxiv.org/abs/2609.00665) | Triple-Bottom-Line Sustainability of Language Models for Edge AI: A Comparison Between SLMs and Quantized LLMs | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00667](https://arxiv.org/abs/2609.00667) | From Saliency to Discriminability: Rank-Preserving Visual Token Pruning for VLM Rerankers | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00718](https://arxiv.org/abs/2609.00718) | A Closed-Loop Evaluation of Capability Loss and Recovery in Compressed Driving Policies | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00791](https://arxiv.org/abs/2609.00791) | Instella-MoE Technical Report | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00796](https://arxiv.org/abs/2609.00796) | SFAD: Speculative Factuality-Aware Decoding | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00798](https://arxiv.org/abs/2609.00798) | Advanced Pixel Diffusion Model with Guided Sparse Global Refinement | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00865](https://arxiv.org/abs/2609.00865) | MemoryWalker: Stop Training Agents on Contexts They Never Saw | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00891](https://arxiv.org/abs/2609.00891) | CacheBridge: Efficient Cross-Model KV Cache Transfer | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.00951](https://arxiv.org/abs/2609.00951) | CERF: Communication-Efficient and Retraining-Free Collaborative Perception | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01004](https://arxiv.org/abs/2609.01004) | SinkPruner: Sink-Free Visual Token Pruning for Multimodal Large Language Models | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01024](https://arxiv.org/abs/2609.01024) | PCoMoE: Shifting MoE Inference from Monolithic Expert Selection to Fine-Grained Path Composition | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01084](https://arxiv.org/abs/2609.01084) | Hardware Acceleration of Block-Diffusion LLM for Edge Devices | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01091](https://arxiv.org/abs/2609.01091) | Subliminal Learning as Trait-Direction Drift: A Mechanism and Targeted Control under SFT Distillation | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01111](https://arxiv.org/abs/2609.01111) | ClinTraceBench: Source-Verifiable Longitudinal Clinical Reasoning over EHR-Derived Dialogues | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01158](https://arxiv.org/abs/2609.01158) | Superposed Latent Autoencoder | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01200](https://arxiv.org/abs/2609.01200) | Compressing AI Traffic: Standardized Neural Network Coding of Visual-Token Representations in Split Vision-Language Inference | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01212](https://arxiv.org/abs/2609.01212) | Recent Developments in Transformer Inference Deployment on FPGA Platforms: A Survey | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01224](https://arxiv.org/abs/2609.01224) | S$^2$Prune: Spatially Structured Visual Token Pruning for Multimodal Large Language Models | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01232](https://arxiv.org/abs/2609.01232) | Position Matters: Feature Inversion Attacks in ViT Split Inference with Token Reduction and Shuffling | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01343](https://arxiv.org/abs/2609.01343) | SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01345](https://arxiv.org/abs/2609.01345) | Cheap Verifiers, Large Blind Spots: Measuring the Reliability Cost of Cost-Saving Cascades | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01374](https://arxiv.org/abs/2609.01374) | Behaviorally Effective LoRA Writes Are Sparse and Structured | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01406](https://arxiv.org/abs/2609.01406) | Contribution-Aware Bandwidth Allocation for Multimodal Split Learning | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01428](https://arxiv.org/abs/2609.01428) | TRIAGE: Three-level Routing and Intelligent Agent Guidance for Efficient Execution | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01430](https://arxiv.org/abs/2609.01430) | Learning Sparse Decision Trees via Transformer Variational Auto-Encoders | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01507](https://arxiv.org/abs/2609.01507) | LatentPress: Context Compression Beyond Text and Vision | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01532](https://arxiv.org/abs/2609.01532) | Knowledge Distillation During Mid-Training Favors Reasoning over Factual Recall | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01550](https://arxiv.org/abs/2609.01550) | A Mathematical Theory of Reusable Neural Bases for Network Compression | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01567](https://arxiv.org/abs/2609.01567) | Selective Agent Guidance via Entropy: Learning Autonomous Policies from Imperfect VLM Teachers | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01575](https://arxiv.org/abs/2609.01575) | Closing Cost-Quality Gap in Document VLMs: Difficulty-Aware Data Curation and Quality-Adjusted Deployment Economics | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |
| [2609.01587](https://arxiv.org/abs/2609.01587) | The Structure of Quantization Damage in LLMs: Why the Next Bit Should Be Spent Globally | 2026-09-01 | origin/feature/arxiv-daily-2026-09-03 |

## 4. 本次新增论文总表与评分

评分为 1–10：精度效果、压缩倍率、创新性、可复现性。无统一端到端倍率时不从参数量推断；每篇评分依据已经在对应 `tech_analysis.md` 的实验节明确说明。

| # | arXiv | 标题 | v1 日期 | 技术 | 一句话结论 | 精度 | 压缩 | 创新 | 复现 |
|---:|---|---|---|---|---|---:|---:|---:|---:|
| 1 | [2609.01683](https://arxiv.org/abs/2609.01683) | FORGE: Forward-Only Test-Time Adaptation for Integer-Only Vision Models on Microcontrollers | 2026-09-01 | 量化 | 量化后 BN 折叠使常见测试时自适应失去统计量；FORGE 只用前向估计重归一化卷积通道，并只适配 3/21 层。 | 8 | 7 | 8 | 8 |
| 2 | [2609.01740](https://arxiv.org/abs/2609.01740) | ZipTok3D: High-Fidelity 3D Tokenization with Compact Token Prefixes | 2026-09-01 | 其他压缩与高效推理 | ZipTok3D 用可截断的全局 token 前缀表达完整 3D 物体，以极短序列换取生成与重建效率。 | 8 | 9 | 8 | 7 |
| 3 | [2609.01743](https://arxiv.org/abs/2609.01743) | SCULPT: Training Edge Vision Models for Post-Training Quantization Readiness | 2026-09-01 | 量化 | SCULPT 在普通 FP32 微调阶段塑造激活统计，使同一检查点更适合后续 INT8/W4A8 PTQ。 | 8 | 7 | 8 | 8 |
| 4 | [2609.01749](https://arxiv.org/abs/2609.01749) | Swin Meets EfficientNet: Lightweight Architectures for GAN-Based Face Forensics | 2026-09-01 | 其他压缩与高效推理 | 以 EfficientNet-B0 局部特征与 Swin 分层注意力组合，构造面向伪造人脸检测的轻量混合模型。 | 8 | 6 | 6 | 8 |
| 5 | [2609.01768](https://arxiv.org/abs/2609.01768) | Emergence of Fibrations, Compression, and Symmetry Breaking in Artificial Neural Networks | 2026-09-01 | 其他压缩与高效推理 | 论文把训练中涌现的 graph fibration/covering 对称性用于网络折叠，并把结构压缩与持续学习中的可塑性联系起来。 | 8 | 9 | 9 | 6 |
| 6 | [2609.01807](https://arxiv.org/abs/2609.01807) | hLLM: Single Pass Decoding for Generative Reranking | 2026-09-01 | 知识蒸馏 | hLLM 把生成式重排序从逐 token 解码改为一次隐藏态打分加匈牙利指派。 | 8 | 9 | 9 | 7 |
| 7 | [2609.01840](https://arxiv.org/abs/2609.01840) | Cross-Model Distillation of a Human-Pose Foundation Model from Unannotated Infant Video for Markerless 3D Pose Estimation | 2026-09-01 | 知识蒸馏 | 将 Sapiens 2 的精确 2D 姿态伪标签蒸馏进能输出 3D 人体的 SAM 3D Body，且不需要婴儿标注。 | 8 | 6 | 7 | 7 |
| 8 | [2609.01925](https://arxiv.org/abs/2609.01925) | CRISP: Cliff-awaRe Input-adaptive Sparse Prefilling with Structural-Mass-Motivated Routing | 2026-09-01 | 剪枝/稀疏化 | CRISP 用输入自适应结构代理和注意力质量悬崖来稀疏长上下文 prefill。 | 8 | 9 | 9 | 7 |
| 9 | [2609.01947](https://arxiv.org/abs/2609.01947) | On-Policy Distillation Meets Off-Policy GRPO: Training Compact Instruction-Following Rerankers | 2026-09-01 | 知识蒸馏 | 先用离策略 GRPO 强化 4B 教师，再让 1B 学生在自身采样排名上接受软教师奖励。 | 9 | 8 | 8 | 7 |
| 10 | [2609.01952](https://arxiv.org/abs/2609.01952) | Convergence Theory of Knowledge Distillation in Asynchronous P2P Gossip Learning Network | 2026-09-01 | 知识蒸馏 | 为异步 P2P gossip 网络中的知识蒸馏建立函数空间收敛理论，使不同参数形状的节点也能达成预测共识。 | 8 | 5 | 9 | 7 |
| 11 | [2609.01962](https://arxiv.org/abs/2609.01962) | Post-Training Ternarization of Qwen3-4B Capability, Effective Bit Budget, Storage Compression, and Deployment | 2026-09-02 | 量化 | 把 Qwen3-4B 经旋转、E2M-ATQ 三值化和 GPTQ 式误差补偿转成权重量化模型，并严格区分名义位数、实际存储和速度。 | 6 | 9 | 8 | 9 |
| 12 | [2609.02006](https://arxiv.org/abs/2609.02006) | Train What You Deploy: Closing the MLP Reachability Gap in Low-Rank Clone Distillation | 2026-09-02 | 知识蒸馏 | Low-Rank Clone 的训练可达子空间远小于最终部署矩阵；论文让训练对象与实际部署权重完全一致。 | 9 | 8 | 9 | 7 |
| 13 | [2609.02029](https://arxiv.org/abs/2609.02029) | HeadWiseKV: Budgeted Per-Head Cache Residency for Hybrid Long-Context Language Models | 2026-09-02 | 其他压缩与高效推理 | HeadWiseKV 在总驻留预算下为每个物理 KV head 分配静态多级历史窗口，并真正缩短物理缓存。 | 8 | 7 | 8 | 8 |
| 14 | [2609.02036](https://arxiv.org/abs/2609.02036) | SelfLift: Accelerating Few-Step Diffusion via Self-Recovering Resolution Transition | 2026-09-02 | 其他压缩与高效推理 | SelfLift 让少步扩散先以低分辨率去噪，再用模型自身的纠错信号安全升到高分辨率。 | 9 | 9 | 8 | 7 |
| 15 | [2609.02083](https://arxiv.org/abs/2609.02083) | XMerge: Cross-Axis Selection and Reconstructive Layer Merging for LLM Depth Compression | 2026-09-02 | 剪枝/稀疏化 | XMerge 先跨幅值与方向两轴选择可删层，再局部重建相邻存活块，实现无标签深度压缩。 | 8 | 8 | 8 | 8 |
| 16 | [2609.02107](https://arxiv.org/abs/2609.02107) | A Unified Rate-Distortion Perspective on Vector, Product, and Scalar Quantization | 2026-09-02 | 量化 | 用统一 rate-distortion 框架比较视觉 token 的 VQ、PQ、SQ，强调同码率和同 latent 统计下才公平。 | 8 | 8 | 8 | 8 |
| 17 | [2609.02160](https://arxiv.org/abs/2609.02160) | GeoSPRINT: Geometric Redundancy-Aware Step Pruning for Inference in Diffusion Trajectories | 2026-09-02 | 剪枝/稀疏化 | GeoSPRINT 依据去噪轨迹几何冗余裁剪扩散采样步，而不是固定等间隔跳步。 | 8 | 7 | 8 | 8 |
| 18 | [2609.02219](https://arxiv.org/abs/2609.02219) | Hardware-Accelerated Instance Segmentation for Resource-Constrained Space Robotics with Criticality Analysis | 2026-09-02 | 量化 | AVIS 用激活方差无标签选取校准样本，并把量化部署与太空辐射故障关键度联合优化。 | 8 | 7 | 8 | 8 |
| 19 | [2609.02350](https://arxiv.org/abs/2609.02350) | LookStep: Efficient Vision-Language Navigation with Linguistic Foresight and Event Driven Memory | 2026-09-02 | 其他压缩与高效推理 | LookStep 用语言化未来状态和事件驱动滚动记忆替代持续堆积历史帧，降低 VLN 时间与内存开销。 | 8 | 7 | 7 | 7 |
| 20 | [2609.02401](https://arxiv.org/abs/2609.02401) | CA-OPD: Confidence-Aware On-Policy Distillation for Structured Visual Prediction | 2026-09-02 | 知识蒸馏 | CA-OPD 用教师置信度决定何时纠正学生轨迹，并让监督形式与干预位置一致。 | 9 | 7 | 8 | 7 |
| 21 | [2609.02451](https://arxiv.org/abs/2609.02451) | Scalable Kronecker-Fisher Approximation: Efficient Hessian Analysis for Billion-Parameter Language Models Compression | 2026-09-02 | 其他压缩与高效推理 | 用可线性扩展的 Kronecker-Fisher 近似保留跨层曲率交互，为量化、稀疏化和低秩分配敏感度预算。 | 8 | 6 | 9 | 7 |
| 22 | [2609.02496](https://arxiv.org/abs/2609.02496) | Debias-SparseGPT: Bias-Aware Pruning for Large Language Models | 2026-09-02 | 剪枝/稀疏化 | Debias-SparseGPT 在二阶剪枝目标中加入人口属性对比输入的表示去偏项，处理稀疏化放大偏差的问题。 | 8 | 8 | 8 | 8 |
| 23 | [2609.02548](https://arxiv.org/abs/2609.02548) | Learn from Whoever Is Right: Answer-Verified Multi-Teacher Distillation for Multi-Domain LLMs | 2026-09-02 | 知识蒸馏 | MT-SDPO 不按领域标签固定教师，而是逐样本验证答案后汇总所有正确教师，再蒸馏到单一学生。 | 9 | 8 | 9 | 7 |
| 24 | [2609.02652](https://arxiv.org/abs/2609.02652) | Unfolding the Leech Lattice: Fused Multi-Shell Decoding and VRAM Layouts for 2-Bit LLM Weights | 2026-09-02 | 量化 | 补全 Leech-lattice 2-bit 权重多壳解码与实际 VRAM 布局，区分磁盘码率、驻留码率和服务速度。 | 6 | 8 | 9 | 9 |
| 25 | [2609.02676](https://arxiv.org/abs/2609.02676) | LoFi RADIO: A Distilled In-Domain Backbone Applied for Artifact-Severity Grading of Ultra-Low-Field Neonatal Brain MR | 2026-09-02 | 知识蒸馏 | 把多个互补医学视觉基础模型蒸馏为一个域内 ViT-S，用单模型替代推理时的多教师门控。 | 8 | 8 | 7 | 7 |
| 26 | [2609.02684](https://arxiv.org/abs/2609.02684) | H3DNAS: Hardware-Aware ONNX-Native 3D Point Cloud Model Compression | 2026-09-02 | 剪枝/稀疏化 | H3DNAS 直接在 ONNX 图上建立合法通道依赖和硬件感知搜索，无需源码、模型类或搜索期梯度。 | 9 | 9 | 9 | 8 |
| 27 | [2609.02731](https://arxiv.org/abs/2609.02731) | RVSD: Retrieval Vision Sparse Decoding for Mitigating Visual Hallucinations in Large Vision-Language Models | 2026-09-02 | 剪枝/稀疏化 | RVSD 将视觉 token 稀疏化与语义空间按需检索放进一次解码，以可逆补偿缓解稀疏导致的幻觉。 | 8 | 8 | 8 | 7 |
| 28 | [2609.02737](https://arxiv.org/abs/2609.02737) | Language Models Can Control Their Own Attention | 2026-09-02 | 剪枝/稀疏化 | Declarative Attention 让模型在 CoT 中声明 global/focus/local 模式，由引擎据此跳过多数 KV cache 读取。 | 8 | 8 | 9 | 8 |
| 29 | [2609.02760](https://arxiv.org/abs/2609.02760) | Measurement-Driven Sub-Network Selection for On-Premise Retrieval-Augmented Factory Agents | 2026-09-02 | 剪枝/稀疏化 | 以 weight-shared supernetwork、结构压缩和检索蒸馏生成多个子网，再按设备实测质量/吞吐/内存选一个部署。 | 8 | 8 | 8 | 7 |
| 30 | [2609.02780](https://arxiv.org/abs/2609.02780) | ShallowStream: Index Shallow then Answer Deep for Streaming Video Understanding | 2026-09-02 | 其他压缩与高效推理 | ShallowStream 用 MLLM 浅层持续索引视频，仅对查询相关证据启用完整深度，联合压缩计算与 KV 增长。 | 8 | 9 | 9 | 7 |
| 31 | [2609.02846](https://arxiv.org/abs/2609.02846) | UE5M3 FP4 Block Scaling for Stable Language Model Pretraining | 2026-09-02 | 量化 | 用 UE5M3 宽范围块尺度配 E2M1 payload，减少 FP4 预训练对当前张量缩放、RHT 与末层 BF16 回退的依赖。 | 8 | 8 | 8 | 6 |

## 5. 量化复现范围

本次 7 篇量化论文均在 `scripts/quantization/<id>/` 提供 `README.md` 与 `demo.py`，以真实本地 Qwen3-0.6B checkpoint 的权重/激活做算法迁移验证。运行结果、命令、环境和未复现边界见下节及各 README；视觉 MCU、DPU、Nemotron 8B 或专用 GPU kernel 不会被写成已复现。

### 实际运行结果

| arXiv | Qwen3-0.6B 验证路径 | 结果摘要 | 状态 |
|---|---|---|---|
| 2609.01683 | BN-folded forward-only channel renormalization around INT8 projection | 重校准将输出 MSE 0.0141251→2.96737e-05，cosine 0.944702→0.999886。 | PASS |
| 2609.01743 | W4A8 PTQ with exported percentile activation clipping | max-range/裁剪 MSE 为 0.00120821/0.00570164；裸裁剪在此迁移上失败。 | PASS |
| 2609.01962 | Hadamard/KOTMS-style rotation, group-128 affine ternarization and low-rank error compensation | 三值/补偿 MSE 为 0.00914294/0.00801944，补偿后 cosine=0.929254。 | PASS |
| 2609.02107 | equal-8-bit rate-distortion comparison on real Qwen embedding vectors | 同 8 bit/vector 下 SQ/PQ/VQ MSE=0.000261143/0.000159213/7.65529e-05。 | PASS |
| 2609.02219 | activation-variance informative INT8 calibration with output bias correction | AVIS 与随机校准 MSE 均为 4.17197e-05；bias correction 降至 3.67724e-05。 | PASS |
| 2609.02652 | 24D multi-shell signed-vector decoder with bit-plane residency accounting | 估算驻留 1.2348 bpw，输出 cosine=0.933708，shell 直方图=[37, 670, 4675, 80]。 | PASS |
| 2609.02846 | E2M1 FP4 payload with block-16 UE5M3 scale | power-of-two/UE5M3 输出 MSE=0.000621194/0.000414082，UE5M3 cosine=0.998368。 | PASS |

所有脚本使用 CPU 软件 reference；没有 CUDA/MPS。`2609.01743` 的裸 percentile 裁剪变差、`2609.02219` 的 AVIS 与随机校准持平，均作为真实负结果保留，不通过调参或选择性报告伪造正向结论。

## 6. 可审计边界

- 官方 `/abs` 详情页 31/31 成功；全文 31/31 有可读证据（HTML 30、PDF 1）。
- 09-03 尚无入窗相关 v1 时，明确记录“截至运行时未检出”，不把网络错误写成零结果。
- 日报和 metadata 只包含当前新增；历史成果只出现在去重审计表，不复制进 papers 或 scripts。
