# Paper: 2602.13710 — HBVLA 复现说明

**论文**: HBVLA: Pushing 1-Bit Post-Training Quantization for Vision-Language-Action Models

**复现内容**（论文三大机制，均为架构无关的 1-bit PTQ 技术）：

1. **策略感知增强 Hessian**：用对角 Hessian 代理 `s = W²·E[x²]` 识别对输出（VLA 场景即动作）真正关键的显著权重，显著权重走 fp16 保护路径；
2. **稀疏正交/ Harr 域变换**：对非显著权重做随机 Hadamard（Harr）变换，诱导高斯化的低熵中间分布；
3. **Harr 域分组 1-bit 量化**：在变换域做逐组 sign+scale 1-bit 量化后逆变换回原域。

**对比基线**：朴素 1-bit sign+scale；无显著性拆分的全域 Harr 1-bit（消融）。

**验证方式**：真实验证。真实 **Qwen3-0.6B** `layer0.mlp.down_proj` 前 256 行权重 + 前向 hook 捕获的真实激活（充当"策略"信号），输出域相对误差评测。Qwen3-0.6B 是 LLM 而非 VLA，但三项机制与架构无关。

**运行**:

```bash
python3 demo.py                # 真实 Qwen3-0.6B
python3 demo.py --mock         # 随机回退
python3 demo.py --salient 0.03
```

**预期现象**：HBVLA（显著保护 + Harr 域 1-bit）输出误差应显著低于朴素 1-bit，并优于无拆分的 Harr 消融。

**与论文的差异**：论文在 OpenVLA-OFT（LIBERO 92.2% 性能保持）、CogAct（93.6%）及真实机器人上闭环验证；本 demo 为开环单层机制级验证。
