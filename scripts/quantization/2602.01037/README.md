# Paper: 2602.01037 — VEQ 复现说明

**论文**: VEQ: Modality-Adaptive Quantization for MoE Vision-Language Models

**复现内容**（论文两大核心机制）：

1. **模态-专家感知量化（Modality-expert-aware）**：利用专家激活频率（expert activation frequency），对"关键专家"优先最小化量化误差——demo 中体现为按专家点火频率 `freq_e` 提升其 Hessian 权重。
2. **模态亲和感知 Hessian（Modality-affinity-aware）**：用 token-专家亲和度 + 模态信息构建增强 Hessian 指导校准——demo 中 Hessian 按 `affinity(token, expert)` 加权两种模态（文本/视觉）token 的二阶统计。

量化器为 GPTQ 式 Hessian 误差补偿算法（cholesky 递推），对比"无权重 Hessian 的标准 GPTQ"。

**验证方式**：半真实验证。Qwen3-0.6B 是稠密模型（无 MoE），因此构造**模拟 MoE 层**：3 个"专家"取真实 Qwen3-0.6B `layer0.mlp.gate_proj` 权重的三个切片（保证真实 LLM 权重分布）；文本 token 为用前向 hook 捕获的**真实隐状态**，视觉 token 为低秩+重尾噪声合成的模拟 ViT 特征。评测为两个模态留出校准 token 上的专家输出相对误差。

**运行**:

```bash
python3 demo.py          # 真实 Qwen3-0.6B 权重
python3 demo.py --mock   # 全随机回退
```

**预期现象**：VEQ 加权 Hessian 的量化误差应集中在低频/低亲和 token 上，关键专家与高亲和模态的输出误差低于无权重 GPTQ。

**与论文的差异**：论文在 Kimi-VL、Qwen3-VL 等真实 MoE VLM 上做 W3A16 全模型评测（报告平均精度提升 2.04%/3.09%）；本 demo 为单层机制级验证，不涉及多模态端到端 benchmark。
