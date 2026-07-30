# GSQ: Gumbel-Softmax Quantization for LLMs

## Paper Information

- **Title**: GSQ: Highly-Accurate Low-Precision Scalar Quantization for LLMs via Gumbel-Softmax Sampling
- **arXiv ID**: 2604.18556
- **Authors**: Alireza Dadgarnia, Soroush Tabesh, Mahdi Nikdan, Michael Helcig, Eldar Kurtić, Maximilian Kleinegger, Dan Alistarh
- **Institution**: ISTA, ETH Zürich, Red Hat AI, TU Wien
- **Published**: April 2026 (v1), May 2026 (v2)
- **Code**: https://github.com/IST-DASLab/GSQ

## Core Contribution

GSQ is a post-training scalar quantization (PTQ) method that closes most of the accuracy gap between simple scalar quantization (GPTQ, AWQ) and complex vector/trellis quantization (QTIP, AQLM) at low bit-widths (2-3 bits), while remaining fully compatible with existing scalar inference kernels (GGUF, Humming, etc.).

## Key Idea

Reformulate layer-wise weight reconstruction as a **differentiable discrete-assignment problem** using Gumbel-Softmax relaxation:

1. For each weight coordinate, introduce trainable logits over candidate grid points
2. Sample soft quantized weights via Gumbel-Softmax
3. Anneal temperature to collapse soft assignments to discrete grid points
4. Jointly optimize discrete assignments and per-group scales via gradient descent

## Method Details

### 1. Gumbel-Softmax Sampling (Algorithm 1)

Given a discrete set $\mathcal{D} = \{d_1, ..., d_n\}$ with learnable logits $\ell_1, ..., \ell_n$:

```
For each candidate i:
  Draw g_i ~ Gumbel(0, 1)
  p_i = exp((κ·ℓ_i + g_i) / τ) / Σ_j exp((κ·ℓ_j + g_j) / τ)
Return soft sample: d̃ = Σ_i p_i · d_i
```

- **τ (temperature)**: Controls sharpness. Annealed from 2.0 → 0.05
- **κ (scale factor)**: Controls logit influence. Annealed from 100 → 500

### 2. Ternary Quantization (1.58-bit)

Constraint: $\bar{w} = s \cdot m \odot b$ where $s \in \mathbb{R}$, $m \in \{0,1\}^d$, $b \in \{-1,1\}^d$

- **mask logits** $\ell^{(m)} \in \mathbb{R}^d$: controls whether weight is nonzero
- **sign logits** $\ell^{(b)} \in \mathbb{R}^d$: controls sign of nonzero weight
- **shared scale** $s$: single scalar (or per-group)

Initialization from GPTQ ternary solution (Equation 3):
- mask logit = +1.0 if GPTQ weight ≠ 0, else -1.0
- sign logit = +1.0 if GPTQ weight = +1, -1.0 if -1, 0.0 if 0

### 3. 2-bit Quantization

Grid: $\mathcal{G}_2 = \{-2, -1, 0, 1\}$

- 4 logits per coordinate (one for each grid point)
- Shared scale $s$ (can be negative to remove bias)
- Total trainable params: $4d + 1$

Initialization: Gaussian-like prior centered at GPTQ solution (Appendix A).

### 4. Higher Bit-widths (b > 2): Local-Shift Formulation

**Problem**: Naive approach requires $2^b$ logits per coordinate — exponentially expensive.

**Solution**: Local-shift parameterization (Figure 1):
- Given GPTQ-initialized grid index $j_i^0$ for each coordinate
- Learn 5 logits for shifts $\delta_i \in \{-2, -1, 0, +1, +2\}$
- Final index: $j_i = \text{clip}(j_i^0 + \delta_i, 1, 2^b)$
- Reduces params from $d \times 2^b + 1$ to $5d + 1$

**Validation** (Table 16): 99.999996% of full-relaxation assignments lie within {-2,-1,0,1,2} neighborhood.

### 5. Objective and Optimization

**Objective**: Minimize reconstruction MSE
```
L = ||f(x; w̄) - f(x; w)||_F^2
```

**Optimizer**: Lion (not AdamW)
- Lion is sign-based, less sensitive to vanishing gradients in saturated Gumbel-Softmax
- AdamW stalls when gradients become exponentially small (Lemma B.1)

