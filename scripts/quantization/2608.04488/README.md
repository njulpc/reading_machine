# Energy- and Memory-Efficient PEFT Methods for Personalized On-Device SLMs

## 论文信息
- **标题**: Energy- and Memory-Efficient PEFT Methods for Personalized On-Device SLMs
- **arXiv**: 2608.04488
- **关键词**: PEFT, LoRA, LoRA+, QLoRA, BitFit, NF4, On-Device SLM, Parameter-Efficient Fine-Tuning

## 方法概述

本文系统比较了五种参数高效微调 (PEFT) 方法在端侧小语言模型 (SLM) 上的能效与显存表现，
并提出了综合指标 NetScore-E 来权衡精度、显存和能耗。五种方法包括：

1. **Full Fine-Tuning (Full FT)**：全参数微调，所有权重均可训练。精度最高但显存和能耗
   开销最大，不适合端侧部署。

2. **BitFit**：仅微调偏置 (bias) 参数，其余参数冻结。可训练参数极少，但表达能力有限。

3. **LoRA (Low-Rank Adaptation)**：冻结原始权重 W，引入低秩增量 ΔW = (α/r)·B·A，
   其中 A∈R^{r×d_in}，B∈R^{d_out×r}，r 远小于 d。A 用 Kaiming 初始化，B 初始化为零，
   保证训练开始时 ΔW=0。

4. **LoRA+**：在 LoRA 基础上，为 A 和 B 矩阵设置不同的学习率。核心观察：A 和 B 在梯度
   更新中扮演不对称角色（B 的梯度依赖于 A 的当前值），统一学习率导致 A 和 B 的有效学习
   速度不匹配。LoRA+ 使用 lr_A = η, lr_B = η × ratio (ratio > 1)，B 矩阵使用更高学习率
   以加速收敛，显著提升训练质量。

5. **QLoRA (Quantized LoRA)**：将基础模型权重量化为 4-bit NF4 (NormalFloat4) 格式，
   在量化后的冻结权重上叠加 LoRA 适配器。NF4 基于正态分布的分位点设计 16 个量化级别，
   对预训练权重的分布天然适配。QLoRA 将 VRAM 消耗降低 3.9x，同时保持接近全精度的微调效果。

## 关键结果
- **QLoRA**: VRAM 降低 3.9x，是端侧部署的最佳能效选择
- **LoRA+**: 在 24 种配置中的 19 种取得最佳 NetScore-E，精度-能效权衡最优
- **NetScore-E**: 综合精度提升、显存节省和能耗降低的统一评估指标

## 文件列表
- `demo.py` - 五种 PEFT 方法实现与对比验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.04488
python3 demo.py
```

脚本会自动尝试加载 Qwen3-0.6B 模型；若无法下载则使用 Mock Transformer 保证可运行。
运行后输出各方法的可训练参数量、显存占用估计、量化误差及 LoRA+ 差异化学习率效果对比。
