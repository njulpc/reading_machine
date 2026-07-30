# CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs

> **Branch**: `paper/2606.26650-qwen3-catq`  
> **Paper**: [arXiv:2606.26650](https://arxiv.org/abs/2606.26650)  
> **Target Model**: Qwen3-0.6B

This branch contains a PyTorch implementation of **CAT-Q** (Cost-efficient and Accurate Ternary Quantization), adapted for **Qwen3-0.6B**.

## Structure

- `analysis/paper_analysis.md` — Detailed paper analysis
- `code/` — PyTorch implementation
  - `catq_quantizer.py` — Core CAT-Q algorithm (LM + ST)
  - `qwen3_catq.py` — Qwen3-0.6B model adapter
  - `demo.py` — CLI demo script
  - `utils.py` — Evaluation utilities
  - `requirements.txt` — Python dependencies
  - `README.md` — Code documentation
- `papers/2026-06/2606.26650/` — Paper reference

## Quick Start

```bash
cd code
pip install -r requirements.txt
python demo.py --model Qwen/Qwen3-0.6B --calibration-samples 512 --epochs 60
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

- **Title**: CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs
- **arXiv**: [2606.26650](https://arxiv.org/abs/2606.26650)
- **Authors**: Wang et al., Intel Labs China
- **Code**: https://github.com/IntelChina-AI/BitTern
