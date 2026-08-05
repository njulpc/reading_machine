# SparseKAN: Compressing KANs Across Basis Functions, Neurons, and Bits

## 论文信息
- **标题**: SparseKAN: Compressing Kolmogorov-Arnold Networks Across Basis Functions, Neurons, and Bits
- **arXiv**: 2608.00859
- **作者**: Kazi Ahmed Asif Fuad, Lizhong Chen
- **代码**: https://github.com/OSU-STARLAB/SparseKAN

## 方法概述

SparseKAN 沿三个互补的轴压缩 Kolmogorov-Arnold Networks (KAN)：

1. **基函数门控剪枝**：为每个基函数项配备可学习门控 g_k (sigmoid 参数化)，低门控值的基函数在训练后被剪枝。
2. **神经元/通道剪枝**：为每个输出神经元配备可学习门控 h_j，低门控值的神经元被剪枝并物理压缩为更小的密集张量。
3. **数值精度量化**：对系数进行量化感知训练 (QAT)，支持 INT8 和 4-bit，前向使用 Fake Quantization (STE)。
4. **可微主动代价目标**：L = L_task + λ_basis × Σ(gates) + λ_neuron × Σ(gates)，鼓励稀疏性。
5. **硬剪枝与物理压缩**：训练后门控阈值化，移除剪枝项，压缩为更小的密集张量。

## 文件列表
- `demo.py` - SparseKAN 三轴压缩完整实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.00859
python3 demo.py
```

脚本包含两部分：
- Part A：独立 KAN 网络的函数逼近任务，展示完整的三轴压缩流程（门控学习 → INT8 QAT → 4-bit QAT → 硬剪枝）。
- Part B：将 Qwen3-0.6B 的 Linear 层转换为 KAN 边函数，应用三轴压缩并统计参数压缩率。
