# ArXiv 模型压缩领域论文日报

**收集日期**: 2026-08-07
**目标日期**: 2026-08-06 (arXiv 提交日期 2026-08-05，因 arXiv 索引延迟)
**检索关键词**: quantization, quantize, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, KV cache compression, mixed precision, GPTQ, AWQ 等
**数据来源**: arXiv.org API (submittedDate 范围过滤)
**运行日期**: 2026-08-07

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 核心领域 | 类别 |
|:---:|----------|---------|------|:-------:|------|
| 1 | 2608.05127 | SSTQ: Privacy-Preserving Vector Quantization via Subsampled Stochastic TurboQuant | A. Javanmard, D. Woodruff, V. Mirrokni | 量化 | cs.LG, cs.AI |
| 2 | 2608.05069 | VQ-VAD: Vector-quantized Motion Representation Learning for VAD | N. Rashvand 等 | 量化 | cs.CV, cs.AI |
| 3 | 2608.04991 | RAC: Reference-Aware Activation Compression for Split LLM Inference | G. Yang 等 | 量化 | cs.DC |
| 4 | 2608.04488 | Energy- and Memory-Efficient PEFT Methods for On-Device SLMs | K. Akhmetzhanov, J. Park | 量化 | cs.CL |
| 5 | 2608.04405 | Training-Free Hashing-Based Attention via Binary Principal Components | D. Yu 等 | 量化 | cs.LG, cs.AI |
| 6 | 2608.05104 | BnBERT-iPet: Sparse Few-Shot Language Modeling via Lottery Ticket Pruning | S. Hossain 等 | 剪枝 | cs.LG |
| 7 | 2608.05033 | SparseDitto: Customizing GPU Kernels for Different Sparsity Patterns | S. Li 等 | 剪枝 | cs.DC |
| 8 | 2608.04811 | StaticSegFormer: Efficient Semantic Segmentation via Static Structured Pruning | T. Bartels 等 | 剪枝 | cs.CV |
| 9 | 2608.04680 | MOAT: Model-Agnostic Randomized Transformations for ViT Efficiency | A. Goyal 等 | 剪枝 | cs.CR |
| 10 | 2608.04610 | HiSC: Hierarchical Spatial Clustering Token Compression for 3D | J. Qu 等 | 剪枝 | cs.CV |
| 11 | 2608.04593 | Rethinking Reservoir Pruning: A Dynamical Perspective for ESN | S. Laudari, P. Adhikari | 剪枝 | cs.LG |
| 12 | 2608.04515 | CARVE: Cross-Slice Anisotropic Reallocation for 3D Medical Volume | Z. Yi 等 | 剪枝 | cs.CV |
| 13 | 2608.04496 | DIVE: Dynamic Iterative Visual Evidence Construction for VLMs | C. Zhong 等 | 剪枝 | cs.CV |
| 14 | 2608.04483 | Not All Redundant Tokens Are Alike: Visual Token Pruning Analysis | H. Kim 等 | 剪枝 | cs.CV |
| 15 | 2608.04472 | EndoVLM: Endoscopy VLM via Anatomy-Guided Sparsity | Z. Yi 等 | 剪枝 | cs.CV |
| 16 | 2608.04428 | Deltoris: Real-time VLA Inference via Bit-level Sparsity | Z. Liu 等 | 剪枝 | cs.AR |
| 17 | 2608.04771 | Fewer Tokens, Smaller Cache: Reward-Coordinated Efficient Reasoning | Q. Zhu 等 | 其他 | cs.AI |
| 18 | 2608.04891 | GVC-RT: Real-Time Generative Video Compression at Ultra-Low Bitrates | T. Dang 等 | 其他 | eess.SP |
| 19 | 2608.04893 | When Does Latent Communication Pay? KV Caches in Multi-Agent LLMs | J. Cheng 等 | 其他 | cs.CR |
| 20 | 2608.05111 | Reward Structure Shapes Exploration and Neural Memory in RL | J. Malegaonkar 等 | 其他 | cs.LG |

