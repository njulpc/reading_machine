# 2608.24207 PRQ-KMeans 复现

在 Qwen3-0.6B 真实 token embedding 上验证 [PRQ-KMeans（arXiv:2608.24207）](https://arxiv.org/abs/2608.24207) Algorithm 1：先 L2 normalize，再投影移除全局均值并 normalize；逐级从当前 residual 随机采样码本，以 Top-k cosine/`exp(βs)` 软权重更新，硬分配后移除选中 centroid 投影并再次 normalize；最后冻结 mean/codebook，独立编码并逐项核对 SID。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-27）

- 算法一致性：**部分一致**。Algorithm 1 的几何与拟合/编码双路径已对齐；默认 512 个 Qwen embedding、3 层 K=16 是结构兼容验证，不是论文工业/公开推荐数据的码本规模、层数和下游 generative retrieval 训练。
- 修复：原代码直接减去未归一化 embedding 的算术均值、用等距行初始化 centroid，并漏掉全局均值投影与每级 residual normalization；还没有冻结码本后的独立 encoding 检查。上述问题均已修复，默认改为论文敏感性配置 `top_k=2, β=15`。
- 环境：Python 3.9.6，PyTorch 2.8.0，safetensors 0.7.0；Apple arm64 CPU，CUDA/MPS 不可用。
- 结果：退出码 0，墙钟 0.62 s；两级 projection carry 为 `1.125e-08/4.245e-09`，512 个样本得到 405 个不同 12-bit SID，拟合期与冻结编码期 SID 逐项相等。
- **真实 Qwen3-0.6B：未跑通量化**。本方法是推荐/检索语义 ID tokenizer，不量化 LLM 权重、激活或 KV；这里只使用了真实 Qwen embedding 验证算法几何，不能宣称完成 Qwen 模型量化或论文 HitRate/MRR 复现。
