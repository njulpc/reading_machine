# 2608.15531 FlashQuant Qwen3-0.6B 复现

脚本把真实 Qwen3-0.6B `up_proj` 分成 W4 dense 路径和 FP32（概念上对应 FP16）稀疏异常值路径，并验证两条路径在同一输出上的数值融合。异常值阈值默认为每行平均绝对值的 6 倍，W4 为 per-row symmetric。论文贡献中的 Tile-COO、shared-memory 复用和 CUDA pipeline 需要专用 kernel，本 CPU demo 不伪造速度。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --outlier-threshold 6
```

依赖 PyTorch、safetensors；固定 128×512 权重切片、16 个校准输入。

**2026-08-19 实测**：异常值密度 `0.000381`，W4+稀疏路径 MSE `0.00732583`，融合等价断言与语法检查通过。
