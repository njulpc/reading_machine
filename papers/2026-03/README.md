# 2026-03 论文分类存放说明

本目录按核心领域将论文与技术分析分类存放（一篇论文按优先级只归入一类，优先级：quantization > pruning > knowledge_distillation > others）：

- `quantization/`：量化相关（56 篇）
- `pruning/`：剪枝与稀疏（26 篇）
- `knowledge_distillation/`：知识蒸馏（11 篇）
- `others/`：其他方向，如低秩分解、KV cache 非量化压缩、硬件协同、早退机制、综述等（8 篇）

每篇论文的完整六段式技术分析位于 `<domain>/<arxiv_id>/tech_analysis.md`；分类标签同步记录在 `metadata/2026-03/papers_index.json` 的 `domain` 字段。
