# arXiv 模型压缩精读日报 — 2026-11-08

运行日：2026-11-09，Asia/Shanghai。检索窗口固定为 **2026-11-06 00:00:00 至 2026-11-08 23:59:59（北京时间）**，主日报日期11-08。生成时间：2026-11-09T01:18:05.284164+08:00。

窗口公开相关 **9篇**，历史重复 **0篇**，本次新增 **9篇**。按类别为量化2、剪枝2、知识蒸馏3、其他2。这里的知识蒸馏包含策略/跨模态转移；没有测得单模型压缩率的工作明确标注，不将小模型训练或普通推测解码自动算作压缩。

## 1. 三日召回与去重审计

| 实际v1提交日（北京时间） | 相关列表出现次数（跨入口未去重） | 规范ID相关数 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 11-06 | 28 | 9 | 0 | 9 |
| 11-07 | 0 | 0* | 0 | 0 |
| 11-08 | 0 | 0* | 0 | 0 |

\* **截至运行时 arXiv 官方网页未检出**，不是断言该日没有真实投稿。最新公开列表为11-06；后续仍以三天窗口回查公告延迟。没有使用arXiv API，也没有用公告日替代v1时间。

fetch后逐一对 **53个** `origin/feature/arxiv-daily-*` 历史分支执行ls-tree，按真实 `papers/**/<id>/tech_analysis.md` 识别并去版本后缀，得到 **612个** 历史已分析ID；逐分支读取papers_index.json交叉核验。metadata-only的2607.27951、2607.28410、2607.28457不算已完成。当日远端分支开始时不存在，本地新建，未把本次状态算作历史。

本次相关ID在列表跨分类/入口出现28次，先合并成9个规范ID，再与612个历史ID比较：**排除的重复ID与来源分支：无**。最终新增集合：2611.08453, 2611.08413, 2611.08376, 2611.08363, 2611.08290, 2611.08275, 2611.08245, 2611.08236, 2611.08216。两集合交集为空。53个来源分支及精确SHA、覆盖证据、逐篇排除理由见[去重审计](../../../metadata/2026-11/dedup_audit.json)。完整逐分支树及metadata核验原始证据保存在自动化本轮审计目录。

## 2. 官方分类页覆盖

每个入口使用`show=2000&skip=0`，页面总数均小于2000，因此无需后续页；实际dt条目数与页面总数相等，各日期/新投稿/cross-list/replacement分组实计也匹配。`new`同时检查新投稿和cross-lists，并额外解析replacements。`recent`全部日期分组为11-06、11-05、11-04、11-03、11-02。

