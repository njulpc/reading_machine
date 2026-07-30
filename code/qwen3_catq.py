"""
CAT-Q Qwen3-0.6B Adapter
=========================
Apply CAT-Q ternary quantization to Qwen3-0.6B.

Fixed versus the previous compact demo: calibration inputs are real layer
activations captured with forward hooks from tokenized text, not random noise.
After a layer is quantized, later layers are captured through the already
quantized prefix, so accumulated quantization error is visible.
"""

import torch
import torch.nn as nn
from typing import Optional, List, Tuple

from catq_quantizer import CATQQuantizer, CATQConfig


class Qwen3CATQ:
    """Apply CAT-Q post-training ternary quantization to Qwen3-0.6B."""

    def __init__(self, model_path: str = "Qwen/Qwen3-0.6B", config: Optional[CATQConfig] = None):
        self.config = config or CATQConfig()
        self.device = torch.device(self.config.device)

        from transformers import AutoModelForCausalLM, AutoTokenizer

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

        self.quantizer = CATQQuantizer(self.config)
        print("Model loaded successfully.")

    def get_quantizable_layers(self) -> Tuple[List[nn.Linear], List[str]]:
        """Linear layers to quantize (excluding embeddings and lm_head)."""
        layers, names = [], []
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                if "embed" in name.lower() or "lm_head" in name.lower():
                    continue
                layers.append(module)
                names.append(name)
        return layers, names

    def _prepare_calibration_data(self, calibration_texts: List[str]):
        inputs = self.tokenizer(
            calibration_texts[: self.config.num_calibration_samples],
            return_tensors="pt",
            truncation=True,
            max_length=self.config.seq_length,
            padding=True,
        )
        return inputs["input_ids"].to(self.device), inputs["attention_mask"].to(self.device)

    def _get_layer_activations(self, layer: nn.Linear, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Capture real inputs to `layer` with a forward hook."""
        activations = []

        def hook_fn(module, inputs, output):
            inp = inputs[0]
            if inp.dim() == 3:
                inp = inp.reshape(-1, inp.shape[-1])
            activations.append(inp.detach())

        handle = layer.register_forward_hook(hook_fn)
        with torch.no_grad():
            self.model(input_ids=input_ids, attention_mask=attention_mask)
        handle.remove()

        all_activations = torch.cat(activations, dim=0)
        max_rows = max(int(self.config.activation_rows), 1)
        if all_activations.shape[0] > max_rows:
            idx = torch.randperm(all_activations.shape[0], device=all_activations.device)[:max_rows]
            all_activations = all_activations[idx]
        return all_activations

    def quantize_model(self, calibration_texts: List[str]):
        input_ids, attention_mask = self._prepare_calibration_data(calibration_texts)
        print(f"Calibration input_ids shape: {tuple(input_ids.shape)}")

        layers, names = self.get_quantizable_layers()
        print(f"Found {len(layers)} layers to quantize.")
        if self.config.window_size != 1:
            print(
                "Note: CAT-Q's SliderQuant-style multi-layer window is not plumbed "
                "into this compact adapter; using window_size=1 per-layer output reconstruction."
            )

        for i, (layer, name) in enumerate(zip(layers, names)):
            print(f"\n[{i + 1}/{len(layers)}] Quantizing {name}...")
            print(f"  Shape: {tuple(layer.weight.shape)}")
            calib_input = self._get_layer_activations(layer, input_ids, attention_mask)
            print(f"  Captured activations: {tuple(calib_input.shape)}")

            qw, alpha, delta = self.quantizer.quantize_layer(layer.weight.data, calib_input)
            layer.weight.data = qw.to(self.device, dtype=layer.weight.dtype)
            print(f"  Done. Alpha(mean)={alpha:.4f}, Delta(mean)={delta:.4f}")

        print("\nTernary quantization complete!")

    def save_quantized_model(self, output_path: str):
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        print(f"Ternary model saved to {output_path}")

    def evaluate_perplexity(self, texts: List[str]) -> float:
        self.model.eval()
        total_loss, total_tokens = 0.0, 0
        with torch.no_grad():
            for text in texts:
                tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                input_ids = tokens["input_ids"].to(self.device)
                outputs = self.model(input_ids, labels=input_ids)
                n_tokens = input_ids.numel()
                total_loss += outputs.loss.item() * n_tokens
                total_tokens += n_tokens
        return torch.exp(torch.tensor(total_loss / total_tokens)).item()
