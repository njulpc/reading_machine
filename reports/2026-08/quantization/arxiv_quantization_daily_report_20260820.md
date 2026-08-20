# arXiv 模型压缩论文日报（2026-08-20）

> 运行日：2026-08-21（Asia/Shanghai）  
> 固定检索窗口：2026-08-18 00:00 至 2026-08-20 23:59（按 arXiv `/abs` Submission history 的 v1 时间归日）  
> 结论：窗口内确认模型压缩相关论文 19 篇；历史已完成 7 篇，本次新增 12 篇。

## 一、结果总览

| v1 实际提交日 | 相关论文 | 历史重复 | 本次新增 |
|---|---:|---:|---:|
| 2026-08-18 | 7 | 7 | 0 |
| 2026-08-19 | 12 | 0 | 12 |
| 2026-08-20 | 0 | 0 | 0 |
| **合计** | **19** | **7** | **12** |

2026-08-20 的“0”表示：截至本次运行时，在下述已完整覆盖的 arXiv 官方网页中，没有发现 v1 时间落在该自然日且满足模型压缩语义口径的论文；不是把抓取失败记为零。公告日仅用于建立候选全集，最终归日逐篇以 `/abs/<id>` 的 v1 时间为准。

方向分布：知识蒸馏 6 篇、剪枝/稀疏 3 篇、量化 1 篇、其他压缩（KV/子 token）2 篇。

## 二、官方网页覆盖审计

检索未调用 arXiv API。完整读取 `cs.LG`、`cs.CL`、`cs.CV`、`cs.AI`、`cs.AR` 的 `new` 与 `recent` HTML，统一使用 `show=2000`，覆盖 new submissions 与 cross-lists；随后读取候选的官方 `/abs` 页面，并下载 12 篇新增论文的官方 PDF 精读。

### recent 页面

| 分类 | 入口 | 页面总数 | 08-20 | 08-19 | 08-18 | 窗口外阳性对照 |
|---|---|---:|---:|---:|---:|---|
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 980 | 169 | 142 | 374 | 08-17: 138；08-14: 157 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 490 | 99 | 72 | 156 | 08-17: 62；08-14: 101 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 662 | 94 | 103 | 269 | 08-17: 89；08-14: 107 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1210 | 186 | 170 | 465 | 08-17: 185；08-14: 204 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 42 | 8 | 7 | 8 | 08-17: 8；08-14: 11 |

每页显示数等于页面声明总数，无遗漏分页。窗口公告组跨分类规范化去重后共 1,727 个 ID；1,727 个官方 `/abs` 页面全部成功解析。按 v1 时间，其中 595 条落在窗口（08-18: 334，08-19: 261，08-20: 0），再逐条读取标题与摘要作语义筛选。

### new 页面

| 分类 | 入口 | 总数 | new submissions | cross-lists | replacements |
|---|---|---:|---:|---:|---:|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 233 | 91 | 78 | 64 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 141 | 72 | 27 | 42 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 152 | 83 | 11 | 58 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 267 | 67 | 119 | 81 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 13 | 8 | 0 | 5 |

五个 `new` 页面均显示 Thursday, 20 Aug 2026，页面实际展示数与声明总数一致。筛选时关键词只用于排序复核；每条摘要均按语义判断。纳入权重/激活量化、结构或注意力稀疏、teacher→student 蒸馏、KV/运行时状态压缩；排除图像/数据压缩、统计意义稀疏、稀疏标签、只使用现成量化而贡献在普通系统调度的论文。比如 APEX 的核心是双稀疏 SNN 加速器，虽含 INT4/INT8 配置，仍归为稀疏；仅使用现成 INT4 的分布式流水线不纳入。

## 三、历史去重审计

`git fetch --prune origin` 后枚举了全部 20 个 `origin/feature/arxiv-daily-*` 远端分支。逐分支对 `git ls-tree -r --name-only` 结果提取真实 `papers/**/<arxiv_id>/tech_analysis.md`，规范化去除版本后缀后得到 197 个历史已完成 ID；同时读取 `metadata/**/papers_index.json` 交叉核验。`2607.27951`、`2607.28410`、`2607.28457` 仅存在于旧 metadata、没有真实精读文件，因此没有误判为已完成。

本窗口的 7 个重复 ID 均来自 `origin/feature/arxiv-daily-2026-08-20`：`2608.17336`、`2608.17515`、`2608.17657`、`2608.17707`、`2608.17872`、`2608.17896`、`2608.17995`。本次 12 个新增 ID 与 197 个历史完成 ID 的交集为零。

## 四、本次新增论文

评分顺序为“精度效果 / 压缩倍率 / 创新性 / 可复现性”，均为 1–10 分。精度分衡量效果证据强度，不等同单一 accuracy；压缩分同时考虑实际内存、计算或部署收益。

