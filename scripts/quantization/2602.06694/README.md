# Paper: 2602.06694 — NanoQuant 复现说明

**论文**: NanoQuant: Efficient Sub-1-Bit Quantization of Large Language Models

**复现内容**（论文核心算法链路）：

1. **低秩二值分解**：W ≈ s·(B₁B₂)，B₁∈{±1}^{m×r}、B₂∈{±1}^{r×n}、s 为逐行 fp16 缩放；等效位宽 = r(m+n)/(mn) + 16/(mn)，当 r < mn/(m+n) 时即 **亚 1-bit**。
2. **ADMM 求解器**：连续代理 Z₁/Z₂ 的岭最小二乘更新 + ±1 二值投影 + 对偶变量上升，逐轮逼近离散约束解（SVD 初始化）。
3. **块重建微调（block reconstruction）**：ADMM 初始化后，交替精确重解 B₁/B₂ 并逐行重拟合缩放，做廉价 Gauss-Seidel 重建。

**对比基线**：朴素 1-bit sign+scale（1.00 bit/param），与亚 1-bit 分解在权重误差与输出误差上对比。

**验证方式**：真实验证。真实 **Qwen3-0.6B** `layer0.mlp.gate_proj` 的前 256 行权重（为 CPU 速度取切片）+ 前向 hook 捕获的真实激活；ADMM 全程真实迭代 30 轮并打印收敛曲线。

**运行**:

```bash
python3 demo.py                 # 真实 Qwen3-0.6B
python3 demo.py --mock          # 随机权重回退
python3 demo.py --rank 40       # 自定义秩（位宽随之变化）
```

**预期现象**：亚 1-bit（≈0.4 bit/param）低秩二值分解的重构误差应显著低于 1-bit sign+scale——即用不到一半的位宽获得更低误差。

**与论文的差异**：论文在整个 Llama2-70B 上做 block/model 级重建（25.8× 压缩、单卡 H100 13 小时）；本 demo 为单层切片上的算法机制验证，不做全模型 PPL 评测。
