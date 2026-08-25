# 2608.23144 复现：Activation-Weighted Seeded Residual Coding

demo 在真实 Qwen3-0.6B `q_proj` 256×256 权重切片上先做 group-64 INT4 RTN，再以确定性 seed 生成 16 个 ±1 basis 候选；用 64 个校准激活的二阶矩加权选择 basis，将每块 coefficient 量化为 signed 4-bit，并比较修复前后 layer-output MSE。

```bash
PYTHONPATH=/private/tmp/arxiv_pydeps python3 demo.py --checkpoint /path/to/model.safetensors
```

本次验证成功加载官方权重、完成 INT4 + seeded sidecar 路径并通过有限值断言。首层 256×256 切片的 layer-output MSE 从 **0.003483492183** 降到 **0.003409918863**，小规模 gap closed = **2.112%**；256 个 block 的保守 sidecar 估算为 **0.156250 bit/weight**。校准激活为固定随机小样本，basis/编码也做了小规模化，因此不声称复现论文 Qwen2.5-3B 的 88.2% PPL gap、49.25 MB sidecar 或端到端任务准确率。
