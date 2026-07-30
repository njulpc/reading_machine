# HESTIA: A Hessian-Guided Differentiable Quantization-Aware Training Framework for Extremely Low-Bit LLMs (arXiv:2601.20745)

See demo.py for the core algorithm reproduction with detailed header notes.
Validation: real Qwen3-0.6B weights from two layers (mock fallback); hard-STE vs uniform anneal vs Hestia-paced anneal final 2-bit MSE.

Run: python3 demo.py
