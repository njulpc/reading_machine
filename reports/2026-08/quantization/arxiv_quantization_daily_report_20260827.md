# arXiv 模型压缩论文日报（2026-08-27）

**检索窗口**：2026-08-25 00:00 至 2026-08-27 23:59（Asia/Shanghai；按 `/abs` Submission history 的 v1 日期归日）
**官方来源**：cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`，含 new submissions、cross-lists 与 replacements。

## 1. 结论速览

- 逐日相关：2026-08-25 为 22 篇，2026-08-26 为 23 篇，2026-08-27 为 0 篇（截至运行时 arXiv 官方网页未检出）。
- 窗口相关总数 45；历史重复 15；本次新增 30。
- 扫描 27 个远端历史日更分支，真实已分析规范 ID 269 个；metadata-only 的 3 个 ID 未计完成。

## 2. 官方列表覆盖审计

| 分类 | 入口 | 页面总数 | 日期/分组 | 完整性 |
|---|---|---:|---|---|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 308 | 2026-08-27:105；2026-08-27:83；2026-08-27:120 | 通过 |
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 873 | 2026-08-27:188；2026-08-26:155；2026-08-25:291；2026-08-24:112；2026-08-21:127 | 通过 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 182 | 2026-08-27:69；2026-08-27:39；2026-08-27:74 | 通过 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 564 | 2026-08-27:108；2026-08-26:89；2026-08-25:204；2026-08-24:87；2026-08-21:76 | 通过 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 173 | 2026-08-27:90；2026-08-27:17；2026-08-27:66 | 通过 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 642 | 2026-08-27:107；2026-08-26:112；2026-08-25:234；2026-08-24:103；2026-08-21:86 | 通过 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 351 | 2026-08-27:55；2026-08-27:154；2026-08-27:142 | 通过 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1144 | 2026-08-27:209；2026-08-26:228；2026-08-25:362；2026-08-24:200；2026-08-21:145 | 通过 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 18 | 2026-08-27:7；2026-08-27:3；2026-08-27:8 | 通过 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 53 | 2026-08-27:10；2026-08-26:9；2026-08-25:16；2026-08-24:6；2026-08-21:12 | 通过 |

十页声明总数、实际条目数和组内计数全部一致，且均低于 `show=2000`。合并得到 2,666 个跨分类唯一 ID；当前五个 new 页合并 720 个唯一 ID，标题/摘要 720/720 完整。recent 完整覆盖 8 月 27、26、25，并以 8 月 24 与 21 日作为窗口外阳性对照。30 篇新增均读取官方 v1 HTML 全文。

公告页日期不等于 v1 日期：本轮广义候选中 2608.24904 的 v1 为 7 月 17 日，2608.24936 为 8 月 23 日，2608.24938/2608.24945 为 8 月 24 日，均按窗口规则排除。

## 3. 历史去重审计

- 去重来源分支数：27。
- 历史真实 `tech_analysis.md` 规范 ID：269。
- metadata 交叉核验为 272 个 ID；2607.27951、2607.28410、2607.28457 没有真实精读，不计完成。
- 8 月 25 日的 15 个重复 ID 全部来自 `origin/feature/arxiv-daily-2026-08-27`：2608.23962, 2608.23987, 2608.24063, 2608.24070, 2608.24114, 2608.24173, 2608.24207, 2608.24293, 2608.24310, 2608.24469, 2608.24615, 2608.24646, 2608.24674, 2608.24696, 2608.24759。
- 本次新增 30 个 ID 与历史已分析集合交集为空。

## 4. 本次新增论文

| 日期 | ID | 方向 | 标题 | 效果 | 压缩 | 创新 | 复现 | 评分依据 |
|---|---|---|---|---:|---:|---:|---:|---|
| 2026-08-25 | [2608.24973](https://arxiv.org/abs/2608.24973) | 剪枝/稀疏 | Resource-Efficient Pruning for Transformer via Low-Rank Importance Estimation | 8 | 8 | 8 | 8 | REP-LIE 用 LoRA 低秩梯度近似全权重重要性，并以稳定度控制迭代剪枝，使 Transformer 剪枝不再依赖全参数梯度。 |
| 2026-08-25 | [2608.24987](https://arxiv.org/abs/2608.24987) | 知识蒸馏 | D$^3$-MOPD: Adaptive Dynamic Domain ScheDuling for Efficient Multi-Teacher Distillation | 9 | 7 | 8 | 8 | D³-MOPD 用训练中现成的逐域 reverse-KL 轨迹动态调度多教师数据比例，把蒸馏算力从已饱和域转移到仍有提升空间的域。 |
| 2026-08-25 | [2608.25037](https://arxiv.org/abs/2608.25037) | 知识蒸馏 | Retrieve, Match, Escalate: Accurate and Scalable Product Linking with VLM-Distilled Cross-Encoders and Agentic VLMs | 8 | 7 | 8 | 7 | 该生产级级联把双 VLM 共识标签蒸馏进廉价 cross-encoder，只把难例升级到 agentic VLM，以分层模型容量控制实体匹配成本。 |
| 2026-08-25 | [2608.25053](https://arxiv.org/abs/2608.25053) | 量化 | Hydra: Phase-Aware Workload Characterization of LLM Inference across Edge SoC Generations, Backends, and Quantization Levels | 8 | 6 | 8 | 9 | Hydra 说明边缘 LLM 的量化收益必须按 prefill/decode、后端和 SoC 世代拆开测量；位宽降低通常减内存流量和能耗，但不能单独预测功率。 |
| 2026-08-25 | [2608.25068](https://arxiv.org/abs/2608.25068) | 剪枝/稀疏 | SHIFT-LLM: Distribution Shift Correction in Depth-Pruned LLMs | 9 | 8 | 9 | 8 | SHIFT-LLM 在被删 Transformer block 位置插入可闭式标定的残差适配器，直接修复深度剪枝造成的隐藏分布错位。 |
| 2026-08-25 | [2608.25188](https://arxiv.org/abs/2608.25188) | 量化 | Transforms for LLM Quantization: The Great Inversion and Format Co-Design | 9 | 7 | 9 | 8 | 该综述以“Great Inversion”统一解释量化前变换：可变码率变换编码偏好能量集中，而共享尺度硬件量化偏好组内展平。 |
| 2026-08-25 | [2608.25230](https://arxiv.org/abs/2608.25230) | 其他压缩与高效推理 | Trust the Mass: Forced Weights in KV-Cache Eviction | 9 | 9 | 9 | 8 | 这项大规模审计发现 KV eviction 的选择算法已接近上限，真正决定内存与质量的往往是掩码存储、预算是否强制以及查询泄漏。 |
| 2026-08-26 | [2608.25332](https://arxiv.org/abs/2608.25332) | 剪枝/稀疏 | Not All Attention Heads Contribute to Critical Visual Token Selection: Head-Aware Pruning Matters More | 9 | 9 | 8 | 9 | ProViP 先判断哪些注意力头真正擅长定位关键视觉证据，再用这些头逐层剪 token，避免全头平均稀释信号。 |
| 2026-08-26 | [2608.25354](https://arxiv.org/abs/2608.25354) | 其他压缩与高效推理 | Escaping Low-Dimensional Overlap: Multi-Task Model Merging via High-Dimensional Sparse Disentanglement | 8 | 7 | 8 | 7 | 该方法把 task vector 投到高维稀疏 SAE 空间后再合并，以特征级解缠缓解多任务模型合并中的参数叠加冲突。 |
| 2026-08-26 | [2608.25356](https://arxiv.org/abs/2608.25356) | 知识蒸馏 | Where to Look Matters: On-Policy Self-Distillation for Long-Video Understanding | 8 | 6 | 8 | 7 | Clue-OPSD 用训练时可见的短线索区间充当特权自教师，让推理仍读完整视频的学生学会聚焦相关片段且无需额外模块。 |
| 2026-08-26 | [2608.25380](https://arxiv.org/abs/2608.25380) | 量化 | APT: Accelerating Diffusion Transformers via Attention Probability-Guided Pruning and Quantization | 9 | 9 | 9 | 6 | APT 用预测的注意力概率同时决定元素是否剪除和剩余元素的精度，再以软硬件协同执行不规则稀疏与双精度 DiT attention。 |
| 2026-08-26 | [2608.25386](https://arxiv.org/abs/2608.25386) | 剪枝/稀疏 | Efficient Training with Foresight: Multi-Token Auxiliary Supervision for Autoregressive Image Generation | 8 | 7 | 8 | 7 | MTAR 把多 token 预测、token 对比正则和语义 token dropping 合在训练期，提高自回归图像模型的监督密度并减少低信息计算。 |
| 2026-08-26 | [2608.25539](https://arxiv.org/abs/2608.25539) | 量化 | CropCop: An Auditable 120-Class Plant-Health Model from Benchmark Reconstruction to a Quantised Runtime Artifact | 9 | 7 | 8 | 9 | CropCop 的价值不在新量化器，而在把数据去重、验证集 PTQ、转换后 INT8 图与最终 PTE 文件逐层审计到可执行工件。 |
| 2026-08-26 | [2608.25542](https://arxiv.org/abs/2608.25542) | 其他压缩与高效推理 | Reflection Steering: Disentangling Reflection from Reasoning in Activation Space for Token-Efficient Inference | 8 | 7 | 8 | 7 | Reflection Steering 在激活空间分离反思、普通推理和长度方向，只抑制冗余复查而不粗暴截断整条思维链。 |
| 2026-08-26 | [2608.25564](https://arxiv.org/abs/2608.25564) | 剪枝/稀疏 | Physics-Informed Foresight Pruning for Sparse PINN Solvers of Nonlinear PDEs | 8 | 7 | 8 | 8 | PI-SAP 用 PDE residual 对参数的敏感度做初始化剪枝，补足只看网络输出 NTK 时忽略物理导数约束的问题。 |
| 2026-08-26 | [2608.25575](https://arxiv.org/abs/2608.25575) | 知识蒸馏 | MLLMCLIP: Feature-Level Distillation of MLLM for Robust Vision-Language Representations | 8 | 6 | 8 | 7 | MLLMCLIP 直接把生成式多模态大模型的逐层特征蒸馏给判别式 CLIP，省去 LLM→T2I 合成 hard negatives 的昂贵级联。 |
| 2026-08-26 | [2608.25583](https://arxiv.org/abs/2608.25583) | 其他压缩与高效推理 | GRIP: Granular Reward-Guided Parameter Interpolation for Efficient Reasoning | 8 | 6 | 8 | 7 | GRIP 只学习同架构 reasoning model 与 instruction model 的模块级插值系数，把两份检查点合并成一个更简洁的推理模型。 |
| 2026-08-26 | [2608.25643](https://arxiv.org/abs/2608.25643) | 知识蒸馏 | A Token-Level Analysis of Sampled-Token Reverse-KL On-Policy Distillation | 8 | 5 | 9 | 8 | 该工作把 sampled-token reverse-KL 的梯度拆成师生概率差与学生置信度因子，解释低概率 token 为何主导 on-policy distillation 更新。 |
| 2026-08-26 | [2608.25692](https://arxiv.org/abs/2608.25692) | 知识蒸馏 | CloSeR: Unified Relational Distillation from Closed-Set Teachers for Category Discovery | 8 | 5 | 8 | 8 | CloSeR 让轻量 closed-set teacher 只提供全局 prototype 与局部邻域关系，避免在开放类别发现中直接覆盖 noisy pseudo-label。 |
| 2026-08-26 | [2608.25741](https://arxiv.org/abs/2608.25741) | 知识蒸馏 | Why Does Graph Learning Fail to Fully Benefit from a Text Teacher? | 7 | 4 | 8 | 8 | 这篇负结果分析说明文本教师与图学生即使余弦对齐更强，也可能因目标空间、图传播和源几何约束冲突而无法改善分类边界。 |
| 2026-08-26 | [2608.25761](https://arxiv.org/abs/2608.25761) | 其他压缩与高效推理 | Beam Search, Self-Consistency, and the Limits of Inference-Time Scaling for Grammar-Constrained Text-to-SQL in Small Language Models | 8 | 7 | 7 | 9 | 该研究发现语法约束 Text-to-SQL 中，用更小 4-bit 模型换更宽搜索通常不如直接换大模型，beam search 又比等预算 sample-and-vote 更有效。 |
| 2026-08-26 | [2608.25836](https://arxiv.org/abs/2608.25836) | 知识蒸馏 | Socialized Detector Learning: Trajectory-Guided and Reciprocal Distillation for Heterogeneous Object Detectors | 9 | 6 | 9 | 7 | TGRD 先按估计的教师间转移难度规划 carrier 路径逐步吸收异构检测器知识，再把联合类别能力反向蒸馏回各专家。 |
| 2026-08-26 | [2608.25936](https://arxiv.org/abs/2608.25936) | 知识蒸馏 | One Symptom, Three Levers: A Critical Review of On-Policy Self-Distillation | 7 | 4 | 8 | 9 | 该综述把 on-policy self-distillation 的 collapse 统一为三个可控杠杆：信号施加位置、教师可见的特权信息、以及教师随训练变化的时机。 |
| 2026-08-26 | [2608.25941](https://arxiv.org/abs/2608.25941) | 剪枝/稀疏 | When Pruning Meets Interpretability: Preserving Sparse Autoencoder Robustness in LLMs | 8 | 7 | 9 | 8 | 该研究用协方差加权的 perturbation energy 解释剪枝后 SAE 可解释性为何退化，并据此把更多稀疏预算留给敏感中层。 |
| 2026-08-26 | [2608.25977](https://arxiv.org/abs/2608.25977) | 量化 | When Personality Meets Quantization: A Layer-wise MBTI Analysis of Quantized LLMs | 8 | 6 | 8 | 8 | 这项层级行为审计发现 4-bit GPTQ/AWQ 大体保持粗粒度 MBTI 结构，而 2-bit AQLM 更容易破坏 prompt 一致性和跨精度一致。 |
| 2026-08-26 | [2608.26019](https://arxiv.org/abs/2608.26019) | 知识蒸馏 | DualOPSD: Adaptive Privileged Teachers for On-Policy Self-Distillation | 9 | 5 | 8 | 8 | DualOPSD 让 privileged teacher 在每轮学生更新后沿同一轨迹向学生分布靠拢，以零额外 rollout 的交替更新修复固定教师失配。 |
| 2026-08-26 | [2608.26049](https://arxiv.org/abs/2608.26049) | 知识蒸馏 | RTLGuard: A Lightweight Teacher-Student Defense for Poisoned RTL Code Generation Models | 8 | 5 | 8 | 7 | RTLGuard 用少量可信 RTL 训练小型 clean teacher，再以特征与知识蒸馏清洗被投毒的代码生成目标模型，避免全参数重训。 |
| 2026-08-26 | [2608.26052](https://arxiv.org/abs/2608.26052) | 其他压缩与高效推理 | How Much Rank Does LoRA Need? Rank-Error Bounds for Transformer Attention | 8 | 6 | 9 | 7 | 该理论用下游加权谱尾能量 T_r 给出 Transformer attention 的 LoRA rank—函数误差上下界，并证明 softmax 饱和会让所需函数 rank 小于 logit rank。 |
| 2026-08-26 | [2608.26069](https://arxiv.org/abs/2608.26069) | 其他压缩与高效推理 | Group-Shared Low-Rank Approximation for Mobile-Efficient Pointwise Convolutions in Large-Kernel CNNs | 8 | 8 | 8 | 8 | CGS 对 large-kernel CNN 中真正占参数主导的 pointwise convolution 做组共享低秩分解，用共享投影加组专属对角缩放降低存储。 |
| 2026-08-26 | [2608.26070](https://arxiv.org/abs/2608.26070) | 其他压缩与高效推理 | Prefix Sliding for efficient test-time scaling | 9 | 9 | 8 | 8 | Prefix Sliding 在长推理中永久保留系统前缀和最近窗口、丢弃中间旧 token，使 KV 内存不再随思维链长度线性增长。 |

评分为 1–10 的相对审阅分：效果依据质量/效率增益与对照强度；压缩依据真实资源减少与口径；创新依据方法区分度；复现依据算法、配置、数据和硬件可获得性。

## 5. 量化复现

5 篇量化论文均在 `scripts/quantization/<id>/` 提供 README 与 demo.py，并以 Qwen3-0.6B 做真实权重或真实前向小规模验证。大规模多 SoC 测量、专用 DiT accelerator、MBTI 全基准和移动端 PTE 未伪造，边界在各 README 单独列明。

## 6. 零结果说明

2026-08-27 只能写作“截至运行时 arXiv 官方网页未检出”。五个 recent 页都有 2026-08-27 日期组且组计数完整，但语义筛选后的相关候选详情页 v1 日期最晚为 2026-08-26；后续运行仍由三天窗口回查公告延迟。
