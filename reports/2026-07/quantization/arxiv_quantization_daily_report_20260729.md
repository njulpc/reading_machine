# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-07-29 00:00–23:59 UTC
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, sparsity
**数据来源**: arXiv.org

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2607.26515 | HiFloat4 Format for End-To-End RL Post-Training of LLMs | Hei Yi Mak 等 | 07-29 | FP4、Quantization、RL、HiFloat4 | cs.LG |
| 2 | 2607.27042 | GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding | Jiale Chen 等 | 07-29 | GPTQ、Adaptive Rounding、Two-Sided、Quantization | cs.DS |
| 3 | 2607.27054 | CoCaRS: Correlation Calibration-Based Redundancy Suppression for Heterogeneous KD | Fengming Yu 等 | 07-29 | Knowledge Distillation、Heterogeneous、Redundancy Suppression | cs.CV |
| 4 | 2607.27031 | Lottery Tickets Are Not Deployment Tickets | Bum Jun Kim | 07-29 | Lottery Ticket、Sparsity、Deployment、Behavioral Compatibility | cs.LG |
| 5 | 2607.26835 | A Low-Power Sparse Convolution Accelerator with IFTA for Edge Vision | Jingyue Zhuge 等 | 07-29 | Sparse Accelerator、Edge Vision、Low Power、FPGA | cs.AR |
| 6 | 2607.26648 | The Sparsity Ceiling: Where Spiking Networks Can and Cannot Trade Activity for Energy | Zeyu Wang | 07-29 | Sparsity、SNN、Energy Efficiency、Firing Floor | cs.NE |
| 7 | 2607.26763 | Long-Tailed 3D Point Cloud Dataset Distillation | Jiahao You 等 | 07-29 | Dataset Distillation、3D Point Cloud、Long-Tailed | cs.CV |
| 8 | 2607.27113 | Veritas++: Value-aware On-Policy Distillation for Perception-Enhanced AIGI Detection | Hao Tan 等 | 07-29 | Distillation、AIGI Detection、Perception、MLLM | cs.CV |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 2篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| HiFloat4 (2607.26515) | FP4 Hierarchical Scaling | Qwen2.5 (RL post-training) | 三级层次化缩放 + Rollout-ResQ，端到端FP4 RL训练 |
| GPTQ-2D (2607.27042) | INT4/Adaptive Rounding | 通用权重矩阵 | 双边自适应舍入，反斜对角线并行，O(m³)复杂度 |

### 2.2 剪枝/稀疏 (Pruning/Sparsity) — 3篇

| 论文 | 稀疏类型 | 目标 | 核心贡献 |
|------|---------|------|---------|
| Lottery Tickets (2607.27031) | 结构性/非结构性剪枝 | 图像分类 | 清洁精度恢复≠部署兼容性，7-10%决策变化 |
| Sparse Accelerator (2607.26835) | 稀疏卷积加速器 | 边缘视觉 | 16nm芯片，0.5mm²，12-16mW，6.5×加速 |
| Sparsity Ceiling (2607.26648) | SNN稀疏性分析 | 脉冲神经网络 | 任务决定稀疏上限，前馈5% vs 循环50% firing rate |

### 2.3 知识蒸馏 (Distillation) — 3篇

| 论文 | 蒸馏类型 | 应用场景 |
|------|---------|---------|
| CoCaRS (2607.27054) | 异构特征蒸馏 | 图像分类 |
| Dataset Distillation (2607.26763) | 数据集蒸馏 | 3D点云 |
| Veritas++ (2607.27113) | On-Policy Distillation | AIGI检测 |

---

## 三、量化论文详细评分

| arXiv ID | 论文标题 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 总分 |
|---------|---------|:-------:|:-------:|:-----:|:-------:|:----:|
| 2607.26515 | HiFloat4 Format for End-To-End RL Post-Training | 8 | 8 | 9 | 7 | **32** |
| 2607.27042 | GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding | 7 | 7 | 9 | 8 | **31** |

### 评分说明

**2607.26515 - HiFloat4**
- **精度效果 (8/10)**: BF16差距从4.9%缩小至1.1%（HiF4+Rollout-ResQ），MXFP4下从13.6%缩小至5.3%
- **压缩倍率 (8/10)**: FP4实现约4×权重压缩，但需配合稀疏残差
- **创新性 (9/10)**: 首次端到端FP4 RL训练，三级层次化缩放格式，Rollout-ResQ机制
- **可复现性 (7/10)**: 核心算法可复现，但HiF4格式需华为自研硬件支持

**2607.27042 - GPTQ-2D**
- **精度效果 (7/10)**: 理论优雅，与naive quartic等价，但实际量化效果取决于Hessian近似质量
- **压缩倍率 (7/10)**: 标准4-bit权重量化，4×压缩
- **创新性 (9/10)**: Kronecker结构中的反斜对角线并行化，复杂度从四次降至三次
- **可复现性 (8/10)**: 算法清晰，纯PyTorch可实现，无特殊硬件依赖

---

## 四、值得关注的高亮点

1. **FP4 RL 训练突破**: [2607.26515] 首次实现端到端FP4精度的RL后训练，发现rollout-training mismatch是主要失效模式，提出Rollout-ResQ稀疏残差修正。

2. **复杂度优化**: [2607.27042] 将双边自适应舍入从四次复杂度降至三次，利用Kronecker积的反斜对角线结构实现并行化。

3. **部署兼容性警示**: [2607.27031] 彩票假说模型即使精度恢复，在实际部署中仍导致7-10%的决策变化，挑战了clean-accuracy-as-proxy的假设。

4. **稀疏上限理论**: [2607.26648] 形式化SNN firing rate的信息论下界，证明能量收益是任务属性而非SNN本身属性。

---

## 五、复现代码位置

| 论文 | 代码位置 |
|------|---------|
| 2607.26515 HiFloat4 | `scripts/quantization/2607.26515/` (README.md + demo.py) |
| 2607.27042 GPTQ-2D | `scripts/quantization/2607.27042/` (README.md + demo.py) |

---

*报告生成时间: 2026-07-30 10:46 GMT+8*
