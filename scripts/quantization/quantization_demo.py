#!/usr/bin/env python3
"""
================================================================================
Quantization Research Toolkit - Complete Runnable Demo
================================================================================

This script demonstrates quantization methods from arXiv papers on a 
synthetic transformer model (mimicking Qwen3-0.6B architecture).

Papers implemented:
- 2607.25870: Angle-Aware QAT (INT4 with self-distillation)
- 2607.24953: 2D Block FP4 (transposition-invariant)
- 2607.25451: RTN Quantization (4/8-bit)
- 2607.25180: INT8 Per-Channel Quantization
- 2607.24981: Integer-Only Operations (GELU, Softmax, LayerNorm)

Usage:
    python quantization_demo.py --demo

Requirements:
    pip install torch numpy

Author: AI Assistant
Date: 2026-07-29
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import time
import json
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class QuantConfig:
    """Quantization configuration"""
    weight_bits: int = 4          # Weight quantization bits
    activation_bits: int = 8      # Activation quantization bits
    group_size: int = 128         # Group size for RTN
    block_size: int = 32          # Block size for FP4
    per_channel: bool = True      # Per-channel quantization
    use_stochastic_rounding: bool = True
    lambda_repel: float = 1.0     # For angle-aware loss


# =============================================================================
# 1. Base Quantizer (Abstract Interface)
# =============================================================================

class BaseQuantizer:
    """Base class for all quantizers"""
    
    def __init__(self, bits: int = 8):
        self.bits = bits
        self.qmax = 2 ** (bits - 1) - 1
        self.qmin = -(2 ** (bits - 1))
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError
    
    def dequantize(self, x_q: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        return x_q * scale


# =============================================================================
# 2. RTN Quantizer (Paper 2607.25451: Bits and Memories)
# =============================================================================

class RTNQuantizer(BaseQuantizer):
    """
    Round-to-Nearest Quantizer
    Paper: "Bits and Memories: Measuring Verbatim Extraction Across LLM Quantization"
    
    Simple group-wise symmetric quantization.
    """
    
    def __init__(self, bits: int = 4, group_size: int = 128):
        super().__init__(bits)
        self.group_size = group_size
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Quantize tensor using RTN.
        
        Args:
            x: Input tensor of any shape
            
        Returns:
            x_dq: Dequantized tensor (same shape as x)
            scales: Scale factors per group
            zeros: Zero points (always 0 for symmetric quantization)
        """
        orig_shape = x.shape
        x_flat = x.flatten()
        
        # Pad to group_size multiple
        pad_size = (self.group_size - x_flat.numel() % self.group_size) % self.group_size
        if pad_size > 0:
            x_flat = F.pad(x_flat, (0, pad_size))
        
        x_blocks = x_flat.reshape(-1, self.group_size)
        
        # Symmetric quantization: scale = max(|x|) / qmax
        w_max = x_blocks.abs().amax(dim=1, keepdim=True)
        scales = (w_max / self.qmax).clamp_min(1e-8)
        
        # Quantize and dequantize
        x_q = torch.clamp(torch.round(x_blocks / scales), self.qmin, self.qmax)
        x_dq = (x_q * scales).flatten()[:x.numel()].reshape(orig_shape)
        
        return x_dq, scales.squeeze(), torch.zeros_like(scales.squeeze())
    
    def quantize_model(self, model: nn.Module):
        """Apply RTN quantization to all Linear layers in a model"""
        count = 0
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                w_dq, scales, zeros = self.quantize(module.weight.data)
                module.weight.data = w_dq
                module.register_buffer('quant_scales', scales)
                module.register_buffer('quant_zeros', zeros)
                count += 1
        print(f"[RTN] Quantized {count} Linear layers to {self.bits}-bit")


# =============================================================================
# 3. INT8 Per-Channel Quantizer (Paper 2607.25180: Bekko Embedding)
# =============================================================================

