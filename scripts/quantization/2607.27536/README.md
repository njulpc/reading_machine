# GyRot: 2607.27536 复现代码

## 论文信息

> **⚠️ 重要审查发现：论文 ID 错误匹配**
>
> 经 arXiv 核查，**2607.27536 实际论文标题为 "Strategy, Not Payoffs: A Behavioural Embedding of Normal-Form Games"**（作者 Joshua Caiata 等），内容涉及博弈论与 LLM 策略迁移，**与量化完全无关**。
>
> 本目录下的复现代码（GyRot 方法）对应的论文可能使用了错误的 arXiv ID。README 中记录的 GyRot 论文信息（标题、作者）与 arXiv 2607.27536 实际内容不符。**代码实现本身是一个合理的旋转+分组量化算法，但无法验证其是否对应任何真实发表的论文。**

---

## 核心方法复现

本 demo 实现了 GyRot 的三大核心组件：

### 1. CoRFiG (Coarse Rotation, Fine Grouping)
- **粗粒度旋转**: 使用 Hadamard 变换在较大块（如 512 元素）上执行旋转，抑制全局异常值
- **细粒度分组**: 在旋转后的张量上以小组（如 128 元素）执行组量化
- **粒度解耦**: 旋转粒度 > 分组粒度，避免全局变换对局部缩放的干扰

### 2. HAP (Harmonic-Aligned Permutation)
- 在组内对元素排序，使数值分布与组边界对齐
- 减少跨组边界的数值不连续性
- 通过逆置换恢复原始顺序

### 3. 零舍入非对称量化
- 将零点舍入到最近的整数
- 调整缩放因子补偿舍入误差
- 实现完全整数反量化（模拟固定点运算）

## 文件说明

| 文件 | 说明 |
|------|------|
| `demo.py` | 主演示脚本，包含完整算法实现 |
| `mock_validate.py` | Mock 模型验证脚本（资源受限时使用） |

## 运行方式

### 方式一：合成权重验证（无需下载模型）
```bash
python3 demo.py --synthetic
```

此模式生成带有异常值的合成权重矩阵，模拟 LLM 权重分布，验证 CoRFiG 相对于直接分组量化的精度提升。

### 方式二：真实模型量化（需要 transformers）
```bash
pip install transformers accelerate
python3 demo.py --model Qwen/Qwen3-0.6B
```

对 Qwen3-0.6B 模型的 q_proj 层执行 GyRot 量化，用 `GyRotLinear` 包装层替换原始 `Linear`，在 forward 中同步旋转输入，并生成文本验证效果。可用 `--max-layers N` 限制真实模型验证时的 q_proj 层数量；`0` 表示全部 q_proj 层。

**注意**: 如果无法下载模型权重（网络限制或权限问题），请使用 `--synthetic` 模式或 `mock_validate.py` 验证算法逻辑。代码中的算法实现不依赖特定模型权重。

### 方式三：Mock 模型验证（推荐，资源受限时）
```bash
python3 mock_validate.py
```

使用小型随机初始化模型验证全部代码路径可执行，包括量化、推理和生成。

## 算法流程

```
输入: 权重矩阵 W [out_features, in_features]
      量化位宽 n_bits (默认 4)
      粗旋转块大小 coarse_block_size (默认 512)
      细分组大小 group_size (默认 128)

步骤 1: 粗粒度旋转
    - 将 W 划分为 coarse_block_size 的块
    - 对每个块应用 Hadamard 旋转
    - 结果: W_rot（全局异常值被分散）

步骤 2: 细粒度分组
    - 将 W_rot 划分为 group_size 的组
    - 结果: W_groups [n_groups, group_size]

步骤 3: 谐波对齐置换 (HAP)
    - 对每组内元素排序
    - 记录置换索引 perm_indices
    - 结果: W_sorted（数值分布对齐组边界）

步骤 4: 组级非对称量化
    - 计算每组 wmin, wmax
    - scale = (wmax - wmin) / (2^n_bits - 1)
    - zero_point_raw = -wmin / scale
    - zero_point = round(zero_point_raw)  ← 零舍入
    - w_q = round(w_sorted / scale + zero_point)

步骤 5: 反量化
    - w_dq = (w_q - zero_point) * scale

步骤 6: 逆 HAP
    - 对每组应用逆置换
    - 结果: W_restored

输出: 量化后的权重 W_restored（保留在旋转空间中，推理时需旋转输入）
```

