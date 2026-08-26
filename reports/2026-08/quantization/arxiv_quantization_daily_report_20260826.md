# arXiv 模型压缩论文日报（2026-08-26）

**检索窗口**：2026-08-24 00:00 至 2026-08-26 23:59（Asia/Shanghai；按 `/abs` v1 时间归日）
**官方来源**：cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`，含 new submissions、cross-lists、replacements。

## 1. 结论速览

- 逐日相关：2026-08-24 为 22 篇，2026-08-25 为 15 篇，2026-08-26 为 0 篇（截至本次运行时官方网页未检出）。
- 窗口相关总数 37；历史重复 10；本次新增 27。
- 历史去重扫描 26 个远端日更分支，真实已分析 ID 242 个；metadata-only 的 3 个 ID 未计完成。

## 2. 官方列表覆盖审计

| 分类 | 入口 | 页面总数 | 日期分组 | 完整性 |
|---|---|---:|---|---|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 277 | 2026-08-26 New:85；Cross:70；Replacement:122 | 通过 |
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 854 | 2026-08-26:155；2026-08-25:291；2026-08-24:112；2026-08-21:127；2026-08-20:169 | 通过 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 163 | 2026-08-26 New:53；Cross:36；Replacement:74 | 通过 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 555 | 2026-08-26:89；2026-08-25:204；2026-08-24:87；2026-08-21:76；2026-08-20:99 | 通过 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 194 | 2026-08-26 New:95；Cross:17；Replacement:82 | 通过 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 629 | 2026-08-26:112；2026-08-25:234；2026-08-24:103；2026-08-21:86；2026-08-20:94 | 通过 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 352 | 2026-08-26 New:117；Cross:111；Replacement:124 | 通过 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1121 | 2026-08-26:228；2026-08-25:362；2026-08-24:200；2026-08-21:145；2026-08-20:186 | 通过 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 14 | 2026-08-26 New:9；Replacement:5（Cross:0） | 通过 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 51 | 2026-08-26:9；2026-08-25:16；2026-08-24:6；2026-08-21:12；2026-08-20:8 | 通过 |

十页合并 2,618 个唯一 ID；本次 new 批次 744 个唯一 ID，标题/摘要 744/744 完整。recent 还显示 2026-08-21 与 2026-08-20 的相邻阳性日期组。27 篇新增均读取官方全文，其中 25 篇为 HTML、2 篇为 PDF。

## 3. 历史去重审计

- 去重来源分支数：26。
- 历史真实 `tech_analysis.md` 规范 ID：242。
- metadata 交叉核验：245 个 ID；其中 2607.27951、2607.28410、2607.28457 没有真实精读，未计完成。
- 2026-08-24 的 10 个重复 ID 全部来自 `origin/feature/arxiv-daily-2026-08-26`：2608.22704, 2608.22745, 2608.22854, 2608.22963, 2608.23018, 2608.23048, 2608.23144, 2608.23167, 2608.23253, 2608.23296。
- 最终新增集合与历史已分析集合交集为空。

## 4. 本次新增论文

| 日期 | ID | 方向 | 标题 | 效果 | 压缩 | 创新 | 复现 | 评分依据 |
|---|---|---|---|---:|---:|---:|---:|---|
| 2026-08-24 | [2608.23744](https://arxiv.org/abs/2608.23744) | 剪枝/稀疏 | Calibration-Preserving Pruning: Compression as a Reliability Contract | 8 | 7 | 8 | 8 | 把稀疏化从“尽量保准确率”改写为“经独立 conformal 校准后尽量缩小预测集”，让模型压缩与可靠性目标直接对齐。 |
| 2026-08-24 | [2608.23752](https://arxiv.org/abs/2608.23752) | 知识蒸馏 | Too much of a good thing -- when knowledge distillation promotes overfitting, and how to avoid it | 8 | 6 | 8 | 8 | 中间层蒸馏并非越多越好：经典充足数据上末层监督常已足够，细粒度少样本任务才真正受益于额外中间蒸馏点。 |
| 2026-08-24 | [2608.23794](https://arxiv.org/abs/2608.23794) | 剪枝/稀疏 | Mixture of Channel Experts: Static Sparse Supports with Input-Adaptive Mixing for Pointwise Projections | 8 | 7 | 9 | 8 | 用训练后固定的稀疏通道支持替代稠密 1x1 投影，只让输入动态调节混合温度，在精度、稀疏性和实际延迟之间取得更稳的折中。 |
| 2026-08-24 | [2608.23816](https://arxiv.org/abs/2608.23816) | 量化 | AQLoRA: A Zero-Search Recipe for Fast Quantized LoRA Fine-Tuning | 8 | 7 | 8 | 9 | 用一次无数据 CPU 权重扫描自动决定 QLoRA 中保留 FP16 的层数和适配位置，换取可复现的训练加速；关键收益来自保护层数量，而非误差排序本身。 |
| 2026-08-24 | [2608.23834](https://arxiv.org/abs/2608.23834) | 量化 | Minima-KV: Retention-Preserving KV Cache Compression with Mixed-Format Paged Attention | 8 | 9 | 9 | 6 | Minima-KV 以 FP8 保存近期/锚点页、以打包 TQ3 保存旧页，并让异构格式直接参加统一 softmax，避免保留稠密影子缓存。 |
| 2026-08-24 | [2608.23841](https://arxiv.org/abs/2608.23841) | 其他压缩与高效推理 | Pipeline-Native Transformers: Co-Designing Model Architecture and CPU Inference for Bandwidth-Efficient Autoregressive Decode | 7 | 8 | 9 | 6 | 通过共同设计 Transformer 层间依赖和 CPU 执行顺序，把单 token 解码改造成垂直流水，减少每 token 必须从内存读取的活跃权重。 |
| 2026-08-24 | [2608.23843](https://arxiv.org/abs/2608.23843) | 其他压缩与高效推理 | PuzzleKV: Page-Wise Low-Rank Decomposition for KV Cache Compression | 8 | 9 | 9 | 7 | PuzzleKV 在页粒度独立做低秩分解，并直接对稠密页与因子化页计算注意力，使压缩粒度同时适配局部统计与 paged serving。 |
| 2026-08-24 | [2608.23850](https://arxiv.org/abs/2608.23850) | 知识蒸馏 | DDMS: Discriminative Distillation of Multi-view Foundational Features into Single-view Models | 8 | 6 | 8 | 7 | 把多视角几何模型内部的 3D 一致知识蒸馏到单图编码器，在保持原基础模型语义空间的同时增强跨视角对应能力。 |
| 2026-08-24 | [2608.23879](https://arxiv.org/abs/2608.23879) | 知识蒸馏 | Spatiotemporal Distillation via Recurrent Bottlenecks for Aortic Tracking | 8 | 5 | 8 | 7 | 以空间教师监督带循环瓶颈的时空学生，在不增加标注的情况下消除 cine-MRI 逐帧跟踪掉线。 |
| 2026-08-24 | [2608.23880](https://arxiv.org/abs/2608.23880) | 知识蒸馏 | LG-GER: Language-Guided Group Emotion Recognition via Multimodal Evidence Distillation | 8 | 6 | 8 | 8 | 训练时让 MLLM 生成带框、情绪标签和置信度的密集证据，蒸馏后推理只保留单流 VLM，从而去掉检测器和多流融合。 |
| 2026-08-24 | [2608.23911](https://arxiv.org/abs/2608.23911) | 知识蒸馏 | PROOF-Gen: From Optimized Data to Better Distillation | 9 | 6 | 9 | 7 | 不再丢弃教师失败轨迹，而是针对每个失败场景优化提示把近失误修成可通过轨迹，再移除脚手架训练学生。 |
| 2026-08-24 | [2608.23921](https://arxiv.org/abs/2608.23921) | 剪枝/稀疏 | HAP: Head-Adaptive Visual Token Pruning via Cross-Modal Alignment | 9 | 10 | 9 | 9 | 依据各注意力头与文本查询的跨模态对齐质量自适应融合打分，再按层组预算剪除视觉 token，避免坏头淹没细粒度证据。 |
| 2026-08-25 | [2608.23962](https://arxiv.org/abs/2608.23962) | 其他压缩与高效推理 | More GPUs or a Smaller Cache? Tensor Parallelism versus KV Compression for Memory-Bound LLM Serving | 7 | 8 | 8 | 8 | 把 tensor parallel 与 KV 压缩放到同一成本轴后发现二者不是替代关系：前者解决权重可行性和延迟，后者主要扩大单卡并发容量。 |
| 2026-08-25 | [2608.23987](https://arxiv.org/abs/2608.23987) | 剪枝/稀疏 | Low-Latency Activation-Regularized Sparse Neural Operators with Distillation Assistance Towards Real-Time Edge-Deployable Virtual Sensing | 8 | 8 | 8 | 7 | 以单步 Sparse-Activation-ReLU 替代多步脉冲神经元，并用合成知识蒸馏进一步降低边缘虚拟传感的误差-延迟-能耗综合指标。 |
| 2026-08-25 | [2608.24063](https://arxiv.org/abs/2608.24063) | 剪枝/稀疏 | VisCache: Visual KV Cache Pruning for Efficient Vision Large Language Model Inference | 8 | 9 | 8 | 8 | 先用轻量视觉模型过滤冗余关键帧，再按 VLLM 层级注意力动态剪 key 并融合 value，实现视频 KV cache 的粗到细压缩。 |
| 2026-08-25 | [2608.24070](https://arxiv.org/abs/2608.24070) | 其他压缩与高效推理 | Compression Trinity: Exploring Sparsity, Quantization, and Low-Rank Approximations for LLM Compression | 9 | 9 | 9 | 7 | “Compression Trinity”把稀疏、量化和低秩恢复作为同一优化问题，分别作用于优化器、训练图和后训练压缩，避免单技术的精度-效率天花板。 |
| 2026-08-25 | [2608.24114](https://arxiv.org/abs/2608.24114) | 知识蒸馏 | AHEAD: Adaptive Hindsight with Environment-Augmented Distillation for Agentic RL | 9 | 6 | 8 | 8 | AHEAD 按步骤类型分配特权信息：普通步骤只给环境反馈，关键错误步骤再给纠错提示，使 agent 自蒸馏的密集监督与错误位置对齐。 |
| 2026-08-25 | [2608.24173](https://arxiv.org/abs/2608.24173) | 量化 | SandwichQuant: Which Parameters Matter Before and After Quantization? | 9 | 7 | 9 | 8 | SandwichQuant 发现归一化 affine 参数是低维但高杠杆的量化修正子空间，分别在 PTQ 前后短暂优化以增强鲁棒性和修补冻结图残差。 |
| 2026-08-25 | [2608.24207](https://arxiv.org/abs/2608.24207) | 量化 | PRQ-KMeans: Projection Residual Quantization for Semantic ID Tokenization | 8 | 8 | 8 | 8 | PRQ-KMeans 把多级语义 ID 看作逐级移除公共分量：先去全局均值，再以 Top-k 软更新码本，并用投影残差避免下一层重复编码同方向。 |
| 2026-08-25 | [2608.24293](https://arxiv.org/abs/2608.24293) | 其他压缩与高效推理 | Keep-or-Drop? Adaptive Tokenizer for Compact Video Representation | 8 | 9 | 9 | 6 | KATok 让视频 VAE 为每个 token 学习 keep/drop 概率，以内容复杂度决定压缩率，并显式修复稀疏 token 引起的时空位置错位。 |
| 2026-08-25 | [2608.24310](https://arxiv.org/abs/2608.24310) | 知识蒸馏 | OPDSearch+: On-Policy Distillation with RL Refinement for Search-Augmented Reasoning | 9 | 6 | 8 | 8 | 先用冻结通用教师做 on-policy forward-KL，建立搜索分解与证据整合行为，再用 RL 突破教师上限，比同时优化两个目标更稳定。 |
| 2026-08-25 | [2608.24469](https://arxiv.org/abs/2608.24469) | 量化 | Low-Rank Ternary Adaptation for Fine-Tuning Transformers | 8 | 9 | 9 | 7 | 以两个小型 ternary 矩阵的低秩 Kronecker 因子表示符号翻转/置零更新，使三值 Transformer 微调后仍能直接合并为三值权重。 |
| 2026-08-25 | [2608.24615](https://arxiv.org/abs/2608.24615) | 量化 | Quantization Effects on Bangla Language Understanding in Large Language Models: A Systematic Evaluation | 9 | 7 | 7 | 9 | Bangla NLU 上量化稳健性主要由模型家族和格式决定，而不是简单由位宽决定：Qwen/LLaMA 的 GPTQ 稳定，GPT-OSS 的 GGUF-W8A16 可严重退化。 |
| 2026-08-25 | [2608.24646](https://arxiv.org/abs/2608.24646) | 知识蒸馏 | On-Policy Self-Distillation in Diffusion Models | 9 | 5 | 9 | 8 | DiffusionOPSD 把图像级奖励梯度转成同一 query 上的有界正负 clean-output 目标，使扩散 RL 的中间去噪更新变得可监督、可诊断。 |
| 2026-08-25 | [2608.24674](https://arxiv.org/abs/2608.24674) | 知识蒸馏 | TurboT2VA: Fast Large-Scale Text-to-Video-Audio Generation via Score-Regularized Consistency Distillation | 9 | 10 | 9 | 7 | TurboT2VA 用逐阶段一致性蒸馏把 19B 联合视频-音频生成器压到四步，并叠加 W8A8、文本压紧和模态感知稀疏注意力。 |
| 2026-08-25 | [2608.24696](https://arxiv.org/abs/2608.24696) | 知识蒸馏 | On-policy Distillation with Verifiable Reward | 8 | 5 | 8 | 8 | OPDVR 用一个无新增超参的 ReLU gate，让 sampled-token 蒸馏的隐式奖励符号与整条轨迹正确性一致，从而自然兼容 RLVR/GRPO。 |
| 2026-08-25 | [2608.24759](https://arxiv.org/abs/2608.24759) | 知识蒸馏 | IDeaL: Data-Free Multi-Teacher Distillation via Improved Dead Leaves | 8 | 6 | 9 | 8 | IDeaL 在无真实数据时用教师本身优化 structured noise，通过图像级和 patch 级去相关生成各教师互补的蒸馏样本。 |

评分为 1–10 的相对审阅分：效果看论文报告的质量/效率增益与对照强度；压缩看真实资源减少及口径完整性；创新看方法与既有工作的区分；复现看算法、代码/配置和所需硬件数据的可获得性。

## 5. 量化复现

本次 6 篇量化论文均提供 `scripts/quantization/<id>/README.md` 与 `demo.py`，统一以 Qwen3-0.6B 本地 checkpoint 做真实权重或真实 KV/隐藏表示验证；未复现大规模训练、专用 GPU kernel 与论文硬件吞吐的部分会在各 README 明示。

## 6. 零结果说明

2026-08-26 写作“截至运行时 arXiv 官方网页未检出”。这不是永久零结果；后续三天窗口会自动回查公告延迟。五个 recent 页均出现 2026-08-26 日期组，页面总数、分组声明与实际条目一致，且以 2026-08-21/20 可见条目作为相邻阳性对照。
