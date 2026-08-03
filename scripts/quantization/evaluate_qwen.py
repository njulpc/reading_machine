#!/usr/bin/env python3
"""
Qwen3-0.6B Quantization Evaluation
====================================
验证论文中的量化方法在 Qwen3-0.6B 上的效果。

支持的量化方法:
- RTN4/RTN8: Round-to-Nearest (论文2607.25451)
- FP4: 2D Block FP4 (论文2607.24953)
- INT8: Per-channel INT8 (论文2607.25180)
- GPTQ4: GPTQ-style 4-bit

使用方法:
    python evaluate_qwen.py --method rtn4 --eval_file eval_texts.txt
"""

import torch
import torch.nn as nn
import math
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# 导入量化工具包
import sys
sys.path.insert(0, str(Path(__file__).parent))
from quantization_toolkit import (
    RTNQuantizer, INT8Quantizer, FP4Quantizer,
    AngleAwareQATLoss, IntegerGELU, IntegerSoftmax,
    QuantizedModelEvaluator
)


class QwenQuantizationPipeline:
    """
    Qwen3-0.6B 量化管道
    
    实现流程:
    1. 加载 Qwen3-0.6B (FP16)
    2. 应用选择的量化方法
    3. 评估困惑度 (perplexity)
    4. 比较不同方法的压缩率和精度损失
    """
    
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B", device: str = "cuda"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.original_size_mb = 0
        
        self._load_model()
    
    def _load_model(self):
        """加载 Qwen3-0.6B 模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            print(f"Loading {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # 使用 FP16 加载以节省显存
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map=self.device,
                trust_remote_code=True
            )
            
            # 计算原始模型大小
            self.original_size_mb = sum(
                p.numel() * 2  # FP16 = 2 bytes
                for p in self.model.parameters()
            ) / (1024 ** 2)
            
            print(f"Original model size: {self.original_size_mb:.1f} MB (FP16)")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Note: Qwen3-0.6B requires 'transformers>=4.40.0' and model access.")
            print("Falling back to demo mode with synthetic model...")
            self._create_demo_model()
    
    def _create_demo_model(self):
        """创建演示模型 (当真实模型不可用时)"""
        print("Creating demo transformer model...")
        
        # 模拟 Qwen3-0.6B 的架构参数
        vocab_size = 151936
        hidden_size = 1536
        num_layers = 28
        num_heads = 12
        intermediate_size = 8960
        
        # 创建简化模型用于演示
        class DemoTransformer(nn.Module):
            def __init__(self, vocab_size, hidden_size, num_layers, intermediate_size):
                super().__init__()
                self.embed = nn.Embedding(vocab_size, hidden_size)
                self.layers = nn.ModuleList([
                    DemoTransformerLayer(hidden_size, intermediate_size)
                    for _ in range(num_layers)
                ])
                self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)
                self.hidden_size = hidden_size
            
            def forward(self, input_ids, labels=None):
                x = self.embed(input_ids)
                for layer in self.layers:
                    x = layer(x)
                logits = self.lm_head(x)
                
                if labels is not None:
                    loss = nn.functional.cross_entropy(
                        logits.view(-1, logits.size(-1)),
                        labels.view(-1)
                    )
                    return type('Output', (), {'loss': loss, 'logits': logits})()
                return logits
        
        class DemoTransformerLayer(nn.Module):
            def __init__(self, hidden_size, intermediate_size):
                super().__init__()
                self.attn = nn.MultiheadAttention(hidden_size, num_heads=8, batch_first=True)
                self.mlp = nn.Sequential(
                    nn.Linear(hidden_size, intermediate_size),
                    nn.GELU(),
                    nn.Linear(intermediate_size, hidden_size)
                )
                self.norm1 = nn.LayerNorm(hidden_size)
                self.norm2 = nn.LayerNorm(hidden_size)
            
            def forward(self, x):
                x = x + self.attn(self.norm1(x), self.norm1(x), self.norm1(x))[0]
                x = x + self.mlp(self.norm2(x))
                return x
        
        self.model = DemoTransformer(vocab_size, hidden_size, num_layers, intermediate_size)
        self.model = self.model.to(self.device)
        
        # 模拟tokenizer
        class DemoTokenizer:
            def __init__(self):
                self.vocab_size = vocab_size
                self.pad_token_id = 0
            
            def __call__(self, text, return_tensors=None, **kwargs):
                tokens = [ord(c) % self.vocab_size for c in text[:100]]
                if return_tensors == "pt":
                    return type('Tokens', (), {'input_ids': torch.tensor([tokens])})()
                return tokens
        
        self.tokenizer = DemoTokenizer()
        
        self.original_size_mb = sum(
            p.numel() * 2 for p in self.model.parameters()
        ) / (1024 ** 2)
        print(f"Demo model size: {self.original_size_mb:.1f} MB")
    
    def apply_quantization(self, method: str) -> Dict:
        """
        应用量化方法
        
        Args:
            method: 量化方法名称
        
        Returns:
            量化结果统计
        """
        quantizers = {
            "rtn4": RTNQuantizer(bits=4, group_size=128),
            "rtn8": RTNQuantizer(bits=8, group_size=128),
            "fp4": FP4Quantizer(bits=4, block_size=32),
            "int8": INT8Quantizer(per_channel=True),
        }
        
        if method not in quantizers:
            raise ValueError(f"Unknown method: {method}. Choose from {list(quantizers.keys())}")
        
        quantizer = quantizers[method]
        print(f"\nApplying {method} quantization...")
        
        # 应用量化
        if isinstance(quantizer, RTNQuantizer):
            quantizer.quantize_model(self.model)
            quant_type = "RTN"
        elif isinstance(quantizer, INT8Quantizer):
            # INT8 per-channel量化
            for name, module in self.model.named_modules():
                if isinstance(module, nn.Linear):
                    w_dq, scale = quantizer.quantize(module.weight.data)
                    module.weight.data = w_dq
                    module.register_buffer('quant_scale', scale)
            quant_type = "INT8"
        elif isinstance(quantizer, FP4Quantizer):
            # FP4 2D block量化
            for name, module in self.model.named_modules():
                if isinstance(module, nn.Linear) and module.weight.ndim >= 2:
                    try:
                        w_dq, scales = quantizer.quantize(module.weight.data)
                        module.weight.data = w_dq
                    except Exception as e:
                        print(f"  Skip {name}: {e}")
            quant_type = "FP4"
        
        # 计算量化后大小
        if method in ["rtn4", "fp4"]:
            bits = 4
        elif method in ["rtn8", "int8"]:
            bits = 8
        else:
            bits = 16
        
        quantized_size_mb = self.original_size_mb * (bits / 16)
        compression_ratio = self.original_size_mb / quantized_size_mb
        
        return {
            "method": method,
            "quant_type": quant_type,
            "bits": bits,
            "original_size_mb": self.original_size_mb,
            "quantized_size_mb": quantized_size_mb,
            "compression_ratio": compression_ratio,
        }
    
    def evaluate_perplexity(self, texts: List[str], max_length: int = 512) -> float:
        """
        评估困惑度
        
        Args:
            texts: 评估文本列表
            max_length: 最大序列长度
        
        Returns:
            平均困惑度
        """
        if self.model is None:
            return float('inf')
        
        self.model.eval()
        total_loss = 0.0
        total_tokens = 0
        
        for text in texts:
            try:
                # 编码文本
                if hasattr(self.tokenizer, 'encode'):
                    tokens = self.tokenizer.encode(text, return_tensors="pt")
                else:
                    tokens = self.tokenizer(text, return_tensors="pt").input_ids
                
                tokens = tokens.to(self.device)
                
                # 截断
                if tokens.size(1) > max_length:
                    tokens = tokens[:, :max_length]
                
                with torch.no_grad():
                    outputs = self.model(tokens, labels=tokens)
                    loss = outputs.loss if hasattr(outputs, 'loss') else outputs
                    
                    # 累计
                    num_tokens = tokens.size(1)
                    total_loss += loss.item() * num_tokens
                    total_tokens += num_tokens
            
            except Exception as e:
                print(f"  Error evaluating text: {e}")
                continue
        
        if total_tokens == 0:
            return float('inf')
        
        avg_loss = total_loss / total_tokens
        perplexity = math.exp(avg_loss)
        
        return perplexity
    
    def run_full_evaluation(
        self,
        methods: List[str],
        eval_texts: List[str],
        output_file: str = "results.json"
    ) -> Dict:
        """
        运行完整的量化评估
        
        Args:
            methods: 要评估的量化方法列表
            eval_texts: 评估文本
            output_file: 结果输出文件
        
        Returns:
            所有结果的字典
        """
        results = {
            "model": self.model_name,
            "eval_samples": len(eval_texts),
            "methods": {}
        }
        
        # 1. 评估原始模型 (FP16)
        print("\n" + "="*60)
        print("Evaluating FP16 baseline...")
        print("="*60)
        
        fp16_ppl = self.evaluate_perplexity(eval_texts)
        results["fp16_baseline"] = {
            "perplexity": fp16_ppl,
            "size_mb": self.original_size_mb
        }
        print(f"FP16 Perplexity: {fp16_ppl:.2f}")
        
        # 2. 评估每种量化方法
        for method in methods:
            print("\n" + "="*60)
            print(f"Evaluating {method}...")
            print("="*60)
            
            try:
                # 需要重新加载模型（因为量化会修改权重）
                self._load_model()
                
                # 应用量化
                quant_result = self.apply_quantization(method)
                
                # 评估困惑度
                ppl = self.evaluate_perplexity(eval_texts)
                quant_result["perplexity"] = ppl
                
                # 计算相对FP16的损失
                if fp16_ppl > 0:
                    ppl_increase = ((ppl - fp16_ppl) / fp16_ppl) * 100
                    quant_result["ppl_increase_pct"] = ppl_increase
                
                results["methods"][method] = quant_result
                
                print(f"  Perplexity: {ppl:.2f}")
                print(f"  Size: {quant_result['quantized_size_mb']:.1f} MB")
                print(f"  Compression: {quant_result['compression_ratio']:.1f}x")
                
            except Exception as e:
                print(f"  FAILED: {e}")
                results["methods"][method] = {"error": str(e)}
        
        # 3. 保存结果
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        return results
    
    def print_summary(self, results: Dict):
        """打印结果摘要"""
        print("\n" + "="*60)
        print("QUANTIZATION EVALUATION SUMMARY")
        print("="*60)
        print(f"Model: {results['model']}")
        print(f"Eval samples: {results['eval_samples']}")
        print()
        
        # Baseline
        fp16 = results.get("fp16_baseline", {})
        print(f"FP16 Baseline:")
        print(f"  Perplexity: {fp16.get('perplexity', 'N/A'):.2f}")
        print(f"  Size: {fp16.get('size_mb', 'N/A'):.1f} MB")
        print()
        
        # Quantized methods
        print("Quantized Methods:")
        print(f"{'Method':<10} {'Bits':<6} {'PPL':<10} {'Size(MB)':<12} {'Ratio':<8} {'Loss%':<8}")
        print("-" * 60)
        
        for method, data in results.get("methods", {}).items():
            if "error" in data:
                print(f"{method:<10} FAILED: {data['error']}")
                continue
            
            bits = data.get('bits', 'N/A')
            ppl = data.get('perplexity', 0)
            size = data.get('quantized_size_mb', 0)
            ratio = data.get('compression_ratio', 0)
            loss = data.get('ppl_increase_pct', 0)
            
            print(f"{method:<10} {bits:<6} {ppl:<10.2f} {size:<12.1f} {ratio:<8.1f} {loss:<8.1f}")


def load_eval_texts(file_path: str) -> List[str]:
    """加载评估文本"""
    if not Path(file_path).exists():
        # 使用默认评估文本
        return [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Quantization reduces the precision of neural network weights.",
            "Large language models have revolutionized natural language processing.",
            "Edge deployment requires efficient model compression techniques.",
        ]
    
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate quantization methods on Qwen3-0.6B"
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-0.6B",
        help="Model name or path"
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["rtn4", "rtn8", "int8"],
        choices=["rtn4", "rtn8", "fp4", "int8", "gptq4"],
        help="Quantization methods to evaluate"
    )
    parser.add_argument(
        "--eval_file",
        default="",
        help="Path to evaluation texts file (one per line)"
    )
    parser.add_argument(
        "--output",
        default="quantization_results.json",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use demo mode (synthetic model)"
    )
    args = parser.parse_args()
    
    # 加载评估文本
    eval_texts = load_eval_texts(args.eval_file)
    print(f"Loaded {len(eval_texts)} evaluation texts")
    
    # 创建评估管道
    pipeline = QwenQuantizationPipeline(
        model_name=args.model if not args.demo else "demo",
        device=args.device
    )
    
    # 运行评估
    results = pipeline.run_full_evaluation(
        methods=args.methods,
        eval_texts=eval_texts,
        output_file=args.output
    )
    
    # 打印摘要
    pipeline.print_summary(results)


if __name__ == "__main__":
    main()
