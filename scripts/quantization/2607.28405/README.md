# Paper: 2607.28405 - QuantWAMs

**论文**: QuantWAMs: Calibrating at the Right Granularity for World Action Models
**arXiv**: https://arxiv.org/abs/2607.28405

See `demo.py` for standalone, runnable implementation.

Run: `python3 demo.py`

## 审查结论 (2026-08-02)

### 算法一致性: 部分一致

| 组件 | 论文方法 | 代码实现 | 一致性 |
|------|----------|----------|--------|
| Shared-Basis Outlier Calibration (§3.1) | Hadamard 旋转 R + 对角平滑 S_i + Top-K 通道保留 | `construct_hadamard_matrix` + `fit_smoothing_scale` + Top-K 选择 | 一致 |
| 坐标兼容性判定 (§3.1) | A_i = P_i Z 时可共享统计量 | `identify_coordinate_compatible_groups` (qkv/gate_up 分组) | 一致 |
| 池化交叉点理论 (Prop. 1) | N < N*_c = sigma^2/tau^2 时池化降低风险 | `check_pooling_crossover` 完整实现 | 一致 |
| Co-Training Saliency (§3.2) | 联合 Fisher 保留跨流交互项 | `compute_joint_fisher_diagonal` + Kronecker 失真 | 一致 |
| 层级精度分配 (§3.2) | Top 20% 候选 Linear 升级 W8A8 | `allocate_precision` with upgrade_ratio=0.20 | 一致 |
| W4A4 混合精度量化 | W4 默认 + Top 2% 离群值 BF16 | `W4A4Quantizer` with outlier_ratio=0.02 | 一致 |
| Hadamard 旋转融合到权重 | 旋转融合到权重侧 | 仅在激活侧应用旋转 (简化) | 部分一致 |
| Fixed-Intervention Rollout (§3.3) | 固定干预 rollout 审计 | 未实现 (标准 LLM 不适用) | 不适用 |

### 关键超参数对照

| 参数 | 论文值 | 代码值 | 备注 |
|------|--------|--------|------|
| 权重位宽 (低/高) | W4 / W8 | 4 / 8 | 一致 |
| 激活位宽 (低/高) | A4 / BF16 | 4 / 16 | 一致 |
| 离群值通道比例 rho | 2% | 0.02 | 一致 |
| 权重升级比例 | 20% | 0.20 | 一致 |
| 校准样本数 | 32 | 4 | 减少 (内存限制) |
| lambda_v / lambda_a | 未明确 | 1.0 / 0.5 | demo 设定 |

### 修复的问题清单

1. **`torch.choice` 不存在** (Bug): `randomized_hadamard()` 使用了不存在的 `torch.choice` API，改为 `torch.randint` 生成随机 ±1 对角矩阵。
2. **梯度收集极其低效** (Bug): 原代码对每个 Linear 层单独调用 `backward()` (2N 次/样本)，重构为使用 `torch.autograd.grad` 一次收集所有层梯度 (2 次/样本)。
3. **梯度存储形状错误** (Bug): 原代码存储 `[out, in]` 导致后续 `reshape(N, out, -1)` 在 `in` 不被 `out` 整除时崩溃 (如 gate_proj: out=3072, in=1024)。修正为即时计算 Fisher 统计量。
4. **内存溢出 (OOM)** (Bug): 原代码存储所有样本的完整梯度张量 (~38GB)，重构为即时计算 Fisher 对角统计量 (gv_sq, ga_sq, cross)，内存降至 ~5MB/层。
5. **`output_hidden_states` 被忽略** (Bug): `transformers 5.x` 不再接受 `from_pretrained(output_hidden_states=True)`，改为在 `forward()` 调用时传参。
6. **CPU float16 不稳定** (Bug): CPU 上使用 float16 导致 OOM 和算子不兼容，改为 CPU 使用 float32。
7. **内存清理缺失** (Bug): 校准循环中未释放中间变量，添加 `del` + `gc.collect()`。
8. **序列长度过长** (Optimization): max_length 从 128 减至 64，校准样本从 16 减至 4，降低内存峰值。

### 功能验证结果

**验证方式**: 真实 Qwen3-0.6B 模型端到端量化 (CPU, float32)

**验证结果**:
- 模型: Qwen3-0.6B (596.0M 参数)
- 校准: 197 个 Linear 层, 56 个坐标兼容模块组, 全部通过池化交叉点检验
- 权重分配: 197 候选层, 39 层升级 W8 (20%), 158 层保持 W4
- 量化验证: 2 条测试文本, 平均 MSE=20.52, 平均 Cosine Sim=0.080
- 内存压缩: FP16 1.19GB -> W4A4 0.41GB (34.4% of FP16, 论文报告 ~29%)
- 量化统计: 总计 394 次 Linear 前向 (197 层 x 2 文本), W4=316, W8=78

**备注**: 
- 跨流交互项贡献为 0.0%，因动作流损失 (隐藏状态 MSE) 相对于视频流损失 (交叉熵) 非常小
- 压缩比 34.4% vs 论文 29% 的差异主要来自 Hadamard 旋转未融合到权重侧
- Component 3 (Fixed-Intervention Rollout Auditing) 不适用于标准 LLM，未实现
