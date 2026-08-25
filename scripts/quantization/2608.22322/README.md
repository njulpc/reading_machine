# 2608.22322 复现：Adaptive Log-Space optimizer state

该 demo 在真实 Qwen3-0.6B `q_proj` 权重上构造 Adam 风格一阶动量与非负二阶矩，复现论文的三个关键点：按块自适应 log range、零值独立码点、非负状态与带符号动量分开选精度。

```bash
PYTHONPATH=/private/tmp/arxiv_pydeps python3 demo.py --checkpoint /path/to/Qwen3-0.6B/model.safetensors
```

本次验证：官方 checkpoint 成功加载，扫描首层 `q_proj` 的 524,288 个真实权重元素。AL8 二阶矩 relative RMSE = **0.01544387**，精确零保留；INT8 momentum relative RMSE = **0.00725156**。计入每块两个 FP32 log 边界后，两个 FP32 状态从 4,194,304 B 估算降到 1,064,960 B，即 **3.938×**。它验证编码路径，不复现论文 20K/100K-step 训练、72.90 PPL 或 fused optimizer kernel。

依赖：Python 3、PyTorch、safetensors。可通过 `--checkpoint` 显式指定权重。
