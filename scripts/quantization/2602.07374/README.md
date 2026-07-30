# Paper: 2602.07374 — TernaryLM 复现说明

**论文**: TernaryLM: Memory-Efficient Language Modeling via Native 1.5-Bit Quantization with Adaptive Layer-wise Scaling

**复现内容**（论文三大训练原语）：

1. **原生三值量化 {-1, 0, +1}**（log₂3 ≈ 1.58 bit 等效精度），含幅度阈值 Δ = 0.7·E|w| 的软稀疏化；
2. **直通估计器（STE）**：前向使用三值权重，反向将量化函数在裁剪区间内视为恒等映射；
3. **自适应逐层缩放（adaptive layer-wise scaling）**：每层缩放因子 s 作为可学习参数与潜在权重联合 SGD 更新。

**实验设计**：将三值线性层训练为复现真实 **Qwen3-0.6B** `layer0.mlp.up_proj` 在真实激活上的输入→输出映射（数百步，CPU 可跑）；对比冻结的 RTN 三值基线；报告收敛曲线、最终输出误差、零值比例与显存换算（1.58 bit vs FP32）。

**验证方式**：真实验证（真实权重 + 前向 hook 捕获的真实激活 + 真实 STE 训练循环）。论文本身在 132M 参数模型上从头训练（TinyStories PPL 58.42、2.4× 显存下降）；本 demo 验证其训练原语在真实 LLM 权重上的数值行为，不做从头预训练。

**运行**:

```bash
python3 demo.py           # 真实 Qwen3-0.6B
python3 demo.py --mock    # 随机权重回退
python3 demo.py --steps 600
```

**预期现象**：STE 训练的三值层输出误差应随步数持续下降并显著低于冻结 RTN 三值基线。
