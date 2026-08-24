# arXiv 模型压缩论文日报（2026-08-24）

> 运行日：2026-08-25（Asia/Shanghai）
> 固定检索窗口：2026-08-22 00:00 至 2026-08-24 23:59；逐篇按 arXiv `/abs` Submission history 的 v1 日期归日。
> 结论：截至 2026-08-25 02:14 CST，窗口内官方可见条目 0 篇，模型压缩相关论文 0 篇，历史重复 0 篇，本次新增 0 篇。

## 一、三天结果

| v1 实际提交日 | 官方可见条目 | 相关论文 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-08-22 | 0 | 0 | 0 | 0 |
| 2026-08-23 | 0 | 0 | 0 | 0 |
| 2026-08-24 | 0 | 0 | 0 | 0 |
| **合计** | **0** | **0** | **0** | **0** |

本轮官方分类页已经更新到 Monday, 24 August 2026 公告组，不能沿用上轮列表快照。五个 `new?show=2000` 页面跨分类去重后共有 581 个唯一 ID，页面内 581/581 均成功读取标题和摘要；随后 581/581 个官方 `/abs/<id>` 全部成功解析 Submission history，零失败，v1 最晚日期为 2026-08-21。因此三天的“0”是“截至运行时 arXiv 官方网页未检出”，不是把抓取失败写成零结果，也不是把 8 月 24 日公告日期误当成 submittedDate。

## 二、官方网页覆盖审计

未使用 arXiv API。完整读取 `cs.LG`、`cs.CL`、`cs.CV`、`cs.AI`、`cs.AR` 的 `new?show=2000` 与 `recent?show=2000`。十个页面声明总数均小于 2,000；每个 recent 日期组和 new/cross/replacement section 的 actual、shown、declared 条目数逐项一致，无第二页。十页合并共有 2,610 个唯一 ID；与本次公告相关的五个 new 页合并为 581 个唯一 ID。

### recent 页面

| 分类 | 入口 | 总数 | 08-24 公告组 | 08-21 相邻阳性对照 | 08-20 | 08-19 | 08-18 |
|---|---|---:|---:|---:|---:|---:|---:|
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 924 | 112 | 127 | 169 | 142 | 374 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 490 | 87 | 76 | 99 | 72 | 156 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 655 | 103 | 86 | 94 | 103 | 269 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1,166 | 200 | 145 | 186 | 170 | 465 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 41 | 6 | 12 | 8 | 7 | 8 |

表内是分类页公告组数量，同一论文可能跨分类重复；公告日期不用于归日。8 月 24 日公告组逐篇 `/abs` 核验后，v1 最晚为 8 月 21 日，所以 8 月 22–24 日没有官方可见条目。8 月 21 日组及更早分组是页面完整性的窗口外阳性对照。

### new 页面（Monday, 24 August 2026）

| 分类 | 入口 | 总数 | new | cross | replacement |
|---|---|---:|---:|---:|---:|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 195 | 55 | 57 | 83 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 139 | 70 | 17 | 52 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 151 | 82 | 21 | 48 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 290 | 88 | 112 | 90 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 11 | 3 | 3 | 5 |

日期边界证据：[2608.21360](https://arxiv.org/abs/2608.21360)、[2608.21359](https://arxiv.org/abs/2608.21359) 与压缩主题前沿候选 [2608.21134](https://arxiv.org/abs/2608.21134) 的 v1 均为 2026-08-21；历史完成论文 [2608.20334](https://arxiv.org/abs/2608.20334) 的 v1 为 2026-08-20。它们共同说明 8 月 24 日公告组尚未包含 v1 落入本窗口的论文。

## 三、语义召回与关键词复核

五个 new 页的 581 个唯一条目均读取了标题和摘要。先按研究对象和方法语义判断是否属于模型压缩，再用关键词作排序与漏检复核；至少覆盖 quantization、quantize、low-bit、model compression、compress、pruning、sparsity、knowledge distillation、distill、teacher/student、KV cache compression、mixed precision、GPTQ、AWQ，以及 token reduction、speculative inference、low-rank、compact/lightweight 等同义或邻近表达。纳入口径包括权重/激活量化、结构/注意力稀疏、teacher→student 蒸馏、KV cache 或视觉 token 压缩，以及有直接模型体积/推理压缩证据的紧凑架构；排除数据/媒体压缩、prompt/context 压缩、普通 PEFT、纯硬件调度和同词异义工作。

为审计高召回边界，139 个宽松语义候选首先逐篇读取 `/abs`；随后把核验扩展到全部 581 个唯一条目。由于 581 个条目没有任何 v1 落入 2026-08-22 至 2026-08-24，窗口原始相关数逐日均为 0，不存在需要下载全文、提取实验数字或评分的候选。

## 四、历史去重审计

`git fetch --prune origin` 后完整枚举 24 个 `origin/feature/arxiv-daily-*` 分支，对每个分支执行 `git ls-tree -r --name-only`。从真实 `papers/**/<id>/tech_analysis.md` 提取并去版本后缀，得到 223 个规范化历史已分析 ID。metadata 交叉核验额外发现 `2607.27951`、`2607.28410`、`2607.28457`，但三者没有真实 `tech_analysis.md`，按规则不计完成。

本窗口相关集合为空，所以被排除的重复 ID 及来源分支均为空，最终新增集合为空；最终集合与 223 个历史完成 ID 的交集为零。

## 五、完整论文表与评分

窗口内没有相关论文，故无论文表行。精度效果、压缩倍率、创新性、可复现性 1–10 评分均不适用；没有以缺失数据臆造评分。

## 六、本次产物与复现

- `papers/` 不创建论文目录，仅保留说明文件。
- `scripts/quantization/` 不存在；没有新增量化论文，因此不创建 Qwen3-0.6B 复现或空壳代码。
- `metadata/2026-08/papers_index.json` 中 `papers=[]`、`total_papers=0`、`new_papers_count=0`；`keywords.csv` 仅保留表头。

## 七、独立快照说明

本分支严格从最新 `origin/main`（`abfe8f2767d8bf881d586718ab4db33fc576be6a`）创建隔离 linked worktree。已删除 main 自带的 2026-07 历史日报；最终 `papers/`、`reports/`、`scripts/`、`metadata/` 只保留说明文件、本次日报和空的 2026-08 索引。原工作树的 3 个已修改文件和 3 个未跟踪项均未触碰。
