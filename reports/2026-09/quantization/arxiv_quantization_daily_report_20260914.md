# arXiv 模型压缩论文日报

日报日期：2026-09-14；运行日期：2026-09-15；核验时间：2026-09-15T01:16:41.635938+08:00。

**三天窗口：北京时间 2026-09-12 00:00–2026-09-14 23:59。** 依据官方 abs 的 Submission history v1 转换时区，公告日期不作提交日期。

## 1. 本次结果

| 实际提交日（北京时间） | 全主题可见 | 原始相关（历史去重前） | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-09-12 | 38 | 4 | 0 | 4 |
| 2026-09-13 | 0 | 0 | 0 | 0 |
| 2026-09-14 | 0 | 0 | 0 | 0 |

窗口相关总数 **4**，历史重复 **0**，本次新增 **4**。9月13、14日仅表述为“**截至运行时 arXiv 官方网页未检出**”，不代表尚未公告的最终投稿数为零。后续运行继续按三天窗口回查。

范围包括模型低比特、模型结构压缩、任务能力蒸馏和注意力计算剪枝。输出语音码率压缩、普通跨模态表示对齐、完整KV卸载/分页，以及未实际压缩模型的训练或推理实现优化不计入。

## 2. 完整论文表

| ID / 标题 | v1 UTC | 实际提交时间（北京时间） | 分类 | 一句话结论 |
|---|---|---|---|---|
| [2609.13024 · Label-Guided Knowledge Distillation for 3D-CNNs in Action Recognition](https://arxiv.org/abs/2609.13024) | 2026-09-11T16:21:21Z | 2026-09-12T00:21:21+08:00 | knowledge_distillation；Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI) | 标签与原型蒸馏提高轻量视频模型准确率，仍有明显教师差距。 |
| [2609.13031 · Attention Quantization for Tabular Foundation Models](https://arxiv.org/abs/2609.13031) | 2026-09-11T16:31:29Z | 2026-09-12T00:31:29+08:00 | quantization；Machine Learning (cs.LG) ; Artificial Intelligence (cs.AI) | 协调两侧FP8误差比单侧量化更稳，大表推理最高1.67倍。 |
| [2609.13060 · CanvasAnneal: Curriculum Reinforcement Learning for Diffusion Language Models](https://arxiv.org/abs/2609.13060) | 2026-09-11T16:59:52Z | 2026-09-12T00:59:52+08:00 | knowledge_distillation；Machine Learning (cs.LG) | 教师轨迹逐步退场可改善部分扩散RL任务，压缩倍率未获验证。 |
| [2609.13141 · SAS: Simple Attention Sparsification via End-to-End Optimization of Context Ranking](https://arxiv.org/abs/2609.13141) | 2026-09-11T17:58:06Z | 2026-09-12T01:58:06+08:00 | pruning；Computation and Language (cs.CL) | 任务损失驱动稀疏块排序有效，但极长文本检索仍有显著损失。 |

## 3. 四维评分及依据

1–10分，越高越好；评分是阅读判断。压缩分同时考虑证据，不把训练收敛速度、理论张量倍率或decode吞吐当成整模型压缩比。

| ID | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 依据（按四项顺序） |
|---|---:|---:|---:|---:|---|
| 2609.13024 | 6 | 5 | 6 | 6 | 学生明显提升但仍落后教师16.84/14.25个百分点；参数1.21倍、FLOPs2.45倍，无实测延迟；标签时间权重与类别原型组合；公式与超参明确但单split、表文存在冲突 |
| 2609.13031 | 8 | 6 | 8 | 7 | 多数据集损失很小但部分统计检验提示微弱退化；FP8张量名义2倍，大表端到端最高1.67倍；协调训练/测试注意力误差并共享尺度；CPU与真实Qwen数值通过，缺少GPU原任务复现 |
| 2609.13060 | 5 | 2 | 7 | 5 | MATH/Countdown改善、GSM8K和部分工具任务退化；教师规模不公开；没有模型参数或推理倍率证据；Beta后缀课程与组内统一画布的轨迹蒸馏；超参披露充分，但闭源教师轨迹与八卡训练未复现 |
| 2609.13141 | 7 | 7 | 8 | 6 | 常见任务紧预算强，128K RULER严重退化；decode最高约13倍，不含prefill或全部KV容量压缩；以最终LM损失训练块排序，四因素消融；算法/配置详细，未执行selector训练与GPU后端 |

## 4. 官方页面覆盖与时区证据

本次重新完整下载五分类new/recent共10页，全部使用show=2000；每页声明总数、实际条目和逐组showing数全部相等。new覆盖New submissions、Cross submissions及Replacement submissions；recent覆盖页面列出的全部日期组。共4513次列表出现，按无版本ID合并为3010条。全部3010个abs本次重新下载，标题/摘要/主分类/全部分类/v1完整，网络/解析失败0。未使用arXiv官方API，未用搜索摘要代替全量列表。

每条记录先读取官方字段，以v1时间作无关键词日期排除；窗口38篇全部逐篇审阅标题摘要，9篇候选/边界读官方HTML正文。没有声称人工重新精读3010篇窗口外旧稿。关键词只复核排序：quantization、quantize、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache compression、mixed precision、GPTQ、AWQ，以及FP8、低秩、块选择等同义表达。

| 分类入口 | 声明=实际 | 实际覆盖 | 页面显示分组 |
|---|---:|---|---|
| [cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000) | 260 | 1–260，show=2000，无后续未读页 | Showing new listings for Monday, 14 September 2026；New submissions (showing 99 of 99 entries)；Cross submissions (showing 59 of 59 entries)；Replacement submissions (showing 102 of 102 entries) |
| [cs.LG recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 1076 | 1–1076，show=2000，无后续未读页 | Mon, 14 Sep 2026 (showing 158 of 158 entries )；Fri, 11 Sep 2026 (showing 171 of 171 entries )；Thu, 10 Sep 2026 (showing 163 of 163 entries )；Wed, 9 Sep 2026 (showing 447 of 447 entries )；Mon, 7 Sep 2026 (showing 137 of 137 entries ) |
| [cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000) | 115 | 1–115，show=2000，无后续未读页 | Showing new listings for Monday, 14 September 2026；New submissions (showing 44 of 44 entries)；Cross submissions (showing 20 of 20 entries)；Replacement submissions (showing 51 of 51 entries) |
| [cs.CL recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 604 | 1–604，show=2000，无后续未读页 | Mon, 14 Sep 2026 (showing 64 of 64 entries )；Fri, 11 Sep 2026 (showing 91 of 91 entries )；Thu, 10 Sep 2026 (showing 94 of 94 entries )；Wed, 9 Sep 2026 (showing 257 of 257 entries )；Mon, 7 Sep 2026 (showing 98 of 98 entries ) |
| [cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000) | 144 | 1–144，show=2000，无后续未读页 | Showing new listings for Monday, 14 September 2026；New submissions (showing 74 of 74 entries)；Cross submissions (showing 16 of 16 entries)；Replacement submissions (showing 54 of 54 entries) |
| [cs.CV recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 754 | 1–754，show=2000，无后续未读页 | Mon, 14 Sep 2026 (showing 90 of 90 entries )；Fri, 11 Sep 2026 (showing 89 of 89 entries )；Thu, 10 Sep 2026 (showing 106 of 106 entries )；Wed, 9 Sep 2026 (showing 359 of 359 entries )；Mon, 7 Sep 2026 (showing 110 of 110 entries ) |
| [cs.AI new](https://arxiv.org/list/cs.AI/new?show=2000) | 270 | 1–270，show=2000，无后续未读页 | Showing new listings for Monday, 14 September 2026；New submissions (showing 69 of 69 entries)；Cross submissions (showing 98 of 98 entries)；Replacement submissions (showing 103 of 103 entries) |
| [cs.AI recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1210 | 1–1210，show=2000，无后续未读页 | Mon, 14 Sep 2026 (showing 167 of 167 entries )；Fri, 11 Sep 2026 (showing 171 of 171 entries )；Thu, 10 Sep 2026 (showing 150 of 150 entries )；Wed, 9 Sep 2026 (showing 517 of 517 entries )；Mon, 7 Sep 2026 (showing 205 of 205 entries ) |
| [cs.AR new](https://arxiv.org/list/cs.AR/new?show=2000) | 7 | 1–7，show=2000，无后续未读页 | Showing new listings for Monday, 14 September 2026；New submissions (showing 3 of 3 entries)；Cross submissions (showing 2 of 2 entries)；Replacement submissions (showing 2 of 2 entries) |
| [cs.AR recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 73 | 1–73，show=2000，无后续未读页 | Mon, 14 Sep 2026 (showing 5 of 5 entries )；Fri, 11 Sep 2026 (showing 12 of 12 entries )；Thu, 10 Sep 2026 (showing 17 of 17 entries )；Wed, 9 Sep 2026 (showing 25 of 25 entries )；Mon, 7 Sep 2026 (showing 14 of 14 entries ) |

列表最新公告为9月14日；recent所显示日期组全部读取，并覆盖到窗口前。9月11日v1共339条作为相邻日期阳性对照。午夜边界对照：

- [2609.12997](https://arxiv.org/abs/2609.12997)：2026-09-11T15:59:06Z → 2026-09-11T23:59:06+08:00。
- [2609.13003](https://arxiv.org/abs/2609.13003)：2026-09-11T16:02:19Z → 2026-09-12T00:02:19+08:00。

## 5. 历史去重审计

git fetch --prune origin成功后逐个git ls-tree扫描全部41个历史日更远端分支，并读取每个分支的metadata/**/papers_index.json交叉核验。git ls-remote的分支全集与SHA逐一匹配本地远端引用。真实tech_analysis.md规范化ID为530，metadata为533；仅metadata存在的2607.27951、2607.28410、2607.28457不计完成。

跨分类/列表/日期先按规范ID合并，再排除历史集合。历史重复ID及来源分支：**无**。最终新增ID：2609.13024、2609.13031、2609.13060、2609.13141；与530个历史ID交集为空。当前09-15分支为从origin/main新建，无旧续跑成果。其他仅本地的未推送日期分支不算历史完成记录。

完整历史扫描来源：

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
- `origin/feature/arxiv-daily-2026-09-06`
- `origin/feature/arxiv-daily-2026-09-07`
- `origin/feature/arxiv-daily-2026-09-08`
- `origin/feature/arxiv-daily-2026-09-09`
- `origin/feature/arxiv-daily-2026-09-14`

## 6. 全窗口语义审阅

| ID | 标题 | 判定与依据 |
|---|---|---|
| [2609.13003](https://arxiv.org/abs/2609.13003) | Judging by the Cover: Cleaning LLM Truthfulness Benchmarks to Avoid Surface-Level Feature Leakage | 基准数据对清洗，Audit-Prune删除的是题目，不是模型。 |
| [2609.13005](https://arxiv.org/abs/2609.13005) | Tasks over Application Manuals: Revealing Gaps in Long-Horizon Procedural Reasoning for Language Models | 长程规则推理基准。 |
| [2609.13009](https://arxiv.org/abs/2609.13009) | How Good Are Frontier Models at Physics? Expert Re-Grading Reveals Broken Evaluations and Near-Saturation of Leading Benchmarks | 物理问题与评分基准审计。 |
| [2609.13010](https://arxiv.org/abs/2609.13010) | Dual-guided Hierarchical Edge Localization for Large-scale Optimal Transport Across Dimensions | 最优传输图边剪枝，非神经模型权重/注意力压缩。 |
| [2609.13011](https://arxiv.org/abs/2609.13011) | Comfort by Construction: Adaptive, Comfort-Bounded Action Spaces for Learned Driving Policies | 舒适度约束驾驶动作网格。 |
| [2609.13013](https://arxiv.org/abs/2609.13013) | TileNet: Tile-Based CNN-SVM Architecture for Autonomous Unmanned Aerial Systems Inspection of Flat Roofs | 全文复核：独立CNN-SVM结构与图像分块，未压缩既有模型；端侧部署留未来。 |
| [2609.13024](https://arxiv.org/abs/2609.13024) | Label-Guided Knowledge Distillation for 3D-CNNs in Action Recognition | 纳入：I3D到Top-I3D的标签引导特征蒸馏。 |
| [2609.13031](https://arxiv.org/abs/2609.13031) | Attention Quantization for Tabular Foundation Models | 纳入：逐头FP8注意力与两侧误差协调。 |
| [2609.13035](https://arxiv.org/abs/2609.13035) | Groupoid-Based Internal State Representations for Reinforcement Learning with Local Symmetries | 状态对称性抽象以加速RL学习，非模型压缩。 |
| [2609.13039](https://arxiv.org/abs/2609.13039) | Transfer Learning for Evolving Domains | 演变域迁移学习问题定义。 |
| [2609.13040](https://arxiv.org/abs/2609.13040) | Quantile-based Loss Filtering for Outlier-Robust Stochastic Gradient Descent | 按损失分位数筛样本的鲁棒优化。 |
| [2609.13042](https://arxiv.org/abs/2609.13042) | DynSHAP: Towards Explainable Dynamic Survival Analysis | 生存分析解释方法。 |
| [2609.13043](https://arxiv.org/abs/2609.13043) | Unified CT and MRI Pancreas Segmentation for Label-Efficient Cross-Modality Subregion Transfer | 跨模态分割表示迁移，未缩小模型。 |
| [2609.13044](https://arxiv.org/abs/2609.13044) | Robust Policy Optimization via Adversarial Importance Sampling | 鲁棒RL重要性采样。 |
| [2609.13045](https://arxiv.org/abs/2609.13045) | Kraken: LLM-based Speech-to-Speech Translation via Low-bitrate VQ and Dual-path Source Conditioning | 全文复核：325bps声学token码率压缩，量化对象为输出语音表示；未量化LLM权重/激活/KV或压缩既有模型。 |
| [2609.13047](https://arxiv.org/abs/2609.13047) | Diffusion Models and Concept Formation | 扩散模型与概念层级认知联系。 |
| [2609.13048](https://arxiv.org/abs/2609.13048) | MCRL2: Multi-resource Cross-attention-based Representation Learning-augmented Reinforcement Learning for Cloud Microservice Scheduling | 云微服务调度强化学习。 |
| [2609.13050](https://arxiv.org/abs/2609.13050) | A Unified and Constrained View of Regularization-Based Robust Reinforcement Learning | 鲁棒RL正则化与约束。 |
| [2609.13053](https://arxiv.org/abs/2609.13053) | Dynin-Robotics: Omnimodal Unified Diffusion Vision-Language-Action Model | 全文复核：共享轨迹模型、block-parallel解码和实现优化，未进行低比特模型压缩或学生蒸馏。 |
| [2609.13057](https://arxiv.org/abs/2609.13057) | Benign Loss Landscapes Can Coexist with Worst-Case Hardness | 张量网络损失景观理论，非低秩压缩实验。 |
| [2609.13058](https://arxiv.org/abs/2609.13058) | Expert-Space Exploration in MoE Reinforcement Learning | MoE路由探索保持计算预算，未永久删除专家或降低比特。 |
| [2609.13060](https://arxiv.org/abs/2609.13060) | CanvasAnneal: Curriculum Reinforcement Learning for Diffusion Language Models | 纳入：教师前缀进入奖励加权surrogate loss，明确轨迹蒸馏；不声称参数压缩倍率。 |
| [2609.13062](https://arxiv.org/abs/2609.13062) | Anchoring Clinical Events in Time: UID-Preserving Multimodal Reconstruction and Source-Grounded Adjudication | 临床事件时间线重建与评估。 |
| [2609.13071](https://arxiv.org/abs/2609.13071) | Involving before Evolving: A Vision for Trustworthy Enterprise Digital Twin Engineering | 企业数字孪生工程愿景。 |
| [2609.13072](https://arxiv.org/abs/2609.13072) | MAxBench: A Multinomial Concept Recovery Benchmark | 概念恢复与模型解释基准，rank-one为解释子空间。 |
| [2609.13073](https://arxiv.org/abs/2609.13073) | Autonomous Research for Open-Ended Problems: A Case Study on Telecom Ticket Retrieval | 自动研究工作流评价。 |
| [2609.13076](https://arxiv.org/abs/2609.13076) | MP-Bench: Evaluating Voice Agents as a Multiparty Conversation Participant | 多人语音代理基准。 |
| [2609.13082](https://arxiv.org/abs/2609.13082) | Embodied-BenchForge: A Closed-Loop Agentic Workflow for Embodied Benchmark Construction | 具身基准生成与验证工作流。 |
| [2609.13083](https://arxiv.org/abs/2609.13083) | ASTRIL-MPC: Autonomous Traversal Framework of Articulated Tracked Robots with Language-Guided Neural-Kinematic MPC | 机器人控制器与MPC参数调整。 |
| [2609.13100](https://arxiv.org/abs/2609.13100) | A Ranking Approach for Measuring Calibration | 概率校准评价量，不是量化校准。 |
| [2609.13117](https://arxiv.org/abs/2609.13117) | Continue, Adapt, or Yield: In-Turn Adaptation to Overlapping Speech in Full-Duplex Agents | 全双工语音交互评价。 |
| [2609.13118](https://arxiv.org/abs/2609.13118) | CMA-OT: Hierarchical Expert Supervision for Dance-to-Music Generation | 全文复核：跨任务音乐专家表示对齐，未以替换/缩小专家模型为目标；VAE的2048为音频表示下采样，不是模型压缩。 |
| [2609.13125](https://arxiv.org/abs/2609.13125) | A Hybrid LSTM-XGBoost Framework for Multi-Horizon Stock Return Prediction Across Diversified Equity Portfolios | 股票预测混合模型。 |
| [2609.13134](https://arxiv.org/abs/2609.13134) | Rethinking Heterogeneous System Disaggregation for Subquadratic Attention | 全文复核：已有稀疏模型的异构卸载、分页缓存和预取；完整KV保留，无新量化/剪枝算法或压缩效果评估。 |
| [2609.13135](https://arxiv.org/abs/2609.13135) | Recurrent Dynamic Range Extension | 循环HDR图像重建。 |
| [2609.13141](https://arxiv.org/abs/2609.13141) | SAS: Simple Attention Sparsification via End-to-End Optimization of Context Ranking | 纳入：冻结预训练主干，学习块选择以剪除decode注意力计算。 |
| [2609.13144](https://arxiv.org/abs/2609.13144) | Type Diversity Enables Transformers to Generalise Compositionally | 语言组合泛化数据集与实验。 |
| [2609.13146](https://arxiv.org/abs/2609.13146) | SNAP3D: Physically Grounded 3D Parts for Assembly from a Single Image | 三维几何与物理装配优化。 |

全文复核：13024、13031、13060、13141为四篇纳入论文；13013、13045、13053、13118、13134为排除边界。CanvasAnneal的教师前缀确实进入奖励加权学习目标，因此归于知识蒸馏，但其参数/推理压缩倍率未披露。CMA-OT为跨任务音乐特征监督，没有模型压缩目标；Kraken量化的是声学输出码，不能冒称LLM低比特。

## 7. 精读与真实复现

四篇精读按实际提交月放在papers/2026-09下，均含核心速览、背景、方法、实验、局限、启发六节。

唯一新增量化论文2609.13031，复现目录`scripts/quantization/2609.13031/`包含README.md、demo.py、results.json、gate_results.json。真实Qwen3-0.6B、28层、三段固定文本、84次量化attention调用；FP8转换/逐头动态尺度/在线softmax/共享尺度配对测试均实际执行。PyTorch2.8.0、Transformers4.57.6、macOS arm64 CPU、FP32权重、4线程。缓存模型revision c1899de289a04d12100db370d81485cdf75e47ca。

70/81/91 token基线CE为2.317776/2.180148/1.753602，FP8参考CE为2.281809/2.162833/1.758144，logits相对L2为0.071643/0.067547/0.060050。小样本不代表基准精度改善。CPU参考略慢，无加速结论。默认8192门限检查84次回退，logits误差全0；强制小形状路径明确为数值测试。语法、导入、FP8零张量、因果注意力与SDPA对照、共享Q尺度测试均通过。

未完成的原论文实验：无NVIDIA GPU，未执行Triton原生FP8/TabPFN/TabICL大表基准；Qwen没有表格训练/测试双调用，相关不变量用配对小张量独立验证。其余三篇未运行视频蒸馏、闭源教师轨迹的八卡RL或SAS选择器训练。未伪造硬件性能或创建占位复现。

## 8. 分支独立快照与提交检查

分支`feature/arxiv-daily-2026-09-15`严格从最新origin/main `abfe8f2767d8bf881d586718ab4db33fc576be6a`建立；linked worktree位于`/private/tmp/reading_machine_arxiv_20260915`，Git公共目录属于指定仓库。删除main自带2026-07-28历史日报，仅保留说明文件、本次四篇论文、本日报、四条metadata/CSV及唯一新增量化复现。历史feature只读。

提交前核验papers/metadata/CSV四个ID一致，quantization复现ID精确等于新增量化子集{2609.13031}；最终集合与历史零交集，无窗口外成果。原工作树六处用户改动逐文件SHA256和git status核验保持不变。提交后核验origin/main..HEAD仅一个本次提交、merge-base等于main、ls-remote SHA一致，具体提交SHA见运行汇报。
