# Paper: 2607.24953 — Stable FP4 Training via Transposition-Invariant Block Quantization

Run: `python3 demo.py`

## 复现内容
- 1D 块量化的转置缩放不一致现象演示（Q(W) ≠ Q(Wᵀ)ᵀ）；
- 2D 块 FP4 量化（转置不变缩放）；
- 无截断缩放 + 随机舍入（梯度无偏性验证）；
- Q/K 投影 MXFP8、其余 FP4 的混合精度设计；
- 以 Qwen3-0.6B 为目标模型的量化演示。

## 验证方式
- [1][2] 在合成矩阵上量化并比较转置前后逐元素不一致比例（核心机理验证）；
- [3] 多次随机舍入平均偏差 vs 确定性舍入偏差；
- [4] 真实 Qwen/Qwen3-0.6B 上对前 3 个线性层应用 2D 块量化并比较 logits 余弦相似度（无模型时跳过并注明）。
