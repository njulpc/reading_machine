# Paper: 2607.23047 — MixQuant: Adaptive Mixed-Precision Quantization for LLMs

Run: `python3 demo.py`

## 复现内容
- 预算无关层评分：对随机上游量化配置做失真边缘化 + 最低比特惩罚；
- 单次贪心遍历为任意预算产出比特分配；
- 验证论文核心论断：层敏感度依赖上游层比特配置；
- 以 Qwen3-0.6B 为目标的混合精度分配 + 量化演示。

## 验证方式
- [1]–[3] 在 6 层 mock Transformer（Qwen3-0.6B 结构缩小版）上完整运行评分、分配与依赖验证；
- [4] 加载真实 Qwen/Qwen3-0.6B，对前 4 个线性层做混合比特量化并比较 logits 余弦相似度（无模型时跳过并注明）。
