# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-07-27 ~ 2026-07-28 (昨天24小时内)  
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference  
**数据来源**: arXiv.org

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2607.25870 | VAD to the Bone: Ultra-Tiny Speech Activity Detection for Edge Deployment | Stephen Bauer 等 | 07-28 | QAT、Pruning、Self-distillation、Edge Deployment | eess.AS, cs.LG |
| 2 | 2607.25583 | How Small Can You Go? LoRA Rank, Target Modules, and Quantization Trade-offs | Mahendra Singh Rathor 等 | 07-28 | Quantization、LoRA、PEFT、Low-bit | cs.AI |
| 3 | 2607.25529 | Are High-weight Neurons the Important Ones? | Qitao Chen 等 | 07-28 | Pruning、Neuron Importance、Image Classification | cs.AI |
| 4 | 2607.25527 | Argus-Unified: Compact Unified Model for Image Understanding and Generation | Weiming Zhuang 等 | 07-27 | Quantizer、VLM、Unified Model、Multimodal | cs.CV, cs.AI |
| 5 | 2607.25451 | Bits and Memories: Verbatim Extraction Across LLM Quantization | Akshay Sasi | 07-27 | LLM Quantization、Privacy、Memorization | cs.LG, cs.CR |
| 6 | 2607.25209 | VaLiDRec: Variable-Length LLM-Aligned Semantic IDs for Recommendation | Shutong Qiao 等 | 07-27 | Quantization、Semantic IDs、Generative Rec | cs.IR, cs.AI |
| 7 | 2607.25180 | Bekko Embedding: Ultra-Compact Multilingual Retrieval Encoders | Yuichi Tateno | 07-27 | INT8 Quantization、Embedding、ONNX | cs.IR |
| 8 | 2607.24981 | Enabling Fully Integer-Only Inference for Lightweight Detection Transformers | Thanh Cong Le 等 | 07-27 | Integer-Only、Detection Transformer、Quantization | cs.CV |
| 9 | 2607.24953 | Stable FP4 Training via Transposition-Invariant Block Quantization | Mehdi Rahimifar 等 | 07-27 | FP4、Block Quantization、Training Stability | cs.LG, cs.AI |
| 10 | 2607.24868 | Noise-Shaped One-Bit Coefficients in Discrete Polynomial Fourier Extension | Shengquan Wang | 07-26 | One-Bit Quantization、Sigma-Delta | cs.CL |
| 11 | 2607.24865 | Tokens are All You Need: Dual-purpose Semantic IDs for Recommendation | Baolei Li 等 | 07-26 | Hierarchical Quantization、Semantic IDs | cs.IR, cs.AI, cs.LG |
| 12 | 2607.24568 | Bit-Accurate FPGA Evaluation of Learned Feature Gating | Gawthaman Senthilvelan 等 | 07-27 | PTQ、QAT、FPGA、Fixed-Point | cs.LG |
| 13 | 2607.24562 | Hierarchical Group-Conditional Conformal Risk Control for LMs | Murilo Salem 等 | 07-27 | Quantization、Selective Prediction、Conformal | cs.AI |
| 14 | 2607.24440 | Scale and Quantization Effects on Uncertainty in VLMs | M M Asif Ferdous | 07-27 | VLM、Quantization、Uncertainty、Calibration | cs.CV, cs.CL, cs.LG |
| 15 | 2607.24377 | MXAttention: Data-Free Optimal Scaling and Pre-Normalization Quantization for MXFP4 | Jianlin Yu 等 | 07-27 | MXFP4、Attention Quantization、Data-Free | cs.LG, cs.AI, cs.CV |
| 16 | 2607.24192 | LLM-based Source Code Compression via Thresholded Symbol Ranking | Angelo Nardone 等 | 07-27 | Quantized Models、Source Code Compression | cs.IT, cs.CL, cs.LG |
| 17 | 2607.24148 | Motion-Aware Vector Quantization with Centroid Reuse for Efficient VLA | Zhuoran Song 等 | 07-27 | Vector Quantization、VLA、Motion-Aware | cs.AI |
| 18 | 2607.22790 | The Sparsity Tax: Weight Sparsity Trade-offs in Event-Driven Neuromorphic Cores | Mattias Westerink 等 | 07-24 | Pruning、Sparsity、Neuromorphic、FPGA | cs.AR |
| 19 | 2607.22564 | Loss-Aware Feature-Map Pruning Using Multi-Armed Bandits | Salem Ameen 等 | 05-29 | Pruning、Feature-Map、Bandits | cs.AI |
| 20 | 2607.19248 | A Flexible Sparsity-Aware FPGA Accelerator for Efficient CNN Inference | Amirhossein Zarei 等 | 07-21 | Pruning、Sparsity、FPGA、CNN | cs.AR |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 12篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| VAD to the Bone (2607.25870) | Angle-based QAT | Speech CNN | 超小边缘部署，per-layer结构化剪枝+QAT |
| LoRA Quantization Trade-offs (2607.25583) | Low-bit QAT | 60M Text-to-SQL | 首次在小模型上系统研究LoRA+量化联合影响 |
| Argus-Unified (2607.25527) | Image Token Quantizer | Unified VLM |  frozen encoder + 可训练 quantizer |
| Bits and Memories (2607.25451) | LLM PTQ | LLMs | 量化对逐字记忆提取的影响评估 |
| VaLiDRec (2607.25209) | Semantic ID Quantization | RecSys | 变长LLM对齐语义ID，避免过度压缩 |
| Bekko Embedding (2607.25180) | INT8 Row-wise | Multilingual Retriever | 124MiB超紧凑编码器，CPU实时 |
| Integer-Only Detection (2607.24981) | Full INT8 | DETR-like | 端到端纯整数轻量检测Transformer |
| Stable FP4 Training (2607.24953) | FP4 Block | 通用 | 转置不变块量化解决训练不稳定性 |
| One-Bit Fourier (2607.24868) | 1-bit ΣΔ | 多项式扩展 | 噪声整形一比特系数的变分估计 |
| Dual-purpose Semantic IDs (2607.24865) | Hierarchical Quant | RecSys | 层次量化实现双重语义ID角色 |
| FPGA Feature Gating (2607.24568) | PTQ/QAT | MLP Classifier | FPGA比特精确评估学习特征门控 |
| MXAttention (2607.24377) | MXFP4 | Diffusion Attention | Data-free最优缩放+预归一化量化 |

