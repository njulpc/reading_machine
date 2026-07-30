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

- **Learnable Modulation (LM)**: Three learnable factors (δ_μ, δ_α, δ_Δ) modulate weight distribution
- **Softened Ternarization (ST)**: Two-stage relay with tanh-based transition function
  - Stage 1 (0 < t ≤ γ): Differentiable with progressive sharpness s = (t/γ)·s₀
  - Stage 2 (γ < t ≤ 1): Hard ternarization with straight-through estimator
- **Sliding-window optimization**: Output reconstruction across multiple layers
- **Default calibration**: 512 samples, 60 epochs, γ=0.5, s₀=30
