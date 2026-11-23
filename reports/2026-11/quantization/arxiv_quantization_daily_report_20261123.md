# arXiv 模型压缩论文日报：2026-11-23

运行日：2026-11-24（Asia/Shanghai）。固定窗口：2026-11-21 00:00:00 至 2026-11-23 23:59:59，北京时间。日期依据官方 /abs 的 v1 UTC 时间转换，公告日期不代替提交日期。

## 检索与去重结论

| 实际提交日期（北京时间） | 窗口全主题记录 | 相关论文 | 历史已分析重复 | 本次新增 |
|---|---:|---:|---:|---:|
| 2026-11-21 | 59 | 5 | 0 | 5 |
| 2026-11-22 | 0 | 0 | 0 | 0 |
| 2026-11-23 | 0 | 0 | 0 | 0 |
| 合计 | 59 | 5 | 0 | 5 |

11-22、11-23 的准确表述：**截至运行时 arXiv 官方网页未检出**。这不代表后台不存在未公告投稿，下次三天窗口继续回查。检索时列表最新公告为 11-23，recent 分组为 11-23、20、19、18、17；跨周末不能依公告分组直接计零。

fetch 成功后，对全部 54 个历史 origin/feature/arxiv-daily-* 分支逐一执行 ls-tree，读取各 metadata 索引交叉核验，得到 621 个有真实 tech_analysis.md 的规范化 ID。仅 metadata 存在的 2607.27951、2607.28410、2607.28457 不计完成。当日分支此前不存在，未混入历史集合。

跨分类去重后全列表 3629 个 ID；全部官方 abs 可解析、无最终错误，其中缓存均校验 SHA256。本轮已逐条人工语义阅读窗口内 59 条标题和摘要；窗口外按官方 v1 日期排除，未对全部窗口外记录重复进行人工主题审阅。关键词只作复核，不作窗口内召回门槛。主题包含参数压缩、KV 压缩、token 缩减及有实际删除实验的剪枝机制研究。

历史重复 ID 及来源分支：空。最终新增：2611.27788、2611.27901、2611.27911、2611.27962、2611.27973。五者与历史集合交集为空。

## 官方列表覆盖证据

每个入口使用 show=2000&skip=0；总数均低于2000，无后续页。new 的新提交、cross submissions、replacement 三组均按实际 dt 数核验；recent 各日期分组逐一核验。以下为页面显示总数与实际解析数，二者相同。

