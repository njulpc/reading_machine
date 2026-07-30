# Paper: 2607.10137 — RDQ: Residual Distribution Quantization for Large Language Models

Run: `python3 demo.py`

## 复现内容
- 两级残差量化：粗量化后对残差分布（近高斯）用高斯最优非均匀电平做第二级量化；
- 残差分布形态统计（峰度≈0）与 2-bit / RDQ 2+2 / 4-bit 的 MSE 对比；
- 以 Qwen3-0.6B 真实权重做 RDQ(3+2) 量化演示。

## 验证方式
- [1][2] 合成权重上的残差统计与 MSE 对比（核心机理）；
- [3] 真实 Qwen/Qwen3-0.6B 前 2 个线性层 RDQ 量化并比较 logits 余弦相似度（无模型时跳过并注明）。
