# Paper: 2602.17681 — LATMiX 复现说明

**论文**: LATMiX: Learnable Affine Transformations for Microscaling Quantization of LLMs

**复现内容**（针对硬件原生 MX 格式的可学习仿射变换）：

1. **MXFP4 量化器**：块大小 B=32，每块共享一个 E8M0 式 2 的幂指数缩放，块内元素量化到 FP4（E2M1 网格：0, 0.5, 1, 1.5, 2, 3, 4, 6）——论文面向的硬件原生 microscaling 格式；
2. **LATMiX 可学习仿射变换**：逐通道 `x' = (x - μ_c)·g_c`，μ 与 log g 用 Adam + 输出重建损失经 STE 穿过 MX 量化器直接优化，把激活 outlier 抑制的目标从固定旋转（Hadamard/QuaRot 式）推广到可学习可逆仿射；
3. **推理时逆变换折叠**：`W' = W / g`、偏置修正 `μ·Wᵀ`，评测完整 round trip（量化→反量化→逆变换）后的函数误差，无隐藏近似。

**对比基线**：raw MXFP4（无变换）；逐通道 absmax 均衡（AWQ 式固定缩放）。

**验证方式**：真实验证。真实 **Qwen3-0.6B** `layer0.mlp.gate_proj` 权重 + 前向 hook 捕获的真实 hidden states，输出域相对误差评测。

**运行**:

```bash
python3 demo.py                # 真实 Qwen3-0.6B
python3 demo.py --mock         # 随机回退（带 outlier 通道）
python3 demo.py --steps 1500   # 更长训练
```

**预期现象**：round trip 误差呈 raw MXFP4 > 固定 absmax 均衡 > LATMiX 可学习仿射 的递减序；训练 mse 单调下降。实测：0.2096 → 0.1954 → 0.1886。

**与论文的差异**：论文在 LLaMA/Qwen 系列上做了全模型逐层变换 + 困惑度/下游任务评测，并使用更丰富的仿射参数化与训练日程；本 demo 为单层机制级验证，仅含逐通道 shift+gain 的简化仿射族。
