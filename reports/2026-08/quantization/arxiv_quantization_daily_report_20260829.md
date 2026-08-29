# arXiv 模型压缩论文日报（2026-08-29）

**检索窗口**：2026-08-27 00:00 至 2026-08-29 23:59（Asia/Shanghai；按 `/abs` Submission history 的 v1 日期归日）
**官方来源**：cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`，完整覆盖 new submissions、cross-lists 与 replacements。

## 1. 结论速览

- 逐日相关：2026-08-27 为 33 篇，2026-08-28 为 0 篇，2026-08-29 为 0 篇；后两日均为“截至运行时 arXiv 官方网页未检出”。
- 窗口相关总数 33；历史重复 33；本次新增 0。公开相关并非 0，而是全部已在历史日更分支完成精读。
- 扫描 29 个远端历史日更分支，真实已分析规范 ID 337 个；metadata-only 的 3 个 ID 未计完成。
- 33 篇重复全部来自 `origin/feature/arxiv-daily-2026-08-29`，本分支不复制其精读或复现。

## 2. 官方列表覆盖审计

| 分类 | 入口 | 页面总数 | 日期/分组 | 实际覆盖 | 完整性 |
|---|---|---:|---|---:|---|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 252 | 08-28 new 77 / cross 80 / replacement 95 | 252 | 通过 |
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 903 | 08-28:157；08-27:188；08-26:155；08-25:291；08-24:112 | 903 | 通过 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 236 | 08-28 new 118 / cross 36 / replacement 82 | 236 | 通过 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 642 | 08-28:154；08-27:108；08-26:89；08-25:204；08-24:87 | 642 | 通过 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 184 | 08-28 new 93 / cross 21 / replacement 70 | 184 | 通过 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 670 | 08-28:114；08-27:107；08-26:112；08-25:234；08-24:103 | 670 | 通过 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 312 | 08-28 new 96 / cross 100 / replacement 116 | 312 | 通过 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1195 | 08-28:196；08-27:209；08-26:228；08-25:362；08-24:200 | 1195 | 通过 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 12 | 08-28 new 6 / cross 3 / replacement 3 | 12 | 通过 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 50 | 08-28:9；08-27:10；08-26:9；08-25:16；08-24:6 | 50 | 通过 |

十页的声明总数、实际条目数与组内计数全部一致，且均低于 `show=2000`，无需额外分页。跨分类合并为 2,785 个唯一 ID；五个当前 new 页合并为 728 个唯一 ID，标题和摘要均完整。recent 完整覆盖窗口相关公告日，并以 8 月 26、25、24 日作为窗口外阳性对照。候选详情页重新核验时，标题、摘要、分类及 Submission history 均可解析；相关候选 v1 最晚为 2026-08-27。

## 3. 历史去重审计

- 去重来源分支数：29。
- 历史真实 `tech_analysis.md` 规范 ID：337。
- metadata 交叉核验为 340 个 ID；2607.27951、2607.28410、2607.28457 没有真实精读，不计完成。
- 排除的 33 个规范 ID：2608.26550、2608.26556、2608.26574、2608.26580、2608.26581、2608.26641、2608.26650、2608.26676、2608.26684、2608.26720、2608.26735、2608.26771、2608.26806、2608.26848、2608.26872、2608.26926、2608.26948、2608.26949、2608.26958、2608.26965、2608.26973、2608.27065、2608.27128、2608.27198、2608.27206、2608.27241、2608.27254、2608.27339、2608.27370、2608.27395、2608.27409、2608.27413、2608.27448。
- 每个重复 ID 的真实 `tech_analysis.md` 均位于 `origin/feature/arxiv-daily-2026-08-29`；本次最终新增集合为空，与历史集合交集为空。

## 4. 窗口相关论文（全部为历史重复）

| v1 日期 | ID | 方向 | 标题 | 效果 | 压缩 | 创新 | 复现 | 评分依据 |
|---|---|---|---|---:|---:|---:|---:|---|
| 2026-08-27 | [2608.26550](https://arxiv.org/abs/2608.26550) | 知识蒸馏 | SPEAR: Distilling Domain-Adaptive Reasoning Skeletons via Sequential Symbolic Alignment in Reinforcement Learning | 8 | 5 | 8 | 8 | 符号里程碑与 LCS 为学生探索提供顺序奖励。 |
| 2026-08-27 | [2608.26556](https://arxiv.org/abs/2608.26556) | 其他 | Dynamical phase selection controls compute scaling in looped transformers | 8 | 7 | 9 | 6 | 权重共享架构的动力学相决定 test-time compute 尾部。 |
| 2026-08-27 | [2608.26574](https://arxiv.org/abs/2608.26574) | 其他 | Dependency-Aware Revocable Decoding for Efficient Diffusion Large Language Model Inference | 9 | 8 | 8 | 8 | 可撤销候选与可靠上下文改善扩散解码效率和质量。 |
| 2026-08-27 | [2608.26580](https://arxiv.org/abs/2608.26580) | 其他 | Visual Information-Guided Parallel Decoding for Diffusion Multimodal Large Language Models | 9 | 8 | 8 | 8 | 视觉注意力与多样性联合指导并行 token 选择。 |
| 2026-08-27 | [2608.26581](https://arxiv.org/abs/2608.26581) | 量化 | Activation Outliers Matter: Robust Recovery for Quantized Multimodal LLMs | 9 | 8 | 9 | 7 | 低比特残差通路补偿 4-bit 多模态激活异常值。 |
| 2026-08-27 | [2608.26641](https://arxiv.org/abs/2608.26641) | 其他 | Information-Guided Frontier Decoding: Contextual Utility-Driven Commitment in dMLLMs | 8 | 6 | 8 | 8 | 不增加 forward 地优先提交可靠语义锚点。 |
| 2026-08-27 | [2608.26650](https://arxiv.org/abs/2608.26650) | 剪枝/稀疏 | Meta-Learning Where to Allocate Experts: Task-Conditioned Layer-Wise Compression for MoEs | 9 | 9 | 9 | 8 | 按任务和层动态保留冻结 MoE 的专家。 |
| 2026-08-27 | [2608.26676](https://arxiv.org/abs/2608.26676) | 剪枝/稀疏 | FOCUS & RePAIR: Mitigating Text Degeneration via Token-Level Guidance for Pruned Large Language Models | 9 | 6 | 9 | 8 | token 级蒸馏修复剪枝后的重复退化。 |
| 2026-08-27 | [2608.26684](https://arxiv.org/abs/2608.26684) | 知识蒸馏 | Reason in the Words You Speak: Idiolectal Paraphrasing Off-Policy Traces for Reasoning Distillation in VideoLLMs | 8 | 5 | 9 | 7 | 将强教师轨迹改写为学生措辞后再蒸馏。 |
| 2026-08-27 | [2608.26720](https://arxiv.org/abs/2608.26720) | 其他 | Parameter Efficient Continual Learning for Sparse Event-Based Transformers | 8 | 7 | 8 | 8 | 低秩注意力与共享阈值兼顾更新参数和事件能耗。 |
| 2026-08-27 | [2608.26735](https://arxiv.org/abs/2608.26735) | 知识蒸馏 | Preserving General Capabilities during Domain Specialization with Uncertainty-Calibrated MOPD | 9 | 5 | 9 | 8 | 不确定性校准 MOPD 降低领域专化遗忘。 |
| 2026-08-27 | [2608.26771](https://arxiv.org/abs/2608.26771) | 知识蒸馏 | Cross-Architecture Knowledge Distillation from a Vision Foundation Model to a Lightweight Visual State Space Model for Tea Leaf Disease Classification | 9 | 9 | 8 | 9 | DINOv2 蒸馏到 4.45M 参数视觉状态空间学生。 |
| 2026-08-27 | [2608.26806](https://arxiv.org/abs/2608.26806) | 剪枝/稀疏 | Multi-Image Visual Token Pruning in Large Visual Language Models | 9 | 9 | 8 | 9 | 动态分配多图视觉 token 且兼容 FlashAttention。 |
| 2026-08-27 | [2608.26848](https://arxiv.org/abs/2608.26848) | 其他 | MedFG-VQA: Low-Frequency Memory and Graph Attention for Lightweight Medical VQA | 8 | 7 | 7 | 7 | DCT 低频记忆与图交叉注意构建轻量医疗 VQA。 |
| 2026-08-27 | [2608.26872](https://arxiv.org/abs/2608.26872) | 知识蒸馏 | Self-OPD: On-Policy Distillation for Flow Matching Models without Teacher | 8 | 4 | 8 | 7 | 无专用教师的 flow matching 自蒸馏。 |
| 2026-08-27 | [2608.26926](https://arxiv.org/abs/2608.26926) | 量化 | A Layer Importance Metric for Quantization Accounting for the Speed-Quality Trade-off in Autoregressive Models | 8 | 8 | 8 | 9 | SQNR 与 roofline 收益联合确定逐层量化优先级。 |
| 2026-08-27 | [2608.26948](https://arxiv.org/abs/2608.26948) | 其他 | KISS-GS: 3D Gaussian Splatting Compression Kept Simple | 9 | 10 | 8 | 8 | 解耦 3DGS 剪枝、属性编码和微调。 |
| 2026-08-27 | [2608.26949](https://arxiv.org/abs/2608.26949) | 其他 | A Table Is Worth 64 Tokens: Pixel-level Compression for Multi-Table Document Question Answering | 9 | 9 | 9 | 9 | 压缩表格只做检索，原分辨率读取少量相关表。 |
| 2026-08-27 | [2608.26958](https://arxiv.org/abs/2608.26958) | 知识蒸馏 | Scaling Model-Generated Distillation Data Can Make Latent Teacher Traits More Recoverable | 8 | 4 | 9 | 8 | 更多生成式蒸馏数据增强隐蔽教师特质恢复。 |
| 2026-08-27 | [2608.26965](https://arxiv.org/abs/2608.26965) | 其他 | ClusterAttention: A training-free speedup of bidirectional attention | 9 | 9 | 9 | 8 | 聚类块稀疏注意力用簇质心补偿遗漏信息。 |
| 2026-08-27 | [2608.26973](https://arxiv.org/abs/2608.26973) | 其他 | Squeezing More from Limited Data with Recursive Transformers | 8 | 8 | 8 | 7 | 跨深度共享 block 解耦参数容量与每 token 计算。 |
| 2026-08-27 | [2608.27065](https://arxiv.org/abs/2608.27065) | 知识蒸馏 | Video-OPSD: Exploiting Privileged Visual Evidence for On-Policy Self-Distillation in Video Large Language Models | 8 | 6 | 8 | 7 | 自教师读取证据帧并按 token 证据依赖加权。 |
| 2026-08-27 | [2608.27128](https://arxiv.org/abs/2608.27128) | 其他 | TwinKV: A Composable Repair Pass for KV Cache Eviction via Pairwise Key Redundancy | 9 | 9 | 9 | 8 | 用成对 key 冗余修复固定预算 KV eviction。 |
| 2026-08-27 | [2608.27198](https://arxiv.org/abs/2608.27198) | 知识蒸馏 | Knowledge Distillation Driven Semantic NOMA with GAN Refinement for 6G Robotic Vehicle Networks | 8 | 6 | 7 | 6 | 正交教师蒸馏 NOMA 学生并用 GAN 修复图像。 |
| 2026-08-27 | [2608.27206](https://arxiv.org/abs/2608.27206) | 剪枝/稀疏 | PACE: A Unified Condense-and-Extract Paradigm for Fast VLM Inference | 9 | 10 | 9 | 9 | 同时减少视觉编码器像素与 LLM 视觉 token 成本。 |
| 2026-08-27 | [2608.27241](https://arxiv.org/abs/2608.27241) | 剪枝/稀疏 | Importance Scoring of Transformer Attention Heads in Learning Tabular Data | 8 | 7 | 7 | 8 | 头重要性分数指导 tabular Transformer 删头。 |
| 2026-08-27 | [2608.27254](https://arxiv.org/abs/2608.27254) | 其他 | Circuit Condensation: Post-Training that Concentrates a Behavior's Causal Circuit | 9 | 8 | 9 | 7 | 交替剪边与 LoRA 重训压缩行为因果图。 |
| 2026-08-27 | [2608.27339](https://arxiv.org/abs/2608.27339) | 其他 | Beyond Parallel Blindness: Information Floors and Model Gaps in Block Drafting | 9 | 7 | 9 | 8 | 分离 block drafting 的信息下界和模型 gap。 |
| 2026-08-27 | [2608.27370](https://arxiv.org/abs/2608.27370) | 其他 | Puro-2B: Poor Lab's Qwen2-1.5B Trained on RTX 5090 within $5090 | 8 | 7 | 8 | 8 | FP8 与消费级 GPU 配方降低 2B 预训练门槛。 |
| 2026-08-27 | [2608.27395](https://arxiv.org/abs/2608.27395) | 剪枝/稀疏 | LeVJEPA: Efficient & Scalable Video Pretraining without the Heuristics | 9 | 9 | 9 | 8 | 随机 token dropping 同时降算力并提升准确率。 |
| 2026-08-27 | [2608.27409](https://arxiv.org/abs/2608.27409) | 知识蒸馏 | Consolidating RLVR Capabilities Across Domains: A Deep Dive into Fusion Paradigms | 9 | 7 | 9 | 9 | 统一比较 task-vector merge、混合 RL 与多教师 OPD。 |
| 2026-08-27 | [2608.27413](https://arxiv.org/abs/2608.27413) | 其他 | Scaling Graph Neural Networks for Friend Recommendation: Multi-Hash User Embeddings and Temporal Neighbor Sampling | 9 | 10 | 8 | 8 | multi-hash 把用户 embedding 表缩小 98% 以上。 |
| 2026-08-27 | [2608.27448](https://arxiv.org/abs/2608.27448) | 知识蒸馏 | TTPO: Test-Time Policy Optimization | 9 | 4 | 9 | 7 | 同意 rollout 做自蒸馏、不同意 rollout 做 grouped RL。 |

评分为 1–10 的相对审阅分：效果看质量/效率增益与对照强度；压缩看真实资源减少与口径；创新看方法区分度；复现看算法、配置、数据和硬件可获得性。评分沿用对应历史精读的证据口径，本次不重复生成分析。

## 5. 新增成果与复现

本次新增论文为 0，因此 `papers/` 仅保留说明文件，`scripts/quantization/` 不存在；没有新增量化论文，也没有需要执行的 Qwen3-0.6B 复现。历史精读与历史复现均未复制到本分支。

## 6. 零结果与时效边界

2026-08-28 和 2026-08-29 均只能表述为“截至运行时 arXiv 官方网页未检出”。五个分类页的最新公告组为 2026-08-28；当前相关候选的 `/abs` v1 最晚为 2026-08-27。后续运行仍需用三天窗口回查，以覆盖公告延迟。
