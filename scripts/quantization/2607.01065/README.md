# Paper: 2607.01065 — GSRQ: Gain-Shape Residual Quantization for Sub-1-bit KV Cache

Run: `python3 demo.py`

## 复现内容
- 高维 ℓ₂ K-means 质心收缩现象的定量演示（质心/成员模长比 <1）；
- Gain-Shape K-means（模长与方向分离的码本学习）；
- 残差量化（RQ）管线用于亚 1-bit KV 缓存压缩；
- 以 Qwen3-0.6B 第 0 层真实 K cache 向量为对象的 GSRQ 重建验证。

## 验证方式
- [1]–[3] 合成高维数据上对比 K-means vs GSKM 的角度保真与 ℓ₂ 失真（核心机理）；
- [4] 真实 Qwen/Qwen3-0.6B 前向取 past_key_values，对 K 向量做 GSRQ 重建并报告余弦相似度（无模型时跳过并注明）。
