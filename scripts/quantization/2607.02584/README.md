# Paper: 2607.02584 — RotateAttention: RoPE-Aware Rotation and Range Rectification for INT4 Quantized Attention

Run: `python3 demo.py`

## 复现内容
- 3D RoPE 维度划分对 Q/K 异常值分布的影响演示；
- RoPE 感知（可融合）旋转抑制异常值（Hadamard 实现）；
- 非负注意力矩阵 P 的范围优化无符号 INT4 量化（固定缩放/零点用满 [0,15]）；
- 以 Qwen3-0.6B 为目标的 INT4 注意力权重量化演示。

## 验证方式
- [1]–[3] 合成张量上验证异常值抑制与 P 量化分辨率提升（核心机理）；
- [4] 真实 Qwen/Qwen3-0.6B 前 2 个 Q/K 投影层 INT4 量化并比较 logits 余弦相似度（无模型时跳过并注明）。
