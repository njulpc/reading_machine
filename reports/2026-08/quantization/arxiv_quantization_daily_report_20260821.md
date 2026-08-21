# arXiv 模型压缩论文日报（2026-08-21）

> 运行日：2026-08-22（Asia/Shanghai）
> 固定检索窗口：2026-08-19 00:00 至 2026-08-21 23:59；逐篇按 arXiv `/abs` Submission history 的 v1 日期归日。
> 结论：窗口内确认相关论文 26 篇；历史已完成 12 篇；本次新增 14 篇。

## 一、三天结果

| v1 实际提交日 | 相关论文 | 历史重复 | 本次新增 |
|---|---:|---:|---:|
| 2026-08-19 | 12 | 12 | 0 |
| 2026-08-20 | 14 | 0 | 14 |
| 2026-08-21 | 0 | 0 | 0 |
| **合计** | **26** | **12** | **14** |

2026-08-21 的“0”表示：截至本次运行时，官方分类页最新公告为 Friday, 21 August 2026，但其中逐篇 `/abs` v1 日期均未落在 8 月 21 日；不是把抓取失败记为零。三天公告组跨分类去重后共 1,109 个 ID，1,109 个官方详情页全部成功读取；其中 v1 落窗 557 条（8 月 19 日 309、8 月 20 日 248、8 月 21 日 0），再逐条依据标题与摘要进行语义判断。

纳入口径包括权重/激活量化、结构/注意力稀疏、teacher→student 或推理搜索蒸馏、KV cache 压缩，以及有直接模型体积证据的紧凑架构。排除只压 retrieved text 的 context compression、普通 PEFT、数据/媒体压缩、纯硬件调度，以及借用 `sparse/distill` 词汇但不压缩模型或推理图的工作。

## 二、官方网页覆盖审计

未使用 arXiv API。完整读取 cs.LG、cs.CL、cs.CV、cs.AI、cs.AR 的 `new` 与 `recent?show=2000`；所有页面声明总数均小于 show=2000，页面实际条目数等于声明数，new submissions、cross submissions、replacement submissions 均覆盖。

### recent 页面

