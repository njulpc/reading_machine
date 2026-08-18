# arXiv 模型压缩论文日报（2026-08-18）

> 运行时间：2026-08-19 02:25 CST（Asia/Shanghai）
> 固定检索窗口：2026-08-16 00:00:00 至 2026-08-18 23:59:59（三个完整自然日）
> 主日报日期：2026-08-18

## 1. 检索与公告核验

通过 arXiv API 的 `submittedDate:[YYYYMMDD0000 TO YYYYMMDD2359]` 分日查询；关键词覆盖 quantization/quantize/low-bit/model compression/compress/pruning/sparsity/knowledge distillation/KV cache compression/mixed precision/GPTQ/AWQ，并扩展 distillation、binary、INT8/INT4/FP4、token pruning、attention sparsification、KV cache eviction。每一天同时执行无关键词全集查询。

| submittedDate | API 全量 | 扩展关键词候选 | 阅读摘要/全文后真实相关 | 历史重复 | 本次新增 |
|---|---:|---:|---:|---:|---:|
| 2026-08-16 | 524 | 58 | 12 | 0 | 12 |
| 2026-08-17 | 915 | 94 | 10 | 0 | 10 |
| 2026-08-18 | 0 | 0 | 0 | 0 | 0 |
| 合计 | 1439 | 152 | 22 | 0 | 22 |

