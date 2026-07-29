#!/usr/bin/env python3
"""
Paper: 2607.25583v1 - How Small Can You Go? A Controlled Study of LoRA R
Auto-generated INT8 quantization demo
"""

import torch
import torch.nn as nn

class INT8Quantizer:
    def quantize(self, x):
        scale = x.abs().max() / 127.0
        x_q = torch.clamp(torch.round(x / scale), -128, 127)
        return x_q * scale

class INT8Linear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))
    
    def forward(self, x):
        quantizer = INT8Quantizer()
        w_q = quantizer.quantize(self.weight)
        return torch.matmul(x, w_q.t()) + self.bias

def demo():
    layer = INT8Linear(512, 256)
    x = torch.randn(4, 512)
    out = layer(x)
    print(f"INT8 quantized output: {out.shape}")

if __name__ == "__main__":
    demo()
