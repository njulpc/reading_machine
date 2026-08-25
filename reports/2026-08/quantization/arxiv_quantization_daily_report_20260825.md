# arXiv 模型压缩论文日报（2026-08-25）

**运行日 R**：2026-08-26（Asia/Shanghai）
**固定检索窗口**：2026-08-23 00:00:00 ～ 2026-08-25 23:59:59（按 arXiv `/abs` Submission history 的 v1 日期归档）
**结论**：窗口相关 19 篇，历史重复 0 篇，本次新增 19 篇；逐日为 **9 / 10 / 0**。8 月 25 日准确表述为“截至 2026-08-26 运行时 arXiv 官方网页未检出 v1 落在该日的模型压缩论文”。

## 1. 官方网页全量扫描证据

不使用 arXiv API。完整读取 cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new?show=2000` 与 `recent?show=2000`；十页声明总数均与实际 `dt/dd` 数一致。`new` 页最新公告均为 Tuesday, 25 August 2026，五页 new+cross 跨分类去重后为 839 个 ID，标题和摘要字段 839/839 完整。十页合计跨入口去重 2,761 个 ID。

| 分类 | new 总数（new/cross/repl） | recent 总数 | recent 日期组（条目数） |
|---|---:|---:|---|
| [cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000) / [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 485（164/127/194） | 841 | 08-25:291, 08-24:112, 08-21:127, 08-20:169, 08-19:142 |
| [cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000) / [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 332（141/63/128） | 538 | 08-25:204, 08-24:87, 08-21:76, 08-20:99, 08-19:72 |
| [cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000) / [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 353（185/49/119） | 620 | 08-25:234, 08-24:103, 08-21:86, 08-20:94, 08-19:103 |
| [cs.AI new](https://arxiv.org/list/cs.AI/new?show=2000) / [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 585（165/197/223） | 1,063 | 08-25:362, 08-24:200, 08-21:145, 08-20:186, 08-19:170 |
| [cs.AR new](https://arxiv.org/list/cs.AR/new?show=2000) / [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 21（10/6/5） | 49 | 08-25:16, 08-24:6, 08-21:12, 08-20:8, 08-19:7 |

`recent` 明确显示窗口外 08-21、08-20、08-19 阳性日期组，证明页面并非空白或截断。37 个广义语义候选逐篇打开官方 `/abs` 核验 v1、主/交叉分类和摘要；最终 19 篇符合模型/状态/表示/上下文压缩或部署型蒸馏。22 篇有官方 HTML 全文；2608.22237 无 HTML，改读官方 v1 PDF（9 页）。

## 2. 历史去重审计

- fetch 后完整扫描 **25** 个 `origin/feature/arxiv-daily-*` 历史分支；今日 `origin/feature/arxiv-daily-2026-08-26` 不存在，不涉及续跑混淆。
- 逐分支执行 `git ls-tree -r --name-only`，仅以真实 `papers/**/<id>/tech_analysis.md` 计完成，得到 **223** 个规范化历史 ID。
- metadata 交叉核验得到 226 个 ID；2607.27951、2607.28410、2607.28457 只有 metadata、没有真实分析，未计完成。
- 窗口内先跨日期、分类、入口和语义表达按规范化 ID 去重；最终 19 个 ID 与历史集合交集为空。
- **逐日原始相关数**：2026-08-23 = 9，2026-08-24 = 10，2026-08-25 = 0。
- **历史重复 ID / 来源分支**：无。**排除重复数**：0。**最终新增数**：19。

## 3. 新增论文总览与评分

评分均为 1–10；“精度效果”看压缩后质量保持，“压缩倍率”结合 token/参数/内存/通信收益，“创新性”看方法新颖度，“可复现性”看公开细节、依赖和算力门槛。

| 日期 | ID | 方向 | 一句话结论 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 |
|---|---|---|---|---|---|---|---|
| 08-23 | [2608.22237](https://arxiv.org/abs/2608.22237) | 上下文压缩 | SparseRead 在准入前稀疏读取，最高省 92.9% token / 89.0% 时间且质量不降。 | 8（质量持平/提升） | 10（最高 92.9%） | 8（前置准入） | 8（训练自由） |
| 08-23 | [2608.22322](https://arxiv.org/abs/2608.22322) | 量化 | 状态感知 AL8/16 将 AdamW 状态 8392.7→2119.2 MiB，PPL 72.90 vs FP32 72.48。 | 9（差 0.42 PPL） | 9（约 74.8%） | 8（状态拓扑） | 7（训练成本高） |
| 08-23 | [2608.22344](https://arxiv.org/abs/2608.22344) | 剪枝 | POP 在训练中极化 opacity，避免 3DGS 先膨胀再剪枝。 | 8（质量可比） | 8（显著减 Gaussian） | 7（内生剪枝） | 7（需 3DGS 训练） |
| 08-23 | [2608.22364](https://arxiv.org/abs/2608.22364) | 蒸馏 | on-policy teacher 修复加速 WAM student，两任务成功率 0→58.3%、16.7→33.3%。 | 7（仅两任务） | 7（加速 student） | 8（部署分布） | 6（需环境/teacher） |
| 08-23 | [2608.22368](https://arxiv.org/abs/2608.22368) | 蒸馏 | 对齐 detector 接口，87 分钟无标签完成 softmax→linear，延迟 -62%、显存 -49%。 | 9（匹配监督模型） | 8（延迟/显存双降） | 9（接口蒸馏） | 8（流程清楚） |
| 08-23 | [2608.22378](https://arxiv.org/abs/2608.22378) | 量化/硬件 | NSGA-II 搜索近似 FP PE，报告 66%–92% 面积、60%–93% 功耗节省。 | 8（CNN 精度可比） | 9（PPA 高收益） | 7（电路联合搜索） | 5（需硬件工具） |
| 08-23 | [2608.22465](https://arxiv.org/abs/2608.22465) | 压缩基准 | M³ISR 用 25 场景、6 路 1080p 视图统一 3D/4DGS 压缩与流式评价。 | 7（benchmark） | 8（含 rate-distortion） | 7（受控几何） | 9（数据/赛道明确） |
| 08-23 | [2608.22526](https://arxiv.org/abs/2608.22526) | 剪枝 | 同时 read/store sparse，VOS 最高 FPS +38.8%、峰值显存 -13.1%。 | 8（J&F 有竞争力） | 7（系统中等） | 8（双路径 token） | 8（训练自由 hook） |
| 08-23 | [2608.22643](https://arxiv.org/abs/2608.22643) | 稀疏推理 | 利用 82%–85% 跨 token 活跃延续，只从 NVMe 预取 delta rows，快 7.9–12×。 | 8（保持稀疏模型） | 9（工作集显著减） | 8（存储感知） | 5（硬件/运行时门槛） |
| 08-24 | [2608.22704](https://arxiv.org/abs/2608.22704) | KV cache | anchor/tidal/fixed 三态 cache 只留 20% 音频 token 在 GPU 仍接近 Full Cache。 | 9（近满缓存） | 8（GPU token -80%） | 9（可召回淘汰） | 6（需跨层存储） |
| 08-24 | [2608.22745](https://arxiv.org/abs/2608.22745) | 状态压缩 | DiaRelay 用常量大小 memory 传递远距情绪证据，仅增 7.1M 参数。 | 8（MELD SOTA） | 8（历史常量化） | 7（有界 relay） | 7（标准 ERC） |
| 08-24 | [2608.22854](https://arxiv.org/abs/2608.22854) | 蒸馏 | ADAPT 一次蒸馏覆盖 L 个尺寸 × K 个 post-training 变体。 | 8（平滑插值） | 8（训练摊销） | 9（双轴模型族） | 6（同源模型假设） |
| 08-24 | [2608.22963](https://arxiv.org/abs/2608.22963) | 上下文剪枝 | reverse-KL 判断 reasoning 可删性，移除 37.89%–64.58% token 且平均准确率最高。 | 9（优于剪枝基线） | 8（最高 64.58%） | 8（未来分布判据） | 6（双 replay 昂贵） |
| 08-24 | [2608.23018](https://arxiv.org/abs/2608.23018) | 量化/通信 | LoRA residual 的 rank-2r/4r 结构支持量化 SVD，uplink -93.5%、总通信 -83.7%。 | 9（无性能下降） | 10（通信大幅降低） | 8（rank 推导） | 7（需 split 环境） |
| 08-24 | [2608.23048](https://arxiv.org/abs/2608.23048) | 剪枝 | O(M) logits 学 N:M mask，比组合式方案少 1.5–8.75× mask 参数。 | 8（Qwen2.5 竞争力） | 8（优化开销显降） | 8（无放回采样） | 7（需 mask 学习） |
| 08-24 | [2608.23144](https://arxiv.org/abs/2608.23144) | 量化 | 0.162 bit/weight seed sidecar 为 INT4 修复 88.2% PPL gap，sidecar 仅 BF16 payload 0.8%。 | 9（多指标改善） | 9（极小 sidecar） | 9（seed residual） | 8（算法可小张量验证） |
| 08-24 | [2608.23167](https://arxiv.org/abs/2608.23167) | token 压缩 | local/middle/tail 结构化 suffix + 跨步复用，组合长序列最高 72.81×。 | 8（多数配置提升） | 9（组合上界高） | 8（结构分区） | 7（需 DLM） |
| 08-24 | [2608.23253](https://arxiv.org/abs/2608.23253) | 剪枝 | 证据三态与跨层冲突融合，64 token 时吞吐 2.09×、保留 90.6% 聚合性能。 | 8（可调退化） | 8（2.09×） | 9（证据融合） | 9（训练自由） |
| 08-24 | [2608.23296](https://arxiv.org/abs/2608.23296) | KV cache | sigmoid normalization 缓解 soft-gate 到 hard eviction 的错配。 | 8（PPL 变化近零） | 8（物理删除） | 9（改 substrate） | 7（GPT-2 规模） |

## 4. 量化复现说明

本次 4 个量化方向均在 `scripts/quantization/<id>/` 提供 `README.md` 与 `demo.py`：2608.22322（AL optimizer state）、2608.22378（近似 variable-bit PE）、2608.23018（量化低秩 residual）、2608.23144（activation-weighted seeded residual repair）。复现目标统一为 Qwen3-0.6B；脚本包含真实 checkpoint 发现、论文关键数值路径与小张量自测。运行结果及不可复现边界写入各 README，不把软件模拟声称为论文硬件 PPA 或完整训练结果。

## 5. 口径与边界

“相关”要求论文贡献直接压缩模型参数、优化状态、通信表示、KV/上下文/token，或把 teacher 转成明确更快/更小 student。只借用 distillation 做偏好数据生成、解释性 surrogate 或 FL 校准而没有压缩目标的论文不计入。本日报的实验数字均来自官方摘要/全文；没有可比统一倍率时明确保留定性结论。
