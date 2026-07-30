# Paper: 2607.04302 — HiFA4: Training-Free 4-bit FlashAttention on Ascend HIF4 NPUs

Run: `python3 demo.py`

## 复现内容
- HIF4 风格 4-bit 块量化器（E2M1 网格 + 幂次缩放）；
- Smooth-QK：RoPE 后逐通道静态等价重缩放，把量化难度从 K 转移到 Q（注意力 logits 不变性断言）；
- P-Reordering：归一化项与 PV GEMM 使用同一量化 P_hat，消除相干输出缩放误差；
- 以 Qwen3-0.6B 为目标的注意力量化演示。

## 验证方式
- [1][2] 合成张量上验证平滑后 K 量化 MSE 下降、logits 等价性、归一化一致性（核心机理）；
- [3] 真实 Qwen/Qwen3-0.6B 前 2 个注意力投影层 HIF4 量化并比较 logits 余弦相似度（无模型时跳过并注明）。
