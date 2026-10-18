# arXiv 模型压缩精读日报：2026-10-18

运行日为2026-10-19（Asia/Shanghai），固定检索2026-10-16、17、18三个完整自然日；本文按官方abs的v1时间转换北京时间归档，不使用公告日期代替提交日期。未使用arXiv官方API。

## 结果与日期边界

|实际提交自然日（北京时间）|公开相关独立ID|历史已分析重复|本次新增|
|---|---:|---:|---:|
|2026-10-16|17|0|17|
|2026-10-17|0|0|0|
|2026-10-18|0|0|0|
|三天合计|17|0|17|

10月17日与18日：**截至运行时 arXiv 官方网页未检出**。页面最新公告仍是10月16日；这不是对尚未公开投稿的零值断言，后续固定三天窗口需继续回查。三天窗口不代表本轮补齐此前10月13–15日未完成的任务，未把那些草稿或缓存当作历史已完成。

分类：量化1篇、剪枝2篇、知识蒸馏7篇、其他模型内部存储/计算压缩7篇。纳入模型权重/内部激活/KV压缩、专家整合、规划器或多步生成器蒸馏及显式token计算裁减；不将所有teacher/student、图像/文本数据压缩或更便宜的agent路由自动纳入。

## 论文总览

分数依次为精度效果/压缩倍率/创新性/可复现性，1–10，为本轮主观评估。各数值的对象不同，不能横向当作统一的整模压缩倍数。