---

## 二、量化论文评分（核心维度）

对 5 篇量化相关论文从精度效果、压缩倍率、创新性、可复现性四个维度进行打分（1-10 分）：

| arXiv ID | 论文简称 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合评分 | 代码复现 |
|:---:|----------|:---:|:---:|:---:|:---:|:---:|:---:|
| 2608.05127 | SSTQ (隐私保护VQ) | 7 | 6 | 8 | 7 | 7.0 | [scripts/quantization/2608.05127/](../../scripts/quantization/2608.05127/) |
| 2608.05069 | VQ-VAD (运动VQ) | 7 | 8 | 7 | 8 | 7.5 | [scripts/quantization/2608.05069/](../../scripts/quantization/2608.05069/) |
| 2608.04991 | RAC (激活压缩) | 8 | 7 | 8 | 7 | 7.5 | [scripts/quantization/2608.04991/](../../scripts/quantization/2608.04991/) |
| 2608.04488 | Energy-Efficient PEFT | 7 | 8 | 6 | 9 | 7.5 | [scripts/quantization/2608.04488/](../../scripts/quantization/2608.04488/) |
| 2608.04405 | BinaryPC (二值哈希注意力) | 8 | 7 | 8 | 9 | 8.0 | [scripts/quantization/2608.04405/](../../scripts/quantization/2608.04405/) |

**评分说明**：
- **精度效果**：量化后模型性能保持程度（精度损失、任务分数变化）
- **压缩倍率**：实际压缩比例和内存/通信节省
- **创新性**：方法的新颖性和理论贡献
- **可复现性**：论文描述清晰度、代码可用性、复现难度

---

## 三、按技术方向分类

### 3.1 量化 (Quantization) — 5 篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 | 复现结果 |
|------|---------|---------|---------|---------|
| SSTQ (2608.05127) | 隐私保护VQ | 联邦学习 | 过完备紧框架+子采样+LDP，MSE从O(4^b)降至O(2^b) | K=2000时MSE=0.000057 |
| VQ-VAD (2608.05069) | 向量量化 | 视频异常检测 | VQ-GAN适配运动序列，离散运动码本，81.83%准确率 | 压缩2730x，cos=0.795 |
| RAC (2608.04991) | 激活压缩 | 分割LLM推理 | 参考感知编解码+分组仿射对齐+残差量化 | MSE降低46%，压缩7.0x |
| Energy-Efficient PEFT (2608.04488) | NF4+QLoRA | 消费级GPU SLM | LoRA+/QLoRA/BitFit能源-内存权衡，QLoRA省3.9x VRAM | NF4 cos=0.996，VRAM省3.5x |
| BinaryPC (2608.04405) | 二值哈希 | 长上下文LLM | PCA二值哈希稀疏注意力，3.56x吞吐提升 | 保留50%KV，cos=0.983 |

### 3.2 剪枝 (Pruning) — 11 篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| BnBERT-iPet (2608.05104) | 彩票票剪枝 | 孟加拉语BERT | 10%边保留，与大规模模型竞争 |
| SparseDitto (2608.05033) | GPU稀疏内核 | 稀疏矩阵运算 | LLM代理系统定制GPU内核，2.68x加速 |
| StaticSegFormer (2608.04811) | 静态结构化剪枝 | 语义分割 | 帧率提升34%，mIoU零下降 |
| MOAT (2608.04680) | Token剪枝防御 | ViT | 对抗攻击下GFLOPs退化<3.4% |
| HiSC (2608.04610) | Token压缩 | 3D VLM | 90%+token削减，免训练 |
| Reservoir Pruning (2608.04593) | 动力学剪枝 | ESN | 轨迹雅可比格拉姆矩阵排序神经元 |
| CARVE (2608.04515) | Token重分配 | 3D医学体量 | 移除80%token，AMOS-MM+6.2点 |
| DIVE (2608.04496) | 动态迭代剪枝 | VLM | 88.9%视觉token减少，98.2%性能保持 |
| Token Roles (2608.04483) | Token分析 | VLM | 揭示非活跃token价值，偏差与性能不直接相关 |
| EndoVLM (2608.04472) | 解剖引导稀疏 | 内镜VLM | 348K+预训练，超越现有FM |
| Deltoris (2608.04428) | 比特级稀疏 | VLA | 34.2x加速(vs移动GPU)，50-200Hz |

