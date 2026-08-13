#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.12239 - HAMP-LIC
Title: Hessian-Aware Mixed-Precision Post-Training Quantization
Core Method: Hessian trace + task-aware sensitivity + global bit allocation
================================================================================

This script demonstrates:
1. Hessian trace estimation for layer sensitivity
2. Mixed-precision bit allocation under global constraint
3. Block-wise reconstruction for error suppression

Usage:
    python3 demo.py

Requirements:
    pip install torch
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import copy

# =============================================================================
# 1. Hessian Trace Estimator
# =============================================================================

class HessianTraceEstimator:
    """
    Estimate Hessian trace using Hutchinson's stochastic trace estimator.
    
    tr(H) ≈ E[v^T H v] where v ~ N(0, I)
    
    Hv product computed via automatic differentiation.
    """
    
    def __init__(self, num_samples=10):
        self.num_samples = num_samples
    
    def estimate_trace(self, model, loss_fn, data_input, data_target):
        """
        Estimate Hessian trace for each parameter group (layer).
        
        Returns:
            sensitivities: dict mapping layer_name -> trace_value
        """
        model.eval()
        sensitivities = {}
        
        # Get all trainable parameters grouped by layer
        param_groups = {}
        for name, param in model.named_parameters():
            if param.requires_grad and 'weight' in name:
                layer_name = name.rsplit('.', 1)[0]
                if layer_name not in param_groups:
                    param_groups[layer_name] = []
                param_groups[layer_name].append((name, param))
        
        for layer_name, params in param_groups.items():
            traces = []
            for _ in range(self.num_samples):
                # Sample random vector
                v = []
                for _, param in params:
                    v.append(torch.randn_like(param))
                
                # Compute Hv product
                model.zero_grad()
                output = model(data_input)
                loss = loss_fn(output, data_target)
                
                # First gradient
                grads = torch.autograd.grad(loss, [p for _, p in params], create_graph=True)
                
                # Compute v^T H v = v^T d(grad)/d(param)
                grad_v = sum((g * vi).sum() for g, vi in zip(grads, v))
                
                # Second gradient gives Hv
                Hv = torch.autograd.grad(grad_v, [p for _, p in params], retain_graph=False)
                
                # v^T H v
                trace_est = sum((vi * hvi).sum().item() for vi, hvi in zip(v, Hv))
                traces.append(trace_est)
            
            sensitivities[layer_name] = sum(traces) / len(traces)
        
        return sensitivities


# =============================================================================
# 2. Mixed-Precision Quantizer
# =============================================================================