| ID | 方向 | 核心结论 | 评分 | 评分依据 |
|---|---|---|---|---|
| [2608.18399](https://arxiv.org/abs/2608.18399) | 蒸馏 | attention transfer 几乎复制教师注意力，但分布外鲁棒性差距主要来自训练成熟度/特征，而非可见注意力结构。 | 8/8/8/7 | 14× 少参数、10× 少数据；KL 0.0170、cosine 0.989；三 seed 中两组延训后差距低于预注册阈值。 |
| [2608.18410](https://arxiv.org/abs/2608.18410) | 其他 | RoleSub 保留 token、路由 value 子空间，在 33/36 个同预算设置胜过 token-only，并把总 KV 降到 9.2–11.3%。 | 8/10/9/6 | 压缩激进且跨 LIBERO 四套件；论文未给 kernel 级延迟。 |
| [2608.18484](https://arxiv.org/abs/2608.18484) | 稀疏 | SparsePR 用响应耦合分区和 probe 拟合残差，在 22–26% 执行 pair 密度下保持质量并实现 1.48–2.61× 端到端加速。 | 9/9/9/6 | 四种视频/世界模型；Wan 延迟 1650→917 秒；probe 约 1.1%，但需要模型特定集成。 |
| [2608.18486](https://arxiv.org/abs/2608.18486) | 其他 | WhiteMatter 把全层状态混成 k 个 KV channel，半 KV cache 时仍保留大部分性能增益。 | 8/7/9/5 | k=8 时 PPL 20.377，优于同 cache LCKV 21.461；训练/预填充成本约 2.32×/3.05×。 |
| [2608.18578](https://arxiv.org/abs/2608.18578) | 量化 | bitsandbytes INT4 会放大语义相似上下文中的主动干扰，Qwen 高干扰准确率由 81.0% 降到 68.3%。 | 8/8/8/8 | 三模型、配对检验；same-key intrusion 21.5→24.6%，p=4.8e-7；代码公开且本次有 Qwen3 真模型复现。 |
| [2608.18590](https://arxiv.org/abs/2608.18590) | 蒸馏 | FD-CanKD 联合预测、非局部关系与频域对齐，部署时移除全部蒸馏模块。 | 8/7/8/7 | 19.7M 学生 +20 epoch 达 48.87 mAP50:95，接近 49.58 教师并高于 45.63 学生基线。 |
| [2608.18819](https://arxiv.org/abs/2608.18819) | 剪枝 | 将强表达 lottery ticket 的存在性与随机剪枝概率推广到关系/时序 GNN，并连接表达性与优化。 | 7/7/9/7 | 理论贡献扎实并有合成、时序、分子实验；缺少通用大模型部署数据。 |
| [2608.18849](https://arxiv.org/abs/2608.18849) | 蒸馏 | GEAR 先用合成 query 扩覆盖，再用真实标签/OOF 教师预测锚定，将 TFM 蒸馏为 CPU 学生。 | 9/9/9/8 | AUC 提升约 1.19–2.00 点；推理快 57–2866×、峰值内存低 1.9–3.3×。 |
| [2608.18952](https://arxiv.org/abs/2608.18952) | 蒸馏 | rEDMRec 把教师推理压入四类可编辑经验记忆，使轻量学生在线无需再次调用教师。 | 7/7/8/6 | 十种学生上 HR@1 普遍改善；记忆重复率 18.0→10.6%，但维护仍依赖 LLM controller。 |
| [2608.19046](https://arxiv.org/abs/2608.19046) | 稀疏 | APEX 将 PASC-IF 与输入/权重双稀疏数据流结合，以较低硬件开销保持精确 SNN 推理。 | 9/8/8/5 | 最佳精度配置平均节能 40%，功耗开销 1.3–5.4%、面积 2.1–2.7%；依赖硬件评估链。 |
| [2608.19098](https://arxiv.org/abs/2608.19098) | 蒸馏 | Open-MOPD 发现多教师 OPD 的关键不是梯度冲突，而是 token 优化预算错配，并用三项机制修复。 | 9/7/9/6 | headroom 恢复率 35.6→83.4%，总分 28.05→31.24；需多教师 RL 训练资源。 |
| [2608.19181](https://arxiv.org/abs/2608.19181) | 蒸馏 | GC-OPD 以组内标准化的 verifier–teacher 残差校准 token 信号，改善长上下文推理。 | 8/6/8/7 | Qwen3-4B/8B 五基准均值 39.31→40.47、43.56→44.65；不直接压模型尺寸。 |

所有论文的六节精读位于 `papers/2026-08/<direction>/<id>/tech_analysis.md`，数字均来自官方摘要或已下载 PDF；没有全文不可得的新增论文。

## 五、量化论文 Qwen3-0.6B 复现

复现目录：`scripts/quantization/2608.18578/`。代码真实加载本机缓存的 Qwen3-0.6B（596,049,920 参数），实现同 key 连续重绑定、word/numeric 对照、候选受限末 token 评分，以及三条数值路径：未 fake-quant 基线、per-output-channel 对称 INT8、NF4 codebook + 64-weight block + 256-scale double quant 近似。

完整命令（12 trials × 5 levels × 2 tasks × 3 modes）通过 `self_test=PASS`。INT8/NF4 各量化 440,401,920 个权重元素，权重 MAE 为 0.00021444/0.00200510。word-type 在 level 8 的准确率为基线 0.250、INT8 0.333、NF4 0.167；旧值 intrusion 为 0.750/0.667/0.833。numeric control 在 level 8 的准确率为 0.500/0.500/0.250。小样本复现了“干扰随重绑定增大、NF4 word-type 最明显”的方向，但不把它冒充论文效应量。

本机无 CUDA/MPS 与 bitsandbytes，因此采用真实 Qwen3 权重上的 CPU fake-quant，不能验证 bitsandbytes 原生 kernel、文件压缩或吞吐；详细命令、全部分档结果和边界见复现 README。

## 六、独立快照说明

本分支严格从最新 `origin/main` 创建隔离 linked worktree。清除了基线携带的 2026-07 历史日报；`papers/` 只包含 12 篇本次新增精读，`reports/` 只包含本日报，`scripts/quantization/` 只包含新增量化论文复现，`metadata/` 只重建 2026-08 的本次 12 篇索引与关键词表。提交前后均执行集合一致性、历史零交集、语法/自测、JSON/CSV 与 Git 基线检查。