class INT8Quantizer(BaseQuantizer):
    """
    INT8 Per-Channel Quantizer
    Paper: "Bekko Embedding: Parameter-Efficient Multilingual Retrieval with Ultra-Compact Encoders"
    
    Per-channel (row-wise for weights) symmetric INT8 quantization.
    """
    
    def __init__(self, per_channel: bool = True, channel_dim: int = 0):
        super().__init__(bits=8)
        self.per_channel = per_channel
        self.channel_dim = channel_dim
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """INT8 quantization"""
        if self.per_channel and x.ndim >= 2:
            # For weight matrices [out_features, in_features], quantize per output channel
            dims = list(range(x.ndim))
            dims.remove(self.channel_dim)
            w_max = x.abs().amax(dim=dims, keepdim=True)
        else:
            w_max = x.abs().max()
        
        scale = (w_max / 127.0).clamp_min(1e-8)
        x_q = torch.clamp(torch.round(x / scale), -128, 127)
        x_dq = x_q * scale
        
        return x_dq, scale
    
    def fake_quantize(self, x: torch.Tensor) -> torch.Tensor:
        """
        Fake quantization for QAT (Quantization-Aware Training).
        Uses Straight-Through Estimator (STE) for gradients.
        """
        x_q, scale = self.quantize(x)
        # STE: forward uses quantized value, backward passes gradient through
        return x + (x_q - x).detach()


# =============================================================================
# 4. 2D Block FP4 Quantizer (Paper 2607.24953: Stable FP4 Training)
# =============================================================================

