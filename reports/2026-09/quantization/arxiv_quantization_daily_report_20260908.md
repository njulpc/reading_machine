# arXiv 模型压缩与量化日报 — 2026-09-08

运行日期：2026-09-09；核验时间：2026-09-09T01:12:56+08:00。

**检索窗口：北京时间2026-09-06、09-07、09-08三个完整自然日。窗口公开相关0篇，历史排除0篇，本次新增0篇。**

三日均为“截至运行时 arXiv 官方网页未检出”。这表示已完整扫描的官方公开列表中没有v1提交时间落入窗口的条目，不代表尚未公告的后台投稿为零。页面最新公告仍为09-07，后续三日窗口继续回查。

## 1. 官方页面全量覆盖

五分类各扫描new与recent，均show=2000。声明总数与实际解析条目数相等，覆盖序号1至总数，无需后续分页；检查new submissions、cross-lists，连同replacements一并核验。跨日期、跨分类按去版本ID合并为3118条；不以关键词筛选召回，未调用arXiv API。

| 分类 | new入口及声明=实际 | 新稿/交叉/替换分组 | recent入口及声明=实际 | recent日期分组 |
|---|---:|---|---:|---|
| cs.LG | [228](https://arxiv.org/list/cs.LG/new?show=2000) | New submissions (showing 79 of 79 entries)；Cross submissions (showing 58 of 58 entries)；Replacement submissions (showing 91 of 91 entries) | [1002](https://arxiv.org/list/cs.LG/recent?show=2000) | Mon, 7 Sep 2026 (showing 137 of 137 entries )；Fri, 4 Sep 2026 (showing 168 of 168 entries )；Thu, 3 Sep 2026 (showing 159 of 159 entries )；Wed, 2 Sep 2026 (showing 202 of 202 entries )；Tue, 1 Sep 2026 (showing 336 of 336 entries ) |
| cs.CL | [151](https://arxiv.org/list/cs.CL/new?show=2000) | New submissions (showing 63 of 63 entries)；Cross submissions (showing 35 of 35 entries)；Replacement submissions (showing 53 of 53 entries) | [797](https://arxiv.org/list/cs.CL/recent?show=2000) | Mon, 7 Sep 2026 (showing 98 of 98 entries )；Fri, 4 Sep 2026 (showing 115 of 115 entries )；Thu, 3 Sep 2026 (showing 101 of 101 entries )；Wed, 2 Sep 2026 (showing 185 of 185 entries )；Tue, 1 Sep 2026 (showing 298 of 298 entries ) |
| cs.CV | [174](https://arxiv.org/list/cs.CV/new?show=2000) | New submissions (showing 81 of 81 entries)；Cross submissions (showing 29 of 29 entries)；Replacement submissions (showing 64 of 64 entries) | [826](https://arxiv.org/list/cs.CV/recent?show=2000) | Mon, 7 Sep 2026 (showing 110 of 110 entries )；Fri, 4 Sep 2026 (showing 112 of 112 entries )；Thu, 3 Sep 2026 (showing 136 of 136 entries )；Wed, 2 Sep 2026 (showing 152 of 152 entries )；Tue, 1 Sep 2026 (showing 316 of 316 entries ) |
| cs.AI | [298](https://arxiv.org/list/cs.AI/new?show=2000) | New submissions (showing 106 of 106 entries)；Cross submissions (showing 99 of 99 entries)；Replacement submissions (showing 93 of 93 entries) | [1265](https://arxiv.org/list/cs.AI/recent?show=2000) | Mon, 7 Sep 2026 (showing 205 of 205 entries )；Fri, 4 Sep 2026 (showing 165 of 165 entries )；Thu, 3 Sep 2026 (showing 162 of 162 entries )；Wed, 2 Sep 2026 (showing 309 of 309 entries )；Tue, 1 Sep 2026 (showing 424 of 424 entries ) |
| cs.AR | [19](https://arxiv.org/list/cs.AR/new?show=2000) | New submissions (showing 12 of 12 entries)；Cross submissions (showing 2 of 2 entries)；Replacement submissions (showing 5 of 5 entries) | [55](https://arxiv.org/list/cs.AR/recent?show=2000) | Mon, 7 Sep 2026 (showing 14 of 14 entries )；Fri, 4 Sep 2026 (showing 9 of 9 entries )；Thu, 3 Sep 2026 (showing 10 of 10 entries )；Wed, 2 Sep 2026 (showing 12 of 12 entries )；Tue, 1 Sep 2026 (showing 10 of 10 entries ) |

全部3118个官方/abs页本次重新下载，标题、摘要、主分类、交叉分类和Submission history v1均完整解析，抓取失败0、解析失败0。没有用前次abs缓存代替本次抓取。先按真实v1从UTC换算北京时间，窗口内全部主题可见条目为0，因而无待语义判定的窗口论文；未声称本次人工重新精读3118篇窗口外旧稿。

复核词覆盖：quantization, quantize, quantise, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, distill, teacher, student, KV cache compression, mixed precision, GPTQ, AWQ, low-rank, binary, ternary, FP4, INT4, FP8, INT8, token pruning, token merging, early exit, weight sharing。对全体标题摘要执行复核以检查可能遗漏的主题表达，所有命中仍以v1日期归属；没有以无关键词命中证明零结果。

相邻日期阳性对照：09-05共有36个可见条目，证明列表与v1解析不是空抓取。

- [2609.05309 — How Does mHC Use Its Residual Streams? Selective Routing and Near-Identity Mixing](https://arxiv.org/abs/2609.05309)：v1 2026-09-04T16:02:20Z，北京时间 2026-09-05T00:02:20+08:00，在本次窗口外。
- [2609.05416 — WorldSculpt: Generating Compositional Worlds from Grounded Videos](https://arxiv.org/abs/2609.05416)：v1 2026-09-04T17:59:35Z，北京时间 2026-09-05T01:59:35+08:00，在本次窗口外。

本次可见最晚v1为2609.05416的2026-09-05T01:59:35+08:00。公告日期没有用于替代提交日期。与前次相比7页HTML字节一致，cs.LG/cs.CL/cs.AI的recent页仅发现作者姓名修正；全部abs关键字段变化数为5（详见metadata）。

## 2. 逐日计数与历史去重审计

| v1北京时间日期 | 全主题可见 | 原始相关 | 历史重复 | 本次新增 | 结论 |
|---|---:|---:|---:|---:|---|
| 2026-09-06 | 0 | 0 | 0 | 0 | 截至运行时 arXiv 官方网页未检出 |
| 2026-09-07 | 0 | 0 | 0 | 0 | 截至运行时 arXiv 官方网页未检出 |
| 2026-09-08 | 0 | 0 | 0 | 0 | 截至运行时 arXiv 官方网页未检出 |
| 合计 | 0 | 0 | 0 | 0 | 公开窗口未检出；非“全部已分析” |

fetch --prune origin成功后，逐一对全部39个历史origin/feature/arxiv-daily-*执行git ls-tree -r --name-only，真实papers/**/<id>/tech_analysis.md共527个规范ID。逐分支读取metadata/**/papers_index.json交叉核验，共530个ID；2607.27951、2607.28410、2607.28457仅有metadata，没有真实精读，均不计完成。ls-remote已验证分支全集与逐分支SHA一致。09-09当前分支此前不存在，未误计为历史。

窗口重复ID及来源分支：无；最终新增ID：空集；新增集合与历史527个ID交集为空。历史集合规模527不是本次排除重复数，本次排除数为0。

历史扫描分支（完整SHA见metadata）：

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
- `origin/feature/arxiv-daily-2026-09-08`

## 3. 新增论文表与评分

| arXiv ID | 完整标题 | v1实际提交时间 | 分类 | 一句话结论 |
|---|---|---|---|---|
| — | 本次无新增论文 | — | — | 截至运行时官方窗口未检出 |

精度效果、压缩倍率、创新性、可复现性四项1–10评分均不适用：没有新增论文，不填虚构评分或实验结果。不存在需要精读的新增论文，也不把历史论文再次复制到本日分支。

## 4. 复现与证据边界

新增quantization论文0篇，故本次没有Qwen3-0.6B算法复现、模型运行或小张量验证任务；scripts/quantization无论文复现目录。该状态来自官方v1时间核验，不是由权重、算力或依赖失败导致。

## 5. 独立快照与验证

分支feature/arxiv-daily-2026-09-09严格从最新origin/main abfe8f2767d8bf881d586718ab4db33fc576be6a建立，linked worktree为/private/tmp/reading_machine_arxiv_20260909。原工作树用户3个修改文件与3处未跟踪内容不参与，逐文件SHA256及git status用于保护验证。

清理main自带2026-07-28旧日报及其空目录；papers仅README，reports仅README和本次09-08日报，scripts仅README，metadata仅README与2026-09空索引/表头CSV。papers=[]、total_papers=0、new_papers_count=0，无累计条目。

提交前校验实际树、JSON/CSV、ID集合、历史零交集、日期范围、diff及main基线；提交后核验origin/main..HEAD只含本次1提交，并以ls-remote/log/merge-base验证远端。推送结果写最终回执，本文不预写尚未发生的远端成功。

本地审计证据：/private/tmp/arxiv_20260909，包括十页HTML、3118个abs HTML、完整扫描JSON、历史树审计、关键词复核、原始工作树指纹和验证结果。论文数量证据边界是公开公告延迟，后续运行仍需三天回查。
