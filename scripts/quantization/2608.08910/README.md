# Paper: 2608.08910 - Tied Trit-Planes

## Implementation

This directory contains a standalone PyTorch implementation of Tied Trit-Planes (TTP) quantization targeting Qwen3-0.6B.

## Run

```bash
python3 demo.py
```

## Method Overview

TTP constrains PTQTP's two free per-group scales to a fixed ratio of 3:1, collapsing the representation to a uniform nine-level quantizer. This reduces storage overhead and simplifies hardware implementation.

## Files

- `demo.py`: Standalone implementation with synthetic Qwen-like layers
- `README.md`: This file
