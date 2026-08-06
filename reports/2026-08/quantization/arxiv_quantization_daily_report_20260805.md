# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-08-03 ~ 2026-08-05 (arXiv 最新可用论文)
**检索关键词**: quantization, quantize, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, KV cache compression, mixed precision, GPTQ, AWQ, INT8, INT4, FP4, FP8, LoRA, token pruning, token compression
**数据来源**: arXiv.org (API + Listing Pages)
**说明**: 目标日期 2026-08-05 的论文在 arXiv 上尚未发布（API 最新论文截止 2026-08-04T17:59Z）。本报告收录 2026-08-03 至 2026-08-04 期间未被前日分支覆盖的模型压缩相关论文。

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2608.02901 | AnchorKV: Anchor-Residual KV Cache Compression | Malik Khalaf 等 | 08-03 | KV Cache、Anchor、Compression | cs.LG, cs.CL |
| 2 | 2608.02954 | LowRank-SSM: Hardware-Software Co-Design for Rank-Reduced Mamba | Haocheng Xu 等 | 08-03 | Low-Rank、SVD、FPGA、Mamba | cs.AR |
| 3 | 2608.02048 | SmartGR: Hierarchy and Beam-Aware KD for Generative Recommendation | Ziheng Zhang 等 | 08-03 | Knowledge Distillation、Generative Rec | cs.IR |
| 4 | 2608.03026 | Pruning-Aware Multi-Cluster Co-Inference for Large AI Models | Xiaowen Cao 等 | 08-04 | Pruning、Co-Inference、AI-RAN | cs.DC |
| 5 | 2608.03057 | TASQ: Temporal-Adaptive Bit Sparsification Quantization | Seokho Han 等 | 08-04 | Quantization、Bit Sparsification、Diffusion | cs.CV |
| 6 | 2608.03083 | GSTEP: Global Spatio-Temporal Density-Driven Visual Token Pruning | Mengjie Zhang 等 | 08-04 | Token Pruning、VideoLLM、Spatio-Temporal | cs.CV, cs.CL |
| 7 | 2608.03112 | Adaptive Two-Stage Visual Token Pruning for Video-Language Models | Paribesh Regmi 等 | 08-04 | Token Pruning、Video、Adaptive | cs.CV, cs.AI |
| 8 | 2608.03276 | TaskPress: Query-Agnostic KV Cache Compression via Task-Guided Pruning | Wonpyo Park 等 | 08-04 | KV Cache、Pruning、Query-Agnostic | cs.AI |
| 9 | 2608.03490 | Lightweight 3D Object Detection via Mamba-Based Knowledge Distillation | Quoc Cuong Ninh 等 | 08-04 | Knowledge Distillation、3D Detection、Mamba | cs.RO, cs.CV |
| 10 | 2608.03579 | Pin Once, Swap Light: Subspace-Aligned Centroid-Residual for Ultra-LoRA | Xiang Li 等 | 08-04 | LoRA、Low-Rank、Serving | cs.LG, cs.AI |
| 11 | 2608.03580 | SlimVLM: Sensitivity-aware Dynamic Structured Pruning for VLMs | Yaozhi Wen 等 | 08-04 | Structured Pruning、VLM、Sensitivity | cs.CV |
| 12 | 2608.03649 | When Do Fewer Visual Tokens Accelerate Multimodal Inference? | Hao Dou 等 | 08-04 | Token Reduction、Break-Even、Latency | cs.CV |
| 13 | 2608.03681 | Keep the Needle, Prune the Haystack: Defect-Preserving Token Pruning | Yanning Hou 等 | 08-04 | Token Pruning、Anomaly Detection | cs.CV |
| 14 | 2608.03796 | Efficient Knowledge Distillation for LLMs: Offline Top-K Logits | Bakbergen Ryskulov 等 | 08-04 | Knowledge Distillation、LLM、KL Loss | cs.CL, cs.AI, cs.LG |
| 15 | 2608.03812 | OmniPack: Unified Token Compression for Efficient Omni-modal LLMs | Wanshun Su 等 | 08-04 | Token Compression、Omni-modal、Training-free | cs.CV |
| 16 | 2608.03854 | Quantization Effects on Biomedical LLM Reliability | Anton Rasmussen 等 | 08-04 | Quantization、INT8、INT4、Calibration | cs.LG |
| 17 | 2608.03867 | Heterogeneity-Aware Microscaling for Efficient Low-Bit LLM Inference | Junyi Luo 等 | 08-04 | Microscaling、MXFP4、LLM Inference | cs.AR |
| 18 | 2608.03919 | Low-Dimensional High-Leverage Subspace Optimization for NN Quantization | Peng Xia 等 | 08-04 | Quantization、PTQ、QAT、Subspace | cs.CV |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 6篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| AnchorKV (2608.02901) | KV Cache 压缩 | 70B LLM | 锚点残差表示，20x压缩保留99%精度 |
| TASQ (2608.03057) | Bit Sparsification | 扩散模型 | 时序自适应LSB截断，BitOPs减少25-50% |
| TaskPress (2608.03276) | KV Cache 剪枝+量化 | LLM | 任务引导query-agnostic压缩，量化scale factor检测outlier |
| Biomedical LLM (2608.03854) | INT8/INT4 评估 | Mistral-7B | 量化对校准可靠性影响，scoring rule主导校准 |
| AdaMX (2608.03867) | MXFP4 自适应 | 3B-70B LLM | 异质性感知微缩放，消除83% MXFP4精度损失 |
| NAP (2608.03919) | PTQ/QAT 优化 | 紧凑网络 | 归一化仿射预处理，低维子空间优化量化鲁棒性 |

