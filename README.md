# reading_machine

自动化的 arXiv 论文采集、分析与归档系统，专注于量化(Quantization)、模型压缩(Model Compression)、剪枝(Pruning)与知识蒸馏(Knowledge Distillation)领域。

---

## 📁 目录结构

```
reading_machine/
├── papers/              # 论文原始资料 (PDF、阅读笔记)
│   └── YYYY-MM/
│       └── arxiv_id/
│           ├── paper.pdf
│           └── notes.md
├── reports/             # 分析报告 (按技术方向分类)
│   └── YYYY-MM/
│       ├── quantization/
│       ├── pruning/
│       ├── distillation/
│       └── nas/
├── metadata/            # 结构化元数据
│   └── YYYY-MM/
│       ├── papers_index.json   # 论文索引
│       ├── keywords.csv        # 关键词统计
│       └── authors.json        # 作者信息
├── scripts/             # 自动化脚本
│   ├── arxiv_fetch.py
│   ├── paper_parser.py
│   └── report_generator.py
└── README.md
```

---

## 📊 最新日报：2026-07-28

**收集范围**: 2026-07-27 ~ 2026-07-28  
**论文总数**: 20 篇  
**技术方向分布**:
- 量化 (Quantization): 12 篇
- 剪枝 (Pruning): 5 篇
- 混合压缩 (P+Q+D): 2 篇
- 知识蒸馏 (Distillation): 1 篇

### 🔥 五大亮点

1. **超极端压缩** — [VAD to the Bone](https://arxiv.org/abs/2607.25870): 语音活动检测仅 **2.1k 参数**，三重压缩协同
2. **FP4训练稳定性** — [Stable FP4 Training](https://arxiv.org/abs/2607.24953): 转置不变块量化首次实现稳定FP4训练
3. **量化隐私风险** — [Bits and Memories](https://arxiv.org/abs/2607.25451): 系统测量LLM量化对逐字记忆的影响
4. **Data-Free MXFP4** — [MXAttention](https://arxiv.org/abs/2607.24377): 无需校准数据量化扩散视频Attention
5. **纯整数检测** — [Integer-Only Detection](https://arxiv.org/abs/2607.24981): 端到端INT8轻量检测Transformer

详见 [`reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md`](reports/2026-07/quantization/arxiv_quantization_daily_report_20260728.md)

---

## 🚀 使用方式

```bash
# 克隆仓库
git clone https://github.com/njulpc/reading_machine.git
cd reading_machine

# 查看论文索引
cat metadata/2026-07/papers_index.json | jq '.papers[] | {id, title, highlight}'

# 查看关键词统计
cat metadata/2026-07/keywords.csv
```

---

## 📝 贡献

每日自动采集 + 人工审核补充。欢迎提交 Issue 或 PR。

---

*Maintained by njulpc*
