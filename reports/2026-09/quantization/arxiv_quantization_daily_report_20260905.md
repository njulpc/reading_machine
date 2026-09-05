# arXiv 模型压缩与量化日报 — 2026-09-05

运行时间：2026-09-06T01:15:14+08:00。运行日 R=2026-09-06；固定回查窗口为 **2026-09-03、09-04、09-05 三个完整北京时间自然日**。

**结论：窗口相关 38 篇，历史重复 37 篇，本次新增 1 篇（知识蒸馏），新增量化 0 篇。** 09-05 截至运行时 arXiv 官方网页未检出；这不是最终投稿数量为零的声明。

## 检索与覆盖证据

五分类 new/recent 十页均以 `show=2000` 完整下载，包含 new submissions、cross-lists，并额外保留 replacements 供回溯。所有页面声明总数与实际解析条目数相等且小于 2000，因此各页首个 show 覆盖已穷尽，无后续分页。合并为 3087 个规范 ID；本次重新下载 3087/3087 个官方 /abs，标题、摘要、主/交叉分类及 v1 全部解析成功。未使用 arXiv 官方 API 或 submittedDate API 查询。

| 分类 | new：声明=实际 | new/交叉/替换分组 | recent：声明=实际 | recent 日期分组及各日条目数 |
|---|---:|---|---:|---|
| cs.LG | [272](https://arxiv.org/list/cs.LG/new?show=2000) | New submissions (showing 85 of 85 entries)；Cross submissions (showing 83 of 83 entries)；Replacement submissions (showing 104 of 104 entries) | [985](https://arxiv.org/list/cs.LG/recent?show=2000) | Fri, 4 Sep 2026 (showing 168 of 168 entries )；Thu, 3 Sep 2026 (showing 159 of 159 entries )；Wed, 2 Sep 2026 (showing 202 of 202 entries )；Tue, 1 Sep 2026 (showing 336 of 336 entries )；Mon, 31 Aug 2026 (showing 120 of 120 entries ) |
| cs.CL | [183](https://arxiv.org/list/cs.CL/new?show=2000) | New submissions (showing 75 of 75 entries)；Cross submissions (showing 40 of 40 entries)；Replacement submissions (showing 68 of 68 entries) | [781](https://arxiv.org/list/cs.CL/recent?show=2000) | Fri, 4 Sep 2026 (showing 115 of 115 entries )；Thu, 3 Sep 2026 (showing 101 of 101 entries )；Wed, 2 Sep 2026 (showing 185 of 185 entries )；Tue, 1 Sep 2026 (showing 298 of 298 entries )；Mon, 31 Aug 2026 (showing 82 of 82 entries ) |
| cs.CV | [175](https://arxiv.org/list/cs.CV/new?show=2000) | New submissions (showing 102 of 102 entries)；Cross submissions (showing 10 of 10 entries)；Replacement submissions (showing 63 of 63 entries) | [809](https://arxiv.org/list/cs.CV/recent?show=2000) | Fri, 4 Sep 2026 (showing 112 of 112 entries )；Thu, 3 Sep 2026 (showing 136 of 136 entries )；Wed, 2 Sep 2026 (showing 152 of 152 entries )；Tue, 1 Sep 2026 (showing 316 of 316 entries )；Mon, 31 Aug 2026 (showing 93 of 93 entries ) |
| cs.AI | [269](https://arxiv.org/list/cs.AI/new?show=2000) | New submissions (showing 69 of 69 entries)；Cross submissions (showing 96 of 96 entries)；Replacement submissions (showing 104 of 104 entries) | [1250](https://arxiv.org/list/cs.AI/recent?show=2000) | Fri, 4 Sep 2026 (showing 165 of 165 entries )；Thu, 3 Sep 2026 (showing 162 of 162 entries )；Wed, 2 Sep 2026 (showing 309 of 309 entries )；Tue, 1 Sep 2026 (showing 424 of 424 entries )；Mon, 31 Aug 2026 (showing 190 of 190 entries ) |
| cs.AR | [10](https://arxiv.org/list/cs.AR/new?show=2000) | New submissions (showing 4 of 4 entries)；Cross submissions (showing 5 of 5 entries)；Replacement submissions (showing 1 of 1 entries) | [46](https://arxiv.org/list/cs.AR/recent?show=2000) | Fri, 4 Sep 2026 (showing 9 of 9 entries )；Thu, 3 Sep 2026 (showing 10 of 10 entries )；Wed, 2 Sep 2026 (showing 12 of 12 entries )；Tue, 1 Sep 2026 (showing 10 of 10 entries )；Mon, 31 Aug 2026 (showing 5 of 5 entries ) |

窗口外相邻日期阳性对照：北京时间 09-02 可见 **425** 个 v1 条目；例如 [2609.01456](https://arxiv.org/abs/2609.01456) 为 2026-09-01T16:00:25Z / 2026-09-02T00:00:25+08:00。recent 同时显示 08-31、09-01、09-02 分组，证明列表覆盖超出窗口下界。列表最新公告仍为 09-04；用 /abs 的 v1 而非公告日期归日。

### 语义审阅与边界复核

本次十页 HTML 与 09-05 扫描逐字节一致；3087 条官方摘要重新下载后，标题、摘要、v1、主分类及分类字段也逐条相同。因此复用前次全量语义审阅作为初始判断，并额外阅读 74 篇窗口内尚无历史分析的边界候选摘要，结合四篇官方全文复核；不是用关键词筛掉其余记录，也未把未重做的独立审阅说成本次新完成。该复核发现并补录 Uno。证据未变化并不意味着历史筛选必然正确，三日回查仍可修正语义漏项。

关键词仅作审阅排序和交叉复核：quantization、quantize/quantise、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache compression、mixed precision、GPTQ、AWQ，以及低秩、二值/三值、token 选择/合并、FP4/INT4/FP8/INT8 等同义表达。

| 边界候选 | 判定与证据 |
|---|---|
| [Uno / 2609.04010](https://arxiv.org/abs/2609.04010) | 纳入：PDF §3.2 明确冻结 AR 教师与 gated LoRA 学生的分布蒸馏；共享 KV 并减小独立草稿开销。归入知识蒸馏，基座未压缩，BF16 不构成量化创新。 |
| [MSFD / 2609.03446](https://arxiv.org/html/2609.03446v1) | 排除：§3 与结论以先前模型监督当前同构模型，目标为持续深伪检测的抗遗忘；未提供压缩学生、推理资源减少或模型压缩实验。频率掩码用于蒸馏损失，不是部署剪枝。 |
| [Cliff / 2609.02817](https://arxiv.org/html/2609.02817v1) | 排除：教师标识第一处推理错误，转换为 GRPO token advantage；核心是奖励塑形，不是教师分布蒸馏或压缩部署。 |
| [Matrix-CODI / 2609.03090](https://arxiv.org/pdf/2609.03090) | 排除：研究潜在矩阵的 rank 干预和位置无关混淆；摘要/正文中的低秩消融不是模型权重压缩，也没有相应部署收益。 |
| Tree-VQ / 2609.03641；Spruce / 2609.03376 | 分别为图像码流压缩和检索索引二值编码，未压缩模型权重、计算图或模型内部推理缓存。 |
| FReSH-IR / 2609.02839；SPARK / 2609.03813 | 前者为重新设计轻量恢复架构，后者增加稀疏通道控制器；未对既有模型执行压缩。轻量、稀疏、参数更少本身不作为纳入依据。 |

## 逐日计数与去重审计

逐日“原始相关”表示五分类合并后按规范 ID 去重、尚未排除历史完成项的语义相关数，不是分类页出现次数。

| v1 北京时间日期 | 所有主题可见条目 | 原始相关 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-09-03 | 359 | 28 | 27 | 1 |
| 2026-09-04 | 63 | 10 | 10 | 0 |
| 2026-09-05 | 0 | 0 | 0 | 0 |
| 合计 | 422 | 38 | 37 | 1 |

fetch 成功后逐一执行全部 **36** 个历史 `origin/feature/arxiv-daily-*` 分支的 `git ls-tree -r --name-only`，以真实 `papers/**/<id>/tech_analysis.md` 的规范 ID 建集合，共 **521** 个；逐分支读取 metadata JSON 交叉核验得到 524 个 metadata ID。仅 metadata 存在的 2607.27951、2607.28410、2607.28457 不计为已完成。当日分支创建前不存在，未混入历史集合。

历史扫描来源（完整 36 分支；均只读）：

- `origin/feature/arxiv-daily-2026-07-29`
- `origin/feature/arxiv-daily-2026-07-30`
- `origin/feature/arxiv-daily-2026-07-31`
- `origin/feature/arxiv-daily-2026-08-01`
- `origin/feature/arxiv-daily-2026-08-02`
- `origin/feature/arxiv-daily-2026-08-03`
- `origin/feature/arxiv-daily-2026-08-04`
- `origin/feature/arxiv-daily-2026-08-05`
- `origin/feature/arxiv-daily-2026-08-06`
- `origin/feature/arxiv-daily-2026-08-07`
- `origin/feature/arxiv-daily-2026-08-08`
- `origin/feature/arxiv-daily-2026-08-10`
- `origin/feature/arxiv-daily-2026-08-12`
- `origin/feature/arxiv-daily-2026-08-14`
- `origin/feature/arxiv-daily-2026-08-15`
- `origin/feature/arxiv-daily-2026-08-16`
- `origin/feature/arxiv-daily-2026-08-17`
- `origin/feature/arxiv-daily-2026-08-18`
- `origin/feature/arxiv-daily-2026-08-19`
- `origin/feature/arxiv-daily-2026-08-20`
- `origin/feature/arxiv-daily-2026-08-21`
- `origin/feature/arxiv-daily-2026-08-22`
- `origin/feature/arxiv-daily-2026-08-23`
- `origin/feature/arxiv-daily-2026-08-24`
- `origin/feature/arxiv-daily-2026-08-25`
- `origin/feature/arxiv-daily-2026-08-26`
- `origin/feature/arxiv-daily-2026-08-27`
- `origin/feature/arxiv-daily-2026-08-28`
- `origin/feature/arxiv-daily-2026-08-29`
- `origin/feature/arxiv-daily-2026-08-30`
- `origin/feature/arxiv-daily-2026-08-31`
- `origin/feature/arxiv-daily-2026-09-01`
- `origin/feature/arxiv-daily-2026-09-02`
- `origin/feature/arxiv-daily-2026-09-03`
- `origin/feature/arxiv-daily-2026-09-04`
- `origin/feature/arxiv-daily-2026-09-05`

## 完整相关论文表

历史条目仅在日报中记录去重证据，未复制其分析或复现。历史评分与摘要沿用其来源分支 metadata，精度/压缩/创新/可复现均为 1–10 主观分；其依据见链接的原分析。新增 Uno 的评分依据在下节给出。

| ID / 标题 | v1 UTC / 北京时间 | 方向；结论与评分依据 | 精度/压缩/创新/可复现 | 处理及来源 |
|---|---|---|---|---|
| [2609.02760 — Measurement-Driven Sub-Network Selection for On-Premise Retrieval-Augmented Factory Agents](https://arxiv.org/abs/2609.02760) | 2026-09-02T16:00:05Z / 2026-09-03T00:00:05+08:00 | ； | —/—/—/— | 历史重复；`origin/feature/arxiv-daily-2026-09-04` |
| [2609.02780 — ShallowStream: Index Shallow then Answer Deep for Streaming Video Understanding](https://arxiv.org/abs/2609.02780) | 2026-09-02T16:14:48Z / 2026-09-03T00:14:48+08:00 | ； | —/—/—/— | 历史重复；`origin/feature/arxiv-daily-2026-09-04` |
| [2609.02846 — UE5M3 FP4 Block Scaling for Stable Language Model Pretraining](https://arxiv.org/abs/2609.02846) | 2026-09-02T17:32:07Z / 2026-09-03T01:32:07+08:00 | ； | —/—/—/— | 历史重复；`origin/feature/arxiv-daily-2026-09-04` |
| [2609.02854 — MuyBridge: Mobile Human Center-of-Mass Estimation from Monocular Video via Sparse Fusion](https://arxiv.org/abs/2609.02854) | 2026-09-02T17:38:36Z / 2026-09-03T01:38:36+08:00 | quantization；MuyBridge 联合姿态裁剪、INT8量化和少步深度估计，实现手机端人体质心测量。 | 8/8/8/6 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.02854/tech_analysis.md) |
| [2609.02886 — SolarWM: Open Data and Scalable Training for Long-Horizon Video World Models](https://arxiv.org/abs/2609.02886) | 2026-09-02T17:59:41Z / 2026-09-03T01:59:41+08:00 | knowledge_distillation；SolarWM 以统一动作数据和分阶段蒸馏，把视频基础模型转为实时自回归世界模型。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.02886/tech_analysis.md) |
| [2609.02998 — Verify Before You Distill: Prompt-Level Teacher Gating for On-Policy Distillation](https://arxiv.org/abs/2609.02998) | 2026-09-02T17:54:09Z / 2026-09-03T01:54:09+08:00 | knowledge_distillation；先验证教师在当前提示上的可靠性，再决定蒸馏还是强化学习。 | 8/4/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.02998/tech_analysis.md) |
| [2609.03079 — LeanStream: A Speculate-and-Refine Streaming Framework for Efficient on-Device LLM Inference](https://arxiv.org/abs/2609.03079) | 2026-09-02T18:49:08Z / 2026-09-03T02:49:08+08:00 | pruning；LeanStream 用逐步修正的稀疏预测重叠权重读取与 GPU 计算。 | 7/9/8/6 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.03079/tech_analysis.md) |
| [2609.03100 — Distilling deep optical flow stereo methods to retrieve dense three-dimensional wind fields](https://arxiv.org/abs/2609.03100) | 2026-09-02T19:22:45Z / 2026-09-03T03:22:45+08:00 | knowledge_distillation；把多卫星立体光流教师迁移到单卫星学生，扩大三维风场覆盖。 | 7/5/7/6 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03100/tech_analysis.md) |
| [2609.03125 — A Time-Encoded Analog Photonic Interposer for Energy-EfficientIntegration of Analog Vision Sensors and Analog Accelerators](https://arxiv.org/abs/2609.03125) | 2026-09-02T20:01:11Z / 2026-09-03T04:01:11+08:00 | quantization；模拟光互连通过6位斜坡比较传递激活，减少模拟计算边界的数字转换。 | 8/7/8/5 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.03125/tech_analysis.md) |
| [2609.03158 — Who Speaks for the Pruned? Visual Token Pruning as Coverage Optimization](https://arxiv.org/abs/2609.03158) | 2026-09-02T20:51:02Z / 2026-09-03T04:51:02+08:00 | pruning；CoverPruner 将保留 token 选择改写为对全部视觉证据的代表性覆盖。 | 9/8/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.03158/tech_analysis.md) |
| [2609.03216 — ProgResViT: Progressive Resolution and Width for Adaptive Vision Transformers](https://arxiv.org/abs/2609.03216) | 2026-09-02T23:10:56Z / 2026-09-03T07:10:56+08:00 | pruning；ProgResViT 按图像难度逐轮增加分辨率和子网络宽度。 | 9/6/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.03216/tech_analysis.md) |
| [2609.03235 — SGD-KV: Summarization Guided KV Cache Compression](https://arxiv.org/abs/2609.03235) | 2026-09-03T00:31:11Z / 2026-09-03T08:31:11+08:00 | other；SGD-KV 用分块摘要诊断识别信息聚合头，再按头分配缓存。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03235/tech_analysis.md) |
| [2609.03355 — ALRA: Adaptive Local Relational Alignment for Logit-Based Pre-training Distillation of Autoregressive Language Models](https://arxiv.org/abs/2609.03355) | 2026-09-03T04:26:39Z / 2026-09-03T12:26:39+08:00 | knowledge_distillation；ALRA 同时对齐局部概率质量和候选 token 的相对关系。 | 8/7/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03355/tech_analysis.md) |
| [2609.03378 — When Depth Hurts: Reliability-Aware Geometry Distillation for Depth-Free RGB-D Salient Object Detection](https://arxiv.org/abs/2609.03378) | 2026-09-03T05:29:10Z / 2026-09-03T13:29:10+08:00 | knowledge_distillation；把深度基础模型的几何知识蒸馏进小分支，实现RGB-only显著目标检测。 | 8/6/7/6 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03378/tech_analysis.md) |
| [2609.03426 — Lngram v2: Latent N-Gram Memory with Interpretable Discrete Representations](https://arxiv.org/abs/2609.03426) | 2026-09-03T06:33:23Z / 2026-09-03T14:33:23+08:00 | other；Lngram v2 解耦离散记忆规模与骨干宽度，减少条件记忆扩展的参数和激活负担。 | 8/7/9/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03426/tech_analysis.md) |
| [2609.03430 — Random Attention: Rethinking KV Cache Eviction for Efficient Reasoning](https://arxiv.org/abs/2609.03430) | 2026-09-03T06:38:38Z / 2026-09-03T14:38:38+08:00 | other；保护提示后按头随机淘汰推理缓存，可接近复杂打分器。 | 8/7/9/9 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03430/tech_analysis.md) |
| [2609.03459 — FlowTT: Exploiting Computation Flow Reuse in Irregular Tensor-Train Embedding](https://arxiv.org/abs/2609.03459) | 2026-09-03T07:17:33Z / 2026-09-03T15:17:33+08:00 | other；FlowTT 面向张量列车嵌入表，用索引复用和融合执行降低查表开销。 | 8/7/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03459/tech_analysis.md) |
| [2609.03494 — GrowPage: On-Demand KV Budgeting for Efficient LLM Reasoning Serving](https://arxiv.org/abs/2609.03494) | 2026-09-03T07:53:05Z / 2026-09-03T15:53:05+08:00 | other；GrowPage 根据实时注意力需求，在压缩已有KV与申请新页之间决策。 | 8/8/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03494/tech_analysis.md) |
| [2609.03502 — Building and Evaluating Fixed-Voice Thai TTS from Synthetic Speech](https://arxiv.org/abs/2609.03502) | 2026-09-03T08:03:58Z / 2026-09-03T16:03:58+08:00 | knowledge_distillation；用大语音模型生成并筛选数据，训练82M固定声音泰语学生。 | 8/8/6/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03502/tech_analysis.md) |
| [2609.03515 — What Matters for Aggressive Decoding-Time KV Eviction? Temporal Aggregation and Ranking Preservation](https://arxiv.org/abs/2609.03515) | 2026-09-03T08:17:34Z / 2026-09-03T16:17:34+08:00 | other；InertiaKV 用注意力时间惯性降低KV排序更新开销。 | 8/7/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03515/tech_analysis.md) |
| [2609.03563 — FlashRender: Few-Step Generative Rendering via Camera-Controlled Video MeanFlow](https://arxiv.org/abs/2609.03563) | 2026-09-03T09:05:07Z / 2026-09-03T17:05:07+08:00 | knowledge_distillation；FlashRender 先稳定相机控制轨迹，再压缩视频生成采样步数。 | 8/9/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03563/tech_analysis.md) |
| [2609.03604 — On the Interaction Between Model Compression and Test-Time Adaptation](https://arxiv.org/abs/2609.03604) | 2026-09-03T09:49:29Z / 2026-09-03T17:49:29+08:00 | pruning；压缩后监督适应仍可成功，并不意味着无标签测试时适应也能恢复。 | 7/5/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.03604/tech_analysis.md) |
| [2609.03675 — CoFiE: Coarse-to-Fine Evidence Selection for Efficient Streaming Video Understanding](https://arxiv.org/abs/2609.03675) | 2026-09-03T11:14:21Z / 2026-09-03T19:14:21+08:00 | pruning；CoFiE 在视觉编码前过滤冗余帧，并在预填充时按查询进一步精简。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.03675/tech_analysis.md) |
| [2609.03702 — Synthetic Semantic Supervision for Contrastive Code Representation Learning in Small Transformers: An Empirical Study](https://arxiv.org/abs/2609.03702) | 2026-09-03T11:41:09Z / 2026-09-03T19:41:09+08:00 | knowledge_distillation；SyncDesc 将大模型合成的代码语义描述迁移进125M代码编码器。 | 8/7/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03702/tech_analysis.md) |
| [2609.03796 — LLaDA-Image: Building Strong Image Generators with Fully Open Training Recipes](https://arxiv.org/abs/2609.03796) | 2026-09-03T13:02:40Z / 2026-09-03T21:02:40+08:00 | knowledge_distillation；LLaDA-Image 使用原生掩码语言模型并以Turbo蒸馏获得2至4步生成。 | 8/8/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.03796/tech_analysis.md) |
| [2609.03820 — Select, Compress, Reinvest: A Controlled Study of Visual-Token Allocation in Long-Video MLLMs](https://arxiv.org/abs/2609.03820) | 2026-09-03T13:20:48Z / 2026-09-03T21:20:48+08:00 | pruning；在固定评测框架中把选帧、空间压缩和预算再分配拆开研究。 | 8/7/7/9 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.03820/tech_analysis.md) |
| [2609.03949 — VestigeKV: The NoPE-MLA KV Cache Carries Its Own Eviction Signal in a Vestigial Branch](https://arxiv.org/abs/2609.03949) | 2026-09-03T14:53:20Z / 2026-09-03T22:53:20+08:00 | other；VestigeKV 使用 NoPE-MLA 的解耦分支选择活跃缓存，保留可召回归档。 | 8/6/9/6 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.03949/tech_analysis.md) |
| [2609.04010 — Unlocking Lossless Speedups in LLMs via Discrete Diffusion](https://arxiv.org/abs/2609.04010) | 2026-09-03T15:48:43Z / 2026-09-03T23:48:43+08:00 | knowledge_distillation；Uno 将冻结 AR 教师分布蒸馏到共享基座的 gated LoRA 草稿路径；Qwen3-8B 单请求约2.53倍、64并发约1.57倍吞吐，基座权重未压缩。 | 9/5/9/7 | **本次新增**；[精读](../../../papers/2026-09/knowledge_distillation/2609.04010/tech_analysis.md) |
| [2609.04031 — DSAQuant: Denoising-Stage-Aligned Quantization-Aware Training for Video Generation](https://arxiv.org/abs/2609.04031) | 2026-09-03T16:09:25Z / 2026-09-04T00:09:25+08:00 | quantization；DSA 按去噪阶段切换监督来源，并把低比特误差与CFG调度共同处理。 | 8/9/9/5 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.04031/tech_analysis.md) |
| [2609.04071 — TAP-Path: Task-Adaptive Structural and Token Pruning for Efficient and Trustworthy Pathology Foundation Models](https://arxiv.org/abs/2609.04071) | 2026-09-03T16:43:36Z / 2026-09-04T00:43:36+08:00 | pruning；TAPPath 联合裁剪病理视觉编码器层数与token，得到更小且有外部验证的模型。 | 9/7/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.04071/tech_analysis.md) |
| [2609.04083 — CORE: Improving Compositional Reasoning in MLLM Embedding via Reranker Distillation](https://arxiv.org/abs/2609.04083) | 2026-09-03T16:50:29Z / 2026-09-04T00:50:29+08:00 | knowledge_distillation；CORE 将跨模态重排序器的组合关系判断迁移给可预计算的嵌入模型。 | 8/5/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04083/tech_analysis.md) |
| [2609.04098 — Why Gated DeltaNet Survives 4-Bit Quantization: NVFP4 W4A4 for the Recurrent Half of a Hybrid 27B LLM](https://arxiv.org/abs/2609.04098) | 2026-09-03T17:04:26Z / 2026-09-04T01:04:26+08:00 | quantization；Minima 给出混合GDN/注意力模型可部署的NVFP4校准及融合尺度协调方案。 | 9/9/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.04098/tech_analysis.md) |
| [2609.04105 — Hardware-Aware FP4 FlashAttention-4](https://arxiv.org/abs/2609.04105) | 2026-09-03T17:12:35Z / 2026-09-04T01:12:35+08:00 | quantization；Direct-P 直接从分数产生 FP4 概率码，并用相同表示计算归一化分母。 | 8/7/9/5 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.04105/tech_analysis.md) |
| [2609.04108 — Sequential Beats Joint: On the Interplay between On-Policy Distillation and RLVR](https://arxiv.org/abs/2609.04108) | 2026-09-03T17:14:27Z / 2026-09-04T01:14:27+08:00 | knowledge_distillation；先 OPD 再 RLVR 比多种联合损失更好，教师扩展覆盖后由奖励强化正确模式。 | 8/7/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04108/tech_analysis.md) |
| [2609.04131 — Beyond Retrieval: Progressive Latent Memory Evolution for Streaming Video Understanding](https://arxiv.org/abs/2609.04131) | 2026-09-03T17:28:14Z / 2026-09-04T01:28:14+08:00 | other；LatentStream 用查询无关的分层潜在记忆持续压缩视频，再按问题读取证据。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.04131/tech_analysis.md) |
| [2609.04172 — Rethinking On-Policy Distillation of Large Language Models II: One Training Example](https://arxiv.org/abs/2609.04172) | 2026-09-03T17:54:38Z / 2026-09-04T01:54:38+08:00 | knowledge_distillation；单条查询也能支持持续OPD，训练效率瓶颈可能在吸收监督而非提示数量。 | 8/3/9/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04172/tech_analysis.md) |
| [2609.04199 — Compile by Training: Turning Natural-Language Specifications into Local Neural Functions](https://arxiv.org/abs/2609.04199) | 2026-09-03T17:59:49Z / 2026-09-04T01:59:49+08:00 | knowledge_distillation；将自然语言规格编译成可复用的本地 Qwen3-0.6B 适配器。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04199/tech_analysis.md) |
| [2609.04203 — Temporal Self-Distillation: Learning Visual State Tracking in Videos Without Supervision](https://arxiv.org/abs/2609.04203) | 2026-09-03T17:59:55Z / 2026-09-04T01:59:55+08:00 | knowledge_distillation；S3T 用同一模型的密集时间视图监督稀疏视图，提高视频时间理解。 | 8/6/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[原分析](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04203/tech_analysis.md) |

## 本次新增精读

**Unlocking Lossless Speedups in LLMs via Discrete Diffusion（Uno）**：gated LoRA 学生学习冻结 AR 教师分布，通过精确校验保持目标分布；共享 KV 降低草稿开销。官方 [v1 PDF](https://arxiv.org/pdf/2609.04010v1) 可得（38 页），官方 HTML v1 为 404，已使用 PDF 并渲染核对 Table 2。

Table 2/18：Qwen3-8B 单请求 176→445 tokens/s（2.53×）；64 并发 3662→5733（1.57×）。增加 0.35B 适配器参数；相对 DFlash 的 1.05B 草稿附加参数减少 2/3，系统峰值 130.1→122.2 GiB，约减少 6.1%。基座权重没有压缩，不能将速度或草稿参数倍率写成整模型压缩倍率。

| 维度 | 评分 | 依据 |
|---|---:|---|
| 精度效果 | 9 | 精确拒绝校正保持目标分布，依赖正确实现 |
| 压缩倍率 | 5 | 基座未压缩；增加0.35B适配器，较DFlash附加参数减少2/3，峰值内存减少约6.1% |
| 创新性 | 9 | 共享gated LoRA、一步分布蒸馏与AR校验相结合 |
| 可复现性 | 7 | 公开Qwen与数据和详细参数；训练需32 H200约32小时，本机未运行 |

注意原文证据差异：正文 Takeaway 1 声称各批量超过2×，但表值仅支持上述具体配置。40% RL 训练加速尚缺作者承诺后续给出的完整实验；本文不把它视为已独立验证。

## 复现、独立快照与未完成项

本次新增为知识蒸馏 1 篇、量化 0 篇，因此无新增量化代码，也无 Qwen3-0.6B 量化运行任务。Uno 未在本机训练或测吞吐：论文 Qwen 配置为 32 H200×32 小时、14.7B tokens；当前任务只完成精读与数据核验，未声称复现结果。

隔离 worktree 严格从最新 `origin/main` `abfe8f2767d8bf881d586718ab4db33fc576be6a` 创建；分支 `feature/arxiv-daily-2026-09-06`。清理 main 自带 2026-07-28 历史日报。最终 papers 仅说明与 Uno；reports 仅说明与本日报；scripts 仅通用说明、无 quantization 论文目录；metadata 仅说明与 2026-09 本次 1 篇索引/CSV。

最终新增集合 `{2609.04010}` 与历史 521 个 ID 交集为空。论文目录、metadata 和 CSV 的 ID 集合必须一致；量化目录集合与新增量化集合均为空。原工作树 3 个修改、3 个未跟踪项保持不变。Git 单提交、diff、JSON/CSV、实际目录和远端 SHA 核验结果在最终回执中记录。

本次完整召回与去重已通过；09-05 仅作“截至运行时 arXiv 官方网页未检出”的时点结论，后续运行继续用三日窗口回查。
