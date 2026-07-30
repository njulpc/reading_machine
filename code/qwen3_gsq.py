"""
GSQ Qwen3-0.6B Adapter
======================
Apply GSQ quantization to Qwen3-0.6B model.
"""

import torch
import torch.nn as nn
from typing import Optional, List, Dict
from transformers import AutoModelForCausalLM, AutoTokenizer

from gsq_quantizer import GSQQuantizer, GSQConfig


class Qwen3GSQ:
    """
    Apply GSQ post-training quantization to Qwen3-0.6B.
    
    Quantizes all linear layers (except embeddings and lm_head) to the
    target bit-width using Gumbel-Softmax optimization.
    """
    
    def __init__(self, model_path: str = "Qwen/Qwen3-0.6B", config: Optional[GSQConfig] = None):
        self.config = config or GSQConfig()
        self.device = torch.device(self.config.device)
        
        print(f"Loading Qwen3-0.6B from {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if self.config.device == "cuda" else torch.float32,
            trust_remote_code=True,
        ).to(self.device)
        self.model.eval()
        
        self.quantizer = GSQQuantizer(self.config)
        print("Model loaded successfully.")
    
    def get_quantizable_layers(self) -> List[nn.Linear]:
        """Get list of linear layers to quantize (excluding embeddings and lm_head)."""
        layers = []
        names = []
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                # Skip embedding and lm_head layers
                if "embed" in name.lower() or "lm_head" in name.lower():
                    continue
                layers.append(module)
                names.append(name)
        return layers, names
    
    def quantize_model(self, calibration_texts: List[str]):
        """
        Quantize all quantizable layers using calibration data.
        
        Args:
            calibration_texts: List of text strings for calibration
        """
        # Prepare calibration input
        calib_inputs = []
        for text in calibration_texts:
            tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            calib_inputs.append(tokens["input_ids"].to(self.device))
        
        layers, names = self.get_quantizable_layers()
        print(f"Found {len(layers)} layers to quantize.")
        
        for i, (layer, name) in enumerate(zip(layers, names)):
            print(f"\n[{i+1}/{len(layers)}] Quantizing {name}...")
            print(f"  Shape: {layer.weight.shape}")
            
            # Get calibration input for this layer
            # In practice, you'd compute the actual input activations
            # Here we use a simplified approach with random input matching the layer's input dim
            with torch.no_grad():
                calib_input = torch.randn(
                    self.config.batch_size, 
                    layer.weight.shape[1],
                    device=self.device,
                    dtype=layer.weight.dtype,
                )
            
            # Quantize
            quantized_weight, scale = self.quantizer.quantize(layer.weight.data, calib_input)
            
            # Replace weight
            layer.weight.data = quantized_weight.to(self.device)
            print(f"  Done. Scale: {scale.item():.6f}")
        
        print("\nQuantization complete!")
    
    def save_quantized_model(self, output_path: str):
        """Save the quantized model."""
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        print(f"Quantized model saved to {output_path}")
    
    def evaluate_perplexity(self, texts: List[str]) -> float:
        """Evaluate perplexity on a set of texts."""
        self.model.eval()
        total_loss = 0.0
        total_tokens = 0
        
        with torch.no_grad():
            for text in texts:
                tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                input_ids = tokens["input_ids"].to(self.device)
                
                outputs = self.model(input_ids, labels=input_ids)
                loss = outputs.loss
                n_tokens = input_ids.numel()
                
                total_loss += loss.item() * n_tokens
                total_tokens += n_tokens
        
        avg_loss = total_loss / total_tokens
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        return perplexity
