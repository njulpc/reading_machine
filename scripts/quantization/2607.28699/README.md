# WitCert: KV-Cache 量化的运行时风险观测与门控

> **论文**: WitCert: Sound Runtime Risk Observability and Gating for KV-Cache Quantization
> **arXiv**: 2607.28699

## 核心方法

### 1. Tier A: 确定性带范数见证界

- 残差见证: `r_t = k_hat_t - k_t`（量化 key 与精确 key 之差）
- 将 d/2 个 RoPE 频率对分为 B=16 个连续频带
- 存储每个频带的欧几里得范数: `w_{t,b} = ||r_{t,b}||`
- 见证在写入时计算一次，与 query 无关

### 2. RoPE 带酉性 (Lemma 1)

- RoPE 在每个频率对上表现为 2x2 旋转（角度 n*theta_j）
- 每个频率对完全包含在单个频带内
- 对任意频带 b、任意位置 n: `||(R_n * x)_b|| = ||x_b||`
- post-RoPE 残差的见证 = pre-RoPE 残差的见证（位置不变）

### 3. Theorem 1: Sound Replacement

- `TV(p, p_tilde) <= 0.5 * (A^2 - 1)`
- `A = E_{p_tilde}[e^c]`，c 为注意力 logit
- 当 `|epsilon_t| <= c_t` 对所有 t 成立时

### 4. INT8/FP8 KV-Cache 量化

- 对 KV cache 的 key 进行 INT8 量化
- 计算量化残差和频带范数

### 5. 门控机制

- `tau < 1`: 认证模式（certified），提供数学保证
- `tau >= 1`: 风险排序模式（risk-ranked），度量值仍具经验判别力

### 6. 减法抖动量化 (Subtractive Dither)

- `Q(x) = x - d`，d 为抖动噪声
- 使量化误差均匀且无偏

## 运行方式

```bash
cd scripts/quantization/2607.28699
python3 demo.py
```

## 输出说明

- RoPE 带酉性验证
- INT8 KV-cache 量化残差与频带范数计算
- TV 上界计算与验证 (Theorem 1)
- 门控机制演示（certified vs risk-ranked）
- 减法抖动量化对比
