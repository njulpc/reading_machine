# Reading Machine — 完整任务描述

## 一、任务起源

**时间**: 2026-07-29 09:53  
**发起者**: 用户  
**初始需求**: 
> "帮我在arxiv上搜索量化(quantization, model compress)相关的论文，收集昨天24小时内全部的该领域的论文，做一个论文的列表和关键字，相关领域的表格给我"

---

## 二、任务演进过程

### Phase 1: 论文采集（09:53 - 10:15）

**目标**: 采集2026-07-27至2026-07-28期间arXiv上量化与模型压缩领域论文。

**执行步骤**:
1. 通过arXiv API、网页抓取、搜索等多种方式定位论文
2. 确认arXiv日期格式（2607.24xxx = 2026-07-24之后提交）
3. 从cs.LG、cs.CL、cs.CV等类别中筛选相关论文
4. 最终确认20篇核心论文（12篇量化、5篇剪枝、2篇混合、1篇蒸馏）

**交付物**:
- `reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md`
- 包含：论文总览表、技术方向分类表、应用领域分类表、五大亮点

---

### Phase 2: Git仓库搭建（16:22 - 16:40）

**目标**: 建立GitHub仓库管理论文和分析结果。

**执行步骤**:
1. 初始化Git仓库 (`git init`)
2. 配置远程地址 (`git remote add origin https://github.com/njulpc/reading_machine.git`)
3. 创建标准目录结构：
   ```
   reading_machine/
   ├── papers/          # 论文PDF + 技术分析
   ├── reports/         # 日报/分析报告
   ├── metadata/        # 结构化数据
   └── scripts/         # 自动化脚本
   ```
4. 创建 `papers_index.json` 和 `keywords.csv`
5. 推送至GitHub分支 `feature/arxiv-daily-2026-07-28`

---

### Phase 3: PDF下载与技术深度分析（16:40 - 17:40）

**目标**: 
1. 下载全部20篇论文PDF
2. 对每篇论文进行技术深度分析

**执行步骤**:
1. 编写 `scripts/download_pdfs.py` 批量下载PDF
2. 编写 `scripts/extract_pdf.py` 提取PDF文本
3. 对3篇重点论文进行深度分析（基于PDF全文）：
   - 2607.25870 — VAD to the Bone（角度感知QAT + 结构化剪枝）
   - 2607.24953 — Stable FP4 Training（2D块转置不变FP4）
   - 2607.25451 — Bits and Memories（RTN量化 + 记忆隐私）
4. 对其余17篇论文进行标准分析

**交付物**:
- 20篇PDF文件：`papers/2026-07/<arxiv_id>/paper.pdf`
- 20篇技术分析：`papers/2026-07/<arxiv_id>/tech_analysis.md`

---

### Phase 4: PyTorch量化代码实现（17:40 - 18:00）

**目标**: 将核心论文的方法用PyTorch实现为可运行代码。

**执行步骤**:
1. 编写 `scripts/quantization/quantization_toolkit.py`
   - RTNQuantizer（4/8-bit）
   - FP4Quantizer（2D块 + 随机舍入）
   - INT8Quantizer（per-channel）
   - AngleAwareQATLoss（角度感知损失）
   - IntegerGELU/Softmax/LayerNorm（整数运算）
2. 编写 `scripts/quantization/evaluate_qwen.py`
   - 以Qwen3-0.6B为目标的评估管道
   - Demo模式（无需真实模型）
3. 编写 `scripts/quantization/quantization_demo.py`
   - 统一演示脚本，对比所有方法
4. 运行验证：FP4转置不变性 ✅、角度感知梯度 ✅、压缩比4x/2x ✅

---

### Phase 5: 按论文拆分独立代码（18:00 - 18:15）

**目标**: 每篇论文对应独立的可运行代码，不依赖其他文件。

**执行步骤**:
为8篇核心量化论文各创建独立目录和 `demo.py`：

| 论文 | 目录 | 核心代码 |
|------|------|---------|
| 2607.25870 | `2607.25870/` | Angle-Aware QAT + 结构化剪枝 + 自蒸馏 |
| 2607.24953 | `2607.24953/` | 2D块FP4 + 转置不变性验证 |
| 2607.25451 | `2607.25451/` | RTN量化 + 记忆提取评估 |
| 2607.25180 | `2607.25180/` | INT8行级量化 |
| 2607.24981 | `2607.24981/` | 整数GELU/Softmax/LayerNorm |
| 2607.24377 | `2607.24377/` | MXFP4数据无关量化 |
| 2607.25583 | `2607.25583/` | LoRA + 量化联合分析 |
| 2607.24568 | `2607.24568/` | PTQ vs QAT + FPGA定点仿真 |

