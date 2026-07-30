# GSQ: Gumbel-Softmax Quantization for LLMs

This branch contains a PyTorch implementation of **GSQ (Gumbel-Softmax Quantization)** from arXiv:2604.18556, adapted for **Qwen3-0.6B**.

## Structure

- `analysis/paper_analysis.md` — Detailed paper analysis
- `code/` — PyTorch implementation
  - `gsq_quantizer.py` — Core GSQ algorithm (ternary, 2-bit, b-bit with local-shift)
  - `qwen3_gsq.py` — Qwen3-0.6B model adapter
  - `demo.py` — CLI demo script
  - `utils.py` — Evaluation utilities
  - `requirements.txt` — Python dependencies
  - `README.md` — Code documentation
- `papers/2026-04/2604.18556/README.md` — Paper reference

## Quick Start

```bash
cd code
pip install -r requirements.txt

# Run ternary quantization demo
python demo.py --model Qwen/Qwen3-0.6B --bits ternary --calibration-data path/to/calib

# Run 2-bit quantization demo
python demo.py --model Qwen/Qwen3-0.6B --bits 2 --calibration-data path/to/calib

# Run 3-bit with local-shift
python demo.py --model Qwen/Qwen3-0.6B --bits 3 --calibration-data path/to/calib
```

## Target Model: Qwen3-0.6B

| Config | Value |
|--------|-------|
| hidden_size | 1024 |
| num_hidden_layers | 28 |
| num_attention_heads | 16 |
| num_key_value_heads | 8 (GQA) |
| intermediate_size | 3072 |
| vocab_size | 151936 |

## Paper Reference

- **Title**: GSQ: Highly-Accurate Low-Precision Scalar Quantization for LLMs via Gumbel-Softmax Sampling
- **arXiv**: [2604.18556](https://arxiv.org/abs/2604.18556)
- **Authors**: Dadgarnia et al., ISTA/ETH Zürich/Red Hat AI
- **Code**: https://github.com/IST-DASLab/GSQ