| 分类 | 入口 | 总数 | 08-21 | 08-20 | 08-19 | 窗口外阳性对照 |
|---|---|---:|---:|---:|---:|---|
| cs.LG | [recent](https://arxiv.org/list/cs.LG/recent?show=2000) | 950 | 127 | 169 | 142 | 08-18: 374；08-17: 138 |
| cs.CL | [recent](https://arxiv.org/list/cs.CL/recent?show=2000) | 465 | 76 | 99 | 72 | 08-18: 156；08-17: 62 |
| cs.CV | [recent](https://arxiv.org/list/cs.CV/recent?show=2000) | 641 | 86 | 94 | 103 | 08-18: 269；08-17: 89 |
| cs.AI | [recent](https://arxiv.org/list/cs.AI/recent?show=2000) | 1,151 | 145 | 186 | 170 | 08-18: 465；08-17: 185 |
| cs.AR | [recent](https://arxiv.org/list/cs.AR/recent?show=2000) | 43 | 12 | 8 | 7 | 08-18: 8；08-17: 8 |

### new 页面（Friday, 21 August 2026）

| 分类 | 入口 | 总数 | new | cross | replacement |
|---|---|---:|---:|---:|---:|
| cs.LG | [new](https://arxiv.org/list/cs.LG/new?show=2000) | 200 | 65 | 62 | 73 |
| cs.CL | [new](https://arxiv.org/list/cs.CL/new?show=2000) | 109 | 49 | 27 | 33 |
| cs.CV | [new](https://arxiv.org/list/cs.CV/new?show=2000) | 137 | 66 | 20 | 51 |
| cs.AI | [new](https://arxiv.org/list/cs.AI/new?show=2000) | 222 | 62 | 83 | 77 |
| cs.AR | [new](https://arxiv.org/list/cs.AR/new?show=2000) | 14 | 10 | 2 | 2 |

## 三、历史去重审计

`git fetch --prune origin` 后完整枚举 21 个 `origin/feature/arxiv-daily-*` 分支，并对每个分支运行 `git ls-tree -r --name-only`。从真实 `papers/**/<id>/tech_analysis.md` 得到 209 个规范化历史 ID；metadata 有 212 个，`2607.27951`、`2607.28410`、`2607.28457` 没有真实精读文件，未计为完成。

本窗口 12 个重复 ID 全部来自 `origin/feature/arxiv-daily-2026-08-21`：`2608.18399`、`2608.18410`、`2608.18484`、`2608.18486`、`2608.18578`、`2608.18590`、`2608.18819`、`2608.18849`、`2608.18952`、`2608.19046`、`2608.19098`、`2608.19181`。本次 14 个新增 ID 与 209 个历史完成 ID 的交集为零。

## 四、本次新增论文与评分

评分为“精度效果 / 压缩倍率 / 创新性 / 可复现性”，均为 1–10 分。

| ID | 方向 | 一句话结论 | 评分 | 依据 |
|---|---|---|---|---|
| [2608.19536](https://arxiv.org/abs/2608.19536) | 蒸馏 | DINOv2 语义蒸馏进纯 LiDAR 学生，三基准严格成功率 97.7/99.0/99.3%。 | 9/7/8/7 | 最高 +44 pp；推理去教师/相机，但未报参数压缩率。 |
| [2608.19540](https://arxiv.org/abs/2608.19540) | 蒸馏 | 统一 ε/x/v/u 到 MeanFlow，CAMF 平均改善少步 FID 29%，NFE 最多降 125×。 | 9/10/9/6 | 四源模型五目标域；对抗后训练较重。 |
| [2608.19639](https://arxiv.org/abs/2608.19639) | 稀疏 | 结构化 Gaussian residual 更新令逐帧优化时间降 59%、存储降 85%。 | 8/9/8/6 | Jetson 60+ FPS；依赖场景连续性和逐场景优化。 |
| [2608.19662](https://arxiv.org/abs/2608.19662) | KV 压缩 | 资源级可组合 KV block + 路由/字段剪枝，内存降 92.43%、TTFT 3.655×。 | 9/10/9/8 | Inv-F1 82.3 对 dense 82.4；七数据集且开源。 |
| [2608.19670](https://arxiv.org/abs/2608.19670) | 压缩评测 | 平均指标会掩盖知识保持、错误置信和人口子群体的反向变化。 | 8/7/9/8 | 三模型、11 类量化/剪枝设置；行为审计可直接复用。 |
| [2608.19748](https://arxiv.org/abs/2608.19748) | 蒸馏 | TUP 分离下尾截断 λ 与上尾锐化 β，把 Best-of-N 压成单策略。 | 8/8/9/7 | Llama/Mistral 多 judge 竞争力强；需额外调 λ。 |
| [2608.19758](https://arxiv.org/abs/2608.19758) | 稀疏 | 生产级 block-sparse prefill 在 128K 上相对 FA2 FP8 最高 47.26×。 | 9/10/9/6 | 还有 FA3/4 风格强基线；集中于 H20。 |
| [2608.19837](https://arxiv.org/abs/2608.19837) | 量化 | E4M3 逐层 exponent-bias 校准把工业准确率 80.33% 提至 84.13%。 | 6/7/7/8 | FPGA 能效 2.5×，但距 FP32 仍 13.81 pp；有 Qwen3 复现。 |
| [2608.19894](https://arxiv.org/abs/2608.19894) | 紧凑架构 | 点/线特征共享 backbone 并蒸馏，约快 4×、内存小 10×。 | 8/9/8/7 | 多几何任务验证；收益依赖 pipeline 基线。 |
| [2608.19920](https://arxiv.org/abs/2608.19920) | 稀疏 | policy-aware 微调让模型真正适应 KV eviction，并可在单张 A100 40GB 求梯度。 | 8/9/9/6 | 64K/128K 多任务；sparse kernel latency 尚未成熟。 |
| [2608.20052](https://arxiv.org/abs/2608.20052) | 紧凑架构 | 趋势/季节双 VAE 用结构先验把模型权重最多降 93%、速度升 74%。 | 9/9/8/7 | 七数据集、三次运行；依赖可分解时序假设。 |
| [2608.20122](https://arxiv.org/abs/2608.20122) | 自蒸馏 | 特权视觉观察蒸馏使 AdvSpot 准确率/IoU 从 31.2/49.1 升至 55.7/63.3。 | 9/6/8/6 | 推理去工具但训练需 120K 合成样本和 GRPO。 |
| [2608.20210](https://arxiv.org/abs/2608.20210) | 4-bit 紧凑架构 | 6 attention + 12 短卷积的 CPU 模型在 2048 context 快 1.76×。 | 7/9/8/7 | 4-bit 文件小 6.3%，但 PPL 代价约 6%。 |
| [2608.20334](https://arxiv.org/abs/2608.20334) | 剪枝/蒸馏 | 6B→3B head pruning 与 50→8 步 DMD 组合，编辑总分近乎无损。 | 9/10/9/4 | 压缩全面；完整训练约 243K GPU-hours，复现门槛极高。 |

每篇均已读取官方 PDF，并在 `papers/2026-08/<direction>/<id>/tech_analysis.md` 写入六节精读。没有全文不可得的新增论文。

## 五、量化论文 Qwen3-0.6B 复现

复现目录：`scripts/quantization/2608.19837/`。代码实现有限值 E4M3、可配置 exponent bias、真实 Qwen input/weight fake quant，以及逐 Linear 校准搜索。论文以小校准集和 Bayesian optimization 搜索；本次 7 个离散候选采用穷举，得到同一目标下的精确最优。

语法和张量 self-test 通过；真实加载 Qwen3-0.6B 的 596,049,920 参数，校准首层 7 个 Linear、15,728,640 个权重元素和 32-token 激活。最优 bias 依次为 10/11/10/10/11/11/11；相对固定 bias=7，校准 MSE 几何平均比 0.876381，即下降约 12.36%。

本机为 Apple CPU，无 CUDA/MPS，也没有 Xilinx XC7A200T、工业 X 光数据或 FFT RTL。Qwen 没有 FFT 蝶形，因此未伪造 PBA 与 inverse-FFT `1/N` scaling；结果只验证 E4M3 数值路径和逐层 bias 优于统一 bias 的方向，不声称论文 FPGA 2.5× 能效、1.91 ms 或 84.13% 准确率复现。

## 六、独立快照说明

本分支严格从最新 `origin/main` 创建隔离 linked worktree。已删除 main 自带的 2026-07 历史日报；`papers/` 只含 14 篇本次新增精读，`reports/` 只含本日报，`scripts/quantization/` 只含唯一新增量化复现，`metadata/` 只重建 2026-08 本次索引和 CSV。提交前将再次执行集合一致性、历史零交集、JSON/CSV、代码、diff、单提交和远端关系检查。
