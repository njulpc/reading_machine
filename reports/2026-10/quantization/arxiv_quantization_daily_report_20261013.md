# arXiv 模型压缩论文日报：2026-10-13

- 运行日：2026-10-14，时区 Asia/Shanghai；核验时间：2026-10-14T01:08:26.988918+08:00。
- 固定窗口：**2026-10-11、10-12、10-13**，各日00:00–23:59:59。论文归日依据官方 `/abs` 的 Submission history v1 提交时间，转换为北京时间；不用公告日期或ID月份代替。
- 结果：**截至运行时 arXiv 官方网页未检出**窗口内公开论文，相关0篇、历史重复0篇、本次新增0篇。不是“已有相关论文全部去重”，也不代表这三天实际无人投稿。

## 1. 假期延迟与结果时效性

[arXiv官方10月8日通知](https://blog.arxiv.org/2026/10/08/announcement_schedule_holiday_change/)明确：10月12日停止公告；美东10月9日14:00至10月13日14:00前接收并接受的稿件，延至10月13日20:00 ET公告，即**北京时间10月14日08:00**。本轮运行早于这一时刻。[官方常规时刻及假日列表](https://info.arxiv.org/help/availability.html)也列出10月12日假日。

常规列表响应存在约39小时的缓存Age，因此额外用Cache-Control:no-cache、不同show参数及独立查询参数验证cs.LG new/recent；最终两页均得到Age=0、X-Cache全MISS的原站响应，仍为10月12日列表，内容ID与主扫描一致。日期停留与官方停刊通知相符，不是把网络失败当零。所有五分类的完整日期/类型分组计数均核验通过。

**回查注意**：明日固定R-3/R-2/R-1窗口变为10月12–14日，将漏出尚未公告的10月11日。要补全10月11日，应在今天08:00公告后重跑本次10月11–13日窗口。本轮未自行改动自动化配置或扩大既定窗口。

## 2. 逐日计数与论文表

|v1实际提交日（北京时间）|公开全主题记录|相关原始跨列表出现数|相关规范ID数|历史重复|本次新增|
|---|---:|---:|---:|---:|---:|
|2026-10-11|0|0|0|0|0|
|2026-10-12|0|0|0|0|0|
|2026-10-13|0|0|0|0|0|

三日逐日结论均为“截至运行时 arXiv 官方网页未检出”。

|arXiv ID / 标题|v1 UTC|v1 北京时间|主/交叉分类|方法与一句话结论|
|---|---|---|---|---|
|无窗口内公开记录|不适用|不适用|不适用|不生成虚构论文条目|

|本次新增论文|精度效果（1–10）|压缩倍率（1–10）|创新性（1–10）|可复现性（1–10）|依据|
|---|---|---|---|---|---|
|无|不适用|不适用|不适用|不适用|没有新增论文，不捏造评分或实验数字|

## 3. 官方HTML全量覆盖证据

本轮重新下载五分类的new/recent共10个入口，show=2000、skip=0。全部页面总数小于2000，无需第二页；实际dt记录数与页面总数逐一相等。每个h3的“showing a of b”也核验为实际数=a=b；new包含new submissions、cross submissions和replacements。recent的公告日期为10月12、9、8、7、6日，完整覆盖目前已公开批次。

|官方入口|页面显示总数|实际范围|日期/类型分组|
|---|---:|---|---|
|[cs.AI new](https://arxiv.org/list/cs.AI/new?show=2000&skip=0)|313|skip0，1–313|Showing new listings for Monday, 12 October 2026；New submissions (showing 83 of 83 entries)；Cross submissions (showing 78 of 78 entries)；Replacement submissions (showing 152 of 152 entries)|
|[cs.AI recent](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0)|1649|skip0，1–1649|Mon, 12 Oct 2026 (showing 161 of 161 entries )；Fri, 9 Oct 2026 (showing 302 of 302 entries )；Thu, 8 Oct 2026 (showing 282 of 282 entries )；Wed, 7 Oct 2026 (showing 350 of 350 entries )；Tue, 6 Oct 2026 (showing 554 of 554 entries )|
|[cs.AR new](https://arxiv.org/list/cs.AR/new?show=2000&skip=0)|11|skip0，1–11|Showing new listings for Monday, 12 October 2026；New submissions (showing 6 of 6 entries)；Cross submissions (showing 4 of 4 entries)；Replacement submissions (showing 1 of 1 entries)|
|[cs.AR recent](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0)|67|skip0，1–67|Mon, 12 Oct 2026 (showing 10 of 10 entries )；Fri, 9 Oct 2026 (showing 9 of 9 entries )；Thu, 8 Oct 2026 (showing 8 of 8 entries )；Wed, 7 Oct 2026 (showing 26 of 26 entries )；Tue, 6 Oct 2026 (showing 14 of 14 entries )|
|[cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0)|172|skip0，1–172|Showing new listings for Monday, 12 October 2026；New submissions (showing 72 of 72 entries)；Cross submissions (showing 44 of 44 entries)；Replacement submissions (showing 56 of 56 entries)|
|[cs.CL recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0)|768|skip0，1–768|Mon, 12 Oct 2026 (showing 116 of 116 entries )；Fri, 9 Oct 2026 (showing 144 of 144 entries )；Thu, 8 Oct 2026 (showing 118 of 118 entries )；Wed, 7 Oct 2026 (showing 147 of 147 entries )；Tue, 6 Oct 2026 (showing 243 of 243 entries )|
|[cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000&skip=0)|237|skip0，1–237|Showing new listings for Monday, 12 October 2026；New submissions (showing 127 of 127 entries)；Cross submissions (showing 26 of 26 entries)；Replacement submissions (showing 84 of 84 entries)|
|[cs.CV recent](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0)|995|skip0，1–995|Mon, 12 Oct 2026 (showing 153 of 153 entries )；Fri, 9 Oct 2026 (showing 207 of 207 entries )；Thu, 8 Oct 2026 (showing 186 of 186 entries )；Wed, 7 Oct 2026 (showing 164 of 164 entries )；Tue, 6 Oct 2026 (showing 285 of 285 entries )|
|[cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0)|413|skip0，1–413|Showing new listings for Monday, 12 October 2026；New submissions (showing 146 of 146 entries)；Cross submissions (showing 116 of 116 entries)；Replacement submissions (showing 151 of 151 entries)|
|[cs.LG recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0)|1894|skip0，1–1894|Mon, 12 Oct 2026 (showing 262 of 262 entries )；Fri, 9 Oct 2026 (showing 324 of 324 entries )；Thu, 8 Oct 2026 (showing 353 of 353 entries )；Wed, 7 Oct 2026 (showing 355 of 355 entries )；Tue, 6 Oct 2026 (showing 600 of 600 entries )|

共**6519次出现→4299个规范ID**，去掉v1/v2等后缀，跨分类、日期和入口统一。所有4299份官方abs HTML本轮重新解析，标题、摘要、主/交叉分类和v1均完整，0解析失败。原始HTML复用2026-10-13运行缓存，四个阳性对照在本轮重新下载；缓存来源与SHA256逐条保留，不能声称4299份均为本轮新请求。

先按v1检查全部4299个ID，窗口内全主题记录为0。全部窗外标题摘要已解析并逐词复核，但本轮没有人工语义精读4299篇窗外论文；它们的排除仅依据提交日期，不依赖关键词或主题判断。由于没有窗内记录，窗内逐篇语义判定与全文候选集合均为空。关键词只用于复核，不用于召回或截断列表。

复核词：quantization, quantize, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, distill, teacher, student, KV cache compression, mixed precision, GPTQ, AWQ, quantisation, low precision, token pruning, token merging, weight sharing, low rank, binary, ternary。每个词保存全列表命中ID和窗口命中ID（均空）到审计JSON。

### 窗口外相邻日期阳性对照

|论文|真实v1 UTC|北京时间|复核作用|
|---|---|---|---|
|[2610.13948 — Can Language Models Play the Wikipedia Game?](https://arxiv.org/abs/2610.13948)|2026-10-09 17:59:56|2026-10-10 01:59:56|所有列表ID中最新v1，位于窗口前一自然日，详情正常可读|
|[2610.13944 — InstantFusion](https://arxiv.org/abs/2610.13944)|2026-10-09 17:59:04|2026-10-10 01:59:04|相邻日蒸馏正例，本轮日期窗外；历史10-13分支已完成|
|[2610.13806 — FORTE](https://arxiv.org/abs/2610.13806)|2026-10-09 16:18:39|2026-10-10 00:18:39|相邻日特征/参数剪枝正例，本轮日期窗外；历史10-13分支已完成|
|[2610.12494 — Algebraic Integer Quantization](https://arxiv.org/abs/2610.12494)|2026-09-25 19:36:04|2026-09-26 03:36:04|new页面量化正例，v1远早于公告日；不能按2610前缀或标题纳入|

这些对照的标题、摘要、分类和Submission history均本轮阅读。量化与蒸馏检索能发现主题正例，零窗口不是关键词失效。

## 4. 历史去重审计

1. `git fetch --prune origin`成功后，遍历47个远端 `origin/feature/arxiv-daily-*`；每个分支实际执行`git ls-tree -r --name-only`，并`git show`读取其metadata索引交叉核验。
2. 只把真实 `papers/**/<arxiv_id>/tech_analysis.md` 算为完成，规范化后历史已分析**567个ID**，包含10-13分支新增5篇。metadata-only的2607.27951、2607.28410、2607.28457不计完成。
3. `git ls-remote --heads origin`与本地历史审计47个分支名称/SHA及main SHA逐项一致，没有遗漏远端日更分支。当日分支起初不存在，不是旧feature续跑。
4. 窗口相关原始数0、跨列表去重后0、历史重复0、最终新增0；排除重复ID及来源分支为空，最终新增ID=[]。这里不把窗外历史正例计为本窗口“被去重”数量。
5. 新增集合与历史集合交集=[]。所有来源分支和精确SHA写入papers_index.json和retrieval_audit.json；逐分支树、metadata-only差异保存在本地history.json。

## 5. 精读、复现与独立快照

本次无新增论文，无需生成tech_analysis.md；新增quantization为0，不创建Qwen3-0.6B复现目录，不运行无关历史代码，也没有伪造实验结果。语法/导入/小张量验证不适用，因为没有本次复现代码。

从fetch后origin/main `abfe8f2767d8bf881d586718ab4db33fc576be6a`严格创建linked worktree `/private/tmp/reading_machine_arxiv_20261014`，分支`feature/arxiv-daily-2026-10-14`。没有复制用户未提交文件或历史feature成果。

仅在隔离worktree删除main自带的 `reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md`，清除空旧月目录。最终papers仅README、scripts仅README（无scripts/quantization）、reports仅README及本日报；metadata仅README与2026-10空papers索引、仅表头CSV、检索审计。零结果月份为R-1所属2026-10，total_papers=new_papers_count=0。

原工作树6项未提交状态与逐文件SHA256均核验。发布检查包括目录/索引/CSV一致、历史零交集、git diff --check、origin/main基线和单提交；推送后再用ls-remote、log、merge-base核验。实际提交SHA与最终检查结果保存在本地run_status.json、validation.json，避免提交内容自引用SHA。

## 6. 证据边界及未完成事项

检索结论仅代表上述运行时刻已经公开的页面。假期延迟批次尚未公告，无法提前精读、统计或复现其中论文；这是公开时间限制，不是抓取失败。本轮未修改定时配置；需要公告后回查当天窗口以覆盖10月11日。4299份abs采用可审计缓存并重新解析，四个对照本轮刷新；未声称人工精读全部窗外摘要或全文。

本地完整证据：`/Users/lipengcheng/.codex/automations/arxiv/runs/2026-10-14`，包括10页官方HTML、逐组覆盖、4299份abs及来源哈希、官方假期公告、Age=0时效性对照、47分支历史树、原工作树保护及发布验证。
