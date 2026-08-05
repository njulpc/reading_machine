# DeVIT: Low-Power ViT Acceleration Using Delta Computation

## 论文信息
- **标题**: DeVIT: Low-Power Vision Transformer Acceleration Using Delta Computation
- **arXiv**: 2608.01343
- **作者**: Reyhaneh Hosseinzadeh, Parham Zilouchian Moghaddam, Mehdi Modarressi

## 方法概述

DeVIT 利用量化后权重的值局部性 (value locality)，通过差分计算实现无乘法 (multiplier-less) 矩阵乘法。

核心组件：
1. **低比特权重量化**：将权重量化到 4-bit，量化后权重来自有限值域 {-7, ..., 7}。
2. **值局部性**：量化后相邻位置的权重值往往相同，差分编码 delta[i] = w[i] - w[i-1] 使大部分 delta = 0。
3. **无乘法矩阵乘法**：利用后缀和将 y = sum(x[i]*w[i]) 转化为 y = sum(delta[i]*S[i])，其中 S[i] 是后缀和。零值 delta 跳过，非零 delta 用移位-加法查找表替代乘法。
4. **移位-加法 LUT**：将 delta 分解为 2 的幂次之和（如 5 = 4+1），用移位和加法实现乘法。

## 文件列表
- `demo.py` - DeVIT 差分计算完整实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.01343
python3 demo.py
```

脚本自动尝试加载 Qwen3-0.6B；若无法下载则使用 Mock Transformer。运行后输出值局部性分析、乘法消除率统计、移位-加法查找表示例、以及标准量化 vs DeVIT 差分计算的输出对比。
