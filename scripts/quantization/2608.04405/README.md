# BinaryPC: Training-Free Hashing-Based Attention via Binary Principal Components

## 论文信息
- **标题**: Training-Free Hashing-Based Attention via Binary Principal Components
- **arXiv**: 2608.04405
- **方法**: BinaryPC

## 方法概述

BinaryPC 是一种无需训练 (training-free)、数据感知 (data-aware) 的二值哈希方法, 用于加速大语言模型的注意力计算。其核心思想是利用二值主成分分析 (binary PCA) 将 K 向量压缩为紧凑的二值哈希码, 再通过 Hamming 距离进行近似最近邻搜索, 仅对 top-k 最近的 KV 对计算精确注意力, 从而大幅减少 KV cache 的计算开销。

### 核心步骤

1. **提取 K/V 投影**: 从模型注意力层获取 K 向量作为校准数据。
2. **PCA 主成分学习**: 对校准 K 向量进行 PCA, 取前 n_bits 个主成分方向作为二值哈希的投影基。这一步是 data-aware 的 (投影方向由数据方差决定), 但无需梯度训练 (training-free)。
3. **二值量化**: `hash_code = sign((K - mean) @ principal_components)`, 每个 PCA 投影方向产生 1 bit, 将浮点 K 向量压缩为 n_bits 位二值码。
4. **Hamming 距离近邻搜索**: 用二值码间的 Hamming 距离 (XOR + popcount) 近似真实注意力分数的排序, 为每个 query 快速找到 top-k 最近的 key。相比浮点点积 O(d), Hamming 距离仅需 O(n_bits/64) 的位运算。
5. **稀疏注意力**: 仅在选中的 top-k 个 KV 对上计算精确缩放点积注意力, 计算量从 O(seq^2 * d) 降至 O(seq * top_k * d)。

### 关键特性
- **无需训练**: PCA 主成分直接从校准数据计算, 无需任何梯度优化
- **数据感知**: 投影方向由数据方差决定, 比随机投影 (如 LSH) 更准确
- **高效搜索**: 二值 Hamming 距离用位运算实现, 远快于浮点点积
- **精度保持**: top-k 稀疏注意力保留关键信息, 精度接近全注意力

### 论文报告结果
- 相比 FlashAttention 实现 **3.56x 解码吞吐量提升**
- 在多个基准任务上精度保持 (接近全注意力)

## 文件列表
- `demo.py` - BinaryPC 完整实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.04405
python3 demo.py
```

脚本会自动尝试加载 Qwen3-0.6B 模型; 若无法下载则使用 MockTransformer 保证可运行。运行后输出:
- 全注意力 vs BinaryPC 稀疏注意力的输出 MSE 与余弦相似度
- 稀疏比例与理论计算量减少
- Hamming 距离与真实注意力分数的 Spearman 排序相关性 (哈希质量评估)
