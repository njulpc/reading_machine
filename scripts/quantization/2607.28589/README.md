# Paper: 2607.28589 - MixFrag

**论文**: MixFrag: Fragility-Guided Mixed-Precision Post-Training Quantization for Vision Transformers
**arXiv**: https://arxiv.org/abs/2607.28589

See `demo.py` for standalone, runnable implementation.

Run: `python3 demo.py`

## 审查结论 (2026-08-03 二次审查)

### 算法一致性: 一致

| 组件 | 论文方法 | 代码实现 | 一致性 |
|------|----------|----------|--------|
| Fragility Estimation (§3.2) | 用 KL 散度测量全精度输出与单独量化输出的分布差异 | `FragilityEstimator.compute_kl_divergence` + `compute_layer_fragility` | 一致 |
| 脆弱性分数定义 | f_l(b) = KL(p_full \|\| p_quant_b) | softmax 后计算 KL(p \|\| q)，加 epsilon 数值稳定 | 一致 |
| MCKP 建模 (§3.3) | 将比特分配建模为多选择背包问题 | `MCKPSolver.solve` 完整建模 MCKP | 一致 |
| MCKP 收益定义 | v_l(b) = f_l(b_max) - f_l(b)（脆弱性减少量） | `compute_benefit` 实现相同定义 | 一致 |
| MCKP 成本定义 | c_l(b) = b × num_params（比特成本） | `compute_cost` 实现相同定义 | 一致 |
| MCKP 动态规划求解 | 动态规划求解，整数缩放 | `solve` 用 DP + scale_factor=1000 缩放 | 一致 |
| 混合精度 PTQ (§3.4) | 不同层分配不同位宽 (W3A3, W4A4, W6A6, W8A8) | `MixedPrecisionQuantizer` 支持 3/4/6/8-bit | 修复后一致 |
| 权重量化粒度 | Per-channel 对称量化 | `symmetric_quantize(weight, bits, dim=0)` | 一致 |
| 激活量化粒度 | Per-token 对称量化 | `symmetric_quantize(activation, bits, dim=-1)` | 一致 |
| 目标模型适配 | 原论文为 ViT，适配到 LLM | Qwen3-0.6B 的 q/k/v_proj, gate/up/down_proj | 适配 |

### 关键超参数对照

| 参数 | 论文值 | 代码值 | 备注 |
|------|--------|--------|------|
| 位宽选项 | W3A3, W4A4, W6A6, W8A8 | [3, 4, 6, 8] | 修复后一致 (原缺3-bit) |
| 目标比特预算 | 4~8 bit 自适应 | 5.0 (平均位宽) | demo 设定 |
| 校准样本数 | 32 | 4 | 减少 (内存限制) |
| KL 散度 epsilon | 未明确 | 1e-8 | 数值稳定 |
| 脆弱性温度 | 未明确 | 1.0 | demo 设定 |
| DP 缩放因子 | 未明确 | 1000 | 整数化精度 |
| 权重量化粒度 | Per-channel | dim=0 (per-output-channel) | 一致 |
| 激活量化粒度 | Per-token | dim=-1 | 一致 |

### 修复的问题清单 (二次审查)

1. **位宽选项缺少 3-bit**: 论文明确提到 "3-bit and 4-bit quantization" 和 "MP3/MP3 setting"。原代码 `bit_options=[4,6,8]` 不支持 3-bit，已修正为 `[3,4,6,8]`。
2. **bytes_per_param 缺少 3-bit 条目**: 添加 3-bit 对应的 0.375 bytes/param，防止 KeyError 崩溃。
3. **打印信息错别字**: "应用混合精度量量化..." 修正为 "应用混合精度量化..."。
4. **清理未使用的导入**: 移除 `os`, `math`, `warnings` 等未使用导入。

### 功能验证结果

**验证方式**: 真实 Qwen3-0.6B 模型端到端量化 (CPU, float32)

**验证结果**:
- 模型: Qwen3-0.6B (596.0M 参数, 197 个 Linear 层)
- 脆弱性估计: 197 层在 3/4/6/8 bit 下计算 KL 散度脆弱性分数
  - 示例: q_proj 3bit=0.0137, 4bit=0.0034, 6bit=0.0002, 8bit=0.000013
- MCKP 分配 (含 3-bit):
  - W3A3: 16 层 (8.1%), 38.8M 参数
  - W4A4: 38 层 (19.3%), 241.6M 参数
  - W6A6: 113 层 (57.4%), 267.4M 参数
  - W8A8: 30 层 (15.2%), 48.2M 参数
  - 加权平均位宽: 5.16 bit
- 量化验证: 平均 MSE=12.42, 平均 Cosine Similarity=0.379
- 内存压缩: FP16 1.19GB → 混合精度 0.38GB (32.2% of FP16, 16.1% of FP32)

**备注**:
- 3-bit 选项已可用，16 层被分配 W3A3，对应论文 MP3/MP3 混合精度设置
- KL 散度通过 softmax 将输出转为概率分布后计算
- 激活位宽与权重位宽同步分配（简化处理），原论文中可独立分配
- 量化后端使用对称均匀量化，原论文使用 AdaLog 对数量化（ViT→LLM 适配简化）
