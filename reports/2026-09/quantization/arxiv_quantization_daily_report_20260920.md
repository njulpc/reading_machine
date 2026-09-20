# arXiv 模型压缩日报：2026-09-20

运行日2026-09-21，Asia/Shanghai；检索 **2026-09-18 00:00:00—2026-09-20 23:59:59** 三个完整自然日。运行记录时间：2026-09-21T01:18:57.665225+08:00。按官方 `/abs/` Submission history 的v1 UTC转换北京时间归档；公告日期不替代提交日期。未调用arXiv API。

## 1. 结果与日期边界

|实际提交日（北京时间）|公开可见全主题条目|模型压缩相关|历史已分析重复|本次新增|
|---|---:|---:|---:|---:|
|2026-09-18|58|7|0|7|
|2026-09-19|0|0|0|0|
|2026-09-20|0|0|0|0|
|三天合计|58|7|0|7|

9月19、20日均为“**截至运行时 arXiv 官方网页未检出**”，不代表后台最终投稿为零。列表最新公告为9月18日，后续运行仍须按三天窗口回查公告延迟。7篇均v1 UTC9月17日16:00后，属于北京时间9月18日，不能误排除。

## 2. 完整新增论文表

|ID / 论文|v1 UTC → 北京时间|方向|一句话结论|
|---|---|---|---|
|[2609.20623 PhGS: Post-Hoc Pruning and Refinement of Single-View Feed-Forward 3D Gaussian Reconstructions](https://arxiv.org/abs/2609.20623)|2026-09-17T16:07:03Z → 2026-09-18 00:07:03|pruning|PhGS 以边缘/不透明度采样剪枝并循环修复，Flash3D 高斯存储减半时 PSNR 仅下降 0.06 dB，但完整重建吞吐下降。|
|[2609.20734 On-Demand Attention: Language Models Know When to Recall](https://arxiv.org/abs/2609.20734)|2026-09-17T17:24:48Z → 2026-09-18 01:24:48|pruning|ODA 用局部前向后的状态预测是否需要全局 attention，RULER16K 接近原精度；1.98倍加速来自独立受控长上下文配置。|
|[2609.20744 Video DeltaNet: A Video-Native Hybrid Attention for Livestream Video Generation](https://arxiv.org/abs/2609.20744)|2026-09-17T17:33:15Z → 2026-09-18 01:33:15|knowledge_distillation|Video DeltaNet 结合局部注意力、逐帧线性记忆和8步蒸馏，在8张B200上完成6.70秒去噪；倍率必须区分GPU数与NFE。|
|[2609.20756 OPTED: On-Policy Fine-Tuning for End-to-End Driving using a Render-Free Teacher](https://arxiv.org/abs/2609.20756)|2026-09-17T17:41:51Z → 2026-09-18 01:41:51|knowledge_distillation|OPTED 用特权RL教师标注视觉学生实际访问的状态，显著节省渲染交互；教师比学生小，不能称为参数压缩。|
|[2609.20784 RetireOPD: Self-Retiring On-Policy Distillation for Agentic Reinforcement Learning](https://arxiv.org/abs/2609.20784)|2026-09-17T17:52:08Z → 2026-09-18 01:52:08|knowledge_distillation|RetireOPD 在学生接近教师且对齐停滞时退出蒸馏，3B ALFWorld从GRPO的75.0%升至93.8%，但师生等规模。|
|[2609.20807 Score Centering Stabilizes Off-policy Reinforcement Learning](https://arxiv.org/abs/2609.20807)|2026-09-17T17:58:17Z → 2026-09-18 01:58:17|quantization|Score Centering 抵消量化采样器导致的梯度漂移；重度W8A8/KV4的30B实验训练准确率30%，高于TIS的12%。|
|[2609.20820 Workspace Models: Lightweight Robotic Memory via Saliency-Driven Supervision](https://arxiv.org/abs/2609.20820)|2026-09-17T17:59:53Z → 2026-09-18 01:59:53|knowledge_distillation|Workspace Models 将训练期VLM显著性监督蒸馏成记忆编码器，平均成功率91.5%对66.8%，优化后规划延迟49.2ms。|

## 3. 评分（1–10，越高越好）

精度分评质量保持与证据强度；压缩分只评论文直接支持的资源收益，区分权重、表示、计算和训练开销；创新分评方法贡献；可复现分评公开细节、代码与本机验证。不同资源口径不能直接排序为参数压缩率。详细依据在每篇精读第6节。

|ID|精度效果|压缩收益|创新性|可复现性|主要评分依据|
|---|---:|---:|---:|---:|---|
|2609.20623|8|7|7|7|精度8（同域小损失但KITTI降0.80dB）；压缩7（明确2倍表示存储）；创新7（跨骨干后处理与预算混合）；可复现7（训练设置充分，未本机验证）。|
|2609.20734|8|5|8|5|精度8（多骨干保持较好）；压缩5（仅动态计算减少，容量不降）；创新8（冻结模型状态读出收益）；可复现5（细节较全但完整实现与成本记录不齐）。|
|2609.20744|8|7|8|6|精度8（多指标接近但端点退化）；压缩7（6.25倍NFE减少，无权重倍率）；创新8（视频原生帧级更新）；可复现6（公开实现线索和训练配方，但算力门槛高）。|
|2609.20756|7|3|7|6|精度7（闭环改善但若干指标退化）；压缩3（无参数节省，只省监督交互）；创新7（跨模拟器与动作接口）；可复现6（协议详细但部署复杂）。|
|2609.20784|8|3|7|7|精度8（跨六种模型任务组合提升）；压缩3（等规模、无存储倍率）；创新7（训练信号驱动退出）；可复现7（公开代码线索与阈值、消融较全）。|
|2609.20807|8|5|8|8|精度8（重TIM改善且有多规模证据）；压缩5（采样器W8/KV低位，训练器仍高精度，无整机倍率）；创新8（漂移分解与可组合加性校正）；可复现8（官方代码加本机数值/真实模型验证，非完整基准）。|
|2609.20820|8|6|7|6|精度8（四任务提升但样本小）；压缩6（约4.05倍优化后时延比，无参数倍率）；创新7（集合重建显著性记忆）；可复现6（机制与设置明确，硬件数据链复杂）。|

## 4. 历史去重审计

fetch成功后逐一 `git ls-tree -r --name-only` 全部42个远端日更分支，从真实 `papers/**/<id>/tech_analysis.md` 得到534个规范化ID，去除版本后缀；逐分支 `git show` 元数据交叉核对得到537个ID。仅有metadata的2607.27951、2607.28410、2607.28457不计已完成。当前9月21分支此前不存在，从最新origin/main创建，未作为历史分支误计。

跨日期/分类去重：十列表共4680次条目出现（含new/recent重复及cross-list），规范化后3016个ID；详情日期过滤后58篇，逐篇标题+摘要语义审阅后7篇相关。关键词仅作复核排序，不作召回门槛。窗口相关历史重复ID及来源分支：**无（空集合）**；最终7个新增ID与534个历史已分析ID交集为空。

扫描分支及树中真实精读数如下；完整SHA、元数据数和实际扫描证据保存在索引与本机审计目录。

|历史分支|真实精读ID数|metadata ID数|
|---|---:|---:|
|origin/feature/arxiv-daily-2026-07-29|20|20|
|origin/feature/arxiv-daily-2026-07-30|8|8|
|origin/feature/arxiv-daily-2026-07-31|7|5|
|origin/feature/arxiv-daily-2026-08-01|29|32|
|origin/feature/arxiv-daily-2026-08-02|4|4|
|origin/feature/arxiv-daily-2026-08-03|12|8|
|origin/feature/arxiv-daily-2026-08-04|12|12|
|origin/feature/arxiv-daily-2026-08-05|12|12|
|origin/feature/arxiv-daily-2026-08-06|30|30|
|origin/feature/arxiv-daily-2026-08-07|50|50|
|origin/feature/arxiv-daily-2026-08-08|60|10|
|origin/feature/arxiv-daily-2026-08-10|9|9|
|origin/feature/arxiv-daily-2026-08-12|12|12|
|origin/feature/arxiv-daily-2026-08-14|10|10|
|origin/feature/arxiv-daily-2026-08-15|0|0|
|origin/feature/arxiv-daily-2026-08-16|0|0|
|origin/feature/arxiv-daily-2026-08-17|0|0|
|origin/feature/arxiv-daily-2026-08-18|0|0|
|origin/feature/arxiv-daily-2026-08-19|22|22|
|origin/feature/arxiv-daily-2026-08-20|9|9|
|origin/feature/arxiv-daily-2026-08-21|12|12|
|origin/feature/arxiv-daily-2026-08-22|14|14|
|origin/feature/arxiv-daily-2026-08-23|0|0|
|origin/feature/arxiv-daily-2026-08-24|0|0|
|origin/feature/arxiv-daily-2026-08-25|0|0|
|origin/feature/arxiv-daily-2026-08-26|19|19|
|origin/feature/arxiv-daily-2026-08-27|27|27|
|origin/feature/arxiv-daily-2026-08-28|30|30|
|origin/feature/arxiv-daily-2026-08-29|38|38|
|origin/feature/arxiv-daily-2026-08-30|0|0|
|origin/feature/arxiv-daily-2026-08-31|0|0|
|origin/feature/arxiv-daily-2026-09-01|0|0|
|origin/feature/arxiv-daily-2026-09-02|60|60|
|origin/feature/arxiv-daily-2026-09-03|56|56|
|origin/feature/arxiv-daily-2026-09-04|31|31|
|origin/feature/arxiv-daily-2026-09-05|37|37|
|origin/feature/arxiv-daily-2026-09-06|1|1|
|origin/feature/arxiv-daily-2026-09-07|0|0|
|origin/feature/arxiv-daily-2026-09-08|5|5|
|origin/feature/arxiv-daily-2026-09-09|0|0|
|origin/feature/arxiv-daily-2026-09-14|3|3|
|origin/feature/arxiv-daily-2026-09-15|4|4|

## 5. 官方分类页覆盖证据

全部入口均本次重新下载 `show=2000, skip=0`，没有超过2000的列表；页面声明总数、实际dt记录数、每个日期/投稿分组的显示数和实际数逐一相等。new完整包含新投稿、交叉投稿、替换稿；recent覆盖9月14/15/16/17/18五个公告日。不存在默认首屏截断。官方页面未公开后续日期条目，因此此时不能推出未来公告的零结果。

|分类|列表链接|声明=实际|日期/分组完整范围|
|---|---|---:|---|
|cs.LG|[new](https://arxiv.org/list/cs.LG/new?show=2000)|304|Showing new listings for Friday, 18 September 2026；New submissions (showing 107 of 107 entries)；Cross submissions (showing 91 of 91 entries)；Replacement submissions (showing 106 of 106 entries)|
|cs.LG|[recent](https://arxiv.org/list/cs.LG/recent?show=2000)|1127|Fri, 18 Sep 2026 (showing 198 of 198 entries )；Thu, 17 Sep 2026 (showing 219 of 219 entries )；Wed, 16 Sep 2026 (showing 186 of 186 entries )；Tue, 15 Sep 2026 (showing 366 of 366 entries )；Mon, 14 Sep 2026 (showing 158 of 158 entries )|
|cs.CL|[new](https://arxiv.org/list/cs.CL/new?show=2000)|164|Showing new listings for Friday, 18 September 2026；New submissions (showing 72 of 72 entries)；Cross submissions (showing 32 of 32 entries)；Replacement submissions (showing 60 of 60 entries)|
|cs.CL|[recent](https://arxiv.org/list/cs.CL/recent?show=2000)|608|Fri, 18 Sep 2026 (showing 104 of 104 entries )；Thu, 17 Sep 2026 (showing 127 of 127 entries )；Wed, 16 Sep 2026 (showing 109 of 109 entries )；Tue, 15 Sep 2026 (showing 204 of 204 entries )；Mon, 14 Sep 2026 (showing 64 of 64 entries )|
|cs.CV|[new](https://arxiv.org/list/cs.CV/new?show=2000)|177|Showing new listings for Friday, 18 September 2026；New submissions (showing 101 of 101 entries)；Cross submissions (showing 24 of 24 entries)；Replacement submissions (showing 52 of 52 entries)|
|cs.CV|[recent](https://arxiv.org/list/cs.CV/recent?show=2000)|689|Fri, 18 Sep 2026 (showing 125 of 125 entries )；Thu, 17 Sep 2026 (showing 118 of 118 entries )；Wed, 16 Sep 2026 (showing 123 of 123 entries )；Tue, 15 Sep 2026 (showing 233 of 233 entries )；Mon, 14 Sep 2026 (showing 90 of 90 entries )|
|cs.AI|[new](https://arxiv.org/list/cs.AI/new?show=2000)|329|Showing new listings for Friday, 18 September 2026；New submissions (showing 89 of 89 entries)；Cross submissions (showing 126 of 126 entries)；Replacement submissions (showing 114 of 114 entries)|
|cs.AI|[recent](https://arxiv.org/list/cs.AI/recent?show=2000)|1189|Fri, 18 Sep 2026 (showing 215 of 215 entries )；Thu, 17 Sep 2026 (showing 204 of 204 entries )；Wed, 16 Sep 2026 (showing 195 of 195 entries )；Tue, 15 Sep 2026 (showing 408 of 408 entries )；Mon, 14 Sep 2026 (showing 167 of 167 entries )|
|cs.AR|[new](https://arxiv.org/list/cs.AR/new?show=2000)|20|Showing new listings for Friday, 18 September 2026；New submissions (showing 9 of 9 entries)；Cross submissions (showing 4 of 4 entries)；Replacement submissions (showing 7 of 7 entries)|
|cs.AR|[recent](https://arxiv.org/list/cs.AR/recent?show=2000)|73|Fri, 18 Sep 2026 (showing 13 of 13 entries )；Thu, 17 Sep 2026 (showing 16 of 16 entries )；Wed, 16 Sep 2026 (showing 15 of 15 entries )；Tue, 15 Sep 2026 (showing 24 of 24 entries )；Mon, 14 Sep 2026 (showing 5 of 5 entries )|

3016个官方abs全部本次重新下载，标题、摘要、主分类/交叉分类及v1解析均成功，抓取/解析失败均0。程序获取全部标题摘要，人工式逐篇语义判断覆盖窗口内58条；窗口外按真实v1排除，不声称对全部3016篇进行独立精读。已复核 quantization/quantize/low-bit/model compression/compress/pruning/sparsity/knowledge distillation/distill/teacher/student/KV cache/mixed precision/GPTQ/AWQ 及稀疏、低秩等同义词。

阳性对照：窗口外9月17日本地日期有400条；[2609.20614](https://arxiv.org/abs/2609.20614) v1 15:59:45Z=本地23:59:45，[2609.20623](https://arxiv.org/abs/2609.20623) v1 16:07:03Z=次日00:07:03，验证跨午夜归属。

10篇候选/边界论文已读官方HTML；RISC-V综述2609.20677的HTML404，仅用完整官方摘要判断非本流水线核心主题，未据此虚构全文结果。所有入选7篇官方HTML均可读。详情页无未解决读取失败。

## 6. 本次复现与独立快照

量化主题2609.20807：`scripts/quantization/2609.20807/README.md`、`demo.py`、`results.json`。真实Qwen3-0.6B，197个线性模块、596049920参数、4条×8token INT8采样、逐头KV8误差、top128 SC、全参数反传及SGD一步。梯度范数2.703324，末层down_proj实际变化0.00422262；prefill logits相对L2=0.227216、argmax一致率0.80。四种梯度等价小张量最大误差6.60e-17、恒定奖励中心化/量化误差界验证通过。

运行边界：CPU FP32反量化矩阵乘与FP32训练器，非原论文JAX低精度GPU内核；KV未打包；使用toy数字密度奖励，不是Countdown；没有长期、多种子、30B或原生加速结果。其他6篇未运行原论文视觉/机器人/蒸馏训练。VDN的MXFP8是部署配套，按其主要混合注意力和少步蒸馏贡献归档，不冒充已复现MXFP8内核。

分支 `feature/arxiv-daily-2026-09-21` 严格从origin/main `abfe8f2767d8bf881d586718ab4db33fc576be6a` 建立于隔离linked worktree。删除main自带的2026-07-28历史日报；最终papers只含7篇新精读、reports只含本日报、scripts只含说明及1个本次量化复现目录、metadata只含2026-09本次7条JSON/CSV及说明。原工作树6处未提交改动不带入；提交前后以status和逐文件SHA256核验。

## 7. 窗口内排除审计

以下51篇已逐篇检查完整题名和摘要；边界条目补读全文，排除不依赖“未命中关键词”。

|ID|标题|排除依据|
|---|---|---|
|[2609.20615](https://arxiv.org/abs/2609.20615)|INSPECT: Learning Robot View Selection from Assistant Use|机器人视角选择，不压缩模型|
|[2609.20620](https://arxiv.org/abs/2609.20620)|A Simulation Platform for AUV Fault Recovery: Exploring LLM-Based Diagnostic Strategies|AUV诊断模拟与既有模型比较，非压缩|
|[2609.20625](https://arxiv.org/abs/2609.20625)|Chronicle: Cut-Point Replay for Regression Testing of LLM Agents|agent记录重放测试|
|[2609.20630](https://arxiv.org/abs/2609.20630)|UniPolicy: Unified Objective-Specific Policies for Generative Search Advertising|广告多目标策略对齐，稀疏MoE路由不构成压缩实验|
|[2609.20633](https://arxiv.org/abs/2609.20633)|Refinement Is Inherently Editable: Training-Free Prompt-to-Prompt Image Editing with Generative Refinement Network|二进制图像码用于编辑，非低比特权重|
|[2609.20634](https://arxiv.org/abs/2609.20634)|PAA: The Probabilistic Allen Algebra: A Generative and Complete Probabilistic Extension of Allen's Interval Relations|概率区间关系代数|
|[2609.20638](https://arxiv.org/abs/2609.20638)|PROVIA: Procedure State Tracking for Online Mistake Detection in Egocentric Videos|过程状态检测|
|[2609.20641](https://arxiv.org/abs/2609.20641)|Beyond PINNs: A Unified Gauss--Newton and Petrov--Galerkin Framework for Neural and Hybrid PDE Solvers|PDE数值求解框架|
|[2609.20649](https://arxiv.org/abs/2609.20649)|DexTouch-WM: Learning Action-Conditioned Tactile World Models from Human Touch for Dexterous Robot Manipulation|人类触觉世界模型数据迁移，非教师压缩|
|[2609.20650](https://arxiv.org/abs/2609.20650)|Multi-center Medical Data Mining with FL-Net - A One-stop Shop for Federated Learning|联邦临床数据框架|
|[2609.20658](https://arxiv.org/abs/2609.20658)|Ownership in AI-Assisted Everyday Tasks|AI作品归属问卷|
|[2609.20659](https://arxiv.org/abs/2609.20659)|HIL-UMI: Bringing Human-in-the-Loop Post-Training of Vision-Language-Action Models to Universal Manipulation Interface|人工反馈VLA后训练|
|[2609.20662](https://arxiv.org/abs/2609.20662)|Earth Surface Immune System for Rapid Monitoring of Unknown Anomalies|遥感异常检测与prompt选择|
|[2609.20669](https://arxiv.org/abs/2609.20669)|Learning Foresight without Explicit Trajectories for 3D Diffusion Policies|新策略增加3.52%参数，非压缩|
|[2609.20673](https://arxiv.org/abs/2609.20673)|FunArt: Decoding Functional Structure and Articulation from Generative 3D Latents|使用既有稀疏VAE表征，研究重点是3D结构预测|
|[2609.20676](https://arxiv.org/abs/2609.20676)|Epidemiological Causal Graph Identification: Challenges, Identifiability and Algorithms|因果方向可辨识性|
|[2609.20677](https://arxiv.org/abs/2609.20677)|RISC-V and machine learning: a survey|通用RISC-V/ML生态综述，摘要未给新模型压缩方法或对照；HTML404，仅依摘要判断主题|
|[2609.20680](https://arxiv.org/abs/2609.20680)|Towards Scaling Marine Perception with Synthetic Data|水下合成训练数据|
|[2609.20684](https://arxiv.org/abs/2609.20684)|HerHealthEval: Evaluating Multilingual and Register-Sensitive Understanding of Women's Health Communication|QLoRA作医疗任务适配工具，核心是标签偏差，未研究量化压缩权衡|
|[2609.20687](https://arxiv.org/abs/2609.20687)|The First-Order Oracle Complexity of Lipschitz Convex Optimization in Nondual Settings|凸优化oracle理论|
|[2609.20693](https://arxiv.org/abs/2609.20693)|TetrisCNN for interpretable detection of phases of matter from experimental quantum simulator data|稀疏可解释物理特征，非模型参数剪枝|
|[2609.20700](https://arxiv.org/abs/2609.20700)|Should This Case Be Adapted? Prediction Fragmentation Controls Test-Time Adaptation|测试时适配路由，控制适配伤害而非压缩|
|[2609.20701](https://arxiv.org/abs/2609.20701)|Stable Movement for Nondual Lipschitz Convex Optimization: Efficiency and Nearly Optimal Oracle Rates|凸优化算法|
|[2609.20712](https://arxiv.org/abs/2609.20712)|Summarization Bias: The Directional Collapse of Objective Projection into Told-Mode Labels in Large Language Models --- A Conceptual Framework and Registered Test Protocol|叙事摘要偏差框架|
|[2609.20715](https://arxiv.org/abs/2609.20715)|Don't Mask the Environment: Observation Supervision Changes How Agents Explore Under RL|环境观察token监督增强RL|
|[2609.20722](https://arxiv.org/abs/2609.20722)|Deep Noir: Autonomous Steering Discovery via Architectural Chronometry in Transformer Models|激活steering及安全，不减少网络|
|[2609.20732](https://arxiv.org/abs/2609.20732)|Q&A on Any Spreadsheet Requires Interpreting Its Grid Structure|表格RAG表示|
|[2609.20747](https://arxiv.org/abs/2609.20747)|MILER: Semantic Mid-Level Representation for Sim-to-Real Reinforcement Learning in Unstructured Autonomous Driving|自动驾驶sim-to-real强化学习|
|[2609.20751](https://arxiv.org/abs/2609.20751)|dQwen3.5: Hybrid-Attention Diffusion Language Models|既有混合AR架构改为DLM；并行解码是生成形式转换，未做模型压缩|
|[2609.20752](https://arxiv.org/abs/2609.20752)|Large Language Models as Falsifiers for Cyber-Physical Systems|CPS规格证伪|
|[2609.20754](https://arxiv.org/abs/2609.20754)|RAFT: A Stateful Retrieval-Augmented Framework for Troubleshooting Agents|客服RAG检索|
|[2609.20758](https://arxiv.org/abs/2609.20758)|Prediction-Powered Smoothing and Validation for Disaggregated AI Evaluation|评估统计估计|
|[2609.20761](https://arxiv.org/abs/2609.20761)|Agile-WAM: An Agile Tactile World Action Model for Contact-Rich Robot Control|从头训练小型WAM，未压缩或蒸馏既有模型（全文确认）|
|[2609.20765](https://arxiv.org/abs/2609.20765)|Calibrated RF-Fingerprinting Under Interference With Heterogeneous Transmission Protocols|无线信号分类校准|
|[2609.20768](https://arxiv.org/abs/2609.20768)|Semantic Action Graph: A Shared Representation for Agent Grounding and Human Interpretation of Sports Highlights|体育视频语义图|
|[2609.20769](https://arxiv.org/abs/2609.20769)|FlowSGS: Improving Flow Matching Priors for Inverse Imaging with Stochastic Interpolants|后验采样器求解改进，无模型压缩或蒸馏|
|[2609.20776](https://arxiv.org/abs/2609.20776)|GeoAAC: Geometry-Based Adaptive Action Chunking from Denoising Trajectories in VLA Policies|动作执行horizon调节，不是网络压缩|
|[2609.20779](https://arxiv.org/abs/2609.20779)|Harm Laundering in GPT Models: Evidence That Gender Discrimination Is Transformed Rather Than Reduced Across Safety-Trained Generations|模型安全偏差评估|
|[2609.20794](https://arxiv.org/abs/2609.20794)|PosteriorBench: From Point Estimates to Posterior Matching in Evaluating Generative Inverse Solvers|逆问题后验评估基准|
|[2609.20800](https://arxiv.org/abs/2609.20800)|JEPA-Anything: Learning Predictive Models across Different Worlds|跨领域JEPA预测因子分解，不是压缩已有模型|
|[2609.20804](https://arxiv.org/abs/2609.20804)|An Empirical Study of Harness Design for Coding Agents|编码agent外部上下文摘要/省略，不是模型/KV压缩|
|[2609.20808](https://arxiv.org/abs/2609.20808)|Unifying Models of Intergroup Hostility in Online Discourse|网络群体敌意分析|
|[2609.20812](https://arxiv.org/abs/2609.20812)|Quantifying Overclaiming Propensity in Frontier LLM Agents|agent过度宣称评估|
|[2609.20814](https://arxiv.org/abs/2609.20814)|How Does Distribution Shift Shape Pretraining Gains in Neural PDE Surrogates?|PDE预训练数据效率|
|[2609.20815](https://arxiv.org/abs/2609.20815)|ERCPMP-Gx: Endoscopic Image and Video Dataset for Morphological, Histopathological, and Genomic Characterization of Colorectal Polyposis|内镜数据集|
|[2609.20816](https://arxiv.org/abs/2609.20816)|Paint-Anything: Unified Any-Color Control for Image Generation and Editing|图像颜色可控训练|
|[2609.20817](https://arxiv.org/abs/2609.20817)|FAMOS: Feed-Forward 3D Articulation Modeling from Sparse Observations|3D关节模型预测|
|[2609.20818](https://arxiv.org/abs/2609.20818)|SplashSplat: Reconstructing Splashing Liquids from Real-World Multi-View Videos|液体三维重建，不针对压缩|
|[2609.20819](https://arxiv.org/abs/2609.20819)|Can 4D Foundation Models Remember?|4D模型视觉记忆评估|
|[2609.20821](https://arxiv.org/abs/2609.20821)|Embedding Models Measure in Peculiar Ways|embedding物理量语义评估|
|[2609.20822](https://arxiv.org/abs/2609.20822)|Coding Agents with an Obstacle-Aware Harness for Safe Robot Manipulation|机器人障碍规划harness|
