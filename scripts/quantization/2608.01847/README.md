# FOCUS: FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling

## 论文信息
- **标题**: FOCUS: FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling
- **arXiv**: 2608.01847
- **作者**: Xianglong Yan, Hong Liu, Chengzhu Bao, Tianao Zhang, Guanghua Yu, Jianchen Zhu, Yulun Zhang
- **代码**: https://github.com/tencent/AngelSlim

## 方法概述

FOCUS 是面向 FP4 精度的训练后量化 (PTQ) 框架，通过端到端尺度学习优化 FP4 量化精度。核心包含两个组件：

1. **CRS (Coupled-Relaxation Scaling / 耦合松弛缩放)**：松弛量化尺度与反量化尺度的紧耦合关系。引入可学习全精度系数 alpha，使得 `s_quant = s_dequant * alpha`。反量化尺度遵守硬件格式 (E8M0/E4M3)，而量化尺度可为全精度，释放优化空间且不增加推理开销。

2. **DGS (Dual-Granularity Scaling / 双粒度缩放)**：在更细的子块粒度 (sub-block) 上优化量化尺度因子 beta，使量化尺度更精确地适应局部权重分布，同时反量化尺度保持在块级别。

支持两种 FP4 格式：
- **MXFP4**: 块大小 32，尺度为 E8M0 (2 的幂)
- **NVFP4**: 块大小 16，尺度为 E4M3 (8 位浮点)

## 文件列表
- `demo.py` - FOCUS 量化完整实现与验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.01847
python3 demo.py
```

脚本会自动尝试加载 Qwen3-0.6B 模型；若无法下载则使用 Mock Transformer 保证可运行。运行后输出量化前后权重误差和模型输出误差对比，展示 CRS+DGS 相比基线 FP4 的改善。