class FP4Quantizer(BaseQuantizer):
    """
    2D Block FP4 Quantizer with Transposition Invariance
    Paper: "Stable FP4 Training via Transposition-Invariant Block Quantization"
    
    Key innovation: 2D square blocks ensure S(X) = S(X^T), eliminating
    forward-backward scale inconsistency.
    """
    
    def __init__(self, bits: int = 4, block_size: int = 32, use_stochastic_rounding: bool = True):
        super().__init__(bits=4)
        self.block_size = block_size
        self.use_stochastic_rounding = use_stochastic_rounding
        self.fp4_range = 6.0  # FP4 E2M1 representable range
    
    def _stochastic_round(self, x: torch.Tensor) -> torch.Tensor:
        """Stochastic rounding: E[round(x)] = x"""
        floor = torch.floor(x)
        prob = x - floor
        rand = torch.rand_like(x)
        return floor + (rand < prob).float()
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        2D block FP4 quantization with transposition invariance.
        
        Args:
            x: 2D tensor [m, n]
            
        Returns:
            x_dq: Dequantized tensor
            scales: Block scales
        """
        assert x.ndim >= 2, "2D block quantization requires at least 2D tensor"
        
        orig_shape = x.shape
        m, n = x.shape[0], x.shape[1]
        
        # Pad to block_size multiples
        pad_m = (self.block_size - m % self.block_size) % self.block_size
        pad_n = (self.block_size - n % self.block_size) % self.block_size
        x_pad = F.pad(x, (0, pad_n, 0, pad_m)) if (pad_m > 0 or pad_n > 0) else x
        
        m_p, n_p = x_pad.shape[0], x_pad.shape[1]
        num_b_m = m_p // self.block_size
        num_b_n = n_p // self.block_size
        
        # Reshape to blocks: [num_b_m, num_b_n, block_size, block_size]
        x_blocks = x_pad.reshape(num_b_m, self.block_size, num_b_n, self.block_size).permute(0, 2, 1, 3)
        
        # Truncation-free scaling: S = 2^ceil(log2(2*M / Q_range))
        M = x_blocks.abs().amax(dim=(-2, -1), keepdim=True)
        log_scale = torch.ceil(torch.log2(2 * M / self.fp4_range))
        log_scale = torch.clamp(log_scale, min=-126, max=127)
        scales = 2 ** log_scale
        scales = scales.clamp_min(1e-8)
        
        # Quantize
        x_scaled = x_blocks / scales
        if self.use_stochastic_rounding:
            x_q = self._stochastic_round(x_scaled)
        else:
            x_q = torch.round(x_scaled)
        x_q = torch.clamp(x_q, -self.fp4_range, self.fp4_range)
        
        # Dequantize and reshape back
        x_dq = x_q * scales
        x_out = x_dq.permute(0, 2, 1, 3).reshape(m_p, n_p)[:m, :n]
        
        return x_out, scales.squeeze()
    
    def verify_transpose_invariance(self, x: torch.Tensor) -> bool:
        """Verify S(X) == S(X^T)"""
        _, s1 = self.quantize(x)
        _, s2 = self.quantize(x.t())
        # Compare max scales across blocks
        return torch.allclose(s1.flatten()[:s2.numel()], s2.flatten(), atol=1e-5)


# =============================================================================
# 5. Angle-Aware QAT Loss (Paper 2607.25870: VAD to the Bone)
# =============================================================================

class AngleAwareQATLoss(nn.Module):
    """
    Angle-Aware Self-Distillation Loss for QAT
    Paper: "VAD to the Bone: Ultra-Tiny Speech Activity Detection for Edge Deployment"
    
    Freezes full-precision classifier weights as prototypes and optimizes
    the angular geometry between features and prototypes.
    """
    
    def __init__(self, lambda_repel: float = 1.0, num_classes: int = 2):
        super().__init__()
        self.lambda_repel = lambda_repel
        self.num_classes = num_classes
    
    def forward(self, features: torch.Tensor, targets: torch.Tensor, 
                frozen_prototypes: torch.Tensor) -> torch.Tensor:
        """
        Args:
            features: [B, d] quantized backbone penultimate features
            targets: [B] class labels
            frozen_prototypes: [C, d] frozen full-precision classifier weights
            
        Returns:
            loss: scalar tensor
        """
        B = features.size(0)
        
        # L2 normalize
        f_norm = F.normalize(features, p=2, dim=1)           # [B, d]
        w_norm = F.normalize(frozen_prototypes, p=2, dim=1)  # [C, d]
        
        # Cosine similarities
        similarities = torch.mm(f_norm, w_norm.t())  # [B, C]
        
        losses = []
        for i in range(B):
            f_i = f_norm[i]
            y_i = targets[i].item()
            
            # Term 1: Align to target prototype (maximize cosine)
            cos_target = torch.dot(f_i, w_norm[y_i])
            align_loss = 1.0 - cos_target
            
            # Term 2: Repel from non-target prototypes (hinge)
            non_target_sims = [similarities[i, c] for c in range(self.num_classes) if c != y_i]
            if non_target_sims:
                max_non_target = max(non_target_sims)
                repel_loss = torch.clamp(max_non_target, min=0.0)
            else:
                repel_loss = torch.tensor(0.0, device=features.device)
            
            losses.append(align_loss + self.lambda_repel * repel_loss)
        
        return torch.stack(losses).mean()


# =============================================================================
# 6. Integer-Only Operations (Paper 2607.24981: I-LW-DETR)
# =============================================================================

class IntegerGELU(nn.Module):
    """
    Integer GELU Approximation
    Paper: "Enabling Fully Integer-Only Inference for Lightweight Detection Transformers"
    """
    
    def __init__(self, num_bits: int = 8, use_lut: bool = True):
        super().__init__()
        self.num_bits = num_bits
        self.qmax = 2 ** (num_bits - 1) - 1
        self.use_lut = use_lut
        
        if use_lut:
            self.register_buffer('lut', self._build_lut())
    
    def _build_lut(self) -> torch.Tensor:
        """Build GELU lookup table for integer range"""
        x_vals = torch.arange(-128, 128, dtype=torch.float32)
        # GELU(x) = 0.5 * x * (1 + erf(x / sqrt(2)))
        gelu_vals = 0.5 * x_vals * (1 + torch.erf(x_vals / math.sqrt(2)))
        scale = gelu_vals.abs().max() / self.qmax
        gelu_q = torch.clamp(torch.round(gelu_vals / scale), -self.qmax - 1, self.qmax)
        return gelu_q
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.use_lut:
            # Map to LUT indices
            x_idx = torch.clamp(x + 128, 0, 255).long()
            return self.lut[x_idx]
        else:
            # Piecewise linear approximation
            return torch.where(x > 0, x, torch.zeros_like(x))


class IntegerSoftmax(nn.Module):
    """
    Integer Softmax using shift-based approximation (Shiftmax)
    """
    
    def __init__(self, dim: int = -1, num_bits: int = 8):
        super().__init__()
        self.dim = dim
        self.num_bits = num_bits
        self.scale = 8  # Shift factor
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Subtract max for stability
        x_max = x.amax(dim=self.dim, keepdim=True)
        x_shifted = x - x_max
        
        # exp(x) ≈ 2^(x / scale) using bit shifts
        exp_shift = x_shifted.long() // self.scale
        exp_shift = exp_shift.clamp(0, self.num_bits - 1)
        # Use torch.pow for float-compatible computation
        exp_approx = torch.clamp(torch.pow(torch.tensor(2.0), exp_shift.float()), 1, 2**self.num_bits - 1)
        
        # Normalize
        sum_exp = exp_approx.sum(dim=self.dim, keepdim=True).clamp_min(1)
        out = (exp_approx * (2**self.num_bits - 1)) // sum_exp
        
        return out


# =============================================================================
# 7. Synthetic Transformer Model (Mimicking Qwen3-0.6B)
# =============================================================================

class SyntheticTransformerLayer(nn.Module):
    """A simplified transformer layer for demonstration"""
    
    def __init__(self, hidden_size: int = 768, num_heads: int = 12, intermediate_size: int = 2048):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        
        # Self-attention
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        self.o_proj = nn.Linear(hidden_size, hidden_size)
        
        # FFN
        self.gate_proj = nn.Linear(hidden_size, intermediate_size)
        self.up_proj = nn.Linear(hidden_size, intermediate_size)
        self.down_proj = nn.Linear(intermediate_size, hidden_size)
        
        # Norm
        self.input_layernorm = nn.LayerNorm(hidden_size)
        self.post_attention_layernorm = nn.LayerNorm(hidden_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, seq_len, _ = x.shape
        
        # Self-attention
        residual = x
        x = self.input_layernorm(x)
        
        q = self.q_proj(x).view(B, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        attn = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, v).transpose(1, 2).contiguous().view(B, seq_len, self.hidden_size)
        out = self.o_proj(out)
        x = residual + out
        
        # FFN (SwiGLU-like)
        residual = x
        x = self.post_attention_layernorm(x)
        gate = F.silu(self.gate_proj(x))
        up = self.up_proj(x)
        ffn_out = self.down_proj(gate * up)
        x = residual + ffn_out
        
        return x


class SyntheticQwenModel(nn.Module):
    """
    Synthetic model mimicking Qwen3-0.6B architecture.
    Much smaller for fast demo (configurable layers).
    """
    
    def __init__(self, vocab_size: int = 32000, hidden_size: int = 768, 
                 num_layers: int = 4, num_heads: int = 12, intermediate_size: int = 2048):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        
        self.embed_tokens = nn.Embedding(vocab_size, hidden_size)
        self.layers = nn.ModuleList([
            SyntheticTransformerLayer(hidden_size, num_heads, intermediate_size)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(hidden_size)
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        x = self.embed_tokens(input_ids)
        
        for layer in self.layers:
            x = layer(x)
        
        x = self.norm(x)
        logits = self.lm_head(x)
        return logits
    
    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())
    
    def get_model_size_mb(self) -> float:
        return sum(p.numel() * p.element_size() for p in self.parameters()) / (1024**2)


# =============================================================================
# 8. Quantization Pipeline
# =============================================================================

class QuantizationPipeline:
    """
    Complete quantization pipeline for evaluation.
    """
    
    def __init__(self, model: nn.Module, device: str = "cpu"):
        self.model = model.to(device)
        self.device = device
        self.original_size_mb = model.get_model_size_mb() if hasattr(model, 'get_model_size_mb') else 0
    
    def apply_rtn(self, bits: int = 4, group_size: int = 128):
        """Apply RTN quantization"""
        quantizer = RTNQuantizer(bits=bits, group_size=group_size)
        quantizer.quantize_model(self.model)
        return self._compute_stats(bits)
    
    def apply_int8(self):
        """Apply INT8 per-channel quantization"""
        quantizer = INT8Quantizer(per_channel=True)
        count = 0
        for module in self.model.modules():
            if isinstance(module, nn.Linear):
                w_dq, scale = quantizer.quantize(module.weight.data)
                module.weight.data = w_dq
                count += 1
        print(f"[INT8] Quantized {count} Linear layers")
        return self._compute_stats(8)
    
    def apply_fp4(self, block_size: int = 32):
        """Apply 2D block FP4 quantization"""
        quantizer = FP4Quantizer(bits=4, block_size=block_size)
        count = 0
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear) and module.weight.ndim >= 2:
                try:
                    w_dq, scales = quantizer.quantize(module.weight.data)
                    module.weight.data = w_dq
                    count += 1
                except Exception as e:
                    print(f"  [FP4] Skip {name}: {e}")
        print(f"[FP4] Quantized {count} Linear layers with 2D block (size={block_size})")
        return self._compute_stats(4)
    
    def _compute_stats(self, bits: int) -> Dict:
        """Compute compression statistics"""
        quantized_size = self.original_size_mb * (bits / 16)
        return {
            "bits": bits,
            "original_size_mb": self.original_size_mb,
            "quantized_size_mb": quantized_size,
            "compression_ratio": self.original_size_mb / quantized_size
        }
    
    def evaluate_inference(self, batch_size: int = 4, seq_len: int = 128, num_runs: int = 10):
        """Measure inference latency"""
        self.model.eval()
        dummy_input = torch.randint(0, 32000, (batch_size, seq_len), device=self.device)
        
        # Warmup
        with torch.no_grad():
            for _ in range(3):
                _ = self.model(dummy_input)
        
        # Measure
        times = []
        with torch.no_grad():
            for _ in range(num_runs):
                start = time.time()
                _ = self.model(dummy_input)
                times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        return {
            "avg_latency_ms": avg_time * 1000,
            "min_latency_ms": min(times) * 1000,
            "max_latency_ms": max(times) * 1000,
            "throughput_samples_per_sec": batch_size / avg_time
        }


# =============================================================================
# 9. Demonstration
# =============================================================================

def print_separator(title: str):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def run_demo():
    """Run complete quantization demonstration"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    
    # Create synthetic model
    print_separator("Creating Synthetic Model (Mimicking Qwen3-0.6B)")
    model = SyntheticQwenModel(
        vocab_size=32000,
        hidden_size=768,
        num_layers=4,  # Smaller for demo
        num_heads=12,
        intermediate_size=2048
    )
    print(f"Parameters: {model.count_parameters():,}")
    print(f"Model size (FP16): {model.get_model_size_mb():.2f} MB")
    
    # Baseline evaluation
    print_separator("FP16 Baseline")
    pipeline = QuantizationPipeline(model, device)
    fp16_stats = pipeline.evaluate_inference()
    print(f"Latency: {fp16_stats['avg_latency_ms']:.2f} ms")
    print(f"Throughput: {fp16_stats['throughput_samples_per_sec']:.2f} samples/sec")
    
    # Test data for verification
    test_input = torch.randint(0, 32000, (2, 64), device=device)
    with torch.no_grad():
        fp16_output = model(test_input)
    
    results = {
        "model": "SyntheticQwen (demo)",
        "baseline": {
            "size_mb": pipeline.original_size_mb,
            "latency_ms": fp16_stats['avg_latency_ms'],
            "throughput": fp16_stats['throughput_samples_per_sec']
        },
        "methods": {}
    }
    
    # RTN 4-bit
    print_separator("RTN 4-bit Quantization (Paper 2607.25451)")
    model_rtn4 = SyntheticQwenModel(vocab_size=32000, hidden_size=768, num_layers=4, 
                                     num_heads=12, intermediate_size=2048).to(device)
    pipeline_rtn4 = QuantizationPipeline(model_rtn4, device)
    stats = pipeline_rtn4.apply_rtn(bits=4, group_size=128)
    perf = pipeline_rtn4.evaluate_inference()
    
    with torch.no_grad():
        rtn4_output = model_rtn4(test_input)
    
    # Verify outputs are close
    diff = (fp16_output - rtn4_output).abs().mean().item()
    
    results["methods"]["rtn4"] = {
        **stats,
        "latency_ms": perf['avg_latency_ms'],
        "throughput": perf['throughput_samples_per_sec'],
        "output_diff": diff
    }
    print(f"Compressed: {stats['quantized_size_mb']:.2f} MB (ratio: {stats['compression_ratio']:.1f}x)")
    print(f"Latency: {perf['avg_latency_ms']:.2f} ms")
    print(f"Output diff vs FP16: {diff:.4f}")
    
    # RTN 8-bit
    print_separator("RTN 8-bit Quantization")
    model_rtn8 = SyntheticQwenModel(vocab_size=32000, hidden_size=768, num_layers=4,
                                     num_heads=12, intermediate_size=2048).to(device)
    pipeline_rtn8 = QuantizationPipeline(model_rtn8, device)
    stats = pipeline_rtn8.apply_rtn(bits=8, group_size=128)
    perf = pipeline_rtn8.evaluate_inference()
    
    with torch.no_grad():
        rtn8_output = model_rtn8(test_input)
    diff = (fp16_output - rtn8_output).abs().mean().item()
    
    results["methods"]["rtn8"] = {
        **stats,
        "latency_ms": perf['avg_latency_ms'],
        "throughput": perf['throughput_samples_per_sec'],
        "output_diff": diff
    }
    print(f"Compressed: {stats['quantized_size_mb']:.2f} MB (ratio: {stats['compression_ratio']:.1f}x)")
    print(f"Output diff vs FP16: {diff:.4f}")
    
    # INT8
    print_separator("INT8 Per-Channel Quantization (Paper 2607.25180)")
    model_int8 = SyntheticQwenModel(vocab_size=32000, hidden_size=768, num_layers=4,
                                     num_heads=12, intermediate_size=2048).to(device)
    pipeline_int8 = QuantizationPipeline(model_int8, device)
    stats = pipeline_int8.apply_int8()
    perf = pipeline_int8.evaluate_inference()
    
    with torch.no_grad():
        int8_output = model_int8(test_input)
    diff = (fp16_output - int8_output).abs().mean().item()
    
    results["methods"]["int8"] = {
        **stats,
        "latency_ms": perf['avg_latency_ms'],
        "throughput": perf['throughput_samples_per_sec'],
        "output_diff": diff
    }
    print(f"Compressed: {stats['quantized_size_mb']:.2f} MB (ratio: {stats['compression_ratio']:.1f}x)")
    print(f"Output diff vs FP16: {diff:.4f}")
    
    # FP4
    print_separator("FP4 2D Block Quantization (Paper 2607.24953)")
    model_fp4 = SyntheticQwenModel(vocab_size=32000, hidden_size=768, num_layers=4,
                                    num_heads=12, intermediate_size=2048).to(device)
    pipeline_fp4 = QuantizationPipeline(model_fp4, device)
    stats = pipeline_fp4.apply_fp4(block_size=32)
    perf = pipeline_fp4.evaluate_inference()
    
    with torch.no_grad():
        fp4_output = model_fp4(test_input)
    diff = (fp16_output - fp4_output).abs().mean().item()
    
    results["methods"]["fp4"] = {
        **stats,
        "latency_ms": perf['avg_latency_ms'],
        "throughput": perf['throughput_samples_per_sec'],
        "output_diff": diff
    }
    print(f"Compressed: {stats['quantized_size_mb']:.2f} MB (ratio: {stats['compression_ratio']:.1f}x)")
    print(f"Output diff vs FP16: {diff:.4f}")
    
    # Verify FP4 transpose invariance
    print_separator("Verifying FP4 Transpose Invariance")
    quantizer = FP4Quantizer(bits=4, block_size=32)
    test_matrix = torch.randn(64, 64)
    is_invariant = quantizer.verify_transpose_invariance(test_matrix)
    print(f"S(X) == S(X^T): {is_invariant} {'✅' if is_invariant else '❌'}")
    results["fp4_transpose_invariant"] = is_invariant
    
    # Angle-Aware Loss Demo
    print_separator("Angle-Aware QAT Loss Demo (Paper 2607.25870)")
    loss_fn = AngleAwareQATLoss(lambda_repel=1.0, num_classes=10)
    features = torch.randn(16, 128, requires_grad=True)
    targets = torch.randint(0, 10, (16,))
    prototypes = torch.randn(10, 128)
    loss = loss_fn(features, targets, prototypes)
    loss.backward()
    print(f"Angle-aware loss: {loss.item():.4f}")
    print(f"Feature gradients computed: {'✅' if features.grad is not None else '❌'}")
    results["angle_aware_loss"] = loss.item()
    
    # Integer Operations Demo
    print_separator("Integer-Only Operations Demo (Paper 2607.24981)")
    int_gelu = IntegerGELU(num_bits=8, use_lut=True)
    int_softmax = IntegerSoftmax(dim=-1, num_bits=8)
    
    x_int = torch.randint(-128, 127, (1, 64))
    gelu_out = int_gelu(x_int)
    softmax_out = int_softmax(x_int.float())
    
    print(f"Integer GELU output range: [{gelu_out.min()}, {gelu_out.max()}]")
    print(f"Integer Softmax output range: [{softmax_out.min()}, {softmax_out.max()}]")
    results["integer_ops"] = {
        "gelu_range": [gelu_out.min().item(), gelu_out.max().item()],
        "softmax_range": [softmax_out.min().item(), softmax_out.max().item()]
    }
    
    # Summary
    print_separator("SUMMARY")
    print(f"{'Method':<12} {'Bits':<8} {'Size(MB)':<12} {'Ratio':<8} {'Latency(ms)':<14} {'Diff':<10}")
    print("-" * 70)
    print(f"{'FP16':<12} {'16':<8} {results['baseline']['size_mb']:<12.2f} {'1.0x':<8} "
          f"{results['baseline']['latency_ms']:<14.2f} {'-':<10}")
    for method, data in results["methods"].items():
        print(f"{method.upper():<12} {data['bits']:<8} {data['quantized_size_mb']:<12.2f} "
              f"{data['compression_ratio']:<8.1f} {data['latency_ms']:<14.2f} {data['output_diff']:<10.4f}")
    
    # Save results
    with open("quantization_demo_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: quantization_demo_results.json")
    
    return results


if __name__ == "__main__":
    run_demo()
