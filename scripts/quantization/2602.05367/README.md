# Paper: 2602.05367 — RaBiT 复现说明

**论文**: RaBiT: Residual-Aware Binarization Training for Accurate and Efficient LLMs

**复现内容**（论文核心机制）：

1. **残差层级（residual hierarchy）**：W ≈ Σᵢ αᵢ·Bᵢ 的多条 ±1 二值路径**依次**从共享全精度权重的残差中导出——R₀=W，第 i 条路径拟合 R_{i-1} 后更新 Rᵢ = R_{i-1} − αᵢBᵢ，保证每条路径纠正前一条的误差，从算法上杜绝论文所称的 inter-path adaptation（并行路径学出冗余特征）。
2. **功能保持初始化（functional preservation）**：在权重域最小二乘之后，再在校准激活上用**输出域最小二乘**重拟合每条路径的缩放 αᵢ，优先保持层功能而非权重数值。

**对比基线**：2-bit RTN；naive multi-binary（k 条路径同时拟合完整权重、各分摊 1/k 缩放——即论文指出的共适应失败模式）；RaBiT 仅权重域最小二乘（消融）。

**验证方式**：真实验证。加载真实 **Qwen3-0.6B** `layer0.mlp.down_proj` 权重（1024×3072），用前向 hook 捕获真实校准激活，报告权重相对误差与输出相对误差。

**运行**:

```bash
python3 demo.py            # 真实 Qwen3-0.6B
python3 demo.py --mock     # 随机权重回退
python3 demo.py --paths 3  # 3 条二值路径（~3-bit 等效）
```

**预期现象**：RaBiT（残差层级 + 功能保持初始化）的输出误差应显著低于 naive 多二值与 2-bit RTN。

**与论文的差异**：论文为完整 QAT 训练框架并在多个 LLM 上评估下游精度；本 demo 复现其初始化与残差推导机制的数值行为（训练循环本身不在范围内）。
