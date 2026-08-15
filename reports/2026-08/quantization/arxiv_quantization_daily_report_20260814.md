# ArXiv 量化与模型压缩领域论文日报

**目标日期**: 2026-08-14 00:00-23:59

**检索状态**: 截至 2026-08-15 运行时，公开可检索论文 0 篇

**数据来源**: arXiv API、cs.LG / cs.CL / cs.CV new 列表

---

## 一、检索方法与证据

使用 `submittedDate:[202608140000 TO 202608142359]` 过滤，并对以下关键词取并集：

`quantization`, `quantize`, `low-bit`, `model compression`, `compress`, `pruning`, `sparsity`, `knowledge distillation`, `KV cache compression`, `mixed precision`, `GPTQ`, `AWQ`。

合并关键词查询返回 `opensearch:totalResults = 0`。进一步移除所有关键词、仅按该日期查询 arXiv 全部公开记录，结果仍为 0；使用相同语法查询 2026-08-13 则返回 41 个关键词命中，证明日期范围语法有效。

- [arXiv API：2026-08-14 全量日期查询](https://export.arxiv.org/api/query?search_query=submittedDate%3A%5B202608140000%20TO%202608142359%5D&start=0&max_results=1)
- [cs.LG new](https://arxiv.org/list/cs.LG/new)
- [cs.CL new](https://arxiv.org/list/cs.CL/new)
- [cs.CV new](https://arxiv.org/list/cs.CV/new)

分类列表中命中压缩关键词的代表性候选均逐篇检查 v1 提交历史：

| arXiv ID | 候选方向 | v1 提交时间（UTC） | 排除原因 |
|---|---|---|---|
| [2608.12780](https://arxiv.org/abs/2608.12780) | 稀疏视频注意力 | 2026-08-13 03:43:31 | 不属于目标日期 |
| [2608.12953](https://arxiv.org/abs/2608.12953) | LLM 结构化剪枝 | 2026-08-13 08:32:18 | 不属于目标日期 |
| [2608.13226](https://arxiv.org/abs/2608.13226) | 3D VLM Token 剪枝 | 2026-08-13 13:29:15 | 不属于目标日期 |
| [2608.13365](https://arxiv.org/abs/2608.13365) | 动态 W4A4KV4 量化 | 2026-08-13 15:31:01 | 不属于目标日期 |
| [2608.13387](https://arxiv.org/abs/2608.13387) | On-policy 蒸馏 | 2026-08-13 15:48:16 | 不属于目标日期 |
| [2608.13391](https://arxiv.org/abs/2608.13391) | 视频生成蒸馏 | 2026-08-13 15:51:31 | 不属于目标日期 |

---

## 二、论文总览

**截至本次运行，目标日期无公开新增相关论文。**

| 序号 | arXiv ID | 论文标题 | 分类 | 一句话结论 |
|:---:|---|---|---|---|
| - | - | 当日无公开新增模型压缩相关论文 | - | API 全量日期查询为 0，分类列表候选均因 v1 日期不符而排除 |

---

## 三、量化论文评分与复现

目标日期无公开量化论文，因此精度效果、压缩倍率、创新性、可复现性评分均不适用，也无需创建量化复现目录。

| arXiv ID | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 说明 |
|---|:---:|:---:|:---:|:---:|---|
| - | N/A | N/A | N/A | N/A | 当日无公开量化论文 |

---

## 四、证据边界

零结果是截至运行时 arXiv 公开 API 的状态，不排除作者后台中尚未公告、尚在处理或尚未公开的投稿。后续流水线应回查该日期，避免公告延迟造成遗漏。

---

*报告生成日期: 2026-08-15 CST*

*分支: feature/arxiv-daily-2026-08-15*

*检索状态: 完成（公开记录 0 篇）*
