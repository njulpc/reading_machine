# arXiv 模型压缩论文日报：2026-09-28

运行日：2026-09-29（Asia/Shanghai）；记录时间：2026-09-29T01:21:06.438043+08:00。
固定检索三天：**09-26 00:00–09-28 23:59:59 北京时间**。日报主日期09-28，论文按v1实际提交时间归日、归月，公告日期不替代提交日期。未使用arXiv API。

## 结果与口径

| 北京时间日期 | 窗口各主题记录 | 相关论文（跨分类去重） | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-09-26 | 58 | 7 | 0 | 7 |
| 2026-09-27 | 0 | 0 | 0 | 0 |
| 2026-09-28 | 0 | 0 | 0 | 0 |
| 合计 | 58 | 7 | 0 | 7 |

09-27/28均为“截至运行时 arXiv 官方网页未检出”，不是保证最终无投稿。列表最近公告为09-28；后续三天窗口继续回查公告延迟。

纳入2篇量化/权重压缩、3篇蒸馏、2篇稀疏计算。BSD压缩内部状态，Scaffold稀疏GNN消息图，DeepEdu减少选择/注意力开销，均明确区别于权重体积压缩。普通prompt压缩、LoRA适配、从头小网络以及多SLM聚合不因含有“compact/teacher/pruning”而自动纳入。

## 新增论文完整表

