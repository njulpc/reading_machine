# arXiv 模型压缩日报：2026-11-01

运行日：2026-11-02，Asia/Shanghai。固定窗口：2026-10-30 00:00至2026-11-01 23:59。本报告覆盖三天，主日期11月1日。

## 检索结果与去重审计

窗口相关8篇，历史重复0篇，本次新增8篇（量化1、知识蒸馏2、其他5）。逐日相关数为10月30日8、10月31日0、11月1日0。后两日只能表述为“截至运行时 arXiv 官方网页未检出”，并不表示实际没有投稿；之后运行继续三天回查。

fetch后逐一读取51个远端日更分支的完整论文树，并交叉读取各metadata索引；真实tech_analysis.md规范化ID共593个。metadata-only的2607.27951、2607.28410、2607.28457不算完成。当前11月2日远端分支开始时不存在；未将任何未推送的本地草稿算作历史已完成。

全部6569次列表出现先按去版本ID合并为3970个记录，再解析官方v1时间。97篇落入窗口，逐篇读取完整题名和摘要作语义判断，8篇纳入。窗口外记录以v1日期排除，不宣称逐篇人工语义精读全部3970篇。98个详情页（97窗口+1相邻日期对照）本轮新获取，题名、摘要、分类、v1全部与原始缓存一致；所有缓存有来源和SHA256。关键词只作复核，不作召回门槛。

相关记录跨分类/入口的原始出现数：24，归并8个ID后与593个历史ID取交集为空。排除的历史重复ID及来源分支：无。最终ID：2610.40345, 2610.40454, 2610.40576, 2610.40611, 2610.40614, 2610.40618, 2610.40637, 2610.40647。

历史源分支清单（全部已逐树扫描）：

