# Paper: 2608.12140 - FQTree

## Fine-grained Quantization of Boosted Decision Trees

This script demonstrates fine-grained quantization-aware training for boosted decision trees.

## Run

```bash
pip install torch scikit-learn
python3 demo.py
```

## Core Algorithm

1. **Global step + tree-wise offset**: Compact non-negative integer leaf representations.
2. **Controlled clipping/pruning**: Remove low-information leaves during quantization.
3. **Bias folding**: Fold systematic bias into global bias term.
4. **Quantization-aware boosting**: Later trees adapt to already-quantized ensemble errors.
