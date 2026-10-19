# arXiv 模型压缩论文日报（主日期2026-10-19）

运行时间：2026-10-20T01:17:23.302192+08:00。固定检索窗口：**2026-10-17、10-18、10-19（Asia/Shanghai，逐日00:00–23:59）**。按官方abs Submission history的v1 UTC换算北京时间，不使用公告日或ID大小代替提交日期。

**结论：窗口相关6篇，历史重复0篇，本次新增6篇；量化1篇、知识蒸馏2篇、other 3篇。** 当前公开结果不能代表尚未公告投稿。

## 逐日统计与口径

|v1本地提交日|原始相关出现次数（含跨列表重复）|跨列表去重后相关|历史已完成重复|本次新增|说明|
|---|---:|---:|---:|---:|---|
|2026-10-17|14|6|0|6|当前公开相关结果|
|2026-10-18|0|0|0|0|截至运行时 arXiv 官方网页未检出|
|2026-10-19|0|0|0|0|截至运行时 arXiv 官方网页未检出|

两个零值日不是实际无人投稿的断言。五分类当前最新公告为10月19日；全体可见条目的最新v1本地时间仅10月17日01:59:55。后续依固定三天窗口自动回查。公开但提交日期已在窗口外的论文，本轮不补入。

## 新增论文完整表

