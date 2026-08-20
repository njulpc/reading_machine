# arXiv 模型压缩论文日报（2026-08-19）

> 运行时间：2026-08-20 09:58 CST（Asia/Shanghai）  
> 固定检索窗口：2026-08-17 00:00:00 至 2026-08-19 23:59:59（三个完整自然日）  
> 主日报日期：2026-08-19  
> 检索方式：arXiv 官方 HTML 分类页、论文详情页和 PDF；未使用 arXiv API

## 1. 官方网页检索与日期核验

完整下载并解析了 [cs.LG](https://arxiv.org/list/cs.LG/recent?skip=0&show=2000)、[cs.CL](https://arxiv.org/list/cs.CL/recent?skip=0&show=2000)、[cs.CV](https://arxiv.org/list/cs.CV/recent?skip=0&show=2000)、[cs.AI](https://arxiv.org/list/cs.AI/recent?skip=0&show=2000)、[cs.AR](https://arxiv.org/list/cs.AR/recent?skip=0&show=2000) 的 `recent?show=2000` 页面，并核对相应 `new?show=2000` 页的 new/cross/replacement 三个区段。五类页面在 8 月 17–19 日公告组内跨分类去重后共有 **1,680** 个 ID；标题全量扫描后，对压缩明确命中及轻量化语义候选逐篇读取 `/abs/<id>` 摘要与 Submission history，并对最终入选论文读取官方 PDF。

| 分类 | recent 总条目 | 08-19 公告组 | 08-18 公告组 | 08-17 公告组 | 08-14 阳性对照 | 08-19 new / cross / replacement |
|---|---:|---:|---:|---:|---:|---:|
| cs.LG | 993 | 142/142 | 374/374 | 138/138 | 157/157 | 81 / 61 / 95 |
| cs.CL | 483 | 72/72 | 156/156 | 62/62 | 101/101 | 49 / 23 / 62 |
| cs.CV | 694 | 103/103 | 269/269 | 89/89 | 107/107 | 89 / 14 / 68 |
| cs.AI | 1,235 | 170/170 | 465/465 | 185/185 | 204/204 | 65 / 105 / 105 |
| cs.AR | 42 | 7/7 | 8/8 | 8/8 | 11/11 | 7 / 0 / 6 |

公告日期只用于证明分类页覆盖，论文归日严格采用 `/abs` 的 v1 提交时间。运行时所有 `new` 页显示 Wednesday, 19 August 2026；逐篇核验后，没有公开条目的 v1 落在 2026-08-19。因此该日准确表述为：**截至 2026-08-20 09:58 CST，arXiv 官方网页未检出 submitted v1 为 2026-08-19 的相关论文**。8 月 14 日的相邻公告组在五类均有非零条目，说明页面解析没有把抓取失败误记为零；后续运行会继续通过三日窗口回查。

主题口径包含权重/激活量化、结构或 token 剪枝、teacher→student 蒸馏、KV/运行时 state 压缩。图像编解码本身、统计稀疏、稀疏标注、检索索引和只在背景中提及压缩的论文被排除。

## 2. 历史去重审计

- `git fetch --prune origin` 成功后，逐一扫描全部 **19** 个 `origin/feature/arxiv-daily-*` 远端分支。
- 只以 `papers/**/<arxiv_id>/tech_analysis.md` 真实存在判断完成，共 **188** 个规范化历史 ID；metadata-only 的 `2607.27951`、`2607.28410`、`2607.28457` 未误算为已完成。
- 三日窗口相关论文共 **19** 篇，其中 **10** 篇已完成、**9** 篇为本次新增；全部 10 个重复均来自 `origin/feature/arxiv-daily-2026-08-19`。

| submitted v1 | 窗口相关 | 历史重复 | 本次新增 |
|---|---:|---:|---:|
| 2026-08-17 | 12 | 10 | 2 |
| 2026-08-18 | 7 | 0 | 7 |
| 2026-08-19 | 0 | 0 | 0 |
| 合计 | **19** | **10** | **9** |

排除的历史 ID：`2608.16010`、`2608.16104`、`2608.16172`、`2608.16236`、`2608.16316`、`2608.16320`、`2608.16333`、`2608.16585`、`2608.16647`、`2608.16756`。

## 3. 本次新增论文与评分

评分顺序为 **精度效果 / 压缩倍率 / 创新性 / 可复现性**（1–10）。精度分评价任务质量证据，压缩分评价参数、状态、FLOPs、延迟或训练资源节省，不等同于论文总体质量。

| 日期 | 论文 | 方向 | 关键结论 | 评分 | 依据 |
|---|---|---|---|---|---|
| 08-17 | [2608.17069 EWP](https://arxiv.org/abs/2608.17069) | 量子模型剪枝/遗忘 | accuracy 0.837；3.96s vs 全重训 65.03s | 8/6/8/8 | 3 seeds 与多基线完整，但仅 4-qubit 模拟 |
| 08-17 | [2608.17129 PROBE](https://arxiv.org/abs/2608.17129) | agent 轨迹蒸馏 | Qwen3-VL-8B 48.1%→67.8%，实机 34.4%→70.0% | 8/5/8/6 | 模拟到实机证据强，未报告结构/延迟倍率 |
| 08-18 | [2608.17336 TileMix](https://arxiv.org/abs/2608.17336) | tile 级混合精度 | 4k prefill 31.80 vs FlashAttn 14.33 K token/s | 8/8/9/6 | 长上下文与 kernel 实证充分，依赖 A100/Triton |
| 08-18 | [2608.17515 Beyond FLOPs](https://arxiv.org/abs/2608.17515) | 能耗感知蒸馏 | CodeT5+ 体积 -86%、能耗最高 -90%，ROUGE-L -13%~-15% | 7/9/8/7 | 实测 20 次且有统计检验，跨硬件泛化有限 |
| 08-18 | [2608.17657 DVBP+OB²C](https://arxiv.org/abs/2608.17657) | 结构剪枝 | 50% MLP pruning，Swin-S 比 VBP +7.33pp | 8/8/9/8 | 多架构、闭式方法、无需训练；LLM 仅附录 |
| 08-18 | [2608.17707 DynaForcing](https://arxiv.org/abs/2608.17707) | 视频蒸馏/图剪枝 | Dyn-Deg 0.31→0.73；GPU·h 7,111→667 | 9/8/9/5 | 动态指标与消融强，但需 14B/多 H100 |
| 08-18 | [2608.17872 DistillPath](https://arxiv.org/abs/2608.17872) | 特征蒸馏 | 22M student 距 632M teacher 0.015 EVA，快 26.6× | 9/10/8/8 | 多 benchmark/设备，teacher 每个仅单 run |
| 08-18 | [2608.17896 Dynamic Compression](https://arxiv.org/abs/2608.17896) | recurrent state 压缩 | 111k dynamic state 优于 3.1M single-pass | 7/9/8/7 | 状态收益巨大，但仅合成任务且保留 raw context |
| 08-18 | [2608.17995 AViTS](https://arxiv.org/abs/2608.17995) | token 选择 | FLUX 最高 9.78× latency；与 step distill 合计 14.76× FLOPs | 9/10/9/6 | 多模型/组合充分，依赖内部 hook 与特定 GPU |

## 4. Qwen3-0.6B 量化复现

本次唯一新增量化论文是 TileMix，复现位于 `scripts/quantization/2608.17336/`。实现从本机完整缓存读取 **Qwen3-0.6B（596,049,920 参数）真实权重**，提取第 0 层真实 Q/K/V，并按 score tile group 在浮点和 INT8 QK 路径间路由；V/PV 保持浮点、所有 causal attention 边保留。

| 请求 coverage | 实际 causal cell coverage | MAE vs FP | cosine |
|---:|---:|---:|---:|
| 25% | 28.87% | 0.00062068 | 0.99978173 |
| 50% | 57.73% | 0.00177458 | 0.99898285 |
| 75% | 84.66% | 0.00540970 | 0.99184644 |
| 100% | 100.00% | 0.01488368 | 0.96480840 |

语法检查、deterministic synthetic self-test 和真实权重运行均通过，输出 `validation=PASS`。论文使用 A100 Triton 的 packed bitmask 与共享 online-softmax fused kernel；本复现为了可移植和可检查而显式构造 score，因此只验证算法数值机制，不声称复现论文吞吐。

## 5. 独立快照与一致性

分支从最新 `origin/main`（`abfe8f2767d8bf881d586718ab4db33fc576be6a`）建立隔离 linked worktree。原工作树的 6 处用户未提交改动未被读取或带入。快照删除了 `origin/main` 自带的 2026-07-28 历史日报；最终：

- `papers/` 只有 README 与 9 篇新增精读；
- `reports/` 只有 README 与本日报；
- `scripts/` 只有 README 与 TileMix 新增复现；
- `metadata/` 只有 README 与本次 2026-08 索引/CSV；
- papers、metadata 的 ID 集合一致，quantization 复现集合恰为 `2608.17336`；
- 9 个新增 ID 与 188 个历史完成 ID 的交集为空。

