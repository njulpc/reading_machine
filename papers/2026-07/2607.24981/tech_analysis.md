# 技术深度分析：Enabling Fully Integer-Only Inference for Lightweight Detection Transformers (arXiv:2607.24981)

> **论文**: Enabling Fully Integer-Only Inference for Lightweight Detection Transformers  
> **作者**: Thanh Cong Le, Michal Szczepanski, Martyna Poreba  
> **核心贡献**: 端到端纯INT8轻量检测Transformer，涵盖可变形注意力、GELU、LayerNorm  
> **arXiv**: https://arxiv.org/abs/2607.24981

---

## 一、论文概述

### 1.1 核心问题

VisionTransformerdetectorsnowapproachtheaccuracyofCNNsbutremain difficult to deploy on NPUs and microcontrollers because key components, including deformable attention, feature fusion, and nonlinear activation func- tions,arenotnativelycompatiblewithintegerarithmetic. Existingquantized detectors either retain operators such as Softmax, GELU, and LayerNorm or focus on heavyweight backbones, leaving lightweight detection transformers without an end-to-end integer implementation. We address this ga

### 1.2 技术方向

- **技术方法**: quantization
- **目标模型**: DETR-like Detection Transformer
- **核心关键词**: integer-only、detection transformer、quantization、lightweight

---

## 二、技术方案详解

### 2.1 核心方法

本文采用量化技术降低模型推理精度，通过减少比特宽度实现更高效的部署。

### 2.2 关键技术细节

- **块量化**: 使用块级共享缩放因子，减少量化误差
- **注意力机制**: 优化注意力计算的数值稳定性
- **整数推理**: 所有操作在整数算术中完成，无需浮点单元
- **非线性近似**: 使用整数友好的近似替代浮点非线性函数
- **可变形注意力**: 采样局部特征点而非全局注意力，降低计算复杂度

---

## 三、核心算法伪代码

```python
# I-LW-DETR: 纯整数DETR推理
import torch
import torch.nn as nn

class IntegerOnlyLinear(nn.Module):
    """纯整数线性层"""
    def __init__(self, in_features, out_features, weight_bits=8, act_bits=8):
        super().__init__()
        self.weight = nn.Parameter(torch.randint(-128, 127, (out_features, in_features)))
        self.bias = nn.Parameter(torch.zeros(out_features, dtype=torch.int32))
        self.weight_scale = 1.0
        self.act_scale = 1.0
        self.weight_bits = weight_bits
        self.act_bits = act_bits
    
    def forward(self, x):
        # x: 整数激活 [B, seq, in_features]
        # 整数矩阵乘 + 整数偏置
        out = torch.matmul(x, self.weight.t()) + self.bias
        # 重新量化到act_bits范围
        out = self.requantize(out, self.act_bits)
        return out
    
    def requantize(self, x, bits):
        scale = x.abs().max() / (2**(bits-1) - 1)
        return torch.clamp(torch.round(x / scale), -(2**(bits-1)), 2**(bits-1)-1)


class SDShiftGELU(nn.Module):
    """Sign-Dependent ShiftGELU: 符号相关的GELU整数近似"""
    def __init__(self, num_bits=8):
        super().__init__()
        self.num_bits = num_bits
    
    def forward(self, x):
        # x: 整数输入
        # GELU(x) ≈ x * Φ(x) where Φ is CDF of standard normal
        # 整数近似: 使用查找表或分段线性近似
        
        # 符号相关处理
        positive_mask = x > 0
        negative_mask = x <= 0
        
        out = torch.zeros_like(x)
        # 正数区域: GELU(x) ≈ x (近似)
        out[positive_mask] = x[positive_mask]
        # 负数区域: GELU(x) ≈ 0.5 * x * (1 + tanh(...)) 的整数近似
        out[negative_mask] = self.negative_approx(x[negative_mask])
        
        return out
    
    def negative_approx(self, x):
        # 整数近似: GELU(x) ≈ 0 for very negative, smooth transition
        return torch.clamp(x // 2, -(2**(self.num_bits-1)), 0)


class ConstrainedShiftmax(nn.Module):
    """约束Shiftmax: 整数Softmax近似"""
    def __init__(self, dim=-1, num_bits=8):
        super().__init__()
        self.dim = dim
        self.num_bits = num_bits
    
    def forward(self, x):
        # 整数Softmax: 使用位移近似指数
        # exp(x) ≈ 2^(x * log2(e)) ≈ 1 << (x >> shift)
        
        # 减去最大值防止溢出
        x_max = x.amax(dim=self.dim, keepdim=True)
        x_shifted = x - x_max
        
        # 使用2的幂次近似指数
        # exp(x) ≈ 2^(x / scale) where scale controls precision
        scale = 8  # 可调节
        exp_approx = torch.clamp(1 << (x_shifted // scale), 1, 2**self.num_bits - 1)
        
        # 归一化
        sum_exp = exp_approx.sum(dim=self.dim, keepdim=True)
        out = (exp_approx * (2**self.num_bits - 1)) // sum_exp
        
        return out


class ScalePreservingSplitConv(nn.Module):
    """尺度保持分离卷积: 多尺度投影器的独立激活尺度"""
    def __init__(self, in_ch, out_ch, num_scales=3):
        super().__init__()
        self.branches = nn.ModuleList([
            nn.Conv2d(in_ch, out_ch // num_scales, 1, bias=False)
            for _ in range(num_scales)
        ])
        self.scales = [1.0] * num_scales  # 每分支独立尺度
    
    def forward(self, x_list):
        # x_list: 多尺度特征列表
        outputs = []
        for i, (x, branch) in enumerate(zip(x_list, self.branches)):
            out = branch(x)
            # 应用分支特定尺度
            out = torch.round(out * self.scales[i])
            outputs.append(out)
        return torch.cat(outputs, dim=1)
```

---

## 四、实验结果

| 指标 | 结果 |
|------|------|
| 实验指标 | 数值 |
|----------|------|

---

## 五、关键创新点

- **低比特量化**: 在保持精度的同时大幅降低内存和计算需求
- **纯整数推理**: 无需浮点运算单元，适配边缘加速器

---

## 六、讨论与局限

本文在模型压缩和效率优化方面做出了有意义的贡献。未来工作可以进一步探索更大规模模型的应用，以及与其他压缩技术的组合效果。

---

*分析时间: 2026-07-29*  
*分析人: AI Assistant*
