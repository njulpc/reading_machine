# arXiv 模型压缩论文日报：2026-10-12

- 运行日：2026-10-13，Asia/Shanghai；核验时间：2026-10-13T01:12:00.299120+08:00。
- 固定三天窗口：2026-10-10、10-11、10-12 各日00:00–23:59:59（北京时间）。归日依据官方 /abs 的 v1 提交时间，不使用公告日期。
- 结论：窗口相关 **5篇**，历史重复 **0篇**，本次新增 **5篇**。量化0、剪枝2、知识蒸馏1、其他2。
- 10-11及10-12：**截至运行时 arXiv 官方网页未检出**。此处只描述当前公开网页，不能推断最终投稿量为零，后续三天窗口继续回查。

## 1. 逐日计数与完整论文表

|v1实际提交日（北京时间）|全主题窗口记录|相关原始跨列表出现数|相关规范ID数|历史重复|本次新增|
|---|---:|---:|---:|---:|---:|
|2026-10-10|63|12|5|0|5|
|2026-10-11|0|0|0|0|0|
|2026-10-12|0|0|0|0|0|

63是全主题数，不是模型压缩论文数；跨分类、new/recent和版本按规范ID统一。时间同时列出UTC以消除“10月9日提交为何属于10月10日”的歧义。

|arXiv ID / 标题|v1 UTC|v1 北京时间|主/交叉分类|方向与结论|
|---|---|---|---|---|
|[2610.13806 — FORTE: A Production Framework for Feature Evaluation and Deprecation in Industrial Recommender Systems](https://arxiv.org/abs/2610.13806)|2026-10-09T16:18:39+00:00|2026-10-10T00:18:39+08:00|Machine Learning (cs.LG) ; Artificial Intelligence (cs.AI)|pruning；FORTE 通过持续特征评估、联合消融和在线验证，删除低贡献输入及关联参数；Pin Ranker 参数减少29.9%，吞吐提高19.8–25.5%。|
|[2610.13856 — Event-based Action Recognition by Pre-Training on Multi-Frame Representations](https://arxiv.org/abs/2610.13856)|2026-10-09T17:05:40+00:00|2026-10-10T01:05:40+08:00|Computer Vision and Pattern Recognition (cs.CV)|pruning；基于事件活动量筛除token，在8帧设置将token从1568减至784；跨数据预训练后的THU准确率78.7%→78.5%。|
|[2610.13858 — LapMerge: Differentiable Exact-Budget Token Merging in Linear Time](https://arxiv.org/abs/2610.13858)|2026-10-09T17:07:17+00:00|2026-10-10T01:07:17+08:00|Computer Vision and Pattern Recognition (cs.CV)|other；LapMerge 用Laplace核等质量分段及前后缀扫描实现可微、精确预算token合并；10%视觉token下POPE F1为81.31。|
|[2610.13881 — Prediction Is Not a Sufficient Memory State](https://arxiv.org/abs/2610.13881)|2026-10-09T17:27:06+00:00|2026-10-10T01:27:06+08:00|Machine Learning (cs.LG)|other；该理论证明只保留当前预测不足以支持未来更新；softmax前缀的精确连续记忆需要N(d+p)个坐标，不能解释为实用KV压缩不可行。|
|[2610.13944 — InstantFusion: A Shared Latent Interface for Heterogeneous Image Generators](https://arxiv.org/abs/2610.13944)|2026-10-09T17:59:04+00:00|2026-10-10T01:59:04+08:00|Computer Vision and Pattern Recognition (cs.CV)|knowledge_distillation；InstantFusion 对齐异构生成器潜状态及动态，支持Qwen-Image→SD3蒸馏；HPSv2仅提升0.19，混合加速存在质量与显存代价。|

## 2. 评分与精读导航

1–10分为本日报编辑判断；理论论文缺乏任务精度或部署倍率时低分表示证据尚缺，不是实验失败。量纲不同的压缩与速度不能直接相比。

|论文|精度效果|压缩倍率|创新性|可复现性|评分依据|
|---|---:|---:|---:|---:|---|
|[2610.13806 六节精读](../../../papers/2026-10/pruning/2610.13806/tech_analysis.md)|8|5|7|5|精度8：两个生产模型经在线验证无显著主指标退化，但59特征方案触发护栏。压缩5：最大参数减少29.9%，约1.43倍，而非43.3%特征删除等价整模压缩。创新7：重点在时序筛选、成本筛选与特征血缘形成闭环。复现5：流程较清楚，但工业数据、模型与在线流量不可直接复得。|
|[2610.13856 六节精读](../../../papers/2026-10/pruning/2610.13856/tech_analysis.md)|8|6|6|7|精度8：一半token下跨数据迁移只降0.2个百分点，但DailyDVS同配置下降1.4点。压缩6：明确2倍token削减，无端到端时延或权重字节证明。创新6：活动量选择、稀疏感知MAE和多mask组合，单个机制较直接。复现7：数据、模型和训练参数较完整，但1500轮预训练成本较高，本轮未运行。|
|[2610.13858 六节精读](../../../papers/2026-10/other/2610.13858/tech_analysis.md)|8|8|9|8|精度8：POPE 10%预算较VisionSelector+1.58点，病理学第二名；30%预算增益区间跨零。压缩8：10%token预算即10倍序列压缩，未证明10倍整模显存压缩。创新9：精确预算、可微边界与线性扫描的统一。复现8：正文、附录与补充包说明充分，准确率使用native PyTorch；本轮未执行。|
|[2610.13881 六节精读](../../../papers/2026-10/other/2610.13881/tech_analysis.md)|3|3|8|7|精度3：无神经模型任务精度实验，不是负面效果。压缩3：给出状态与有限比特下界，未提供可部署压缩倍率。创新8：原生单次延续辨识与精确隐藏状态维数相连接。复现7：定理假设和确定性验证脚本说明完整，但本轮未下载运行补充脚本，亦未逐行证明审计。|
|[2610.13944 六节精读](../../../papers/2026-10/knowledge_distillation/2610.13944/tech_analysis.md)|6|5|8|5|精度6：SD3蒸馏平均HPSv2+0.19且低于教师；不同混合指标涨跌并存。压缩5：混合推理可快约4.31–7.40倍但不减少总模型存储，不能视作权重压缩倍率。创新8：共享潜接口同时匹配状态与动力学，支持跨架构OPD。复现5：训练参数明确，但切换公式符号/方向不一致且跨架构监督实现细节仍需核实。|

## 3. 全量网页覆盖证据

本轮实际下载下列五分类的new及recent官方HTML，统一show=2000、skip=0。各页总数均低于2000，无第二页；逐一验证总条数=实际dt数，并逐h3日期/类型分组核验“showing a of b”与实计数全部相等。new同时包含新稿、交叉与替换；recent覆盖10-12、10-09、10-08、10-07、10-06。公告日期仅用于验证页面覆盖，不用于论文归日。

|分类入口|显示总数|实际覆盖|日期/类型分组（原文）|
|---|---:|---|---|
|[cs.AI new](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)|313|skip0，1–313|Showing new listings for Monday, 12 October 2026；New submissions (showing 83 of 83 entries)；Cross submissions (showing 78 of 78 entries)；Replacement submissions (showing 152 of 152 entries)|
|[cs.AI recent](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0)|1649|skip0，1–1649|Mon, 12 Oct 2026 (showing 161 of 161 entries )；Fri, 9 Oct 2026 (showing 302 of 302 entries )；Thu, 8 Oct 2026 (showing 282 of 282 entries )；Wed, 7 Oct 2026 (showing 350 of 350 entries )；Tue, 6 Oct 2026 (showing 554 of 554 entries )|
|[cs.AR new](https://arxiv.org/list/cs.AR/new?show=2000&skip=0)|11|skip0，1–11|Showing new listings for Monday, 12 October 2026；New submissions (showing 6 of 6 entries)；Cross submissions (showing 4 of 4 entries)；Replacement submissions (showing 1 of 1 entries)|
|[cs.AR recent](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0)|67|skip0，1–67|Mon, 12 Oct 2026 (showing 10 of 10 entries )；Fri, 9 Oct 2026 (showing 9 of 9 entries )；Thu, 8 Oct 2026 (showing 8 of 8 entries )；Wed, 7 Oct 2026 (showing 26 of 26 entries )；Tue, 6 Oct 2026 (showing 14 of 14 entries )|
|[cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)|172|skip0，1–172|Showing new listings for Monday, 12 October 2026；New submissions (showing 72 of 72 entries)；Cross submissions (showing 44 of 44 entries)；Replacement submissions (showing 56 of 56 entries)|
|[cs.CL recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|768|skip0，1–768|Mon, 12 Oct 2026 (showing 116 of 116 entries )；Fri, 9 Oct 2026 (showing 144 of 144 entries )；Thu, 8 Oct 2026 (showing 118 of 118 entries )；Wed, 7 Oct 2026 (showing 147 of 147 entries )；Tue, 6 Oct 2026 (showing 243 of 243 entries )|
|[cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)|237|skip0，1–237|Showing new listings for Monday, 12 October 2026；New submissions (showing 127 of 127 entries)；Cross submissions (showing 26 of 26 entries)；Replacement submissions (showing 84 of 84 entries)|
|[cs.CV recent](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0)|995|skip0，1–995|Mon, 12 Oct 2026 (showing 153 of 153 entries )；Fri, 9 Oct 2026 (showing 207 of 207 entries )；Thu, 8 Oct 2026 (showing 186 of 186 entries )；Wed, 7 Oct 2026 (showing 164 of 164 entries )；Tue, 6 Oct 2026 (showing 285 of 285 entries )|
|[cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)|413|skip0，1–413|Showing new listings for Monday, 12 October 2026；New submissions (showing 146 of 146 entries)；Cross submissions (showing 116 of 116 entries)；Replacement submissions (showing 151 of 151 entries)|
|[cs.LG recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|1894|skip0，1–1894|Mon, 12 Oct 2026 (showing 262 of 262 entries )；Fri, 9 Oct 2026 (showing 324 of 324 entries )；Thu, 8 Oct 2026 (showing 353 of 353 entries )；Wed, 7 Oct 2026 (showing 355 of 355 entries )；Tue, 6 Oct 2026 (showing 600 of 600 entries )|

10页共6519次出现，规范化后4299个ID；全部已读取官方abs HTML并成功解析标题、摘要、分类和v1，0失败。本轮新抓815份，复用上轮原始官方HTML3484份（来源及哈希保存在本地证据目录）；不声称4299篇全部为本轮新请求。v1先筛选出63篇窗口记录，这63份abs均为本轮新抓，并全部逐篇语义审阅。其余4236篇因v1在窗口外排除，不声称本轮逐篇全文精读它们。关键词不是召回门槛。

阳性对照：[2610.13778](https://arxiv.org/abs/2610.13778) v1=2026-10-09 15:59:40 UTC / 北京23:59:40（窗外相邻日）；[2610.13780](https://arxiv.org/abs/2610.13780) v1=2026-10-09 16:01:04 UTC / 北京10-10 00:01:04（窗内）。这确认按真实v1跨日划分。列表和详情正常可读，零日不是抓取错误。

复核关键词含 quantization、quantize、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache compression、mixed precision、GPTQ、AWQ 及 token selection/merging、memory、feature deprecation。逐词命中和全部63条语义判定保存在 `metadata/2026-10/retrieval_audit.json`。6篇候选阅读官方全文相关章节，最终5篇入选；[2610.13834](https://arxiv.org/html/2610.13834) 的DoubleCat/SemiCat属于扩散路径与训练推理匹配设计，没有模型压缩或蒸馏方案，排除。13819是解释性方向删除，13841是软件sandbox快照，13843是量子指令集，均不能因“删除/状态/量子”误归类。

## 4. 历史去重审计

- fetch后逐一执行46个历史 `origin/feature/arxiv-daily-*` 的 `git ls-tree -r --name-only`，并用git show读取每个metadata索引交叉核验。
- 真实 `papers/**/<id>/tech_analysis.md` 提取规范ID，去掉版本后缀，得到562个已分析ID。上轮10-12分支的12篇计入本轮历史集合。
- metadata-only：2607.27951、2607.28410、2607.28457，没有对应真实精读文件，不计完成。
- 本窗口相关跨列表出现12次→5规范ID；历史重复0；排除重复ID及来源分支为空；最终新增：2610.13806, 2610.13856, 2610.13858, 2610.13881, 2610.13944。
- 新增集合与历史集合交集=[]。今日远端分支初始不存在，不属于续跑旧feature。46个来源分支与精确SHA完整记录于索引和审计JSON，本地完整论文树证据位于 `/Users/lipengcheng/.codex/automations/arxiv/runs/2026-10-13/history.json`。

## 5. 复现与证据边界

本次新增quantization论文为0，因此不创建Qwen3-0.6B量化复现目录。13881虽讨论有限比特码，但提供的是状态压缩下界与离线量化存在性，不是可用于Qwen的量化算法；不伪造“实现”。其他5篇均未在本轮重跑论文实验，报告数字明确来自官方全文。没有网络、依赖或算力阻塞，也不把“未运行”包装成复现实验完成。

重点阅读LapMerge（精确预算线性合并）与FORTE（参数削减的真实线上证据）。InstantFusion需注意式13/14切换指标定义不一致、三阶段顺序影响及显存代价；理论记忆下界不能推广为实践KV压缩不可能。

## 6. 独立快照与检查

从fetch后origin/main `abfe8f2767d8bf881d586718ab4db33fc576be6a` 创建linked worktree `/private/tmp/reading_machine_arxiv_20261013`，分支 `feature/arxiv-daily-2026-10-13`。历史feature只读用于规范学习和去重，未继承内容。

隔离目录删除main自带 `reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md`；最终papers仅README与本次5精读，reports仅README和本日报，scripts仅README（无历史或本次quantization复现），metadata仅README与2026-10本次索引/CSV/审计。原工作树6项用户改动以status与逐文件SHA256检查保护。

提交前检查目录ID、索引与CSV、新增月份、六节标题、历史零交集、diff与单次提交关系；push后通过ls-remote、log和merge-base核对远端SHA、父提交为origin/main且仅一提交。最终提交SHA与实际检查结果记录于本地 `run_status.json`、`validation.json`，避免在提交内容内自引用SHA。

证据范围限制：未重新下载3484份窗口外abs缓存；没有逐行审计全部数学证明和所有附录，未重跑5篇论文实验。除这些披露的验证边界，本次检索、精读、独立快照和发布流程按要求执行。
