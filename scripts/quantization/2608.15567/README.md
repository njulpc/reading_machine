# 2608.15567 SchurQuant Qwen3-0.6B 复现

脚本在 Qwen3-0.6B `q_proj` 的 32×128 真实权重切片上运行 2-bit、group-size=32 的离散优化：由 96 个校准激活形成 Hessian，对未处理后缀求 Schur complement；组内交替重拟合 affine scale/zero-point 和整数码坐标下降。输出与普通 affine 初始化的校准输出 MSE 对比。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --group-size 32
```

这是可运行的 SchurOpt 数值核心，不含论文完整的 quantized-prefix teacher、token weighting 与全模型逐层误差传播；CPU 小切片用于可审计验证。

**2026-08-19 实测**：普通 2-bit affine 输出 MSE `0.0151324`，Schur+坐标下降后 `0.0131029`；语法检查通过。
