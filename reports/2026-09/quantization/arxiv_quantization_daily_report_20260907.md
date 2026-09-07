# arXiv 模型压缩与量化日报 — 2026-09-07

运行日：2026-09-08；生成时间：2026-09-08T01:26:43+08:00。

**固定检索窗口：北京时间2026-09-05、09-06、09-07三个完整自然日。窗口相关5篇，历史重复0篇，新增5篇，其中量化1篇。**

09-06、09-07只能表述为“截至运行时 arXiv 官方网页未检出”，不代表后台投稿最终为零。此时列表最新公告为09-07；后续依靠三日窗口回查公告延迟。

## 1. 官方列表全量覆盖与提交时间

五分类new/recent共10个页面均使用show=2000，声明数与实际条目数完全相等，均小于2000；覆盖序号1至各页总数，无遗漏的后续分页。new submissions和cross-lists均检查，replacements也保留核验。跨日期、分类及关键词按去版本ID合并为3,118篇，不以关键词限定召回。未调用export.arxiv.org API或submittedDate查询。

| 分类 | new声明=实际 | 新稿/交叉/替换分组 | recent声明=实际 | recent日期与分组计数 |
|---|---:|---|---:|---|
| cs.LG | [228](https://arxiv.org/list/cs.LG/new?show=2000) | New submissions (showing 79 of 79 entries)；Cross submissions (showing 58 of 58 entries)；Replacement submissions (showing 91 of 91 entries) | [1002](https://arxiv.org/list/cs.LG/recent?show=2000) | Mon, 7 Sep 2026 (showing 137 of 137 entries )；Fri, 4 Sep 2026 (showing 168 of 168 entries )；Thu, 3 Sep 2026 (showing 159 of 159 entries )；Wed, 2 Sep 2026 (showing 202 of 202 entries )；Tue, 1 Sep 2026 (showing 336 of 336 entries ) |
| cs.CL | [151](https://arxiv.org/list/cs.CL/new?show=2000) | New submissions (showing 63 of 63 entries)；Cross submissions (showing 35 of 35 entries)；Replacement submissions (showing 53 of 53 entries) | [797](https://arxiv.org/list/cs.CL/recent?show=2000) | Mon, 7 Sep 2026 (showing 98 of 98 entries )；Fri, 4 Sep 2026 (showing 115 of 115 entries )；Thu, 3 Sep 2026 (showing 101 of 101 entries )；Wed, 2 Sep 2026 (showing 185 of 185 entries )；Tue, 1 Sep 2026 (showing 298 of 298 entries ) |
| cs.CV | [174](https://arxiv.org/list/cs.CV/new?show=2000) | New submissions (showing 81 of 81 entries)；Cross submissions (showing 29 of 29 entries)；Replacement submissions (showing 64 of 64 entries) | [826](https://arxiv.org/list/cs.CV/recent?show=2000) | Mon, 7 Sep 2026 (showing 110 of 110 entries )；Fri, 4 Sep 2026 (showing 112 of 112 entries )；Thu, 3 Sep 2026 (showing 136 of 136 entries )；Wed, 2 Sep 2026 (showing 152 of 152 entries )；Tue, 1 Sep 2026 (showing 316 of 316 entries ) |
| cs.AI | [298](https://arxiv.org/list/cs.AI/new?show=2000) | New submissions (showing 106 of 106 entries)；Cross submissions (showing 99 of 99 entries)；Replacement submissions (showing 93 of 93 entries) | [1265](https://arxiv.org/list/cs.AI/recent?show=2000) | Mon, 7 Sep 2026 (showing 205 of 205 entries )；Fri, 4 Sep 2026 (showing 165 of 165 entries )；Thu, 3 Sep 2026 (showing 162 of 162 entries )；Wed, 2 Sep 2026 (showing 309 of 309 entries )；Tue, 1 Sep 2026 (showing 424 of 424 entries ) |
| cs.AR | [19](https://arxiv.org/list/cs.AR/new?show=2000) | New submissions (showing 12 of 12 entries)；Cross submissions (showing 2 of 2 entries)；Replacement submissions (showing 5 of 5 entries) | [55](https://arxiv.org/list/cs.AR/recent?show=2000) | Mon, 7 Sep 2026 (showing 14 of 14 entries )；Fri, 4 Sep 2026 (showing 9 of 9 entries )；Thu, 3 Sep 2026 (showing 10 of 10 entries )；Wed, 2 Sep 2026 (showing 12 of 12 entries )；Tue, 1 Sep 2026 (showing 10 of 10 entries ) |

全部3,118条官方abs的标题、摘要、分类及Submission history v1读取解析成功；其中2,108条窗口外旧稿复用09-07官方abs缓存，复用前确认当前列表标题一致、已有v1明确早于窗口。缓存来源单独记录，未把它们称为本次全部重新下载。36条窗口内记录均有本次官方abs证据，逐篇阅读完整标题和摘要，再按语义判断；本次没有人工重新精读全部窗口外旧稿。

窗口外相邻日期阳性对照：北京时间09-04可见428条。例：[2609.05303](https://arxiv.org/abs/2609.05303)的v1为09-04 15:56:10 UTC / 23:56:10北京时间；紧接的[2609.05309](https://arxiv.org/abs/2609.05309)为16:02:20 UTC / 09-05 00:02:20北京时间。两者虽同属09-07公告，只有后者进入窗口。归属采用v1真实时间，公告日不替代提交日。

## 2. 逐日计数与历史去重

原始相关数指三日跨分类合并规范ID之后、历史排除之前的相关数。先语义判定，再与历史真实精读集合比较。

| v1北京时间日期 | 全主题可见 | 原始相关 | 历史重复 | 新增 |
|---|---:|---:|---:|---:|
| 2026-09-05 | 36 | 5 | 0 | 5 |
| 2026-09-06 | 0 | 0 | 0 | 0 |
| 2026-09-07 | 0 | 0 | 0 | 0 |
| 合计 | 36 | 5 | 0 | 5 |

git fetch --prune origin成功后，对全部38个远端历史日更分支逐一执行git ls-tree -r --name-only，从真实papers/**/<id>/tech_analysis.md得到522个规范ID。各分支metadata/**/papers_index.json另得525个ID；仅有metadata的2607.27951、2607.28410、2607.28457不计完成。git ls-remote核验远端分支全集和逐分支SHA与本地枚举完全相等。当前09-08分支在创建前不存在，不混入历史。

**重复ID与来源分支：无。最终新增ID：2609.05309、2609.05320、2609.05334、2609.05351、2609.05363。与历史522个ID交集为空。**

扫描分支：

- `origin/feature/arxiv-daily-2026-07-29`
- `origin/feature/arxiv-daily-2026-07-30`
- `origin/feature/arxiv-daily-2026-07-31`
- `origin/feature/arxiv-daily-2026-08-01`
- `origin/feature/arxiv-daily-2026-08-02`
- `origin/feature/arxiv-daily-2026-08-03`
- `origin/feature/arxiv-daily-2026-08-04`
- `origin/feature/arxiv-daily-2026-08-05`
- `origin/feature/arxiv-daily-2026-08-06`
- `origin/feature/arxiv-daily-2026-08-07`
- `origin/feature/arxiv-daily-2026-08-08`
- `origin/feature/arxiv-daily-2026-08-10`
- `origin/feature/arxiv-daily-2026-08-12`
- `origin/feature/arxiv-daily-2026-08-14`
- `origin/feature/arxiv-daily-2026-08-15`
- `origin/feature/arxiv-daily-2026-08-16`
- `origin/feature/arxiv-daily-2026-08-17`
- `origin/feature/arxiv-daily-2026-08-18`
- `origin/feature/arxiv-daily-2026-08-19`
- `origin/feature/arxiv-daily-2026-08-20`
- `origin/feature/arxiv-daily-2026-08-21`
- `origin/feature/arxiv-daily-2026-08-22`
- `origin/feature/arxiv-daily-2026-08-23`
- `origin/feature/arxiv-daily-2026-08-24`
- `origin/feature/arxiv-daily-2026-08-25`
- `origin/feature/arxiv-daily-2026-08-26`
- `origin/feature/arxiv-daily-2026-08-27`
- `origin/feature/arxiv-daily-2026-08-28`
- `origin/feature/arxiv-daily-2026-08-29`
- `origin/feature/arxiv-daily-2026-08-30`
- `origin/feature/arxiv-daily-2026-08-31`
- `origin/feature/arxiv-daily-2026-09-01`
- `origin/feature/arxiv-daily-2026-09-02`
- `origin/feature/arxiv-daily-2026-09-03`
- `origin/feature/arxiv-daily-2026-09-04`
- `origin/feature/arxiv-daily-2026-09-05`
- `origin/feature/arxiv-daily-2026-09-06`
- `origin/feature/arxiv-daily-2026-09-07`

## 3. 新增论文完整表

| ID与完整标题 | v1 UTC / 北京时间 | 类别与一句话结论 | 六节精读 |
|---|---|---|---|
| [2609.05309 — How Does mHC Use Its Residual Streams? Selective Routing and Near-Identity Mixing](https://arxiv.org/abs/2609.05309) | 2026-09-04T16:02:20Z / 2026-09-05T00:02:20+08:00 | pruning：四流路由四留三或将后半层混合器改单位阵仅带来较小质量变化，但没有整机压缩倍率。 | [分析](../../../papers/2026-09/pruning/2609.05309/tech_analysis.md) |
| [2609.05320 — Adaptive Gated Deepfake Detection for Low-Resolution and Resource-Constrained Environments](https://arxiv.org/abs/2609.05320) | 2026-09-04T16:14:57Z / 2026-09-05T00:14:57+08:00 | other：质量门控动态选择双分支深度，Celeb-DF AUC 0.9370，但FF++仅0.5163。 | [分析](../../../papers/2026-09/other/2609.05320/tech_analysis.md) |
| [2609.05334 — Lightweight Vision Transformer Compression for On-Device Plant Disease Detection in Resource-Constrained Agricultural Field Conditions](https://arxiv.org/abs/2609.05334) | 2026-09-04T16:40:06Z / 2026-09-05T00:40:06+08:00 | quantization：文件327.42→6.01MB约54.5倍，但同尺寸直接训练94.87%与完整流水线均值95.13%接近。 | [分析](../../../papers/2026-09/quantization/2609.05334/tech_analysis.md) |
| [2609.05351 — MEOX: Compact Multimodal Mixture-of-Experts for Earth Observation](https://arxiv.org/abs/2609.05351) | 2026-09-04T16:59:36Z / 2026-09-05T00:59:36+08:00 | other：共享专家投影加rank-8残差将编码器控制在2.939M参数，高分辨率时算量优势消失。 | [分析](../../../papers/2026-09/other/2609.05351/tech_analysis.md) |
| [2609.05363 — Distill Globally, Adapt Locally: Reasoning Distillation and Product-Type Test-Time Training for Scalable Trade-Up Recommendation](https://arxiv.org/abs/2609.05363) | 2026-09-04T17:08:50Z / 2026-09-05T01:08:50+08:00 | knowledge_distillation：LLM理由蒸馏到非生成学生，AUC0.924；品类少样本适配后0.941，线上无需生成教师。 | [分析](../../../papers/2026-09/knowledge_distillation/2609.05363/tech_analysis.md) |

## 4. 四项评分及依据

分数均为1–10的主观证据评分，不是指标或倍率。参数数、文件体积、算量、延迟和服务成本分别解读。

| ID | 精度效果 | 压缩倍率/资源 | 创新性 | 可复现性 |
|---|---|---|---|---|
| 2609.05309 | 8/10：读top-3均分−0.38点，后半混合器替换+0.04点；PPL仍有代价。 | 3/10：局部路由支持减少25%；无参数/显存/延迟实测倍率。 | 8/10：保持尺度的路由干预结合深度分解。 | 6/10：C4和六任务协议清楚，284B模型本次未运行。 |
| 2609.05320 | 4/10：Celeb-DF弱于full-only和ShuffleNet，FF++近随机。 | 3/10：有早退与0.14ms作者报告，缺少匹配full路径速度/体积倍率。 | 6/10：质量规则监督与RGB/DCT多出口结合。 | 6/10：代码入口和训练设置可用，阈值及计时仍需核验。 |
| 2609.05334 | 6/10：跨村庄/相机OOD，但流水线波动大且表文存在冲突。 | 8/10：54.5倍为文件体积；量化CPU无显著加速。 | 6/10：曲率预算与注意力KD/动态PTQ组合。 | 5/10：Qwen真实运行通过；原视觉数据、精确配置和目标硬件复现未完成。 |
| 2609.05351 | 7/10：Cashew64.42 mIoU、EuroSAT90.56 AA，其他任务仍落后。 | 8/10：与CSMoE参数比约87，非同模型受控压缩；224像素51.477G。 | 7/10：共享参数、低秩私有残差及有效性加权模态融合。 | 7/10：开源实现/数据与协议清楚，预训练166.9h MIG，本次未重训。 |
| 2609.05363 | 8/10：有bootstrap和同928条人工监督控制；品类内AUC也改善。 | 8/10：约5000倍速度、10000倍估计成本是特定服务比较，非权重倍率。 | 7/10：四类理由监督与品类适配分工，含多个匹配控制。 | 5/10：损失/LoRA配置清晰；黑盒教师与人工支持限制精确复现。 |

重点复核发现：H-BAC论文部分正文/表格数值与延迟状态互相冲突，采用主表与结论交叉一致的数据并降低可信度；AdaGate-DF的FF++高准确率主要反映类别不平衡；MEOX在224像素下算量增长而非普遍低成本；Trade-up的速度/成本巨大倍率不是权重压缩倍数；mHC只测局部路由/混合器干预，未证明整机收益。

## 5. 语义复核与边界排除

复核词：quantization, quantize, quantise, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, distill, teacher/student, KV cache compression, mixed precision, GPTQ, AWQ, low-rank, binary, ternary, FP4, INT4, FP8, INT8, token pruning, token merging, early exit, weight sharing。关键词只用于复核和排序；例如mHC与MEOX按路由/共享投影语义纳入，不能只搜quantization；普通LoRA微调、输入压缩、agent记忆摘要、数据合成和应用层输出token减少不自动等同模型压缩。

36篇窗口摘要逐篇决策如下；5篇入选读官方全文，其中AdaGate-DF HTML404改读官方8页PDF并渲染核对表II/III。其余31篇排除依据来自官方摘要，无伪造全文结论。

| 排除ID | 语义理由 |
|---|---|
| [2609.05314](https://arxiv.org/abs/2609.05314) | HVAC应用综述，不是压缩方法/模型内部计算削减。 |
| [2609.05318](https://arxiv.org/abs/2609.05318) | 网络化学习的统计聚合速率理论，不是模型压缩。 |
| [2609.05323](https://arxiv.org/abs/2609.05323) | 压缩多焦显微输入与I/O，不压缩模型。 |
| [2609.05324](https://arxiv.org/abs/2609.05324) | 机器人数据集与评测，未压缩VLA。 |
| [2609.05327](https://arxiv.org/abs/2609.05327) | LLM生成量子电路变量排序启发式，压缩对象为电路，不是LLM。 |
| [2609.05328](https://arxiv.org/abs/2609.05328) | 分类图的连续嵌入流生成，非模型低比特/剪枝。 |
| [2609.05333](https://arxiv.org/abs/2609.05333) | 词形语境表示测量工具，低维可视化非压缩部署。 |
| [2609.05335](https://arxiv.org/abs/2609.05335) | 漏洞历史规则与检测流水线，非模型压缩。 |
| [2609.05337](https://arxiv.org/abs/2609.05337) | 双摆周期轨道的Hessian数值延拓，非模型剪枝。 |
| [2609.05339](https://arxiv.org/abs/2609.05339) | 自然语言笔记/知识图谱的agent记忆迁移，非权重或KV缓存压缩。 |
| [2609.05346](https://arxiv.org/abs/2609.05346) | 学生指真实大学生，非知识蒸馏。 |
| [2609.05364](https://arxiv.org/abs/2609.05364) | 性能建模软件与设计文档，非压缩算法。 |
| [2609.05369](https://arxiv.org/abs/2609.05369) | 任务图/程序记忆增强VLA，不削减模型表示。 |
| [2609.05370](https://arxiv.org/abs/2609.05370) | 反编译可靠性评估，不是模型压缩。 |
| [2609.05374](https://arxiv.org/abs/2609.05374) | GUI+CLI环境和轨迹后训练，推理步数/输出token减少不等于模型内部压缩。 |
| [2609.05376](https://arxiv.org/abs/2609.05376) | 视觉干扰鲁棒性、增强和注意力正则，非压缩。 |
| [2609.05381](https://arxiv.org/abs/2609.05381) | 分子数值逐字检索/记忆审计，非模型压缩。 |
| [2609.05382](https://arxiv.org/abs/2609.05382) | 镜面几何条件增强新视角生成，非稀疏化或缓存压缩。 |
| [2609.05385](https://arxiv.org/abs/2609.05385) | LLM解释必要性/充分性测量，非压缩。 |
| [2609.05388](https://arxiv.org/abs/2609.05388) | 逻辑规则归纳与验证，非模型压缩。 |
| [2609.05395](https://arxiv.org/abs/2609.05395) | 工具调用数据合成及GRPO；小模型接近大模型不构成教师蒸馏或模型压缩方法。 |
| [2609.05396](https://arxiv.org/abs/2609.05396) | 无线信号GAN数据生成，非模型压缩。 |
| [2609.05397](https://arxiv.org/abs/2609.05397) | 标定几何约束跨图注意力以提高深度一致性，未建立压缩目标/资源削减。 |
| [2609.05399](https://arxiv.org/abs/2609.05399) | 可解释性立场与评估议程，非压缩。 |
| [2609.05400](https://arxiv.org/abs/2609.05400) | 冻结7.18M模型加约1%LoRA，减少可训练参数而增加部署参数，未压缩原模型。 |
| [2609.05401](https://arxiv.org/abs/2609.05401) | 视觉语言奖励模型释义鲁棒性基准，非压缩。 |
| [2609.05403](https://arxiv.org/abs/2609.05403) | 联邦学习梯度个性化与隐私，非模型压缩。 |
| [2609.05404](https://arxiv.org/abs/2609.05404) | 扩散模型交互艺术装置，非压缩。 |
| [2609.05405](https://arxiv.org/abs/2609.05405) | 可穿戴健康推理基准，非压缩。 |
| [2609.05415](https://arxiv.org/abs/2609.05415) | 拓扑感知运动生成，非模型压缩。 |
| [2609.05416](https://arxiv.org/abs/2609.05416) | 多视图条件的3D对象生成，不是3DGS模型压缩。 |

## 6. Qwen3-0.6B真实代码运行

本次唯一新增量化论文2609.05334的[复现目录](../../../scripts/quantization/2609.05334/README.md)包含demo.py和两份原始结果JSON。本地Qwen3-0.6B真实checkpoint、CPU、PyTorch2.8.0、Transformers4.57.6。

- 完整28层197个Linear执行native动态INT8：独立短文本CE 6.347614→7.014916，相对logits L2误差0.352920；估计逻辑张量payload约1.9565倍缩减，非实测文件倍率。单次前向0.498→0.917秒，没有加速证据。
- H-BAC在真实CE上计算第0/14块Hessian，K=10/参数组，直接曲率分配0.760276/0.239724；GQA/SwiGLU掩码和真实恢复更新完成。4层迁移学生经一步注意力KD的独立短文本CE15.730988→15.584406，INT8后16.156311，仍严重退化。
- 语法、导入、已知二次函数Hessian trace、分配规则、GQA/SwiGLU掩码、原生INT8、全模型前向及梯度更新均通过。记录qnnpack忽略reduce_range警告，性能数值仅单次健全性检查。

**完整论文复现0/1，真实量化迁移运行1/1。** 未取得农业原始数据/视觉checkpoint，未执行15轮视觉KD、全块剪枝、静态PTQ、结构缩形、Core ML导出或手机基准；Qwen的因果任务/GQA/SwiGLU不同于ViT。其他4篇未本机复现，精读实验全部标为作者报告。

## 7. 独立快照与Git验证

分支feature/arxiv-daily-2026-09-08在隔离linked worktree严格从本次origin/main abfe8f2767d8bf881d586718ab4db33fc576be6a创建，未继承任何feature成果。已删除main自带07-28日报；papers仅README和5篇本次精读，reports仅README和本日报，scripts仅README和本次1个复现目录，metadata仅README和2026-09的5篇索引/CSV。全部新增论文的实际提交月份为2026-09，没有跨月累计。

原工作树3处修改和3个未跟踪项均以逐文件SHA256及完整status保护。提交前检查JSON/CSV/六节/相对链接、实际目录ID与新集合一致、窗口日期、历史零交集、git diff --check及main基线；提交后要求origin/main..HEAD仅本次1提交，并以ls-remote/log/merge-base核验远端SHA与基线。推送结果见最终运行回执，不预写未发生的远端验证为成功。

检索页面及详情读取无阻塞。剩余限制为上节原论文完整复现、公开页面公告延迟与量化短样本验证的证据边界。
