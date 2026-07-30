"""
GSQ Demo Script
===============
Demonstrate GSQ quantization on Qwen3-0.6B.
"""

import argparse
import torch
from qwen3_gsq import Qwen3GSQ
from gsq_quantizer import GSQConfig


def main():
    parser = argparse.ArgumentParser(description="GSQ Quantization for Qwen3-0.6B")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="Model path")
    parser.add_argument("--bits", default="2", choices=["ternary", "2", "3", "4"], help="Bit-width")
    parser.add_argument("--group-size", type=int, default=128, help="Quantization group size")
    parser.add_argument("--init-method", default="gptq", choices=["gptq", "rtn"], help="Warm-start prior")
    parser.add_argument("--epochs", type=int, default=20, help="Number of optimization epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Calibration batch size")
    parser.add_argument("--output", default="./gsq_qwen3_0.6b", help="Output path")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="Device")
    args = parser.parse_args()
    
    # Parse bits
    bits = args.bits if args.bits == "ternary" else int(args.bits)
    
    print("=" * 60)
    print("GSQ: Gumbel-Softmax Quantization")
    print("Paper: arXiv:2604.18556")
    print("=" * 60)
    print(f"Config:")
    print(f"  Model: {args.model}")
    print(f"  Bits: {bits}")
    print(f"  Group size: {args.group_size}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Device: {args.device}")
    print()
    
    # Create config
    config = GSQConfig(
        bits=bits,
        group_size=args.group_size,
        init_method=args.init_method,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
    )
    
    # Initialize
    qwen3_gsq = Qwen3GSQ(model_path=args.model, config=config)
    
    # Calibration texts (in practice, use domain-relevant data)
    calibration_texts = [
        "人工智能正在改变我们的世界。",
        "深度学习是机器学习的一个分支。",
        "Transformer架构已成为自然语言处理的主流。",
        "大语言模型通过预训练获得了强大的语言能力。",
        "模型量化是减少模型大小和加速推理的重要技术。",
        "Gumbel-Softmax是一种用于离散采样的松弛技术。",
        "后训练量化可以在不重训练的情况下压缩模型。",
        "混合专家模型通过稀疏激活实现了高效推理。",
    ] * 10  # Repeat for more calibration samples
    
    # Quantize
    qwen3_gsq.quantize_model(calibration_texts)
    
    # Save
    qwen3_gsq.save_quantized_model(args.output)
    
    # Evaluate
    print("\nEvaluating perplexity...")
    test_texts = [
        "神经网络是一种模拟人脑工作方式的计算模型。",
        "自然语言处理使计算机能够理解和生成人类语言。",
    ]
    ppl = qwen3_gsq.evaluate_perplexity(test_texts)
    print(f"Perplexity: {ppl:.2f}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
