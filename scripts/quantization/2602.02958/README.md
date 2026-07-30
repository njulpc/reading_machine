# Paper: 2602.02958 — Quant VideoGen (QVG) 复现说明

**论文**: Quant VideoGen: Auto-Regressive Long Video Generation via 2-Bit KV-Cache Quantization

**复现内容**（论文两大训练自由机制，均为模态无关的 KV cache 压缩技术）：

1. **语义感知平滑（Semantic-Aware Smoothing）**：利用相邻位置的冗余，先对 K/V 沿序列轴做逐通道滑动平均提取"语义分量"，再对**低幅值残差**做量化——残差比原始值对量化更友好；
2. **渐进残差量化（Progressive Residual Quantization）**：第一阶段粗比特（4-bit）量化平滑参考，第二阶段 2-bit 量化残差，可选第三阶段对剩余误差再量化，构成粗到细的"质量-显存"平滑调节。

**对比基线**：对原始 K/V 直接做逐通道 2-bit RTN。**评测指标**：用反量化 cache 重算注意力输出 softmax(QKᵀ)V 的相对误差 + 显存换算。

**验证方式**：真实验证。用真实 **Qwen3-0.6B** 在长提示（约 2400 字符重复文本，相邻位置冗余强，对应视频的时序冗余）上做真实前向，截取第 0 层真实 KV cache 进行实验。

**运行**:

```bash
python3 demo.py           # 真实 Qwen3-0.6B
python3 demo.py --mock    # 合成的冗余 KV cache 回退
python3 demo.py --bits 2
```

**预期现象**：在相同的 2-bit 预算下，QVG（平滑+渐进残差）的注意力输出误差应显著低于直接 2-bit RTN；第三阶段进一步降低误差。

**与论文的差异**：论文面向自回归视频扩散模型（LongCat Video 等基准，KV cache 显存最高降 7.0×）；本 demo 将同样机制应用于 LLM 文本 KV cache 验证其数值有效性，不涉及视频生成质量评测。
