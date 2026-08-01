#!/usr/bin/env python3
"""
Mock model validation for GyRot quantization.
Uses a small randomly-initialized model to verify all code paths are executable
when real model download fails due to network or resource constraints.
"""

import torch
import torch.nn as nn
from demo import CoRFIGQuantizer, GyRotLinear

class MockTransformerLayer(nn.Module):
    """Minimal transformer-like layer with q_proj Linear."""
    def __init__(self, hidden_size=512, num_heads=8):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        self.q_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.k_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.v_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.o_proj = nn.Linear(hidden_size, hidden_size, bias=False)
    
    def forward(self, x):
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)
        # Simplified attention
        attn = torch.softmax(q @ k.transpose(-2, -1) / (self.head_dim ** 0.5), dim=-1)
        out = attn @ v
        return self.o_proj(out)

class MockLM(nn.Module):
    """Small mock language model."""
    def __init__(self, vocab_size=1000, hidden_size=512, num_layers=2):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, hidden_size)
        self.layers = nn.ModuleList([
            MockTransformerLayer(hidden_size) for _ in range(num_layers)
        ])
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)
    
    def forward(self, input_ids):
        x = self.embed(input_ids)
        for layer in self.layers:
            x = x + layer(x)  # residual
        return self.lm_head(x)
    
    def generate(self, input_ids, max_new_tokens=10, **kwargs):
        """Greedy generation."""
        for _ in range(max_new_tokens):
            logits = self.forward(input_ids)
            next_token = logits[:, -1:].argmax(dim=-1)
            input_ids = torch.cat([input_ids, next_token], dim=1)
        return input_ids

def validate_mock():
    print("=" * 70)
    print(" GyRot Mock Model Validation")
    print("=" * 70)
    
    # Create mock model
    model = MockLM(vocab_size=1000, hidden_size=512, num_layers=2)
    model.eval()
    
    # Reference forward pass
    input_ids = torch.randint(0, 1000, (1, 10))
    with torch.no_grad():
        logits_ref = model.forward(input_ids)
    print(f"\nMock model created: {sum(p.numel() for p in model.parameters())} params")
    print(f"Reference logits shape: {logits_ref.shape}")
    
    # Quantize q_proj layers with GyRot
    gyrot = CoRFIGQuantizer(n_bits=4, group_size=128, coarse_block_size=512)
    quantized = 0
    for name, m in model.named_modules():
        if isinstance(m, nn.Linear) and 'q_proj' in name:
            w_q, meta = gyrot.quantize(m.weight.data)
            layer_idx = int(name.split(".")[1])
            model.layers[layer_idx].q_proj = GyRotLinear(m, w_q, meta)
            quantized += 1
            print(f"  Quantized {name}: {m.weight.shape}")
    print(f"\nTotal quantized layers: {quantized}")
    
    # Forward pass after quantization
    with torch.no_grad():
        logits_q = model.forward(input_ids)
    
    # Compare outputs
    mse = ((logits_ref - logits_q) ** 2).mean().item()
    max_diff = (logits_ref - logits_q).abs().max().item()
    print(f"\nOutput comparison:")
    print(f"  MSE: {mse:.6f}")
    print(f"  Max absolute diff: {max_diff:.6f}")
    
    # Test generation
    with torch.no_grad():
        generated = model.generate(input_ids, max_new_tokens=5)
    print(f"\nGeneration test: input shape {input_ids.shape} -> output shape {generated.shape}")
    print(f"Generated tokens: {generated[0].tolist()}")
    
    # Test inference with rotation
    print("\n--- Testing gyrot.inference() code path ---")
    x = torch.randn(1, 10, 512)
    for name, m in model.named_modules():
        if isinstance(m, GyRotLinear) and 'q_proj' in name:
            out = m(x)
            print(f"  {name} GyRotLinear output shape: {out.shape}")
            break
    
    print("\n" + "=" * 70)
    print(" Mock validation PASSED - all code paths executed successfully")
    print("=" * 70)

if __name__ == "__main__":
    validate_mock()
