"""
CAT-Q Demo Script
=================
Demonstrate CAT-Q ternary quantization on Qwen3-0.6B.
"""

import argparse
import torch
from qwen3_catq import Qwen3CATQ
from catq_quantizer import CATQConfig


def main():
    parser = argparse.ArgumentParser(description="CAT-Q Ternary Quantization for Qwen3-0.6B")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="Model path")
    parser.add_argument("--calibration-samples", type=int, default=512, help="Number of calibration samples")
    parser.add_argument("--seq-length", type=int, default=2048, help="Sequence length")
    parser.add_argument("--epochs", type=int, default=60, help="Number of optimization epochs")
    parser.add_argument("--gamma", type=float, default=0.8, help="Differentiable stage ratio (paper default)")
    parser.add_argument("--activation-rows", type=int, default=512, help="Rows subsampled from captured layer inputs")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--output", default="./catq_qwen3_0.6b", help="Output path")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="Device")
    args = parser.parse_args()
    
    print("=" * 60)
    print("CAT-Q: Cost-efficient and Accurate Ternary Quantization")
    print("Paper: arXiv:2606.26650")
    print("=" * 60)
    print(f"Config:")
    print(f"  Model: {args.model}")
    print(f"  Calibration samples: {args.calibration_samples}")
    print(f"  Sequence length: {args.seq_length}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Gamma: {args.gamma}")
    print(f"  Activation rows: {args.activation_rows}")
    print(f"  LR: {args.lr}")
    print(f"  Device: {args.device}")
    print()
    
    config = CATQConfig(
        num_calibration_samples=args.calibration_samples,
        seq_length=args.seq_length,
        num_epochs=args.epochs,
        gamma=args.gamma,
        activation_rows=args.activation_rows,
        lr=args.lr,
        device=args.device,
    )
    
    qwen3_catq = Qwen3CATQ(model_path=args.model, config=config)
    
    # Calibration texts
    calibration_texts = [
        "人工智能正在改变我们的世界。",
        "深度学习是机器学习的一个分支。",
        "Transformer架构已成为自然语言处理的主流。",
        "大语言模型通过预训练获得了强大的语言能力。",
        "模型量化是减少模型大小和加速推理的重要技术。",
        "三值量化将权重映射到{-1, 0, 1}。",
        "后训练量化可以在不重训练的情况下压缩模型。",
        "可学习调制可以调整权重分布以减少信息损失。",
    ] * 70  # ~560 samples
    
    qwen3_catq.quantize_model(calibration_texts)
    qwen3_catq.save_quantized_model(args.output)
    
    print("\nEvaluating perplexity...")
    test_texts = [
        "神经网络是一种模拟人脑工作方式的计算模型。",
        "自然语言处理使计算机能够理解和生成人类语言。",
    ]
    ppl = qwen3_catq.evaluate_perplexity(test_texts)
    print(f"Perplexity: {ppl:.2f}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
