"""
GSQ Qwen3-0.6B Adapter
======================
Apply GSQ quantization to Qwen3-0.6B model.

FIXED: Uses forward hooks to capture real layer activations from calibration data.
"""

import torch
import torch.nn as nn
from typing import Optional, List, Dict, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer

from gsq_quantizer import GSQQuantizer, GSQConfig


class Qwen3GSQ:
    """
    Apply GSQ post-training quantization to Qwen3-0.6B.

    Quantizes all linear layers (except embeddings and lm_head) to the
    target bit-width using Gumbel-Softmax optimization.

    FIXED: Uses real calibration data propagated through the model.
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

    def get_quantizable_layers(self) -> Tuple[List[nn.Linear], List[str]]:
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

    def _prepare_calibration_data(self, calibration_texts: List[str]) -> torch.Tensor:
        """Tokenize calibration texts into input_ids."""
        inputs = self.tokenizer(
            calibration_texts,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        return inputs["input_ids"].to(self.device)

    def _get_layer_activations(self, layer: nn.Linear, calibration_input_ids: torch.Tensor) -> torch.Tensor:
        """
        Capture real input activations for a linear layer using forward hooks.

        Args:
            layer: The target Linear layer
            calibration_input_ids: Tokenized calibration data

        Returns:
            activations: [batch * seq_len, in_features] — real layer inputs
        """
        activations = []

        def hook_fn(module, input, output):
            # input is a tuple, take the first element
            inp = input[0]
            # Flatten to [batch * seq_len, in_features]
            if inp.dim() == 3:
                inp = inp.reshape(-1, inp.shape[-1])
            activations.append(inp.detach())

        handle = layer.register_forward_hook(hook_fn)

        with torch.no_grad():
            # Forward pass through the model
            self.model(calibration_input_ids)

        handle.remove()

        # Concatenate all captured activations
        all_activations = torch.cat(activations, dim=0)

        # Sample a subset for efficiency
        if all_activations.shape[0] > self.config.batch_size:
            indices = torch.randperm(all_activations.shape[0])[:self.config.batch_size]
            all_activations = all_activations[indices]

        return all_activations

    def quantize_model(self, calibration_texts: List[str]):
        """
        Quantize all quantizable layers using real calibration data.

        Args:
            calibration_texts: List of text strings for calibration
        """
        # Prepare calibration data
        calib_input_ids = self._prepare_calibration_data(calibration_texts)
        print(f"Calibration data shape: {calib_input_ids.shape}")

        layers, names = self.get_quantizable_layers()
        print(f"Found {len(layers)} layers to quantize.")

        for i, (layer, name) in enumerate(zip(layers, names)):
            print(f"\n[{i+1}/{len(layers)}] Quantizing {name}...")
            print(f"  Weight shape: {layer.weight.shape}")

            # Capture real input activations for this layer
            calib_input = self._get_layer_activations(layer, calib_input_ids)
            print(f"  Captured activations: {calib_input.shape}")

            # Quantize
            quantized_weight, scales = self.quantizer.quantize(layer.weight.data, calib_input)

            # Replace weight
            layer.weight.data = quantized_weight.to(self.device)
            print(f"  Done. Scales shape: {scales.shape}, range: [{scales.min():.4f}, {scales.max():.4f}]")

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
