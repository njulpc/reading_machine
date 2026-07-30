# MAB-driven Structured Pruning for Qwen3-0.6B

> **Paper**: [arXiv:2607.22564](https://arxiv.org/abs/2607.22564)  
> **Title**: Loss-Aware Feature-Map Pruning in Convolutional Neural Networks Using Multi-Armed Bandits  
> **Authors**: Salem Ameen, Sunil Vadera  
> **Adaptation**: Transformer attention head & FFN neuron pruning for Qwen3-0.6B

---

## 📋 Overview

This project adapts the **Multi-Armed Bandit (MAB) driven structured pruning** framework from the paper to the **Qwen3-0.6B** Transformer language model. The core idea is:

1. **Treat each pruning candidate as an "arm"**: attention heads or FFN neurons
2. **Temporarily mask one arm at a time** and evaluate the loss change
3. **Use UCB1 or Thompson Sampling** to adaptively allocate evaluation budget
4. **Permanently remove the top-k safest arms** after the search phase

This approach is **loss-aware** (evaluates actual impact on model performance) and **computationally efficient** (avoiding exhaustive evaluation of all candidates).

---

## 🏗️ Architecture Target: Qwen3-0.6B

| Parameter | Value |
|-----------|-------|
| `hidden_size` | 1024 |
| `intermediate_size` | 3072 |
| `num_hidden_layers` | 28 |
| `num_attention_heads` | 16 |
| `num_key_value_heads` | 8 (GQA) |
| `head_dim` | 128 |
| `vocab_size` | 151936 |

**Pruning Targets**:
- **Attention Heads**: 28 layers × 16 heads = 448 candidate arms
- **FFN Neurons**: 28 layers × 3072 neurons = 86,016 candidate arms

---

## 📁 Project Structure

```
.
├── analysis/
│   └── paper_analysis.md          # Detailed paper analysis (in Chinese)
├── code/
│   ├── mab_pruner.py              # Core MAB pruning framework
│   ├── qwen3_pruner.py            # Qwen3-0.6B adapter
│   ├── demo.py                    # Demonstration script
│   ├── utils.py                   # Evaluation & visualization utilities
│   └── requirements.txt           # Python dependencies
└── papers/                        # Original paper metadata
    └── 2026-07/
        └── 2607.22564/
            └── tech_analysis.md   # Original technical analysis
```

---

## 🚀 Quick Start

### Installation

```bash
cd code
pip install -r requirements.txt
```

### Attention Head Pruning (UCB1)

```bash
python demo.py \
    --target attention \
    --play-budget 500 \
    --top-k 50 \
    --policy ucb1 \
    --output-dir ./pruned_attention
```

### FFN Neuron Pruning (Thompson Sampling)

```bash
python demo.py \
    --target ffn \
    --play-budget 1000 \
    --top-k 500 \
    --policy thompson \
    --output-dir ./pruned_ffn
```

### Evaluate Perplexity Impact

```bash
python demo.py \
    --target attention \
    --play-budget 500 \
    --top-k 50 \
    --eval-perplexity
```

---

## 🔧 Core Algorithm

### UCB1 Policy

At each iteration $t$, select the arm with the highest Upper Confidence Bound:

$$a_t = \arg\max_{a \in A} \left[ \mu_a + \sqrt{\frac{2\ln t}{n_a}} \right]$$

where $\mu_a$ is the empirical mean reward and $n_a$ is the play count for arm $a$.

### Thompson Sampling Policy

At each iteration, sample from the posterior distribution of each arm:

$$\theta_a \sim \text{Beta}(\alpha_a, \beta_a)$$

and select the arm with the highest sampled value.

### Reward Definition

For language modeling, the reward is based on **perplexity change**:

$$r_a = \text{clip}\left(\tau + \frac{L_{\text{original}} - L_{\text{masked}}}{s_r}, 0, 1\right)$$

where $L$ is the cross-entropy loss, $\tau$ is the tolerance parameter, and $s_r$ is the scaling constant.

---

## 📊 Expected Results

Based on the paper's findings on CNNs, we expect similar behavior for Transformers:

| Method | Pruning Ratio | Perplexity Δ | Search Time |
|--------|--------------|--------------|-------------|
| Magnitude-based | 30% | ~+5% | <1s |
| UCB1 (ours) | 30% | ~+1% | ~5min |
| Thompson (ours) | 30% | ~+1.5% | ~5min |
| Direct Eval | 30% | baseline | ~2h |

*Note: Exact numbers depend on calibration data and hyperparameters.*

---

## 🧪 Code Modules

### `mab_pruner.py`

Core MAB framework with:
- `MABPruner`: Main pruning engine
- `UCB1Policy`: Upper Confidence Bound policy
- `ThompsonSamplingPolicy`: Bayesian posterior sampling policy
- `direct_evaluation_pruning`: Oracle baseline for comparison

### `qwen3_pruner.py`

Qwen3-0.6B adapter with:
- `Qwen3MABPruner`: High-level interface for Qwen3 pruning
- `prune_attention_heads()`: Attention head MAB search
- `prune_ffn_neurons()`: FFN neuron MAB search
- `apply_permanent_attention_pruning()`: Physical weight removal
- `apply_permanent_ffn_pruning()`: Physical weight removal
- `evaluate_perplexity()`: Language model evaluation

### `utils.py`

Utility functions:
- `compute_flops_reduction()`: FLOPs analysis
- `compare_models()`: Parameter count comparison
- `plot_pruning_results()`: Visualization

---

## 📖 Citation

If you use this code, please cite the original paper:

```bibtex
@article{ameen2026loss,
  title={Loss-Aware Feature-Map Pruning in Convolutional Neural Networks Using Multi-Armed Bandits},
  author={Ameen, Salem and Vadera, Sunil},
  journal={arXiv preprint arXiv:2607.22564},
  year={2026}
}
```

---

## ⚠️ Notes

1. **GQA Handling**: Qwen3-0.6B uses Grouped Query Attention (GQA). When pruning query heads, the KV heads are kept intact. A more sophisticated implementation would map query heads to KV head groups.

2. **Permanent Pruning**: The `apply_permanent_*_pruning()` methods physically remove weights. This is a simplified implementation; for production use, consider using libraries like `torch-pruning` or `neural-compressor`.

3. **Memory**: Evaluating Qwen3-0.6B requires ~2GB GPU memory. The MAB search temporarily creates masked models in-place.

4. **Calibration Data**: Use domain-relevant text for best results. The demo uses sample Chinese texts.

---

## 🔗 References

- Original Paper: [arXiv:2607.22564](https://arxiv.org/abs/2607.22564)
- Qwen3 Model: [HuggingFace Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)
- MAB Theory: [Auer et al., "Finite-time Analysis of the Multiarmed Bandit Problem", 2002](https://link.springer.com/article/10.1023/A:1013689704352)
