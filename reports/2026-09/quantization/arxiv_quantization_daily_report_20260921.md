# arXiv 模型压缩论文日报：2026-09-21

运行日：2026-09-22；核验完成时间：2026-09-22T01:14:50.571504+08:00。
检索窗口：北京时间2026-09-19、09-20、09-21三个完整自然日，00:00:00–23:59:59。归档依据为官方详情页Submission history的v1时间转换为Asia/Shanghai，公告日仅用于核验列表覆盖。

本窗口相关论文 **2篇**，历史重复 **0篇**，本次新增 **2篇**。历史扫描43个日更分支，已有真实精读541个规范ID。

## 逐日计数与公开时效

| 实际v1本地日期 | 窗口内全主题记录 | 相关原始出现次数 | 相关规范ID数 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|---:|
| 2026-09-19 | 34 | 4 | 2 | 0 | 2 |
| 2026-09-20 | 0 | 0 | 0 | 0 | 0 |
| 2026-09-21 | 0 | 0 | 0 | 0 | 0 |

出现次数包含跨分类、new/recent重复；规范ID先去掉版本号再合并，因此不是论文篇数。

- 2026-09-20：**截至运行时 arXiv 官方网页未检出**窗口相关论文；不是因历史去重而归零，也不是对尚未公告投稿的最终零数量判断。后续运行继续三天窗口回查。
- 2026-09-21：**截至运行时 arXiv 官方网页未检出**窗口相关论文；不是因历史去重而归零，也不是对尚未公告投稿的最终零数量判断。后续运行继续三天窗口回查。

## 新增论文完整表

