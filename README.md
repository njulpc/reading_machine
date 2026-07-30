# Paper 2607.22564: MAB-driven Structured Pruning

> **Branch**: `paper/2607.22564-qwen3-pruning`  
> **Paper**: [arXiv:2607.22564](https://arxiv.org/abs/2607.22564)  
> **Title**: Loss-Aware Feature-Map Pruning in Convolutional Neural Networks Using Multi-Armed Bandits

This branch contains a focused implementation of the paper's core method, adapted for the **Qwen3-0.6B** Transformer language model.

## What's Included

| Directory | Content |
|-----------|---------|
| `analysis/` | Detailed paper analysis and adaptation notes |
| `code/` | PyTorch implementation for Qwen3-0.6B pruning |
| `papers/` | Original paper metadata |

## Quick Links

- [Paper Analysis](analysis/paper_analysis.md)
- [Code README](code/README.md)
- [Demo Script](code/demo.py)

## Run the Demo

```bash
cd code
pip install -r requirements.txt
python demo.py --target attention --play-budget 500 --top-k 50 --policy ucb1
```

## Original Paper Abstract

> Convolutional neural networks often contain redundant feature maps that increase storage and inference cost. This paper presents a loss-aware feature-map pruning framework using multi-armed bandits. Feature-map pruning is structured because it removes complete convolutional output channels and their producing filters rather than isolated scalar weights. Each candidate feature map is treated as an arm. At each play time, one map is temporarily masked and evaluated on a sampled mini-batch; the map is then restored and the observed loss change is converted into a safe-removal reward. After a fixed play budget, candidate maps are ranked by learned scores and the top-k maps are permanently removed.

## License

See original paper for licensing. Code provided for research purposes.
