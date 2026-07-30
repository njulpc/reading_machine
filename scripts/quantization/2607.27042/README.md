# 2607.27042 - GPTQ-2D

## Paper
**GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding**  
arXiv:2607.27042

## Implementation

This directory contains a PyTorch implementation of:
1. **GPTQ-2D** - Two-sided adaptive rounding with anti-diagonal parallelism
2. **Naive Quartic GPTQ** - Baseline for verification
3. **One-Sided GPTQ** - Standard GPTQ for comparison

## Files

- `demo.py` - Standalone demonstration script

## Usage

```bash
python3 demo.py
```

## Key Components

### GPTQ-2D
- **Objective**: Minimize ||A(Z - X)B||_F^2
- **Parallelism**: Anti-diagonal entries rounded in parallel
- **Complexity**: O(m^3) for square matrices (vs O(m^4) naive)
- **Equivalence**: Produces identical results to naive quartic method

### Anti-Diagonal Structure
For an m×n matrix, anti-diagonal k contains entries (i, j) where i + j = k.
Entries on the same anti-diagonal are independent under the Kronecker structure.

## Model Target

Qwen3-0.6B weight quantization (576 dim, 28 layers)

## Notes

- This is a demonstration implementation of the core algorithm
- Full production implementation would include:
  - Actual Hessian computation from calibration data
  - Group-wise quantization for better accuracy
  - Integration with HuggingFace transformers
- The anti-diagonal parallelization requires custom GPU kernels for full speedup
