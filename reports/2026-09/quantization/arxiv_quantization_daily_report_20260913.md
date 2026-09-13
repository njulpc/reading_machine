# arXiv 模型压缩论文日报

日报主日期：2026-09-13；运行日：2026-09-14；核验时间：2026-09-14T01:12:48.780524+08:00。

检索窗口：北京时间 **2026-09-11 00:00–2026-09-13 23:59**（三个完整自然日）。以官方 abs 的 Submission history 中 v1 转北京时间归日，公告日不替代投稿日。

## 1. 结果与范围

| 提交日（北京时间） | 全主题可见 | 相关（历史去重前） | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-09-11 | 50 | 3 | 0 | 3 |
| 2026-09-12 | 0 | 0 | 0 | 0 |
| 2026-09-13 | 0 | 0 | 0 | 0 |

窗口相关总数3，历史重复0，本次新增3。9月12、13日仅能表述为“**截至运行时 arXiv 官方网页未检出**”，不代表后台或后续公告的最终投稿数为零。后续三天窗口继续回查。

纳入教师—学生压缩、模型权重低秩分解、多专家能力合并；普通数据/文本/检索压缩、KV卸载、未实施模型压缩的训练优化不纳入。BF16训练本身不作为量化论文。

## 2. 完整相关论文表

