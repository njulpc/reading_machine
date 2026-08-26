# 2608.24207 PRQ-KMeans 复现

取 Qwen3-0.6B 真实 token embedding 的前 512 行，先去全局均值，再顺序训练 3 个 K=16 码本；centroid 用 Top-3、温度 0.07 的软权重更新，每层以所选 centroid 的投影而非完整码字构造残差。脚本验证下一层残差对上一 centroid 近似正交，并报告 12-bit 语义 ID 的实际唯一组合数。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

论文目标是推荐/检索 SID；Qwen embedding 仅用于验证算法几何，不声称复现工业 HitRate/MRR 或完整 tokenizer 训练。

实测：三层投影残差对上一 centroid 的平均绝对内积依次为 `7.543e-09/2.056e-09/1.390e-09`，512 个样本形成 399 个不同的 12-bit SID。
