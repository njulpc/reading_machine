# Paper: 2602.12609 — QuEPT 复现说明

**论文**: QuEPT: Quantized Elastic Precision Transformers with One-Shot Calibration for Multi-Bit Switching

**复现内容**（弹性多位宽量化，一次校准多位宽切换）：

1. **4-bit 基底**：逐输出通道对称均匀 4-bit RTN 量化，作为存储与切换的基座；
2. **级联低位宽 adapter**：对每个更低目标位宽 b ∈ {3, 2}，重建误差 `E_b = W - Q_b(W)` 用秩 r 低秩 adapter 逼近——**激活加权 SVD**（权重 `s = sqrt(E[x²])` 逐输入通道，来自同一小校准切片），校准一次（one-shot）、无需重复优化；
3. **实时切换**：部署时在 b-bit 量化权重上挂载 adapter_b 即可从 4-bit 基底切到 b-bit，有效位宽 = b + adapter 开销 `r·(m+n)·16/(m·n)`（r=16 时约 0.33 bit/param）。

**对比基线**：各位宽 raw RTN 量化；4-bit 基底作精度参照。

**验证方式**：真实验证。真实 **Qwen3-0.6B** `layer0.mlp.gate_proj` 权重 + 前向 hook 捕获的真实 hidden states（同一校准切片同时用于 SVD 加权与评测），输出域相对误差。

**运行**:

```bash
python3 demo.py                # 真实 Qwen3-0.6B
python3 demo.py --mock         # 随机回退
python3 demo.py --rank 8       # 更小 adapter
```

**预期现象**：adapter 修正后的 3/2-bit 输出误差应明显低于对应 raw 量化，且只增加约 0.33 bit/param。实测：3-bit 0.2285 → 0.1855（3.33 bit）；2-bit 0.6387 → 0.4604（2.33 bit）；4-bit 基底 0.0981。

**与论文的差异**：论文在完整 Transformer（LLM/ViT）上做逐 block 多位宽误差重建，并含 MB-ToMe（Multi-Bit Token Merging）跨位宽 token 融合机制与困惑度/下游任务评测；本 demo 为单层机制级验证，仅含低秩 adapter 校准与切换核心。
