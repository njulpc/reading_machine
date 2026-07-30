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

quantized_weight, scales = quantizer.quantize(weight, calibration_input)
# scales: [num_groups] per-group scale factors
```

## Implementation Details

- **Group-wise quantization**: group_size=128, per-group scales
- **GPTQ warm-start initialization**: Round-to-nearest initialization with Gaussian noise
- **Gumbel-Softmax relaxation**: Temperature annealed 2.0 → 0.05, kappa annealed 100 → 500
- **Lion optimizer**: Sign-based updates with separate LR for logits (1e-4) and scales (5e-5)
- **Local-shift (b>2)**: Soft indexing maintains gradient flow; 5 logits per coordinate
- **Integer symmetric grid**: Compatible with scalar inference kernels
- **Real calibration data**: Forward hooks capture actual layer activations