- `origin/feature/arxiv-daily-2026-07-29` @ `37139ece193fa4d66212a2f2951ed88a8d83b76a`
- `origin/feature/arxiv-daily-2026-07-30` @ `8fe81f3241431f5f6af227ce768402d6f91f97ca`
- `origin/feature/arxiv-daily-2026-07-31` @ `25e3d35f37713e9b407a24c6f7b045dd26208f92`
- `origin/feature/arxiv-daily-2026-08-01` @ `29b36a60ead969c281bd57e4fb6efd9e0001f6b1`
- `origin/feature/arxiv-daily-2026-08-02` @ `f397bf7f726f7b7b8286a035d43da5c12236d336`
- `origin/feature/arxiv-daily-2026-08-03` @ `69a31ee7e2fea63cf20be9c34ca847ad58ab4ea5`
- `origin/feature/arxiv-daily-2026-08-04` @ `f798a00e0569952212d0e6451f00ba6ea28de99a`
- `origin/feature/arxiv-daily-2026-08-05` @ `333264be93bb365ee7d29436235e6b056427943e`
- `origin/feature/arxiv-daily-2026-08-06` @ `67600577ca268cd88675d221f0e19fdb59673789`
- `origin/feature/arxiv-daily-2026-08-07` @ `87a4eb0f56e25253b22b8c7e9a288af8a467386a`
- `origin/feature/arxiv-daily-2026-08-08` @ `4f19f7ec424ae7c273a5ae9a01fdc4aa1fbc07ff`
- `origin/feature/arxiv-daily-2026-08-10` @ `652ee043ff7fad81734a95010b9b49b6dca1ec11`
- `origin/feature/arxiv-daily-2026-08-12` @ `5dea9ebeff4db72522e85962764ae51a4978a4e6`
- `origin/feature/arxiv-daily-2026-08-14` @ `fe27109ab9b86bd7b9ac4a4393dde4a77bb3b372`
- `origin/feature/arxiv-daily-2026-08-15` @ `e463baea815c06d95ffc36eec034113b28db7927`
- `origin/feature/arxiv-daily-2026-08-16` @ `940ef56b2ebd4bd22ce5636302234aaa63691e2d`
- `origin/feature/arxiv-daily-2026-08-17` @ `1320530c9060d6acfd6a6814ebe65415b62c760d`
- `origin/feature/arxiv-daily-2026-08-18` @ `2190e4aef62423032c78b7594a0e208c6d128c0d`
- `origin/feature/arxiv-daily-2026-08-19` @ `3518b1fff91bab3cd78421810c0798177060063f`
- `origin/feature/arxiv-daily-2026-08-20` @ `6413646a6fec8b54f937415084c2df3e99b358a1`
- `origin/feature/arxiv-daily-2026-08-21` @ `dc8a46573315edb88419bb4eb181bea89d209de7`
- `origin/feature/arxiv-daily-2026-08-22` @ `0dd4154cce8306873ec37767b6ab27e00b07735f`
- `origin/feature/arxiv-daily-2026-08-23` @ `e1a83986b75aec3a0289a50082ac44a6b359a130`
- `origin/feature/arxiv-daily-2026-08-24` @ `574caeb9b2e6e763f4a216b80bfa33b539f8c71b`
- `origin/feature/arxiv-daily-2026-08-25` @ `508ce04ebcda0238aceb1d32991db50aac8904e0`
- `origin/feature/arxiv-daily-2026-08-26` @ `4a627bc35cb9075ac416e12165c9418f79e1bbee`
- `origin/feature/arxiv-daily-2026-08-27` @ `f57ca87589c728a68851f21acdff1c333b402e35`
- `origin/feature/arxiv-daily-2026-08-28` @ `daeb352421a9263136927bc71497c86ddb512c77`
- `origin/feature/arxiv-daily-2026-08-29` @ `e73be2a46c726bdd0a42b13b8d3ec75b5dfd9060`
- `origin/feature/arxiv-daily-2026-08-30` @ `0cff4d39f94bca3cfdf18e85e8f056850bad6bda`
- `origin/feature/arxiv-daily-2026-08-31` @ `d21ad3ba2970c7664ffd084b568f61b1dbde8866`
- `origin/feature/arxiv-daily-2026-09-01` @ `ebb94ff45394bcf77d90c41d5f4eec02dc948b0b`
- `origin/feature/arxiv-daily-2026-09-02` @ `ab05a346a491f043142867c74593f45e669812d1`
- `origin/feature/arxiv-daily-2026-09-03` @ `710202d696a1295b25e55f50d4fee966434549d4`
- `origin/feature/arxiv-daily-2026-09-04` @ `623673ccf816fda6de51daf471f55c79b0a24801`
- `origin/feature/arxiv-daily-2026-09-05` @ `1ab9858c9e986133aafa40226b1c5af0a760c175`
- `origin/feature/arxiv-daily-2026-09-06` @ `05108f7ef5b13b0fcc118d633a53c99d31d55166`
- `origin/feature/arxiv-daily-2026-09-07` @ `4fa4065a723520e6413d4bed69790612999517cd`
- `origin/feature/arxiv-daily-2026-09-08` @ `3db8912129f5ebdfb2399a213f0688ac30cdf971`
- `origin/feature/arxiv-daily-2026-09-09` @ `88c76b0c8b21a4a366dbba0de17d2c63327dcca8`
- `origin/feature/arxiv-daily-2026-09-14` @ `5068f2a8c89b815b69665b35900fd0e8d3800a54`
- `origin/feature/arxiv-daily-2026-09-15` @ `b580dd8c66660802f18e5c25bdff7f9ad0f85e66`
- `origin/feature/arxiv-daily-2026-09-21` @ `263f4647c46bdea7fd86ecdabca69c889ef96806`
- `origin/feature/arxiv-daily-2026-09-22` @ `7b0317385f6f8b9e6e79d2863a7e4d7a3a355968`
- `origin/feature/arxiv-daily-2026-09-29` @ `2874106cd594d482ab71a00c8b6ef5fdf3622cbb`
- `origin/feature/arxiv-daily-2026-10-12` @ `252ce3d0f428984f276bb380dea030f165e9e9d3`
- `origin/feature/arxiv-daily-2026-10-13` @ `52bf4827692c57ccabbd1dd61a6e4641b683379f`
- `origin/feature/arxiv-daily-2026-10-14` @ `71c9c681c89725a10453f8fdee59633fcebb1bec`
- `origin/feature/arxiv-daily-2026-10-19` @ `883eb5828be85a82364fc08bcf40ea2295443902`
- `origin/feature/arxiv-daily-2026-10-20` @ `5a0766dd8748557393073127bb2557ad7b5b54a7`
- `origin/feature/arxiv-daily-2026-10-27` @ `b8974213ae16f5787f9e4287835b1351fa632048`