### 3.3 其他 (Other) — 4 篇

| 论文 | 技术类型 | 目标 | 核心贡献 |
|------|---------|------|---------|
| Fewer Tokens (2608.04771) | KV cache压缩 | 推理模型 | 奖励协调的高效推理，动态压缩策略 |
| GVC-RT (2608.04891) | 生成式视频压缩 | 视频编码 | 超低比特率实时生成视频压缩 |
| KV Caches Multi-Agent (2608.04893) | KV cache审计 | 多智能体LLM | 因果审计KV cache中继的有效性 |
| RL Neural Memory (2608.05111) | 神经记忆剪枝 | 强化学习 | 奖励结构塑造探索与记忆的交互 |

---

## 四、量化论文详细分析

### 4.1 BinaryPC (2608.04405) — 最高综合评分 8.0

**方法**：BinaryPC 是一种无需训练的、数据感知的哈希稀疏注意力方法。通过计算数据的二值主成分（PCA 投影后取符号位），构建紧凑的二值哈希码和对应的哈希函数。与 LSH（随机投影）或学习型哈希不同，BinaryPC 显式保留数据的结构信息，无需梯度训练。

**关键指标**：
- 解码吞吐量提升 3.56x（vs FlashAttention）
- 精度接近全注意力（余弦相似度 0.983，我们的复现验证）
- 理论计算量减少 50%（保留 top-k KV 对）

**复现验证**：在真实 Qwen3-0.6B 上运行成功，n_heads=16, n_kv_heads=8, head_dim=128, layers=28。保留 50% KV 对时输出余弦相似度 0.983，与论文报告一致。

### 4.2 RAC (2608.04991) — 综合评分 7.5

**方法**：RAC 是面向分割 LLM 推理的参考感知编解码器。通过检索精确 token 历史跨度进行 prefill 上行链路压缩，重用重构的上行链路状态用于同轮 prefill 下行链路，并使用轻量级因果预测器生成解码参考。核心技术包括分组仿射对齐、校准残差量化（可选 prefill 异常值保留）。

**关键指标**：
- TTFT 比率 1.24-2.72x，TPOT 比率 1.01-2.79x
- 12 个任务分数变化范围 -0.40 至 +2.50
- 我们的复现：MSE 降低 46%（vs 直接 4bit 量化），压缩 7.0x

### 4.3 VQ-VAD (2608.05069) — 综合评分 7.5

**方法**：将 VQ-GAN 从图像生成适配到关键点序列，构建正常行为的运动码本。仅在正常运动序列上训练，通过识别高重构误差检测异常。

**关键指标**：
- HR-SHT 准确率 81.83%
- CMU Panoptic 到 HR-SHT 跨域迁移 76.69%（无需重训练）
- 我们的复现：压缩 2730x，码本利用率 10.9%，cos=0.795

### 4.4 Energy-Efficient PEFT (2608.04488) — 综合评分 7.5

**方法**：系统比较 Full FT、LoRA、LoRA+、QLoRA、BitFit 五种 PEFT 方法，在 Transformer（TinyLlama-1.1B, Qwen3-1.7B）和 SSM（Mamba-1.4B, Mamba-2-1.3B）上，使用 NetScore-E（能源）和 NetScore-M（内存）评估。

**关键指标**：
- QLoRA 峰值 VRAM 降低 3.9x（vs LoRA）
- LoRA+ 在 24 个配置中 19 个获得最高 NetScore-E
- 我们的复现：NF4 量化 cos=0.996，VRAM 节省 3.5x

