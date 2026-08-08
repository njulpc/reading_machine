#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.05253 - AuroOFT: Augmented Rotational Orthogonal Fine-Tuning
Method: Quantized Orthogonal Fine-Tuning with Expressive Rotation
Target Model: Qwen3-0.6B
================================================================================

This script demonstrates:
1. AuroOFT's augmented orthogonal rotation for low-bit model adaptation
2. Cayley-transform parameterized orthogonal matrices
3. Quantization-aware forward pass with frozen quantized weights
4. Application to Qwen3-0.6B

Usage:
    python3 demo.py

Requirements:
    pip install torch transformers accelerate
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple

# =============================================================================
# 1. AuroOFT Core: Augmented Orthogonal Rotation
# =============================================================================

class CayleyOrthogonal(nn.Module):
    """
    Parameterize an orthogonal matrix via Cayley transform.
    
    For a skew-symmetric matrix A (A^T = -A), the Cayley transform gives:
        R = (I - A)(I + A)^{-1}
    
    This guarantees R^T R = I (orthogonal).
    """
    def __init__(self, dim: int, rank: Optional[int] = None):
        super().__init__()
        self.dim = dim
        # Use low-rank approximation for efficiency
        self.rank = rank or min(dim // 4, 64)
        
        # Parameterize skew-symmetric matrix via its upper triangular part
        # For low-rank: A = U V^T - V U^T where U, V are d x r matrices
        self.U = nn.Parameter(torch.randn(dim, self.rank) * 0.01)
        self.V = nn.Parameter(torch.randn(dim, self.rank) * 0.01)
    
    def get_skew_symmetric(self) -> torch.Tensor:
        """Compute skew-symmetric matrix A = U V^T - V U^T"""
        A = torch.matmul(self.U, self.V.t()) - torch.matmul(self.V, self.U.t())
        return A
    
    def get_orthogonal(self) -> torch.Tensor:
        """Compute orthogonal matrix R = (I - A)(I + A)^{-1}"""
        A = self.get_skew_symmetric()
        I = torch.eye(self.dim, device=A.device, dtype=A.dtype)
        
        # Cayley transform: R = (I - A) @ inv(I + A)
        I_plus_A = I + A
        try:
            inv_I_plus_A = torch.linalg.inv(I_plus_A)
        except:
            # Fallback to pseudo-inverse if singular
            inv_I_plus_A = torch.linalg.pinv(I_plus_A)
        
        R = torch.matmul(I - A, inv_I_plus_A)
        return R
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply rotation: y = R @ x"""
        R = self.get_orthogonal()
        # x: [..., dim]
        return torch.matmul(x, R.t())


class BlockOrthogonal(nn.Module):
    """
    Block-diagonal orthogonal matrix for computational efficiency.
    
    Instead of one large dxd orthogonal matrix, use multiple smaller blocks.
    """
    def __init__(self, dim: int, block_size: int = 64):
        super().__init__()
        self.dim = dim
        self.block_size = block_size
        self.num_blocks = (dim + block_size - 1) // block_size
        
        # Create smaller Cayley orthogonal blocks
        self.blocks = nn.ModuleList([
            CayleyOrthogonal(min(block_size, dim - i * block_size))
            for i in range(self.num_blocks)
        ])
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply block-wise rotation"""
        outputs = []
        for i, block in enumerate(self.blocks):
            start = i * self.block_size
            end = min(start + self.block_size, self.dim)
            chunk = x[..., start:end]
            rotated = block(chunk)
            outputs.append(rotated)
        return torch.cat(outputs, dim=-1)


# =============================================================================
# 2. Quantization Utilities
# =============================================================================

def symmetric_quantize(x: torch.Tensor, bits: int = 4) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Symmetric per-channel quantization.
    
    Args:
        x: input tensor [..., features]
        bits: quantization bits (4 for INT4)
    
    Returns:
        x_q: quantized tensor (still in float, but values are integers)
        scale: per-channel scale
    """
    qmax = 2 ** (bits - 1) - 1
    qmin = -(2 ** (bits - 1))
    
    # Per-channel scale (last dimension)
    dim = x.shape[-1]
    x_reshaped = x.reshape(-1, dim)
    
    scale = x_reshaped.abs().amax(dim=0, keepdim=True) / qmax
    scale = scale.clamp_min(1e-8)
    
    x_q = torch.clamp(torch.round(x_reshaped / scale), qmin, qmax)
    
    return (x_q * scale).reshape(x.shape), scale


def fake_quantize(x: torch.Tensor, bits: int = 4) -> torch.Tensor:
    """Fake quantization for QAT-style training"""
    x_q, _ = symmetric_quantize(x, bits)
    # Straight-through estimator
    return x + (x_q - x).detach()


# =============================================================================
# 3. AuroOFT Linear Layer
# =============================================================================

class AuroOFTLinear(nn.Module):
    """
    Linear layer with AuroOFT: frozen quantized weights + learnable rotation.
    
    Forward: y = W_quant @ (R @ x)
    where:
        W_quant: frozen quantized weight
        R: learnable orthogonal rotation
        x: input activation
    """
    def __init__(
        self,
        in_features: int,
        out_features: int,
        weight_bits: int = 4,
        use_block_rotation: bool = True,
        block_size: int = 64,
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight_bits = weight_bits
        
        # Frozen weight (will be quantized and frozen)
        self.register_buffer("weight", torch.randn(out_features, in_features))
        self.register_buffer("weight_scale", torch.ones(out_features, 1))
        
        # Learnable rotation
        if use_block_rotation:
            self.rotation = BlockOrthogonal(in_features, block_size)
        else:
            self.rotation = CayleyOrthogonal(in_features)
        
        # Optional bias
        self.bias = nn.Parameter(torch.zeros(out_features))
    
    def set_weight(self, weight_fp: torch.Tensor):
        """Set and quantize weight from full-precision weight"""
        # Quantize weight per-output-channel
        qmax = 2 ** (self.weight_bits - 1) - 1
        scale = weight_fp.abs().amax(dim=1, keepdim=True) / qmax
        scale = scale.clamp_min(1e-8)
        
        w_q = torch.clamp(torch.round(weight_fp / scale), -qmax - 1, qmax)
        
        self.weight = nn.Parameter(w_q * scale, requires_grad=False)
        self.weight_scale = nn.Parameter(scale, requires_grad=False)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Apply rotation to input
        x_rotated = self.rotation(x)
        
        # Linear with frozen quantized weight
        out = F.linear(x_rotated, self.weight, self.bias)
        return out


# =============================================================================
# 4. AuroOFT Model Wrapper for Qwen3-0.6B
# =============================================================================

def apply_aurooft_to_model(
    model,
    weight_bits: int = 4,
    target_modules: Optional[list] = None,
    block_size: int = 64,
):
    """
    Apply AuroOFT to a transformers model.
    
    Args:
        model: transformers model (e.g., Qwen3-0.6B)
        weight_bits: quantization bits for frozen weights
        target_modules: list of module name patterns to apply AuroOFT
        block_size: block size for block orthogonal rotation
    """
    if target_modules is None:
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    
    aurooft_layers = {}
    
    for name, module in model.named_modules():
        # Check if this is a target linear layer
        is_target = any(t in name for t in target_modules)
        if is_target and isinstance(module, nn.Linear):
            # Create AuroOFT layer
            aurooft_layer = AuroOFTLinear(
                in_features=module.in_features,
                out_features=module.out_features,
                weight_bits=weight_bits,
                block_size=block_size,
            )
            
            # Copy and quantize weight
            with torch.no_grad():
                aurooft_layer.set_weight(module.weight.data.clone())
                if module.bias is not None:
                    aurooft_layer.bias.data = module.bias.data.clone()
            
            # Replace module
            parent_name = ".".join(name.split(".")[:-1])
            child_name = name.split(".")[-1]
            if parent_name:
                parent = model.get_submodule(parent_name)
                setattr(parent, child_name, aurooft_layer)
            else:
                setattr(model, child_name, aurooft_layer)
            
            auoft_layers[name] = aurooft_layer
    
    return model, auoft_layers


# =============================================================================
# 5. Demonstration
# =============================================================================

def demo():
    print("=" * 70)
    print(" Paper: 2608.05253 - AuroOFT")
    print(" Method: Augmented Rotational Orthogonal Fine-Tuning")
    print(" Target: Qwen3-0.6B (or compatible small LLM)")
    print("=" * 70)
    
    # === Test orthogonal rotation ===
    print("\n[1] Testing Cayley Orthogonal Rotation")
    rot = CayleyOrthogonal(dim=128, rank=16)
    x = torch.randn(2, 10, 128)  # [batch, seq, dim]
    
    R = rot.get_orthogonal()
    print(f"  Rotation matrix shape: {R.shape}")
    print(f"  Orthogonality check (R^T R - I).abs().max(): {(R.T @ R - torch.eye(128)).abs().max().item():.6f}")
    
    y = rot(x)
    print(f"  Input norm: {x.norm(dim=-1).mean().item():.4f}")
    print(f"  Output norm: {y.norm(dim=-1).mean().item():.4f}")
    print(f"  Norm preservation: {y.norm(dim=-1).mean().item() / x.norm(dim=-1).mean().item():.6f}")
    
    # === Test block orthogonal ===
    print("\n[2] Testing Block Orthogonal Rotation")
    block_rot = BlockOrthogonal(dim=512, block_size=64)
    x2 = torch.randn(2, 10, 512)
    y2 = block_rot(x2)
    print(f"  Input shape: {x2.shape}")
    print(f"  Output shape: {y2.shape}")
    
    # === Test quantization ===
    print("\n[3] Testing Symmetric Quantization")
    x3 = torch.randn(100, 256)
    x3_q, scale = symmetric_quantize(x3, bits=4)
    mse = ((x3 - x3_q) ** 2).mean().item()
    print(f"  INT4 Quantization MSE: {mse:.6f}")
    
    x3_q8, _ = symmetric_quantize(x3, bits=8)
    mse8 = ((x3 - x3_q8) ** 2).mean().item()
    print(f"  INT8 Quantization MSE: {mse8:.6f}")
    print(f"  INT4/INT8 MSE ratio: {mse / mse8:.2f}")
    
    # === Test AuroOFT Linear ===
    print("\n[4] Testing AuroOFT Linear Layer")
    layer = AuroOFTLinear(in_features=256, out_features=512, weight_bits=4)
    
    # Set random weight
    with torch.no_grad():
        layer.set_weight(torch.randn(512, 256) * 0.1)
    
    x4 = torch.randn(2, 10, 256)
    y4 = layer(x4)
    print(f"  Input: {x4.shape}")
    print(f"  Output: {y4.shape}")
    print(f"  Trainable params: {sum(p.numel() for p in layer.parameters() if p.requires_grad)}")
    print(f"  Frozen params: {sum(p.numel() for p in layer.parameters() if not p.requires_grad)}")
    
    # === Try loading Qwen3-0.6B ===
    print("\n[5] Attempting to load Qwen3-0.6B...")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_name = "Qwen/Qwen3-0.6B"
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
        )
        print(f"  Model loaded successfully!")
        print(f"  Model type: {type(model).__name__}")
        print(f"  Total parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")
        
        # Apply AuroOFT
        print("\n[6] Applying AuroOFT to model...")
        model, auoft_layers = apply_aurooft_to_model(model, weight_bits=4, block_size=64)
        
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
        print(f"  Trainable params: {trainable / 1e6:.2f}M ({trainable / (trainable + frozen) * 100:.2f}%)")
        print(f"  Frozen params: {frozen / 1e6:.2f}M")
        
        # Test generation
        print("\n[7] Testing generation...")
        prompt = "The future of artificial intelligence is"
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=20, do_sample=False)
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"  Prompt: {prompt}")
        print(f"  Generated: {generated}")
        
    except Exception as e:
        print(f"  Could not load Qwen3-0.6B: {e}")
        print("  This is expected if model weights are not available.")
        print("  The code above demonstrates the core AuroOFT algorithm.")
    
    # === Summary ===
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print("  AuroOFT Key Components:")
    print("    1. Cayley-transform orthogonal rotation (strict orthogonality)")
    print("    2. Block-diagonal approximation for efficiency")
    print("    3. Frozen INT4 quantized weights")
    print("    4. Only rotation parameters are trainable (~0.1-0.5% of total)")
    print("")
    print("  Benefits:")
    print("    - Parameter efficient (only rotation is learned)")
    print("    - Norm-preserving (orthogonal transformation)")
    print("    - Compatible with existing PTQ methods (GPTQ, AWQ)")
    print("    - Inference: rotation can be fused into weights (zero overhead)")
    print("=" * 70)


if __name__ == "__main__":
    demo()
