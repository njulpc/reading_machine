# arXiv 模型压缩论文日报（2026-08-30）

**检索窗口**：2026-08-28 00:00 至 2026-08-30 23:59（Asia/Shanghai；按 `/abs` Submission history 的 v1 日期归日）

**运行时间**：2026-08-31 01:18 CST

**官方来源**：cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`；完整覆盖 new submissions、cross-lists、replacements 和 recent 日期组。

## 1. 结论速览

- 逐日相关：2026-08-28 为 0 篇、2026-08-29 为 0 篇、2026-08-30 为 0 篇，均应表述为“截至运行时 arXiv 官方网页未检出”。
- 窗口内全部 arXiv 条目即为 0，因此窗口相关总数、历史重复数和本次新增数均为 0；这不是抓取失败，也不是“存在相关论文但去重后新增为 0”。
- 十个官方列表页合并得到 2,785 个唯一 ID；逐条读取 2,785 个官方 `/abs` 页面，标题、摘要和 v1 history 均为 2,785/2,785 可解析。所有条目的 v1 最晚为 2026-08-27。
- 历史去重扫描 30 个远端日更分支，得到 337 个真实 `tech_analysis.md` 规范 ID；metadata 共 340 个 ID，其中 3 个 metadata-only ID 未计为已完成。

## 2. 官方列表覆盖审计

| 分类 | 入口 | 页面总数 | 日期/分组 | 实际覆盖 | 完整性 |
|---|---|---:|---|---:|---|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 252 | 08-28 new 77 / cross 80 / replacement 95 | 252 | 通过 |
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 903 | 08-28:157；08-27:188；08-26:155；08-25:291；08-24:112 | 903 | 通过 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 236 | 08-28 new 118 / cross 36 / replacement 82 | 236 | 通过 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 642 | 08-28:154；08-27:108；08-26:89；08-25:204；08-24:87 | 642 | 通过 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 184 | 08-28 new 93 / cross 21 / replacement 70 | 184 | 通过 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 670 | 08-28:114；08-27:107；08-26:112；08-25:234；08-24:103 | 670 | 通过 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 312 | 08-28 new 96 / cross 100 / replacement 116 | 312 | 通过 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1,195 | 08-28:196；08-27:209；08-26:228；08-25:362；08-24:200 | 1,195 | 通过 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 12 | 08-28 new 6 / cross 3 / replacement 3 | 12 | 通过 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 50 | 08-28:9；08-27:10；08-26:9；08-25:16；08-24:6 | 50 | 通过 |

十页声明总数、实际条目数和各组计数全部一致，且均低于 `show=2000`，无需继续分页。五个 `new` 页含 replacements 合并为 728 个唯一 ID；排除 replacements 后，new submissions 与 cross-lists 合并为 481 个唯一 ID。`recent` 页覆盖 8 月 28、27、26、25、24 日公告组，其中 8 月 27/26 的 v1 条目分别为 323/371 个，是窗口外阳性对照。公告组日期不用于归日；全量 `/abs` history 证明目标窗口三天没有 v1 条目。

逐条语义审阅所需的标题与摘要均来自官方 `/abs` 页面。由于窗口内全部条目数已经是 0，不存在需要进一步按 quantization、low-bit、compression、pruning、sparsity、distillation、teacher/student、KV cache、mixed precision、GPTQ、AWQ 或同义表达筛选的窗口候选，也不存在关键词漏召回问题。

## 3. 历史去重审计

- 去重来源分支数：30。
- 历史真实 `tech_analysis.md` 规范 ID：337。
- metadata 交叉核验：340 个 ID；`2607.27951`、`2607.28410`、`2607.28457` 没有真实 `tech_analysis.md`，不计完成。
- 逐日原始相关数：2026-08-28 为 0，2026-08-29 为 0，2026-08-30 为 0。
- 排除的历史重复 ID：无；重复来源分支：无；最终新增 ID：无。
- 最终新增集合为空，与历史已分析集合交集为空。

## 4. 窗口论文与评分

窗口内没有 v1 条目，因此没有模型压缩论文表格，也没有可填写的精度效果、压缩倍率、创新性和可复现性评分。这里的 0 是“截至运行时官方网页未检出”，不是以标题关键词筛选得到的 0。

## 5. 新增成果与复现

本次新增论文为 0，因此 `papers/` 仅保留说明文件，`scripts/quantization/` 不存在；没有新增 quantization 论文，也没有需要执行的 Qwen3-0.6B 复现。历史精读与历史复现均未复制到本分支。

## 6. 时效边界

五个分类页的最新公告组仍为 Friday, 28 August 2026，而全量详情页的 v1 最晚为 2026-08-27。2026-08-28、29、30 的结论只能解释为截至本次运行时的官方公开状态；后续运行仍需按三天窗口自动回查，以覆盖周末与公告延迟。
