# Paper: 2602.02151 — VQRound 复现说明

**论文**: Revisiting Adaptive Rounding with Vectorized Reparameterization for LLM Quantization

**复现内容**（论文核心思想）：

1. **自适应舍入**：每个权重的舍入方向 Δ∈{0,1}（向上/向下）作为可学习变量，实现跨元素误差抵消，替代 round-to-nearest；
2. **码本重参数化（vectorized reparameterization）**：将稠密逐元素舍入矩阵压缩为"K 个长度为 g 的舍入模式原型 + 每组 soft assignment  logits"，可训练参数量从 m·n 降至 K·g + m·(n/g)·K 的一小部分；
3. **L∞ 最差情况误差**：在 MSE 输出重建损失之外加入逐元素误差的 smooth-max（logsumexp）惩罚，呼应论文对重尾权重分布下最坏误差的强调；
4. **128 校准样本**的轻量端到端微调流程。

**对比**：RTN / 稠密逐元素自适应舍入（AdaRound 式）/ VQRound 码本版，报告输出相对误差、逐元素 L∞ 误差与可训练参数量对比。

**验证方式**：真实验证。真实 **Qwen3-0.6B** `layer0.mlp.down_proj` 前 256 行权重 + 前向 hook 捕获的 **128 条真实校准激活**（与论文样本数一致），W4 量化，200 步真实优化（STE）。

**运行**:

```bash
python3 demo.py           # 真实 Qwen3-0.6B
python3 demo.py --mock    # 随机权重回退
python3 demo.py --bits 3 --steps 400
```

**预期现象**（实测于真实 Qwen3-0.6B 单层切片，W3）：稠密逐元素自适应舍入显著优于 RTN（输出误差约 0.24 → 0.08）；码本版以约 0.26% 的可训练参数量稳定收敛到接近 RTN 的水平。这如实反映了论文讨论的表达力-可扩展性权衡：论文通过**跨层联合码本微调**在全模型尺度上弥补码本表达力，本 demo 为单层机制复现，未做跨层联合优化。

**与论文的差异**：论文在 OPT/LLaMA/LLaMA2/Qwen3 全模型上做跨层联合优化并评估 PPL/下游任务；本 demo 为单层机制级复现。
