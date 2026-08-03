# GyRot: 旋转与细粒度分组量化的协同框架

> **论文**: GyRot: Leveraging Hidden Synergy between Rotation and Fine-grained Group Quantization for Low-bit LLM Inference
> **arXiv**: 2607.27694

## 核心方法

### 1. CoRFiG (Coarse Rotation, Fine Grouping)

旋转在比量化组（32 通道）更大的范围（如 128）进行：
- 旋转范围 G_rot (128) > 量化组大小 G_quant (32)
- 异常值在组间尺度上分散，组内局部方差保持一致
- 解决了旋转（全局操作）与细粒度分组量化（局部操作）的尺度冲突

### 2. HAP (Harmonic-Aligned Permutation)

将异常值通道映射到 Hadamard 矩阵的谐波行：
- Hadamard 矩阵的谐波行具有特定的频率结构
- 异常值经旋转后均匀分散到量化组内所有通道
- 比 LightRot 的 ODA（仅用全 1 行）更通用，利用完整谐波谱

### 3. 非对称量化重构

```
x_hat = clip(round(x/s) + z, qmin, qmax)
s = (max(x_group) - min(x_group)) / (2^b - 1)
z = round(-min(x_group) / s)
```

### 4. 零点舍入策略

- 零点 z 四舍五入到整数，消除截断误差
- 实现全整数反量化，无需浮点运算

### 5. 内积重构

```
y ≈ Σ_g s_x^(g) · s_w^(g) · Σ_i (x_hat_i - z_x^(g)) · w_hat_i
```

### 6. INT4 细粒度分组量化

- 量化组大小: 32 通道
- 旋转组大小: 128 通道（CoRFiG）

## 运行方式

```bash
cd scripts/quantization/2607.27694
python3 demo.py
```

## 输出说明

- 各线性层在四种方案下的 INT4 量化误差对比:
  - 无旋转（基线）
  - 朴素旋转（旋转组=量化组=32，展示冲突）
  - CoRFiG 旋转（旋转组=128 > 量化组=32）
  - CoRFiG + HAP（完整方案）
- 零点舍入策略验证
- 全整数内积重构演示
