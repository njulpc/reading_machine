# NAP: Normalization Affine Preconditioning for Neural Network Quantization

## 论文信息
- **标题**: Low-Dimensional High-Leverage Subspace Optimization: Beyond Full-Parameter Coupled Training for Neural Network Quantization
- **arXiv**: 2608.03919
- **作者**: Peng Xia, Junbiao Pang, Zheng Huang
- **发表日期**: 2026-08-04
- **类别**: cs.CV
- **URL**: https://arxiv.org/abs/2608.03919

## 问题背景

低比特量化在紧凑网络上精度严重下降, 根源在于主流的**全参数耦合训练范式**忽略了参数子空间异质性。紧凑网络的特征冗余有限, 难以吸收量化误差。

传统流水线的问题:
- **PTQ**: 重建固定的预训练模型, 不提升内在的量化友好性
- **QAT**: 联合更新所有参数, 骨干权重和校准参数之间的梯度耦合导致性能瓶颈

## 方法概述

### 核心发现
识别**归一化仿射参数 (normalization affine parameters)** 为主导量化鲁棒性的**低维高杠杆子空间 (low-dimensional high-leverage subspace)**:
- **低维**: 参数量远少于骨干权重 (通常 <1%)
- **高杠杆**: 微小调整可大幅影响量化鲁棒性

### NAP-PTQ (后训练量化)
1. 冻结骨干权重 (backbone weights)
2. 仅微调归一化层的仿射参数 (LayerNorm/RMSNorm 的 gamma/beta)
3. 在目标 fake-quantization 图上, 用全精度模型作为 teacher 进行优化
4. 主动提升量化友好性 (proactively boost quantization friendliness)
5. 之后再执行下游重建 (reconstruction)

### NAP-QAT (量化感知训练)
交替 QAT-NAP schema, 解耦特征学习和数值校准:
- **QAT 阶段**: 全参数联合训练, 学习量化友好的特征表示
- **NAP 阶段**: 冻结骨干, 仅微调仿射参数, 校准量化误差
- 交替执行, 打破饱和的全参数联合训练的性能上限

### 理论分析
- BN 仿射参数**完全抵消**量化畸变的通道级仿射分量
- 非线性舍入和截断残差构成不可约误差边界
- 蒸馏引导的 NAP 充当**方向性平坦度优化 (directional flatness optimization)**, 将 teacher-student logit 不匹配投影到受限子空间

### 论文结果
- 在 ImageNet 和 CIFAR-100 上, NAP 恢复了严重崩溃的低比特量化
- 持续提升基于重建的 PTQ
- 以可忽略的微调成本超越饱和的全参数 QAT

## 代码使用说明

### 运行
```bash
cd scripts/quantization/2608.03919
python3 demo.py
```

### 核心组件
- `FakeQuantize`: Fake quantization 模块, 前向模拟量化, 反向用 STE 传梯度
- `apply_fake_quantize_to_linear`: 在模型 Linear 层权重上添加 fake quantization
- `identify_norm_affine_params`: 识别归一化仿射参数 (低维高杠杆子空间)
- `NAPPTQ`: NAP-PTQ 核心类
  - `calibrate`: 冻结骨干, 微调仿射参数, 最小化 teacher-student KL 散度
  - `compute_loss`: 蒸馏损失 = KL(logits) + lambda * MSE(hidden)
  - `apply_weight_quantization`: 微调后执行实际权重量化
- `NAPQAT`: NAP-QAT 交替训练
  - `qat_phase`: 全参数联合训练 (特征学习)
  - `nap_phase`: 冻结骨干, 微调仿射参数 (数值校准)
- `direct_ptq`: 直接 PTQ 基线 (无 NAP)
- `evaluate_output_fidelity`: 评估输出保真度 (MSE/cosine/top-1/KL)
- `evaluate_perplexity`: 评估困惑度 (PPL)

### 实验设计
1. **基线**: 全精度模型评估
2. **实验1**: 直接 PTQ (无 NAP) - 基线对比
3. **实验2**: NAP-PTQ (归一化仿射预处理) - 核心方法
4. **实验3**: NAP-QAT 交替训练 (简化版演示)
5. **对比**: 直接 PTQ vs NAP-PTQ 的输出保真度、PPL、量化误差

脚本会自动尝试加载 Qwen3-0.6B; 若无法下载则使用 MockTransformer 保证可运行。

## 依赖项
- Python >= 3.8
- PyTorch >= 1.10
- transformers (用于加载 Qwen3-0.6B, 可选)
- 共享工具包 `quantization_toolkit.py` (上级目录)

## 文件列表
- `demo.py` - NAP-PTQ/NAP-QAT 实现与验证脚本
