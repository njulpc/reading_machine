# AnchorKV: Anchor-Residual KV Cache Compression

## 论文信息
- **标题**: AnchorKV: Anchor-Residual KV Cache Compression
- **arXiv**: 2608.02901
- **作者**: Malik Khalaf, Yara Shamshoum, Nitzan Hodos, Yuval Sieradzki, Assaf Schuster
- **发表日期**: 2026-08-03
- **类别**: cs.LG, cs.CL
- **URL**: https://arxiv.org/abs/2608.02901

## 问题背景

KV cache 是长上下文 LLM 推理的主要内存瓶颈，其大小随序列长度线性增长。已有压缩方法存在两类缺陷：

- **驱逐方法 (Eviction)**：永久丢弃 token，一旦被丢弃的 token 后续被需要则性能不可逆下降。
- **量化方法 (Quantization)**：保留所有 token 但以低精度存储，单靠量化压缩比有限（通常 8x 以内）。

## 方法概述

AnchorKV 提出一种 **不丢弃任何 token 即可实现约 20x 压缩** 的方案，核心包含三个机制：

### 1. 锚点选择 (Anchor Selection)
选取少量 anchor token，以全精度 (FP16) 精确存储其 K/V。anchor 的选取基于 token 重要性（注意力分数的累积作为重要性信号）。

### 2. 残差表示 (Residual Representation)
每个 non-anchor token 通过其最近 anchor 的残差表示：
```
residual_i = token_i - anchor_{nearest(i)}
```
残差幅度通常远小于原值，因此可用极低比特（如 2-bit）量化残差而几乎不损失精度。这样每个 token 都被保留（不丢弃），只是精度不同。

### 3. 精化 (Refinement)
只精化那些近似误差对模型输出影响最大的 token。影响度由 attention score 与残差幅度综合衡量，被选中的 token 提升到全精度。这样在固定预算下最大化输出保真度。

### 压缩比分析
设序列长度 N、KV 维度 d、anchor 比例 a、精化比例 r、残差比特 b_r：
- 全精度：`N * d * 2字节 * 2(K,V)`
- AnchorKV：`a*N (FP16) + (1-a-r)*N (b_r-bit残差) + r*N (FP16精化) + 索引开销`

通过调节 a、r、b_r 可达到 20x 压缩。论文在 70B 规模保留 99% 全缓存分数。

## 代码使用说明

### 运行
```bash
cd scripts/quantization/2608.02901
python3 demo.py
```

### 核心组件
- `AnchorKVCompressor`：主压缩器，参数包括 anchor_ratio、refine_ratio、residual_bits
- `lowbit_quantize`：group-wise 对称低比特量化（用于残差）
- `extract_kv_cache`：从 Qwen3-0.6B 提取真实 K/V cache（失败则用 Mock）
- `attention_output_mse`：评估重构 K/V 的注意力输出保真度

### 对比基线
- **Uniform-2bit**：所有 token 统一 2-bit 量化（同等压缩比的简单量化）
- **Eviction-15%**：保留 15% token，其余丢弃（驱逐方法）

脚本会自动尝试加载 Qwen3-0.6B；若无法下载则使用 MockTransformer 保证可运行。运行后输出压缩比分析、逐层 K/V 量化误差、注意力输出 MSE 与余弦相似度对比。

## 依赖项
- Python >= 3.8
- PyTorch >= 1.10
- transformers (用于加载 Qwen3-0.6B，可选)
- 共享工具包 `quantization_toolkit.py`（上级目录）

## 文件列表
- `demo.py` - AnchorKV 完整实现与验证脚本