### 2.2 剪枝 (Pruning) — 5篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| High-weight Neurons (2607.25529) | Neuron-level | CNN Image Classifier | 质疑大权重=重要神经元的假设 |
| VAD to the Bone (2607.25870) | Structured per-layer | Speech CNN | 自蒸馏指导结构化剪枝 |
| Sparsity Tax (2607.22790) | Unstructured | Event-driven SNN | 神经形态核心的稀疏性开销分析 |
| Loss-Aware Feature-Map (2607.22564) | Feature-map | CNN | 多臂老虎机优化特征图剪枝 |
| Sparsity-Aware FPGA (2607.19248) | Column-wise | CNN | 面向FPGA的列压缩稀疏加速器 |

### 2.3 混合压缩 (Pruning + Quantization) — 2篇

| 论文 | 技术组合 | 目标 | 核心贡献 |
|------|---------|------|---------|
| VAD to the Bone (2607.25870) | Pruning + QAT + Distillation | Edge SAD | 三重压缩协同，仅2.1k参数 |
| FPGA Feature Gating (2607.24568) | PTQ/QAT + Pruning | AM Classifier | 比特精确FPGA验证学习门控 |

### 2.4 知识蒸馏 (Distillation) — 1篇

| 论文 | 蒸馏类型 | 应用 |
|------|---------|------|
| VAD to the Bone (2607.25870) | Self-distillation | 语音活动检测 |

---

## 三、按应用领域分类

| 应用领域 | 论文数量 | 代表性论文 |
|---------|:-------:|-----------|
| **大语言模型 (LLM)** | 4 | Bits and Memories, LoRA Quantization, VaLiDRec, Source Code Compression |
| **计算机视觉 (CV)** | 4 | Argus-Unified, Integer-Only Detection, VLM Uncertainty, MXAttention |
| **推荐系统 (RecSys)** | 2 | VaLiDRec, Dual-purpose Semantic IDs |
| **语音/音频** | 1 | VAD to the Bone |
| **边缘/嵌入式** | 3 | VAD to the Bone, Bekko Embedding, FPGA Feature Gating |
| **机器人 (VLA)** | 1 | Motion-Aware VQ |
| **科学计算** | 1 | One-Bit Fourier |

---

## 四、值得关注的高亮点

1. **超极端压缩**: [2607.25870] 将语音活动检测模型压缩到仅 **2.1k 参数**，通过结构化剪枝+角度QAT+自蒸馏三重手段，在边缘设备上达到 0.850 AUC。

2. **FP4训练稳定性突破**: [2607.24953] 发现现有微缩放FP4量化中张量转置导致的尺度不一致问题，提出转置不变块量化，首次实现稳定的FP4训练。

3. **量化隐私风险**: [2607.25451] 首次系统测量LLM量化对逐字记忆提取的影响，发现低比特量化可能改变模型记忆行为。

4. **Data-Free MXFP4 Attention**: [2607.24377] 无需校准数据即可对扩散视频生成中的Attention进行MXFP4量化，解决裁剪-下溢权衡问题。

5. **纯整数检测Transformer**: [2607.24981] 首次实现端到端纯INT8轻量检测Transformer，涵盖可变形注意力、特征融合和激活函数。

---

*报告生成时间: 2026-07-29 10:15 GMT+8*
