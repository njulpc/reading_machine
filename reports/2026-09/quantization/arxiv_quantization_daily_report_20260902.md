# arXiv 模型压缩论文日报（2026-09-02）

## 1. 本次结论

- 固定窗口：2026-08-31、2026-09-01、2026-09-02 三个完整自然日；日报主日期为 2026-09-02。
- 五类官方 HTML 合并 3,196 个唯一 ID，标题、摘要和 `/abs` v1 history 均为 3,196/3,196 成功。
- 按 v1 归窗原始论文为 552 / 427 / 0；语义复核后的模型压缩相关数为 **58 / 35 / 0**，窗口相关共 93 篇。
- 扫描 33 个历史分支与 397 个真实分析 ID，排除历史重复 37 篇；本次新增 **56** 篇，与历史集合交集为空。
- 2026-09-02 的准确表述是：**截至运行时 arXiv 官方网页未检出 v1=2026-09-02 的目标分类论文**，并非抓取失败。

## 2. 官方分类页覆盖审计

所有入口使用 `show=2000`；声明总数与实际解析数逐页一致且小于 2,000。`new` 包含 New/Cross/Replacement；`recent` 覆盖窗口，并以 8 月 28、27 日作为窗口外阳性对照。

| 分类 | 模式 | 入口 | 页面声明 | 实际解析 | 日期/提交分组 |
|---|---|---|---:|---:|---|
| cs.LG | new | [https://arxiv.org/list/cs.LG/new?show=2000](https://arxiv.org/list/cs.LG/new?show=2000) | 323 | 323 | Showing new listings for Wednesday, 2 September 2026；New submissions (showing 109 of 109 entries)；Cross submissions (showing 93 of 93 entries)；Replacement submissions (showing 121 of 121 entries) |
| cs.LG | recent | [https://arxiv.org/list/cs.LG/recent?show=2000](https://arxiv.org/list/cs.LG/recent?show=2000) | 1003 | 1003 | Wed, 2 Sep 2026 (showing 202 of 202 entries )；Tue, 1 Sep 2026 (showing 336 of 336 entries )；Mon, 31 Aug 2026 (showing 120 of 120 entries )；Fri, 28 Aug 2026 (showing 157 of 157 entries )；Thu, 27 Aug 2026 (showing 188 of 188 entries ) |
| cs.CL | new | [https://arxiv.org/list/cs.CL/new?show=2000](https://arxiv.org/list/cs.CL/new?show=2000) | 304 | 304 | Showing new listings for Wednesday, 2 September 2026；New submissions (showing 127 of 127 entries)；Cross submissions (showing 58 of 58 entries)；Replacement submissions (showing 119 of 119 entries) |
| cs.CL | recent | [https://arxiv.org/list/cs.CL/recent?show=2000](https://arxiv.org/list/cs.CL/recent?show=2000) | 827 | 827 | Wed, 2 Sep 2026 (showing 185 of 185 entries )；Tue, 1 Sep 2026 (showing 298 of 298 entries )；Mon, 31 Aug 2026 (showing 82 of 82 entries )；Fri, 28 Aug 2026 (showing 154 of 154 entries )；Thu, 27 Aug 2026 (showing 108 of 108 entries ) |
| cs.CV | new | [https://arxiv.org/list/cs.CV/new?show=2000](https://arxiv.org/list/cs.CV/new?show=2000) | 227 | 227 | Showing new listings for Wednesday, 2 September 2026；New submissions (showing 116 of 116 entries)；Cross submissions (showing 36 of 36 entries)；Replacement submissions (showing 75 of 75 entries) |
| cs.CV | recent | [https://arxiv.org/list/cs.CV/recent?show=2000](https://arxiv.org/list/cs.CV/recent?show=2000) | 782 | 782 | Wed, 2 Sep 2026 (showing 152 of 152 entries )；Tue, 1 Sep 2026 (showing 316 of 316 entries )；Mon, 31 Aug 2026 (showing 93 of 93 entries )；Fri, 28 Aug 2026 (showing 114 of 114 entries )；Thu, 27 Aug 2026 (showing 107 of 107 entries ) |
| cs.AI | new | [https://arxiv.org/list/cs.AI/new?show=2000](https://arxiv.org/list/cs.AI/new?show=2000) | 445 | 445 | Showing new listings for Wednesday, 2 September 2026；New submissions (showing 124 of 124 entries)；Cross submissions (showing 185 of 185 entries)；Replacement submissions (showing 136 of 136 entries) |
| cs.AI | recent | [https://arxiv.org/list/cs.AI/recent?show=2000](https://arxiv.org/list/cs.AI/recent?show=2000) | 1328 | 1328 | Wed, 2 Sep 2026 (showing 309 of 309 entries )；Tue, 1 Sep 2026 (showing 424 of 424 entries )；Mon, 31 Aug 2026 (showing 190 of 190 entries )；Fri, 28 Aug 2026 (showing 196 of 196 entries )；Thu, 27 Aug 2026 (showing 209 of 209 entries ) |
| cs.AR | new | [https://arxiv.org/list/cs.AR/new?show=2000](https://arxiv.org/list/cs.AR/new?show=2000) | 14 | 14 | Showing new listings for Wednesday, 2 September 2026；New submissions (showing 5 of 5 entries)；Cross submissions (showing 7 of 7 entries)；Replacement submissions (showing 2 of 2 entries) |
| cs.AR | recent | [https://arxiv.org/list/cs.AR/recent?show=2000](https://arxiv.org/list/cs.AR/recent?show=2000) | 46 | 46 | Wed, 2 Sep 2026 (showing 12 of 12 entries )；Tue, 1 Sep 2026 (showing 10 of 10 entries )；Mon, 31 Aug 2026 (showing 5 of 5 entries )；Fri, 28 Aug 2026 (showing 9 of 9 entries )；Thu, 27 Aug 2026 (showing 10 of 10 entries ) |

跨页去重后 3,196 个 ID；v1 窗口外阳性对照为 2026-08-28=352、2026-08-27=416。54 篇新增论文读取官方 HTML 全文；2608.30141、2609.01084 的 HTML 返回 404，改读官方 PDF。

## 3. 去重审计

- 去重来源分支数：33；历史真实分析 ID：397；metadata ID：400；metadata-only 为 2607.27951、2607.28410、2607.28457。
- 三日相关数：58 / 35 / 0；历史重复 37；最终新增 56。
- 被排除重复及来源：2608.30122（origin/feature/arxiv-daily-2026-09-02）、2608.30135（origin/feature/arxiv-daily-2026-09-02）、2608.30158（origin/feature/arxiv-daily-2026-09-02）、2608.30163（origin/feature/arxiv-daily-2026-09-02）、2608.30181（origin/feature/arxiv-daily-2026-09-02）、2608.30218（origin/feature/arxiv-daily-2026-09-02）、2608.30252（origin/feature/arxiv-daily-2026-09-02）、2608.30258（origin/feature/arxiv-daily-2026-09-02）、2608.30263（origin/feature/arxiv-daily-2026-09-02）、2608.30277（origin/feature/arxiv-daily-2026-09-02）、2608.30294（origin/feature/arxiv-daily-2026-09-02）、2608.30295（origin/feature/arxiv-daily-2026-09-02）、2608.30320（origin/feature/arxiv-daily-2026-09-02）、2608.30384（origin/feature/arxiv-daily-2026-09-02）、2608.30394（origin/feature/arxiv-daily-2026-09-02）、2608.30427（origin/feature/arxiv-daily-2026-09-02）、2608.30439（origin/feature/arxiv-daily-2026-09-02）、2608.30564（origin/feature/arxiv-daily-2026-09-02）、2608.30567（origin/feature/arxiv-daily-2026-09-02）、2608.30695（origin/feature/arxiv-daily-2026-09-02）、2608.30741（origin/feature/arxiv-daily-2026-09-02）、2608.30760（origin/feature/arxiv-daily-2026-09-02）、2608.30782（origin/feature/arxiv-daily-2026-09-02）、2608.30841（origin/feature/arxiv-daily-2026-09-02）、2608.30870（origin/feature/arxiv-daily-2026-09-02）、2608.30908（origin/feature/arxiv-daily-2026-09-02）、2608.30927（origin/feature/arxiv-daily-2026-09-02）、2608.30963（origin/feature/arxiv-daily-2026-09-02）、2608.30978（origin/feature/arxiv-daily-2026-09-02）、2608.30996（origin/feature/arxiv-daily-2026-09-02）、2608.31046（origin/feature/arxiv-daily-2026-09-02）、2608.31053（origin/feature/arxiv-daily-2026-09-02）、2608.31066（origin/feature/arxiv-daily-2026-09-02）、2608.31069（origin/feature/arxiv-daily-2026-09-02）、2608.31106（origin/feature/arxiv-daily-2026-09-02）、2608.31108（origin/feature/arxiv-daily-2026-09-02）、2608.31157（origin/feature/arxiv-daily-2026-09-02）。
- 新增集合与历史集合交集为空；跨日期、跨分类与跨关键词均先按去版本规范 ID 合并。

## 4. 新增论文总表与评分

评分为 1–10：精度效果、压缩倍率、创新性、可复现性。无统一端到端倍率时不从参数量推断。

| # | arXiv | 标题 | v1 日期 | 技术 | 一句话结论 | 精度 | 压缩 | 创新 | 复现 |
|---:|---|---|---|---|---|---:|---:|---:|---:|
| 1 | [2609.00575](https://arxiv.org/abs/2609.00575) | Residual Sparsification via Output Importance for Compressing Mixture-of-Experts LLMs | 2026-09-01 | 剪枝/稀疏化 | 同峰值显存下降下，PARSER 将 Qwen 与 DeepSeek 相对未压缩模型的准确率差距分别缩小 1.41× 和 1.44×。 | 8 | 8 | 8 | 7 |
| 2 | [2609.00588](https://arxiv.org/abs/2609.00588) | Quit While You're Ahead: Quit for Efficient Candidate Generation in Machine Translation Reranking | 2026-09-01 | 其他压缩与高效推理 | 19 个语向上，MBR 端到端加速 1.47–2.66×，QE 重排加速 3.43–4.12×，质量保持在预设等价界内。 | 8 | 8 | 7 | 7 |
| 3 | [2609.00611](https://arxiv.org/abs/2609.00611) | Panda Diplomacy: Foundation Model Pre-training across Particle Imaging Detectors for High Energy and Nuclear Physics | 2026-09-01 | 知识蒸馏 | 仅 1,000 个标注样本即可迁移；在 sPHENIX 上以少 70× 的标注匹配强基线，在 LArTPC 上最高少 1,000×。 | 8 | 7 | 8 | 7 |
| 4 | [2609.00624](https://arxiv.org/abs/2609.00624) | Trust Your Guide Only When Certain: Uncertainty-Aware Sparse Alignment at Inference Time | 2026-09-01 | 剪枝/稀疏化 | 跳过约 50% 对齐步骤，相比密集基线安全偏好最高提升 15.6%，通用偏好最高提升 12.0%。 | 8 | 8 | 8 | 7 |
| 5 | [2609.00665](https://arxiv.org/abs/2609.00665) | Triple-Bottom-Line Sustainability of Language Models for Edge AI: A Comparison Between SLMs and Quantized LLMs | 2026-09-01 | 量化 | 30 个实测配置中，Qwen3-30B-A3B/GGUF Q4 的 HSS 为 93.38，优于最高 SLM 的 89.49。 | 8 | 8 | 8 | 7 |
| 6 | [2609.00667](https://arxiv.org/abs/2609.00667) | From Saliency to Discriminability: Rank-Preserving Visual Token Pruning for VLM Rerankers | 2026-09-01 | 剪枝/稀疏化 | 20% token 预算可在部分检索集匹配或超过稠密模型；FLOPs 降 39–45%，实测加速 1.28–1.45×。 | 8 | 8 | 8 | 7 |
| 7 | [2609.00718](https://arxiv.org/abs/2609.00718) | A Closed-Loop Evaluation of Capability Loss and Recovery in Compressed Driving Policies | 2026-09-01 | 量化 | 闭环实验显示结构化剪枝最先造成能力丢失，蒸馏只部分恢复；量化未剪枝演员则保住全部五项课程。 | 8 | 8 | 8 | 7 |
| 8 | [2609.00791](https://arxiv.org/abs/2609.00791) | Instella-MoE Technical Report | 2026-09-01 | 知识蒸馏 | 16B 总参数、每 token 2.8B 激活；预训练平均 76.7，后训练 Think 检查点平均 73.2。 | 8 | 7 | 8 | 7 |
| 9 | [2609.00796](https://arxiv.org/abs/2609.00796) | SFAD: Speculative Factuality-Aware Decoding | 2026-09-01 | 其他压缩与高效推理 | 在提升上下文忠实度的同时报告 2.48× 推测解码加速。 | 8 | 8 | 7 | 7 |
| 10 | [2609.00798](https://arxiv.org/abs/2609.00798) | Advanced Pixel Diffusion Model with Guided Sparse Global Refinement | 2026-09-01 | 剪枝/稀疏化 | ImageNet 上 256² FID 1.51，扩展到 512² 后 FID 1.60。 | 8 | 8 | 8 | 7 |
| 11 | [2609.00865](https://arxiv.org/abs/2609.00865) | MemoryWalker: Stop Training Agents on Contexts They Never Saw | 2026-09-01 | 知识蒸馏 | 七个网页搜索基准上，精确方法回到无压缩误差底线，SDCC 降低 logit 漂移并提高 rollout reward。 | 8 | 7 | 8 | 7 |
| 12 | [2609.00891](https://arxiv.org/abs/2609.00891) | CacheBridge: Efficient Cross-Model KV Cache Transfer | 2026-09-01 | 其他压缩与高效推理 | Qwen3 迁移平均保留 99.83%；映射存储降 8×、应用最快 3.0×、构建从 92.63 秒降至 8.63 秒。 | 8 | 8 | 7 | 7 |
| 13 | [2609.00951](https://arxiv.org/abs/2609.00951) | CERF: Communication-Efficient and Retraining-Free Collaborative Perception | 2026-09-01 | 其他压缩与高效推理 | 在多种下游任务保持与中间特征协同方法相当的性能，同时通信开销下降 95%。 | 8 | 8 | 7 | 7 |
| 14 | [2609.01004](https://arxiv.org/abs/2609.01004) | SinkPruner: Sink-Free Visual Token Pruning for Multimodal Large Language Models | 2026-09-01 | 剪枝/稀疏化 | 论文报告在多个 MLLM 和图像/视频基准上以更少视觉 token 保持或改善精度；具体预算见全文表格。 | 8 | 8 | 8 | 7 |
| 15 | [2609.01024](https://arxiv.org/abs/2609.01024) | PCoMoE: Shifting MoE Inference from Monolithic Expert Selection to Fine-Grained Path Composition | 2026-09-01 | 剪枝/稀疏化 | 端到端推理最高加速 1.31×，同时报告准确率提升 10%。 | 8 | 8 | 8 | 7 |
| 16 | [2609.01084](https://arxiv.org/abs/2609.01084) | Hardware Acceleration of Block-Diffusion LLM for Edge Devices | 2026-09-01 | 量化 | 1.5B/7B 模型上能耗分别降 3.79×/3.96×，延迟加速 2.88×/4.44×，分数下降均小于 1 个百分点。 | 8 | 8 | 8 | 7 |
| 17 | [2609.01091](https://arxiv.org/abs/2609.01091) | Subliminal Learning as Trait-Direction Drift: A Mechanism and Targeted Control under SFT Distillation | 2026-09-01 | 知识蒸馏 | 全文用多组教师—学生与训练阶段实验追踪隐藏偏好迁移；结论强调控制机制而非一般精度压缩收益。 | 8 | 7 | 8 | 7 |
| 18 | [2609.01111](https://arxiv.org/abs/2609.01111) | ClinTraceBench: Source-Verifiable Longitudinal Clinical Reasoning over EHR-Derived Dialogues | 2026-09-01 | 其他压缩与高效推理 | 6,271 个问题、200,672 次预测；关系注入后多种压缩记忆仅恢复 0–5.3%，显示聚合损失严重。 | 8 | 8 | 7 | 7 |
| 19 | [2609.01158](https://arxiv.org/abs/2609.01158) | Superposed Latent Autoencoder | 2026-09-01 | 其他压缩与高效推理 | 相同存储预算下重构误差最高降低 56%，下游分类最高提升 16.79 个百分点。 | 8 | 8 | 7 | 7 |
| 20 | [2609.01200](https://arxiv.org/abs/2609.01200) | Compressing AI Traffic: Standardized Neural Network Coding of Visual-Token Representations in Split Vision-Language Inference | 2026-09-01 | 量化 | 标准 NNC 在分割式 VLM 上压缩视觉 token；论文以率失真和下游任务变化联合报告，避免只看码率。 | 8 | 8 | 8 | 7 |
| 21 | [2609.01212](https://arxiv.org/abs/2609.01212) | Recent Developments in Transformer Inference Deployment on FPGA Platforms: A Survey | 2026-09-01 | 其他压缩与高效推理 | 作为系统综述不主张单一算法增益，价值在于统一比较 FPGA 数据流、精度与存储设计证据。 | 8 | 8 | 7 | 7 |
| 22 | [2609.01224](https://arxiv.org/abs/2609.01224) | S$^2$Prune: Spatially Structured Visual Token Pruning for Multimodal Large Language Models | 2026-09-01 | 剪枝/稀疏化 | 多种 MLLM 与视觉任务验证空间覆盖优于简单重要性/冗余准则；精确保留率和吞吐见官方全文。 | 8 | 8 | 8 | 7 |
| 23 | [2609.01232](https://arxiv.org/abs/2609.01232) | Position Matters: Feature Inversion Attacks in ViT Split Inference with Token Reduction and Shuffling | 2026-09-01 | 其他压缩与高效推理 | 实验显示 token 缩减和打乱并不自动阻断特征反演，隐私收益必须与攻击者和位置假设一起评估。 | 8 | 8 | 7 | 7 |
| 24 | [2609.01343](https://arxiv.org/abs/2609.01343) | SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers | 2026-09-01 | 其他压缩与高效推理 | 计算最优前沿节省 6.8–18.0% 训练 FLOPs，优势随样本长度和上下文示例数量增加。 | 8 | 8 | 7 | 7 |
| 25 | [2609.01345](https://arxiv.org/abs/2609.01345) | Cheap Verifiers, Large Blind Spots: Measuring the Reliability Cost of Cost-Saving Cascades | 2026-09-01 | 知识蒸馏 | 学生从 0.5B 扩到 32B 时验证器盲区 β 从 0.12 升到 0.55；内部仪表仍显示约 3% 错误而真实错误最高 32%。 | 8 | 7 | 8 | 7 |
| 26 | [2609.01374](https://arxiv.org/abs/2609.01374) | Behaviorally Effective LoRA Writes Are Sparse and Structured | 2026-09-01 | 剪枝/稀疏化 | 14 次精确切换的准确率不变、写入矩阵相对误差不超过 0.25%；12 个种子案例最优每模块 k 均在 2 或 4。 | 8 | 8 | 8 | 7 |
| 27 | [2609.01406](https://arxiv.org/abs/2609.01406) | Contribution-Aware Bandwidth Allocation for Multimodal Split Learning | 2026-09-01 | 其他压缩与高效推理 | 5× 压缩且同 payload 下，CREMA-D 与 MVSA 准确率分别提高 15.4 和 12.4 个百分点。 | 8 | 8 | 7 | 7 |
| 28 | [2609.01428](https://arxiv.org/abs/2609.01428) | TRIAGE: Three-level Routing and Intelligent Agent Guidance for Efficient Execution | 2026-09-01 | 其他压缩与高效推理 | 1,007 个查询节省 62.3% token；ToolBench 跨域节省 76.3%，平均 token 成本由 198 降到 74.7。 | 8 | 8 | 7 | 7 |
| 29 | [2609.01430](https://arxiv.org/abs/2609.01430) | Learning Sparse Decision Trees via Transformer Variational Auto-Encoders | 2026-09-01 | 剪枝/稀疏化 | 与近最优树算法预测性能相当，同时得到更高结构稀疏度；摘要未给出统一压缩倍率。 | 8 | 8 | 8 | 7 |
| 30 | [2609.01507](https://arxiv.org/abs/2609.01507) | LatentPress: Context Compression Beyond Text and Vision | 2026-09-01 | 其他压缩与高效推理 | 压缩 4–16×；LongMemEval 在 7.70× 下准确率 0.504，高于未压缩 0.490，读取快 5–9×。 | 8 | 8 | 7 | 7 |
| 31 | [2609.01532](https://arxiv.org/abs/2609.01532) | Knowledge Distillation During Mid-Training Favors Reasoning over Factual Recall | 2026-09-01 | 知识蒸馏 | 相对 NTP，推理达 1.61–1.71×、知识常识达 1.13–1.19×，同时保留 96.7–96.8% 事实回忆。 | 8 | 7 | 8 | 7 |
| 32 | [2609.01550](https://arxiv.org/abs/2609.01550) | A Mathematical Theory of Reusable Neural Bases for Network Compression | 2026-09-01 | 其他压缩与高效推理 | 实验显示同参数预算可构造更宽更深网络，并保持稳定训练与不劣收敛；摘要未给统一压缩倍率。 | 8 | 8 | 7 | 7 |
| 33 | [2609.01567](https://arxiv.org/abs/2609.01567) | Selective Agent Guidance via Entropy: Learning Autonomous Policies from Imperfect VLM Teachers | 2026-09-01 | 知识蒸馏 | 稀疏奖励视觉推理与导航任务上，部署时零 VLM 调用；部分环境中轻量策略超过教师。 | 8 | 7 | 8 | 7 |
| 34 | [2609.01575](https://arxiv.org/abs/2609.01575) | Closing Cost-Quality Gap in Document VLMs: Difficulty-Aware Data Curation and Quality-Adjusted Deployment Economics | 2026-09-01 | 其他压缩与高效推理 | 35B 总参数仅激活 3B；质量调整成本比人工低 80% 以上、比最佳可部署开源模型低 50% 以上。 | 8 | 8 | 7 | 7 |
| 35 | [2609.01587](https://arxiv.org/abs/2609.01587) | The Structure of Quantization Damage in LLMs: Why the Next Bit Should Be Spent Globally | 2026-09-01 | 量化 | 9 个模型、4 个架构族中 8 个模型恢复 75% 量化损失约需一半层；全局细粒度比局部修复高 21–52 分。 | 8 | 8 | 8 | 7 |
| 36 | [2608.30141](https://arxiv.org/abs/2608.30141) | Balancing Privacy, Utility, and Safety in LLM Alignment through Preference Optimization | 2026-08-31 | 其他压缩与高效推理 | 4-bit Gemma-2-2B 的隐私混合组 AUROC/AUPRC 为 0.596–0.629/0.541–0.575，基线为 0.804/0.790，但跨数据源不一致。 | 8 | 8 | 7 | 7 |
| 37 | [2608.30226](https://arxiv.org/abs/2608.30226) | LaMoC: Loss-Aware Modular Compression for LLMs | 2026-08-31 | 其他压缩与高效推理 | 四个模型族八个模型上，4–8B 模型平均困惑度降 2.5%，任务准确率相对现有模块压缩提高 1%。 | 8 | 8 | 7 | 7 |
| 38 | [2608.30310](https://arxiv.org/abs/2608.30310) | Tail-Replay: Escaping the Curse of Linear Attention in Prefix Caching for Hybrid LLMs | 2026-08-31 | 其他压缩与高效推理 | 仅重放 5–10% 前缀可保留 92.8–99.9% 全预填质量；32K 前缀 TTFT 加速 9.1–14.3×。 | 8 | 8 | 7 | 7 |
| 39 | [2608.30352](https://arxiv.org/abs/2608.30352) | Co-Annotator: Expert-Distilled ViT and VLM for Visual and Documentation Guidance in Age-Related Macular Degeneration | 2026-08-31 | 知识蒸馏 | 两机构联合部署中，每分钟正确诊断提高 40%，评论编辑时间降低 67%，且未牺牲诊断准确率。 | 8 | 7 | 8 | 7 |
| 40 | [2608.30386](https://arxiv.org/abs/2608.30386) | DASC: Decay-Aware State Compression for Hybrid Linear-Attention Serving | 2026-08-31 | 其他压缩与高效推理 | KDA 状态检查点压缩 2.63×；固定预算下平均 TTFT 降 42.6%，输入吞吐提高 68.4%。 | 8 | 8 | 7 | 7 |
| 41 | [2608.30505](https://arxiv.org/abs/2608.30505) | Tensor Methods for Language Models: From Token Representation to Training, Adaptation, Inference, Compression, and Interpretability | 2026-08-31 | 其他压缩与高效推理 | 综述提出 ρ_gap 衡量理论内存下降与系统实测加速的差距，不把参数减少直接等同吞吐收益。 | 8 | 8 | 7 | 7 |
| 42 | [2608.30563](https://arxiv.org/abs/2608.30563) | Modality Disentangled Learning for Incomplete Multimodal Emotion Recognition: A Primitive Memory Distillation Perspective | 2026-08-31 | 知识蒸馏 | IEMOCAP、CMU-MOSI、CMU-MOSEI 多种缺失模态设置下达到或超过强基线，并提升稳定性。 | 8 | 7 | 8 | 7 |
| 43 | [2608.30647](https://arxiv.org/abs/2608.30647) | What It Costs to Compose, Rebuild, and Correct Precomputed Memory | 2026-08-31 | 其他压缩与高效推理 | Llama-3.1-8B 上显示分块组合、更新和旁路纠错都会带来可测成本，需按知识变化节奏重建记忆。 | 8 | 8 | 7 | 7 |
| 44 | [2608.30785](https://arxiv.org/abs/2608.30785) | SkillZip Pro: Execution-Aware Dynamic Compression of Progressively Loaded Skills for Self-Evolving Agents | 2026-08-31 | 其他压缩与高效推理 | 工业内容审核技能中目录 token 降 38%、端到端每次运行 token 降 10.4% 且无质量损失；过激 71% 配置最高掉 26 分。 | 8 | 8 | 7 | 7 |
| 45 | [2608.30811](https://arxiv.org/abs/2608.30811) | TopoCompress: Long Context Compression via Graph-Wired Semantic Trajectories | 2026-08-31 | 其他压缩与高效推理 | 五个长上下文任务上，以强基线 1/4 的预算达到相当性能，压缩耗时比最快基线再小 1.41×。 | 8 | 8 | 7 | 7 |
| 46 | [2609.00097](https://arxiv.org/abs/2609.00097) | Faster Than Flash: Exploiting Attention Sparsity for Efficient Long-Context Decoding | 2026-08-31 | 剪枝/稀疏化 | 上下文最长 256K，内核最高加速 11.6×，端到端吞吐提高 2.37×并保持 RULER/LongBench 准确率。 | 8 | 8 | 8 | 7 |
| 47 | [2609.00103](https://arxiv.org/abs/2609.00103) | Good Memory Has ECC: Evaluating the Memory of Vision-Language Models Beyond Accuracy | 2026-08-31 | 其他压缩与高效推理 | 实验证明预训练 VLM 能压缩文本记忆却不能同样压缩视频记忆，且两者校准均不足。 | 8 | 8 | 7 | 7 |
| 48 | [2609.00224](https://arxiv.org/abs/2609.00224) | QTEA: Ternary LLMs with Sparse Residual Salient Weight and By-Column Optimization | 2026-08-31 | 量化 | Qwen3-14B 达 1.7 bit/weight，准确率比强三值基线高 16.7%，查表内核逐 token 生成快 7.2×。 | 8 | 8 | 8 | 7 |
| 49 | [2609.00251](https://arxiv.org/abs/2609.00251) | Hypotheses-Guided Self Distillation for Continual Personalization | 2026-08-31 | 知识蒸馏 | 三类持续个性化设置均优于原始历史与增量更新基线，并对新用户、跨域和上下文预算变化保持稳定。 | 8 | 7 | 8 | 7 |
| 50 | [2609.00291](https://arxiv.org/abs/2609.00291) | StreamScout: Learning When to Look Deeper for Streaming Video Understanding | 2026-08-31 | 知识蒸馏 | OVO-Bench 上 Qwen3-VL-8B 提高 14.65 分、token 少 59%，平均回答时间 1.04 秒。 | 8 | 7 | 8 | 7 |
| 51 | [2609.00355](https://arxiv.org/abs/2609.00355) | Vision Is Not Overhead: One-Pass Block Drafting for Lossless Speculative Decoding in Vision-Language Models | 2026-08-31 | 其他压缩与高效推理 | 同引擎同轮预算下最高比自回归快 2.93×，接受块长为同语料 EAGLE-3 的 2.7×。 | 8 | 8 | 7 | 7 |
| 52 | [2609.00421](https://arxiv.org/abs/2609.00421) | VARA: A Voltage-Aware ReRAM-Based Accelerator for Energy-Efficient Computing | 2026-08-31 | 剪枝/稀疏化 | 平均系统能耗降低 60.12%，能效提高 2.68×，准确率仅边际下降。 | 8 | 8 | 8 | 7 |
| 53 | [2609.00446](https://arxiv.org/abs/2609.00446) | CRAD: Class-wise Reliability-Aware Distillation for Decentralized Heterogeneous Federated Learning | 2026-08-31 | 知识蒸馏 | CIFAR-10/100 与 PathMNIST 的异构架构、严重 non-IID 设置中，全局准确率持续优于对比方法。 | 8 | 7 | 8 | 7 |
| 54 | [2609.00450](https://arxiv.org/abs/2609.00450) | HBQ: Hierarchical Scaling Block Quantization with Hardware-Efficiency-Aware Design for Accurate LLM Inference | 2026-08-31 | 量化 | HBQ-E 硬件成本再降 17%；相同准确率下面积/能效提高 2.3×/4.6×，系统加速 1.5–3.0×。 | 8 | 8 | 8 | 7 |
| 55 | [2609.00474](https://arxiv.org/abs/2609.00474) | Exploring Collaboration between a language and a non-language agent | 2026-08-31 | 其他压缩与高效推理 | 4B 到 14B 都存在 verbalization debt；14B LLAMIA 在六项棋类协作任务达到或超过专用/前沿模型。 | 8 | 8 | 7 | 7 |
| 56 | [2609.00489](https://arxiv.org/abs/2609.00489) | A hybrid quantum-classical neural network for learning to route | 2026-08-31 | 其他压缩与高效推理 | 前馈模块替换使参数量减少 56.6%，中小规模路由实例接近经典神经基线，但大实例差距扩大。 | 8 | 8 | 7 | 7 |

## 5. Qwen3-0.6B 量化复现

量化方向共 7 篇：2609.00665, 2609.00718, 2609.01084, 2609.01200, 2609.01587, 2609.00224, 2609.00450。每篇在 `scripts/quantization/<id>/` 提供 README 与 demo；公共工具直接读取本地 Qwen3-0.6B safetensors 的真实权重/表示，不下载模型。验证覆盖语法、导入与真实张量小规模运行；不声称复现论文的大模型训练、驾驶闭环、标准 NNC 位流或专用边缘硬件。

| arXiv | 缩小实现 | 本次实测关键结果 | 验证 |
|---|---|---|---|
| 2609.00224 | 逐列三值 + 显著列 1:4 残差 | MSE 0.00031394 → 0.00024124；relative L2 0.58092 → 0.50923 | PASS |
| 2609.00450 | block-256 W4 + 4-bit significand 二级尺度 | PoT/SIG MSE 1.881e-5/1.604e-5；SIG 确认改善 | PASS |
| 2609.00665 | BF16/INT8/NF4/group-W4 多精度比较 | 估算压缩 1.925×/3.556×/3.710×；cosine 0.999981/0.995658/0.994532 | PASS |
| 2609.00718 | 25% 结构化行剪枝 + rank-16 教师残差 + INT8 | 输出 relative L2：0.33880 → 0.29469 → 0.29470 | PASS |
| 2609.01084 | rank-8 + INT8 KV；中心化 INT4 delta | KV cosine 0.999987、1.441×；FFN 代理 cosine 0.994754、3.697× | PASS |
| 2609.01200 | rank-64 变换 + INT8 表示编码 | 估算 5.971×；cosine 0.710514，显示高倍率下损失明显 | PASS |
| 2609.01587 | 局部 W8 修复 vs 全局 group-32 W4 | 全局预算高 9.09%；累计 MSE 4.827e-5，低于局部 6.501e-5 | PASS |

## 6. 证据边界

- 本次不使用 arXiv 官方 API；官方分类 HTML 是召回源，`/abs` v1 history 是归日依据。
- 论文精读均含六个规定章节；实验数字来自官方摘要/全文，未报告的信息明确留空。
- 第三方索引未替代官方分类页或 `/abs` 页面。