### 2.2 剪枝 (Pruning) — 6篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Pruning-Aware Co-Inference (2608.03026) | 模型剪枝 | 大AI模型 | 多集群协同推理+剪枝率联合优化 |
| GSTEP (2608.03083) | Token 剪枝 | VideoLLM | 全局时空密度驱动，75%剪枝保留100.2%性能 |
| Adaptive Two-Stage (2608.03112) | Token 剪枝 | Video-VLM | 两阶段自适应(帧级+token级)，95% FLOPs减少 |
| SlimVLM (2608.03580) | 结构化剪枝 | VLM | 敏感性感知动态剪枝+自适应视觉token选择 |
| KeepAD (2608.03681) | Token 剪枝 | 异常检测 | 缺陷保留剪枝，7.9x加速，AUROC退化<2.7pp |
| OmniPack (2608.03812) | Token 压缩 | Omni-LLM | 训练免费统一压缩，98%性能@16.7% FLOPs |

### 2.3 知识蒸馏 (Knowledge Distillation) — 3篇

| 论文 | 蒸馏类型 | 应用 |
|------|---------|------|
| SmartGR (2608.02048) | 层次感知+束搜索蒸馏 | 生成式推荐 |
| Mamba-KD 3D Detection (2608.03490) | 特征对齐蒸馏 | 3D目标检测 |
| Efficient KD for LLMs (2608.03796) | 离线Top-K Logits+分块KL | LLM压缩 |

### 2.4 其他 (Other) — 3篇

| 论文 | 技术类型 | 核心贡献 |
|------|---------|---------|
| LowRank-SSM (2608.02954) | 低秩分解 | Mamba投影层截断SVD，FPGA加速2.19x |
| SALT (2608.03579) | 超低秩LoRA | r≤2残差恢复高秩精度，16x内存缩减 |
| Break-Even Study (2608.03649) | Token压缩分析 | 更少token不保证更低延迟的实证研究 |

---

## 三、量化论文评分

| 序号 | arXiv ID | 论文标题 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 总分 |
|:---:|----------|---------|:-------:|:-------:|:-----:|:-------:|:---:|
| 1 | 2608.02901 | AnchorKV | 9 | 9 | 8 | 7 | 33 |
| 2 | 2608.03057 | TASQ | 8 | 8 | 8 | 8 | 32 |
| 3 | 2608.03276 | TaskPress | 7 | 7 | 7 | 6 | 27 |
| 4 | 2608.03854 | Biomedical LLM | 7 | 5 | 6 | 9 | 27 |
| 5 | 2608.03867 | AdaMX | 9 | 8 | 9 | 6 | 32 |
| 6 | 2608.03919 | NAP | 8 | 6 | 8 | 7 | 29 |

**评分标准说明**:
- **精度效果** (1-10): 量化后模型精度保持程度，越高越好
- **压缩倍率** (1-10): 实际压缩比，越高越好
- **创新性** (1-10): 方法论创新程度，越高越好
- **可复现性** (1-10): 代码可用性和实验复现难度，越高越容易复现

---

## 四、整体分析

### 4.1 量化领域趋势

本批论文反映了量化研究的几个重要趋势：

