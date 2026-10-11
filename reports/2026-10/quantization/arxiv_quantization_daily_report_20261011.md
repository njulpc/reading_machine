# arXiv 模型压缩论文日报（主日期 2026-10-11）

运行时间：2026-10-12T01:12:39.642012+08:00。三天窗口：北京时间 **2026-10-09 00:00:00—2026-10-11 23:59:59**。
以官方 `/abs` Submission history 的 v1 UTC 时间转换到北京时间归日，不以公告日或版本更新日代替投稿日。未使用 arXiv API。

## 1. 数量与范围

| 本地提交日期 | 全主题窗口记录 | 相关原始出现次数（跨列表） | 规范ID去重后相关 | 历史已分析重复 | 本次新增 |
|---|---:|---:|---:|---:|---:|
|2026-10-09|110|34|12|0|12|
|2026-10-10|0|0|0|0|0|
|2026-10-11|0|0|0|0|0|
|合计|110|34|12|0|12|

10/10与10/11的结论严格为“**截至运行时 arXiv 官方网页未检出**”；页面仍为10/09公告，不能排除尚未公开/尚未公告稿件。后续三天窗口继续回查。110是全主题数，20是包含边界案例的全文复核候选数，均不能当作相关论文数。

范围覆盖权重/状态压缩、剪枝、紧凑学生知识迁移、生成步骤及推理token压缩。仅出现distill/quantize而用于同规模自改进、数据表示本身或坐标寻址，不自动归为模型低比特量化。DVD、Slot3R、FastBench等边界纳入项的对象与限制均在精读中说明。

## 2. 官方召回覆盖证据

五分类各扫描new与recent，所有入口使用`show=2000&skip=0`；最大页1929项，故无第二页。每页实际dt数与总数相等，每个h3的showing数与该分组实际dt数也逐一一致。new全部覆盖新稿、cross submissions及replacement；recent全部覆盖10/09、10/08、10/07、10/06、10/05五个公告组。