|ID与官方详情|标题|v1北京时间|类别|一句话结论|评分|
|---|---|---|---|---|---|
|[2610.22130](https://arxiv.org/abs/2610.22130)|DropKV: Decoupling Residual-Output Perturbation for Near-Optimal KV-Cache Eviction|2026-10-16 00:05:17+08:00|other|DropKV 用单 token 淘汰造成的输出扰动构造可融合评分，5% KV 预算下保留更好的长上下文能力。|8/9/8/8|
|[2610.22137](https://arxiv.org/abs/2610.22137)|CART: Compatible Routing for Multimodal Continual Instruction Tuning|2026-10-16 00:11:22+08:00|other|CART 联合路由视觉 projector 与语言 LoRA，并按输入分布合并专家以限制持续学习模型增长。|7/5/8/7|
|[2610.22143](https://arxiv.org/abs/2610.22143)|FALCON: FPGA-Accelerated Latency-Certifiable Occupancy Networks for Camera-Based Autonomous Driving|2026-10-16 00:14:24+08:00|quantization|FALCON 以受限 INT8 校准、INT16 几何路径和固定工作量 FPGA 算子部署占据网络；Qwen 转移实验证明非负裁剪不能直接套用。|7/5/6/7|
|[2610.22178](https://arxiv.org/abs/2610.22178)|REKI: Registering Knowledge in VLAs|2026-10-16 00:34:06+08:00|other|REKI 把过去视觉上下文压入动作专家的少量 register KV，使 VLA 保留历史而只增加很小推理成本。|8/5/7/8|
|[2610.22179](https://arxiv.org/abs/2610.22179)|LCT: Losslessly Compressed Tensors with GPU friendly execution for Training|2026-10-16 00:34:35+08:00|other|LCT 无损编码 BF16 指数并支持GPU训练期反复编码，在Qwen3-4B上最多节约23.8%峰值显存。|9/6/8/8|
|[2610.22184](https://arxiv.org/abs/2610.22184)|Whole-Body Dexterity|2026-10-16 00:40:48+08:00|knowledge_distillation|Whole-Body Dexterity 将逐物体强化学习专家蒸馏成不依赖特权物体状态的统一部署控制器。|7/3/7/6|
|[2610.22196](https://arxiv.org/abs/2610.22196)|Hy-Memory-30B-A3B: Attributed Reinforcement Learning for Long-Term Memory Writing|2026-10-16 00:46:47+08:00|knowledge_distillation|Hy-Memory 将旗舰教师的写入协议蒸馏到30B-A3B学生，再用逐chunk强化学习提升跨框架记忆质量。|7/4/7/6|
|[2610.22217](https://arxiv.org/abs/2610.22217)|Skill-Decoupled On-Policy Expert Distillation for Unified Vision-Language Models|2026-10-16 01:01:41+08:00|knowledge_distillation|SCOPED 将四类视觉专家的程序化技能蒸馏进一个VLM，8B学生的八基准均分从67.30升至73.13。|8/6/8/7|
|[2610.22236](https://arxiv.org/abs/2610.22236)|Training-Free On-Policy Distillation|2026-10-16 01:15:01+08:00|knowledge_distillation|TF-OPD 用教师自身生成轨迹的二阶矩求解逐层最小二乘，将数学与代码专家合为一个7B模型。|8/5/8/8|
|[2610.22240](https://arxiv.org/abs/2610.22240)|MMSearch-OPD: Easy Made Hard, Hard Made Learnable for Long-Horizon Multimodal Search Agents|2026-10-16 01:16:18+08:00|knowledge_distillation|MMSearch-OPD 用27B教师对9B学生的失败搜索轨迹提供选择性token指导，联合RL后七基准均分60.2。|8/7/7/7|
|[2610.22256](https://arxiv.org/abs/2610.22256)|BitSparse: Compact Activation Storage for ReLU Feed-Forward Networks|2026-10-16 01:24:51+08:00|other|BitSparse 用位图和紧凑非零值无损保存ReLU激活，避免checkpointing重算并在高稀疏度下节省训练显存。|9/7/7/8|
|[2610.22311](https://arxiv.org/abs/2610.22311)|Velox: Spatial Memory Makes World Models Efficient|2026-10-16 01:50:20+08:00|pruning|Velox 以几何视锥重叠调节历史注意力块路由，使48块世界生成的注意力4.36×、去噪2.43×加速。|8/7/8/7|
|[2610.22340](https://arxiv.org/abs/2610.22340)|Dexterity from Supervised Play|2026-10-16 01:55:50+08:00|knowledge_distillation|DSP 可将世界模型中的MPC搜索蒸馏为闭环目标条件策略，把在线候选评估成本转为离线训练。|7/3/7/6|
|[2610.22347](https://arxiv.org/abs/2610.22347)|Speculative Forcing for Efficient Autoregressive Video Generation|2026-10-16 01:57:01+08:00|pruning|Speculative Forcing 按token收敛程度停止去噪，在保留上下文KV的同时削减视频生成计算。|8/7/8/7|
|[2610.22358](https://arxiv.org/abs/2610.22358)|PathFM: Fast Generative Forecasting of Multivariate Trajectories|2026-10-16 01:58:45+08:00|knowledge_distillation|PathFM 将轨迹flow蒸馏成1–2次网络评估，并共享历史计算，126M模型可在L4上51.6ms生成32条预测路径。|8/8/8/7|
|[2610.22369](https://arxiv.org/abs/2610.22369)|SoftCache: Adaptive Step Size Caching for Diffusion Transformers|2026-10-16 01:59:34+08:00|other|SoftCache 将缓存余量转为可变步长并外推残差，在高加速区更好保持扩散基线输出。|8/8/8/7|
|[2610.22370](https://arxiv.org/abs/2610.22370)|Which Tokens to Merge? Diffusion Dynamics for Efficient Image Generation|2026-10-16 01:59:35+08:00|other|DaTMe 用去噪动态和局部结构共同决定token合并，改善高合并率下的图像保真，但实测加速较温和。|8/5/8/8|

## 评分依据与压缩对象

|ID|精度依据|压缩依据|创新依据|复现依据|
|---|---|---|---|---|
|2610.22130|三模型5%预算均优于比较方法但低于full KV|约20×仅KV槽位|局部扰动理论与融合评分结合|公式/伪代码/kernel说明齐全，本轮未跑GPU|
|2610.22137|容量4优于随机合并6.2点|6→4仅专家池而非主干|兼容路由与成对SVD合并|方法明确，本轮未训练持续学习模型|
|2610.22143|板上保留92.8% mIoU，仍明显下降|INT8/INT16混合，整模字节未报告|固定工作量部署与校准结合|本轮Qwen实跑与6项小张量检查，FPGA未复现|
|2610.22178|同权重历史显著减少振荡|历史表示压缩，未给整模倍率|register与动作专家复用结合|公开数据/权重/代码，仍需机器人与训练资源|
|2610.22179|loss基本一致且存储无损|峰值节省23.8–25.5%，远小于多倍整模|有界指数码与训练算子/分配器结合|细节充分，GPU实现未本轮复跑|
|2610.22184|实机任务有强提升但每项n=10|无参数倍率，主要接口与专家整合|全身抓握到无特权学生链路|需机器人与仿真管线，本轮未运行|
|2610.22196|宏平均+7.84，部分优势仅0.01点|3B active不等于3B存储|状态链OPD与归因chunk奖励|接口与超参公开但系统/算力较重|
|2610.22217|8B均分+5.83但4B有单项回退|4→1专家份数，单学生尺寸不变|教师有技能学生无技能的非对称监督|数据/训练框架明确，本轮未跑A800|
|2610.22236|均值高但专长有回退且精度混杂|2→1模型，FP32磁盘并不自动节省|行为分布选择与闭式蒸馏|方程/数据/超参完整，未本轮执行|
|2610.22240|学生60.2但教师63.2|27B→9B约3×参数而非系统成本|奖励缺口门控及衰减教师指导|框架明确但动态检索与judge影响复跑|
|2610.22256|存储无损、梯度仅舍入差异|90%稀疏payload约6.38×但模型总显存较小收益|GPU位图布局与符号位/反向融合|kernel与公式清楚，未本轮GPU测试|
|2610.22311|API-free仅下降0.15|2.43×去噪，非缓存/权重倍率|视锥软先验与可执行块路由|参数和kernel说明充分，需H200/生成堆栈|
|2610.22340|原框架任务提升明确，蒸馏独立量化证据有限|未报告可靠学生加速/参数比|自play世界模型MPC到闭环策略|多阶段机器人流程，本轮无运行|
|2610.22347|VBench接近/略高但近似生成|短视频实测1.58×而非2.38×|token接受后KV保留/clean刷新|验证器与阈值明确，GPU未跑|
|2610.22358|1–2NFE接近/超过匹配10NFE教师|10→1–2计算评估，实际51.6ms有条件|多headPDD与共享历史/校准结合|方法设置详细，本轮未跑时序训练|
|2610.22369|匹配速度四项保真指标改善但非无损|3.79–6.91×计算加速非权重倍率|缓存headroom驱动非网格跳步|有参数/算法/同seed对照，本轮未跑|
|2610.22370|r=.5 FID接近base且强于CFG|50%token合并仅1.15×实际加速|时间/空间双信号与局部anchor|步骤和表格充分，本轮无GPU重跑|

## 全量召回与覆盖审计

本轮新抓五分类10入口，共11页、7614次条目出现，按去版本ID去重为4883篇。LG recent总2059，使用skip=0/2000覆盖2000+59；其余均show=2000一次覆盖。各页总数与每个h3日期/新稿/交叉/替换分组实计逐一匹配。new包含new submissions和cross submissions，并读取replacement；recent覆盖10月16/15/14/12/9日，跨越窗口起点。实际页面证据如下。

|官方入口（参数即实际覆盖）|页面总数|本页实际数|分组/日期|
|---|---:|---:|---|
|[cs.LG new skip=0](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)|467|467|Showing new listings for Friday, 16 October 2026；New submissions (showing 166 of 166 entries)；Cross submissions (showing 140 of 140 entries)；Replacement submissions (showing 161 of 161 entries)|
|[cs.LG recent skip=0](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|2059|2000|Fri, 16 Oct 2026 (showing 306 of 306 entries )；Thu, 15 Oct 2026 (showing 305 of 305 entries )；Wed, 14 Oct 2026 (showing 862 of 862 entries )；Mon, 12 Oct 2026 (showing 262 of 262 entries )；Fri, 9 Oct 2026 (showing first 265 of 324 entries )|
|[cs.LG recent skip=2000](https://arxiv.org/list/cs.LG/recent?show=2000&skip=2000)|2059|59|Fri, 9 Oct 2026 (continued, showing last 59 of 324 entries )|
|[cs.CL new skip=0](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)|267|267|Showing new listings for Friday, 16 October 2026；New submissions (showing 105 of 105 entries)；Cross submissions (showing 72 of 72 entries)；Replacement submissions (showing 90 of 90 entries)|
|[cs.CL recent skip=0](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|1004|1004|Fri, 16 Oct 2026 (showing 177 of 177 entries )；Thu, 15 Oct 2026 (showing 182 of 182 entries )；Wed, 14 Oct 2026 (showing 385 of 385 entries )；Mon, 12 Oct 2026 (showing 116 of 116 entries )；Fri, 9 Oct 2026 (showing 144 of 144 entries )|
|[cs.CV new skip=0](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)|253|253|Showing new listings for Friday, 16 October 2026；New submissions (showing 135 of 135 entries)；Cross submissions (showing 30 of 30 entries)；Replacement submissions (showing 88 of 88 entries)|
|[cs.CV recent skip=0](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0)|1147|1147|Fri, 16 Oct 2026 (showing 165 of 165 entries )；Thu, 15 Oct 2026 (showing 143 of 143 entries )；Wed, 14 Oct 2026 (showing 479 of 479 entries )；Mon, 12 Oct 2026 (showing 153 of 153 entries )；Fri, 9 Oct 2026 (showing 207 of 207 entries )|
|[cs.AI new skip=0](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)|453|453|Showing new listings for Friday, 16 October 2026；New submissions (showing 132 of 132 entries)；Cross submissions (showing 154 of 154 entries)；Replacement submissions (showing 167 of 167 entries)|
|[cs.AI recent skip=0](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0)|1881|1881|Fri, 16 Oct 2026 (showing 286 of 286 entries )；Thu, 15 Oct 2026 (showing 280 of 280 entries )；Wed, 14 Oct 2026 (showing 852 of 852 entries )；Mon, 12 Oct 2026 (showing 161 of 161 entries )；Fri, 9 Oct 2026 (showing 302 of 302 entries )|
|[cs.AR new skip=0](https://arxiv.org/list/cs.AR/new?show=2000&skip=0)|19|19|Showing new listings for Friday, 16 October 2026；New submissions (showing 6 of 6 entries)；Cross submissions (showing 6 of 6 entries)；Replacement submissions (showing 7 of 7 entries)|
|[cs.AR recent skip=0](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0)|64|64|Fri, 16 Oct 2026 (showing 12 of 12 entries )；Thu, 15 Oct 2026 (showing 10 of 10 entries )；Wed, 14 Oct 2026 (showing 23 of 23 entries )；Mon, 12 Oct 2026 (showing 10 of 10 entries )；Fri, 9 Oct 2026 (showing 9 of 9 entries )|

4883份官方abs原始HTML从既有证据缓存复制，本轮重新解析标题、摘要、主/交叉分类和Submission history；没有把旧列表当作本轮列表。4767篇先按v1时间排除窗口外记录，116篇窗口摘要全部逐项语义复核，21篇进一步读官方HTML v1方法/实验，17篇纳入。随后本轮重新下载116篇窗口abs和2篇相邻日对照，全部四字段与缓存一致；并非声称4883篇均本轮网络重抓或逐篇全文精读。关键词只用于二次复核，命中记录见metadata/2026-10/keyword_audit.json；116条判定见semantic_review.json。

相邻日阳性对照：[2610.22120](https://arxiv.org/abs/2610.22120) v1为10月15日23:59:08；紧随的窗口首条[2610.22122](https://arxiv.org/abs/2610.22122)为10月16日00:00:11；最新可见[2610.22372](https://arxiv.org/abs/2610.22372)为10月16日01:59:59，均北京时间。对照证明解析能跨自然日边界，不能证明尚未公告日期没有投稿。

全文可得，使用10月18日保存的官方HTML v1并在本轮重新阅读；不声称今天再次下载全部全文。FALCON机制在本轮实跑，其他论文数字均来自论文。未使用第三方结果替代列表召回或官方v1时间。

## 历史去重审计

fetch --prune origin成功后，逐一执行全部48个远端origin/feature/arxiv-daily-*的ls-tree，并读取每个存在的metadata/**/papers_index.json交叉验证，得到567个真实tech_analysis.md规范ID。metadata-only的2607.27951、2607.28410、2607.28457未计完成。运行前远端不存在当日分支，无续跑分支被误归历史。

相关条目跨列表出现44次，跨日期/分类/关键词规范化后17个独立ID，再与567历史ID相交为0。重复ID与来源分支：空集；没有将检索失败写为零，也没有把仅有metadata的条目当作精读完成。

最终新增ID：2610.22130, 2610.22137, 2610.22143, 2610.22178, 2610.22179, 2610.22184, 2610.22196, 2610.22217, 2610.22236, 2610.22240, 2610.22256, 2610.22311, 2610.22340, 2610.22347, 2610.22358, 2610.22369, 2610.22370。

扫描分支名及精确SHA全部保存在metadata/2026-10/dedup_audit.json；提交前ls-remote证实48分支全集和main均与fetch快照一致。

## 边界论文排除复核

|ID|结论|
|---|---|
|2610.22169 Lexical Reference Frames|解释方法需通过剩余层读出；早退比例未建立净计算节省，暂不作压缩成果。|
|2610.22221 Audio-to-vision damping|跨模态知识迁移，没有模型/计算缩减目标，蒸馏词命中不够。|
|2610.22328 ACEdit|对既有4步学生改善多轮编辑质量；没有新增参数或步数压缩。|
|2610.22353 MirrorMoE|保持相同专家执行数，功能性低权重抑制不是实际剪枝。|

## Qwen3-0.6B 实际验证

复现目录：scripts/quantization/2610.22143/，含README、demo.py、results.json、tests.json。实际在CPU运行第0层MLP down_proj的每张量W8A8二次幂PTQ，4×128校准和2×128评估；BF16模型完整前向，总18.785秒。六项已知答案/边界小张量检查、导入与py_compile通过。

原论文非负裁剪在Qwen上两样本KL为0.033270/0.020533；有符号适配与无裁剪INT8为0.002777/0.001103。校准约49.61%输入为负且没有超32离群值，说明论文前提不满足，本轮验证的是转移边界，不是声称其裁剪在Qwen有收益。INT8单矩阵payload从6291456到3145728bytes；实验保留浮点对照及临时反量化权重，不能将其称为进程内存减少2倍或整数推理加速。

尚未完成：FALCON原FlashOcc/Occ3D、Vitis bit-exact和KR260硬件时限验证；缺目标硬件/数据/原模型及部署环境。未做整模INT8、标准语料PPL、多seed及其他16篇GPU/机器人训练复跑。论文六节精读和本轮数值转移代码均已完成，原实验边界明确记录。

## 分支独立快照

严格从origin/main abfe8f2767d8bf881d586718ab4db33fc576be6a创建feature/arxiv-daily-2026-10-19 linked worktree。原工作树未切换分支、未stash、未暂存或覆盖用户文件。

main仅带历史07-28日报，本分支已删除；papers保留README及本次17篇，reports保留README及本日报，scripts保留README及本次唯一量化复现，metadata保留README及2026-10本次索引、CSV和审计，没有累计历史条目。论文目录与索引ID集合相同；复现ID集合等于新增集合的quantization子集。新增与历史交集为空。

最终commit/push、单提交与远端SHA验证结果记录在本次自动化持久运行证据中，并在任务最终回复给出，避免将尚未发生的推送写成已成功。日报不嵌入自身commit SHA以避免自引用。

生成时间：2026-10-19T01:21:17.035309+08:00。本地完整原始证据：/Users/lipengcheng/.codex/automations/arxiv/runs/2026-10-19。