**KV Cache 压缩成为热点**: 3篇论文（AnchorKV、TaskPress及间接相关的OmniPack）聚焦KV cache压缩，反映了长上下文推理的内存瓶颈已成为量化的核心战场。AnchorKV的锚点残差表示方法以20x压缩比保留99%精度，TaskPress则通过任务引导实现query-agnostic的可复用压缩。

**微缩放格式持续演进**: AdaMX在MXFP4基础上引入异质性感知的自适应格式选择，消除了83%的MXFP4精度损失。这延续了MXFP4系列工作（如前日的MXAttention）的思路，但从数据无关转向数据驱动的per-block方案选择。

**量化训练优化新视角**: NAP从参数子空间异质性角度重新审视量化训练，识别出归一化仿射参数作为"低维高杠杆子空间"，以极小的微调成本（仅0.01%参数）显著提升量化鲁棒性。

**量化可靠性评估**: Biomedical LLM论文揭示了量化评估中的一个重要盲点——概率提取协议（scoring rule）对校准的 影响 远超量化精度本身，提醒研究者在评估量化效果时需控制实现变量。

### 4.2 剪枝领域趋势

**Token 剪枝主导**: 6篇剪枝论文中5篇涉及token pruning/compression，反映视觉token冗余已成为VLM/VideoLLM效率优化的核心方向。GSTEP（75%剪枝保留100.2%性能）和OmniPack（98%性能@16.7% FLOPs）展示了token压缩的巨大潜力。

**自适应成为标配**: 从固定剪枝率到内容自适应（Adaptive Two-Stage）、敏感性感知（SlimVLM）、密度驱动（GSTEP），自适应策略已成为新一代剪枝方法的标准配置。

### 4.3 知识蒸馏领域趋势

**系统级效率优化**: Efficient KD for LLMs聚焦蒸馏训练的工程效率，通过离线logits缓存和分块KL损失将训练吞吐量提升41%，代表了蒸馏研究从算法创新向系统优化的转向。

**领域特化蒸馏**: SmartGR和Mamba-KD分别将蒸馏应用于生成式推荐和3D检测，展示了KD在非传统NLP领域的泛化能力。

### 4.4 值得关注的高亮点

1. **AnchorKV (2608.02901)**: 锚点残差表示实现20x KV cache压缩且不丢弃任何token，在70B模型上保留99%精度，是KV cache压缩的重要突破。

2. **AdaMX (2608.03867)**: 异质性感知微缩放在不增加等效位宽的前提下，消除83%的MXFP4精度损失，并在22nm芯片上验证仅增1%系统能耗，兼具算法与硬件创新。

3. **NAP (2608.03919)**: 以仅0.01%参数的微调成本恢复严重坍塌的低比特量化，揭示了归一化仿射参数作为量化鲁棒性"控制变量"的关键作用。

4. **OmniPack (2608.03812)**: 训练免费的统一token压缩在Qwen2.5-Omni-7B上实现98%性能@16.7% FLOPs，展示了跨模态压缩的实用价值。

5. **GSTEP (2608.03083)**: 全局时空密度驱动剪枝在LLaVA-OneVision-7B上75%剪枝保留100.2%性能，证明了全局视角优于局部segment-level剪枝。

---

## 五、代码复现说明

以下6篇量化论文已基于 Qwen3-0.6B 完成代码复现，位于 `scripts/quantization/` 目录下：

| arXiv ID | 论文 | 代码路径 | 验证状态 |
|----------|------|---------|---------|
| 2608.02901 | AnchorKV | `scripts/quantization/2608.02901/` | 已验证 (Qwen3-0.6B) |
| 2608.03057 | TASQ | `scripts/quantization/2608.03057/` | 已验证 (Qwen3-0.6B) |
| 2608.03276 | TaskPress | `scripts/quantization/2608.03276/` | 已验证 (Qwen3-0.6B) |
| 2608.03854 | Biomedical LLM | `scripts/quantization/2608.03854/` | 已验证 (Qwen3-0.6B) |
| 2608.03867 | AdaMX | `scripts/quantization/2608.03867/` | 已验证 (Qwen3-0.6B) |
| 2608.03919 | NAP | `scripts/quantization/2608.03919/` | 已验证 (Qwen3-0.6B) |

每个复现包含 `README.md`（方法说明+使用指南）和 `demo.py`（完整算法实现+量化前后对比验证），共享工具脚本位于 `scripts/quantization/quantization_toolkit.py`。

---

*报告生成时间: 2026-08-06 GMT+8*
*分支: feature/arxiv-daily-2026-08-06*
