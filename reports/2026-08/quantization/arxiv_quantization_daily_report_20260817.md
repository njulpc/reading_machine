# ArXiv 量化与模型压缩领域论文日报

**目标日期**: 2026-08-17 00:00–23:59

**检索状态**: 截至 2026-08-18 02:05 CST，公开可检索论文 0 篇

**数据来源**: arXiv API、cs.LG / cs.CL / cs.CV new 列表

---

## 一、检索方法与证据

使用 `submittedDate:[202608170000 TO 202608172359]` 过滤，并对以下关键词取并集：

`quantization`, `quantize`, `low-bit`, `model compression`, `compress`, `pruning`, `sparsity`, `knowledge distillation`, `KV cache compression`, `mixed precision`, `GPTQ`, `AWQ`。

合并关键词查询返回 `opensearch:totalResults = 0`。进一步移除全部关键词、仅按目标日期查询 arXiv 全部公开记录，结果仍为 `0`，因此零结果不是关键词过滤造成。相同查询语法在 2026-08-14 返回关键词结果 `44` 条、全量结果 `711` 条（阳性对照）；2026-08-13 的关键词查询也返回 `53` 条。相邻日期 2026-08-16 与运行日 2026-08-18 在本次运行时的关键词和全量日期查询均为 `0`。

- [arXiv API：2026-08-17 全量日期查询](https://export.arxiv.org/api/query?search_query=submittedDate%3A%5B202608170000%20TO%202608172359%5D&start=0&max_results=100&sortBy=submittedDate&sortOrder=ascending)
- [arXiv API：2026-08-17 模型压缩关键词查询](https://export.arxiv.org/api/query?search_query=submittedDate%3A%5B202608170000%20TO%202608172359%5D%20AND%20%28all%3A%22quantization%22%20OR%20all%3A%22quantize%22%20OR%20all%3A%22low-bit%22%20OR%20all%3A%22model%20compression%22%20OR%20all%3A%22compress%22%20OR%20all%3A%22pruning%22%20OR%20all%3A%22sparsity%22%20OR%20all%3A%22knowledge%20distillation%22%20OR%20all%3A%22KV%20cache%20compression%22%20OR%20all%3A%22mixed%20precision%22%20OR%20all%3A%22GPTQ%22%20OR%20all%3A%22AWQ%22%29&start=0&max_results=100&sortBy=submittedDate&sortOrder=ascending)
- [arXiv API：2026-08-16 同关键词相邻日期对照](https://export.arxiv.org/api/query?search_query=submittedDate%3A%5B202608160000%20TO%202608162359%5D%20AND%20%28all%3A%22quantization%22%20OR%20all%3A%22quantize%22%20OR%20all%3A%22low-bit%22%20OR%20all%3A%22model%20compression%22%20OR%20all%3A%22compress%22%20OR%20all%3A%22pruning%22%20OR%20all%3A%22sparsity%22%20OR%20all%3A%22knowledge%20distillation%22%20OR%20all%3A%22KV%20cache%20compression%22%20OR%20all%3A%22mixed%20precision%22%20OR%20all%3A%22GPTQ%22%20OR%20all%3A%22AWQ%22%29&start=0&max_results=100&sortBy=submittedDate&sortOrder=ascending)
- [arXiv API：2026-08-14 同关键词阳性对照](https://export.arxiv.org/api/query?search_query=submittedDate%3A%5B202608140000%20TO%202608142359%5D%20AND%20%28all%3A%22quantization%22%20OR%20all%3A%22quantize%22%20OR%20all%3A%22low-bit%22%20OR%20all%3A%22model%20compression%22%20OR%20all%3A%22compress%22%20OR%20all%3A%22pruning%22%20OR%20all%3A%22sparsity%22%20OR%20all%3A%22knowledge%20distillation%22%20OR%20all%3A%22KV%20cache%20compression%22%20OR%20all%3A%22mixed%20precision%22%20OR%20all%3A%22GPTQ%22%20OR%20all%3A%22AWQ%22%29&start=0&max_results=100&sortBy=submittedDate&sortOrder=ascending)
- [cs.LG new](https://arxiv.org/list/cs.LG/new?skip=0&show=2000)
- [cs.CL new](https://arxiv.org/list/cs.CL/new?skip=0&show=2000)
- [cs.CV new](https://arxiv.org/list/cs.CV/new?skip=0&show=2000)

三份分类 `new` 列表在本次运行时均显示 `Monday, 17 August 2026`，分别含 70、32、67 篇 new submissions。但列表日期是公告日期，并不等于论文 v1 的 `submittedDate`。题名关键词扫描得到的三个候选均已打开 submission history 核验：

| arXiv ID | 题名 | v1 实际提交时间（UTC） | 处理结论 |
|---|---|---|---|
| [2608.13966](https://arxiv.org/abs/2608.13966) | QUASAR: Lowering the Loss Floor of Quantization-Aware Training with Loss-Aware Reconstruction | 2026-08-14 05:29:58 | 模型量化相关，但不属于目标提交日 |
| [2608.14191](https://arxiv.org/abs/2608.14191) | KV Cache Compression Through the Lens of Transform Coding | 2026-08-14 11:08:01 | KV cache 压缩相关，但不属于目标提交日 |
| [2608.13897](https://arxiv.org/abs/2608.13897) | Practical Lossless Volumetric Medical Image Compression via Tri-plane Context Tree Learning | 2026-08-14 03:01:44 | 非模型压缩，且不属于目标提交日 |

因此没有把公告列表候选误计入 2026-08-17 的 `submittedDate` 结果。

---

## 二、论文总览

**截至本次运行，目标日期无公开新增相关论文。**

| 序号 | arXiv ID | 论文标题 | 分类 | 一句话结论 |
|:---:|---|---|---|---|
| - | - | 当日无公开新增模型压缩相关论文 | - | API 全量日期查询为 0；new 列表候选的 v1 均为 8 月 14 日 |

---

## 三、量化论文评分与复现

目标日期无公开量化论文，因此精度效果、压缩倍率、创新性、可复现性评分均不适用，也不创建量化复现目录。

| arXiv ID | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 评分依据 |
|---|:---:|:---:|:---:|:---:|---|
| - | N/A | N/A | N/A | N/A | 当日无公开量化论文，缺少可评分与可复现对象 |

---

## 四、整体分析与证据边界

截至 2026-08-18 02:05 CST，arXiv 公开 API 未检出任何 `submittedDate` 位于 2026-08-17 的记录，因此不存在可进一步逐篇确认、精读或复现的模型压缩论文。这反映的是公开索引在运行时的状态，不排除论文仍在后台处理或尚未完成公告。由于运行发生在亚洲时区凌晨，而分类列表仍停留在 8 月 17 日公告批次，后续流水线必须回查 2026-08-17，以覆盖公告延迟。

---

*报告生成时间: 2026-08-18 02:05 CST*

*分支: feature/arxiv-daily-2026-08-18*

*检索状态: 完成（截至运行时公开记录 0 篇，需后续回查）*
