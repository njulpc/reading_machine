# Paper: 2608.06763 - CubicQuant
# Title: Parametric Non-Uniform Codebooks for High-Throughput LLM Inference
# Core Method: Monotonic cubic curve mapping for non-uniform scalar quantization

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

This demo implements the core idea of CubicQuant:
1. Parametric non-uniform scalar quantization using monotonic cubic curves
2. Maps uniformly spaced integer codes to non-uniform reconstruction levels
3. Two shape parameters + one scale per group
4. Supports 1-8 bit payloads with group-wise adaptation

The implementation shows CubicQuant applied to Qwen3-0.6B weights,
with RMSE comparison against uniform integer and floating-point baselines.

## Target Model

Qwen3-0.6B (or fallback to Qwen2-0.5B)

## Notes

- CubicQuant preserves a dense integer code stream while adapting reconstruction levels
- The family spans 1-8 bit weight payloads
- Symmetric uniform integer quantization is an exact special case (a=b=0)
