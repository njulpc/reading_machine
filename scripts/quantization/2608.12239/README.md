# Paper: 2608.12239 - HAMP-LIC

## Hessian-Aware Mixed-Precision PTQ Demo

This script demonstrates Hessian-aware mixed-precision post-training quantization for neural networks.

## Run

```bash
pip install torch
python3 demo.py
```

## Core Algorithm

1. **Hessian trace estimation**: Compute second-order sensitivity per layer.
2. **Task-aware refinement**: Adjust sensitivity with task-specific metrics.
3. **Global bit allocation**: Assign bits under model size constraint.
4. **Block reconstruction**: Fine-tune quantized parameters with calibration.
