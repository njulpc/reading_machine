# CAT-Q Code

PyTorch implementation of CAT-Q (Cost-efficient and Accurate Ternary Quantization) for Qwen3-0.6B.

## Files

| File | Description |
|------|-------------|
| `catq_quantizer.py` | Core CAT-Q algorithm (LM + ST) |
| `qwen3_catq.py` | Qwen3-0.6B model adapter |
| `demo.py` | CLI demo script |
| `utils.py` | Evaluation utilities |
| `requirements.txt` | Dependencies |

## Quick Start

```bash
pip install -r requirements.txt

# Run ternary quantization with default settings
python demo.py --calibration-samples 512 --epochs 60

# Custom settings
python demo.py --epochs 40 --gamma 0.4 --lr 5e-4 --output ./my_catq_model
```

## Core API

```python
from catq_quantizer import CATQQuantizer, CATQConfig

config = CATQConfig(num_epochs=60, gamma=0.5, lr=1e-3)
quantizer = CATQQuantizer(config)

quantized_weight, alpha, delta = quantizer.quantize_layer(weight, calibration_input)
```

## Implementation Notes

- **Learnable Modulation (LM)**: per-group statistics (group_size=128) with three learnable factors (δ_μ, δ_α, δ_Δ); reconstruction uses `W ≈ αT` without adding μ back
- **Softened Ternarization (ST)**: two-stage relay with tanh-based transition function
  - Normalized time uses `t=(epoch+1)/num_epochs`; paper defaults are γ=0.8, s₀=30, Δ₀=0.5
  - Stage 1 (`0 < t ≤ γ`): differentiable with progressive sharpness `s=(t/γ)·s₀`
  - Stage 2 (`γ < t ≤ 1`): forward is exactly hard ternarization; backward uses STE (the paper does not specify a different hard-stage backward rule)
- **Calibration**: the adapter captures real layer activations with forward hooks; random-input calibration was removed
- **Sliding window**: CAT-Q's full SliderQuant-style multi-layer window is not plumbed into this compact adapter; `window_size=1` gives per-layer output reconstruction
- **Positive factors**: δ_α and δ_Δ are parameterized with softplus and initialized so the initial multipliers are exactly 1