## 审查结论与验证结果

> 2026-08-01 复审记录：已重新核查 arXiv、修正真实模型量化 forward 路径，并重新运行合成权重与 mock 模型验证。真实 Qwen3-0.6B 加载仍在权重加载阶段触发退出码 139（Segmentation fault），未能完成端到端真实模型验证。

### 算法一致性

| 检查项 | 结论 | 说明 |
|--------|------|------|
| 论文 ID 匹配 | ❌ 不一致 | arXiv 2607.27536 实际为博弈论论文，与量化无关 |
| 旋转 + 分组量化 | ⚠️ 部分一致 | 代码实现了合理的 Hadamard 旋转 + 组量化，但无法与任何真实论文对照 |
| HAP（谐波对齐置换）| ⚠️ 近似实现 | 使用组内排序作为 HAP 的近似，可能与原设计不同 |
| 零舍入非对称量化 | ⚠️ 部分一致 | 实现了非对称量化与整数零点舍入，但未能依据真实 GyRot 论文验证缩放因子补偿细节 |
| 整数反量化 | ✅ 一致 | IntegerDequantizer 实现正确 |

### 功能验证

| 验证方式 | 结果 | 说明 |
|----------|------|------|
| 合成权重验证 (`python3 demo.py --synthetic`) | ✅ 通过 | Baseline output MSE 2262.3650；GyRot output MSE 11.2249；改进 201.55x |
| Mock 模型验证 (`python3 mock_validate.py`) | ✅ 通过 | 随机初始化 2 层 mock LM；2 个 q_proj 替换为 `GyRotLinear`；forward、生成、包装层输出路径全部可执行 |
| Qwen3-0.6B 真实模型 (`python3 demo.py --model Qwen/Qwen3-0.6B --max-layers 1`) | ❌ 未跑通 | 权重加载 0% 阶段进程退出码 139（Segmentation fault），未完成真实模型量化与生成 |

### 修复的问题清单

1. **demo.py `inference()` 方法文档**: 添加说明，明确量化后的权重保留在旋转空间中，推理时必须旋转输入。
2. **demo.py `GyRotLinear` 包装层**: 修复真实模型验证路径，避免把旋转空间权重直接交给标准 `F.linear`；现在 q_proj forward 会先旋转输入再做线性计算。
3. **demo.py `demo_real_model()`**: 改为遍历并替换 q_proj 层，支持 `--max-layers` 控制验证规模，默认可量化全部 q_proj 层。
4. **mock_validate.py**: 改为使用 `GyRotLinear` 替换 mock 模型 q_proj，验证量化后模型 forward、生成与包装层输出路径。

## 关键设计决策

1. **Hadamard vs Random Rotation**: 使用 Hadamard 矩阵因为它正交、结构化、计算高效。论文可能使用更复杂的旋转矩阵。

2. **排序作为 HAP 近似**: 由于缺少论文全文，HAP 的实现采用组内排序作为合理近似。实际论文中的 HAP 可能涉及更复杂的排列策略。

3. **尺度补偿**: 零舍入后通过微调缩放因子补偿误差。这是论文中"零舍入非对称量化"的核心思想。

## 依赖

```
torch >= 2.0
numpy
transformers >= 4.40  (仅用于真实模型模式)
```

## 已知限制

1. **论文 ID 错误**: 本复现代码对应的 GyRot 论文无法通过 arXiv 2607.27536 验证，可能使用了错误的论文 ID。
2. **论文全文未获取**: 本实现基于摘要和标题推断，部分细节（如 HAP 的确切置换策略、硬件架构细节）可能与原论文不同。
3. **INT4 存储**: demo 中量化值以 float 存储以方便验证，实际部署应使用真正的 INT4/INT8 张量。
4. **激活量化**: 本 demo 仅实现权重量化，论文中的激活量化部分未包含。
5. **评估指标**: 由于缺少完整论文，困惑度、下游任务等端到端评估指标未实现。
6. **部署限制**: 权重保留在旋转空间中，标准 `F.linear` 需要配合输入旋转使用；完整部署需修改模型 forward。
