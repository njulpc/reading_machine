# Paper: 2608.12026 - SoftWater

## SoftMax Head Quantization Demo

This script demonstrates class-aware rate allocation for softmax (LM Head) quantization.

**Note**: Qwen3-0.6B model download requires HuggingFace access. If the model is not available locally, the demo falls back to a synthetic vocabulary test.

## Run

```bash
pip install torch transformers accelerate
python3 demo.py
```

## Core Algorithm

1. **KL-divergence objective**: Quantize LM head weights to minimize KL between original and quantized output distributions.
2. **Class-aware geometry**: Per-token quantization grid density based on feature covariance and softmax curvature.
3. **SIC encoding**: Successive interference cancellation for efficient lattice quantization.
