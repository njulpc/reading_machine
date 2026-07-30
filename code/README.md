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

- **Group-wise symmetric quantization**: group_size=128, one learnable scale per group; no zero-points
- **Warm-start**: GPTQ prior by default (`--init-method gptq`); `--init-method rtn` is kept for fast smoke tests
- **Grids**: ternary `{-1,0,1}`, 2-bit `{-2,-1,0,1}`, b-bit `{-(2^(b-1)), ..., 2^(b-1)-1}`
- **Gumbel-Softmax relaxation**: temperature annealed 2.0 → 0.05, kappa annealed 100 → 500
- **Initialization scale**: `init_noise_std=0.01`, `init_alpha=6.0` (paper Eq. 4 / official `std=0.01`, `strength=6`)
- **Lion optimizer**: separate LR for logits (1e-4, weight decay 1.0) and scales (5e-5, weight decay 0), cosine decay to 10%
- **Local-shift (b>2)**: learns shifts `{-2,-1,0,+1,+2}` around the initialized grid value with a boundary validity mask
- **Real calibration data**: forward hooks capture actual layer activations through the already-quantized prefix
