# arXiv 模型压缩论文日报（2026-08-23）

> 运行日：2026-08-24（Asia/Shanghai）
> 固定检索窗口：2026-08-21 00:00 至 2026-08-23 23:59；逐篇按 arXiv `/abs` Submission history 的 v1 日期归日。
> 结论：截至本次运行，窗口内官方可见条目 0 篇，模型压缩相关论文 0 篇，历史重复 0 篇，本次新增 0 篇。

## 一、三天结果

| v1 实际提交日 | 官方可见条目 | 相关论文 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-08-21 | 0 | 0 | 0 | 0 |
| 2026-08-22 | 0 | 0 | 0 | 0 |
| 2026-08-23 | 0 | 0 | 0 | 0 |
| **合计** | **0** | **0** | **0** | **0** |

截至 2026-08-24 02:07 CST，五个官方分类页最新公告仍为 Friday, 21 August 2026，尚无 8 月 22 或 23 日公告组。当前重新下载的十个 `new/recent?show=2000` 页面与 2026-08-23 完整扫描留存页面逐字节一致；对应 720 个跨分类唯一 ID 的官方 `/abs` 在上轮已全部成功解析，无失败，v1 最晚日期为 2026-08-20。本轮又直接核验列表首条、最高 ID 和窗口前沿压缩论文的官方详情页，Submission history 仍分别为 2026-06-12 或 2026-08-20。因此三天的“0”均表示“截至运行时 arXiv 官方网页未检出”，不是把抓取失败写成零结果。

## 二、官方网页覆盖审计

未使用 arXiv API。完整读取 cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`；所有页面声明总数均小于 2,000，每个 recent 日期组及 new/cross/replacement section 的实际条目数均等于页面声明数，不需要第二页。关键词只用于复核，不作为召回门槛；上一轮对同一 720 条记录的标题、摘要和 v1 history 已完成全量语义扫描，本轮以十个页面字节一致性和当前官方详情页复核作为续跑完整性保护。

### recent 页面

| 分类 | 入口 | 总数 | 08-23 | 08-22 | 08-21 公告组 | 窗口外阳性对照 |
|---|---|---:|---:|---:|---:|---|
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 950 | 无日期组 | 无日期组 | 127 | 08-20: 169；08-19: 142 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 465 | 无日期组 | 无日期组 | 76 | 08-20: 99；08-19: 72 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 641 | 无日期组 | 无日期组 | 86 | 08-20: 94；08-19: 103 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1,151 | 无日期组 | 无日期组 | 145 | 08-20: 186；08-19: 170 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 43 | 无日期组 | 无日期组 | 12 | 08-20: 8；08-19: 7 |

表内为分类页公告组数量，不是 v1 提交数量；同一论文可能在多个分类重复。8 月 21 日公告组跨分类去重后属于前述 720 个 ID 集合，逐篇 `/abs` 的 v1 最晚为 8 月 20 日，故本窗口没有官方可见条目。

### new 页面（Friday, 21 August 2026）

| 分类 | 入口 | 总数 | new | cross | replacement |
|---|---|---:|---:|---:|---:|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 200 | 65 | 62 | 73 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 109 | 49 | 27 | 33 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 137 | 66 | 20 | 51 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 222 | 62 | 83 | 77 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 14 | 10 | 2 | 2 |

当前官方详情页复核证据：[2608.20338](https://arxiv.org/abs/2608.20338) 与 [2608.20334](https://arxiv.org/abs/2608.20334) 的 v1 均为 2026-08-20；列表首条 [2608.19210](https://arxiv.org/abs/2608.19210) 的 v1 为 2026-06-12。三者共同验证公告日期不能代替真实 submittedDate。

## 三、语义召回与关键词复核

对同一列表快照的全量记录已读取标题和摘要，并按语义判断模型压缩主题；至少复核 quantization、quantize、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache compression、mixed precision、GPTQ、AWQ 及同义表达。纳入口径包括权重/激活量化、结构/注意力稀疏、teacher→student 或推理搜索蒸馏、KV cache 压缩，以及有直接模型体积证据的紧凑架构；排除数据/媒体压缩、普通 PEFT、仅压 retrieved text 的 context compression、纯硬件调度和同词异义工作。

由于 720 条记录中没有任何 v1 落入 2026-08-21 至 2026-08-23，窗口相关论文总数为 0；不存在需要进一步读取全文或评分的候选。

## 四、历史去重审计

`git fetch --prune origin` 后完整枚举 23 个 `origin/feature/arxiv-daily-*` 分支，并对每个分支执行 `git ls-tree -r --name-only`。从真实 `papers/**/<id>/tech_analysis.md` 得到 223 个规范化历史 ID；metadata 共出现 226 个 ID，其中 `2607.27951`、`2607.28410`、`2607.28457` 没有真实精读文件，未计为完成。

本窗口相关集合为空，因此排除的历史重复 ID 为空，最终新增集合也为空；最终集合与 223 个历史完成 ID 的交集为零。

## 五、完整论文表与评分

窗口内没有相关论文，故无论文表行。精度效果、压缩倍率、创新性、可复现性 1–10 评分均不适用；没有以缺失数据臆造评分。

## 六、本次产物与复现

- `papers/` 不创建论文目录，仅保留说明文件。
- `scripts/quantization/` 不存在；没有新增量化论文，故不创建 Qwen3-0.6B 复现或空壳代码。
- `metadata/2026-08/papers_index.json` 中 `papers=[]`、`total_papers=0`、`new_papers_count=0`；CSV 仅保留表头。

## 七、独立快照说明

本分支严格从最新 `origin/main` 创建隔离 linked worktree。已删除 main 自带的 2026-07 历史日报；最终 `papers/`、`reports/`、`scripts/`、`metadata/` 只保留说明文件、本次日报和空的 2026-08 索引。原工作树中的用户未提交修改和未跟踪文件均未触碰。
