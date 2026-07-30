# Paper: 2607.08643 — BiSCo-LLM: Lookup-Free Binary Spherical Coding for Extreme Low-Bit LLM Compression

Run: `python3 demo.py`

## 复现内容
- 球面二值编码：sign(P·u) 编码单位方向，Pᵀ·b 线性解码（无码本查找）；
- 约 1 bit/维下方向保真 vs 朴素 sign() 二值化对比；
- 以 Qwen3-0.6B 真实权重做行方向 BiSCo 量化演示。

## 验证方式
- [1][2] 合成单位向量上的方向余弦对比（核心机理）；
- [3] 真实 Qwen/Qwen3-0.6B 前 2 个线性层 BiSCo 量化并比较 logits 余弦相似度（无模型时跳过并注明）。
