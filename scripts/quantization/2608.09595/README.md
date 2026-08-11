# Paper: 2608.09595 - From Sweep to Seam: Interleaved Cross-Block Post-Training Quantization

## Implementation

This directory contains a standalone PyTorch implementation of Interleaved Cross-Block PTQ (ICB-PTQ) targeting Qwen3-0.6B.

## Run

```bash
python3 demo.py
```

## Method Overview

ICB-PTQ reorders the quantization pipeline so that all blocks of the same type (Attention vs FFN) are quantized together, enabling kernel fusion and better GPU utilization while maintaining cross-block correlation benefits.

## Files

- `demo.py`: Standalone implementation with synthetic Qwen-like layers
- `README.md`: This file
