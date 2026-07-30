# Paper: 2607.24377 — MXAttention: Data-Free Optimal Scaling and Pre-Normalization Quantization for MXFP4

Run: `python3 demo.py`

## 复现内容
- MXFP4（E2M1 + 32 元素幂次块缩放）量化器，UOS 边界 Qmax=7.25 vs OCP/TFS 对比；
- 上溢舍入区比例验证（论文约 19.27%）；
- PNQ：在线 softmax 行和与 PV 使用同一量化块，构造性保证行归一化；
- 以 Qwen3-0.6B 为目标的注意力权重 MXFP4 量化演示。

## 验证方式
- [1]–[3] 合成张量上验证量化误差、溢出区比例与行和（核心机理）；
- [4] 真实 Qwen/Qwen3-0.6B 前 2 个注意力投影层 MXFP4(UOS) 量化并比较 logits 余弦相似度（无模型时跳过并注明）。