| arXiv ID | 标题 | 作者 | v1 UTC | v1 北京时间 | 分类及结论 |
|---|---|---|---|---|---|
| [2609.22060](https://arxiv.org/abs/2609.22060) | Traffic Sign Recognition for Autonomous Driving Using Branched YOLOv2 and Geometric Features | Arefeh Rezaei | 2026-09-18T17:52:00+00:00 | 2026-09-19T01:52:00+08:00 | Computer Vision and Pattern Recognition (cs.CV)；早退保持mAP 0.680，耗时仅下降约2.07%（整图）或1.21%（逐单元）；无参数压缩证据。 |
| [2609.22083](https://arxiv.org/abs/2609.22083) | MintAct: A Unified Visual Agent for Digital Environments | Mingfei Gao , Rui Tian , Haiming Gang , Bohan Zhai , Le Zhang , Yuanzheng Gong , Di Feng , Ege Özsoy , Kaixin Ma , Vishwesh Kirthivasan , Oğuzhan Fatih Kar , Roman Bachmann , Anders Boesen Lindbo Larsen , Afshin Dehghan | 2026-09-18T17:59:34+00:00 | 2026-09-19T01:59:34+08:00 | Computer Vision and Pattern Recognition (cs.CV)；四域专家轨迹蒸馏为单模型，8B Weblica 57.5→72.8；桌面仍低于教师，最终RL收益单独核算。 |

## 评分及证据边界

评分为1–10的编辑判断，越高越好；压缩分考察实证收益和证据完整性，不能直接换算为倍数。

| 论文 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 依据 |
|---|---:|---:|---:|---:|---|
| Branched YOLOv2 | 5 | 2 | 3 | 3 | 300张测试图上早退mAP保持0.680；约1.021/1.012倍加速，无权重压缩证据；2019硕士论文扩展；缺完整出口实现及计时统计。 |
| MintAct | 8 | 5 | 7 | 5 | 多规模SFT→RFT消融支持蒸馏效果，但8B桌面仍低教师6.1点；四专家→单权重集合，未测端到端压缩倍数；训练配方清楚、环境与资源门槛高。 |

MintAct最终桌面48.9包含后续联合RL，不应全部算作蒸馏收益。YOLOv2推理几何分支的0.713 mAP与早退0.6470 s属于不同配置，不可拼接；几何分支本身耗时0.6714 s。详见两篇六节精读及官方全文。

## 官方网页全量覆盖证据

五分类各读取new与recent，均使用`show=2000`，总数小于2000，单页覆盖1至末条，无需额外skip分页。下面逐页声明数量=实读数量；new同时包含新投稿、交叉与替换。recent五组按09-21/18/17/16/15排列，含窗口外相邻日期对照。

| 官方入口 | 声明/实读 | 实际范围 | 各分组条目数（逐组核对） |
|---|---:|---|---|
| [cs.LG/new?show=2000](https://arxiv.org/list/cs.LG/new?show=2000) | 237/237 | 1–237 | New submissions (showing 83 of 83 entries): 实读83; Cross submissions (showing 66 of 66 entries): 实读66; Replacement submissions (showing 88 of 88 entries): 实读88 |
| [cs.LG/recent?show=2000](https://arxiv.org/list/cs.LG/recent?show=2000) | 1118/1118 | 1–1118 | Mon, 21 Sep 2026 (showing 149 of 149 entries ): 实读149; Fri, 18 Sep 2026 (showing 198 of 198 entries ): 实读198; Thu, 17 Sep 2026 (showing 219 of 219 entries ): 实读219; Wed, 16 Sep 2026 (showing 186 of 186 entries ): 实读186; Tue, 15 Sep 2026 (showing 366 of 366 entries ): 实读366 |
| [cs.CL/new?show=2000](https://arxiv.org/list/cs.CL/new?show=2000) | 138/138 | 1–138 | New submissions (showing 65 of 65 entries): 实读65; Cross submissions (showing 22 of 22 entries): 实读22; Replacement submissions (showing 51 of 51 entries): 实读51 |
| [cs.CL/recent?show=2000](https://arxiv.org/list/cs.CL/recent?show=2000) | 631/631 | 1–631 | Mon, 21 Sep 2026 (showing 87 of 87 entries ): 实读87; Fri, 18 Sep 2026 (showing 104 of 104 entries ): 实读104; Thu, 17 Sep 2026 (showing 127 of 127 entries ): 实读127; Wed, 16 Sep 2026 (showing 109 of 109 entries ): 实读109; Tue, 15 Sep 2026 (showing 204 of 204 entries ): 实读204 |
| [cs.CV/new?show=2000](https://arxiv.org/list/cs.CV/new?show=2000) | 141/141 | 1–141 | New submissions (showing 74 of 74 entries): 实读74; Cross submissions (showing 24 of 24 entries): 实读24; Replacement submissions (showing 43 of 43 entries): 实读43 |
| [cs.CV/recent?show=2000](https://arxiv.org/list/cs.CV/recent?show=2000) | 697/697 | 1–697 | Mon, 21 Sep 2026 (showing 98 of 98 entries ): 实读98; Fri, 18 Sep 2026 (showing 125 of 125 entries ): 实读125; Thu, 17 Sep 2026 (showing 118 of 118 entries ): 实读118; Wed, 16 Sep 2026 (showing 123 of 123 entries ): 实读123; Tue, 15 Sep 2026 (showing 233 of 233 entries ): 实读233 |
| [cs.AI/new?show=2000](https://arxiv.org/list/cs.AI/new?show=2000) | 214/214 | 1–214 | New submissions (showing 49 of 49 entries): 实读49; Cross submissions (showing 76 of 76 entries): 实读76; Replacement submissions (showing 89 of 89 entries): 实读89 |
| [cs.AI/recent?show=2000](https://arxiv.org/list/cs.AI/recent?show=2000) | 1147/1147 | 1–1147 | Mon, 21 Sep 2026 (showing 125 of 125 entries ): 实读125; Fri, 18 Sep 2026 (showing 215 of 215 entries ): 实读215; Thu, 17 Sep 2026 (showing 204 of 204 entries ): 实读204; Wed, 16 Sep 2026 (showing 195 of 195 entries ): 实读195; Tue, 15 Sep 2026 (showing 408 of 408 entries ): 实读408 |
| [cs.AR/new?show=2000](https://arxiv.org/list/cs.AR/new?show=2000) | 14/14 | 1–14 | New submissions (showing 4 of 4 entries): 实读4; Cross submissions (showing 2 of 2 entries): 实读2; Replacement submissions (showing 8 of 8 entries): 实读8 |
| [cs.AR/recent?show=2000](https://arxiv.org/list/cs.AR/recent?show=2000) | 74/74 | 1–74 | Mon, 21 Sep 2026 (showing 6 of 6 entries ): 实读6; Fri, 18 Sep 2026 (showing 13 of 13 entries ): 实读13; Thu, 17 Sep 2026 (showing 16 of 16 entries ): 实读16; Wed, 16 Sep 2026 (showing 15 of 15 entries ): 实读15; Tue, 15 Sep 2026 (showing 24 of 24 entries ): 实读24 |

合计4411次列表出现，合并为2971个规范ID；2971个官方/abs页全部于本次重新下载，标题、摘要、分类与v1均解析成功，失败0。未调用arXiv API。先按v1排除窗口外旧稿，再对窗口内34篇逐篇语义审阅；另审阅最新75条邻接记录，不声称人工独立精读全部窗口外旧稿。关键词仅作复核，没有关键词召回门槛。

复核词覆盖quantization/quantize/low-bit/model compression/compress/pruning/sparsity/knowledge distillation/distill/teacher/student/KV cache compression/mixed precision/GPTQ/AWQ及早退、条件计算、专家整合等语义。MintAct由全文中的专家蒸馏证据纳入，体现了不依赖摘要关键词筛选。

窗口外阳性对照：实际v1为北京时间09-18的350篇可见记录。午夜边界举例：
- [2609.21942](https://arxiv.org/abs/2609.21942)：v1 2026-09-18T15:56:52+00:00 = 2026-09-18T23:56:52+08:00。
- [2609.21944](https://arxiv.org/abs/2609.21944)：v1 2026-09-18T16:00:29+00:00 = 2026-09-19T00:00:29+08:00。

## 历史去重审计

成功执行`git fetch --prune origin`后，逐一对全部43个`origin/feature/arxiv-daily-*`执行`git ls-tree -r --name-only`，从真实`papers/**/<id>/tech_analysis.md`得到541个已分析ID，并用`git show`读取各分支metadata交叉检查。metadata中的544个ID中，2607.27951、2607.28410、2607.28457缺少真实精读，不视为完成。

窗口跨日期、跨分类、跨关键词合并后才排除历史集合。本次重复ID与来源分支：**无**；最终新增ID：2609.22060、2609.22083；与历史已分析集合交集：**空集**。当日远端分支在开始时不存在，不把新建本地分支误作历史。

扫描分支及固定SHA如下（仅作为审计引用，没有复制历史成果）：

| 历史远端分支 | 扫描SHA | 分支内规范ID数 |
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

## 窗口内逐篇语义审阅

| ID | 本地v1时间 | 决策 | 理由 |
|---|---|---|---|
| [2609.21944](https://arxiv.org/abs/2609.21944) | 2026-09-19T00:00:29+08:00 | excluded | 量子博弈张量收缩与均衡求解，不是机器学习模型压缩。 |
| [2609.21945](https://arxiv.org/abs/2609.21945) | 2026-09-19T00:03:11+08:00 | excluded | 城市交通仿真低维状态表示及控制，压缩对象是系统状态数据。 |
| [2609.21948](https://arxiv.org/abs/2609.21948) | 2026-09-19T00:05:03+08:00 | excluded | 跨具身潜动作表征和VLA预训练，不是已有模型的量化/剪枝/蒸馏。 |
| [2609.21953](https://arxiv.org/abs/2609.21953) | 2026-09-19T00:11:05+08:00 | excluded | 人机任务分流与专家能力估计，不是多教师模型蒸馏或内部早退。 |
| [2609.21960](https://arxiv.org/abs/2609.21960) | 2026-09-19T00:18:26+08:00 | excluded | 离散扩散tau-leaping调度的因子分解误差理论，无学生蒸馏或模型压缩。 |
| [2609.21962](https://arxiv.org/abs/2609.21962) | 2026-09-19T00:22:31+08:00 | excluded | 心电生物识别跨时间评测，不是模型压缩。 |
| [2609.21967](https://arxiv.org/abs/2609.21967) | 2026-09-19T00:27:22+08:00 | excluded | 官方全文核验：TTS采用既有RVQ音频编码及MoG输出头，RVQ压缩音频表示；权重BF16/FP32，作者明确未评测低精度/量化变体，无模型压缩主线。 |
| [2609.21976](https://arxiv.org/abs/2609.21976) | 2026-09-19T00:38:29+08:00 | excluded | 博弈遗憾界与学习规则，不是模型压缩。 |
| [2609.21989](https://arxiv.org/abs/2609.21989) | 2026-09-19T00:49:46+08:00 | excluded | 时间序列潜空间压缩后频谱对齐，压缩对象是信号数据，不是模型。 |
| [2609.21992](https://arxiv.org/abs/2609.21992) | 2026-09-19T00:51:07+08:00 | excluded | 道德标注不确定性贝叶斯建模，不是模型压缩。 |
| [2609.21995](https://arxiv.org/abs/2609.21995) | 2026-09-19T00:56:45+08:00 | excluded | 热工流体ML模型跨场景评测，不是模型压缩。 |
| [2609.21996](https://arxiv.org/abs/2609.21996) | 2026-09-19T00:57:00+08:00 | excluded | 语言模型内部知识探针与遗忘验证，不是压缩。 |
| [2609.21997](https://arxiv.org/abs/2609.21997) | 2026-09-19T00:57:14+08:00 | excluded | 代理意见动力学的外部信念层，不是模型压缩。 |
| [2609.22000](https://arxiv.org/abs/2609.22000) | 2026-09-19T01:00:56+08:00 | excluded | 计算机使用代理训练环境与基准，轨迹训练不是以模型压缩为研究目标。 |
| [2609.22005](https://arxiv.org/abs/2609.22005) | 2026-09-19T01:03:58+08:00 | excluded | 官方全文核验：增加少量门控/汇点参数、无生成计算成本变化；噪声过滤不等同token剪枝或KV缓存压缩。 |
| [2609.22008](https://arxiv.org/abs/2609.22008) | 2026-09-19T01:06:44+08:00 | excluded | VLM行为诊断与概念因果评估，不是模型压缩。 |
| [2609.22012](https://arxiv.org/abs/2609.22012) | 2026-09-19T01:08:41+08:00 | excluded | 拓扑持久性模块的有证嵌入，不是模型压缩。 |
| [2609.22038](https://arxiv.org/abs/2609.22038) | 2026-09-19T01:30:27+08:00 | excluded | 语言知识基准，不是模型压缩。 |
| [2609.22039](https://arxiv.org/abs/2609.22039) | 2026-09-19T01:31:05+08:00 | excluded | 对话AI研究复现实验平台，不是模型压缩。 |
| [2609.22040](https://arxiv.org/abs/2609.22040) | 2026-09-19T01:31:34+08:00 | excluded | VLA加入最多29.7M参数的反馈机制，提高感知，不是模型压缩。 |
| [2609.22041](https://arxiv.org/abs/2609.22041) | 2026-09-19T01:33:38+08:00 | excluded | Flow-GRPO重要性比稳定化与梯度分配，不是量化或蒸馏。 |
| [2609.22043](https://arxiv.org/abs/2609.22043) | 2026-09-19T01:34:13+08:00 | excluded | 外部RAG记忆可信度控制，零参数控制器不改变底层LLM大小。 |
| [2609.22048](https://arxiv.org/abs/2609.22048) | 2026-09-19T01:36:52+08:00 | excluded | 选择性预测安全认证和有限样本统计，不是模型压缩。 |
| [2609.22053](https://arxiv.org/abs/2609.22053) | 2026-09-19T01:46:08+08:00 | excluded | GCN训练前图标签修正，移除的是噪声标签，不是网络参数。 |
| [2609.22055](https://arxiv.org/abs/2609.22055) | 2026-09-19T01:46:28+08:00 | excluded | 世界模型持续学习评测，模块复用不构成压缩既有网络。 |
| [2609.22056](https://arxiv.org/abs/2609.22056) | 2026-09-19T01:48:15+08:00 | excluded | 检索置信度及弃答校准，不是模型压缩。 |
| [2609.22060](https://arxiv.org/abs/2609.22060) | 2026-09-19T01:52:00+08:00 | included | 纳入other：YOLOv2中间出口和条件深度执行，报告实际延迟对照；没有参数压缩证据。 |
| [2609.22064](https://arxiv.org/abs/2609.22064) | 2026-09-19T01:54:32+08:00 | excluded | 跨动物神经数据预训练基准，不是模型压缩。 |
| [2609.22067](https://arxiv.org/abs/2609.22067) | 2026-09-19T01:55:09+08:00 | excluded | 代理委托的人机交互价值研究，不是模型压缩。 |
| [2609.22068](https://arxiv.org/abs/2609.22068) | 2026-09-19T01:55:17+08:00 | excluded | 从代码构造RL环境并训练编码代理，不是模型蒸馏压缩。 |
| [2609.22069](https://arxiv.org/abs/2609.22069) | 2026-09-19T01:55:49+08:00 | excluded | 参考视频生成数据集和基准，不是模型压缩。 |
| [2609.22081](https://arxiv.org/abs/2609.22081) | 2026-09-19T01:59:10+08:00 | excluded | 职业事故文本分类跨行业迁移，不是模型压缩。 |
| [2609.22083](https://arxiv.org/abs/2609.22083) | 2026-09-19T01:59:34+08:00 | included | 纳入knowledge_distillation：正文明确四域RL专家轨迹经成功筛选蒸馏到单模型，并报告RFT阶段消融。 |
| [2609.22086](https://arxiv.org/abs/2609.22086) | 2026-09-19T01:59:56+08:00 | excluded | 冻结模型的外部自然语言程序记忆更新，无权重更新，非模型或KV缓存压缩。 |

边界全文证据：[VoiceChat](https://arxiv.org/html/2609.21967v1)的RVQ是音频编码，作者明确未评测量化模型；[注意力噪声门控](https://arxiv.org/html/2609.22005v1)增加少量参数、不改变生成计算成本，因此不计模型压缩。窗口外相邻的[21849](https://arxiv.org/abs/2609.21849)和[21870](https://arxiv.org/abs/2609.21870)实际北京时间均为09-18，未混入本次成果。

## 独立快照、复现与验证

分支`feature/arxiv-daily-2026-09-22`严格从最新`origin/main`（`abfe8f2767d8bf881d586718ab4db33fc576be6a`）创建隔离linked worktree。原工作树6项用户未提交改动以status及全部修改/未跟踪文件SHA256保护。清理main自带的07-28历史日报；papers只保留说明及本次两篇，reports只保留说明及本日报，metadata只保留说明及本次索引/CSV，scripts仅说明且无历史quantization目录。

本次新增量化论文0篇，Qwen3-0.6B量化复现不适用，未创建空壳demo或伪造模型运行结果。两篇非量化原论文训练未本机复现：YOLO需要论文合成数据与精确分支实现，MintAct需要专家、评判器、多平台交互环境及论文训练资源。全文可得，无摘要推测实验数值。

提交门禁核验：六节格式、官方v1日期、论文目录与metadata/CSV ID一致、量化目录与空量化集合一致、历史零交集、无窗口外成果、diff清理范围与单提交main基线关系。Git最终SHA和远端验证结果在本次任务完成汇报给出，避免在提交内容中自引用自身SHA。
