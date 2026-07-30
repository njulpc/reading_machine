# CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs

> **arXiv ID**: 2606.26650
> **Title**: CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs
> **Authors**: Shigeng Wang, Chao Li, Yangyuxuan Kang, Jiawei Fan, Anbang Yao (Intel Labs China)
> **Published**: June 2026 (ICML 2026)

---

## 1. Core Contribution

CAT-Q is a **post-training ternary quantization** method for LLMs that achieves superior performance compared to quantization-aware training (QAT) baselines like BitNet 1.58-bit, while using **100,000× fewer training tokens** (512 calibration samples vs. 100B tokens).

### Key Innovations

1. **Learnable Modulation (LM)**: Modulates pre-trained weight distribution with learnable factors to make weights less sensitive to ternarization
2. **Softened Ternarization (ST)**: Two-stage relay of differentiable ternarization → hard ternarization via a novel tanh-based transition function
3. **Sliding-Layer Optimization**: Optimizes multiple layers together (output reconstruction) rather than layer-wise weight reconstruction

---

## 2. Method Details

### 2.1 Problem Formulation

Ternary quantization maps weights to {-1, 0, 1}:

```
argmin_{α,T} ||W - αT||²
```

Where:
- W: high-precision weights
- α > 0: scaling factor
- T: ternary weights with T_i ∈ {-1, 0, 1}

Hard ternarization:
```
T_i = Q(W_i; Δ) = 
  1,    if W_i > Δ
  0,    if |W_i| ≤ Δ
  -1,   if W_i < -Δ
```

### 2.2 Learnable Modulation (LM)

Transforms weight distribution before ternarization:

```
Ŵ = (W - μ) / α
```

Where:
- μ₀ = mean(W), α₀ = absmean(W - μ₀)
- μ = μ₀ + δ_μ · α₀, where δ_μ ∈ (-1, 1) is learnable
- α = α₀ · δ_α, where δ_α > 0 is learnable
- Δ = δ_Δ · Δ₀, where δ_Δ > 0 is learnable, Δ₀ = 0.5

**Three learnable factors**: δ_μ (mean shift), δ_α (scale), δ_Δ (threshold)

**Disentangled learning strategy**: Use Ŵ as proxy for learning T, but approximate W ≈ αT (without μ) for reconstruction.

### 2.3 Softened Ternarization (ST)

Novel transition function:

```
f(W; s, Δ) = (tanh(s·(W - Δ)) + tanh(s·(W + Δ))) / (2·tanh(s))
```

Properties:
1. Symmetric about origin, differentiable
2. s → 0: approximates identity mapping f(·) = W
3. s increases: progressively sharper, asymptotically converges to ternary output
4. s → ∞: approaches hard ternarization

**Two-stage process** (over m calibration epochs):
```
T_i = 
  W_i,                          if t = 0 (initialization)
  f(Ŵ_i; (t/γ)·s₀, δ_Δ·Δ₀),   if 0 < t ≤ γ (differentiable stage)
  Q(Ŵ_i; δ_Δ·Δ₀),              if γ < t ≤ 1 (hard stage)
```

Where:
- t: normalized calibration time
- γ: epoch ratio for differentiable stage (default ~0.5)
- s₀: initial sharpness (default 30)

### 2.4 Sliding-Layer Optimization

Instead of layer-wise weight reconstruction, uses **sliding-window output reconstruction**:

```
argmin_{A,T} ||F(W, X) - F(A·T, X)||²
```

Where:
- W = {W₁, ..., Wₗ}: weights in sliding window of l layers
- X: calibration input features
- A = {α₁, ..., αₗ}: scaling factors
- T = {T₁, ..., Tₗ}: ternary weights

This makes neighboring layers aware of each other, reducing quantization error.

---

## 3. Experimental Results

### Scaling (Table 1)

| Model | Params | Time (8×A100) | CAT-Q vs BitNet v2 |
|-------|--------|---------------|-------------------|
| Qwen3-1.7B | 1.7B | 1h | Better |
| Qwen3-4B | 4B | 2h | Better |
| Qwen3-8B | 8B | 4h | Better |
| Qwen3-14B | 14B | 8h | First ternary PTQ |
| Qwen3-32B | 32B | 15h | First ternary PTQ |
| Qwen3-235B | 235B | 60h | First ternary PTQ |

**Training token reduction**: ~100,000× (512 samples ≈ 1M tokens vs. 100B tokens for BitNet)

### Zero-Shot Benchmarks (Table 2, Qwen3-8B)

| Method | PIQA | ARC-e | ARC-c | Hella. | WG | Avg |
|--------|------|-------|-------|--------|-----|-----|
| FP16 | 79.1 | 80.2 | 62.1 | 72.3 | 68.2 | 72.4 |
| BitNet v2 | 75.3 | 76.8 | 55.4 | 66.1 | 62.8 | 67.3 |
| **CAT-Q** | **77.8** | **79.1** | **59.7** | **70.5** | **66.3** | **70.7** |

### Ablation Studies (Table 6)

| Method | LM | ST | ARC-c | Hella. |
|--------|-----|-----|-------|--------|
| Baseline | ✗ | ✗ | 52.3 | 64.8 |
| +LM only | ✓ | ✗ | 55.1 | 66.9 |
| +ST only | ✗ | ✓ | 54.7 | 66.2 |
| **CAT-Q** | **✓** | **✓** | **59.7** | **70.5** |

LM and ST are complementary — both needed for best results.

---

## 4. Key Insights

1. **PTQ can beat QAT for ternary**: With proper optimization, post-training methods can surpass training-intensive approaches
2. **Distributional alignment matters**: LM's modulation of weight statistics is crucial for reducing information loss
3. **Differentiable → hard relay works**: ST's smooth transition avoids convergence issues of pure hard ternarization
4. **Sliding-window > layer-wise**: Output reconstruction across multiple layers captures dependencies better
5. **Scales to 235B**: First ternary PTQ method to work on very large models

---

## 5. Adaptation to Qwen3-0.6B

### Architecture Mapping

| Component | Qwen3-0.6B Spec | CAT-Q Application |
|-----------|----------------|-------------------|
| hidden_size | 1024 | All linear layers |
| num_layers | 28 | Sliding window across layers |
| attention | GQA (16 heads, 8 KV) | q/k/v/o projections |
| FFN | SwiGLU (3072 intermediate) | gate/up/down projections |

### Implementation Considerations

1. **Sliding window size**: Use default from SliderQuant (typically 2-3 layers)
2. **Calibration data**: 512 samples from C4, length 2048
3. **Epochs**: 60 epochs (default with 512 samples)
4. **Optimizable layers**: All Linear layers except embeddings and lm_head
5. **Ternary weights**: {-1, 0, 1} with per-layer or per-group scaling

---

## Citation

```bibtex
@inproceedings{wang2026catq,
  title={CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs},
  author={Wang, Shigeng and Li, Chao and Kang, Yangyuxuan and Fan, Jiawei and Yao, Anbang},
  booktitle={International Conference on Machine Learning},
  year={2026}
}
```
