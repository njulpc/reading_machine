# 2608.15636 SpecVLA mixed-precision Qwen3-0.6B 复现

脚本将 Qwen3-0.6B `o_proj` 的 256×256 真实权重切成 64×64 block。用 32 个校准激活估计每个 block 的 4-bit differential residual 对输出的贡献，将最高 25% block 升为 8-bit，其余保持 4-bit，并报告平均 bit 数与全 4-bit 输出 MSE 对比。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --block 64 --eight-bit-fraction 0.25
```

这复现 block-wise residual mixed precision；Qwen 没有 VLA 动作头，故不声称复现 sVLA、状态分类、GPU/机器人异构 dataflow 或闭环成功率。

**2026-08-19 实测**：全 4-bit 输出 MSE `0.00608043`；25% block 升 8-bit 后平均 5.0 bit、MSE `0.00333172`；语法检查通过。