**验证**: 每个 `demo.py` 均可独立运行 `python3 demo.py`

---

### Phase 6: 深度分析模板重写（18:22 - 18:58）

**目标**: 按资深学术研究员标准重写全部20篇论文分析。

**分析模板**（6个章节）：
1. **核心速览** — 研究主题 + 一句话总结
2. **研究背景与动机** — 现有痛点 + 研究必要性
3. **核心方法与创新点** — 方法概述 + 分点创新
4. **实验设计与结果** — 数据集 + 核心结果
5. **局限性与未来展望** — 不足分析 + 未来方向
6. **学术启发** — 可迁移思路 + 实验设计借鉴

**执行方式**: 4个子代理并行处理（每组5篇），共重写20篇，每篇3000-5000字。

---

## 三、最终交付物清单

### 仓库结构
```
reading_machine/
├── papers/                          # 论文资料（20篇）
│   └── 2026-07/
│       └── <arxiv_id>/
│           ├── paper.pdf              # 原始PDF
│           └── tech_analysis.md       # 深度分析（3000-5000字）
├── reports/                         # 分析报告
│   └── 2026-07/quantization/
│       └── arxiv_quantization_daily_report_20260728.md
├── metadata/                        # 结构化数据
│   └── 2026-07/
│       ├── papers_index.json          # 论文索引
│       └── keywords.csv               # 关键词统计
├── scripts/                         # 自动化脚本
│   ├── download_pdfs.py
│   ├── extract_pdf.py
│   ├── batch_analyze.py
│   └── quantization/               # 量化代码
│       ├── quantization_toolkit.py    # 整合版量化模块
│       ├── quantization_demo.py       # 统一演示
│       ├── evaluate_qwen.py          # Qwen3-0.6B评估
│       ├── 2607.25870/demo.py        # 独立代码（8个）
│       ├── 2607.24953/demo.py
│       ├── 2607.25451/demo.py
│       ├── 2607.25180/demo.py
│       ├── 2607.24981/demo.py
│       ├── 2607.24377/demo.py
│       ├── 2607.25583/demo.py
│       └── 2607.24568/demo.py
├── TASK_SUMMARY.md                  # 本文件
└── README.md                        # 项目说明
```

### 统计数据
| 指标 | 数值 |
|------|------|
| 论文总数 | 20篇 |
| PDF下载 | 20/20 ✅ |
| 深度分析 | 20/20 ✅（平均20KB/篇）|
| 独立代码 | 8组 ✅ |
| 代码验证 | 全部通过 ✅ |
| Git提交 | 7次 |

---

## 四、技术亮点

### 论文与代码对应
| 论文 | 核心创新 | 代码实现 |
|------|---------|---------|
| 2607.25870 | 角度感知自蒸馏QAT | `AngleAwareLoss` + 结构化剪枝 |
| 2607.24953 | 2D块转置不变FP4 | `FP4Quantizer.verify_transpose_invariance()` |
| 2607.25451 | RTN量化 + 记忆隐私 | `MemorizationEvaluator` |
| 2607.25180 | INT8行级量化 | `INT8RowQuantizer` |
| 2607.24981 | 整数GELU/Softmax/LN | `IntegerGELU`, `IntegerSoftmax` |
| 2607.24377 | MXFP4数据无关量化 | `MXFP4Quantizer.data_free_optimal_scale()` |
| 2607.25583 | LoRA + 量化联合 | `QuantizedLoRALinear` |
| 2607.24568 | PTQ vs QAT + FPGA | `FixedPointQuantizer.get_fpga_resources()` |

---

## 五、使用方式

```bash
# 1. 克隆仓库
git clone https://github.com/njulpc/reading_machine.git
cd reading_machine

# 2. 查看论文分析
cat papers/2026-07/2607.25870/tech_analysis.md

# 3. 运行独立代码
cd scripts/quantization/2607.24953
python3 demo.py

# 4. 查看日报
cat reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md
```

---

## 六、时间线

| 时间 | 事件 |
|------|------|
| 09:53 | 用户发起论文采集请求 |
| 10:15 | 完成20篇论文采集和日报 |
| 16:22 | 开始Git仓库搭建 |
| 16:40 | 完成仓库结构 + 论文归档 |
| 17:40 | 完成PDF下载 + 技术深度分析 |
| 18:00 | 完成PyTorch量化代码实现 |
| 18:15 | 完成按论文拆分的独立代码 |
| 18:22 | 开始深度分析模板重写 |
| 18:58 | 完成全部20篇重写 |
| 19:00 | 推送最终版本到GitHub |

---

*项目维护: njulpc*  
*最后更新: 2026-07-29 19:00*