| 分类 | new总数/实计 | new 新投稿/交叉/替换 | recent总数/实计 | recent逐日期条目数（06/05/04/03/02） |
|---|---:|---|---:|---|
| cs.LG | [ 417/417 ](https://arxiv.org/list/cs.LG/new?show=2000&skip=0) | 145 / 79 / 193 | [ 1458/1458 ](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0) | 224 / 214 / 252 / 570 / 198 |
| cs.CL | [ 160/160 ](https://arxiv.org/list/cs.CL/new?show=2000&skip=0) | 62 / 32 / 66 | [ 606/606 ](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0) | 94 / 90 / 85 / 251 / 86 |
| cs.CV | [ 258/258 ](https://arxiv.org/list/cs.CV/new?show=2000&skip=0) | 107 / 31 / 120 | [ 943/943 ](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0) | 138 / 148 / 160 / 395 / 102 |
| cs.AI | [ 361/361 ](https://arxiv.org/list/cs.AI/new?show=2000&skip=0) | 75 / 123 / 163 | [ 1374/1374 ](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0) | 198 / 217 / 252 / 521 / 186 |
| cs.AR | [ 16/16 ](https://arxiv.org/list/cs.AR/new?show=2000&skip=0) | 6 / 5 / 5 | [ 65/65 ](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0) | 11 / 12 / 8 / 32 / 2 |

十入口合计5658次出现，合并3729 ID。全部官方abs解析标题、摘要、分类及v1；按v1排除窗外3638条，窗口内91条逐篇阅读标题摘要作语义判断，9篇及边界VFlash进一步读官方全文。未宣称人工精读窗外3638篇全文。关键词仅作复核：quantization/quantize/low-bit/compress/pruning/sparsity/distill/teacher/student/KV/mixed precision/GPTQ/AWQ等，不构成召回门槛。

本轮新抓92个abs（91窗口+1邻日对照），与可校验缓存的标题、摘要、分类、v1四字段全部一致，错误0。相邻阳性对照[2611.08200](https://arxiv.org/abs/2611.08200) v1为11-05 23:54:05北京时间；最早窗内[2611.08216](https://arxiv.org/abs/2611.08216)为11-06 00:04:31，最晚窗内记录为02:59:42。该边界说明UTC11-05晚投稿需归入本地11-06，不能按ID月份之外的公告日期筛选。

边界排除示例：VFlash保留target并新增drafter、使用几何标注做并行解码，非模型压缩；SpecCTMC属于无损采样调度；LAQ压缩外部检索embedding而非模型参数/激活/KV；普通LoRA优化、SAE解释、LLM标签清洗和few-step模型RL后训练均不因关键词自动纳入。完整91条决定见审计JSON。

## 3. 全部新增论文

日期与时间均为实际v1北京时间；链接指向官方提交历史。精读在`papers/2026-11/<category>/<id>/tech_analysis.md`。

| ID / v1时间 | 完整标题 | 类别 | 一句话结论 |
|---|---|---|---|
| [2611.08453](https://arxiv.org/abs/2611.08453) / 11-06 02:47:05 | Unpacking the Compute Efficiency of Strong-to-Weak OPD against GRPO | knowledge_distillation | 外部强教师不必然提高每FLOP学习效率；同源专家蒸馏的价值在于多域能力合并，而非孤立计算50倍蒸馏阶段节省。 |
| [2611.08413](https://arxiv.org/abs/2611.08413) / 11-06 02:17:29 | T3R: Training-Free Two-Stage Token Refinement Towards Efficient and Robust VLA Models | pruning | T3R在解码前剪除场景相机冗余token，再用任务级显著性修复注意力；85%场景token减少只带来1.16倍实测VLA调用加速。 |
| [2611.08376](https://arxiv.org/abs/2611.08376) / 11-06 01:53:49 | Muir: Linear Attention with Sensitivity-Allocated Gating and Matched-Filter Readout | other | Muir按状态更新敏感度分配低秩门控，用匹配滤波读出改善固定容量记忆；节省参数用于加宽FFN，因此不宣称整模型参数缩小。 |
| [2611.08363](https://arxiv.org/abs/2611.08363) / 11-06 01:42:06 | StrataFlux: Memory-Hierarchy-Native Low-Bit LLM Inference | quantization | StrataFlux把低比特常驻底座与按需补充精度分离，拟合被选中通道以补偿遗漏误差；本机验证显示小校准集上的收益明显大于留出集。 |
| [2611.08290](https://arxiv.org/abs/2611.08290) / 11-06 00:53:48 | AutoCompress: Automated Hardware-Guided Model Compression | pruning | AutoCompress把目标硬件、工作负载与推理引擎成本纳入架构搜索，在相同部署预算下优于统一宽度剪枝。 |
| [2611.08275](https://arxiv.org/abs/2611.08275) / 11-06 00:44:24 | Aligning Policy Encoders with a Shape Teacher | knowledge_distillation | 把冻结Point-MAE的3D局部几何特征蒸馏到图像策略encoder，部署时无需3D教师或深度输入，但不缩小原图像策略。 |
| [2611.08245](https://arxiv.org/abs/2611.08245) / 11-06 00:22:55 | Value-oriented policy distillation for interpretable wind farm power control | knowledge_distillation | 用决策价值加权把SAC控制策略蒸馏到透明EBM，降低不平衡费用约82%；目标是可解释控制，未证明参数或延时压缩。 |
| [2611.08236](https://arxiv.org/abs/2611.08236) / 11-06 00:17:48 | Beyond Quadratic Attention: Separable Gaussian Operators for ODE Vision Transformers | other | SSoG用可分离高斯空间算子替代dense attention以减少参数和计算；内存优势取决于基线是否使用融合kernel。 |
| [2611.08216](https://arxiv.org/abs/2611.08216) / 11-06 00:04:31 | ProQuant: Progressive Quantization-aware Training for Edge MLLMs | quantization | ProQuant先用模型自生成标签对齐数据分布，再优先量化视觉敏感层；W4A8 Qwen3-VL-2B均分72.54，距BF16为1.09个百分点。 |

## 4. 四维评分与证据

1–10为本次编辑判断：精度看原论文对照和退化边界；压缩看明确资源分母，缺少实测倍率降分；创新看机制与证据；可复现性看公开细节及本地验证范围。不同任务的分数不代表统一排行榜。

| 论文 | 精度 | 压缩倍率 | 创新性 | 可复现性 | 评分依据 |
|---|---:|---:|---:|---:|---|
| OPD成本审计 | 7 | 3 | 8 | 6 | 精度7：跨尺寸/领域有受控对照，但外部教师常输GRPO；压缩3：同源专家合并不提供单模型字节压缩率；创新8：拆分教师来源与完整训练账本；复现6：目标和FLOP公式清晰，但本次未跑多GPU训练。 |
| T3R | 7 | 7 | 7 | 6 | 精度7：Spatial仅损失1个百分点但单相机退化；压缩7：85%仅一台相机token，非权重压缩；创新7：位置保持、分割与注意力修复协同；复现6：超参数完整，但模拟器、分割器和异步测时未本地复现。 |
| Muir | 8 | 7 | 8 | 6 | 精度8：多尺度100B-token训练与检索对照；压缩7：状态随序列长度保持常数，但总参数匹配；创新8：门控敏感度、读出与稳定kernel联动；复现6：理论和rank可核验，本次未进行TPU训练。 |
| StrataFlux | 8 | 8 | 9 | 7 | 精度8：多模型低比特恢复但仍低于BF16；压缩8：降低GPU常驻精度但依赖外部补偿存储；创新9：编码、选择与交付联合设计；复现7：真实Qwen投影和代数检查通过，系统级内核与吞吐未复现。 |
| AutoCompress | 8 | 8 | 8 | 5 | 精度8：三部署约束下受控比较；压缩8：120B→74B明确但服务配置依赖强；创新8：真实引擎成本约束与异构结构联合；复现5：搜索/恢复token量巨大且需要目标GPUprofiling，本次未运行。 |
| Shape-teacher alignment | 7 | 2 | 6 | 6 | 精度7：LIBERO收敛和成功率改善，DINOv2对照更强；压缩2：原策略结构未变，无参数/字节压缩率；创新6：几何覆盖权重对齐明确；复现6：公式/λ可核验，但本次未运行仿真训练。 |
| Value-oriented policy distillation | 7 | 2 | 6 | 5 | 精度7：时间外测试有经济目标改善，但仍逊SAC教师；压缩2：无存储与延时比率；创新6：收益加权及专家约束结合；复现5：部分真实风场数据与运行环境本次不可复现。 |
| SSoG | 7 | 5 | 7 | 6 | 精度7：CIFAR改善、ImageNet looped略降；压缩5：参数少8.8–16.6%，非量化且内存对照依赖实现；创新7：算子结构与ODE全局适定性连接；复现6：公式明确，本次无训练/速度重跑。 |
| ProQuant | 8 | 8 | 8 | 6 | 精度8：跨小型MLLM和多个基准，W4A4仍明显落后BF16；压缩8：4bit权重理论有效载荷4倍但ViT等仍BF16；创新8：视觉敏感度驱动渐进QAT；复现6：真实Qwen文本组件训练通过，视觉机制受指定纯文本模型约束未验证。 |

重点读数：ProQuant W4A8为72.54对BF16 73.63（1.09个百分点差），W4A4仍低13.80点；AutoCompress的120B→74B是约1.62倍参数压缩；T3R的85%只对场景相机token，实测VLA调用加速1.16倍；Muir保持总参数预算；SSoG在1024² isolated算子对fused MHA内存689.0/304.3MiB，不能泛称总是省内存。OPD的50倍只算蒸馏阶段，计入教师的两域全流程节约42.0% FLOPs。风场蒸馏82%费用减少相对无控制，不是相对SAC教师。

## 5. Qwen3-0.6B真实组件复现

使用已有真实权重revision `c1899de289a04d12100db370d81485cdf75e47ca`。macOS CPU4线程，Python3.9.6、torch2.8.0、transformers4.57.6。两目录均含README、demo.py、results.json、run.log、validation.json，实际退出码均0；源码和结果SHA256绑定在validation.json。

| 目录 | 实现与实际结果 | 证据边界 |
|---|---|---|
| [StrataFlux](../../../scripts/quantization/2611.08363/README.md) | 完整首层2048×1024 q_proj，3bit RTN+4bit拟合补偿，1024通道/k32；2×64token校准和2×64留出。留出MSE 0.00605701→0.00372121，原残差补偿0.00372963；6项断言，4.37秒 | 未做KVarN/SSD/异步内核/整模型PPL或吞吐；KV修正式只小张量验证，不能称系统收益复现 |
| [ProQuant](../../../scripts/quantization/2611.08216/README.md) | 真实模型SRL，前2block W4A8可学习scale QAT，双向KL+CE，2提示10步；最终训练样本forward KL 0.02160/0.01550；5项单测和10步有限损失检查，280.32秒 | Qwen3-0.6B无视觉token，实际是prompt-token代理敏感度；视觉公式仅合成张量验证。不是完整MLLM恢复，无held-out任务结论 |

两项均不是空壳，也不伪造标准benchmark结果。完整多模态ProQuant受指定纯文本模型约束；StrataFlux系统加速需要运行时/硬件集成。本次没有执行其他7篇的全量训练或机器人实验。

## 6. 独立快照与Git基线

严格从fetch后的`origin/main` `abfe8f2767d8bf881d586718ab4db33fc576be6a`建立linked worktree与`feature/arxiv-daily-2026-11-09`。历史feature只读去重，没有继承任何feature提交或原工作树改动。

main只带一个历史成果`reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md`，本次删除。最终papers仅README及9篇新增；reports仅README及11-08日报；scripts仅README及2个新增量化目录；metadata仅README及11月9篇独立索引/CSV/本次审计。历史分支引用只作为去重证据，不是累计论文条目。

提交前验证实际目录/索引ID一致、论文集合与历史集合零交集、无窗口外论文、CSV/JSON可读、六节精读齐全、两项运行证据匹配及原工作树文件哈希不变。提交后另以`git log origin/main..HEAD`、merge-base、ls-remote验证单提交与远端SHA；验证记录与最终SHA保存在自动化run_status，避免在提交内嵌入自身SHA形成循环。

## 7. 尚未完成

完整多模态QAT、原论文GPU/TPU训练和系统级低比特性能未复现，限制如上；这些不是抓取失败或零结果。所有新增量化目录均已完成真实Qwen组件运行与小张量检查。11-07/08仅代表当前官方公开页面未检出，后续继续三天回查。
