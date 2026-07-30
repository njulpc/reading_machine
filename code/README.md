# GSQ Code

PyTorch implementation of GSQ (Gumbel-Softmax Quantization) for Qwen3-0.6B.

## Files

| File | Description |
|------|-------------|
| `gsq_quantizer.py` | Core GSQ algorithm (ternary, 2-bit, b-bit with local-shift) |
| `qwen3_gsq.py` | Qwen3-0.6B model adapter |
| `demo.py` | CLI demo script |
| `utils.py` | Evaluation utilities |
| `requirements.txt` | Dependencies |

## Quick Start

```bash
pip install -r requirements.txt

# Ternary quantization
python demo.py --bits ternary --epochs 20

# 2-bit quantization
python demo.py --bits 2 --epochs 20

# 3-bit with local-shift
python demo.py --bits 3 --epochs 20

# Save to custom path
python demo.py --bits 2 --output ./my_gsq_model
```

## Core API

```python
from gsq_quantizer import GSQQuantizer, GSQConfig

config = GSQConfig(bits=2, num_epochs=20, device="cuda")
quantizer = GSQQuantizer(config)

quantized_weight, scale = quantizer.quantize(weight, calibration_input)
```

## Implementation Notes

- Uses **Lion optimizer** (sign-based, handles vanishing gradients in saturated Gumbel-Softmax)
- Temperature annealed from 2.0 → 0.05
- Kappa annealed from 100 → 500
- Local-shift formulation for b > 2 (5 logits per coordinate instead of 2^b)
- Group-wise quantization with group_size=128