| v1北京时间日期 | 原始相关出现数（含跨列表重复） | 规范化相关ID数 | 历史重复 | 新增 |
|---|---:|---:|---:|---:|
| 2026-10-30 | 24 | 8 | 0 | 8 |
| 2026-10-31 | 0 | 0 | 0 | 0 |
| 2026-11-01 | 0 | 0 | 0 | 0 |

后两日的0限定为截至运行时的官方网页检出数。

## 官方页面覆盖证据

| 分类 | new总数/实取 | recent总数/实取 | 覆盖 |
|---|---:|---:|---|
| cs.LG | [608/608](https://arxiv.org/list/cs.LG/new?show=2000&skip=0) | [1438/1438](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0) | show=2000, skip=0；单页覆盖全部 |
| cs.CL | [279/279](https://arxiv.org/list/cs.CL/new?show=2000&skip=0) | [738/738](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0) | show=2000, skip=0；单页覆盖全部 |
| cs.CV | [374/374](https://arxiv.org/list/cs.CV/new?show=2000&skip=0) | [926/926](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0) | show=2000, skip=0；单页覆盖全部 |
| cs.AI | [605/605](https://arxiv.org/list/cs.AI/new?show=2000&skip=0) | [1497/1497](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0) | show=2000, skip=0；单页覆盖全部 |
| cs.AR | [32/32](https://arxiv.org/list/cs.AR/new?show=2000&skip=0) | [72/72](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0) | show=2000, skip=0；单页覆盖全部 |

new页面最新公告均为10月30日，包含new submissions、cross submissions和replacement submissions；各分组显示数与实际dt条目数一致。recent五日组为10月30、28、27、26、23日，每组实取等于显示数。10月29日公告缺口由[官方系统状态](https://status.arxiv.org/)说明：10月28日维护，周三晚不公告，稿件合并到周四晚公告。并未把日期分组跳跃自动写成零投稿。

相邻日期阳性对照：[2610.40333](https://arxiv.org/abs/2610.40333) v1为北京时间10月29日23:58:15，列表可见但在窗口外；窗口最早v1为10月30日00:03:19，最新为01:59:53。周末与凌晨运行的可见性限制保留，公告日不替代提交时间。

## 新增论文完整表

| ID / 标题 | 作者 | 实际v1北京时间 | 类别 | 一句话结论 |
|---|---|---|---|---|
| [2610.40647](https://arxiv.org/abs/2610.40647) — [Read, Allocate, Route: Role-Coupled Tokenization for Pixel-Space Generative Transformers](../../../papers/2026-10/other/2610.40647/tech_analysis.md) | Jiongfan Yang , Weichen Fan , Haiwen Diao , Zhongang Cai , Ziwei Liu | 2026-10-30T01:59:21+08:00 | other | SpecSlot 仅让低频槽参与全局注意力，在 ImageNet-512 以少38.2%的FLOPs接近 JiT-B/16 的FID。 |
| [2610.40637](https://arxiv.org/abs/2610.40637) — [world2vec: Mechanistic world models through latent dynamics learning](../../../papers/2026-10/other/2610.40637/tech_analysis.md) | Tobias Schmidt , Rodrigo Gonzalez Laiz , Krisztián Szuppinger , Steffen Schneider | 2026-10-30T01:58:23+08:00 | other | world2vec 用潜在动力学匹配构建263K参数模型，把紧凑性与长期轨迹一致性共同验证。 |
| [2610.40618](https://arxiv.org/abs/2610.40618) — [An ODE-based Sampler for Discrete Diffusion Models](../../../papers/2026-10/knowledge_distillation/2610.40618/tech_analysis.md) | Samson Gourevitch , Yazid Janati , Eric Moulines , Eric P. Xing , Alain Durmus , Giacomo Zanella | 2026-10-30T01:55:25+08:00 | knowledge_distillation | ERF通过连续指数残差建立离散扩散轨迹，ERC在uniform diffusion的2/4次模型调用下显著提高蒸馏质量。 |
| [2610.40614](https://arxiv.org/abs/2610.40614) — [L3G-World: Real-Time Infinite World Generation with Latent 3D Gaussian Memory](../../../papers/2026-10/other/2610.40614/tech_analysis.md) | Jinhyeok Choi , JoungBin Lee , Jongmin Lee , Minkyeong Jeon , Jiyoung Kim , Kaeun Han , Yoonjin Yoon , Seungryong Kim | 2026-10-30T01:54:42+08:00 | other | L3G-World按场景新增信息更新高斯记忆并直接渲染VAE特征，显著降低持久状态和重复编码成本。 |
| [2610.40611](https://arxiv.org/abs/2610.40611) — [When to Assist and What to Suggest: Joint Gating and Memory-Grounded Hint Generation in One Compact Decoder](../../../papers/2026-10/other/2610.40611/tech_analysis.md) | A. J. A. Jubayer Talukder , Mohammad Ariful Haque | 2026-10-30T01:54:07+08:00 | other | 单个1B模型共享提示门控与生成，在指定评估流程下比1B双模型流水线快1.31–1.76倍。 |
| [2610.40576](https://arxiv.org/abs/2610.40576) — [PIVOT: Progressive Intervention via Online Teacher Correction](../../../papers/2026-10/knowledge_distillation/2610.40576/tech_analysis.md) | Zhihao Yang , Boyuan Zheng , Puhui Tan , Yukun Chen , Kuan Zhang , Longze Chen , Jiaming Li , Renke Shan , Lu Wang , Xianpei Han | 2026-10-30T01:45:07+08:00 | knowledge_distillation | PIVOT把教师纠正片段与token监督结合，将1.7B学生逻辑游戏平均avg@8由最佳基线19.5%提升至35.6%。 |
| [2610.40454](https://arxiv.org/abs/2610.40454) — [Glance: The Generator Is Its Own Reranker](../../../papers/2026-10/other/2610.40454/tech_analysis.md) | Adilet Metinov , Chingiz Arziev | 2026-10-30T01:01:22+08:00 | other | Glance用同一9B骨干完成RAG重排与回答，额外决策技能约0.1GiB，但缓存和端到端时延仍需单独核算。 |
| [2610.40345](https://arxiv.org/abs/2610.40345) — [A Unified Hessian-Guided Framework for Post-Training Quantization](../../../papers/2026-10/quantization/2610.40345/tech_analysis.md) | Mads Toftrup , Marco Federici , Boris van Breugel , Paul Whatmough , Markus Nagel | 2026-10-30T00:06:01+08:00 | quantization | H_Z-PTQ统一变换、舍入与裁剪的输出敏感度目标，Qwen3-8B W4A4KV4的WikiText PPL为10.43，FP为9.73。 |

## 四维评分（1–10）与依据

评分为本次阅读的主观比较，不是统一基准。精度看任务质量与证据强度，压缩看明确资源节省，创新看方法贡献，可复现性看配置/代码/本机验证及算力门槛；不同资源的倍率不直接相互比较。

| ID | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 依据与边界 |
|---|---:|---:|---:|---:|---|
| 2610.40647 | 8 | 7 | 8 | 6 | §4、表1–3：ImageNet训练120 epochs、有效batch512，主结果5个独立种子；以50段Heun采样，在H800 BF16上统计全网络FLOPs。ImageNet-512的SpecSlot-K4为135.64 GFLOPs、FID9.14、12.69 img/s；JiT-B/16为219.56、8.45、7.93，因此FLOPs少38.2%，FID差0.69，吞吐约1.60倍。算力匹配JiT-CM为141.21 GFLOPs、FID11.98，SpecSlot改善FID2.84。文生图DPG由61.15至62.21，但GenEval26.99低于JiT-B/8的29.78，不能声称各项质量全面领先。 ImageNet-512前向FLOPs少38.2%，对应约1.62倍计算比；非权重文件压缩。 创新依据：将总槽数写成 N=W×K：W个空间anchor，每个anchor扩展K个槽；槽拥有互不重叠的DCT径向频段。每个系数恰好预测一次，所有槽在每个流时间均计算，并非动态丢弃高频槽。 可复现性依据：主对照经过统一重训，结论依赖120-epoch预算与各模型各自扫描的CFG。ImageNet-256相对算力匹配模型的FID差异落在五种子区间内；不能把全局二次项缩小比例当作端到端速度或文件压缩率。未来应测试更大分辨率、其他生成骨干，以及相同墙钟训练预算下的收益。 |
| 2610.40637 | 7 | 8 | 8 | 5 | 官方HTML §3：Pendulum、Reacher、CartPole各收集200K个64×64随机策略RGB帧。视觉编码器2层、宽64、4头，动力学MLP为3层128单元。主模型263K参数，其中编码器221K、动力学42K；Adam学习率1e-3、余弦衰减、20K迭代。A100上一阶模型训练2–6分钟、20步约10分钟、40步约30分钟，闭环控制含模拟渲染约20–50ms/步。摘要另报告71个吸引子、参数比DreamerV3等少至少一个数量级；当前HTML表1数值及部分交叉引用不完整，本精读不补造逐环境奖励与71个系统的明细。 论文摘要为至少10倍参数差异；主控制模型263K，非相同检查点压缩率。 创新依据：用H=3个观测恢复部分可观测状态，编码到32维潜变量；MLP预测状态变化率，主实验通过显式Euler步推进。 可复现性依据：离线随机策略训练的world2vec与在线训练的DreamerV3、TD-MPC2并非完全相同数据协议；Reacher还存在控制频率和目标构造差异。263K属于新架构，不是将某个固定大模型压缩到263K。未来需要更复杂视觉环境和统一数据、频率及规划预算的对照；全文HTML缺失的表格值应以后续完整版本补核。 |
| 2610.40618 | 8 | 7 | 9 | 5 | 官方v1 PDF第9–11页、图3/4和表1/2：同一数据集与扩散家族共享教师检查点，学生从对应教师初始化；所有方法batch128，OWT100 GPU-hours、TinyGSM50 GPU-hours。δ扫描1/8、1/16、1/32、1/64，TinyGSM比较使用相同1024题。UDM ERC在2和4 NFE时约为最强竞争基线的两倍准确率，在32 NFE接近教师；MDM仅约匹配第二强基线。8 NFE的U-NetFlux相对ERF Uniform在TinyGSM为0.130对0.368秒/序列，在OWT为0.323对0.647，分别2.83/2.00倍，这两项是采样器对比，不是蒸馏压缩倍率。 通过一致性蒸馏减少采样NFE；未提供通用权重压缩倍率。 创新依据：每个token位置和候选状态附加非负指数残差。其ODE由前后向跳转率决定，残差到零触发状态变化；不在每次跳转后重新采样所有时钟，并证明边缘分布保持。 可复现性依据：收益主要集中在uniform diffusion，不能推及所有离散扩散。温度、采样器和NFE共同影响质量，必须匹配比较；学生初始化自教师，并无参数量缩小的必然结论。本机未训练离散扩散模型。未来应在更大模型和更长上下文上同时衡量额外残差内存、NFE和墙钟速度。 |
| 2610.40614 | 8 | 9 | 8 | 5 | §4、表2：DA3几何骨干、Cosmos-Predict2.5生成器，DL3DV/RealEstate10K训练，4张A100；评估效率在单张A100上。DL3DV中L3G-World为33K基元、11.88MiB，NeoVerse为8766K、501.57MiB，约266倍基元差和42倍记忆差；FID40.57对152.25。RealEstate10K对应25K、8.91MiB对10437K、597.21MiB。VAE条件渲染相对NeoVerse约349–359倍；这些是记忆组件指标。摘要9FPS属于包括少步生成器的实时系统，不能仅归因于记忆设计。 相对NeoVerse的记忆字节约42–67倍减少；不代表总模型显存同倍率下降。 创新依据：依据已有记忆渲染的不透明度与RGB误差标出缺失区域，只在这些位置从DA3特征经K-means初始化新高斯查询；可见旧高斯由另一条refinement流更新。 可复现性依据：压缩比高度依赖对照：相对点云Lyra2.0与高斯NeoVerse的分母不同，基元数量也不等于字节数。Fast变体在部分一致性与FID指标退化，RealEstate10K的相机误差并非最好。未来应测试动态物体、超大场景和持续误差积累，同时报告总GPU常驻内存而非仅记忆数据。 |
| 2610.40611 | 7 | 6 | 7 | 5 | §7–8表4/5：共28058个决策点。最终checkpoint为53772步，统一k=6/k=10的E2E EM为0.2929/0.2908、墙钟0.748/1.005小时；1B门控+1B生成为0.2619、1.318小时，故约1.76/1.31倍。k=10在21703步三种子门控F1为0.8022±0.0029，约匹配双模型0.8002；不能把最终单种子优势当多种子验证。人工评估1144个评分，统一模型约与匹配1B系统持平、低于8B系统。 共享常驻骨干；匹配1B流水线墙钟比1.31–1.76，非同精度权重压缩。 创新依据：统一模型共享一个解码trunk和一个LoRA适配器，在中间层读取门控决定，再按需继续生成。 可复现性依据：主语料的对话和触发标签为模型生成，人工评分主要来自一位评估者。统一与双模型训练预算不同，双模型prefix caching后成本没有实测，消费设备和ASR误差也未测。未来需自然对话、多评估者、相同训练预算和缓存协议下重测。 |
| 2610.40576 | 8 | 6 | 8 | 6 | §4.1/4.5表2：逻辑游戏学生Qwen3-1.7B、教师Qwen3-4B-Thinking，响应上限8192、教师片段4096。数学学生Qwen3-4B与教师同参数级别，上限16384/8192。逻辑三任务Survo、Minesweeper、Kakurasu：reverse-KL PIVOT为72.90/25.44/8.38，最佳基线KDRL为41.68/13.88/2.93，均值19.5→35.6。数学Math-ID为23.05对POPE22.09；AIME等任务forward KL更优，不能认为reverse KL总是更好。 逻辑设置教师/学生参数比4/1.7≈2.35；数学设置约1，不能混算。 创新依据：构造学生前缀u、教师纠正v、学生续写w的混合轨迹。教师实际走出恢复路径，随后学生在该路径上继续探索。 可复现性依据：直接参数压缩只适用于4B→1.7B逻辑设置，数学4B→4B是能力迁移而非参数缩小。教师介入增加训练成本，蒸馏收益不等于免费获得大模型能力。未来应统一教师token预算，评估更小学生、不同领域及错误恢复是否保持泛化。 |
| 2610.40454 | 7 | 5 | 7 | 6 | §3.6/4/5：4000条MS MARCO训练查询、500步、batch8、学习率LoRA5e-5/head1e-4，B200训练39分钟、峰值21GiB。SciFact/NFCorpus nDCG@10为0.741/0.345，对独立bge-reranker-v2-m3为0.721/0.326。300道HotpotQA上F1提高0.045，配对bootstrap95%CI为[0.014,0.076]。Activated单独100题实验续用缓存F1为0.750，重新prefill为0.754；答案延迟138对181ms。这与主实验训练、GPU、样本数均不同。 移除独立重排骨干的常驻开销；每技能约0.1GiB，无通用总内存压缩率。 创新依据：冻结9B混合注意力骨干，仅训练rank16 LoRA与256维pointer head；probe在决策位置与选项结束位置的隐藏状态间打分，不生成自然语言判断。 可复现性依据：仅两个BEIR数据集、一个QA数据集及一个骨干族，独立cross-encoder单查询仍更快。内存随候选数与上下文长度增长，无法保证合并模型就减少总显存。部分GPU被共享，跨实验延迟不可直接相除。未来应测多查询批处理、长上下文总缓存、不同骨干和显著性。 |
| 2610.40345 | 8 | 7 | 9 | 6 | §4表2/3与附录B：2048条×2048 tokens的DCLM-Edu校准，WikiText上下文2048，CSR为6个常识任务平均归一化准确率，3个校准种子。Qwen3-8B W4A4KV4：FP PPL9.73/CSR67.46；H_Z-PTQ10.43±0.03/65.56±0.46；FlatQuant+GPTQ10.60±0.03/65.26±0.11。g32权重单独量化为9.84±0.01/67.42±0.25，W4A4-g32为9.99±0.01/66.77±0.38。表4去掉梯度对齐变换后Qwen PPL变25.19，但更换Hessian近似并非每个指标都更差，因此不把消融写成无例外定律。 4bit载荷相对16bit理论4倍；实际格式与变换有额外开销，本机未生成压缩检查点。 创新依据：由模型输出分布采样标签，反向计算层输出梯度Gz；用(GzGzᵀ)⊗(GzᵀGz)/||Gz||²近似输出Fisher。估计输出特征曲率、权重输入曲率和token梯度能量，避免构造完整s×o维Hessian。 可复现性依据：Kronecker、分离误差和舍入噪声假设都是近似，校准需要反向传播。小数据曲率可能奇异；本文本机实验明确加1%阻尼。理论16→4bit的4倍只计数值载荷，scale、变换和未量化层会降低实际压缩比。未来应比较校准成本、分布偏移、融合低比特内核及整模型端到端误差。 |

## 边界排除与复现

复核quantization、quantize、low-bit、compress、pruning、sparsity、distill、teacher/student、KV cache、mixed precision、GPTQ、AWQ及低秩、共享、紧凑、少步同义表达。89篇未纳入，主要是应用/数据/评估/训练研究。特别排除：40563的4bit仅应用配置；40574同尺寸自蒸馏无压缩目标；40495多任务知识融合；40432未提供学生缩小证据；40577固定专家预算；40350为agent文本上下文管理。完整97条判定、原始摘要、来源与关键词复核保存在本轮审计目录。

新增量化论文仅2610.40345，代码位于 `scripts/quantization/2610.40345/`。真实Qwen3-0.6B首层128×64矩阵、完整模型采样标签梯度、两条64-token校准及两条留出；通道与g32两种配置均有变换等价性、两侧LDL重构和有限值检查。数值结果及命令见README/results.json。没有复现整模型W4A4KV4/KV、2048×2048 DCLM-Edu、标准PPL或CUDA性能；这是CPU数值组件验证。非量化论文未训练。

## 独立快照与验证

严格从最新origin/main创建linked worktree；移除main自带2026-07-28旧日报。papers仅8篇新增精读和说明；reports仅本日报和说明；scripts仅说明与本次1篇量化复现；metadata仅2026-10新增8条索引与CSV。尽管日报在2026-11，论文实际提交月份均为2026-10，未在11月写重复索引。

提交前执行目录/metadata/CSV/量化复现集合一致、历史ID零交集、六节结构、git diff --check和相对main单提交校验；推送后以ls-remote、merge-base及git log复核。精确SHA与最终机器验证结果在任务最终汇报及本轮validation.json，避免在提交中写自引用SHA。原工作树6项未提交改动通过前后文件哈希保护。

本轮审计证据：`/Users/lipengcheng/.codex/automations/arxiv/runs/2026-11-02/`。未完成项为上述整模型/硬件复现及world2vec HTML缺失表值，没有以臆测填补。