| ID | 标题 | v1北京时间（均09-26） | 主/交叉分类 | 技术方向 |
|---|---|---|---|---|
| [2609.31560](https://arxiv.org/abs/2609.31560) | Generalization behavior of OPTQ and the role of regularization | 01:27:18 | Machine Learning (cs.LG) | quantization |
| [2609.31564](https://arxiv.org/abs/2609.31564) | Weight Pair Encoding: Inducing a Smaller Grammar in Neural Network Weights | 01:29:43 | Machine Learning (cs.LG) | quantization |
| [2609.31568](https://arxiv.org/abs/2609.31568) | DeepEdu-v1: Efficient and Scalable Agentic LLMs for Vietnamese Education | 01:33:41 | Artificial Intelligence (cs.AI) | pruning |
| [2609.31571](https://arxiv.org/abs/2609.31571) | Strategically Diverse Sampling for Self-Training | 01:35:05 | Computation and Language (cs.CL) | knowledge_distillation |
| [2609.31524](https://arxiv.org/abs/2609.31524) | Structured Reasoning Agentic Framework for Interpretable Critical View of Safety Assessment | 01:01:56 | Computer Vision and Pattern Recognition (cs.CV) | knowledge_distillation |
| [2609.31603](https://arxiv.org/abs/2609.31603) | User Model Extraction via Belief Self-Distillation | 01:54:32 | Machine Learning (cs.LG) ; Computation and Language (cs.CL) | knowledge_distillation |
| [2609.31466](https://arxiv.org/abs/2609.31466) | Scaffold: Support Graph Theory Based Sparsification for Graph Neural Networks | 00:17:09 | Machine Learning (cs.LG) | pruning |

## 四维评分与结论

分数是本次阅读判断，均为1–10、越高越强；“压缩”评分反映实际资源节省的证据强度，未报告的倍率不补造。

| ID | 精度效果 | 压缩倍率证据 | 创新性 | 可复现性 | 一句话结论 |
|---|---:|---:|---:|---:|---|
| 2609.31560 | 7 | 5 | 8 | 8 | 用正则化经验二次型控制总体量化误差，提出 λ=β||X||F²/[m^(1/3)min(m,N)^(2/3)]；这不是一种新的低比特格式，也没有证明 β=1 在所有真实 LLM 上最优。 |
| 2609.31564 | 7 | 7 | 8 | 6 | WeightPE把受全局L2预算约束的有损Re-Pair改写放入STE，使ViT的MLP权重语法比对应INT8 QAT基线更小；语法符号数减少不等于部署文件字节或推理延迟同倍下降。 |
| 2609.31568 | 7 | 5 | 7 | 6 | DeepEdu-v1/SCALE的SCR将相似连续query子块聚类，按簇执行一次top-k检索，减少重复选择开销；核心长上下文实验是BF16，不是一项新的AWQ/GPTQ量化算法。 |
| 2609.31571 | 8 | 4 | 8 | 6 | GROOT与VS先生成不同解题策略，再生成正常推理轨迹；4B学生自身的策略多样性可优于235B教师的IID蒸馏，提示“更大教师”不必然给出更好的压缩训练数据。 |
| 2609.31524 | 8 | 2 | 7 | 5 | ReasonCVS让Gemini-3-pro基于观察和正确标签生成理由，再以LoRA训练Qwen-3 32B，Endoscapes-CVS201达68.1% mAP；论文证明的是任务能力转移，而非已量化的模型压缩倍率。 |
| 2609.31603 | 7 | 4 | 8 | 7 | BSD用128维瓶颈保留并可写回LLM的用户信念，32倍是隐状态维度压缩；教师和学生是同一个冻结模型的副本，不是将8B网络压成更小学生。 |
| 2609.31466 | 8 | 6 | 8 | 7 | Scaffold用路径伸长与拥塞选择保留边，以减少消息传递成本；它压缩的是GNN计算支撑图，不是剪掉模型权重。 |

### 2609.31560 评分依据

- accuracy 7/10：有理论泛化界与三种合成分布，但无LLM困惑度实验
- compression 5/10：只改善量化校准，不提出额外压缩倍率
- innovation 8/10：把经验误差与总体误差分开并导出随m变化的正则
- reproducibility 8/10：完整公式及作者代码链接，本次实跑Qwen局部验证

### 2609.31564 评分依据

- accuracy 7/10：ViT/CIFAR-10有精度与压缩权衡，跨任务尚未验证
- compression 7/10：MLP语法符号约0.43倍，非全模型字节倍率
- innovation 8/10：把有损语法改写放入STE并共享层间模式
- reproducibility 6/10：附录完整算法但部分实现约定不明，本次局部Qwen移植

### 2609.31568 评分依据

- accuracy 7/10：有长上下文基准，但配置间精度不能拼接
- compression 5/10：减少检索调用和稀疏计算，不证明常驻KV压缩
- innovation 7/10：固定anchor共享检索并保留簇内因果注意力
- reproducibility 6/10：算法预算完整，H100/SGLang/FlashInfer环境未运行

### 2609.31571 评分依据

- accuracy 8/10：跨代码与NCP及三seed，frontier子集不可替代总体
- compression 4/10：学生仍4B；235B/4B不是实测部署倍率
- innovation 8/10：策略层多样性比IID样本数更关键
- reproducibility 6/10：训练参数详尽，但大教师/数据生成/RL未本机运行

### 2609.31524 评分依据

- accuracy 8/10：mAP与消融有提升，单数据集及小临床评分样本
- compression 2/10：32B学生未给教师规模/部署压缩实测
- innovation 7/10：结构化观察+教师理由蒸馏连接证据与判断
- reproducibility 5/10：参数公开，但教师生成语料及完整H200系统未复现

### 2609.31603 评分依据

- accuracy 7/10：读出信息基本保留，干预存在跨属性泄漏
- compression 4/10：32倍仅4096维隐状态到128维向量，模型大小不变
- innovation 8/10：把KL蒸馏与可写低秩状态联合训练
- reproducibility 7/10：开源链接和rank/优化器设置齐全，未训练三模型

### 2609.31466 评分依据

- accuracy 8/10：19数据集及匹配边预算，但部分图差距明显
- compression 6/10：减少GNN消息边，不减少权重；SpMM端到端不总更快
- innovation 8/10：联合路径伸长与拥塞的无监督稀疏支撑
- reproducibility 7/10：开源/预算/复杂度充分，本次未跑H100图训练

## 检索覆盖与提交时间证据

五分类new/recent共10页均本次获取，show=2000、skip=0，页面总数=解析条目数=分组条目数之和；均小于2000，单页已覆盖完整返回列表，不只读默认首屏。new包含new submissions、cross submissions以及replacement；跨列表5065次出现去重为3333个规范ID。

| 官方入口 | 声明/实取 | 分组与覆盖 |
|---|---:|---|
| [页面](https://arxiv.org/list/cs.LG/new?show=2000) | 332/332 | Showing new listings for Monday, 28 September 2026；New submissions (showing 123 of 123 entries)；Cross submissions (showing 79 of 79 entries)；Replacement submissions (showing 130 of 130 entries) |
| [页面](https://arxiv.org/list/cs.LG/recent?show=2000) | 1283/1283 | Mon, 28 Sep 2026 (showing 202 of 202 entries )；Fri, 25 Sep 2026 (showing 230 of 230 entries )；Thu, 24 Sep 2026 (showing 209 of 209 entries )；Wed, 23 Sep 2026 (showing 216 of 216 entries )；Tue, 22 Sep 2026 (showing 426 of 426 entries ) |
| [页面](https://arxiv.org/list/cs.CL/new?show=2000) | 132/132 | Showing new listings for Monday, 28 September 2026；New submissions (showing 61 of 61 entries)；Cross submissions (showing 28 of 28 entries)；Replacement submissions (showing 43 of 43 entries) |
| [页面](https://arxiv.org/list/cs.CL/recent?show=2000) | 661/661 | Mon, 28 Sep 2026 (showing 89 of 89 entries )；Fri, 25 Sep 2026 (showing 126 of 126 entries )；Thu, 24 Sep 2026 (showing 105 of 105 entries )；Wed, 23 Sep 2026 (showing 108 of 108 entries )；Tue, 22 Sep 2026 (showing 233 of 233 entries ) |
| [页面](https://arxiv.org/list/cs.CV/new?show=2000) | 182/182 | Showing new listings for Monday, 28 September 2026；New submissions (showing 87 of 87 entries)；Cross submissions (showing 27 of 27 entries)；Replacement submissions (showing 68 of 68 entries) |
| [页面](https://arxiv.org/list/cs.CV/recent?show=2000) | 800/800 | Mon, 28 Sep 2026 (showing 114 of 114 entries )；Fri, 25 Sep 2026 (showing 143 of 143 entries )；Thu, 24 Sep 2026 (showing 128 of 128 entries )；Wed, 23 Sep 2026 (showing 143 of 143 entries )；Tue, 22 Sep 2026 (showing 272 of 272 entries ) |
| [页面](https://arxiv.org/list/cs.AI/new?show=2000) | 331/331 | Showing new listings for Monday, 28 September 2026；New submissions (showing 88 of 88 entries)；Cross submissions (showing 113 of 113 entries)；Replacement submissions (showing 130 of 130 entries) |
| [页面](https://arxiv.org/list/cs.AI/recent?show=2000) | 1278/1278 | Mon, 28 Sep 2026 (showing 201 of 201 entries )；Fri, 25 Sep 2026 (showing 260 of 260 entries )；Thu, 24 Sep 2026 (showing 193 of 193 entries )；Wed, 23 Sep 2026 (showing 240 of 240 entries )；Tue, 22 Sep 2026 (showing 384 of 384 entries ) |
| [页面](https://arxiv.org/list/cs.AR/new?show=2000) | 4/4 | Showing new listings for Monday, 28 September 2026；New submissions (showing 1 of 1 entries)；Cross submissions (showing 3 of 3 entries) |
| [页面](https://arxiv.org/list/cs.AR/recent?show=2000) | 62/62 | Mon, 28 Sep 2026 (showing 4 of 4 entries )；Fri, 25 Sep 2026 (showing 15 of 15 entries )；Thu, 24 Sep 2026 (showing 14 of 14 entries )；Wed, 23 Sep 2026 (showing 10 of 10 entries )；Tue, 22 Sep 2026 (showing 19 of 19 entries ) |

3333个ID均成功读取/解析官方abs标题、摘要、分类及Submission history的v1，解析失败0。其中719页本次下载，2614页复用09-28已保存的官方HTML并重新解析v1；58篇窗口记录全部是本次下载。缓存使用透明记录，不能表述为3333页全部重新请求。

阳性对照：
- [2609.31435](https://arxiv.org/abs/2609.31435)：v1 09-25 15:57:02 UTC = 北京时间09-25 23:57:02，窗口外。
- [2609.31448](https://arxiv.org/abs/2609.31448)：v1 09-25 16:06:29 UTC = 北京时间09-26 00:06:29，窗口内（但主题排除）。

窗口外相邻09-25有463个各主题ID，证明解析与日期边界不是“所有日期均为0”。3275个窗口外条目先按v1排除，不声称人工逐篇精读全部旧稿。窗口内58篇全部读标题摘要；10篇候选/边界论文读官方HTML方法与实验，7篇纳入、3篇排除。原始HTML、完整列表ID和详情解析证据本次保存在 /private/tmp/arxiv_20260929；此路径是临时审计缓存，不是持久发布附件。

关键词仅辅助核查，未作召回门槛；检查quantization、quantize、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache、mixed precision、GPTQ、AWQ，并扩展QAT/PTQ/INT8/INT4/sparse/low-rank。逐词命中计数见metadata的keyword_review。

## 历史去重审计

fetch --prune origin成功。遍历**44个**origin/feature/arxiv-daily-*，每个均执行ls-tree并读取metadata索引，实际tech_analysis路径给出**543个**规范ID（去掉v版本）；metadata的papers数组共546个ID。只有metadata的2607.27951、2607.28410、2607.28457不算完成。没有把metadata中的排除审计ID误算为论文成果。

git ls-remote全集与扫描分支名称/SHA逐一相等；完整44个来源分支及SHA见metadata.dedup_source_branches。今日远端分支原先不存在，本次独立创建；09-28未提交草稿不当成已完成历史远端成果。

本窗口相关去重后7篇，历史重复ID=[]，重复来源分支={}；最终新增ID：2609.31560、2609.31564、2609.31568、2609.31571、2609.31524、2609.31603、2609.31466。新增与543个历史已分析ID交集为空。

## 真实量化代码与运行

两目录均含README.md、demo.py、results.json，模型为Qwen/Qwen3-0.6B、revision c1899de289a04d12100db370d81485cdf75e47ca。环境Python3.9.6、torch2.8.0、transformers4.57.6、CPU4线程（WeightPE NumPy2.0.2）。先前使用模型名的tokenizer加载即使local_files_only仍尝试联网，已改为解析缓存snapshot后传入本地路径，随后两项运行成功。

- `scripts/quantization/2609.31560/`：首层gate_proj真实32×1024行子集、54校准/21测试token。实现式12–15及式35，m=16/54，对照旧λ，确定性/随机和有限W4。m54确定性测试相对L2旧0.091047、新0.091823；随机旧0.123657、新0.116477。独立尾部求解与增广目标测试误差0、随机舍入均值误差0.00436。此小样本不支持新λ处处更优。
- `scripts/quantization/2609.31564/`：首层gate/up各4行、完整1024列，共8×1024，35校准/14测试token，11步真实AdamW/STE更新。共享语法、失真预算、行边界、leader筛选、批量merge均实现；符号比0.705202，测试相对L2 0.106052（QAT0.005041），权重变化L2 0.009611。论文worked example、解码、行边界和STE测试通过。比例到绝对τ、局部MSE和批量语法评价的移植假设见README。

未完成：全模型量化/编码、任务困惑度、ViT/CIFAR训练、真实压缩字节、原生低比特加速；另外5篇未执行原论文训练。原因是本次使用CPU与已有0.6B缓存，原研究分别需要H100/H200、大模型教师、完整数据生成和长序列训练。没有伪造对应结果，也没有以局部检查冒充完整原论文复现。

## 分支独立性与清理

本分支feature/arxiv-daily-2026-09-29严格从最新origin/main（abfe8f2767d8bf881d586718ab4db33fc576be6a）创建linked worktree。删除main自带07-28历史日报；papers仅7篇本次精读及说明，reports仅本日报及说明，scripts仅2个本次量化目录及说明，metadata仅09月本次7条JSON/CSV及说明。未继承历史feature成果，原工作树未提交文件受保护。提交与远端验证结果由本次最终汇报给出，避免在提交前捏造SHA。

## 窗口内51篇排除审计

以下每条均已阅读官方标题/摘要；三条边界项另读全文。排除针对模型压缩范围，不评价论文价值。

| ID | 标题 | 排除依据 |
|---|---|---|
| [2609.31620](https://arxiv.org/abs/2609.31620) | FuseReg: Regularizing Layer Fusion Mitigates the Reconstruction-Generation Gap in Representation Autoencoders | 随机层融合正则改善生成/重构，没有压缩网络或蒸馏部署目标。 |
| [2609.31619](https://arxiv.org/abs/2609.31619) | Learning to Stop without Learning to Stop: Self-Supervised Confidence Training Improves Reasoning Efficiency | 全文为置信度标签自监督，减少生成推理长度；50级quantize指标签离散化，非权重/激活量化、结构剪枝或teacher-student蒸馏。 |
| [2609.31614](https://arxiv.org/abs/2609.31614) | Gap-free Differentially Private PCA for Gaussian Data | 差分隐私PCA统计算法，非神经网络压缩。 |
| [2609.31612](https://arxiv.org/abs/2609.31612) | First-Order Stationarity of Reverse Diffusions | 扩散采样驻点理论，非少步蒸馏或模型压缩。 |
| [2609.31607](https://arxiv.org/abs/2609.31607) | Statistical attribute alignment for black-box generative AI via output post-processing | 对生成结果后处理匹配属性分布，不压缩模型。 |
| [2609.31600](https://arxiv.org/abs/2609.31600) | New LoRA Skills Should Read but Never Write | LoRA技能组合与干扰控制，折叠回同一基座，未压缩基座权重。 |
| [2609.31595](https://arxiv.org/abs/2609.31595) | GraphWrit3R: End-to-End 3D Scene Graph Writing | 点云/高斯到场景图的多模态生成架构，无压缩机制。 |
| [2609.31589](https://arxiv.org/abs/2609.31589) | Common-Mode Collapse and Recovery in Direct Feedback Alignment | 反馈对齐训练退化机制，非剪枝/量化。 |
| [2609.31587](https://arxiv.org/abs/2609.31587) | Compact Documentation for Coding Agents: A Benchmark, an Optimizer, and Why It Does Not Transfer | 代码文档压缩和提示优化，压缩对象不是模型。 |
| [2609.31586](https://arxiv.org/abs/2609.31586) | Trust Guided Decision Transformer | 依据状态预测误差选择可信历史后缀并多次评估，目标为控制可靠性，非压缩模型/KV。 |
| [2609.31573](https://arxiv.org/abs/2609.31573) | How Far Can INRs Go? Cross-Domain Parameter-efficient INR-Based Semantic Segmentation for Brain MRI | 全文是小参数INR新架构和跨域分割比较，未对已有网络做量化、剪枝或蒸馏；参数少不单独构成模型压缩证据。 |
| [2609.31572](https://arxiv.org/abs/2609.31572) | OC-GS: Gaussian Splatting for Irregular Turntable Capture | 高斯重建中相机角度校正，无表示压缩率机制。 |
| [2609.31570](https://arxiv.org/abs/2609.31570) | Uncertainty and Explainability in Deep Rough Volatility: A Neural Information-Theoretic Posterior Approach | 金融参数后验推断与不确定性解释，非压缩。 |
| [2609.31569](https://arxiv.org/abs/2609.31569) | Adapting for AI: How elementary teachers adjust their practices for an AI-integrated curriculum | teacher/student指人类小学教师学生，非知识蒸馏。 |
| [2609.31563](https://arxiv.org/abs/2609.31563) | Multi-agent Scaling Across Disjunctive and Compensatory Tasks | 多智能体规模与任务结构评测，不压缩单模型。 |
| [2609.31559](https://arxiv.org/abs/2609.31559) | Online Learning via Learned Latent Bayesian Tracking | 低维隐空间用于在线贝叶斯适配后重建完整权重，未提出部署权重压缩。 |
| [2609.31558](https://arxiv.org/abs/2609.31558) | Region-Level Black-Box Defense Against Stealthy Embedding-Space Backdoors in CLIP | CLIP图像局部净化防御，不压缩模型。 |
| [2609.31553](https://arxiv.org/abs/2609.31553) | MexHat: A Dataset for Hate Speech Detection in Mexican Spanish Videos | 仇恨检测数据集与基线，不涉及压缩。 |
| [2609.31551](https://arxiv.org/abs/2609.31551) | EAServe: Encode-Aware Disaggregated Serving for Multimodal Large Language Models | 编码/预填充/解码GPU调度；pruning指配置搜索空间，不是权重或token剪枝。 |
| [2609.31547](https://arxiv.org/abs/2609.31547) | Two Conformal Constructions for Adaptive Within-Document AI-Text Screening | 文本检测共形统计与提前停止检验，不压缩LLM。 |
| [2609.31546](https://arxiv.org/abs/2609.31546) | BeatGraph: Self-Supervised Heartbeat Graphs for Infant ECG Representations from the Home Environment | ECG自监督图表示预训练，不是教师蒸馏或网络压缩。 |
| [2609.31544](https://arxiv.org/abs/2609.31544) | A Flow Matching Framework for Neural Representational Dissimilarity | 神经响应分布距离估计，不压缩模型。 |
| [2609.31540](https://arxiv.org/abs/2609.31540) | Can You Check That? The Checkability Boundary for Local LLM Network Automation | 全文用7个现成SLM全部生成、聚合后转交大模型，无蒸馏或压缩网络，也无总计算/显存节约证明；降低云端请求比例不等于模型压缩。 |
| [2609.31539](https://arxiv.org/abs/2609.31539) | NEXT: Physics-Informed Neuro-Spectral Exponential Time Differencing Architectures | 刚性PDE指数时间积分架构，非压缩。 |
| [2609.31531](https://arxiv.org/abs/2609.31531) | HySTAR: Anchored Hypergraphs for Stable Credit Assignment in Cooperative Multi-Agent Reinforcement Learning | 稀疏超图用于MARL归因结构稳定，不以模型计算/存储压缩为目标。 |
| [2609.31518](https://arxiv.org/abs/2609.31518) | Retrainable physics-integrated neural differentiable modeling of sintering across material systems | 物理神经微分建模烧结，无压缩机制。 |
| [2609.31514](https://arxiv.org/abs/2609.31514) | Forensic Twins: Self-Supervised Residual Learning for AI-Generated Image Forensics | 残差自监督预训练取代昂贵检测，未压缩既有网络；速度对比不足以证明模型压缩。 |
| [2609.31513](https://arxiv.org/abs/2609.31513) | Statistical Foundations for a Google Play User-Review Sentiment Index: Signal Fusion, Shrinkage, Distributional Validation, and Dynamic Smoothing | 评论情感指数的统计收缩与平滑，非神经网络剪枝。 |
| [2609.31511](https://arxiv.org/abs/2609.31511) | Muslim: A Deployed Arabic Voice AI Platform for Grounded Islamic Knowledge | 语音产品与微调模型部署，无明确压缩算法或对应压缩实验。 |
| [2609.31509](https://arxiv.org/abs/2609.31509) | ClearGS: Reliability-Aware Gaussian Splatting from Handheld Videos | 帧可靠性加权及图像修复改善3DGS，不是高斯表示压缩。 |
| [2609.31507](https://arxiv.org/abs/2609.31507) | SatNav: A Scalable Benchmark for Long-Horizon UAV Vision-Language Navigation from Satellite Imagery | UAV导航数据集和记忆模块比较，非模型压缩。 |
| [2609.31506](https://arxiv.org/abs/2609.31506) | Evaluating Cultural Awareness of LLMs for Haitian Creole | 语言文化意识评测，不涉及压缩。 |
| [2609.31505](https://arxiv.org/abs/2609.31505) | Prompt Minimization: Reducing Input Redundancy Without Sacrificing Output Fidelity | 压缩输入prompt而非模型权重/激活/KV，排除。 |
| [2609.31498](https://arxiv.org/abs/2609.31498) | Retail Product Search: A Practical Approach at Target | 词法/向量混合搜索与融合工程，不是模型压缩。 |
| [2609.31491](https://arxiv.org/abs/2609.31491) | UQ-LOB: Uncertainty-Aware Limit Order Book Mid-Price Forecasting | 额外不确定性模块与选择性预测，非压缩。 |
| [2609.31483](https://arxiv.org/abs/2609.31483) | Scaling Density Functional Theory with Gaussian Splatting | 压缩/优化量子DFT基函数而非神经网络模型。 |
| [2609.31482](https://arxiv.org/abs/2609.31482) | "AI is (not) the new...": A Diagnostic Analogy Framework for Generative AI's Cultural Impacts | 生成AI文化影响类比分析，不涉及压缩。 |
| [2609.31473](https://arxiv.org/abs/2609.31473) | Game Arena: Strategic LLM Evaluation in Competitive Environments | 游戏能力评测平台，不涉及压缩。 |
| [2609.31470](https://arxiv.org/abs/2609.31470) | Beyond Empirical Support: Structured Outlier Generation via Sinkhorn Optimal Transport | 生成异常数据做稳健性评估，不涉及模型压缩。 |
| [2609.31469](https://arxiv.org/abs/2609.31469) | LandscapeSHAP: Which Persistent Homology Class Gets the Credit? | 拓扑特征Shapley归因，非模型压缩。 |
| [2609.31468](https://arxiv.org/abs/2609.31468) | PriceBench: A Diagnostic Benchmark for Price, Quality, and Brand Preferences in LLM Booking Agents | 酒店预订代理偏好基准，无压缩算法。 |
| [2609.31463](https://arxiv.org/abs/2609.31463) | Uncertainty-Aware Federated Learning for Infant Movement Analysis | 联邦不确定性聚合，MC Dropout用于UQ而非部署剪枝。 |
| [2609.31461](https://arxiv.org/abs/2609.31461) | KneePreM: Towards 3D Knee MRI Foundation Models via Large-Scale Unlabeled Pretraining and Label-Efficient Fine-Tuning | 膝MRI预训练提高标签效率，不是模型容量压缩。 |
| [2609.31460](https://arxiv.org/abs/2609.31460) | Segment-Level Agentic Topic Modeling for Improved Data Exploration and Resource Efficiency | 主题生成/整理减少LLM调用，未压缩模型结构或蒸馏学生。 |
| [2609.31458](https://arxiv.org/abs/2609.31458) | Nonparametric In-Context Learning under Growing Geometric Complexity: Minimax Optimality and Local Geometry-Adaptivity of Transformers | ICL非参数估计理论与局部几何，不是压缩算法。 |
| [2609.31456](https://arxiv.org/abs/2609.31456) | Diagnosing the Sources of Compositional Failure in Vision-Language Models: A Controlled Analysis | VLM组合推理诊断，不涉及模型压缩。 |
| [2609.31454](https://arxiv.org/abs/2609.31454) | Different Corruptions, Different Signals: Uncertainty and Loss in Federated Data Quality | 联邦数据质量信号评测，非压缩。 |
| [2609.31452](https://arxiv.org/abs/2609.31452) | Vision-Based 6-DoF Grasp Pose Estimation for Robot Cloth Unfolding | 布料抓取姿态预测新架构，不涉及模型压缩。 |
| [2609.31451](https://arxiv.org/abs/2609.31451) | TemplateCraft: Agentic Visual Template Generation | 视觉模板多智能体生成，无权重更新或压缩。 |
| [2609.31450](https://arxiv.org/abs/2609.31450) | From Reward Signal to Visual Utility: A Controlled Audit of Medical VLM Post-Training | VLM后训练视觉效用审计，LoRA用于适配而非部署压缩。 |
| [2609.31448](https://arxiv.org/abs/2609.31448) | ViSTA: A Simple Bridge Extends Visual Alignment to Clinical Time-Series Understanding in Multimodal LLMs | 紧凑适配器减少可训练参数，完整基座仍保留，非推理模型压缩。 |
