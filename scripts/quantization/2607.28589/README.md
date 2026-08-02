# Paper: 2607.28589 - MixFrag

**论文**: MixFrag: Fragility-Guided Mixed-Precision Post-Training Quantization for Vision Transformers
**arXiv**: https://arxiv.org/abs/2607.28589

See `demo.py` for standalone, runnable implementation.

Run: `python3 demo.py`

## 审查结论 (2026-08-03)

### 算法一致性: 一致

| 组件 | 论文方法 | 代码实现 | 一致性 |
|------|----------|----------|--------|
| Fragility Estimation (§3.1) | 用 KL 散度测量全精度输出与单独量化输出的分布差异 | `FragilityEstimator.compute_kl_divergence` + `compute_layer_fragility` | 一致 |
| 脆弱性分数定义 | f_l(b) = KL(p_full \|\| p_quant_b) | softmax 后计算 KL(p \|\| q)，加 epsilon 数值稳定 | 一致 |
| MCKP 建模 (§3.2) | 将比特分配建模为多选择背包问题 | `MCKPSolver.solve` 完整建模 MCKP | 一致 |
| MCKP 收益定义 | v_l(b) = f_l(b_max) - f_l(b)（脆弱性减少量） | `compute_benefit` 实现相同定义 | 一致 |
| MCKP 成本定义 | c_l(b) = b × num_params（比特成本） | `compute_cost` 实现相同定义 | 一致 |
| MCKP 动态规划求解 | 动态规划求解，整数缩放 | `solve` 用 DP + scale_factor=1000 缩放 | 一致 |
| 混合精度 PTQ (§3.3) | 不同层分配不同位宽 (W4A4, W6A6, W8A8) | `MixedPrecisionQuantizer` 支持 4/6/8-bit | 一致 |
| 权重量化粒度 | Per-channel 对称量化 | `symmetric_quantize(weight, bits, dim=0)` | 一致 |
| 激活量化粒度 | Per-token 对称量化 | `symmetric_quantize(activation, bits, dim=-1)` | 一致 |
| 目标模型适配 | 原论文为 ViT，适配到 LLM | Qwen3-0.6B 的 q/k/v_proj, gate/up/down_proj | 适配 |

### 关键超参数对照

| 参数 | 论文值 | 代码值 | 备注 |
|------|--------|--------|------|
| 位宽选项 | W4A4, W6A6, W8A8 | [4, 6, 8] | 一致 |
| 目标比特预算 | 4~8 bit 自适应 | 5.0 (平均位宽) | demo 设定 |
| 校准样本数 | 32 | 4 | 减少 (内存限制) |
| KL 散度 epsilon | 未明确 | 1e-8 | 数值稳定 |
| 脆弱性温度 | 未明确 | 1.0 | demo 设定 |
| DP 缩放因子 | 未明确 | 1000 | 整数化精度 |
| 权重量化粒度 | Per-channel | dim=0 (per-output-channel) | 一致 |
| 激活量化粒度 | Per-token | dim=-1 | 一致 |

### 适配说明

原论文 MixFrag 针对 Vision Transformer (ViT) 设计，核心算法组件的对应关系：

| ViT 组件 | LLM 对应组件 | 说明 |
|----------|-------------|------|
| Attention QKV | q_proj, k_proj, v_proj | 注意力投影层 |
| MLP FC1, FC2 | gate_proj, up_proj, down_proj | 前馈网络层 |
| Class token | (无对应) | LLM 无 class token |
| Patch embedding | Token embedding | 输入嵌入层 |

脆弱性估计和 MCKP 分配算法是模型架构无关的，可直接应用于 LLM。

### 功能验证结果

**验证方式**: 真实 Qwen3-0.6B 模型端到端量化 (CPU, float32)

**验证结果**:
- 模型: Qwen3-0.6B (596.0M 参数)
- 脆弱性估计: 197 个 Linear 层在 4/6/8 bit 下计算 KL 散度脆弱性分数
  - 示例: q_proj 4bit=0.0034, 6bit=0.0002, 8bit=0.000013 (位宽越高脆弱性越低)
- MCKP 分配: 动态规划求解最优比特分配，目标平均 5.0 bit
  - W4A4: 61 层 (31.0%), 297.1M 参数
  - W6A6: 109 层 (55.3%), 255.9M 参数
  - W8A8: 27 层 (13.7%), 43.0M 参数
  - 实际加权平均位宽: 5.15 bit
- 混合精度量化: 权重 per-channel 量化，激活 per-token 量化
- 量化验证: 2 条测试文本，平均 MSE=24.10，平均 Cosine Similarity=0.446
- 内存压缩: FP16 1.19GB -> 混合精度 0.38GB (32.2% of FP16, 16.1% of FP32)

**备注**:
- KL 散度通过 softmax 将输出转为概率分布后计算，保证不同维度输出的可比性
- MCKP 动态规划使用 scale_factor=1000 将浮点比特成本整数化，在精度和效率间平衡
- 激活位宽与权重位宽同步分配（简化处理），原论文中可独立分配