| 分类 | new 显示/实读 | recent 显示/实读 | 官方入口 |
|---|---:|---:|---|
| cs.LG | 304/304 | 1274/1274 | [new](https://arxiv.org/list/cs.LG/new?show=2000&skip=0) · [recent](https://arxiv.org/list/cs.LG/recent?show=2000&skip=0) |
| cs.CL | 142/142 | 597/597 | [new](https://arxiv.org/list/cs.CL/new?show=2000&skip=0) · [recent](https://arxiv.org/list/cs.CL/recent?show=2000&skip=0) |
| cs.CV | 271/271 | 1156/1156 | [new](https://arxiv.org/list/cs.CV/new?show=2000&skip=0) · [recent](https://arxiv.org/list/cs.CV/recent?show=2000&skip=0) |
| cs.AI | 351/351 | 1383/1383 | [new](https://arxiv.org/list/cs.AI/new?show=2000&skip=0) · [recent](https://arxiv.org/list/cs.AI/recent?show=2000&skip=0) |
| cs.AR | 19/19 | 112/112 | [new](https://arxiv.org/list/cs.AR/new?show=2000&skip=0) · [recent](https://arxiv.org/list/cs.AR/recent?show=2000&skip=0) |

完整分组、54 分支 SHA、59 条窗口记录的判定及相邻日阳性对照保存在 metadata/2026-11/retrieval_audit.json。PLoQ 2611.27092、DWE 2611.27131、量化奖励模型研究 2611.27155 的 v1 均在北京时间 11-20，作为相邻日阳性对照，未纳入本日分支。未调用 arXiv 官方 API。

边界复核：2611.27855 保留全部 patch，研究 anchor routing；2611.27951 研究 OT 稀疏注意力算子，均不作为既有模型压缩流程纳入。2611.27911 有真实连续层移除与 PPL 对照，作为剪枝机制研究纳入；2611.27788 缩减输入 token 计算，列 other，不能宣称权重压缩。

## 论文总览

| ID | 标题 | v1 北京时间 | 方向 | 一句话结论 |
|---|---|---|---|---|
| [2611.27973](https://arxiv.org/abs/2611.27973) | MemOnce: A Scalable Memory Architecture for Large Language Models | 02:51:29（11-21） | other | 跨层和时间压缩记忆，再按需恢复KV；倍率限于缓存口径。 |
| [2611.27962](https://arxiv.org/abs/2611.27962) | Model Carving: Training Transformers That Optimize Their Own Topology | 02:41:39（11-21） | pruning | 训练中删除低收益子层，将算力再分配为训练token。 |
| [2611.27911](https://arxiv.org/abs/2611.27911) | Functional Depth Is Learned: Isolating the Computation That Layers Produce Only Together | 01:50:26（11-21） | pruning | 相似表征不保证可安全剪层，协作度提供互补风险信号。 |
| [2611.27901](https://arxiv.org/abs/2611.27901) | QuantStream3D: Geometry-Aligned Low-Bit KV Cache Quantization for Streaming Visual Geometry Transformers | 01:38:48（11-21） | quantization | 混合精度与几何蒸馏缓解流式KV误差；Qwen仅完成推理组件迁移。 |
| [2611.27788](https://arxiv.org/abs/2611.27788) | When Does Looking Closer Pay Off? Simple Foveated ViTs for Fine-Grained Recognition | 00:20:23（11-21） | other | 选择性细化区域减少token计算，实际延迟收益低于算术降幅。 |

## 评分与依据（1–10，编辑判断）

精度看质量保持与对照；压缩看实际资源节省；创新看方法贡献；可复现性看材料与本地覆盖。各资源口径不可横向当作同一种倍率。低分可以表示未报告，而不表示算法无价值。

| ID | 精度 | 压缩 | 创新 | 可复现性 | 依据 |
|---|---:|---:|---:|---:|---|
| 2611.27973 | 8 | 9 | 8 | 6 | 4B记忆均分+5.77点，1M缓存1313倍；含额外训练，未本地跑架构。 |
| 2611.27962 | 8 | 6 | 9 | 6 | 等训练算力对照；最大34%推理FLOP下降，循环权重不必减少；完整预训练成本高。 |
| 2611.27911 | 6 | 2 | 8 | 7 | 35组删除干预；没有可部署高压缩系统，枚举代价高；设置较清楚。 |
| 2611.27901 | 8 | 8 | 8 | 5 | 5.05倍KV实测与几何任务证据；本地真实Qwen测试通过，但几何QAD未复现。 |
| 2611.27788 | 7 | 5 | 6 | 7 | 44%算术减少，Aircraft约-0.53点；两种子/匹配训练对照，权重不压缩。 |

## 复现与证据边界

唯一新增量化论文的实现位于 scripts/quantization/2611.27901/，含 README.md、demo.py、results.json。真实 Qwen3-0.6B CPU/FP32、256 token、64-token chunk：原生分块与原模型最大 logit 差0；量化历史后的 KL=0.4427199364，top-1一致率91.1458%。实际打包缓存6,520,832字节，相对同形状FP32为9.005倍，相对FP16字节换算为4.5025倍。小张量打包、常量组、尾组和正交内积检查通过。

这不是基准准确率或原论文完整复现。Qwen没有相机/深度/点云头，未复现几何校准、QAD或Triton融合GPU内核。原论文视觉蒸馏训练不能用文本KL替代后宣称完成。本轮已完成推理量化组件的真实运行，完整复现仍有上述未完成项。

## 分支独立性与清理

本地分支 feature/arxiv-daily-2026-11-24 严格从最新 origin/main（abfe8f2767d8bf881d586718ab4db33fc576be6a）创建；未继承feature提交。仅删除main自带的2026-07-28日报。papers保留README及本次5篇；reports保留README及本日报；scripts保留README及本次1个量化目录；metadata按2026-11重建，不累计历史paper条目。原工作树未提交文件不参与提交。

机器可核验的源分支SHA与检索审计随metadata保存；提交SHA与远端验证结果由运行终报给出。
