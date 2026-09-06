# arXiv 模型压缩与量化日报 — 2026-09-06

运行时间：2026-09-07T01:12:52+08:00。运行日 R=2026-09-07，固定检索窗口为北京时间 **2026-09-04、09-05、09-06** 三个完整自然日。

**窗口相关 10 篇，历史重复 10 篇，本次新增 0 篇。** 这是“存在相关但去重后新增为零”。09-05 和 09-06 均仅能表述为“截至运行时 arXiv 官方网页未检出”，不能推断最终投稿数量为零。

## 1. 官方检索覆盖与时间核验

cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 new/recent 十页均以 show=2000 完整下载，包含 new submissions 与 cross-lists，并保留 replacements 以核验旧稿。各页声明数与实际解析数完全一致且均少于2000，覆盖序号1至各页总数，无未覆盖的后续分页。跨日期/分类按去版本后缀的 ID 合并后为3087条；本次3087个官方 /abs 全部重新下载，标题、摘要、主/交叉分类及 Submission history 的 v1 时间全部解析成功。未使用 arXiv API、API submittedDate 查询或搜索摘要代替召回。

| 分类 | new 声明=实际 | new/交叉/替换分组 | recent 声明=实际 | recent 日期分组与覆盖数 |
|---|---:|---|---:|---|
| cs.LG | [272](https://arxiv.org/list/cs.LG/new?show=2000) | New submissions (showing 85 of 85 entries)；Cross submissions (showing 83 of 83 entries)；Replacement submissions (showing 104 of 104 entries) | [985](https://arxiv.org/list/cs.LG/recent?show=2000) | Fri, 4 Sep 2026 (showing 168 of 168 entries )；Thu, 3 Sep 2026 (showing 159 of 159 entries )；Wed, 2 Sep 2026 (showing 202 of 202 entries )；Tue, 1 Sep 2026 (showing 336 of 336 entries )；Mon, 31 Aug 2026 (showing 120 of 120 entries ) |
| cs.CL | [183](https://arxiv.org/list/cs.CL/new?show=2000) | New submissions (showing 75 of 75 entries)；Cross submissions (showing 40 of 40 entries)；Replacement submissions (showing 68 of 68 entries) | [781](https://arxiv.org/list/cs.CL/recent?show=2000) | Fri, 4 Sep 2026 (showing 115 of 115 entries )；Thu, 3 Sep 2026 (showing 101 of 101 entries )；Wed, 2 Sep 2026 (showing 185 of 185 entries )；Tue, 1 Sep 2026 (showing 298 of 298 entries )；Mon, 31 Aug 2026 (showing 82 of 82 entries ) |
| cs.CV | [175](https://arxiv.org/list/cs.CV/new?show=2000) | New submissions (showing 102 of 102 entries)；Cross submissions (showing 10 of 10 entries)；Replacement submissions (showing 63 of 63 entries) | [809](https://arxiv.org/list/cs.CV/recent?show=2000) | Fri, 4 Sep 2026 (showing 112 of 112 entries )；Thu, 3 Sep 2026 (showing 136 of 136 entries )；Wed, 2 Sep 2026 (showing 152 of 152 entries )；Tue, 1 Sep 2026 (showing 316 of 316 entries )；Mon, 31 Aug 2026 (showing 93 of 93 entries ) |
| cs.AI | [269](https://arxiv.org/list/cs.AI/new?show=2000) | New submissions (showing 69 of 69 entries)；Cross submissions (showing 96 of 96 entries)；Replacement submissions (showing 104 of 104 entries) | [1250](https://arxiv.org/list/cs.AI/recent?show=2000) | Fri, 4 Sep 2026 (showing 165 of 165 entries )；Thu, 3 Sep 2026 (showing 162 of 162 entries )；Wed, 2 Sep 2026 (showing 309 of 309 entries )；Tue, 1 Sep 2026 (showing 424 of 424 entries )；Mon, 31 Aug 2026 (showing 190 of 190 entries ) |
| cs.AR | [10](https://arxiv.org/list/cs.AR/new?show=2000) | New submissions (showing 4 of 4 entries)；Cross submissions (showing 5 of 5 entries)；Replacement submissions (showing 1 of 1 entries) | [46](https://arxiv.org/list/cs.AR/recent?show=2000) | Fri, 4 Sep 2026 (showing 9 of 9 entries )；Thu, 3 Sep 2026 (showing 10 of 10 entries )；Wed, 2 Sep 2026 (showing 12 of 12 entries )；Tue, 1 Sep 2026 (showing 10 of 10 entries )；Mon, 31 Aug 2026 (showing 5 of 5 entries ) |

窗口外相邻日期阳性对照：北京时间09-03可见359条 v1，例如 [2609.02760](https://arxiv.org/abs/2609.02760) 的提交时间为 2026-09-02T16:00:05Z / 2026-09-03T00:00:05+08:00。recent 覆盖08-31至09-04公告分组。最新公告仍为09-04，归日一律采用 /abs 的 v1 UTC 转北京时间，公告日期不替代提交日期。

## 2. 语义复核与边界

本次重新下载全部3087个官方abs并逐字段比对标题/摘要/v1/分类；复用09-05全量语义审阅及09-06复核作为窗口外初筛证据，本次另逐篇阅读全部63篇窗口内标题摘要，3篇边界候选读官方全文。关键词仅用于排序和复核。

十个列表与09-06证据逐字节相同，3087条官方记录的标题、摘要、v1及分类亦逐字段相同。窗口内63篇全部重新阅读，相关判定独立于历史集合；先判定相关，再查历史是否完成。未声称本次重新独立精读全部3087篇。

复核词包括 quantization、quantize/quantise、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache compression、mixed precision、GPTQ、AWQ，以及低秩、二值/三值、FP4/INT4/FP8/INT8、token选择/合并等同义表达。关键词不构成召回门槛。

| 边界候选 | 全文/摘要判定依据 |
|---|---|
| [Efficient Semantic Understanding from Digital Foveation](https://arxiv.org/html/2609.04088v1) | 排除。§3以低分辨率显著性和高分辨率裁剪训练分割网络，并增加context CNN与canvas；§7的4.7%计算是输入观察预算，未压缩既有模型参数或内部token/KV。属于主动视觉输入采样。 |
| [EditVid](https://arxiv.org/html/2609.04190v1) | 排除。§4.2式6向冻结图像编辑MM-DiT的当前K/V追加前帧K/V，§4.3以锚帧token替换对应特征；核心为增加时序一致性，不是对既有全时序模型做缓存压缩。constant footprint指新增时序上下文随视频长度不增长。 |
| [LaPla](https://arxiv.org/html/2609.04070v1) | 排除。§III的4层残差VQ（64/64/128/128码本）学习动作表示，未来动作通过连续latent并行预测；Emu3-8B仅用LoRA适配，未提出模型低比特量化或权重压缩。 |
| PreferenceEKF / 2609.04066 | 排除。低维子空间用于贝叶斯后验及主动奖励学习的不确定性估计，摘要未提出压缩部署模型。 |
| ESPO / 2609.04197；Para-Pipe / 2609.04168 | 分别为提示优化与SoC算子映射，不压缩模型。 |

## 3. 逐日计数与历史去重审计

“原始相关”指三日跨分类合并规范ID后、排除历史前的语义相关数；不重复计数分类页出现次数。

| v1 北京时间日期 | 全主题可见 | 原始相关 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-09-04 | 63 | 10 | 10 | 0 |
| 2026-09-05 | 0 | 0 | 0 | 0 |
| 2026-09-06 | 0 | 0 | 0 | 0 |
| 合计 | 63 | 10 | 10 | 0 |

fetch --prune origin 成功后，对全部37个历史日更分支逐一执行 git ls-tree -r --name-only，以真实 papers/**/<id>/tech_analysis.md 提取规范ID，共522个。逐分支读取 metadata/**/papers_index.json 交叉核验得到525个ID。2607.27951、2607.28410、2607.28457仅有metadata而无精读文件，未计完成。当前09-07分支创建前不存在，单独处理而不纳入历史。

完整历史扫描分支：

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

## 4. 完整相关论文及重复来源

以下10篇均为历史重复；本次不复制历史分析、复现和论文metadata条目。精度效果/压缩倍率/创新性/可复现性评分均为1–10主观分，沿用09-05来源metadata，具体实验与评分依据见链接的历史精读；不能将吞吐提升等同于参数压缩倍率。

| ID与标题 | v1 UTC / 北京时间 | 类别与结论 | 精度/压缩/创新/可复现 | 重复来源及依据 |
|---|---|---|---|---|
| [2609.04031 — DSAQuant: Denoising-Stage-Aligned Quantization-Aware Training for Video Generation](https://arxiv.org/abs/2609.04031) | 2026-09-03T16:09:25Z / 2026-09-04T00:09:25+08:00 | quantization；DSA 按去噪阶段切换监督来源，并把低比特误差与CFG调度共同处理。 | 8/9/9/5 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.04031/tech_analysis.md) |
| [2609.04071 — TAP-Path: Task-Adaptive Structural and Token Pruning for Efficient and Trustworthy Pathology Foundation Models](https://arxiv.org/abs/2609.04071) | 2026-09-03T16:43:36Z / 2026-09-04T00:43:36+08:00 | pruning；TAPPath 联合裁剪病理视觉编码器层数与token，得到更小且有外部验证的模型。 | 9/7/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/pruning/2609.04071/tech_analysis.md) |
| [2609.04083 — CORE: Improving Compositional Reasoning in MLLM Embedding via Reranker Distillation](https://arxiv.org/abs/2609.04083) | 2026-09-03T16:50:29Z / 2026-09-04T00:50:29+08:00 | knowledge_distillation；CORE 将跨模态重排序器的组合关系判断迁移给可预计算的嵌入模型。 | 8/5/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04083/tech_analysis.md) |
| [2609.04098 — Why Gated DeltaNet Survives 4-Bit Quantization: NVFP4 W4A4 for the Recurrent Half of a Hybrid 27B LLM](https://arxiv.org/abs/2609.04098) | 2026-09-03T17:04:26Z / 2026-09-04T01:04:26+08:00 | quantization；Minima 给出混合GDN/注意力模型可部署的NVFP4校准及融合尺度协调方案。 | 9/9/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.04098/tech_analysis.md) |
| [2609.04105 — Hardware-Aware FP4 FlashAttention-4](https://arxiv.org/abs/2609.04105) | 2026-09-03T17:12:35Z / 2026-09-04T01:12:35+08:00 | quantization；Direct-P 直接从分数产生 FP4 概率码，并用相同表示计算归一化分母。 | 8/7/9/5 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/quantization/2609.04105/tech_analysis.md) |
| [2609.04108 — Sequential Beats Joint: On the Interplay between On-Policy Distillation and RLVR](https://arxiv.org/abs/2609.04108) | 2026-09-03T17:14:27Z / 2026-09-04T01:14:27+08:00 | knowledge_distillation；先 OPD 再 RLVR 比多种联合损失更好，教师扩展覆盖后由奖励强化正确模式。 | 8/7/7/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04108/tech_analysis.md) |
| [2609.04131 — Beyond Retrieval: Progressive Latent Memory Evolution for Streaming Video Understanding](https://arxiv.org/abs/2609.04131) | 2026-09-03T17:28:14Z / 2026-09-04T01:28:14+08:00 | other；LatentStream 用查询无关的分层潜在记忆持续压缩视频，再按问题读取证据。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/other/2609.04131/tech_analysis.md) |
| [2609.04172 — Rethinking On-Policy Distillation of Large Language Models II: One Training Example](https://arxiv.org/abs/2609.04172) | 2026-09-03T17:54:38Z / 2026-09-04T01:54:38+08:00 | knowledge_distillation；单条查询也能支持持续OPD，训练效率瓶颈可能在吸收监督而非提示数量。 | 8/3/9/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04172/tech_analysis.md) |
| [2609.04199 — Compile by Training: Turning Natural-Language Specifications into Local Neural Functions](https://arxiv.org/abs/2609.04199) | 2026-09-03T17:59:49Z / 2026-09-04T01:59:49+08:00 | knowledge_distillation；将自然语言规格编译成可复用的本地 Qwen3-0.6B 适配器。 | 8/8/8/7 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04199/tech_analysis.md) |
| [2609.04203 — Temporal Self-Distillation: Learning Visual State Tracking in Videos Without Supervision](https://arxiv.org/abs/2609.04203) | 2026-09-03T17:59:55Z / 2026-09-04T01:59:55+08:00 | knowledge_distillation；S3T 用同一模型的密集时间视图监督稀疏视图，提高视频时间理解。 | 8/6/8/8 | 历史重复；`origin/feature/arxiv-daily-2026-09-05`；[实验与评分依据](https://github.com/njulpc/reading_machine/blob/feature/arxiv-daily-2026-09-05/papers/2026-09/knowledge_distillation/2609.04203/tech_analysis.md) |

### 历史评分的具体依据

下表数字转述上述历史精读中核对的论文实验，本次未独立复现。压缩分反映资源节省程度与证据，分数不是倍率。

| ID | 精度效果依据 | 压缩依据及边界 | 创新依据 | 可复现性依据及限制 |
|---|---|---|---|---|
| 2609.04031 | Wan1.3B VBench 67.21，QVGen 63.56、BF16 66.28 | W4A4/W3A3；低位宽不等于整机同比压缩 | 阶段监督与后期CFG关闭协同 | 需24–64张H20；历史Qwen验证仅数值组件 |
| 2609.04071 | 32类准确率87.98%，全模型86.89%；外部91.22% | 参数631.24M→473.70M，FLOPs340.13G→220.40G | 层选择+70%token保留+任务头 | 头部3种子，外部433例仅两类任务 |
| 2609.04083 | 重排0.827、嵌入0.666，指标口径不同 | 8B嵌入可预计算；无统一权重压缩倍数 | 五级候选列表与Rank-KL | 同预算比较三类损失，本次未训练 |
| 2609.04098 | 五任务均值85.62→85.10；缓存校准后32K困惑度10.50 | 权重50.13→17.53GiB，约2.86倍 | 全线性层NVFP4及融合尺度协调 | Blackwell和GDN架构要求；Qwen0.6B组件非27B部署 |
| 2609.04105 | 分布式MXFP4 P/V训练均发散，保留FP8 | 非因果forward最高2.13倍吞吐，不是权重压缩率 | Direct-P及相同量化概率归一化 | GB200内核；计时未含动态量化与重排 |
| 2609.04108 | 逻辑pass@1 80.6，纯OPD53.9、GRPO49.4 | 8B教师→1.7B学生；额外训练预算需计入 | 顺序OPD再RL，以验证分数切换 | 有联合损失对照；收益依赖阶段预算 |
| 2609.04131 | OVO54.0→64.2，StreamingBench73.9→76.9 | 峰值30.80→21.97GB；TTFT7.63→8.41秒 | 分层合并、潜在记忆演化、熵奖励 | 无离线训练，推理优化增加首token开销 |
| 2609.04172 | 1条覆盖71.5%，16条98.9%并接近全量训练 | 多组同规模师生；训练数据减少不等于权重压缩 | 用状态覆盖解释OPD数据需求 | 仍需数百步，覆盖指标依赖表示 |
| 2609.04199 | FuzzyBench-Hard语义准确率83.6% | 本地Qwen3-0.6B适配器取代重复远端调用；无统一字节比 | 将规格编译为可组合神经函数 | rank64、100步等明确；教师成本需摊销 |
| 2609.04203 | VSTAT+1.74、YouTube+7.95、动作计数+4.50 | 同权重密集教师→稀疏学生视图；无权重缩小 | 时间采样密度作为特权自监督 | 300段合成视频，真实分布覆盖仍有限 |

## 5. 复现、独立快照与验证

本次最终新增集合为空，没有新增标题或需精读的论文。新增量化论文为0，因此无Qwen3-0.6B复现任务、无新增复现目录或运行结果。历史量化论文的已有复现不复制、不重跑，也不计作本次成果。

分支 feature/arxiv-daily-2026-09-07 严格从本次fetch后的 origin/main abfe8f2767d8bf881d586718ab4db33fc576be6a 创建于隔离linked worktree。删除main自带07-28历史日报；papers仅README，reports仅README和本日报，scripts仅README且无scripts/quantization论文目录，metadata仅README与2026-09空索引/表头CSV。原工作树3修改和3未跟踪项保持不变。

最终新增ID与历史522个ID的交集为空；papers、metadata.papers、CSV数据行与复现目录的ID集合均为空。提交前检查JSON/CSV、实际文件树、git diff --check、相对origin/main的diff及提交历史；提交后检查仅1个本次提交，推送后用git ls-remote、git log和merge-base验证远端SHA及main基线。Git最终结果见运行回执，不预写尚未执行的远端验证为成功。

检索及去重无未完成项。09-05/06的零结果仅限截至运行时的官方网页可见状态；后续运行继续按三天窗口回查公告延迟。
