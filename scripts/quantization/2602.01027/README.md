# Paper: 2602.01027 — SFMP 复现说明

**论文**: SFMP: Fine-Grained, Hardware-Friendly and Search-Free Mixed-Precision Quantization for Large Language Models

**复现内容**（对应论文四大创新中的前三个算法级思想）：

1. **分数位宽（Fractional bit-width）**：不通过离散搜索，而是用"高/低精度块的混合比例"精确实现任意平均位宽（如 3.25 bit）。
2. **块级混合精度（Block-wise mixed-precision）**：权重被划分为规则的 B×B 块（硬件友好），每块按其显著性被分配到高/低精度。
3. **行列重排（Row-column reordering）**：按激活感知显著性（|W|·√E[x²]，AWQ 式）对行、列排序，使显著权重聚集到连续区域，从而让规则块网格覆盖绝大多数显著权重。
4. 论文第 4 点（统一 GEMM kernel）属于硬件实现，不在本 demo 范围内。

**验证方式**：真实验证。demo 加载真实 **Qwen3-0.6B** 权重（`layer0.mlp.gate_proj`，形状 3072×1024），并用前向 hook 在真实校准句上捕获真实激活；对比

- 基线：统一低比特 RTN；
- 消融：块级混合精度但**不重排**；
- SFMP 完整流程（重排 + 分数位宽块级混合精度）。

三者均在相同或更低的平均位宽下比较权重相对误差与输出相对误差。

**运行**:

```bash
python3 demo.py          # 真实 Qwen3-0.6B（需网络下载，~1.4GB，已缓存则秒载）
python3 demo.py --mock   # 随机权重回退（无网络时）
```

**预期现象**：SFMP（重排+分数位宽）在相同平均位宽下的输出误差应明显低于不重排的块级混合精度，接近或优于统一高一档位宽的 RTN。

**与论文的差异**：论文在 LLaMA/Qwen 全模型上评估 WikiText-2 PPL 与下游任务，并实现了自定义 GEMM kernel；本 demo 在单层真实权重+真实激活上验证算法本身的数值行为，不涉及 kernel 与全模型评测。
