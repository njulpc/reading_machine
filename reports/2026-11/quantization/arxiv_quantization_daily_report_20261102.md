# arXiv 模型压缩论文日报：2026-11-02

运行时间：2026-11-03T01:20:10.792550+08:00。运行日R=2026-11-03，日报主日期R-1=2026-11-02。检索北京时间2026-10-31、2026-11-01、2026-11-02三个完整自然日（00:00–23:59:59）；用官方abs的v1真实时间归日。

## 1. 结果与证据边界

本次窗口相关论文11篇，历史重复0篇，新增11篇。分类：pruning 4、knowledge_distillation 4、other 3、quantization 0。包括两篇压缩路线的负面/方法学评估（层循环、机器人token剪枝）；没有将纯输入压缩、外部调度或一般自蒸馏全部计入模型压缩。

| v1提交日（北京时间） | 窗口相关唯一ID | 历史重复 | 新增 | 口径 |
|---|---:|---:|---:|---|
| 2026-10-31 | 11 | 0 | 11 | 全部来自官方v1提交记录 |
| 2026-11-01 | 0 | 0 | 0 | 截至运行时 arXiv 官方网页未检出 |
| 2026-11-02 | 0 | 0 | 0 | 截至运行时 arXiv 官方网页未检出 |

后两日不能解释为实际没有投稿：官方new最新公告为11月2日，但当前可见v1最晚为10月31日01:59:59。后续依靠三天窗口回查公告延迟。本次所有入选论文UTC提交日为10月30日、北京时间为10月31日；没有用ID月份或公告日期替代v1时间。

## 2. 完整新增论文表

评分依次为精度效果/压缩倍率或资源削减/创新性/可复现性，各1–10分。它们是基于论文证据的阅读评价，非标准化排名；可复现性高分不代表本轮已运行。

