# QUAIL: Quantization Aware Unlearning for Mitigating Misinformation in LLMs (arXiv:2601.15538)

See demo.py for the core algorithm reproduction with detailed header notes.
Validation: real Qwen3-0.6B weight slice (mock fallback); forget logit shift direction cos-sim before/after 4-bit quantization.

Run: python3 demo.py
