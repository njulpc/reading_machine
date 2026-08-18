# 2608.15475 Qwen3-0.6B 复现

`demo.py` 对 Qwen3-0.6B 第一层 `q_proj` 做 per-row symmetric INT8，使用量化重建损失的梯度估计每个 two's-complement bit 的影响，再执行全局 top-k 位翻转。它复现“梯度选位远强于随机翻转”的核心机制；没有 VLA 动作头、Rowhammer 实机和闭环机器人环境，不能复现论文成功率。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --flips 5
```

依赖：Python 3.9+、PyTorch、safetensors。默认切片 64×256 以便 CPU 验证；量化粒度为每输出通道，校准为 32 个固定随机激活样本，seed=7。

**2026-08-19 实测**：本地缓存权重离线运行；INT8 MSE `1.6825e-05`，5 个梯度选位翻转后 MSE `0.0130787`；语法检查通过。