| ID | 标题 | 实际v1提交（北京时间） | 分类 | 一句话结论 | 评分 |
|---|---|---|---|---|---|
| [2610.42147](https://arxiv.org/abs/2610.42147) | Latent Sparse Attention: Towards Subquadratic Ultra-Long Context Attention | 2026-10-31 01:59:34+08:00 | pruning | LSA 用语义聚类和分层索引减少超长上下文注意力计算，但不压缩原始 KV 缓存。 | 8/7/9/7 |
| [2610.42135](https://arxiv.org/abs/2610.42135) | A Better Critic Matters for Distribution Matching Distillation | 2026-10-31 01:58:26+08:00 | knowledge_distillation | DMD 蒸馏需要匹配教师规模的 critic，并让 critic 感知生成步，才能稳定获得高质量少步学生。 | 8/8/8/7 |
| [2610.42128](https://arxiv.org/abs/2610.42128) | DecisionRank: On-Policy Distillation for Decision-Model Rerankers | 2026-10-31 01:56:58+08:00 | knowledge_distillation | DecisionRank 把生成式排序教师蒸馏成首token打分学生，以一次前向替代自回归排序。 | 8/9/8/8 |
| [2610.42116](https://arxiv.org/abs/2610.42116) | ACCT: Asymmetric Cross-LLM Context Transfer | 2026-10-31 01:50:49+08:00 | other | ACCT 将源模型上下文转换成目标模型稀疏 KV；四倍目标缓存缩减可行，但精度和总时延高度依赖迁移方向。 | 5/7/8/6 |
| [2610.42112](https://arxiv.org/abs/2610.42112) | Subquadratic Attention with a Hierarchical Tree-Structured Indexer | 2026-10-31 01:48:37+08:00 | pruning | ZHA 用可学习参考查询构造层级键摘要，以top-p路由稀疏访问KV；长距离性能预测尚待优化内核和实测。 | 8/6/9/5 |
| [2610.42084](https://arxiv.org/abs/2610.42084) | RangeSWA: Training-Free Length Extrapolation for Continuous Diffusion Language Models | 2026-10-31 01:35:48+08:00 | other | RangeSWA 通过局部窗口、远程摘要和动态检索改善扩散语言模型长度外推，8k实测加速约1.21×。 | 7/4/7/7 |
| [2610.42031](https://arxiv.org/abs/2610.42031) | Any Forcing: Any-Step Generality and One-Step Stability for Autoregressive Video Generation | 2026-10-31 00:56:42+08:00 | knowledge_distillation | Any Forcing 联合步间一致性、首帧增强和历史缓存选择，稳定少步自回归视频生成。 | 8/8/7/7 |
| [2610.42030](https://arxiv.org/abs/2610.42030) | There Is No Free Loop: When Does Looping a Trained Model Pay for Its Inference Compute? | 2026-10-31 00:56:29+08:00 | other | 固定参数的层循环只在0.8B模型上通过等参数与等FLOPs双重检验，不能普遍视作有效压缩替代。 | 6/2/8/8 |
| [2610.42018](https://arxiv.org/abs/2610.42018) | Asynchronous Flow Map Language Models | 2026-10-31 00:51:40+08:00 | knowledge_distillation | aFMLM 把异步token生成次序蒸馏进流映射，使单次前向并行生成保留部分顺序推理能力。 | 6/7/9/7 |
| [2610.41970](https://arxiv.org/abs/2610.41970) | When Does Test-Time Search Help World Action Models? An Empirical Audit of Candidate Selection and Simulator Integrity | 2026-10-31 00:21:07+08:00 | pruning | Cosmos Policy 的token剪枝虽减少47.9%单前向FLOPs，部署整路径仅快1.152×，且该测量未验证剪枝动作质量。 | 3/4/8/8 |
| [2610.41968](https://arxiv.org/abs/2610.41968) | Prune Gradually, Adapt Sparsely: Efficient Pruning of Large Language Models at Extreme Sparsity | 2026-10-31 00:17:43+08:00 | pruning | ETAPS 用逐步单调剪枝和小预算稀疏增量恢复，在极高稀疏度下降低困惑度与优化状态成本。 | 7/8/8/8 |

### 评分依据与重点数字

- **2610.42147**：准确率8：多任务接近基线但Tree有退化；压缩7：显著削减计算，KV未缩小；创新9：语义桶与层级索引及原生训练；复现7：配置和内核路线明确，但大规模资源需求高且本轮未运行。 详细方法与实验见 `papers/2026-10/pruning/2610.42147/tech_analysis.md`。
- **2610.42135**：准确率8：多架构少步质量改善；压缩8：参数和采样步有明确削减，非实测同倍加速；创新8：critic容量与步条件的控制实验；复现7：超参数充分，但多模型蒸馏成本高。 详细方法与实验见 `papers/2026-10/knowledge_distillation/2610.42135/tech_analysis.md`。
- **2610.42128**：准确率8：稳定增益但部分任务未超教师；压缩9：1.7B学生及16.7–24.5×测得加速；创新8：item空间OPD；复现8：任务、损失及训练参数明确，本轮未实训。 详细方法与实验见 `papers/2026-10/knowledge_distillation/2610.42128/tech_analysis.md`。
- **2610.42116**：准确率5：Qwen局部有效但跨家族明显下降；压缩7：目标context KV4×，不含全系统；创新8：选择/预算/转换联合接口；复现6：设置详尽但依赖多模型训练与复杂缓存适配。 详细方法与实验见 `papers/2026-10/other/2610.42116/tech_analysis.md`。
- **2610.42112**：准确率8：256k内高稀疏仍较稳；压缩6：访问显著减少但速度仅预测、KV未删；创新9：递归LSE摘要与top-p；复现5：训练可描述，但缺优化内核及超长实测。 详细方法与实验见 `papers/2026-10/pruning/2610.42112/tech_analysis.md`。
- **2610.42084**：准确率7：外推退化明显缓解但非跨模型一致；压缩4：实测仅1.21×且无参数缩减；创新7：摘要检索与控制质量校正；复现7：细节充分但本轮未运行。 详细方法与实验见 `papers/2026-10/other/2610.42084/tech_analysis.md`。
- **2610.42031**：准确率8：短长视频与消融支撑；压缩8：少步生成和有界历史，FPS可核验；创新7：统一判别任务与记忆选择；复现7：配置清楚但训练资源重。 详细方法与实验见 `papers/2026-10/knowledge_distillation/2610.42031/tech_analysis.md`。
- **2610.42030**：准确率6：仅0.8B获益；压缩2：不减少孪生参数且增加计算；创新8：严格双对照揭示边界；复现8：协议、种子与统计充分，但本轮未训练。 详细方法与实验见 `papers/2026-10/other/2610.42030/tech_analysis.md`。
- **2610.42018**：准确率6：单步相对增益大但绝对准确率低；压缩7：轨迹压到单调用但缺统一时延；创新9：联合时间状态与半群蒸馏；复现7：小模型设置充分，本轮未训练。 详细方法与实验见 `papers/2026-10/knowledge_distillation/2610.42018/tech_analysis.md`。
- **2610.41970**：准确率3：剪枝动作质量未评测；压缩4：FLOPs减半但端到端仅1.152×；创新8：前提优先的负面审计；复现8：硬件、计时与统计细节明确，本轮未执行。 详细方法与实验见 `papers/2026-10/pruning/2610.41970/tech_analysis.md`。
- **2610.41968**：准确率7：高稀疏胜强基线但距dense较远；压缩8：非零大幅减少、状态5×，推理尚未量化；创新8：单调渐进与稀疏适配耦合；复现8：数据、资源与超参明确，本轮未训练。 详细方法与实验见 `papers/2026-10/pruning/2610.41968/tech_analysis.md`。

优先阅读 ETAPS（高稀疏剪枝的质量/训练状态折中）、DecisionRank（单次前向任务蒸馏）和 LSA（语义稀疏索引）。比较加速数字时必须注意：ZHA为roofline外推；LSA单层与整模加速不同；ACCT计入source prefill后部分方向变慢；Any Forcing首帧仍2/4步；ETAPS的5×是训练persistent state；Cosmos剪枝没有动作质量验证。

## 3. 全量召回与日期覆盖

直接抓取官方HTML，未调用export.arxiv.org/api/query或submittedDate API。十入口均show=2000、skip=0，实际条目数与总数一致，均少于2000，无需后续分页。new包含new submissions、cross submissions及replacement；recent覆盖全部可见日期组。

| 分类 | new 总数/实读（新投/交叉/替换） | recent 总数/实读 | recent日期组 |
|---|---|---|---|
| cs.LG | [337/337](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)（111/87/139） | [1431/1431](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0) | 11-02、10-30、10-28、10-27、10-26 |
| cs.CL | [138/138](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)（46/40/52） | [707/707](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0) | 11-02、10-30、10-28、10-27、10-26 |
| cs.CV | [165/165](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)（76/26/63） | [914/914](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0) | 11-02、10-30、10-28、10-27、10-26 |
| cs.AI | [297/297](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)（98/88/111） | [1454/1454](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0) | 11-02、10-30、10-28、10-27、10-26 |
| cs.AR | [5/5](https://arxiv.org/list/cs.AR/new?show=2000&skip=0)（1/1/3） | [68/68](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0) | 11-02、10-30、10-28、10-27、10-26 |

共5516条列表出现记录，跨分类/入口及版本规范化去重后3672个ID。全部解析官方abs标题、摘要、主/交叉分类、v1时间；613页本轮获取，3059页复用保存来源及SHA256的官方原始HTML并重新解析。69篇处于窗口内，逐篇阅读完整摘要；13个候选/边界论文阅读官方HTML方法实验，最终纳入11。窗口内69页和相邻日对照页又全部本轮刷新，标题、摘要、分类和v1四字段一致，无抓取或解析错误。3603条因v1在窗口外排除，不宣称人工精读它们全部摘要或全文。

相邻日阳性对照：[2610.41939](https://arxiv.org/abs/2610.41939) 的v1为2026-10-30T23:57:51+08:00，在11月2日公开列表可见但按日期排除；窗口最早可见记录[2610.41946](https://arxiv.org/abs/2610.41946)为2026-10-31T00:04:23+08:00，最晚[2610.42152](https://arxiv.org/abs/2610.42152)为2026-10-31T01:59:59+08:00。这验证了本地午夜转换边界，而非将公告日期当提交日。

关键词与同义表达仅作复核，不作召回门槛：quantization, quantize, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, distill, teacher, student, KV cache compression, mixed precision, GPTQ, AWQ, low precision, sparse attention, weight sharing, few-step, one-step, token pruning。逐条决定、关键词命中、分组实计、候选时间及来源详见 `metadata/2026-10/retrieval_dedup_audit.json`。

边界排除：LARC连续latent reasoning主要验证质量，没有模型资源压缩证据；MoETok在等active FFN计算预算下增加专家能力，没有压缩既有模型的对照；Flide/REA属于执行编排；CausalWAM稀疏性用于因果识别；DAMI仅改初始化；全景self-distillation与Geo-FSRL并未进一步压缩部署模型。

## 4. 历史去重审计

fetch后逐一执行52个历史远端分支的ls-tree，并读取各分支metadata索引。真实tech_analysis.md规范化ID共601；2607.27951、2607.28410、2607.28457仅见metadata、没有对应真实精读，未算完成。相关列表出现28次，经跨日期/分类/入口去重归并为11个ID，再排除历史已完成集合。

历史重复ID与来源分支：无（excluded_duplicate_ids=[]）。本次11个新增ID与历史601个ID交集为空。当前2026-11-03分支此前不存在，不参与历史集合；未推送的旧本地草稿不视为远端已完成。

最终新增ID：2610.41968, 2610.41970, 2610.42018, 2610.42030, 2610.42031, 2610.42084, 2610.42112, 2610.42116, 2610.42128, 2610.42135, 2610.42147。

本次纳入ID的列表出现次数：2610.41968×2, 2610.41970×2, 2610.42018×2, 2610.42030×4, 2610.42031×2, 2610.42084×2, 2610.42112×4, 2610.42116×2, 2610.42128×2, 2610.42135×4, 2610.42147×2。

扫描分支与固定SHA（不是从这些分支继承成果）：

| 历史远端分支 | SHA | 真实精读ID数 |
|---|---|---:|
| `origin/feature/arxiv-daily-2026-07-29` | `37139ece193fa4d66212a2f2951ed88a8d83b76a` | 20 |
| `origin/feature/arxiv-daily-2026-07-30` | `8fe81f3241431f5f6af227ce768402d6f91f97ca` | 8 |
| `origin/feature/arxiv-daily-2026-07-31` | `25e3d35f37713e9b407a24c6f7b045dd26208f92` | 7 |
| `origin/feature/arxiv-daily-2026-08-01` | `29b36a60ead969c281bd57e4fb6efd9e0001f6b1` | 29 |
| `origin/feature/arxiv-daily-2026-08-02` | `f397bf7f726f7b7b8286a035d43da5c12236d336` | 4 |
| `origin/feature/arxiv-daily-2026-08-03` | `69a31ee7e2fea63cf20be9c34ca847ad58ab4ea5` | 12 |
| `origin/feature/arxiv-daily-2026-08-04` | `f798a00e0569952212d0e6451f00ba6ea28de99a` | 12 |
| `origin/feature/arxiv-daily-2026-08-05` | `333264be93bb365ee7d29436235e6b056427943e` | 12 |
| `origin/feature/arxiv-daily-2026-08-06` | `67600577ca268cd88675d221f0e19fdb59673789` | 30 |
| `origin/feature/arxiv-daily-2026-08-07` | `87a4eb0f56e25253b22b8c7e9a288af8a467386a` | 50 |
| `origin/feature/arxiv-daily-2026-08-08` | `4f19f7ec424ae7c273a5ae9a01fdc4aa1fbc07ff` | 60 |
| `origin/feature/arxiv-daily-2026-08-10` | `652ee043ff7fad81734a95010b9b49b6dca1ec11` | 9 |
| `origin/feature/arxiv-daily-2026-08-12` | `5dea9ebeff4db72522e85962764ae51a4978a4e6` | 12 |
| `origin/feature/arxiv-daily-2026-08-14` | `fe27109ab9b86bd7b9ac4a4393dde4a77bb3b372` | 10 |
| `origin/feature/arxiv-daily-2026-08-15` | `e463baea815c06d95ffc36eec034113b28db7927` | 0 |
| `origin/feature/arxiv-daily-2026-08-16` | `940ef56b2ebd4bd22ce5636302234aaa63691e2d` | 0 |
| `origin/feature/arxiv-daily-2026-08-17` | `1320530c9060d6acfd6a6814ebe65415b62c760d` | 0 |
| `origin/feature/arxiv-daily-2026-08-18` | `2190e4aef62423032c78b7594a0e208c6d128c0d` | 0 |
| `origin/feature/arxiv-daily-2026-08-19` | `3518b1fff91bab3cd78421810c0798177060063f` | 22 |
| `origin/feature/arxiv-daily-2026-08-20` | `6413646a6fec8b54f937415084c2df3e99b358a1` | 9 |
| `origin/feature/arxiv-daily-2026-08-21` | `dc8a46573315edb88419bb4eb181bea89d209de7` | 12 |
| `origin/feature/arxiv-daily-2026-08-22` | `0dd4154cce8306873ec37767b6ab27e00b07735f` | 14 |
| `origin/feature/arxiv-daily-2026-08-23` | `e1a83986b75aec3a0289a50082ac44a6b359a130` | 0 |
| `origin/feature/arxiv-daily-2026-08-24` | `574caeb9b2e6e763f4a216b80bfa33b539f8c71b` | 0 |
| `origin/feature/arxiv-daily-2026-08-25` | `508ce04ebcda0238aceb1d32991db50aac8904e0` | 0 |
| `origin/feature/arxiv-daily-2026-08-26` | `4a627bc35cb9075ac416e12165c9418f79e1bbee` | 19 |
| `origin/feature/arxiv-daily-2026-08-27` | `f57ca87589c728a68851f21acdff1c333b402e35` | 27 |
| `origin/feature/arxiv-daily-2026-08-28` | `daeb352421a9263136927bc71497c86ddb512c77` | 30 |
| `origin/feature/arxiv-daily-2026-08-29` | `e73be2a46c726bdd0a42b13b8d3ec75b5dfd9060` | 38 |
| `origin/feature/arxiv-daily-2026-08-30` | `0cff4d39f94bca3cfdf18e85e8f056850bad6bda` | 0 |
| `origin/feature/arxiv-daily-2026-08-31` | `d21ad3ba2970c7664ffd084b568f61b1dbde8866` | 0 |
| `origin/feature/arxiv-daily-2026-09-01` | `ebb94ff45394bcf77d90c41d5f4eec02dc948b0b` | 0 |
| `origin/feature/arxiv-daily-2026-09-02` | `ab05a346a491f043142867c74593f45e669812d1` | 60 |
| `origin/feature/arxiv-daily-2026-09-03` | `710202d696a1295b25e55f50d4fee966434549d4` | 56 |
| `origin/feature/arxiv-daily-2026-09-04` | `623673ccf816fda6de51daf471f55c79b0a24801` | 31 |
| `origin/feature/arxiv-daily-2026-09-05` | `1ab9858c9e986133aafa40226b1c5af0a760c175` | 37 |
| `origin/feature/arxiv-daily-2026-09-06` | `05108f7ef5b13b0fcc118d633a53c99d31d55166` | 1 |
| `origin/feature/arxiv-daily-2026-09-07` | `4fa4065a723520e6413d4bed69790612999517cd` | 0 |
| `origin/feature/arxiv-daily-2026-09-08` | `3db8912129f5ebdfb2399a213f0688ac30cdf971` | 5 |
| `origin/feature/arxiv-daily-2026-09-09` | `88c76b0c8b21a4a366dbba0de17d2c63327dcca8` | 0 |
| `origin/feature/arxiv-daily-2026-09-14` | `5068f2a8c89b815b69665b35900fd0e8d3800a54` | 3 |
| `origin/feature/arxiv-daily-2026-09-15` | `b580dd8c66660802f18e5c25bdff7f9ad0f85e66` | 4 |
| `origin/feature/arxiv-daily-2026-09-21` | `263f4647c46bdea7fd86ecdabca69c889ef96806` | 7 |
| `origin/feature/arxiv-daily-2026-09-22` | `7b0317385f6f8b9e6e79d2863a7e4d7a3a355968` | 2 |
| `origin/feature/arxiv-daily-2026-09-29` | `2874106cd594d482ab71a00c8b6ef5fdf3622cbb` | 7 |
| `origin/feature/arxiv-daily-2026-10-12` | `252ce3d0f428984f276bb380dea030f165e9e9d3` | 12 |
| `origin/feature/arxiv-daily-2026-10-13` | `52bf4827692c57ccabbd1dd61a6e4641b683379f` | 5 |
| `origin/feature/arxiv-daily-2026-10-14` | `71c9c681c89725a10453f8fdee59633fcebb1bec` | 0 |
| `origin/feature/arxiv-daily-2026-10-19` | `883eb5828be85a82364fc08bcf40ea2295443902` | 17 |
| `origin/feature/arxiv-daily-2026-10-20` | `5a0766dd8748557393073127bb2557ad7b5b54a7` | 6 |
| `origin/feature/arxiv-daily-2026-10-27` | `b8974213ae16f5787f9e4287835b1351fa632048` | 3 |
| `origin/feature/arxiv-daily-2026-11-02` | `6cd5cf9f0a49338bd3ec14733d247547db914688` | 8 |

## 5. 复现、独立快照与未完成项

新增量化论文为0，故未建立scripts/quantization论文目录，也没有Qwen3-0.6B复现命令、日志或性能结果。11篇均为全文精读；本轮没有执行非量化方法训练、GPU kernel、视频生成、机器人模拟或性能基准。用户要求的量化复现本次不适用，所有实验数字均明确标为作者报告。

分支 `feature/arxiv-daily-2026-11-03` 严格从最新 `origin/main`（`abfe8f2767d8bf881d586718ab4db33fc576be6a`）建立，隔离linked worktree，原工作树未提交改动未带入。只清理main自带2026-07-28旧日报；papers仅说明和本次11篇，reports仅说明和本日报，scripts仅通用README，metadata仅说明和10月新增索引/CSV/本次检索去重审计。

论文按真实本地提交月份全部放在2026-10；日报放在主日期所属2026-11。没有11月新增论文，故未创建空11月论文索引。提交与推送前验证论文目录、索引、CSV一致及量化目录为空；提交只允许一个直接父为origin/main的本次提交。远端SHA及merge-base验证结果另存自动化运行记录，避免在提交内容中自引用本提交SHA。

原始HTML、缓存来源哈希、完整历史树与远端验证记录保存在本机自动化 runs/2026-11-03。仓库内审计文件提供可重查官方链接、分组计数、52分支SHA和69篇窗口语义决定。
