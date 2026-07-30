# StableQAT: Stable Quantization-Aware Training at Ultra-Low Bitwidths (arXiv:2601.19320)

See demo.py for the core algorithm reproduction with detailed header notes.
Validation: latent-weight QAT on real Qwen3-0.6B q_proj weight (mock fallback); Fourier surrogate vs STE final MSE at 2/3-bit.

Run: python3 demo.py
