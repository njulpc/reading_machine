# GyRot: 2607.27536 复现代码

## 论文信息
- **arXiv ID**: 2607.27536
- **标题**: GyRot: Leveraging Hidden Synergy between Rotation and Fine-grained Group Quantization for Low-bit LLM Inference
- **作者**: Sangjin Kim, Yuseon Choi, Byeongcheol Kim, Jungjun Oh, Hoi-jun Yoo

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

对 Qwen3-0.6B 模型的 q_proj 层执行 GyRot 量化，并生成文本验证效果。

**注意**: 如果无法下载模型权重（网络限制或权限问题），请使用 `--synthetic` 模式验证算法逻辑。代码中的算法实现不依赖特定模型权重。

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

输出: 量化后的权重 W_restored
```

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

1. **论文全文未获取**: 本实现基于论文摘要和标题推断，部分细节（如 HAP 的确切置换策略、硬件架构细节）可能与原论文不同。
2. **INT4 存储**: demo 中量化值以 float 存储以方便验证，实际部署应使用真正的 INT4/INT8 张量。
3. **激活量化**: 本 demo 仅实现权重量化，论文中的激活量化部分未包含。
4. **评估指标**: 由于缺少完整论文，困惑度、下游任务等端到端评估指标未实现。