|ID与官方链接|完整标题|v1 UTC|v1北京时间|主分类/交叉分类（顺序）|类型|一句话结论|
|---|---|---|---|---|---|---|
|[2610.23703](https://arxiv.org/abs/2610.23703)|Blitz: Accelerating the Diffusion Modules of AlphaFold3 and Boltz-2|2026-10-16T16:29:04+00:00|2026-10-17T00:29:04+08:00|Machine Learning (cs.LG)|knowledge_distillation|几何噪声调度与多步一致性蒸馏把AF3的200次扩散评估降到8次，同时必须审查分子几何失效尾部。|
|[2610.23735](https://arxiv.org/abs/2610.23735)|LagNet: Lag-Structured Operators for Long-Term Time Series Forecasting|2026-10-16T16:44:53+00:00|2026-10-17T00:44:53+08:00|Machine Learning (cs.LG)|other|按相对时间滞后共享参数，DLinear替换实例约27倍参数缩减，但精度与收益依赖任务和被替换层占比。|
|[2610.23787](https://arxiv.org/abs/2610.23787)|DLite: History-free Speculative Decoding for Agentic AI|2026-10-16T17:18:54+00:00|2026-10-17T01:18:54+08:00|Computation and Language (cs.CL)|other|通过目标模型隐藏状态和低秩序列头移除草稿历史KV，目标模型自身KV仍保留。|
|[2610.23795](https://arxiv.org/abs/2610.23795)|Persistent Planar Memory for Video World Models|2026-10-16T17:21:54+00:00|2026-10-17T01:21:54+08:00|Computer Vision and Pattern Recognition (cs.CV)|other|以约10万平面基元维护约5MB持久场景记忆，减少的是视频模型的推理状态，不是5B骨干参数。|
|[2610.23796](https://arxiv.org/abs/2610.23796)|FuTransformer: FP8 prefill and INT4 decode for Llama-style inference on Hopper|2026-10-16T17:22:01+00:00|2026-10-17T01:22:01+08:00|Artificial Intelligence (cs.AI)|quantization|FP8预填充与INT4解码按瓶颈分别优化，实际质量损失与双份KV存储限制了理想压缩收益。|
|[2610.23831](https://arxiv.org/abs/2610.23831)|Beyond the Answer: Student-Conditioned Trace Construction for Reasoning Distillation|2026-10-16T17:52:58+00:00|2026-10-17T01:52:58+08:00|Computation and Language (cs.CL) ; Machine Learning (cs.LG)|knowledge_distillation|以学生可读性筛选教师改写轨迹，收益主要体现为跨任务迁移，不能把学生训练前后视作参数压缩。|

## 评分与精度—压缩权衡

评分1–10，越高越好，为有证据支持的主观评价，不把不同任务精度或不同压缩对象统一排名。论文实验未独立重跑，FuTransformer仅完成组件级Qwen数值验证。

|论文|精度效果|压缩倍率|创新性|可复现性|评分依据|
|---|---:|---:|---:|---:|---|
|Blitz|8|8|8|6|8：AF3平均结构精度保留但物理失败长尾仍在；8：AF3 NFE200→8仅扩散25倍；8：schedule、分段蒸馏及几何评估组合；6：32 H100和生物数据管线，本轮未运行。|
|LagNet|7|8|7|8|7：平均精度损失小但Solar替换可恶化10.4%；8：实例65.2K→2.4K，非所有horizon固定倍率；7：lag共享配位置scale；8：算子简单且有5种子配对实验。|
|DLite|7|6|8|7|7：接受长度与端到端吞吐均测，缺系统任务质量细分；6：消除draft历史KV但保留target KV，缺总bytes；8：同构教师桥接无历史草稿；7：细节充分但需32 H800训练。|
|PPMem|8|7|8|6|8：系统比较与同骨干消融相互支持；7：约5MB几何池，2100倍是对理论dense点数非总bytes；8：可融合平面状态与内部几何预测；6：5B视频训练、数据与渲染环境要求高。|
|FuTransformer|6|7|8|7|6：ARC-Challenge下降7.6点；7：INT4 payload理想4倍但有scale及BF16镜像；8：阶段分工、fragment布局及融合；7：完成本地数值验证，Hopper系统未复现。|
|ReDiST|8|5|8|8|8：跨任务EM增益明确但并非全模型领先；5：14B→8B名义1.75倍，未测部署资源；8：学生可读性筛选与编辑联动；8：训练细节充分，离线生成仍有成本。|

重点数值与证据：

- ReDiST：Qwen3-8B在2Wiki EM 0.686，对MBT-R 0.633；Qwen3-4B则略低于NLL基线。见[表1–3](https://arxiv.org/html/2610.23831v1#S4)。
- FuTransformer：Llama3.1-8B PPL 6.240→7.182（GPTQ+旋转KV），ARC-Challenge 0.552→0.476；真实decode 2.8ms/step对8.1ms。见[§4](https://arxiv.org/html/2610.23796v1#S4)。
- DLite：8B SWE-bench速度相对AR为2.74倍，DSpark为1.60倍；64并发LCB TPS5758对5621，仅约2.44%增益。见[表3–4](https://arxiv.org/html/2610.23787v1#S5)。
- PPMem：约100K平面/5MB，210M dense点为理论累计；同骨干几何AbsRel0.210对无记忆0.272。见[表1与表3](https://arxiv.org/html/2610.23795v1#S3)。
- LagNet：DLinear参数例65.2K→2.4K，对应H=336；不同horizon不同参数量，平均MSE+0.1%。见[表3](https://arxiv.org/html/2610.23735v1#Sx3.SSx4)及附录D.1。
- Blitz：AF3 NFE200→8，lDDT0.8615→0.8635，但平均clash0.54→3.80；不是整pipeline25倍加速。见[表2](https://arxiv.org/html/2610.23703v1#S5)。

## 官方分类页覆盖证据

五分类new与recent各完整扫描一次。每页show=2000、skip=0，最大1957条，均无需第二页；实际dt计数等于页面total，所有h3显示条数逐组匹配。new同时覆盖new submissions、cross submissions和replacements；recent覆盖10-19、10-16、10-15、10-14、10-12分组。

|分类|入口|显示总数|实读条目|覆盖分组|
|---|---|---:|---:|---|
|cs.LG|[new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)|391|391|Showing new listings for Monday, 19 October 2026；New submissions (showing 126 of 126 entries)；Cross submissions (showing 96 of 96 entries)；Replacement submissions (showing 169 of 169 entries)|
|cs.LG|[recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|1957|1957|Mon, 19 Oct 2026 (showing 222 of 222 entries )；Fri, 16 Oct 2026 (showing 306 of 306 entries )；Thu, 15 Oct 2026 (showing 305 of 305 entries )；Wed, 14 Oct 2026 (showing 862 of 862 entries )；Mon, 12 Oct 2026 (showing 262 of 262 entries )|
|cs.CL|[new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)|226|226|Showing new listings for Monday, 19 October 2026；New submissions (showing 104 of 104 entries)；Cross submissions (showing 42 of 42 entries)；Replacement submissions (showing 80 of 80 entries)|
|cs.CL|[recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|1006|1006|Mon, 19 Oct 2026 (showing 146 of 146 entries )；Fri, 16 Oct 2026 (showing 177 of 177 entries )；Thu, 15 Oct 2026 (showing 182 of 182 entries )；Wed, 14 Oct 2026 (showing 385 of 385 entries )；Mon, 12 Oct 2026 (showing 116 of 116 entries )|
|cs.CV|[new](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)|201|201|Showing new listings for Monday, 19 October 2026；New submissions (showing 106 of 106 entries)；Cross submissions (showing 20 of 20 entries)；Replacement submissions (showing 75 of 75 entries)|
|cs.CV|[recent](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0)|1066|1066|Mon, 19 Oct 2026 (showing 126 of 126 entries )；Fri, 16 Oct 2026 (showing 165 of 165 entries )；Thu, 15 Oct 2026 (showing 143 of 143 entries )；Wed, 14 Oct 2026 (showing 479 of 479 entries )；Mon, 12 Oct 2026 (showing 153 of 153 entries )|
|cs.AI|[new](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)|344|344|Showing new listings for Monday, 19 October 2026；New submissions (showing 92 of 92 entries)；Cross submissions (showing 82 of 82 entries)；Replacement submissions (showing 170 of 170 entries)|
|cs.AI|[recent](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0)|1753|1753|Mon, 19 Oct 2026 (showing 174 of 174 entries )；Fri, 16 Oct 2026 (showing 286 of 286 entries )；Thu, 15 Oct 2026 (showing 280 of 280 entries )；Wed, 14 Oct 2026 (showing 852 of 852 entries )；Mon, 12 Oct 2026 (showing 161 of 161 entries )|
|cs.AR|[new](https://arxiv.org/list/cs.AR/new?show=2000&skip=0)|18|18|Showing new listings for Monday, 19 October 2026；New submissions (showing 9 of 9 entries)；Cross submissions (showing 3 of 3 entries)；Replacement submissions (showing 6 of 6 entries)|
|cs.AR|[recent](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0)|67|67|Mon, 19 Oct 2026 (showing 12 of 12 entries )；Fri, 16 Oct 2026 (showing 12 of 12 entries )；Thu, 15 Oct 2026 (showing 10 of 10 entries )；Wed, 14 Oct 2026 (showing 23 of 23 entries )；Mon, 12 Oct 2026 (showing 10 of 10 entries )|

总7029次列表出现→4673个规范化ID。每个ID解析官方title、abstract、subjects、v1，失败0。807页本轮新抓，3866页复用以往保存的官方原始HTML，全部重新解析并记录SHA256与来源路径；不声称4673页均本轮联网新抓或逐篇人工精读。先按真实v1排除4612个窗外ID，再对全部61篇窗口摘要逐篇语义判断，关键词只作复核，6候选均阅读官方HTML v1方法、实验及相关附录。窗口61页均本轮新抓。

时间与主题阳性对照：

- [TriRouter 2610.23665](https://arxiv.org/abs/2610.23665)：v1 UTC10-16 15:59:00→本地10-16 23:59:00，窗口外相邻分钟。
- [TUPLE-Bench 2610.23668](https://arxiv.org/abs/2610.23668)：UTC10-16 16:00:57→本地10-17 00:00:57，窗口内；其quantization针对隐私输出概率，非神经模型压缩，语义排除。
- [ECDD 2610.23469](https://arxiv.org/abs/2610.23469)：本地10-16 21:48:30，属于紧凑医学VLM蒸馏，官方列表可召回但本轮按日期排除；说明并非关键词全部失效。
- [2610.23856](https://arxiv.org/abs/2610.23856)是全体可见条目中最新v1（本地10-17 01:59:55）。

边界提示：ECDD等10-16提交稿在当前10-19公告中可见，但已落出本轮17–19窗口。周末/延迟公告加上凌晨运行可能使固定三天回查仍有漏过的提交日；本轮保留证据、不越界补入，也未擅自更改调度。

## 历史去重审计

安全fetch后遍历**49个**远端日更分支，对每个执行ls-tree并读取全部metadata索引；真实tech_analysis目录归一化ID共有**584**。metadata-only 2607.27951、2607.28410、2607.28457无真实精读，不计完成。所有历史分支SHA已与ls-remote全集核验。主线SHA：`abfe8f2767d8bf881d586718ab4db33fc576be6a`。

历史重复ID及来源分支：**无**（相关6篇与584历史ID交集为空）。本次不是续跑已有远端分支。最终新增ID：2610.23703, 2610.23735, 2610.23787, 2610.23795, 2610.23796, 2610.23831。

跨分类/new-recent重复如下，全部先合并规范化ID，未重复生成成果：

|ID|出现次数|列表来源（不是历史分支）|
|---|---:|---|
|2610.23703|2|[cs.LG/new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)；[cs.LG/recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|
|2610.23735|2|[cs.LG/new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)；[cs.LG/recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|
|2610.23787|2|[cs.CL/new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)；[cs.CL/recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|
|2610.23795|2|[cs.CV/new](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)；[cs.CV/recent](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0)|
|2610.23796|2|[cs.AI/new](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)；[cs.AI/recent](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0)|
|2610.23831|4|[cs.LG/new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)；[cs.LG/recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)；[cs.CL/new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)；[cs.CL/recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|

49个去重来源分支与精确SHA记录在`metadata/2026-10/papers_index.json`的dedup_source_branches；本次审计同时记录query_window、historical_analyzed_ids_count、excluded_duplicate_ids与new_papers_count。完整历史树、全部abs、全文、61逐项判断及关键词复核原始证据保存在本机自动化运行目录，不累计进入论文索引。

## Qwen3-0.6B复现与验证

复现目录：`scripts/quantization/2610.23796/`（README.md、demo.py、results.json）。Python3.9.6、torch2.8.0、transformers4.57.6、CPU4线程；本地模型revision c1899de289a04d12100db370d81485cdf75e47ca。

实际实现首层q_proj静态128分组INT4、GPTQ 5% damping/FP64误差反馈、RMS gain折叠、nibble pack/unpack和第一层Hadamard KV；delayed FP8只做小张量测试。4×128人工校准token、2×128独立文本评估；真实64token BF16 prefill+8步缓存decode通过。8项数值测试、语法/导入通过。

GPTQ单层权重KL为0.000614/0.000406，增加旋转KV后为0.083746/0.068204。小样本结果不证明GPTQ普遍优于RTN或整模无损。单矩阵payload+scale从4,194,304降至1,114,112bytes（约3.765倍）；保留BF16主KV并加INT4镜像时，总KV存储约1.266倍原占用。

未完成：Hopper CUDA融合kernel、MMA布局与速度验证、整模INT4、标准WikiText-2及多种子评估；本机无H100，现有代码是可运行的数值机制移植，不是完整系统复现。其余5篇未执行视频/蛋白/语言模型训练和服务基准，原因是缺原数据、硬件与训练环境；不伪造结果。

## 独立快照与版本验证

严格从最新origin/main创建linked worktree及`feature/arxiv-daily-2026-10-20`；未继承历史feature。清理main自带2026-07-28旧日报；papers只含6篇新增精读与README，reports只含本日报与README，scripts只含通用README与本次1个量化复现，metadata只含README与本月6篇独立索引/CSV/审计。

提交前验证最终ID与历史集合零交集、目录/metadata/CSV一致、量化复现集合等于新增量化子集；原工作树未提交文件status及逐文件SHA256前后不变。提交后核验仅一个以origin/main为父的提交，push后核验ls-remote SHA及merge-base；具体提交SHA保留在Git和运行审计，不把自引用SHA写入提交本身。

本机完整证据目录：`/Users/lipengcheng/.codex/automations/arxiv/runs/2026-10-20`。
