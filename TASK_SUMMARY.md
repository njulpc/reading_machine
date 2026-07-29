# Reading Machine — 量化与模型压缩论文分析平台

## 项目概述

本项目是一个自动化的 arXiv 论文采集、技术分析与归档系统，专注于 **量化（Quantization）、模型压缩（Model Compression）、剪枝（Pruning）与知识蒸馏（Knowledge Distillation）** 领域。

---

## 第一阶段：论文采集与归档（已完成 ✅）

### 采集范围
- **日期**: 2026-07-27 ~ 2026-07-28（24小时）
- **关键词**: quantization, model compression, pruning, distillation, efficient inference
- **来源**: arXiv.org
- **论文总数**: 20篇

### 归档内容
- **PDF下载**: 每篇论文原始PDF保存至 `papers/2026-07/<arxiv_id>/paper.pdf`
- **结构化索引**: `metadata/2026-07/papers_index.json`（含作者、URL、关键词、Highlight）
- **关键词统计**: `metadata/2026-07/keywords.csv`
- **日报报告**: `reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md`

---

## 第二阶段：技术深度分析（已完成 ✅）

### 分析方式
- **3篇深度分析**（基于PDF全文提取）：
  - 2607.25870 — VAD to the Bone（角度感知QAT + 结构化剪枝 + 自蒸馏）
  - 2607.24953 — Stable FP4 Training（2D块转置不变FP4量化）
  - 2607.25451 — Bits and Memories（RTN量化 + 逐字记忆提取隐私分析）
- **17篇标准分析**：自动生成包含概述、方法、伪代码、结果、创新的结构化Markdown

### 分析报告位置
```
papers/2026-07/<arxiv_id>/
├── paper.pdf              # 原始PDF
└── tech_analysis.md       # 技术深度分析
```

---

## 第三阶段：核心代码复现（已完成 ✅）

### 按论文拆分的独立可运行代码

每个 `arxiv_id` 对应一个独立目录，包含自包含的 `demo.py`，无需依赖其他文件即可运行：

| 论文 | arXiv ID | 核心方法 | 代码文件 |
|------|----------|---------|---------|
| VAD to the Bone | 2607.25870 | INT4角度感知QAT + 结构化剪枝 + 自蒸馏 | `2607.25870/demo.py` |
| Stable FP4 Training | 2607.24953 | 2D块转置不变FP4量化 + 随机舍入 | `2607.24953/demo.py` |
| Bits and Memories | 2607.25451 | RTN组量化 + 逐字记忆提取评估 | `2607.25451/demo.py` |
| Bekko Embedding | 2607.25180 | INT8行级量化 + 检索编码器 | `2607.25180/demo.py` |
| Integer-Only DETR | 2607.24981 | 整数GELU/Softmax/LayerNorm | `2607.24981/demo.py` |
| MXAttention | 2607.24377 | MXFP4数据无关注意力量化 | `2607.24377/demo.py` |
| LoRA Quantization | 2607.25583 | LoRA秩与量化联合优化 | `2607.25583/demo.py` |
| FPGA Evaluation | 2607.24568 | PTQ vs QAT + FPGA定点仿真 | `2607.24568/demo.py` |

### 运行方式
```bash
cd scripts/quantization/<arxiv_id>
python3 demo.py
```

### 统一工具包（可选）
- `quantization_toolkit.py` — 整合版量化模块（含RTN、FP4、INT8、Angle-Aware QAT等）
- `evaluate_qwen.py` — 以Qwen3-0.6B为目标的评估管道（含Demo模式）
- `quantization_demo.py` — 统一演示脚本（对比所有方法）

---

## 第四阶段：GitHub归档（已完成 ✅）

### 仓库信息
- **仓库**: https://github.com/njulpc/reading_machine
- **分支**: `feature/arxiv-daily-2026-07-28`
- **提交记录**:
  1. `abfe8f2` — 初始化项目结构
  2. `c9c41f4` — 添加论文采集与报告
  3. `163e2aa` — 完整分析 + PyTorch量化工具包
  4. `42bdf07` — 可运行量化演示 + 修复
  5. `edb1535` — 按论文拆分的独立演示代码

---

## 技术亮点

### 论文对应实现
| 论文创新点 | 代码实现 |
|-----------|---------|
| 2D块转置不变量化（S(X)=S(X^T)） | `FP4Quantizer.verify_transpose_invariance()` |
| 角度感知自蒸馏损失 | `AngleAwareLoss.forward()` |
| 整数GELU查找表 | `IntegerGELU` |
| 无数据最优尺度搜索 | `MXFP4Quantizer.data_free_optimal_scale()` |
| LoRA + 量化联合分析 | `QuantizedLoRALinear` |
| FPGA定点资源估计 | `FixedPointQuantizer.get_fpga_resources()` |

### 验证结果
- FP4转置不变性: **✅ 验证通过**
- 角度感知损失梯度: **✅ 正常反向传播**
- 整数操作输出范围: **✅ 符合预期**
- 4-bit压缩比: **✅ 4.0x**
- 8-bit压缩比: **✅ 2.0x**

---

## 文件树

```
reading_machine/
├── papers/                          # 论文资料
│   └── 2026-07/
│       └── <arxiv_id>/
│           ├── paper.pdf
│           └── tech_analysis.md
├── reports/                         # 分析报告
│   └── 2026-07/quantization/
│       └── arxiv_quantization_daily_report_20260728.md
├── metadata/                        # 结构化数据
│   └── 2026-07/
│       ├── papers_index.json
│       └── keywords.csv
├── scripts/                         # 自动化脚本
│   ├── download_pdfs.py
│   ├── extract_pdf.py
│   ├── batch_analyze.py
│   └── quantization/               # 量化代码
│       ├── quantization_toolkit.py
│       ├── quantization_demo.py
│       ├── evaluate_qwen.py
│       ├── 2607.25870/demo.py
│       ├── 2607.24953/demo.py
│       ├── 2607.25451/demo.py
│       ├── 2607.25180/demo.py
│       ├── 2607.24981/demo.py
│       ├── 2607.24377/demo.py
│       ├── 2607.25583/demo.py
│       └── 2607.24568/demo.py
├── requirements.txt
└── README.md
```

---

## 使用指南

### 快速开始
```bash
# 1. 克隆仓库
git clone https://github.com/njulpc/reading_machine.git
cd reading_machine

# 2. 安装依赖
pip install torch

# 3. 运行任意论文的独立演示
cd scripts/quantization/2607.24953
python3 demo.py

# 4. 查看论文分析
cat papers/2026-07/2607.24953/tech_analysis.md
```

### 批量运行所有演示
```bash
cd scripts/quantization
for dir in 2607.*; do
    echo "=== $dir ==="
    (cd "$dir" && python3 demo.py)
done
```

---

## 未来工作

- [ ] 扩展到更大规模模型（70B+）的量化验证
- [ ] 添加GPU加速的量化内核（CUDA/Metal）
- [ ] 集成真实Qwen3-0.6B模型评估（当前为架构模拟）
- [ ] 每日自动采集新论文并更新归档
- [ ] 支持更多量化格式（AWQ、GPTQ、GGUF等）

---

*项目维护: njulpc*  
*最后更新: 2026-07-29*
