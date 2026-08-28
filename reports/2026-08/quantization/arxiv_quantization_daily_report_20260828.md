# arXiv 模型压缩论文日报（2026-08-28）

**检索窗口**：2026-08-26 00:00 至 2026-08-28 23:59（Asia/Shanghai；按 `/abs` Submission history 的 v1 日期归日）
**官方来源**：cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`，完整覆盖 new submissions、cross-lists 与 replacements。

## 1. 结论速览

- 逐日相关：2026-08-26 为 28 篇，2026-08-27 为 33 篇，2026-08-28 为 0 篇（截至运行时 arXiv 官方网页未检出）。
- 窗口相关总数 61；历史重复 23；本次新增 38。
- 扫描 28 个远端历史日更分支，真实已分析规范 ID 299 个；metadata-only 的 3 个 ID 未计完成。
- 当前公告补出了 5 篇 v1=2026-08-26 的相关论文，体现三日回查避免公告/交叉列表延迟漏检。

## 2. 官方列表覆盖审计

| 分类 | 入口 | 页面总数 | 日期/分组 | 完整性 |
|---|---|---:|---|---|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 252 | 2026-08-28:77；2026-08-28:80；2026-08-28:95 | 通过 |
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 903 | 2026-08-28:157；2026-08-27:188；2026-08-26:155；2026-08-25:291；2026-08-24:112 | 通过 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 236 | 2026-08-28:118；2026-08-28:36；2026-08-28:82 | 通过 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 642 | 2026-08-28:154；2026-08-27:108；2026-08-26:89；2026-08-25:204；2026-08-24:87 | 通过 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 184 | 2026-08-28:93；2026-08-28:21；2026-08-28:70 | 通过 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 670 | 2026-08-28:114；2026-08-27:107；2026-08-26:112；2026-08-25:234；2026-08-24:103 | 通过 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 312 | 2026-08-28:96；2026-08-28:100；2026-08-28:116 | 通过 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1195 | 2026-08-28:196；2026-08-27:209；2026-08-26:228；2026-08-25:362；2026-08-24:200 | 通过 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 12 | 2026-08-28:6；2026-08-28:3；2026-08-28:3 | 通过 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 50 | 2026-08-28:9；2026-08-27:10；2026-08-26:9；2026-08-25:16；2026-08-24:6 | 通过 |

十页的声明总数、实际条目数与组内计数全部一致，且都低于 `show=2000`，无需额外分页。跨分类合并为 2,785 个唯一 ID；五个当前 new 页为 728 个唯一 ID，标题/摘要 728/728 完整。recent 完整覆盖 8 月 28、27、26，并以 8 月 25、24 日作为窗口外阳性对照。38 篇新增的 `/abs` 和官方 HTML 全文全部成功读取。

## 3. 历史去重审计

- 去重来源分支数：28。
- 历史真实 `tech_analysis.md` 规范 ID：299。
- metadata 交叉核验为 302 个 ID；2607.27951、2607.28410、2607.28457 没有真实精读，不计完成。
- 23 个历史重复都来自 `origin/feature/arxiv-daily-2026-08-28`，v1 日期均为 2026-08-26：2608.25332, 2608.25354, 2608.25356, 2608.25380, 2608.25386, 2608.25539, 2608.25542, 2608.25564, 2608.25575, 2608.25583, 2608.25643, 2608.25692, 2608.25741, 2608.25761, 2608.25836, 2608.25936, 2608.25941, 2608.25977, 2608.26019, 2608.26049, 2608.26052, 2608.26069, 2608.26070。
- 本次新增 38 个 ID 与历史已分析集合交集为空。

## 4. 本次新增论文

| 日期 | ID | 方向 | 标题 | 效果 | 压缩 | 创新 | 复现 | 评分依据 |
|---|---|---|---|---:|---:|---:|---:|---|
| 2026-08-26 | [2608.26206](https://arxiv.org/abs/2608.26206) | 量化 | Ankhdjet: An Open-Source Compiler for Mask-Programmed Ternary Compute-in-ROM on an Open PDK | 8 | 9 | 9 | 7 | Ankhdjet 把 BitNet b1.58 等三值检查点编译成开放 SKY130 PDK 的掩膜可编程 Compute-in-ROM，打通权重到版图的可审计链路。 |
| 2026-08-26 | [2608.26220](https://arxiv.org/abs/2608.26220) | 其他压缩与高效推理 | MeshReduce-U: Compiler-Guided Communication Reduction for Irregular Neural Reductions on Mesh NoCs | 9 | 8 | 9 | 7 | MeshReduce-U 在 NoC 路由前先重写可结合的神经网络归约流量，证明减少载波比在原始通信图上继续搜索更有效。 |
| 2026-08-26 | [2608.26233](https://arxiv.org/abs/2608.26233) | 量化 | Pruning Binarized Neural Networks: A Dedicated Framework and Globally Weighted Algorithms | 9 | 9 | 8 | 8 | 该工作为已二值化网络设计跨层全局加权剪枝，使剪枝率真正超过通用策略在 BNN 上的硬件收益上限。 |
| 2026-08-26 | [2608.26374](https://arxiv.org/abs/2608.26374) | 其他压缩与高效推理 | Survival-Guided Length Control for Efficient Diffusion Language Models | 9 | 8 | 8 | 9 | 该方法把扩散语言模型的终止长度视为离散生存过程，用训练免费插件避免固定长度造成的无效去噪。 |
| 2026-08-26 | [2608.26389](https://arxiv.org/abs/2608.26389) | 其他压缩与高效推理 | LowRankArena: A Standardized Evaluation Platform for SVD-Based LLM Compression | 9 | 8 | 9 | 9 | LowRankArena 用统一预算、任务版本和推理测量审计 SVD 压缩，显示论文间榜首很大程度受协议影响。 |
| 2026-08-27 | [2608.26550](https://arxiv.org/abs/2608.26550) | 知识蒸馏 | SPEAR: Distilling Domain-Adaptive Reasoning Skeletons via Sequential Symbolic Alignment in Reinforcement Learning | 8 | 5 | 8 | 8 | SPEAR 把教师自然语言轨迹投影成领域自适应符号里程碑，再用 LCS 给学生探索提供无需神经 PRM 的稠密顺序奖励。 |
| 2026-08-27 | [2608.26556](https://arxiv.org/abs/2608.26556) | 其他压缩与高效推理 | Dynamical phase selection controls compute scaling in looped transformers | 8 | 7 | 9 | 6 | 该理论指出权重共享的 looped Transformer 即便架构和准确率相同，也会因训练落入不同动力学相而呈现完全不同的 test-time compute 尾部。 |
| 2026-08-27 | [2608.26574](https://arxiv.org/abs/2608.26574) | 其他压缩与高效推理 | Dependency-Aware Revocable Decoding for Efficient Diffusion Large Language Model Inference | 9 | 8 | 8 | 8 | DARD 在扩散解码中把候选 token 与已确认 token 分开，并排除不可靠上下文做复核，从而同时改善速度和质量。 |
| 2026-08-27 | [2608.26580](https://arxiv.org/abs/2608.26580) | 其他压缩与高效推理 | Visual Information-Guided Parallel Decoding for Diffusion Multimodal Large Language Models | 9 | 8 | 8 | 8 | VIG-Sampler 用视觉注意力和多样性约束选择并行解码 token，避免只按置信度优先生成高频但低信息词。 |
| 2026-08-27 | [2608.26581](https://arxiv.org/abs/2608.26581) | 量化 | Activation Outliers Matter: Robust Recovery for Quantized Multimodal LLMs | 9 | 8 | 9 | 7 | RFQ 识别出多模态模型 4-bit 退化主要来自激活，并用额外低比特残差通路补偿主量化表示。 |
| 2026-08-27 | [2608.26641](https://arxiv.org/abs/2608.26641) | 其他压缩与高效推理 | Information-Guided Frontier Decoding: Contextual Utility-Driven Commitment in dMLLMs | 8 | 6 | 8 | 8 | IGFD 用置信度、邻域不确定性和结构风险共同决定 dMLLM 的提交前沿，在不增加 forward 的前提下先生成可靠语义锚点。 |
| 2026-08-27 | [2608.26650](https://arxiv.org/abs/2608.26650) | 剪枝/稀疏 | Meta-Learning Where to Allocate Experts: Task-Conditioned Layer-Wise Compression for MoEs | 9 | 9 | 9 | 8 | MetaNet 用小型 support-set 控制器按任务和层预测专家保留阈值，在冻结 MoE 下动态减少激活专家。 |
| 2026-08-27 | [2608.26676](https://arxiv.org/abs/2608.26676) | 剪枝/稀疏 | FOCUS & RePAIR: Mitigating Text Degeneration via Token-Level Guidance for Pruned Large Language Models | 9 | 6 | 9 | 8 | FOCUS 与 RePAIR 不只恢复剪枝后的 perplexity，而是针对重复循环的进入风险和持续性做 token 级蒸馏修复。 |
| 2026-08-27 | [2608.26684](https://arxiv.org/abs/2608.26684) | 知识蒸馏 | Reason in the Words You Speak: Idiolectal Paraphrasing Off-Policy Traces for Reasoning Distillation in VideoLLMs | 8 | 5 | 9 | 7 | Echo-GRPO 先把强教师的离策略推理改写成学生自己的措辞，再做视频推理蒸馏，缓解低概率关键 token 被梯度裁剪。 |
| 2026-08-27 | [2608.26720](https://arxiv.org/abs/2608.26720) | 其他压缩与高效推理 | Parameter Efficient Continual Learning for Sparse Event-Based Transformers | 8 | 7 | 8 | 8 | sLoTh 冻结稀疏事件 Transformer，只更新低秩注意力与共享神经元阈值，使持续学习兼顾低参数更新和事件驱动能耗。 |
| 2026-08-27 | [2608.26735](https://arxiv.org/abs/2608.26735) | 知识蒸馏 | Preserving General Capabilities during Domain Specialization with Uncertainty-Calibrated MOPD | 9 | 5 | 9 | 8 | 该 MOPD 通过双温度扩展轨迹，再用优势密度与熵校准教师认可度筛 token，减少领域专化对通用能力的破坏。 |
| 2026-08-27 | [2608.26771](https://arxiv.org/abs/2608.26771) | 知识蒸馏 | Cross-Architecture Knowledge Distillation from a Vision Foundation Model to a Lightweight Visual State Space Model for Tea Leaf Disease Classification | 9 | 9 | 8 | 9 | 该工作把 DINOv2 教师跨架构蒸馏到 4.45M 参数双向视觉状态空间学生，并发现简单 logit KD 胜过特征对齐。 |
| 2026-08-27 | [2608.26806](https://arxiv.org/abs/2608.26806) | 剪枝/稀疏 | Multi-Image Visual Token Pruning in Large Visual Language Models | 9 | 9 | 8 | 9 | AVTP 不依赖 attention score，按架构选择剪枝层并按多图重要性动态分配视觉 token，兼容 FlashAttention。 |
| 2026-08-27 | [2608.26848](https://arxiv.org/abs/2608.26848) | 其他压缩与高效推理 | MedFG-VQA: Low-Frequency Memory and Graph Attention for Lightweight Medical VQA | 8 | 7 | 7 | 7 | MedFG-VQA 用 DCT 低频记忆与图增强交叉注意构建轻量医疗 VQA，在小算力下替代大 VLM。 |
| 2026-08-27 | [2608.26872](https://arxiv.org/abs/2608.26872) | 知识蒸馏 | Self-OPD: On-Policy Distillation for Flow Matching Models without Teacher | 8 | 4 | 8 | 7 | Self-OPD 不训练专用教师，而把 flow matching 学生的随机分支 rollout 相对确定性自基线的优势变成逐步监督。 |
| 2026-08-27 | [2608.26926](https://arxiv.org/abs/2608.26926) | 量化 | A Layer Importance Metric for Quantization Accounting for the Speed-Quality Trade-off in Autoregressive Models | 8 | 8 | 8 | 9 | 该指标把模拟量化的 SQNR 信息保留与 roofline 速度收益合成层优先级，避免小模型按统一位宽量化。 |
| 2026-08-27 | [2608.26948](https://arxiv.org/abs/2608.26948) | 其他压缩与高效推理 | KISS-GS: 3D Gaussian Splatting Compression Kept Simple | 9 | 10 | 8 | 8 | KISS-GS 把 3DGS 剪枝、二维属性编码和可选微调解耦，得到可由 Web 原生图片格式解码的高倍率场景压缩。 |
| 2026-08-27 | [2608.26949](https://arxiv.org/abs/2608.26949) | 其他压缩与高效推理 | A Table Is Worth 64 Tokens: Pixel-level Compression for Multi-Table Document Question Answering | 9 | 9 | 9 | 9 | 该方法先用高度像素压缩的表格只做相关性筛选，再以原分辨率读取少数相关表，避免低清表格诱发更长推理抵消 token 节省。 |
| 2026-08-27 | [2608.26958](https://arxiv.org/abs/2608.26958) | 知识蒸馏 | Scaling Model-Generated Distillation Data Can Make Latent Teacher Traits More Recoverable | 8 | 4 | 9 | 8 | 这项受控研究发现生成式蒸馏数据越多，学生越容易恢复教师隐蔽特质，即便样本离题且从未显式提及该特质。 |
| 2026-08-27 | [2608.26965](https://arxiv.org/abs/2608.26965) | 其他压缩与高效推理 | ClusterAttention: A training-free speedup of bidirectional attention | 9 | 9 | 9 | 8 | ClusterAttention 用快速递归聚类构造固定 2 次幂大小的块稀疏注意力，并以被排除簇质心补偿误差。 |
| 2026-08-27 | [2608.26973](https://arxiv.org/abs/2608.26973) | 其他压缩与高效推理 | Squeezing More from Limited Data with Recursive Transformers | 8 | 8 | 8 | 7 | 递归 Transformer 通过跨深度共享 block、因式分解 embedding，把有限数据下的参数容量与每 token 计算量解耦。 |
| 2026-08-27 | [2608.27065](https://arxiv.org/abs/2608.27065) | 知识蒸馏 | Video-OPSD: Exploiting Privileged Visual Evidence for On-Policy Self-Distillation in Video Large Language Models | 8 | 6 | 8 | 7 | Video-OPSD 让自教师只看标注证据帧、学生看完整视频，并按 token 对证据的依赖程度加权蒸馏。 |
| 2026-08-27 | [2608.27128](https://arxiv.org/abs/2608.27128) | 其他压缩与高效推理 | TwinKV: A Composable Repair Pass for KV Cache Eviction via Pairwise Key Redundancy | 9 | 9 | 9 | 8 | TwinKV 不重写现有 eviction scorer，而是在固定预算内用 key 近重复性把被误删的孤儿 token 与冗余 donor 交换。 |
| 2026-08-27 | [2608.27198](https://arxiv.org/abs/2608.27198) | 知识蒸馏 | Knowledge Distillation Driven Semantic NOMA with GAN Refinement for 6G Robotic Vehicle Networks | 8 | 6 | 7 | 6 | KDG-SemNOMA 用正交传输教师蒸馏 NOMA 学生，再以条件 GAN 修复语义通信的过平滑图像。 |
| 2026-08-27 | [2608.27206](https://arxiv.org/abs/2608.27206) | 剪枝/稀疏 | PACE: A Unified Condense-and-Extract Paradigm for Fast VLM Inference | 9 | 10 | 9 | 9 | PACE 在视觉编码前先按像素信息密度下采样，再在编码后融合视觉与语言信号剪 token，同时压缩 encoder 与 LLM 两段成本。 |
| 2026-08-27 | [2608.27241](https://arxiv.org/abs/2608.27241) | 剪枝/稀疏 | Importance Scoring of Transformer Attention Heads in Learning Tabular Data | 8 | 7 | 7 | 8 | 该工作用头重要性分数指导 tabular Transformer 的 attention-head removal，并显示低分头先删最稳。 |
| 2026-08-27 | [2608.27254](https://arxiv.org/abs/2608.27254) | 其他压缩与高效推理 | Circuit Condensation: Post-Training that Concentrates a Behavior's Causal Circuit | 9 | 8 | 9 | 7 | Circuit Condensation 交替剪低 attribution 边并用 LoRA 重训，把同一行为主动集中进更小的可验证因果图。 |
| 2026-08-27 | [2608.27339](https://arxiv.org/abs/2608.27339) | 其他压缩与高效推理 | Beyond Parallel Blindness: Information Floors and Model Gaps in Block Drafting | 9 | 7 | 9 | 8 | 该研究把 block drafter 的拒绝拆成不可消除的信息下界和可由模型改进的 gap，避免只用 accepted length 混淆两者。 |
| 2026-08-27 | [2608.27370](https://arxiv.org/abs/2608.27370) | 其他压缩与高效推理 | Puro-2B: Poor Lab's Qwen2-1.5B Trained on RTX 5090 within $5090 | 8 | 7 | 8 | 8 | Puro-2B 给出消费级 RTX 5090 上从零训练 2B 模型的开放配方，FP8、优化器与数据课程共同降低预训练成本。 |
| 2026-08-27 | [2608.27395](https://arxiv.org/abs/2608.27395) | 剪枝/稀疏 | LeVJEPA: Efficient & Scalable Video Pretraining without the Heuristics | 9 | 9 | 9 | 8 | LeVJEPA 用可证明防坍塌的单 encoder 目标替代教师—学生非对称，并以随机 token dropping 同时降低视频预训练计算和提高准确率。 |
| 2026-08-27 | [2608.27409](https://arxiv.org/abs/2608.27409) | 知识蒸馏 | Consolidating RLVR Capabilities Across Domains: A Deep Dive into Fusion Paradigms | 9 | 7 | 9 | 9 | 该研究在共享专家和数据下统一比较 task-vector merge、混合 RL 与多教师 OPD，给出多域能力整合的成本选择规则。 |
| 2026-08-27 | [2608.27413](https://arxiv.org/abs/2608.27413) | 其他压缩与高效推理 | Scaling Graph Neural Networks for Friend Recommendation: Multi-Hash User Embeddings and Temporal Neighbor Sampling | 9 | 10 | 8 | 8 | 生产 GNN 用 multi-hash 把超大用户 embedding 表缩小 98% 以上，并用按时间排序 CSR 加速邻居采样。 |
| 2026-08-27 | [2608.27448](https://arxiv.org/abs/2608.27448) | 知识蒸馏 | TTPO: Test-Time Policy Optimization | 9 | 4 | 9 | 7 | TTPO 在测试时把同意伪标签的 rollout 用 OPSD 蒸馏、不同意的用 grouped RL 惩罚，并在 token 级规避错误多数票。 |

评分均为 1–10 的相对审阅分：效果看质量/效率增益与对照强度；压缩看真实资源减少与口径；创新看方法区分度；复现看算法、配置、数据和硬件可获得性。

## 5. 量化复现

4 篇以量化为主要贡献的新增论文（2608.26206、2608.26233、2608.26581、2608.26926）均在 `scripts/quantization/<id>/` 提供 README 与 demo.py，并用 Qwen3-0.6B 做真实权重/小张量验证。Puro-2B 的 FP8 是低成本预训练配方中的组件而非新量化算法，归入“其他压缩与高效推理”，不伪称复现其 1.4T-token 训练。

## 6. 零结果与时效边界

2026-08-28 只能写作“截至运行时 arXiv 官方网页未检出”。五个 recent 页均有 2026-08-28 公告组且计数完整，但经 `/abs` 核验的相关候选 v1 最晚为 2026-08-27；后续运行继续用三天窗口回查。
