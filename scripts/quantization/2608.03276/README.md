# TaskPress: Task-Guided KV Cache Compression via Task-Guided Pruning

## 论文信息
- **标题**: TaskPress: Query-Agnostic KV Cache Compression via Task-Guided Pruning
- **arXiv**: 2608.03276
- **作者**: Wonpyo Park, Seung-won Hwang
- **发表日期**: 2026-08-04
- **类别**: cs.AI
- **URL**: https://arxiv.org/abs/2608.03276

## 问题背景

长上下文推理受 KV cache 线性增长制约。已有剪枝方法基于 query-specific 的 token 重要性（即针对具体 query 计算重要性），无法跨未见 query 复用——每次新 query 都要重新计算重要性并重新剪枝，开销巨大。

## 方法概述

TaskPress 提出任务引导的、query-agnostic 的 KV cache 驱逐框架，核心包含两个机制：

### 1. 任务引导剪枝 (Task-Guided Pruning)
- 用一个高层 **task guide**（meta-query）在 prefill 阶段过滤无关 token。
- task guide 代表任务意图（如 "总结文档" / "回答关于X的问题"），与具体 query 无关。
- 计算 task guide 对各 context token 的注意力，丢弃低注意力 token。
- 得到的压缩 cache 可**跨同任务的不同 query 复用**（query-agnostic），无需为新 query 重新剪枝。

### 2. 量化尺度因子作为离群点检测信号 (Zero-Cost Outlier Detection)
- 对 K/V 做分组量化时，每组的 scale factor（`max|x|`）已被计算。
- 复用这些 scale factor 作为 token 重要性的**零成本代理**：
  - 某个 token 的 scale factor 大 → 含极端值（outlier）→ 对表示影响大 → **保留**
  - scale factor 小 → 表示平淡 → 可安全剪枝 / 低精度量化
- 这样无需额外计算即可识别 influential outlier token。

### 3. 剪枝 + 量化联合压缩
- 先用 task guide 剪枝（丢弃无关 token）
- 再对保留 token 量化，其中 outlier token（大 scale）用更高精度
- 生成紧凑、可复用的 cache

## 代码使用说明

### 运行
```bash
cd scripts/quantization/2608.03276
python3 demo.py
```

### 核心组件
- `TaskPressCompressor`：主压缩器，参数包括 keep_ratio、outlier_ratio、base_bits、outlier_bits
- `compute_task_importance`：task guide 对 context token 的注意力打分（query-agnostic）
- `detect_outliers`：复用量化 scale factor 零成本检测 outlier token
- `group_quantize_with_scale`：分组量化，返回 scale factor 供离群点检测
- `attention_with_pruned_cache`：用压缩 cache 计算注意力输出并评估保真度

### 对比基线
- **Uniform-Prune**：任务剪枝但统一量化（不用 scale factor 离群点检测）
- **Uniform-Q4 (no prune)**：不剪枝，所有 token 统一 4-bit 量化

### Query-Agnostic 复用性验证
脚本生成多个不同测试 query，对同一压缩 cache 评估，验证：
- 跨 query 的注意力输出余弦相似度
- top-1 retrieval 一致性（注意力最关注的 token 是否一致）
- 跨 query 结果极差（越小说明越稳定可复用）

脚本会自动尝试加载 Qwen3-0.6B；若无法下载则使用 MockTransformer 保证可运行。

## 依赖项
- Python >= 3.8
- PyTorch >= 1.10
- transformers (用于加载 Qwen3-0.6B，可选)
- 共享工具包 `quantization_toolkit.py`（上级目录）

## 文件列表
- `demo.py` - TaskPress 完整实现与验证脚本
