# 2607.26515 - HiFloat4 Format

## Paper
**HiFloat4 Format for End-To-End Reinforcement Learning Post-Training of Large Language Models**  
arXiv:2607.26515

## Implementation

This directory contains a PyTorch implementation of:
1. **HiFloat4 (HiF4) Quantizer** - Three-level hierarchical scaling FP4 quantization
2. **Rollout-ResQ** - Sparse residual correction for outlier compensation

## Files

- `demo.py` - Standalone demonstration script

## Usage

```bash
python3 demo.py
```

## Key Components

### HiFloat4 Quantizer
- **Tensor-level scaling**: Global scaling across entire tensor
- **Block-level scaling**: Per-block scaling (32 elements, like MXFP4)
- **Sub-block-level scaling**: Finer-grained scaling for outlier blocks

### Rollout-ResQ
- Sparse residual correction applied after FP4 matmul
- Compensates precision lost to outlier-driven underflow
- Hardware-friendly block-sparse pattern

## Model Target

Qwen3-0.6B-like architecture (576 dim, 8 heads, 28 layers)

## Notes

- This is a demonstration implementation focusing on the core algorithmic ideas
- Full integration with HuggingFace transformers would require additional work
- The actual HiF4 format details (exact encoding) may differ from the paper's hardware implementation
