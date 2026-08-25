# 2608.22378 复现：Variable-bit approximate PE

demo 从真实 Qwen3-0.6B `q_proj` 取 256×256 子矩阵，模拟 FP32/TF32/BF16 mantissa 与更激进的 partial-product 列截断，比较矩阵乘输出的 relative RMSE 和 cosine。

```bash
PYTHONPATH=/private/tmp/arxiv_pydeps python3 demo.py --checkpoint /path/to/model.safetensors
```

本次验证成功加载官方权重并完成三种格式的软件数值扫描与有限值断言。nominal→approx relative RMSE 分别为 FP32 **0→0.00000657**、TF32 **0.00041324→0.00166469**、BF16 **0.00332509→0.02166984**；最激进 BF16 路径 cosine 仍为 **0.99995315**。这里没有论文的 RTL、正/负 compressor、NSGA-II 综合和 FPGA/ASIC 工具，因而不能声称复现 66%–92% 面积或 60%–93% 功耗收益。
