# Paper: 2607.28292 - CACHE-UK

**论文**: CACHE-UK: A Stability-Aware Memory Editor for Sequentially Updated Quantized LLMs in Finance
**arXiv**: https://arxiv.org/abs/2607.28292

See `demo.py` for standalone, runnable implementation.

Run: `python3 demo.py`

## 审查结论 (2026-08-03)

### 算法一致性: 一致

| 组件 | 论文方法 | 代码实现 | 一致性 |
|------|----------|----------|--------|
| 4-bit Quantization (§3.1) | 基础 W4 权重量化 (RTN) | `FourBitQuantizer` per-channel 对称量化 | 一致 |
| Rank-1 LoRA Perturbation (§3.2) | ΔW = α · b ⊗ a 低秩扰动编辑 | `LoRAEditor` SVD rank-1 近似 + 梯度方向编辑 | 一致 |
| LoRA 方向确定 | 由编辑数据梯度决定 | `compute_edit_gradient` 对编辑数据求梯度 + SVD rank-1 近似 | 一致 |
| Finance Domain Priority (§3.3) | 内容自适应编辑强度 | `FinanceDomainPriority` 关键词检测 + 动态强度调整 | 一致 |
| 闭环稳定性控制器 (§3.4) | 退化债务跟踪 + 阈值控制 + 回滚 | `StabilityController` 退化债务累积 + 三级控制动作 | 一致 |
| 顺序更新 | 跨轮次编辑 + 灾难性遗忘防护 | 3 轮顺序编辑 + 每轮退化评估 | 一致 |
| 目标模型适配 | 原论文为金融 LLM，适配到通用 LLM | Qwen3-0.6B + 模拟金融编辑数据 | 适配 |

### 关键超参数对照

| 参数 | 论文值 | 代码值 | 备注 |
|------|--------|--------|------|
| 量化位宽 | 4-bit | 4 | 一致 |
| LoRA 秩 | rank-1 | 1 | 一致 |
| LoRA 缩放因子 α | 未明确 | 0.001 | demo 设定 (需较小以控制扰动幅度) |
| 金融关键词数 | 未明确 | 15 | demo 设定 |
| 金融编辑倍数 | 未明确 | 2.0 | demo 设定 |
| 退化债务阈值 | 未明确 | 0.05 | demo 设定 |
| 最大退化债务 | 未明确 | 0.15 | demo 设定 |
| 回滚缩减比例 | 未明确 | 0.5 | demo 设定 |
| 编辑轮次 | 未明确 | 3 | demo 设定 |
| 权重量化粒度 | Per-channel | dim=0 (per-output-channel) | 一致 |

### 算法流程说明

CACHE-UK 的核心流程为 "量化 -> 编辑 -> 控制稳定性" 的闭环：

```
1. 4-bit 量化 (FourBitQuantizer)
   └─ 对所有 Linear 层进行 W4 RTN 量化

2. 初始化基线 (StabilityController)
   └─ 在保留集上评估量化后模型的基线损失

3. 顺序编辑循环 (每轮):
   ├─ a. 金融领域优先级 (FinanceDomainPriority)
   │   └─ 根据编辑文本的金融关键词计算编辑强度
   ├─ b. 稳定性检查 (StabilityController)
   │   └─ 检查退化债务，决定控制动作 (normal/reduce/rollback)
   ├─ c. LoRA 编辑方向 (LoRAEditor)
   │   └─ 对编辑数据求梯度，SVD rank-1 近似得到 (a, b)
   ├─ d. 应用编辑 (LoRAEditor)
   │   └─ W' = W_quant + α · strength · b ⊗ a
   └─ e. 退化评估 (StabilityController)
       └─ 在保留集上评估，更新退化债务
```

### 功能验证结果

**验证方式**: 真实 Qwen3-0.6B 模型端到端量化+编辑+稳定性控制 (CPU, float32)

**验证结果**:
- 模型: Qwen3-0.6B (596.0M 参数)
- 4-bit 量化: 197 个 Linear 层 W4 RTN 量化，平均量化误差 MSE=3.52e-05，压缩至 FP32 的 12.5%
- LoRA 编辑: 3 轮顺序编辑，每轮对 197 个 Linear 层注入 rank-1 扰动
  - 编辑总扰动幅度: 0.70 -> 0.65 -> 0.49 (逐轮递减，受稳定性控制影响)
- 金融优先级: 编辑文本包含金融关键词时编辑强度增强 (最高 2.0x)
- 稳定性控制:
  - 基线损失: 6.7154 (量化后)
  - 退化轨迹: 6.24 -> 14.57 -> 11.08 (第 3 轮退化降低，回滚生效)
  - 控制动作: normal 1 次, rollback 2 次
- 内存: FP32 2.38GB -> W4 0.30GB (12.5% of FP32), LoRA 额外 0.78M 参数

**备注**:
- LoRA 扰动方向通过对编辑数据的梯度做 SVD rank-1 近似确定
- 退化债务使用衰减累积策略 (正向退化 x0.5，负向恢复 x0.3)
- 稳定性控制器三级动作: normal (正常) / reduce (降低强度) / rollback (回滚)
- 原论文针对金融领域 LLM 顺序更新，本 demo 用通用文本模拟金融内容