2026-08-18 的精确表述是：**截至 2026-08-19 02:25 CST，公开 API 未检出 submittedDate 为 2026-08-18 的记录**，不是断言该日最终不会出现论文。相同语法的窗口外阳性对照 2026-08-14 返回全量 **911**、扩展关键词 **99**，说明查询没有因语法错误静默归零。公告页也已核对：[cs.LG new](https://arxiv.org/list/cs.LG/new?show=2000)、[cs.CL new](https://arxiv.org/list/cs.CL/new?show=2000)、[cs.CV new](https://arxiv.org/list/cs.CV/new?show=2000) 在运行时显示 Tuesday, 18 August 2026 的批次；后续运行将继续用三天窗口回查 8/18。

排除口径：物理/数学 quantization、图像/视频编码本身、数据库/检索索引剪枝、普通二进制术语，以及只把压缩当背景而没有模型压缩贡献的工作。入选项必须直接研究权重/激活低比特、参数/注意力/token 稀疏、蒸馏、KV/serving state 压缩或其可靠性。

## 2. 历史去重审计

- `git fetch --prune origin` 成功后，逐一执行 `git ls-tree -r --name-only` 扫描全部 **18** 个 `origin/feature/arxiv-daily-*` 远端分支。
- 只以 `papers/**/<arxiv_id>/tech_analysis.md` 的真实存在判定已完成，共 **166** 个规范化历史 ID；`v1/v2` 后缀已移除。
- metadata 交叉核验发现 `2607.27951`、`2607.28410`、`2607.28457` 仅在索引中、没有真实 `tech_analysis.md`，因此没有错误计入历史完成集。
- 三天窗口在跨日期、跨关键词规范化后为 22 个真实相关 ID；与 166 个历史 ID 的交集为空。`excluded_duplicate_ids=[]`，没有“来源分支”可列。
- 今日远端分支此前不存在，不涉及续跑状态混入；所有历史 feature 仅只读。

## 3. 新增论文与评分

评分顺序为 **精度效果 / 压缩倍率 / 创新性 / 可复现性**（1–10）。精度分衡量任务质量或可靠性证据；压缩分衡量内存/算力/延迟的实证强度，不等同于论文质量。

| 日期 | 论文 | 方向 | 关键结果 | 评分 | 评分依据 |
|---|---|---|---|---|---|
| 08-16 | [2608.15475 Bit-Flip Attacks on VLA](https://arxiv.org/abs/2608.15475) | 量化安全 | 1–5 个定向 bit 可使部分动作头失败；K=100 实机 0/20 | 7/4/8/6 | 安全效应强但不是压缩增益；有 ancillary code，实机栈复现难 |
| 08-16 | [2608.15516 UniFed-VLM](https://arxiv.org/abs/2608.15516) | 蒸馏 | VQA 0.743；去 TCoD 降 3.6 点 | 8/5/7/6 | 多任务消融充分；主要节省协作成本而非直接模型倍率 |
| 08-16 | [2608.15522 Sync-aware Sparse Attention](https://arxiv.org/abs/2608.15522) | 稀疏注意力 | Ovi 1.992×，PSNR 25.6857、Sync-C 4.606 | 8/7/8/6 | 质量/同步/速度联合报告；需双分支生成器中间状态 |
| 08-16 | [2608.15531 FlashQuant](https://arxiv.org/abs/2608.15531) | W4A16 | 对 BF16 2.74–4.18×，对未融合基线最高 1.53× | 7/8/7/8 | 系统收益清晰；核心分解易复现，CUDA 性能依赖硬件 |
| 08-16 | [2608.15567 SchurQuant](https://arxiv.org/abs/2608.15567) | 2-bit PTQ | Qwen3-4B SchurOpt +11.88pp；最强基线 +9.65pp | 9/9/9/7 | 极低比特增益大且覆盖 8 模型；全流程校准成本较高 |
| 08-16 | [2608.15602 FluxBin](https://arxiv.org/abs/2608.15602) | 二值量化 | 4×内存、最高 5.92×速度、10.19×能耗节省 | 8/10/9/7 | 算法-kernel 协同完整；专用 CUDA/能耗环境限制复制 |
| 08-16 | [2608.15636 SpecVLA](https://arxiv.org/abs/2608.15636) | 混合精度 | 量化 sVLA 短序列验证，全模型长序列预测 | 7/8/8/5 | 可靠性设计新颖；摘要无统一倍率且需机器人专用硬件 |
| 08-16 | [2608.15660 ASCEND](https://arxiv.org/abs/2608.15660) | FedKD/梯度压缩 | 动态策略在 MNIST/CIFAR-10 多带宽保持精度-时间折中 | 7/7/7/6 | 配置覆盖多但无单一通用倍率；候选压缩器可复用 |
| 08-16 | [2608.15693 Large Models for Small Devices](https://arxiv.org/abs/2608.15693) | 部署审计 | 剪枝产物可反增 21–49%，树莓派延迟最高 3.4× | 8/8/8/9 | 真实硬件反例价值高，代码/产物开放，非单一新算法 |
| 08-16 | [2608.15787 Routing Divergence](https://arxiv.org/abs/2608.15787) | 自蒸馏分析 | routing term 范围 1.6×，residual exposure 3.2× | 7/2/8/7 | 机制因果诊断强；不提供部署压缩倍率 |
| 08-16 | [2608.15797 KV-Rescue](https://arxiv.org/abs/2608.15797) | KV eviction | B=64 恢复 87% 精度损失，少生成 43% token | 9/8/9/6 | 精度/退化成本同时改善；需额外全上下文 helper |
| 08-16 | [2608.15810 Runtime Compression Risk](https://arxiv.org/abs/2608.15810) | serving state | 352,333 次 admission 有效，fallback 0.30→0.14 | 8/7/9/5 | 形式化证据强；实现与流量假设复杂、边界仍保守 |
| 08-17 | [2608.16010 BRIDGE](https://arxiv.org/abs/2608.16010) | 剪枝 | 结构化 +4.77%，树莓派 VGG16 最高 43.2× | 8/9/9/7 | 边界反向恢复新颖且有设备测量；需搜索/微调 |
| 08-17 | [2608.16104 Nexus](https://arxiv.org/abs/2608.16104) | INT4/FP4 + MoE | 7B/激活1.6B；对 SD3-Medium 2.8×、内存1.7× | 8/9/8/5 | 三类技术协同；单作者稿、生成训练复现成本高 |
| 08-17 | [2608.16172 SparkVLA](https://arxiv.org/abs/2608.16172) | token 剪枝 | RoboCerebra 47.12%，实机平均 69.3% | 9/7/8/5 | 长时程成功率证据强；真实 token/延迟节省依赖 VLA 栈 |
| 08-17 | [2608.16236 Sparse CI Privacy](https://arxiv.org/abs/2608.16236) | 激活稀疏 | rate 降得远快于泄露，positions 单独可重建/识别 | 6/8/8/8 | 暴露压缩隐私盲点；未给普适精度提升但审计代码开放 |
| 08-17 | [2608.16316 Latent-OPD](https://arxiv.org/abs/2608.16316) | 蒸馏 | 相对 vanilla OPD 六基准平均最高 +2.6pp | 9/6/8/5 | 多帧预算/六基准稳定；需访问教师隐藏状态 |
| 08-17 | [2608.16320 StreamOPD](https://arxiv.org/abs/2608.16320) | 蒸馏 | StreamingBench 77.9→83.9，距9B教师0.3点 | 9/5/8/7 | 固定推理协议归因清楚；训练仍需教师且无模型大小倍率 |
| 08-17 | [2608.16333 SOPD](https://arxiv.org/abs/2608.16333) | 蒸馏 | ALFWorld Seen 65.72→84.29，数学平均 +10 点 | 9/6/9/7 | step 粒度统一 SFT/OPD；教师调用量较大 |
| 08-17 | [2608.16585 SQuad](https://arxiv.org/abs/2608.16585) | 注意力蒸馏 | VBench 83.20≥83.08；67× FLOPs、11×注意力、2×端到端 | 10/10/9/5 | 质量无损且两级压缩强；25页视频蒸馏与 kernel 复现昂贵 |
| 08-17 | [2608.16647 OPD Generalization](https://arxiv.org/abs/2608.16647) | 蒸馏分析 | 同源教师跨语言/长度迁移，多教师出现能力跷跷板 | 7/3/9/6 | 控制研究启发强；不直接给压缩倍率 |
| 08-17 | [2608.16756 BinRVR](https://arxiv.org/abs/2608.16756) | 1-bit 量化 | 计算/参数约降 96%，性能约降 4% | 8/10/8/6 | 多任务视觉验证且倍率极高；需二值 kernel 与 RAW 数据 |

## 4. Qwen3-0.6B 量化复现

对 7 篇以量化为核心、且不是综述的论文建立独立目录。所有脚本都读取本机完整缓存的 **Qwen3-0.6B `model.safetensors` 真实权重**；依赖在 `/private/tmp` 一次性虚拟环境中安装，未改变仓库或系统环境。

| 论文 | 复现核心 | 真实验证结果 |
|---|---|---|
| 2608.15475 | per-row INT8 + 梯度排序 two's-complement bit flip | MSE 1.68e-5 → 0.01308（5 flips） |
| 2608.15531 | W4 dense + FP sparse outlier 数值融合 | outlier density 0.000381；融合断言 PASS |
| 2608.15567 | Schur complement + 2-bit scale/zero refit + code coordinate descent | MSE 0.01513 → 0.01310 |
| 2608.15602 | row/column binary bases + Hessian 对角显著残差 + group-8 LUT | LUT 等价 PASS；MSE 0.01266 |
| 2608.15636 | residual-ranked 64×64 block 4/8-bit mixed precision | 全4-bit 0.00608 → 平均5-bit 0.00333 |
| 2608.16104 | 8 个伪专家的 INT4 weight / FP4 activation STE-QAT | 5 steps 后 MSE 0.00612 |
| 2608.16756 | mean/absmean/std 驱动的 distribution-aware binary scale | absmean 0.280924 → learned 0.280409 |

所有 `demo.py` 已通过把 `PYTHONPYCACHEPREFIX` 指向 `/private/tmp` 的语法检查并实际运行。未完成且明确不伪造的部分：FlashQuant/FluxBin 的专用 CUDA 性能、SpecVLA 的机器人闭环与异构硬件、Nexus 的文生图训练、BinRVR 的 RAW 视频 BIIM。各 README 写明了边界。

## 5. 独立快照与一致性

本分支严格从 `origin/main` 创建。`origin/main` 自带的 2026-07-28 历史日报已删除；最终 `papers/` 仅 README 与这 22 篇新增精读，`reports/` 仅 README 与本日报，`scripts/` 仅通用 README 与 7 个新增量化复现，`metadata/` 仅 README 与本次 2026-08 索引/CSV。论文、metadata 与复现目录的 ID 集合将在提交前机械核验，历史交集必须保持为空。
