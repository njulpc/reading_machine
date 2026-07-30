"""
Demo Script: MAB-driven Pruning for Qwen3-0.6B
===============================================

This script demonstrates how to use the MAB pruning framework to compress
Qwen3-0.6B by pruning attention heads and/or FFN neurons.

Usage:
    # Attention head pruning
    python demo.py --target attention --play-budget 500 --top-k 50
    
    # FFN neuron pruning
    python demo.py --target ffn --play-budget 1000 --top-k 500
    
    # Compare UCB1 vs Thompson Sampling
    python demo.py --target attention --policy ucb1 --play-budget 500 --top-k 50
    python demo.py --target attention --policy thompson --play-budget 500 --top-k 50
"""

import argparse
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer
import numpy as np
import random

from qwen3_pruner import Qwen3MABPruner, Qwen3PruningConfig


class TextDataset(Dataset):
    """Simple text dataset for evaluation."""
    
    def __init__(self, texts, tokenizer, max_length=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
        }


def get_sample_texts():
    """Return sample texts for demonstration."""
    return [
        "人工智能正在改变我们的世界。机器学习算法能够从大量数据中学习模式，",
        "深度学习是机器学习的一个分支，它使用多层神经网络来模拟人脑的工作方式。",
        "自然语言处理使计算机能够理解和生成人类语言，这是人工智能的重要应用领域。",
        "Transformer架构自2017年提出以来，已经成为自然语言处理领域的主流模型架构。",
        "大语言模型通过在海量文本数据上进行预训练，获得了强大的语言理解和生成能力。",
        "强化学习是一种通过与环境交互来学习最优策略的机器学习方法。",
        "计算机视觉技术使机器能够理解和分析图像和视频内容。",
        "神经网络剪枝是一种模型压缩技术，通过移除不重要的权重来减少模型大小。",
        "多臂老虎机问题是一个经典的序列决策问题，在推荐系统和在线广告中有广泛应用。",
        "模型量化通过降低权重精度来减少模型存储和计算需求。",
        "知识蒸馏是一种将大模型的知识转移到小模型的技术。",
        "自注意力机制允许模型在处理序列时关注不同位置的信息。",
        "BERT模型通过双向编码器表示，在多种自然语言理解任务上取得了突破性进展。",
        "GPT系列模型通过自回归语言建模，展现了强大的文本生成能力。",
        "模型压缩技术对于在资源受限设备上部署深度学习模型至关重要。",
    ]


