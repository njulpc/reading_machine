# Paper: 2608.07019 - ReQuant
# Title: Fixed-Grid Discrete Refinement for Post-Training Quantization
# Core Method: Iterative discrete weight refinement on fixed quantization grid

See `demo.py` for standalone, runnable implementation.

## Run

```bash
python3 demo.py
```

## Requirements

```bash
pip install torch transformers
```

## Description

This demo implements the core idea of ReQuant:
1. Start from a simple round-to-nearest quantized model (or any PTQ initializer)
2. Iteratively revisit discrete weight assignments on the fixed quantization grid
3. Accept updates that strictly reduce MSE reconstruction error
4. Repeat for multiple sweeps until convergence

The implementation shows ReQuant as a plug-and-play post-processing stage for PTQ.

## Target Model

Qwen3-0.6B (or any compatible causal LM from HuggingFace)

## Notes

- If Qwen3-0.6B is not available, the script falls back to Qwen2-0.5B
- The demo focuses on weight quantization (INT4/INT8) for linear layers
- ReQuant is agnostic to the PTQ initializer used
