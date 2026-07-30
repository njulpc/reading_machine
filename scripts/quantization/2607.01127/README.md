# Paper: 2607.01127 — Log_bQuant: Quantizing Language Models in Logarithmic Space

Run: `python3 demo.py`

## 复现内容
- 对数空间量化器：量化 log_b|w| 并保留符号，分辨率按权重幅度的乘性结构分配；
- 与线性均匀量化在重尾权重上的相对误差对比（整体与小幅度子集）；
- 基数 b 的敏感性扫描；
- 以 Qwen3-0.6B 为目标的 4-bit 对数量化演示。

## 验证方式
- [1][2] 合成重尾权重上的中位相对误差对比（核心机理）；
- [3] 真实 Qwen/Qwen3-0.6B 前 2 个线性层对数量化并比较 logits 余弦相似度（无模型时跳过并注明）。
