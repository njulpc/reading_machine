# 论文复现: GQ-FSL: Green Quantized Federated Split Learning

**arXiv**: 2607.29659

## 论文概述

将随机量化集成到联邦分割学习 (FSL) 的本地训练和无线传输中，支持客户端/服务器非对称精度，通过联合优化分割点和精度级别最小化系统总能耗。

## 核心方法

### 1. 随机量化 (无偏)

```
量化分辨率: κ = 2^{-(q-1)}, 动态范围: [-1, 1-κ]

Q(w) = floor(w)          (概率 (floor(w)+κ-w)/κ)
     = floor(w)+κ        (概率 (w-floor(w))/κ)

无偏性: E[Q(w)] = w
有界方差: E[(Q_i(w_i)-w_i)²] ≤ 1/2^{2q_i}
```

### 2. 非对称精度

- 客户端 q_c 比特，服务器 q_s 比特，q_c ≠ q_s
- 资源受限客户端用低精度，强大服务器用高精度

### 3. 量化误差界 (论文公式3)

```
E[||Q(w)-w||²] ≤ d_c/2^{2q_c} + d_s/2^{2q_s}
```

### 4. 联邦分割学习 (FSL)

- 模型分割为客户端子模型和服务器子模型
- 切层处交换量化激活
- FedAvg 聚合: w_{t+1} = Σ_k (n_k/n) * w_k^t

### 5. 能耗模型

```
E = E_compute + E_transmit
```

- 计算能耗与精度级别 q 相关
- 传输能耗与量化后数据大小相关

## 文件说明

- `demo.py`: 完整复现代码，包含：
  - `RandomQuantizationVerifier`: 验证无偏性、有界方差、非对称误差界
  - `SplitModel`: 可分割的 Transformer 模型（客户端 + 服务器两部分）
  - `EnergyModel`: 参数化能耗模型（计算 + 传输）
  - `FederatedSplitLearning`: 联邦分割学习训练器（量化前向 + 全精度反向 + FedAvg）
  - 5 个实验：无偏性验证、方差界验证、非对称误差界验证、FSL 训练模拟、能耗分析

## 运行方式

```bash
cd scripts/quantization/2607.29659
python3 demo.py
```

无需 GPU 和模型下载，默认使用 mock 模型运行。若环境中有 Qwen3-0.6B 权重和 GPU，自动切换到真实模型。

## 输出示例

程序会打印：
1. 随机量化无偏性验证（2/4/8/16 比特）
2. 有界方差验证（经验 MSE vs 理论上界）
3. 非对称精度误差界验证（4 种配置）
4. 联邦分割学习训练模拟（4 种精度配置，5 轮训练）
5. 能耗分析（计算/传输能耗分解）
6. 汇总对比和关键发现

## 共享工具

本 demo 依赖 `scripts/quantization/quantization_toolkit.py` 中的：
- `StochasticQuantizer`: 随机量化器（无偏、有界方差）
