# Paper: 2608.06916 - MiCoPro
# Title: End-to-End Mixed Precision HW/SW Co-design with HW-aware Proxy Model
# Core Method: Holistic mixed-precision quantization exploration and deployment

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

This demo implements a simplified version of MiCoPro's core idea:
1. Layer-wise sensitivity analysis to determine quantization robustness
2. Mixed-precision bit-width assignment under a latency budget
3. Hardware-aware proxy for latency estimation
4. Applied to Qwen3-0.6B layers

The demonstration shows how different layers have different sensitivity
to quantization, and how mixed-precision allocation can achieve better
accuracy-latency trade-offs than uniform quantization.

## Target Model

Qwen3-0.6B (or fallback to Qwen2-0.5B)

## Notes

- This is a simplified educational implementation of MiCoPro's MPQ search
- Real MiCoPro includes hardware-specific latency models and bare-metal C code generation
- The demo focuses on the algorithmic core: sensitivity-aware mixed-precision assignment