class MixedPrecisionQuantizer:
    """
    Mixed-precision PTQ with Hessian-aware sensitivity.
    """
    
    def __init__(self, sensitivities, total_bits_budget, min_bits=2, max_bits=8):
        """
        Args:
            sensitivities: dict mapping layer_name -> sensitivity_score
            total_bits_budget: total bit budget across all layers
            min_bits: minimum bit width per layer
            max_bits: maximum bit width per layer
        """
        self.sensitivities = sensitivities
        self.total_bits_budget = total_bits_budget
        self.min_bits = min_bits
        self.max_bits = max_bits
    
    def allocate_bits(self, layer_sizes):
        """
        Greedy bit allocation based on sensitivity.
        
        Args:
            layer_sizes: dict mapping layer_name -> num_elements
            
        Returns:
            bit_assignment: dict mapping layer_name -> bit_width
        """
        # Normalize sensitivities
        max_sens = max(self.sensitivities.values())
        min_sens = min(self.sensitivities.values())
        norm_sens = {
            k: (v - min_sens) / (max_sens - min_sens + 1e-8)
            for k, v in self.sensitivities.items()
        }
        
        # Start with all layers at min_bits
        bit_assignment = {k: self.min_bits for k in self.sensitivities}
        used_bits = sum(bit_assignment[k] * layer_sizes[k] for k in bit_assignment)
        
        # Greedy: repeatedly increase bit width of most sensitive layer
        while used_bits < self.total_bits_budget:
            best_layer = None
            best_benefit = -1
            
            for layer_name in bit_assignment:
                if bit_assignment[layer_name] >= self.max_bits:
                    continue
                
                # Benefit of increasing this layer by 1 bit
                benefit = norm_sens[layer_name] * layer_sizes[layer_name]
                cost = layer_sizes[layer_name]  # 1 extra bit per element
                
                if used_bits + cost <= self.total_bits_budget and benefit > best_benefit:
                    best_benefit = benefit
                    best_layer = layer_name
            
            if best_layer is None:
                break
            
            bit_assignment[best_layer] += 1
            used_bits += layer_sizes[best_layer]
        
        return bit_assignment
    
    def quantize_layer(self, weight, bit_width):
        """Quantize a single weight tensor."""
        if bit_width >= 16:
            return weight
        
        num_levels = 2 ** bit_width
        w_min = weight.min()
        w_max = weight.max()
        scale = (w_max - w_min) / (num_levels - 1)
        
        if scale < 1e-8:
            return weight
        
        quant = torch.round((weight - w_min) / scale).clamp(0, num_levels - 1)
        return quant * scale + w_min
    
    def quantize_model(self, model, bit_assignment):
        """Apply mixed-precision quantization to model."""
        quantized_state = {}
        for name, param in model.named_parameters():
            if 'weight' in name:
                layer_name = name.rsplit('.', 1)[0]
                if layer_name in bit_assignment:
                    bits = bit_assignment[layer_name]
                    quantized_state[name] = self.quantize_layer(param.data, bits)
                else:
                    quantized_state[name] = param.data
            else:
                quantized_state[name] = param.data
        
        return quantized_state


# =============================================================================
# 3. Block-wise Reconstruction
# =============================================================================

class BlockReconstructor:
    """
    Block-wise reconstruction to minimize output error.
    """
    
    def __init__(self, num_iters=100, lr=1e-3):
        self.num_iters = num_iters
        self.lr = lr
    
    def reconstruct(self, layer, calib_input, calib_output_fp, bit_width):
        """
        Reconstruct quantized layer to match FP output.
        
        Args:
            layer: quantized linear layer
            calib_input: calibration inputs [N, in_features]
            calib_output_fp: FP outputs [N, out_features]
            bit_width: target bit width
        """
        weight = layer.weight.data.clone()
        
        # Quantize
        num_levels = 2 ** bit_width
        w_min = weight.min()
        w_max = weight.max()
        scale = (w_max - w_min) / (num_levels - 1)
        
        if scale < 1e-8:
            return layer
        
        # Fine-tune scale and zero-point
        scale_param = nn.Parameter(torch.tensor(scale))
        zp_param = nn.Parameter(torch.tensor(w_min))
        
        optimizer = torch.optim.Adam([scale_param, zp_param], lr=self.lr)
        
        for _ in range(self.num_iters):
            optimizer.zero_grad()
            
            # Quantize and dequantize
            quant = torch.round((weight - zp_param) / scale_param.clamp_min(1e-8)).clamp(0, num_levels - 1)
            w_q = quant * scale_param + zp_param
            
            # Forward
            out = F.linear(calib_input, w_q, layer.bias)
            loss = F.mse_loss(out, calib_output_fp)
            
            loss.backward()
            optimizer.step()
        
        # Apply reconstructed quantization
        with torch.no_grad():
            quant = torch.round((weight - zp_param) / scale_param.clamp_min(1e-8)).clamp(0, num_levels - 1)
            layer.weight.data = quant * scale_param + zp_param
        
        return layer


# =============================================================================
# 4. Demo Model
# =============================================================================

class DemoNet(nn.Module):
    """Simple CNN for demonstration."""
    
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 10)
        self.pool = nn.AdaptiveAvgPool2d(8)
    
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


# =============================================================================
# 5. Demo
# =============================================================================

