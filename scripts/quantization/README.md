# Quantization Toolkit

基于 arXiv 论文的 PyTorch 量化实现，以 Qwen3-0.6B 为验证目标。

## 支持的量化方法

| 方法 | 论文 | 描述 | 比特 |
|------|------|------|------|
| **RTN** | 2607.25451 | Round-to-Nearest 组量化 | 4/8-bit |
| **FP4** | 2607.24953 | 2D块转置不变 FP4 量化 | 4-bit |
| **INT8** | 2607.25180 | Per-channel INT8 对称量化 | 8-bit |
| **GPTQ** | - | OBS补偿 4-bit 量化 | 4-bit |
| **Angle-Aware QAT** | 2607.25870 | 角度感知自蒸馏 QAT | 4-bit |
| **Integer-Only Ops** | 2607.24981 | 整数GELU/Softmax/LayerNorm | 8-bit |

## 快速开始

```bash
# 1. 安装依赖
pip install torch transformers

# 2. 运行评估 (demo模式，无需下载模型)
cd scripts/quantization
python evaluate_qwen.py --demo --methods rtn4 rtn8 int8

# 3. 运行评估 (真实模型，需要GPU)
python evaluate_qwen.py --model Qwen/Qwen3-0.6B --methods rtn4 rtn8 int8 fp4
```

## 模块说明

### `quantization_toolkit.py`

核心量化模块：

- **RTNQuantizer**: 简单的round-to-nearest量化，适合快速验证
- **FP4Quantizer**: 2D块结构保证转置不变性，支持随机舍入
- **INT8Quantizer**: Per-channel对称INT8量化
- **AngleAwareQATLoss**: 冻结分类器原型，优化特征-权重角度几何
- **IntegerGELU/Softmax/LayerNorm**: 纯整数推理的激活函数近似

### `evaluate_qwen.py`

Qwen3-0.6B 评估管道：

```python
from evaluate_qwen import QwenQuantizationPipeline

pipeline = QwenQuantizationPipeline("Qwen/Qwen3-0.6B")
results = pipeline.run_full_evaluation(
    methods=["rtn4", "int8", "fp4"],
    eval_texts=["Hello world", "The quick brown fox"],
    output_file="results.json"
)
pipeline.print_summary(results)
```

## 核心算法示例

### 1. 2D Block FP4 量化

```python
from quantization_toolkit import FP4Quantizer

quantizer = FP4Quantizer(bits=4, block_size=32)
x = torch.randn(64, 64)

# 量化
x_dq, scales = quantizer.quantize(x)

# 验证转置不变性
assert quantizer.forward_backward_consistent(x)
```

### 2. 角度感知QAT损失

```python
from quantization_toolkit import AngleAwareQATLoss

loss_fn = AngleAwareQATLoss(lambda_repel=1.0, num_classes=2)

features = torch.randn(32, 128)      # [B, d]
targets = torch.randint(0, 2, (32,))  # [B]
frozen_classifier = torch.randn(2, 128)  # [C, d]

loss = loss_fn(features, targets, frozen_classifier)
```

### 3. Integer-Only GELU

```python
from quantization_toolkit import IntegerGELU

gelu = IntegerGELU(num_bits=8, use_lookup_table=True)
x = torch.randint(-128, 127, (1, 128))
out = gelu(x)  # 纯整数输出
```

## 论文对应关系

| 论文 | arXiv ID | 实现模块 |
|------|----------|---------|
| VAD to the Bone | 2607.25870 | `AngleAwareQATLoss` |
| Stable FP4 Training | 2607.24953 | `FP4Quantizer` |
| Bits and Memories | 2607.25451 | `RTNQuantizer`, `MemorizationEvaluator` |
| Integer-Only DETR | 2607.24981 | `IntegerGELU`, `IntegerSoftmax`, `IntegerLayerNorm` |
| Bekko Embedding | 2607.25180 | `INT8Quantizer` |
| MXAttention | 2607.24377 | (数据自由量化, 待实现) |
| LoRA Quantization | 2607.25583 | (LoRA+量化联合, 待实现) |

## 注意事项

1. **真实FP4需要硬件支持**: 当前为软件模拟，实际速度提升需下一代加速器
2. **Qwen3-0.6B需要足够显存**: 建议至少 8GB GPU 显存
3. **Demo模式**: 当模型不可用时，会自动使用合成模型进行演示

## 引用

如果你使用了本工具包，请引用相关论文：

```bibtex
@article{rahimifar2026fp4,
  title={Stable FP4 Training via Transposition-Invariant Block Quantization},
  author={Rahimifar, Mehdi and others},
  journal={arXiv preprint arXiv:2607.24953},
  year={2026}
}

@article{bauer2026vad,
  title={VAD to the Bone: Ultra-Tiny Speech Activity Detection for Edge Deployment},
  author={Bauer, Stephen and Seidel, Sheila and others},
  journal={arXiv preprint arXiv:2607.25870},
  year={2026}
}
```