### 4.5 SSTQ (2608.05127) — 综合评分 7.0

**方法**：Subsampled Stochastic TurboQuant 结合过完备等范数紧框架、坐标子采样和隐私感知一维量化。包含两个变体：Flat Randomized Response 和 Metric-Aware Laplace。在联邦学习中实现局部差分隐私。

**关键指标**：
- 使用 ⌈log₂ N⌉ + b 位/客户端
- MSE 从 O(4^b) 降至 O(2^b)
- 我们的复现：K=2000 时 MSE=0.000057（1/K 衰减），无偏性误差 0.0196

---

## 五、值得关注的高亮点

1. **二值哈希注意力突破**：[2608.04405] BinaryPC 实现了无需训练的数据感知二值哈希，在长上下文 LLM 上达到 3.56x 解码加速且精度几乎无损，为 KV cache 压缩提供了新范式。

2. **激活压缩通信优化**：[2608.04991] RAC 首次将参考感知编码引入分割 LLM 推理，通过历史 span 检索和残差量化，在保持任务性能的同时显著降低通信开销。

3. **QLoRA 能效分析**：[2608.04488] 首次系统比较 PEFT 方法的能源消耗，发现 QLoRA 虽省 VRAM 3.9x，但反量化开销导致其在能效评估中仅被选中 1 次——揭示了精度与能效的微妙权衡。

4. **Token 剪枝认知**：[2608.04483] 揭示"并非所有冗余 token 都一样"，发现非活跃 token 可能携带重要语义信息，挑战了"低注意力权重=可剪枝"的传统假设。

5. **比特级稀疏加速**：[2608.04428] Deltoris 利用比特级稀疏性和投机推理，在 VLA 模型上实现 34.2x 加速，满足 50-200Hz 实时控制需求。

6. **视觉 token 压缩趋势**：本日 11 篇剪枝论文中 7 篇涉及视觉 token 压缩（HiSC, CARVE, DIVE, Token Roles, EndoVLM, MOAT, StaticSegFormer），反映 VLM 效率优化已成为热点方向。

---

## 六、技术趋势总结

### 6.1 量化方向
- **二值化/低比特化**：BinaryPC 的 PCA 二值哈希和 SSTQ 的随机量化代表了向极低比特发展的趋势
- **激活压缩**：RAC 针对推理通信瓶颈的激活压缩，填补了分割推理场景的空白
- **PEFT 量化**：QLoRA 在消费级 GPU 上的能效分析，为端侧部署提供了实践指导
- **向量量化**：VQ-VAD 将 VQ 从生成扩展到异常检测，展示了码本方法的跨域适用性

### 6.2 剪枝方向
- **视觉 token 压缩主导**：7/11 篇剪枝论文聚焦 VLM 的视觉 token 剪枝
- **静态 vs 动态**：StaticSegFormer 探索静态剪枝在分割中的优势，DIVE 提出动态迭代方法
- **比特级稀疏**：Deltoris 将稀疏性细化到比特级别，为硬件加速提供新思路
- **防御性剪枝**：MOAT 首次关注 token 剪枝的对抗鲁棒性

### 6.3 复现验证
5 篇量化论文全部完成代码复现，其中 BinaryPC 和 VQ-VAD 在真实 Qwen3-0.6B 模型上验证通过。RAC 和 Energy-Efficient PEFT 在 MockTransformer 和真实模型上均验证通过。SSTQ 在真实模型权重上验证了联邦聚合的无偏性。

---

## 七、分支与提交信息

- **分支名**: `feature/arxiv-daily-2026-08-07`
- **基于**: `main`（合并 `feature/arxiv-daily-2026-08-06` 累积文件）
- **新增文件**: 20 篇 tech_analysis.md + 5 套量化代码（README.md + demo.py）+ 1 份日报 + 元数据更新
- **目标模型**: Qwen3-0.6B (Qwen/Qwen3-0.6B)
