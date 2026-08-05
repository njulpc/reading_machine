# HaTQ: Hadamard-Domain Model Quantization for Learned Image Coding

## 论文信息
- **标题**: Hadamard-Domain Model Quantization for Learned Image Coding
- **arXiv**: 2608.01653
- **作者**: Junqi Shi, Chongzhi Wang, Yiwen He, Ming Lu, Zhan Ma

## 方法概述

HaTQ 在量化前用正交 Hadamard 变换重参数化权重和激活，使其分布更均匀（降低重尾特性），从而提升均匀 INT8 量化的精度。

核心组件：
1. **Hadamard 重参数化**：利用正交 Hadamard 矩阵 H（H@H^T=I, H=H^T）变换权重 W'=W@H 和激活 x'=x@H，变换前后函数映射不变。
2. **两种形式**：
   - Weight-only Hadamard：仅变换权重，激活变换折叠到前一层
   - Double-Hadamard：同时变换权重和激活
3. **敏感层识别**：通过离线 Profiling 计算每层激活的 Hadamard 变换范围放大倍数，敏感层（放大超过阈值）使用 Weight-only Hadamard。
4. **INT8 量化**：对变换后的权重进行均匀 INT8 对称量化，支持 PTQ 和 QAT。

## 文件列表
- `demo.py` - HaTQ 量化完整实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.01653
python3 demo.py
```

脚本自动尝试加载 Qwen3-0.6B；若无法下载则使用 Mock Transformer。运行后输出层敏感度分析、Hadamard 变换前后权重分布变化、以及基线 INT8 vs HaTQ INT8 的量化误差对比。
