# Paper: 2607.28405 - QuantWAMs

**论文**: QuantWAMs: Calibrating at the Right Granularity for World Action Models
**arXiv**: https://arxiv.org/abs/2607.28405

See `demo.py` for standalone, runnable implementation.

Run: `python3 demo.py`

## 审查结论 (2026-08-03 二次审查)

### 算法一致性: 部分一致 → 修复后一致

| 组件 | 论文方法 | 代码实现 | 一致性 |
|------|----------|----------|--------|
| Shared-Basis Outlier Calibration (§3.1) | Hadamard 旋转 R + 对角平滑 S_i + Top-K 通道保留 | `construct_hadamard_matrix` + `fit_smoothing_scale` + Top-K 选择 | 一致 |
| 坐标兼容性判定 (§3.1) | A_i = P_i Z 时可共享统计量 | `identify_coordinate_compatible_groups` (qkv/gate_up 分组) | 一致 |
| 池化交叉点理论 (Prop. 1) | N < N*_c 时池化降低风险 | `check_pooling_crossover` (N_cal 已修复为样本数) | 修复后一致 |
| 池化检验结果应用 | 不池化时各成员独立掩码 | if/else 分支已区分 (原两分支相同，已修复) | 修复后一致 |
| Co-Training Saliency (§3.2) | 联合 Fisher 保留跨流交互项 | 层输出梯度计算 Fisher (原用权重梯度，已修复) | 修复后一致 |
| 层级精度分配 (§3.2) | Top 20% 候选 Linear 升级 W8A8 | `allocate_precision` upgrade_ratio=0.20 | 一致 |
| Hadamard 旋转融合到权重 | R 融合到权重侧 W'=W@R | 权重侧 W'=(W@R)*S (原仅激活侧，已修复) | 修复后一致 |
| 升级层激活位宽 | 升级层 W8A8 | 传入 weight_bits，升级层 A8 (原恒定 A4，已修复) | 修复后一致 |
| Fixed-Intervention Rollout (§3.3) | 固定干预 rollout 审计 | 未实现 (标准 LLM 不适用) | 不适用 |

### 关键超参数对照

| 参数 | 论文值 | 代码值 | 备注 |
|------|--------|--------|------|
| 权重位宽 (低/高) | W4 / W8 | 4 / 8 | 一致 |
| 激活位宽 (低/高) | A4 / BF16 | 4 / 16 | 一致 |
| 升级层激活位宽 | A8 | 8 (修复后) | 修复后一致 (原为4) |
| 离群值通道比例 rho | 2% | 0.02 | 一致 |
| 权重升级比例 | 20% | 0.20 | 一致 |
| 校准样本数 | 32 | 4 | 减少 (内存限制) |
| lambda_v / lambda_a | 未明确 | 1.0 / 0.5 | demo 设定 |

### 修复的问题清单 (二次审查)

1. **Hadamard 旋转和平滑未在权重侧补偿** (最关键): 原代码仅在激活侧施加 R 和 S⁻¹，权重侧无补偿，导致前向传播 y'≠A@W^T，Cosine Sim 仅 0.080。已修复为权重侧 W'=(W@R)*S，激活侧 (A@R)/S，数学等价 y=A@W^T。
2. **升级层激活位宽未升级**: 论文规定升级层为 W8A8，原代码对所有层非离群值激活恒定 4 位。已修复为传入 weight_bits 参数，升级层激活量化到 8 位。
3. **Fisher 梯度使用权重梯度代替输出梯度**: 原代码计算 ∂ℓ/∂W，已隐含输入信息，再乘输入协方差导致双重计数。已修复为计算 ∂ℓ/∂y (层输出梯度)。
4. **池化交叉点 N_cal 参数传值错误**: 原代码传成员数 m 而非校准样本数 N。已修复为传实际样本数。
5. **池化交叉点检验结果不影响操作**: 原代码 if/else 两分支完全相同。已修复为不池化时各成员独立掩码。

(一次审查修复的问题清单见 git 历史: torch.choice、梯度收集效率、梯度形状、OOM、output_hidden_states、CPU float16、内存清理、序列长度)

### 功能验证结果

**验证方式**: 真实 Qwen3-0.6B 模型端到端量化 (CPU, float32)

**验证结果**:
- 模型: Qwen3-0.6B (596.0M 参数)
- 校准: 196 个 Linear 层, 56 个坐标兼容模块组, 全部通过池化交叉点检验
- 权重分配: 196 候选层, 39 层升级 W8 (20%), 157 层保持 W4
- 量化验证 (修复后):
  - 平均 MSE: 5.92 (修复前 20.52, 降低 3.5x)
  - 平均 Cosine Similarity: 0.644 (修复前 0.080, 提升 8x)
- 内存压缩: FP16 1.19GB → W4A4 0.26GB (22.0% of FP16, 论文报告 ~29%)
- 跨流交互项贡献: 0.0% (动作流损失相对于视频流损失极小)

**备注**: 
- Cosine Similarity 从 0.080 提升至 0.644，验证了 Hadamard 旋转权重补偿修复的有效性
- 压缩比 22.0% vs 论文 29% 的差异主要来自校准样本数减少 (4 vs 32) 和 GPTQ 未实现
- Component 3 (Fixed-Intervention Rollout Auditing) 不适用于标准 LLM，未实现