def demo():
    print("="*70)
    print(" Paper: 2608.12239 - HAMP-LIC")
    print(" Method: Hessian-Aware Mixed-Precision PTQ")
    print("="*70)
    
    # Create model
    print("\n[1] Creating demo model...")
    model = DemoNet()
    model.eval()
    
    # Generate synthetic calibration data
    torch.manual_seed(42)
    calib_input = torch.randn(16, 3, 32, 32)
    calib_target = torch.randint(0, 10, (16,))
    
    # Step 1: Estimate Hessian traces
    print("\n[2] Estimating Hessian traces...")
    hessian_est = HessianTraceEstimator(num_samples=5)
    loss_fn = nn.CrossEntropyLoss()
    
    # For speed, use smaller data for Hessian estimation
    hess_input = calib_input[:4]
    hess_target = calib_target[:4]
    
    sensitivities = hessian_est.estimate_trace(model, loss_fn, hess_input, hess_target)
    
    print("  Layer sensitivities:")
    for name, sens in sorted(sensitivities.items(), key=lambda x: -x[1]):
        print(f"    {name}: {sens:.4f}")
    
    # Step 2: Bit allocation
    print("\n[3] Allocating mixed precision bits...")
    
    layer_sizes = {}
    for name, param in model.named_parameters():
        if 'weight' in name:
            layer_name = name.rsplit('.', 1)[0]
            if layer_name in sensitivities:
                layer_sizes[layer_name] = param.numel()
    
    total_elements = sum(layer_sizes.values())
    target_avg_bits = 4.0
    total_budget = int(total_elements * target_avg_bits)
    
    mpq = MixedPrecisionQuantizer(sensitivities, total_budget, min_bits=2, max_bits=8)
    bit_assignment = mpq.allocate_bits(layer_sizes)
    
    print("  Bit assignment:")
    for name, bits in sorted(bit_assignment.items()):
        print(f"    {name}: {bits} bits")
    
    # Step 3: Quantize
    print("\n[4] Applying mixed-precision quantization...")
    quantized_state = mpq.quantize_model(model, bit_assignment)
    
    # Create quantized model
    model_quant = DemoNet()
    model_quant.load_state_dict(quantized_state)
    model_quant.eval()
    
    # Step 4: Evaluate
    print("\n[5] Evaluation")
    with torch.no_grad():
        out_fp = model(calib_input)
        out_q = model_quant(calib_input)
        
        mse = ((out_fp - out_q) ** 2).mean().item()
        
        # Accuracy
        acc_fp = (out_fp.argmax(dim=1) == calib_target).float().mean().item()
        acc_q = (out_q.argmax(dim=1) == calib_target).float().mean().item()
    
    print(f"  Output MSE: {mse:.6f}")
    print(f"  FP accuracy: {acc_fp:.2%}")
    print(f"  Quant accuracy: {acc_q:.2%}")
    
    # Compression ratio
    orig_bits = sum(p.numel() * 32 for p in model.parameters())
    quant_bits = sum(layer_sizes.get(name.rsplit('.', 1)[0], 32) * p.numel() 
                     for name, p in model.named_parameters() if 'weight' in name)
    # Add non-weight params at 32 bits
    quant_bits += sum(p.numel() * 32 for name, p in model.named_parameters() if 'weight' not in name)
    
    # Simplified compression calculation
    weight_bits = sum(bit_assignment.get(name.rsplit('.', 1)[0], 32) * p.numel()
                      for name, p in model.named_parameters() if 'weight' in name)
    other_bits = sum(32 * p.numel() for name, p in model.named_parameters() if 'weight' not in name)
    total_quant_bits = weight_bits + other_bits
    
    compression = orig_bits / total_quant_bits
    print(f"\n  Compression ratio: {compression:.2f}x")
    print(f"  Average bit width: {weight_bits / sum(layer_sizes.values()):.1f} bits")
    
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    print("HAMP-LIC demonstrates Hessian-aware mixed-precision quantization")
    print("that allocates more bits to sensitive layers for better accuracy")
    print("under a global compression budget.")
    print("="*70)


if __name__ == "__main__":
    demo()
