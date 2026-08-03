# LightRot: 分组局部旋转量化方案

> **论文**: LightRot: A Light-Weighted Rotation Scheme and Architecture for Accurate Low-Bit Large Language Model Inference
> **arXiv**: 2607.27704

## 核心方法

### 1. 分组局部旋转 (GLR, Grouped Local Rotation)

将通道划分为局部组（如 `group_size=128`），在组内独立执行 Hadamard 旋转而非全局旋转。
- 全局旋转复杂度: O(N^2)
- 分组旋转复杂度: O(g^2)（g 为组大小）
- 牺牲少量全局异常值分散能力，大幅降低在线旋转计算量

### 2. 异常值方向对齐 (ODA, Outlier Direction Aligning)

将异常值通道排列到 Hadamard 矩阵的全 1 行（all-ones row）对应位置。
- Hadamard 矩阵的全 1 行与输入向量的乘积 = 所有元素之和
- 异常值经旋转后被均匀分散到组内所有通道
- 仅需离线计算一次排列矩阵

### 3. 分层快速 Hadamard 变换 (FHT)

利用 Hadamard 矩阵的 Sylvester 递归结构，将非 2 的幂次维度分解为多个 2 的幂次子块。
- 每个子块独立使用 FHT（复杂度 O(N log_2 N)）
- 支持任意维度的在线旋转

### 4. 4-bit 对称量化

```
x_hat = clip(round(x / s), qmin, qmax)
s = max(|x_group|) / (2^(b-1) - 1)
```

### 5. 旋转矩阵的在线/离线划分

- R1/R2：离线与权重预合并，不增加运行时开销
- R3/R4：在线执行，Hadamard 矩阵仅含 +/-1，只需加法运算

## 运行方式

```bash
cd scripts/quantization/2607.27704
python3 demo.py
```

自动尝试加载 Qwen3-0.6B，若不可用则使用 MockTransformer（随机初始化的小型 Transformer）。

## 输出说明

- FHT 与矩阵乘法一致性验证
- 各线性层在无旋转 / GLR / GLR+ODA 三种方案下的 4-bit 量化误差对比
- 汇总统计（平均 MSE、改善百分比）