| ID / 论文 | v1 UTC | 北京时间 | 分类 | 一句话结论 |
|---|---|---|---|---|
| [2609.11768 · A Unified Per-Token Gating Family for On-Policy Distillation: FKL/RKL Mixing with Multi-Channel and Bias Coefficients](https://arxiv.org/abs/2609.11768) | 2026-09-10T16:22:35Z | 2026-09-11T00:22:35+08:00 | knowledge_distillation；Artificial Intelligence (cs.AI) ; Computation and Language (cs.CL); Machine Learning (cs.LG) | 四参数门控有方向性收益，但三种子优势未达显著。 |
| [2609.11876 · On the Regularization Landscape for the Linear Recommendation Models](https://arxiv.org/abs/2609.11876) | 2026-09-10T17:45:06Z | 2026-09-11T01:45:06+08:00 | other；Artificial Intelligence (cs.AI) | 低秩闭式解在两数据集接近全秩效果，MSD仍有损失。 |
| [2609.11929 · SenseNova-U1.5: Towards Native Unified Visual Intelligence](https://arxiv.org/abs/2609.11929) | 2026-09-10T17:59:55Z | 2026-09-11T01:59:55+08:00 | knowledge_distillation；Computer Vision and Pattern Recognition (cs.CV) | 四专家速度场蒸馏进单学生，部署压缩倍率尚未实测。 |

## 3. 评分与依据

分数为本次阅读者判断，范围1–10，越高越好；压缩分同时考虑证据充分性，未实测倍率不因理论参数比而给满分。

| ID | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 依据（依次对应四项） |
|---|---:|---:|---:|---:|---|
| 2609.11768 | 5 | 7 | 6 | 4 | 三种子单格优势不显著，p≥0.29；32B/4B名义参数比8，未测部署倍率；统一门控坐标与平均KL匹配实验清晰；内部训练栈未开源，6×80GB配置较重 |
| 2609.11876 | 7 | 6 | 7 | 7 | 两数据集nDCG追平全秩，MSD仍下降0.008；因子存储理论n/(2k)，无实测整机倍率；输出加权低秩投影与正则化统一分析；闭式公式明确，完整推荐实验未本机运行 |
| 2609.11929 | 7 | 4 | 7 | 4 | 完整系统ImgEdit4.59但无蒸馏隔离消融；四专家合并单学生，整机倍率未测；学生轨迹速度场蒸馏与时间课程；训练步骤充分披露，数据/专家权重完整可用性未验证 |

## 4. 官方全量召回证据

五分类new/recent各完整下载一次，show=2000覆盖每页全部条目，无默认首屏截断；new同时覆盖新投稿、交叉投稿和替换。跨日期/分类合并后3,080个规范ID；官方abs本次全部重新下载并成功解析标题、摘要、分类和v1，失败0。与上次字段逐一相等，但本次日期判断来自重新读取的abs。未使用arXiv官方API。

窗口内50篇全部逐篇阅读标题和摘要；7篇候选/边界阅读官方HTML全文。窗口外记录按v1日期排除，未声称人工重新精读全部3,080篇。关键词仅复核，不构成召回门槛：quantization/quantize/low-bit/model compression/compress/pruning/sparsity/knowledge distillation/distill/teacher/student/KV cache compression/mixed precision/GPTQ/AWQ及同义表达。

| 分类/入口 | 声明=实际 | 覆盖 | 页面分组 |
|---|---:|---|---|
| [cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000) | 268 | 1–268，show=2000 | Showing new listings for Friday, 11 September 2026；New submissions (showing 73 of 73 entries)；Cross submissions (showing 98 of 98 entries)；Replacement submissions (showing 97 of 97 entries) |
| [cs.LG recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 1086 | 1–1086，show=2000 | Fri, 11 Sep 2026 (showing 171 of 171 entries )；Thu, 10 Sep 2026 (showing 163 of 163 entries )；Wed, 9 Sep 2026 (showing 447 of 447 entries )；Mon, 7 Sep 2026 (showing 137 of 137 entries )；Fri, 4 Sep 2026 (showing 168 of 168 entries ) |
| [cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000) | 155 | 1–155，show=2000 | Showing new listings for Friday, 11 September 2026；New submissions (showing 59 of 59 entries)；Cross submissions (showing 32 of 32 entries)；Replacement submissions (showing 64 of 64 entries) |
| [cs.CL recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 655 | 1–655，show=2000 | Fri, 11 Sep 2026 (showing 91 of 91 entries )；Thu, 10 Sep 2026 (showing 94 of 94 entries )；Wed, 9 Sep 2026 (showing 257 of 257 entries )；Mon, 7 Sep 2026 (showing 98 of 98 entries )；Fri, 4 Sep 2026 (showing 115 of 115 entries ) |
| [cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000) | 158 | 1–158，show=2000 | Showing new listings for Friday, 11 September 2026；New submissions (showing 75 of 75 entries)；Cross submissions (showing 14 of 14 entries)；Replacement submissions (showing 69 of 69 entries) |
| [cs.CV recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 776 | 1–776，show=2000 | Fri, 11 Sep 2026 (showing 89 of 89 entries )；Thu, 10 Sep 2026 (showing 106 of 106 entries )；Wed, 9 Sep 2026 (showing 359 of 359 entries )；Mon, 7 Sep 2026 (showing 110 of 110 entries )；Fri, 4 Sep 2026 (showing 112 of 112 entries ) |
| [cs.AI new](https://arxiv.org/list/cs.AI/new?show=2000) | 273 | 1–273，show=2000 | Showing new listings for Friday, 11 September 2026；New submissions (showing 77 of 77 entries)；Cross submissions (showing 94 of 94 entries)；Replacement submissions (showing 102 of 102 entries) |
| [cs.AI recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1208 | 1–1208，show=2000 | Fri, 11 Sep 2026 (showing 171 of 171 entries )；Thu, 10 Sep 2026 (showing 150 of 150 entries )；Wed, 9 Sep 2026 (showing 517 of 517 entries )；Mon, 7 Sep 2026 (showing 205 of 205 entries )；Fri, 4 Sep 2026 (showing 165 of 165 entries ) |
| [cs.AR new](https://arxiv.org/list/cs.AR/new?show=2000) | 15 | 1–15，show=2000 | Showing new listings for Friday, 11 September 2026；New submissions (showing 7 of 7 entries)；Cross submissions (showing 5 of 5 entries)；Replacement submissions (showing 3 of 3 entries) |
| [cs.AR recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 77 | 1–77，show=2000 | Fri, 11 Sep 2026 (showing 12 of 12 entries )；Thu, 10 Sep 2026 (showing 17 of 17 entries )；Wed, 9 Sep 2026 (showing 25 of 25 entries )；Mon, 7 Sep 2026 (showing 14 of 14 entries )；Fri, 4 Sep 2026 (showing 9 of 9 entries ) |

所有recent页显示9月4、7、9、10、11日公告分组；每组showing数量完整。目标窗口前一自然日9月10日可见366条v1作为阳性对照。以下官方记录核对北京时间午夜边界：

- [2609.11736](https://arxiv.org/abs/2609.11736)：v1 2026-09-10T15:52:28Z → 2026-09-10T23:52:28+08:00。
- [2609.11737](https://arxiv.org/abs/2609.11737)：v1 2026-09-10T15:52:35Z → 2026-09-10T23:52:35+08:00。
- [2609.11739](https://arxiv.org/abs/2609.11739)：v1 2026-09-10T15:53:25Z → 2026-09-10T23:53:25+08:00。
- [2609.11744](https://arxiv.org/abs/2609.11744)：v1 2026-09-10T16:00:35Z → 2026-09-11T00:00:35+08:00。
- [2609.11749](https://arxiv.org/abs/2609.11749)：v1 2026-09-10T16:03:35Z → 2026-09-11T00:03:35+08:00。
- [2609.11752](https://arxiv.org/abs/2609.11752)：v1 2026-09-10T16:08:54Z → 2026-09-11T00:08:54+08:00。

## 5. 历史去重审计

fetch --prune成功后逐一ls-tree扫描40个历史日更远端分支，并git show读取各分支papers_index.json。真实tech_analysis.md规范ID共527；metadata规范ID共530。仅metadata存在的2607.27951、2607.28410、2607.28457未计为完成。

历史重复ID与来源分支：**无**。最终新增ID：2609.11768、2609.11876、2609.11929；与历史527个ID交集为空。当前2026-09-14分支为从origin/main新建，不作为历史；未推送的其他本地日期worktree不冒充已完成远端成果。

完整扫描来源：

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

## 6. 语义排除审计

| ID | 标题 | 判定 |
|---|---|---|
| [2609.11744](https://arxiv.org/abs/2609.11744) | Building py-kvcache: A Performance Characterization of External KV Caching for vLLM with NVMe SSDs | KV状态跨GPU/CPU/NVMe卸载与复用，未量化/裁剪KV。 |
| [2609.11749](https://arxiv.org/abs/2609.11749) | Sparsity Regularized and Robust Mean Variance Portfolio Selection Under Ellipsoidal Uncertainty | 稀疏资产组合与分支定界剪枝，不是神经模型压缩。 |
| [2609.11752](https://arxiv.org/abs/2609.11752) | SIRF: A Spec-Internalized Risk Foundation Model for Industrial Content Risk Control | 同规模8B继续预训练的政策内化，未压缩模型。 |
| [2609.11758](https://arxiv.org/abs/2609.11758) | RAG-Safety-Bench: Reliable Evaluation of Retrieval-Augmented LLM Safety | RAG安全基准。 |
| [2609.11762](https://arxiv.org/abs/2609.11762) | Component-Aware Differential Privacy for Federated Multilingual Speech-LLMs | 差分隐私预算分配，不压缩模型。 |
| [2609.11769](https://arxiv.org/abs/2609.11769) | Recognizing Is Not Reversing: A Controlled Inversion Test of Fact-Preserving News Framing | 新闻框架逆变换评价。 |
| [2609.11770](https://arxiv.org/abs/2609.11770) | The widening evaluation gap in medical large language model research 2023 to 2026 | 医学LLM研究时效审计。 |
| [2609.11772](https://arxiv.org/abs/2609.11772) | Whisper-Based Speech Transcription from Videos Across Multiple Languages for Cross-Cultural Understanding | Whisper转录微调。 |
| [2609.11777](https://arxiv.org/abs/2609.11777) | Differentially Private EEG Feature Anonymization: A Privacy-Utility Case Study in Clinical Neurophysiology | EEG特征差分隐私。 |
| [2609.11780](https://arxiv.org/abs/2609.11780) | Predicting Privacy Leakage from Weight Spectral Density | 权重谱用于隐私审计，未低秩压缩权重。 |
| [2609.11786](https://arxiv.org/abs/2609.11786) | Beyond Word Error Rate: A Switch Aware Evaluation of ASR and Audio Language Models on English Yoruba Code-Switched Speech | 语码切换ASR评价。 |
| [2609.11790](https://arxiv.org/abs/2609.11790) | Dynamic language model representations for multi-objective reaction optimisation | 化学反应优化的语言表示。 |
| [2609.11799](https://arxiv.org/abs/2609.11799) | SpecGuard: Inference-Time Backdoor Detection For Free | 复用投机解码信号检测后门，未提出压缩或草稿蒸馏。 |
| [2609.11801](https://arxiv.org/abs/2609.11801) | Thinking with Looped Flows | 全文复核：共享循环网络上改善推理训练；不是压缩既有模型，ACT为训练饱和停止；留作相关背景。 |
| [2609.11804](https://arxiv.org/abs/2609.11804) | Logit Refiner: Improving Visual Autoregressive Models via Intra-Scale Dependency Modeling | 向冻结VAR追加约10%参数改善采样，不压缩原模型。 |
| [2609.11805](https://arxiv.org/abs/2609.11805) | Understanding Operator Attitudes Toward AI-Supported Decision Making in Maritime Operations | 海事从业者态度调查。 |
| [2609.11807](https://arxiv.org/abs/2609.11807) | Near-Optimal Reinforcement Learning with Multi-Step Transition Lookahead | RL多步前瞻算法。 |
| [2609.11838](https://arxiv.org/abs/2609.11838) | Target leakage, not model class, explains reported accuracy in survey-based cardiovascular screening: a leakage-tiered audit of glass-box and tabular foundation models | 医疗筛查数据泄漏审计与模型比较。 |
| [2609.11842](https://arxiv.org/abs/2609.11842) | Model-Aware Schedules Improve Generation via Fiberwise Optimal Transport | 训练噪声时间分配优化，不做少步蒸馏或模型压缩。 |
| [2609.11851](https://arxiv.org/abs/2609.11851) | IndicTriMix: Developing Language Identification Datasets and Models for Tri-Language Code-Mixing | 语种识别数据集与微调。 |
| [2609.11859](https://arxiv.org/abs/2609.11859) | From Parameters to Answers: How LLMs Retrieve and Use Their Internal Knowledge | 内部知识检索的机制干预。 |
| [2609.11860](https://arxiv.org/abs/2609.11860) | Explainability Assistant: A Conversational XAI Interface for Interpreting Energy Consumption Models | 对话式可解释性界面。 |
| [2609.11864](https://arxiv.org/abs/2609.11864) | RetroThinker: Enabling Retrospective Thinking in Speech LLMs | 语音LLM回溯推理SFT/DPO，不压缩模型。 |
| [2609.11865](https://arxiv.org/abs/2609.11865) | Epistemic orientation predicts legislative effectiveness among members of the US Congress | 议员语言与立法效果研究。 |
| [2609.11867](https://arxiv.org/abs/2609.11867) | AdamX: Cosine similarity meets gradient descent | 优化器。 |
| [2609.11870](https://arxiv.org/abs/2609.11870) | Augustinian BabyLM: What Ostensive Definition Can and Cannot Teach a Small Language Model | 小语言模型视觉初始化，非教师蒸馏压缩。 |
| [2609.11872](https://arxiv.org/abs/2609.11872) | Evaluating Time-Series Foundation Models and Multimodal Dietary Context for CGM Forecasting | 血糖预测基准和微调。 |
| [2609.11873](https://arxiv.org/abs/2609.11873) | The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement | 递归自我改进路线讨论。 |
| [2609.11877](https://arxiv.org/abs/2609.11877) | Biology-in-the-loop: Amortized Adaptive Hit Discovery in CRISPR Screens | CRISPR实验主动采样。 |
| [2609.11878](https://arxiv.org/abs/2609.11878) | Domain-Specific Hallucination Detection in Large Language Models | 幻觉检测与DPO，不压缩生成模型。 |
| [2609.11884](https://arxiv.org/abs/2609.11884) | CoRA-NAS: Coarse Ranking and Anchor-Residual Refinement for Neural Architecture Search | 降低NAS搜索评价成本，未以模型压缩/部署预算为目标。 |
| [2609.11886](https://arxiv.org/abs/2609.11886) | Guided Super-Resolution of Digital Elevation Models with Diffusion-Based Image Generators | DSM超分辨率。 |
| [2609.11892](https://arxiv.org/abs/2609.11892) | Nuha-Speech: Building General-Purpose Arabic Speech-LLMs | 阿拉伯语音模型数据与微调。 |
| [2609.11894](https://arxiv.org/abs/2609.11894) | 3D Point Splatting for mmWave Radar Novel View Synthesis | 雷达物理点渲染，不是神经模型压缩。 |
| [2609.11897](https://arxiv.org/abs/2609.11897) | CausalArena: Benchmarking Causal Discovery in the Foundation Model Era | 因果发现基准。 |
| [2609.11899](https://arxiv.org/abs/2609.11899) | Caption-once, Frames-on-Demand: Visual-Need Routing for Budget-Aware Agentic Long Video Understanding | 全文复核：外部字幕索引和按需帧检索；作者将模型量化留给未来工作。 |
| [2609.11900](https://arxiv.org/abs/2609.11900) | MindTopo: Can Foundation Models Reason in Topological Space? | 空间拓扑推理基准。 |
| [2609.11904](https://arxiv.org/abs/2609.11904) | TART: A Modular Tool for Technique-Aware Audio-to-Tablature Guitar Transcription | 吉他转录流水线。 |
| [2609.11906](https://arxiv.org/abs/2609.11906) | AccelForge: Comprehensive Modeling and Co-Design Framework for AI Accelerators | 全文复核：通用加速器建模框架，bitwidth为配置示例，无新增压缩方法或量化评估。 |
| [2609.11910](https://arxiv.org/abs/2609.11910) | From Protocols to Evidence: Bounded Claims for AI in Service of the Common Good | AI治理证据框架。 |
| [2609.11911](https://arxiv.org/abs/2609.11911) | Artificial Id: Drive and Persistent Alignment in Agentic AI | 持续代理驱动和对齐。 |
| [2609.11913](https://arxiv.org/abs/2609.11913) | Distance generalization in transformers: why bother with positional encoding? | 位置编码距离泛化。 |
| [2609.11915](https://arxiv.org/abs/2609.11915) | Generative Marketing Mix Modeling: A Causal Inference Framework Linking GEO and GEM to Business Impact | 营销因果建模。 |
| [2609.11916](https://arxiv.org/abs/2609.11916) | Can Edge-Deployable Vision-Language Models Identify Species? | 小型VLM物种识别基准，未实际压缩。 |
| [2609.11917](https://arxiv.org/abs/2609.11917) | Data Scarcity and Model Sparsity: Mixtures-of-Experts Overfit More to Repeated Data | 全文复核：从头训练稀疏MoE的数据重复/正则化研究；掩码是训练正则而非永久剪枝，不计压缩论文。 |
| [2609.11918](https://arxiv.org/abs/2609.11918) | General Quantification of Covariate and Concept Shifts | 分布漂移量化（quantification）理论，非低比特量化。 |
| [2609.11923](https://arxiv.org/abs/2609.11923) | GPU-CFR: 80x Faster Counterfactual Regret Minimization by Compiling the Game to Static Dataflow and CUDA Graph Replay | CFR静态编译与GPU执行，非神经模型压缩。 |

边界证据：CFD正文明确把手机模型量化留作未来工作；AccelForge仅以bitwidth配置说明扩展性；MoE论文的随机输出mask为训练正则化，未永久删除参数；Looped Flows用既有小型循环网络增加推理深度，本次不将其作为压缩已训练模型的论文计数。

## 7. 精读、复现与独立快照

三份精读均包含指定六节，按v1实际提交月份写入papers/2026-09。新增量化0，无Qwen3-0.6B量化复现义务；scripts/quantization不存在，没有占位demo。三篇原论文的大规模训练均未本机复现，其证据与资源限制在精读中明确。

严格从origin/main `abfe8f2767d8bf881d586718ab4db33fc576be6a`创建`feature/arxiv-daily-2026-09-14`。隔离worktree清理main的2026-07-28旧日报；papers只保留README和本次3篇，reports只README和本日报，scripts只通用README，metadata只README和2026-09本次3篇JSON/CSV。原工作树未提交文件受保护。

提交前验证项目：论文目录/metadata/CSV ID一致、与历史零交集、窗口日期、六节分析、无历史复现与旧日报、git diff --check。提交后检查单提交基线和远端SHA，结果见运行汇报。