**Hyperparameters** (Table 7):
- Logits LR: 1e-4, Group scales LR: 5e-5
- Weight decay: 1.0, Betas: (0.9, 0.95)
- Epochs: 20 (dense), 10 (MoE)
- Batch size: 64, Group size: 128
- Calibration: 4096 sequences × 4096 length (FineWeb-Edu)

**Within-block staging** (Appendix C):
1. Optimize q_proj, k_proj independently (linear recon)
2. Optimize v_proj, o_proj jointly (attention output recon)
3. Optimize MLP projections (full block recon)

## Results

### Llama-3.1-8B-Instruct (Table 1)

| Method | bpp | ARC-C | ARC-E | Hella. | PIQA | Wino. | Avg. |
|--------|-----|-------|-------|--------|------|-------|------|
| FP16 | 16 | 55.12 | 79.63 | 79.16 | 80.85 | 73.80 | 73.71 |
| QTIP | 2.00 | 50.68 | 75.42 | 75.02 | 78.18 | 70.09 | 69.88 |
| EfficientQAT | 2.25 | 43.77 | 67.55 | 68.65 | 74.65 | 64.33 | 63.79 |
| **GSQ** | **2.13** | **48.12** | **72.35** | **73.42** | **78.07** | **70.80** | **68.55** |

GSQ improves 4.76 points over best scalar baseline (EfficientQAT) at 2 bits, trails QTIP by only 1.33 points.

### Llama-3.1-70B-Instruct

At 2 bits: GSQ improves 4.14 points over EfficientQAT, trails QTIP by 1.68 points.
At 3 bits: GSQ essentially matches QTIP.

### Kimi-K2.5 (1T-parameter MoE)

GSQ quantizes non-shared experts to 2 bits:
- AIME25: 95.33 → 93.00
- GPQA Diamond: 89.29 → 76.57
- LiveCodeBench: 61.37 → 69.37 (improves!)
- MATH500: 96.68 → 97.32 (improves!)

First method to achieve low-bit, near-lossless quantization of trillion-parameter MoE with fully scalar format.

### GGUF K-Quant Extension (Table 4)

Starting from Unsloth Qwen3-8B GGUF checkpoints:
- Q2_K: Average score improves from 50.03 → 56.28
- Q3_K_M: Average score improves from 60.52 → 61.61
- Preserves GGUF format compatibility

## Key Insights

1. **Optimization gap, not representation gap**: Much of the scalar-vs-vector quantization gap is an optimization problem, not fundamental.

2. **Gumbel-Softmax is natural for low-bit**: Small grid cardinality (3-8 levels) makes the relaxation tight and tractable.

3. **Lion > AdamW for saturated relaxations**: Sign-based updates handle vanishing gradients better than second-moment adaptive methods.

4. **Local-shift is sufficient**: For b > 2, weights rarely move more than 2 grid positions from GPTQ initialization.

5. **Symmetric quantization works**: GSQ uses symmetric group-wise quantization without zero-points, proving gains come from better assignments, not more flexible quantizers.

## Limitations

1. **Memory overhead**: Auxiliary logits require 2-5× weight memory during optimization (temporary, not deployed).

2. **Depends on good initialization**: GPTQ warm-start is crucial; poor initialization restricts recovery.

3. **Calibration data sensitivity**: Performance on some tasks (e.g., GPQA) depends on calibration data diversity.

4. **Not universally better than VQ**: Vector methods remain more expressive at fixed bit-width when specialized kernels are acceptable.

## Why This Matters

- **Deployability**: Fully compatible with existing scalar inference kernels (llama.cpp, vLLM + Humming, etc.)
- **Scalability**: Works on trillion-parameter MoE models where VQ methods are infeasible
- **Practicality**: Can improve existing GGUF checkpoints without changing deployment format
- **Speedup**: 2-bit GSQ achieves 6.2× speedup over BF16 on L40s (Table 2)

## Citation

```bibtex
@article{dadgarnia2026gsq,
  title={GSQ: Highly-Accurate Low-Precision Scalar Quantization for LLMs via Gumbel-Softmax Sampling},
  author={Dadgarnia, Alireza and Tabesh, Soroush and Nikdan, Mahdi and Helcig, Michael and Kurti{\'c}, Eldar and Kleinegger, Maximilian and Alistarh, Dan},
  journal={arXiv preprint arXiv:2604.18556},
  year={2026}
}
```
