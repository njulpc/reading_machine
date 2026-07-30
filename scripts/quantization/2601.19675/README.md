# LoPRo: Enhancing Low-Rank Quantization via Permuted Block-Wise Rotation (arXiv:2601.19675)

See demo.py for the core algorithm reproduction with detailed header notes.
Validation: real Qwen3-0.6B weight (mock fallback); LoPRo perm+Hadamard+protect vs naive 2-bit residual quantization MSE.

Run: python3 demo.py
