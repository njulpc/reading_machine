# arXiv 模型压缩论文日报：2026-10-26

运行日：2026-10-27（Asia/Shanghai）；检索完成记录：2026-10-27T01:16:38.324055+08:00。

固定窗口为 **2026-10-24、25、26 三个完整自然日**，从 24 日 00:00 至 26 日 23:59:59（北京时间）。用官方 /abs 的 Submission history 中 **v1 原始提交时间**换算归日；不是公告日。三篇入选论文的 UTC 提交日均为 10 月 23 日，北京时间为 10 月 24 日。

## 1. 数量与完整论文表

| v1 本地日期 | 全主题窗口论文 | 相关条目原始出现次数 | ID 去重后相关数（排历史前） | 历史重复数 | 本次新增数 |
|---|---:|---:|---:|---:|---:|
| 2026-10-24 | 49 | 8 | 3 | 0 | 3 |
| 2026-10-25 | 0 | 0 | 0 | 0 | 0 |
| 2026-10-26 | 0 | 0 | 0 | 0 | 0 |
| 合计 | 49 | 8 | **3** | **0** | **3** |

10 月 25 日、26 日：**截至运行时 arXiv 官方网页未检出**。这是截至本次网页公开状态的结论，不能推断实际没有投稿；后续运行继续以三天窗口回查。公告延迟可能使本次窗口的部分投稿尚未公开。本次没有把抓取失败记为零。

