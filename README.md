# reading_machine

自动化的 arXiv 论文采集、分析与归档系统，专注于**量化(Quantization)**、**模型压缩(Model Compression)**、**剪枝(Pruning)**与**知识蒸馏(Knowledge Distillation)**领域。

---

## 📊 最新日报：2026-07-28

**收集范围**: 2026-07-27 ~ 2026-07-28  
**论文总数**: 20 篇  
**技术方向分布**:
- 量化 (Quantization): 12 篇
- 剪枝 (Pruning): 5 篇
- 混合压缩 (P+Q+D): 2 篇
- 蒸馏 (Distillation): 1 篇

### 🔥 五大亮点

1. **超极端压缩** — [VAD to the Bone](https://arxiv.org/abs/2607.25870): 语音检测仅 **2.1k 参数**，三重压缩
2. **FP4训练稳定性** — [Stable FP4 Training](https://arxiv.org/abs/2607.24953): 转置不变块量化首次稳定FP4
3. **量化隐私风险** — [Bits and Memories](https://arxiv.org/abs/2607.25451): 1B模型4-bit仍保留72%记忆
4. **Data-Free MXFP4** — [MXAttention](https://arxiv.org/abs/2607.24377): 无需校准数据量化Attention
5. **纯整数检测** — [Integer-Only Detection](https://arxiv.org/abs/2607.24981): 端到端INT8 DETR

---

## 📁 目录结构

```
reading_machine/
├── papers/              # 论文原始资料 (PDF + 技术分析)
│   └── 2026-07/
│       └── <arxiv_id>/
│           ├── paper.pdf           # 下载的PDF
│           └── tech_analysis.md    # 技术深度分析
├── reports/             # 分析报告 (按技术方向分类)
│   └── 2026-07/
│       └── quantization/
│           └── arxiv_quantization_daily_report_20260728.md
├── metadata/            # 结构化元数据
│   └── 2026-07/
│       ├── papers_index.json      # 论文索引
│       └── keywords.csv           # 关键词统计
├── scripts/             # 自动化脚本
│   ├── download_pdfs.py
│   ├── extract_pdf.py
│   ├── batch_analyze.py
│   └── quantization/    # PyTorch量化实现
│       ├── quantization_toolkit.py   # 核心量化模块
│       ├── evaluate_qwen.py         # Qwen3-0.6B验证
│       └── README.md
├── requirements.txt
└── README.md
```

---

## 🚀 PyTorch 量化工具包

基于论文实现的可运行量化代码，以 **Qwen3-0.6B** 为验证目标。

### 支持的量化方法

| 方法 | 论文 | 描述 | 代码 |
|------|------|------|------|
| **RTN** | 2607.25451 | Round-to-Nearest 组量化 | ✅ |
| **FP4** | 2607.24953 | 2D块转置不变 FP4 | ✅ |
| **INT8** | 2607.25180 | Per-channel INT8 | ✅ |
| **Angle-Aware QAT** | 2607.25870 | 角度感知自蒸馏 | ✅ |
| **Integer-Only** | 2607.24981 | 整数GELU/Softmax | ✅ |

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/njulpc/reading_machine.git
cd reading_machine

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行Demo评估 (无需下载模型)
cd scripts/quantization
python evaluate_qwen.py --demo --methods rtn4 rtn8 int8

# 4. 运行真实模型评估 (需要GPU)
python evaluate_qwen.py --model Qwen/Qwen3-0.6B --methods rtn4 int8 fp4
```

### 代码示例

```python
from scripts.quantization.quantization_toolkit import FP4Quantizer, AngleAwareQATLoss

# 2D Block FP4 量化
quantizer = FP4Quantizer(bits=4, block_size=32)
x = torch.randn(64, 64)
x_dq, scales = quantizer.quantize(x)
assert quantizer.forward_backward_consistent(x)  # 转置不变性

# 角度感知QAT
loss_fn = AngleAwareQATLoss(lambda_repel=1.0)
loss = loss_fn(features, targets, frozen_classifier)
```

---

## 📋 论文清单 (2026-07-28)

| # | arXiv | 标题 | 量化类型 | 分析 |
|---|-------|------|---------|------|
| 1 | [2607.25870](papers/2026-07/2607.25870/tech_analysis.md) | VAD to the Bone (INT4 QAT + Pruning) | **INT4** | ✅ |
| 2 | [2607.25583](papers/2026-07/2607.25583/tech_analysis.md) | LoRA Rank & Quantization Trade-offs | **Low-bit** | ✅ |
| 3 | [2607.25529](papers/2026-07/2607.25529/tech_analysis.md) | Are High-weight Neurons Important? | Pruning | ✅ |
| 4 | [2607.25527](papers/2026-07/2607.25527/tech_analysis.md) | Argus-Unified (VLM Quantizer) | Quantizer | ✅ |
| 5 | [2607.25451](papers/2026-07/2607.25451/tech_analysis.md) | Bits and Memories (LLM 4-bit) | **4-bit** | ✅ |
| 6 | [2607.25209](papers/2026-07/2607.25209/tech_analysis.md) | VaLiDRec (Semantic IDs) | Quantization | ✅ |
| 7 | [2607.25180](papers/2026-07/2607.25180/tech_analysis.md) | Bekko Embedding (INT8) | **INT8** | ✅ |
| 8 | [2607.24981](papers/2026-07/2607.24981/tech_analysis.md) | Integer-Only DETR | **INT8** | ✅ |
| 9 | [2607.24953](papers/2026-07/2607.24953/tech_analysis.md) | Stable FP4 Training | **FP4** | ✅ |
| 10 | [2607.24868](papers/2026-07/2607.24868/tech_analysis.md) | One-Bit Fourier Extension | **1-bit** | ✅ |
| 11 | [2607.24865](papers/2026-07/2607.24865/tech_analysis.md) | Dual-purpose Semantic IDs | Hierarchical | ✅ |
| 12 | [2607.24568](papers/2026-07/2607.24568/tech_analysis.md) | FPGA QAT/PTQ | **PTQ/QAT** | ✅ |
| 13 | [2607.24562](papers/2026-07/2607.24562/tech_analysis.md) | Conformal Risk Control + Quant | Quantization | ✅ |
| 14 | [2607.24440](papers/2026-07/2607.24440/tech_analysis.md) | VLM Quantization & Uncertainty | **VLM** | ✅ |
| 15 | [2607.24377](papers/2026-07/2607.24377/tech_analysis.md) | MXAttention (MXFP4) | **MXFP4** | ✅ |
| 16 | [2607.24192](papers/2026-07/2607.24192/tech_analysis.md) | LLM Source Code Compression | Quantized | ✅ |
| 17 | [2607.24148](papers/2026-07/2607.24148/tech_analysis.md) | Motion-Aware Vector Quantization | VQ | ✅ |
| 18 | [2607.22790](papers/2026-07/2607.22790/tech_analysis.md) | Sparsity Tax (Neuromorphic) | Pruning | ✅ |
| 19 | [2607.22564](papers/2026-07/2607.22564/tech_analysis.md) | Feature-Map Pruning (Bandits) | Pruning | ✅ |
| 20 | [2607.19248](papers/2026-07/2607.19248/tech_analysis.md) | Sparsity-Aware FPGA | Pruning | ✅ |

---

## 📦 安装

```bash
pip install -r requirements.txt
```

依赖：
- Python >= 3.9
- PyTorch >= 2.0
- transformers >= 4.40
- pdfplumber (PDF文本提取)

---

## 📝 贡献指南

1. 每日自动采集新论文
2. 人工审核重点论文并补充深度分析
3. 实现核心算法的PyTorch代码
4. 以标准模型验证量化效果

---

*Maintained by [njulpc](https://github.com/njulpc)*  
*Last updated: 2026-07-29*