def create_dataloader(tokenizer, batch_size=8, max_length=512, num_samples=None):
    """Create a DataLoader for evaluation."""
    texts = get_sample_texts()
    if num_samples:
        texts = texts[:num_samples]
    
    # Repeat texts to create a larger dataset
    texts = texts * 10
    
    dataset = TextDataset(texts, tokenizer, max_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    return dataloader


def parse_args():
    parser = argparse.ArgumentParser(
        description="MAB-driven pruning for Qwen3-0.6B",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Prune 50 attention heads using UCB1
  python demo.py --target attention --play-budget 500 --top-k 50 --policy ucb1
  
  # Prune 500 FFN neurons using Thompson Sampling
  python demo.py --target ffn --play-budget 1000 --top-k 500 --policy thompson
  
  # Evaluate perplexity before and after pruning
  python demo.py --target attention --play-budget 500 --top-k 50 --eval-perplexity
        """
    )
    
    parser.add_argument(
        "--model-path",
        type=str,
        default="Qwen/Qwen3-0.6B",
        help="Path to Qwen3-0.6B model (default: Qwen/Qwen3-0.6B)",
    )
    parser.add_argument(
        "--target",
        type=str,
        choices=["attention", "ffn", "both"],
        default="attention",
        help="What to prune: attention heads, FFN neurons, or both (default: attention)",
    )
    parser.add_argument(
        "--play-budget",
        type=int,
        default=500,
        help="Number of MAB iterations (default: 500)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=50,
        help="Number of units to prune (default: 50)",
    )
    parser.add_argument(
        "--policy",
        type=str,
        choices=["ucb1", "thompson"],
        default="ucb1",
        help="MAB policy: ucb1 or thompson (default: ucb1)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for evaluation (default: 8)",
    )
    parser.add_argument(
        "--seq-length",
        type=int,
        default=512,
        help="Sequence length (default: 512)",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.01,
        help="Reward tolerance parameter (default: 0.01)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./pruned_qwen3_0.6b",
        help="Output directory for pruned model (default: ./pruned_qwen3_0.6b)",
    )
    parser.add_argument(
        "--eval-perplexity",
        action="store_true",
        help="Evaluate perplexity before and after pruning",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use (default: cuda if available, else cpu)",
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 70)
    print("MAB-driven Structured Pruning for Qwen3-0.6B")
    print("Based on: arXiv:2607.22564")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Model: {args.model_path}")
    print(f"  Target: {args.target}")
    print(f"  Play Budget: {args.play_budget}")
    print(f"  Top-K: {args.top_k}")
    print(f"  Policy: {args.policy}")
    print(f"  Batch Size: {args.batch_size}")
    print(f"  Sequence Length: {args.seq_length}")
    print(f"  Tolerance: {args.tolerance}")
    print(f"  Device: {args.device}")
    print(f"  Seed: {args.seed}")
    print()
    
    # Set seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    
    # Create config
    config = Qwen3PruningConfig(
        model_path=args.model_path,
        play_budget=args.play_budget,
        top_k=args.top_k,
        batch_size=args.batch_size,
        seq_length=args.seq_length,
        tolerance=args.tolerance,
        policy=args.policy,
        device=args.device,
        seed=args.seed,
    )
    
    # Initialize pruner
    pruner = Qwen3MABPruner(config)
    
    # Create evaluation dataloader
    print("Creating evaluation dataset...")
    dataloader = create_dataloader(
        pruner.tokenizer,
        batch_size=args.batch_size,
        max_length=args.seq_length,
        num_samples=15,
    )
    
    # Evaluate baseline perplexity
    if args.eval_perplexity:
        print("\nEvaluating baseline perplexity...")
        baseline_ppl = pruner.evaluate_perplexity(dataloader)
        print(f"  Baseline Perplexity: {baseline_ppl:.2f}")
    
    # Perform pruning
    if args.target == "attention" or args.target == "both":
        print("\n" + "=" * 70)
        print("ATTENTION HEAD PRUNING")
        print("=" * 70)
        
        results = pruner.prune_attention_heads(
            dataloader=dataloader,
            play_budget=args.play_budget,
            top_k=args.top_k,
            policy=args.policy,
        )
        
        print(f"\nPruning Results:")
        print(f"  Top 10 heads to remove:")
        for i, arm in enumerate(results["top_k_arms"][:10]):
            score = results["top_k_scores"][i]
            print(f"    {i+1}. {arm}: score={score:.4f}")
        
        # Apply permanent pruning
        pruner.apply_permanent_attention_pruning()
    
    if args.target == "ffn" or args.target == "both":
        print("\n" + "=" * 70)
        print("FFN NEURON PRUNING")
        print("=" * 70)
        
        results = pruner.prune_ffn_neurons(
            dataloader=dataloader,
            play_budget=args.play_budget,
            top_k=args.top_k,
            policy=args.policy,
        )
        
        print(f"\nPruning Results:")
        print(f"  Top 10 neurons to remove:")
        for i, arm in enumerate(results["top_k_arms"][:10]):
            score = results["top_k_scores"][i]
            print(f"    {i+1}. {arm}: score={score:.4f}")
        
        # Apply permanent pruning
        pruner.apply_permanent_ffn_pruning()
    
    # Evaluate post-pruning perplexity
    if args.eval_perplexity:
        print("\nEvaluating post-pruning perplexity...")
        pruned_ppl = pruner.evaluate_perplexity(dataloader)
        print(f"  Post-Pruning Perplexity: {pruned_ppl:.2f}")
        print(f"  Perplexity Change: {pruned_ppl - baseline_ppl:+.2f}")
    
    # Save pruned model
    print(f"\n{'='*70}")
    print("SAVING PRUNED MODEL")
    print(f"{'='*70}")
    pruner.save_pruned_model(args.output_dir)
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()
