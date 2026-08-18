# 2608.15602 FluxBin Qwen3-0.6B 复现

真实 Qwen3-0.6B `down_proj` 权重先做 row binary basis，再对残差做 column binary basis；用校准激活二阶矩作为 Hessian 对角代理，保留默认 5% 显著残差。主二值基使用每 8 个输入值构建 256 项查找表并按权重 bit pattern 索引，脚本断言 LUT 与直接乘法数值一致。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --salient-fraction 0.05
```

未实现论文 CUDA 的 virtual column mapping、scale fusion 和能耗测量；这里复现算法-数据布局核心，绝不把 Python LUT 延迟当论文速度。

**2026-08-19 实测**：显著残差比例 `0.049988`，输出 MSE `0.0126608`，group-8 LUT 数值等价断言与语法检查通过。