| arXiv ID | 标题/精读 | 作者 | v1 北京时间 | v1 UTC | 技术分类 | 官方主分类及交叉分类 |
|---|---|---|---|---|---|---|
| [2610.32933](https://arxiv.org/abs/2610.32933) | [Yalda-Embedding: Open Development of a Competitive Persian Retrieval Model](../../../papers/2026-10/knowledge_distillation/2610.32933/tech_analysis.md) | Yalda Taheri , Mohammad Hassan Heydari , Armon Rasooli | 2026-10-24T01:30:40+08:00 | 2026-10-23T17:30:40+00:00 | knowledge_distillation | Computation and Language (cs.CL) ; Artificial Intelligence (cs.AI) |
| [2610.32878](https://arxiv.org/abs/2610.32878) | [Advancing SVD-based LLM Compression via Layer-Wise Error Model Search](../../../papers/2026-10/other/2610.32878/tech_analysis.md) | Moritz Thoma , Maximilian Groezinger , Maximilian Forstenhäusler , Emad Aghajanzadeh , Manoj Rohit Vemparala , Christos Anagnostopoulos , Pierpaolo Mori , Nael Fasfous , Alexander Frickenstein , Daniel Mueller-Gritschneder , Ulf Schlichtmann | 2026-10-24T00:46:00+08:00 | 2026-10-23T16:46:00+00:00 | other | Artificial Intelligence (cs.AI) |
| [2610.32859](https://arxiv.org/abs/2610.32859) | [Sustainability of TSFM Deployment and Pretraining: From Carbon Footprint Analysis to Mitigation via Pruning](../../../papers/2026-10/pruning/2610.32859/tech_analysis.md) | Cécile Luc , Nathanaël Lemonnier , Ievgen Redko | 2026-10-24T00:32:29+08:00 | 2026-10-23T16:32:29+00:00 | pruning | Machine Learning (cs.LG) |

## 2. 主要结论与评分

- **Yalda-Embedding**：8B 教师关系蒸馏至 595.8M 检索学生，八任务宏平均从稳定非蒸馏配方 0.4813 升至 0.5488。相对名义8B教师参数比约13.43×，非实测内存/速度。4B参考模型均分0.5563，并不是训练教师。[全文](https://arxiv.org/html/2610.32933v1)
- **LEMS / KFAC-SVD**：token级曲率估计改善低秩分解，校准代理误差支持全局秩分配。Qwen3-8B 保留70%线性参数时，KFAC+LEMS 的 WikiText2 PPL 11.81、平均准确率53.80，原模型9.71/62.04；温和90%保留时9.85/62.89。参数预算排除head，不应当作整模实测压缩倍数。[全文](https://arxiv.org/html/2610.32878v1)
- **Chronos-2 剪枝**：删一个encoder block，参数减少7.90%、FLOPs减少8.15%、实测延迟减少5.97%、碳排放减少8.72%。25任务 MASE skill 降1.12pp，WQL skill升0.29pp；不是所有任务无损。[全文](https://arxiv.org/html/2610.32859v1)

以下是阅读者基于证据的主观1–10评分，10较高，四项不合成总排名。精度看相应预算下质量保持与验证广度；压缩看实际缩减量，理论参数比与实测收益分开；创新看方法新意；可复现性看公开资产和设置细节，不代表本机成功复现。

| ID | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 依据与边界 |
|---|---:|---:|---:|---:|---|
| 2610.32933 | 8 | 8 | 6 | 8 | 八任务同规模领先、接近4B；名义8B/595.8M约13.43倍参数差；方法为成熟关系KD组合；论文声明开放数据代码权重，但未固定全部seed/评测版本，本次未运行。 |
| 2610.32878 | 8 | 6 | 9 | 7 | 多家族与70B扩展，温和压缩近基线、激进压缩仍掉点；线性层保留0.5–0.9而非整模实测内存；token KFAC与校准秩分配互补；细节充分但需H200/梯度统计/Gurobi，本次未运行。 |
| 2610.32859 | 7 | 3 | 6 | 7 | 25任务WQL稍升但MASE skill降1.12pp；参数仅减7.9%，有延迟/碳实测；已知余弦块剪枝迁移到TSFM；校准与边界明确但单硬件、两任务未加载、无替代剪枝对照，本次未运行。 |

## 3. 检索覆盖证据

仅以 arXiv 官方 HTML 分类列表召回，没有调用 export.arxiv.org API、submittedDate API、搜索摘要代替全量列表。五分类的 new/recent 都在本轮重新抓取；包含 new submissions、cross submissions 和 new 页面中替换条目。10页总计 **5,631次条目出现→3,658个唯一ID**，show=2000 已覆盖每页总数，全部小于2000，无后续页。各 h3 分组显示数与实际 dt 条目逐组一致。

| 官方入口 | 页面总条目 | 覆盖范围 | 页面日期/类别分组 |
|---|---:|---|---|
| [cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0) | 321 | skip=0, show=2000；实计 321 | Showing new listings for Monday, 26 October 2026；New submissions (showing 106 of 106 entries)；Cross submissions (showing 92 of 92 entries)；Replacement submissions (showing 123 of 123 entries) |
| [cs.LG recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0) | 1403 | skip=0, show=2000；实计 1403 | Mon, 26 Oct 2026 (showing 198 of 198 entries )；Fri, 23 Oct 2026 (showing 205 of 205 entries )；Thu, 22 Oct 2026 (showing 240 of 240 entries )；Wed, 21 Oct 2026 (showing 249 of 249 entries )；Tue, 20 Oct 2026 (showing 511 of 511 entries ) |
| [cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0) | 169 | skip=0, show=2000；实计 169 | Showing new listings for Monday, 26 October 2026；New submissions (showing 72 of 72 entries)；Cross submissions (showing 34 of 34 entries)；Replacement submissions (showing 63 of 63 entries) |
| [cs.CL recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0) | 802 | skip=0, show=2000；实计 802 | Mon, 26 Oct 2026 (showing 106 of 106 entries )；Fri, 23 Oct 2026 (showing 117 of 117 entries )；Thu, 22 Oct 2026 (showing 137 of 137 entries )；Wed, 21 Oct 2026 (showing 159 of 159 entries )；Tue, 20 Oct 2026 (showing 283 of 283 entries ) |
| [cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000&skip=0) | 205 | skip=0, show=2000；实计 205 | Showing new listings for Monday, 26 October 2026；New submissions (showing 107 of 107 entries)；Cross submissions (showing 26 of 26 entries)；Replacement submissions (showing 72 of 72 entries) |
| [cs.CV recent](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0) | 914 | skip=0, show=2000；实计 914 | Mon, 26 Oct 2026 (showing 133 of 133 entries )；Fri, 23 Oct 2026 (showing 114 of 114 entries )；Thu, 22 Oct 2026 (showing 138 of 138 entries )；Wed, 21 Oct 2026 (showing 183 of 183 entries )；Tue, 20 Oct 2026 (showing 346 of 346 entries ) |
| [cs.AI new](https://arxiv.org/list/cs.AI/new?show=2000&skip=0) | 321 | skip=0, show=2000；实计 321 | Showing new listings for Monday, 26 October 2026；New submissions (showing 79 of 79 entries)；Cross submissions (showing 110 of 110 entries)；Replacement submissions (showing 132 of 132 entries) |
| [cs.AI recent](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0) | 1436 | skip=0, show=2000；实计 1436 | Mon, 26 Oct 2026 (showing 189 of 189 entries )；Fri, 23 Oct 2026 (showing 229 of 229 entries )；Thu, 22 Oct 2026 (showing 211 of 211 entries )；Wed, 21 Oct 2026 (showing 321 of 321 entries )；Tue, 20 Oct 2026 (showing 486 of 486 entries ) |
| [cs.AR new](https://arxiv.org/list/cs.AR/new?show=2000&skip=0) | 9 | skip=0, show=2000；实计 9 | Showing new listings for Monday, 26 October 2026；New submissions (showing 4 of 4 entries)；Cross submissions (showing 3 of 3 entries)；Replacement submissions (showing 2 of 2 entries) |
| [cs.AR recent](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0) | 51 | skip=0, show=2000；实计 51 | Mon, 26 Oct 2026 (showing 7 of 7 entries )；Fri, 23 Oct 2026 (showing 6 of 6 entries )；Thu, 22 Oct 2026 (showing 9 of 9 entries )；Wed, 21 Oct 2026 (showing 11 of 11 entries )；Tue, 20 Oct 2026 (showing 18 of 18 entries ) |

从全部3,658份官方abs提取标题、摘要、主/交叉分类和v1；本轮新抓661份，另2997份复用保留原始官方HTML的历史证据并重新解析，逐文件记录来源和SHA256。49篇窗口摘要全部为本轮新抓并逐条语义复核；其余3,609篇由v1日期排除，没有将关键词不匹配作为召回门槛，也不宣称对窗外论文进行了逐篇全文精读。详情解析失败数为0。

**相邻日期阳性对照：** 官方列表可见 [2610.32822](https://arxiv.org/abs/2610.32822)，v1 北京时间 10月23日23:56:19，属于窗外；[2610.32830](https://arxiv.org/abs/2610.32830) 为10月24日00:03:19，属于窗内但主题是GPU封装而非模型压缩。最新可见v1为 [2610.32982](https://arxiv.org/abs/2610.32982)，10月24日01:59:56。公告页显示10月26日，不表示这些论文于26日提交。

quantization/quantize、low-bit、model compression/compress、pruning/sparsity、knowledge distillation/distill、teacher/student、KV cache、mixed precision、GPTQ、AWQ及低秩、秩分配等同义表达均做了复核；词命中记录见本地审计 `keyword_review.json`。49篇逐条理由见 `semantic_review.json`，8篇候选/边界官方全文及来源哈希见 `fulltext_audit.json`。

## 4. 语义边界与排除理由

本日报采用**直接模型压缩**口径；关联技术不自动计入新增模型压缩论文，下面记录易混淆项以便复核：

| ID | 全文核验后的排除依据 |
|---|---|
| [2610.32943](https://arxiv.org/html/2610.32943v1) IDM/CMM | 是知识蒸馏方法，但全文固定AsymRec学生架构/推理，仅改善推荐质量；未证明师生参数/部署成本缩减。SASRec教师隐藏256、学生448，不能假定学生更小。IDM R@10平均提升15.39%、CMM NDCG@10提升8.28%是质量收益，不是压缩倍率。 |
| [2610.32866](https://arxiv.org/html/2610.32866v1) TopKLoRA | Top-k适配器潜变量用于可解释后门电路，保留基座与适配器矩阵。更小的可解释电路不等于更小的部署模型；缺少净内存或延迟缩减证据。 |
| [2610.32871](https://arxiv.org/html/2610.32871v1) J-Comm | 冻结双模型且保留本地KV；生成文本token减少19.2–74.8%，latent steps另计，不能转写为总FLOPs、显存或模型压缩收益。 |
| [2610.32881](https://arxiv.org/html/2610.32881v1) NgramRL | CPU n-gram草稿缓存及预取加速精确推测解码，目标模型不变；是解码系统优化，不是权重/激活/KV压缩。 |
| [2610.32964](https://arxiv.org/html/2610.32964v1) Flownomaly | 单步条件均值异常恢复，不是把教师或原有多步模型蒸馏成小模型；更紧凑特征提取器是未来工作。 |

此外，舍入位置对齐2610.32951、分词改进2610.32921、LoRA理论2610.32854，以及稀疏像素攻击/视觉输入编辑均按语义排除。完整49项决策保留在运行证据，不把这些边界项隐藏在关键词过滤之外。

## 5. 历史去重审计

fetch成功后逐一对 **50个** `origin/feature/arxiv-daily-*` 执行 `git ls-tree -r --name-only`，并用 `git show` 读取各分支所有 `metadata/**/papers_index.json` 交叉核对。从真实 `papers/**/<id>/tech_analysis.md` 提取去版本号规范化ID，得到 **590个**历史已分析ID。

metadata-only **2607.27951、2607.28410、2607.28457** 没有对应真实精读文件，不算已完成。10月21–26日本地未推送工作状态也不算历史远端完成。本次当日远端分支不存在，按新运行处理。

跨分类、跨new/recent与日期先按ID合并，再与完整历史集合比较：相关原始出现8次→3个唯一相关ID→历史重复0→新增3。排除重复ID及其来源分支列表为空 `[]`；最终新增ID为 `2610.32859, 2610.32878, 2610.32933`，与历史集合交集为空。

远端 `ls-remote --heads` 已与fetch后的50分支SHA全集和main逐一匹配。全部历史来源及SHA如下（对应metadata中的dedup_source_branches/dedup_source_shas）：

- `origin/feature/arxiv-daily-2026-07-29`：`37139ece193fa4d66212a2f2951ed88a8d83b76a`
- `origin/feature/arxiv-daily-2026-07-30`：`8fe81f3241431f5f6af227ce768402d6f91f97ca`
- `origin/feature/arxiv-daily-2026-07-31`：`25e3d35f37713e9b407a24c6f7b045dd26208f92`
- `origin/feature/arxiv-daily-2026-08-01`：`29b36a60ead969c281bd57e4fb6efd9e0001f6b1`
- `origin/feature/arxiv-daily-2026-08-02`：`f397bf7f726f7b7b8286a035d43da5c12236d336`
- `origin/feature/arxiv-daily-2026-08-03`：`69a31ee7e2fea63cf20be9c34ca847ad58ab4ea5`
- `origin/feature/arxiv-daily-2026-08-04`：`f798a00e0569952212d0e6451f00ba6ea28de99a`
- `origin/feature/arxiv-daily-2026-08-05`：`333264be93bb365ee7d29436235e6b056427943e`
- `origin/feature/arxiv-daily-2026-08-06`：`67600577ca268cd88675d221f0e19fdb59673789`
- `origin/feature/arxiv-daily-2026-08-07`：`87a4eb0f56e25253b22b8c7e9a288af8a467386a`
- `origin/feature/arxiv-daily-2026-08-08`：`4f19f7ec424ae7c273a5ae9a01fdc4aa1fbc07ff`
- `origin/feature/arxiv-daily-2026-08-10`：`652ee043ff7fad81734a95010b9b49b6dca1ec11`
- `origin/feature/arxiv-daily-2026-08-12`：`5dea9ebeff4db72522e85962764ae51a4978a4e6`
- `origin/feature/arxiv-daily-2026-08-14`：`fe27109ab9b86bd7b9ac4a4393dde4a77bb3b372`
- `origin/feature/arxiv-daily-2026-08-15`：`e463baea815c06d95ffc36eec034113b28db7927`
- `origin/feature/arxiv-daily-2026-08-16`：`940ef56b2ebd4bd22ce5636302234aaa63691e2d`
- `origin/feature/arxiv-daily-2026-08-17`：`1320530c9060d6acfd6a6814ebe65415b62c760d`
- `origin/feature/arxiv-daily-2026-08-18`：`2190e4aef62423032c78b7594a0e208c6d128c0d`
- `origin/feature/arxiv-daily-2026-08-19`：`3518b1fff91bab3cd78421810c0798177060063f`
- `origin/feature/arxiv-daily-2026-08-20`：`6413646a6fec8b54f937415084c2df3e99b358a1`
- `origin/feature/arxiv-daily-2026-08-21`：`dc8a46573315edb88419bb4eb181bea89d209de7`
- `origin/feature/arxiv-daily-2026-08-22`：`0dd4154cce8306873ec37767b6ab27e00b07735f`
- `origin/feature/arxiv-daily-2026-08-23`：`e1a83986b75aec3a0289a50082ac44a6b359a130`
- `origin/feature/arxiv-daily-2026-08-24`：`574caeb9b2e6e763f4a216b80bfa33b539f8c71b`
- `origin/feature/arxiv-daily-2026-08-25`：`508ce04ebcda0238aceb1d32991db50aac8904e0`
- `origin/feature/arxiv-daily-2026-08-26`：`4a627bc35cb9075ac416e12165c9418f79e1bbee`
- `origin/feature/arxiv-daily-2026-08-27`：`f57ca87589c728a68851f21acdff1c333b402e35`
- `origin/feature/arxiv-daily-2026-08-28`：`daeb352421a9263136927bc71497c86ddb512c77`
- `origin/feature/arxiv-daily-2026-08-29`：`e73be2a46c726bdd0a42b13b8d3ec75b5dfd9060`
- `origin/feature/arxiv-daily-2026-08-30`：`0cff4d39f94bca3cfdf18e85e8f056850bad6bda`
- `origin/feature/arxiv-daily-2026-08-31`：`d21ad3ba2970c7664ffd084b568f61b1dbde8866`
- `origin/feature/arxiv-daily-2026-09-01`：`ebb94ff45394bcf77d90c41d5f4eec02dc948b0b`
- `origin/feature/arxiv-daily-2026-09-02`：`ab05a346a491f043142867c74593f45e669812d1`
- `origin/feature/arxiv-daily-2026-09-03`：`710202d696a1295b25e55f50d4fee966434549d4`
- `origin/feature/arxiv-daily-2026-09-04`：`623673ccf816fda6de51daf471f55c79b0a24801`
- `origin/feature/arxiv-daily-2026-09-05`：`1ab9858c9e986133aafa40226b1c5af0a760c175`
- `origin/feature/arxiv-daily-2026-09-06`：`05108f7ef5b13b0fcc118d633a53c99d31d55166`
- `origin/feature/arxiv-daily-2026-09-07`：`4fa4065a723520e6413d4bed69790612999517cd`
- `origin/feature/arxiv-daily-2026-09-08`：`3db8912129f5ebdfb2399a213f0688ac30cdf971`
- `origin/feature/arxiv-daily-2026-09-09`：`88c76b0c8b21a4a366dbba0de17d2c63327dcca8`
- `origin/feature/arxiv-daily-2026-09-14`：`5068f2a8c89b815b69665b35900fd0e8d3800a54`
- `origin/feature/arxiv-daily-2026-09-15`：`b580dd8c66660802f18e5c25bdff7f9ad0f85e66`
- `origin/feature/arxiv-daily-2026-09-21`：`263f4647c46bdea7fd86ecdabca69c889ef96806`
- `origin/feature/arxiv-daily-2026-09-22`：`7b0317385f6f8b9e6e79d2863a7e4d7a3a355968`
- `origin/feature/arxiv-daily-2026-09-29`：`2874106cd594d482ab71a00c8b6ef5fdf3622cbb`
- `origin/feature/arxiv-daily-2026-10-12`：`252ce3d0f428984f276bb380dea030f165e9e9d3`
- `origin/feature/arxiv-daily-2026-10-13`：`52bf4827692c57ccabbd1dd61a6e4641b683379f`
- `origin/feature/arxiv-daily-2026-10-14`：`71c9c681c89725a10453f8fdee59633fcebb1bec`
- `origin/feature/arxiv-daily-2026-10-19`：`883eb5828be85a82364fc08bcf40ea2295443902`
- `origin/feature/arxiv-daily-2026-10-20`：`5a0766dd8748557393073127bb2557ad7b5b54a7`

## 6. 复现、独立快照与验证范围

本轮 **quantization 新增0篇**，所以 `scripts/quantization/` 无论文复现目录；三个入选类别分别是知识蒸馏、低秩分解和结构化剪枝。常规训练中的BF16或SID向量量化不误标为权重量化。本轮没有运行论文训练、H200分解或A100碳测量，所有实验数字明确来自论文，不声称Qwen3-0.6B量化复现成功。

隔离linked worktree：`/private/tmp/reading_machine_arxiv_20261027`。基线严格为最新 `origin/main` 的 `abfe8f2767d8bf881d586718ab4db33fc576be6a`；每日分支 `feature/arxiv-daily-2026-10-27`。原工作树未提交文件不复制进入。删除main自带2026-07-28旧日报，保留说明文件；最终仅3篇精读、本日报和2026-10独立三条索引/CSV，scripts仅通用说明。

提交前检查覆盖JSON/CSV可解析、论文目录ID=索引ID=本次新增ID、量化复现ID=量化子集（空）、六节结构、全部日期在窗口、历史交集为空、diff仅当次新增与明确旧日报删除；提交后/推送后的SHA、merge-base与单提交日志结果另存运行审计并在任务最终汇报提供，避免在生成报告时提前声称推送成功。

本地完整证据目录：`/Users/lipengcheng/.codex/automations/arxiv/runs/2026-10-27`，含官方列表/abs/全文、分组校验、历史树、来源哈希和语义决策。可用性边界：网页截止最新v1为24日凌晨，后续公告可能补出25–26日或更早投稿；本轮未使用第三方日期代替官方v1。