|分类|new总数/实际数|recent总数/实际数|覆盖范围|
|---|---|---|---|
|cs.LG|[472/472](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)|[1929/1929](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|skip0，show2000，全页全分组|
|cs.CL|[230/230](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)|[765/765](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|skip0，show2000，全页全分组|
|cs.CV|[302/302](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)|[970/970](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0)|skip0，show2000，全页全分组|
|cs.AI|[472/472](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)|[1754/1754](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0)|skip0，show2000，全页全分组|
|cs.AR|[14/14](https://arxiv.org/list/cs.AR/new?show=2000&skip=0)|[74/74](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0)|skip0，show2000，全页全分组|

逐分组明细见`metadata/2026-10/retrieval_audit.json`。本轮重新下载10个列表，共6982次出现、4403个规范ID。4403份官方abs原始HTML复用先前缓存并重新解析（无错误），不是本轮4403次网络请求；窗口内全部110份abs本轮重新下载，标题、摘要、v1历史、分类均与缓存一致。先按日期排除窗口外4293条，再完整语义审阅窗口内110条；关键词仅为复核索引，不作为召回门槛。候选全文15份沿用已下载官方v1，5份本轮取得，均在本轮读取相应章节。

相邻阳性对照：[2610.12207](https://arxiv.org/abs/2610.12207) v1本地2026-10-08T23:57:45+08:00（窗口外）；[2610.12211](https://arxiv.org/abs/2610.12211) v1本地2026-10-09T00:00:23+08:00（窗口内）。完整原始HTML、哈希来源和110项语义审阅保存在自动化审计目录。

## 3. 全历史去重审计

fetch --prune origin成功后，逐一对全部45个origin/feature/arxiv-daily-*历史分支执行ls-tree，抽取真实papers/**/<ID>/tech_analysis.md，去掉版本号，得到550个历史完成ID；逐一git show读取metadata索引交叉核验。metadata-only的2607.27951、2607.28410、2607.28457不计为完成。今日分支在fetch时不存在；10/11草稿未提交推送，不能当历史完成记录。

先合并三个日期、五分类、new/recent的规范ID，再排除历史集合。本轮重复ID及来源分支：**空集**；全部110窗口ID与历史550交集也为空。最终新增ID：2610.12214, 2610.12266, 2610.12274, 2610.12282, 2610.12304, 2610.12307, 2610.12327, 2610.12338, 2610.12374, 2610.12427, 2610.12444, 2610.12448。

扫描分支全集（每个分支及SHA详见自动化history.json；索引dedup_source_branches同步列出）：

`origin/feature/arxiv-daily-2026-07-29`, `origin/feature/arxiv-daily-2026-07-30`, `origin/feature/arxiv-daily-2026-07-31`, `origin/feature/arxiv-daily-2026-08-01`, `origin/feature/arxiv-daily-2026-08-02`, `origin/feature/arxiv-daily-2026-08-03`, `origin/feature/arxiv-daily-2026-08-04`, `origin/feature/arxiv-daily-2026-08-05`, `origin/feature/arxiv-daily-2026-08-06`, `origin/feature/arxiv-daily-2026-08-07`, `origin/feature/arxiv-daily-2026-08-08`, `origin/feature/arxiv-daily-2026-08-10`, `origin/feature/arxiv-daily-2026-08-12`, `origin/feature/arxiv-daily-2026-08-14`, `origin/feature/arxiv-daily-2026-08-15`, `origin/feature/arxiv-daily-2026-08-16`, `origin/feature/arxiv-daily-2026-08-17`, `origin/feature/arxiv-daily-2026-08-18`, `origin/feature/arxiv-daily-2026-08-19`, `origin/feature/arxiv-daily-2026-08-20`, `origin/feature/arxiv-daily-2026-08-21`, `origin/feature/arxiv-daily-2026-08-22`, `origin/feature/arxiv-daily-2026-08-23`, `origin/feature/arxiv-daily-2026-08-24`, `origin/feature/arxiv-daily-2026-08-25`, `origin/feature/arxiv-daily-2026-08-26`, `origin/feature/arxiv-daily-2026-08-27`, `origin/feature/arxiv-daily-2026-08-28`, `origin/feature/arxiv-daily-2026-08-29`, `origin/feature/arxiv-daily-2026-08-30`, `origin/feature/arxiv-daily-2026-08-31`, `origin/feature/arxiv-daily-2026-09-01`, `origin/feature/arxiv-daily-2026-09-02`, `origin/feature/arxiv-daily-2026-09-03`, `origin/feature/arxiv-daily-2026-09-04`, `origin/feature/arxiv-daily-2026-09-05`, `origin/feature/arxiv-daily-2026-09-06`, `origin/feature/arxiv-daily-2026-09-07`, `origin/feature/arxiv-daily-2026-09-08`, `origin/feature/arxiv-daily-2026-09-09`, `origin/feature/arxiv-daily-2026-09-14`, `origin/feature/arxiv-daily-2026-09-15`, `origin/feature/arxiv-daily-2026-09-21`, `origin/feature/arxiv-daily-2026-09-22`, `origin/feature/arxiv-daily-2026-09-29`。

## 4. 新增论文完整表

|arXiv ID / 标题|北京时间v1|主/交叉分类|归类|一句话结论|
|---|---|---|---|---|
|[2610.12214 — DiffuPlex: Accelerating Full-Duplex Spoken Dialog Models via Rolling Masked Diffusion](https://arxiv.org/abs/2610.12214)|2026-10-09T00:01:37+08:00|Sound (cs.SD) ; Computation and Language (cs.CL)|knowledge_distillation|DiffuPlex 通过一次预测多帧、只播放可信前缀并随用户输入修订未来，把 backbone 调用摊薄到多个交互帧。|
|[2610.12266 — DVD: Dynamic Vector Decoding for Efficient MLLM-based Perception](https://arxiv.org/abs/2610.12266)|2026-10-09T00:32:28+08:00|Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI)|other|DVD 把2D/3D几何向量编码为少量离散token，以轻量解码器缩短MLLM生成序列。|
|[2610.12274 — HarnessSQL: Harness-Native Training for SQL Agents in Realistic Database Environments](https://arxiv.org/abs/2610.12274)|2026-10-09T00:36:39+08:00|Computation and Language (cs.CL)|knowledge_distillation|HarnessSQL 在部署数据库工具环境中生成并验证教师轨迹，再对学生做全轨迹SFT和执行奖励RL。|
|[2610.12282 — Slot3R: Set-Associative Spatial Memory for Streaming 3D Reconstruction](https://arxiv.org/abs/2610.12282)|2026-10-09T00:39:39+08:00|Computer Vision and Pattern Recognition (cs.CV)|other|Slot3R 将空间地址和特征状态区分，保留多槽状态并限制每帧读出的记忆token数。|
|[2610.12304 — Looking Inside LLMs: Small-World Connectivity as a Signature of Reasoning Performance](https://arxiv.org/abs/2610.12304)|2026-10-09T00:53:45+08:00|Artificial Intelligence (cs.AI)|pruning|SWA 根据小世界社区内连接与跨社区分散程度，分层分配SparseGPT/Wanda的剪枝预算。|
|[2610.12307 — BudgetPix: Compute-Adaptive Tokenization for Pixel-Space Image Diffusion](https://arxiv.org/abs/2610.12307)|2026-10-09T00:54:40+08:00|Computer Vision and Pattern Recognition (cs.CV)|other|BudgetPix 根据图像局部熵选择大小不同的patch，用可变token预算减少扩散主干计算。|
|[2610.12327 — SparseDecoding: Decoding-Aware Pruning for Accurate and Efficient LLM Inference](https://arxiv.org/abs/2610.12327)|2026-10-09T01:06:32+08:00|Machine Learning (cs.LG) ; Computation and Language (cs.CL)|pruning|SparseDecoding 用dense模型自身生成时的激活校准剪枝，并用bitmask稀疏内核把50%稀疏转成解码加速。|
|[2610.12338 — VFold: Symmetry-Aware Cross-Layer Value Cache Compression](https://arxiv.org/abs/2610.12338)|2026-10-09T01:14:28+08:00|Computation and Language (cs.CL) ; Machine Learning (cs.LG)|other|VFold 先把邻层value头对齐并将变换折入权重，再共享平均缓存，在25%总KV节省下保留大部分长上下文能力。|
|[2610.12374 — AgentGarten: Code Worlds for Evolving Agents](https://arxiv.org/abs/2610.12374)|2026-10-09T01:32:00+08:00|Computer Vision and Pattern Recognition (cs.CV)|knowledge_distillation|AgentGarten 的Adversarial Forcing通过精确重放恢复历史编码梯度，结合DMD与真实视频对抗监督训练四步实时渲染器。|
|[2610.12427 — FastBench: Can Streaming VLMs Perceive High-Dynamic Real-World Streams?](https://arxiv.org/abs/2610.12427)|2026-10-09T01:55:20+08:00|Computer Vision and Pattern Recognition (cs.CV) ; Computation and Language (cs.CL)|other|FastBench 表明高帧率能改善短时感知却挤掉历史，ProactiveFrame用双层窗口动态保留高密度近帧与低密度旧帧。|
|[2610.12444 — Rounding in Preconditioner Space: Redesigning 4-bit AdamW Optimizer-State Quantization](https://arxiv.org/abs/2610.12444)|2026-10-09T01:58:09+08:00|Machine Learning (cs.LG)|quantization|ZIP-SR在预条件器坐标舍入，ZE-EDEN校准正值下限，改善4bit AdamW的误差传播。|
|[2610.12448 — One Block, Multiple Depths: Recurrent Vision Transformers with Depth-Programmed Experts](https://arxiv.org/abs/2610.12448)|2026-10-09T01:58:36+08:00|Computer Vision and Pattern Recognition (cs.CV) ; Machine Learning (cs.LG)|other|reViT 用一个共享attention块和随深度变化的FFN专家权重混合，在相近FLOPs下大幅减少存储参数。|

每篇六节分析位于`papers/2026-10/<category>/<id>/tech_analysis.md`，分别保留官方证据链接、设置、数字、局限及学术启发。全部实际提交月份为2026-10。

## 5. 评分及依据

高分更优，1–10；精度看保留效果和对照可信度，压缩看实际对象及实测收益，创新看机制，可复现性看公开细节与本地验证。无证据的参数、字节或速度倍率不互相换算。

|ID|精度效果|压缩倍率|创新性|可复现性|
|---|---|---|---|---|
|2610.12214|7/10：保留交互能力但SPEAK自然度下降|5/10：部署路径1.46–1.59倍，非权重压缩|8/10：预测、可信前缀与在线修订配合|6/10：细节充分，但本地未跑语音栈|
|2610.12266|7/10：较固定坐标token好，但3D低于文本|7/10：报告特定3D场景8.3倍延迟收益|7/10：跨任务几何token与Chamfer约束|6/10：设置明确，训练成本高且未本地复现|
|2610.12274|8/10：三个交互基准改善明显|3/10：8B对32B只是规模对照，无严格压缩倍率|7/10：将执行harness纳入完整蒸馏链|6/10：数据规模协议清晰，未本地重训|
|2610.12282|8/10：长流重建质量及OOM边界改善|4/10：只限640读出，无统一存储倍率|7/10：多槽地址与稀疏读出解耦|6/10：有压力测试和预算消融，未实跑|
|2610.12304|8/10：固定剪枝器三seed改善PPL|6/10：50/70%稀疏，未证实端到端倍率|7/10：把社区结构转为层和头预算|7/10：公式及消融明确，未本地复现|
|2610.12307|8/10：多主干质量预算曲线，极端预算有代价|7/10：25%预算实速1.36–3.59倍依模型|8/10：熵四叉树配合可恢复多尺度token|6/10：细节与表格充分，微调成本高|
|2610.12327|7/10：比C4显著提升但未恢复dense|6/10：50%稀疏带来1.34–1.48倍实速|8/10：解码激活校准与SpMV联合|7/10：公式、预算和速度协议齐全|
|2610.12338|8/10：25%KV节省下保留至少98.3%相对任务分|5/10：独立总KV仅约1.33倍，组合另计|8/10：对称性对齐与attention后合并|7/10：校准、保护窗口和效能协议明确|
|2610.12374|6/10：定性长流改善，缺完整量化质量表|6/10：四步36.5FPS但无统一教师倍率|8/10：保留历史梯度与执行一致重放|6/10：公式和运行分解充分，需H100视频训练|
|2610.12427|6/10：较2FPS提升但不及更密集采样|3/10：有界输入预算，无实测字节倍率|6/10：把动态事件与历史压缩冲突显式评测|7/10：基线容易实现，评测需要视频及judge|
|2610.12444|8/10：多规模配对seed降低loss差|8/10：packed双moment7.53倍|8/10：将舍入空间与非线性更新联系|8/10：已重新跑Qwen局部验证，完整训练未复现|
|2610.12448|8/10：B模型略优，L及蒸馏有小幅损失|8/10：B约3.67倍、L约7.44倍存储减少|8/10：深度连续程序控制权重空间专家混合|7/10：公开公式及延迟表，未本地训练|

优先阅读SparseDecoding、VFold、4-bit AdamW与reViT。VFold的21.0→27.8ms TPOT和reViT动态权重合并延迟提示：省存储与加速需要独立验证。

## 6. 排除案例与关键词复核

- [2610.12355](https://arxiv.org/abs/2610.12355)：GPD在同一VLM上做RGB/3D特权条件自蒸馏，控制组参数规模不变，未研究小容量学生、推理步数或状态压缩；读取§3.3、§4.1–4.2。
- [2610.12367](https://arxiv.org/abs/2610.12367)：SGUID压的是训练用skill bank，不是模型参数或部署状态；§8明确不评价技能作为推理补丁，不能把11倍技能数减少写成模型压缩。读取§3、§8。
- [2610.12465](https://arxiv.org/abs/2610.12465)：SGS主体是reset采样，附录C.3蒸馏将点云教师迁移到双ResNet18 RGB学生，未建立更小模型或部署计算压缩对照。读取附录C.3、§5。
- [2610.12469](https://arxiv.org/abs/2610.12469)：同一图像编辑器的验证式自训练，未减少模型、采样步数或状态；读取§6–7。
- [2610.12337](https://arxiv.org/abs/2610.12337)：在2D恢复网络上增加跨切片动力学及蒸馏正则，以医学恢复为目标；Bi-CfC与Bi-GRU的成本对照不是对原模型的压缩。读取摘要、§6。
- [2610.12390](https://arxiv.org/abs/2610.12390)：离线生成结构化特征程序，训练目标是下游预测特征搜索，不是对既有模型压缩/教师策略蒸馏；读取摘要、§6。
- [2610.12369](https://arxiv.org/abs/2610.12369)：代码政策代替神经政策的范式及代码搜索，不是压缩训练好的神经模型或状态；读取摘要、§6。
- [2610.12376](https://arxiv.org/abs/2610.12376)：语言学词表与分词结构优化，未提出神经参数/状态压缩或执行成本实测；fertility改善不直接计模型压缩。读取摘要、§7。

复核词：quantization, quantize, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, distill, teacher, student, KV cache compression, mixed precision, GPTQ, AWQ及摘要中同义的cache merging、weight sharing、token reduction、few-step sampling、teacher trajectory等。所有110摘要均先完整阅读；没有关键词的条目也包含在语义审阅记录。

## 7. Qwen3-0.6B真实小规模复现

唯一以低比特神经数值状态为核心的新增量化论文2610.12444，对应`scripts/quantization/2610.12444/README.md`和`demo.py`。从前次未提交草稿复用并重新核对公式，今天重新运行ZIP-SR、ZE-EDEN、FP32三组，原始结果JSON随目录提交。非空壳。

块128，NF4一阶矩、含零Dyn4预条件器空间SR或Dyn4-NZ+EDEN二阶矩；4bit索引真实打包；每块FP32 scale；先更新参数后存储。CPU4线程、Python3.9.6、torch2.8.0、transformers4.57.6，固定本地Qwen3-0.6B revision c1899de289a04d12100db370d81485cdf75e47ca；BF16全模型前向，仅第一层q_proj FP32 master训练，3条人工短文本、3步、lr1e−5、β=.9/.95、eps1e−8、clip1、wd0。

|模式|第3步loss|moment实际字节|最大参数变化|
|---|---:|---:|---:|
|fp32|3.187395|16777216|3.00128e-05|
|zip_sr|3.196646|2228224|4.34048e-05|
|ze_eden|3.170836|2228224|4.15915e-05|

双moment 16MiB→2.125MiB，为7.5294×，不含模型、梯度或临时张量。各步文本不同，不能当学习曲线；三步loss差不能作为任务精度优劣结论。语法/导入、4bit往返、零块、Dyn4最小正值、预条件器SR期望（相对误差1.89e−16）、首步与FP32一致及NF4-SR期望通过。

未完成原论文规模的全参预训练、Tulu SFT、下游任务、多seed、GPU内核/峰值显存测量及真实LM-head末10% SR训练；本地只是CPU小规模算法验证。权重和依赖可用，没有网络失败；未投入多H200训练预算是规模边界。其余11篇不是新增数值量化论文，未执行各自完整训练实验。

## 8. 独立快照与Git校验

严格从fetch后的origin/main `abfe8f2767d8bf881d586718ab4db33fc576be6a`创建linked worktree `/private/tmp/reading_machine_arxiv_20261012`，分支`feature/arxiv-daily-2026-10-12`。未继承历史feature分支。仅在隔离目录删除main自带2026-07-28历史日报，保留各README；papers仅12篇，reports仅本日报，scripts仅通用说明和2610.12444本轮复现，metadata仅本窗口索引/关键词/审计。

提交前检查：新增集合与550历史ID零交集；papers=metadata=12篇，复现目录=量化子集1篇；日期均在窗口且月份正确；六节格式、CSV、JSON、git diff --check及原工作树status与逐文件SHA256保护检查。Git提交及远端SHA在自动化最终消息与本地run_status.json记录，避免在提交正文中自引用未知SHA。
