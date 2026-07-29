#!/usr/bin/env python3
"""
================================================================================
Paper: 2607.25870 - VAD to the Bone
Title: Ultra-Tiny Speech Activity Detection for Edge Deployment
Core Method: Angle-Aware Self-Distillation QAT + Structured Pruning
================================================================================

This script demonstrates:
1. Per-Layer Structured Pruning with multi-objective optimization
2. Self-Distillation fine-tuning (pruned model learns from frozen teacher)
3. Angle-Aware QAT: freeze classifier prototypes, optimize feature angles

Usage:
    python3 demo.py

Requirements:
    pip install torch
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


# =============================================================================
# 1. Angle-Aware Self-Distillation QAT Loss
# =============================================================================

class AngleAwareLoss(nn.Module):
    """
    Angle-Aware Self-Distillation Loss for Quantization-Aware Training.
    
    Key insight from the paper:
    - Freeze the full-precision classifier weights as PROTOTYPES
    - Optimize quantized features to align with their target prototype's angle
    - Repel from non-target prototypes (hinge loss)
    
    This is more stable than standard QAT because:
    - No need to train a separate teacher model
    - The frozen prototypes provide fixed angular anchors
    - Angle geometry is more robust to quantization noise than magnitude
    """
    
    def __init__(self, num_classes: int = 2, lambda_repel: float = 1.0):
        super().__init__()
        self.num_classes = num_classes
        self.lambda_repel = lambda_repel
    
    def forward(self, features, targets, frozen_prototypes):
        """
        Args:
            features: [B, d] quantized backbone penultimate features
            targets: [B] class labels
            frozen_prototypes: [C, d] frozen FP classifier weights
        
        Returns:
            loss: scalar
        """
        B = features.size(0)
        
        # L2 normalize for cosine similarity
        f_norm = F.normalize(features, p=2, dim=1)           # [B, d]
        w_norm = F.normalize(frozen_prototypes, p=2, dim=1)  # [C, d]
        
        # All pairwise cosine similarities
        similarities = torch.mm(f_norm, w_norm.t())  # [B, C]
        
        losses = []
        for i in range(B):
            f_i = f_norm[i]
            y_i = targets[i].item()
            
            # === TERM 1: Align to target prototype ===
            # Maximize cos(f_i, w_target) => minimize (1 - cos)
            cos_target = torch.dot(f_i, w_norm[y_i])
            align_loss = 1.0 - cos_target
            
            # === TERM 2: Repel from non-target prototypes ===
            # Only penalize if a non-target is too close
            non_target_sims = []
            for c in range(self.num_classes):
                if c != y_i:
                    non_target_sims.append(similarities[i, c])
            
            if non_target_sims:
                max_non_target = max(non_target_sims)
                repel_loss = torch.clamp(max_non_target, min=0.0)
            else:
                repel_loss = torch.tensor(0.0, device=features.device)
            
            losses.append(align_loss + self.lambda_repel * repel_loss)
        
        return torch.stack(losses).mean()


# =============================================================================
# 2. Structured Pruning (Per-Layer Ratios)
# =============================================================================

def structured_prune_layer(weight, pruning_ratio, importance_fn='l1'):
    """
    Structured channel pruning for a single conv/linear layer.
    
    Args:
        weight: weight tensor
        pruning_ratio: fraction of channels to remove (0.0 - 0.95)
        importance_fn: 'l1' or 'l2' norm for importance scoring
    
    Returns:
        keep_indices: indices of channels to keep
    """
    if weight.ndim < 2:
        return torch.arange(weight.size(0))
    
    # Compute importance per output channel
    if importance_fn == 'l1':
        importance = weight.abs().sum(dim=tuple(range(1, weight.ndim)))
    else:  # l2
        importance = (weight ** 2).sum(dim=tuple(range(1, weight.ndim)))
    
    num_keep = max(1, int(weight.size(0) * (1 - pruning_ratio)))
    keep_indices = torch.argsort(importance, descending=True)[:num_keep]
    
    return keep_indices


def apply_structured_pruning(model, pruning_ratios):
    """
    Apply per-layer structured pruning to a model.
    
    Args:
        model: nn.Module
        pruning_ratios: dict of {layer_name: ratio}
    
    Returns:
        pruned_model: model with pruned layers
        param_count: total parameter count after pruning
    """
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            ratio = pruning_ratios.get(name, 0.0)
            if ratio > 0:
                keep_idx = structured_prune_layer(module.weight.data, ratio)
                
                # Prune output channels
                module.weight.data = module.weight.data[keep_idx]
                if module.bias is not None:
                    module.bias.data = module.bias.data[keep_idx]
                
                # Update layer dimensions
                if isinstance(module, nn.Linear):
                    module.out_features = len(keep_idx)
                elif isinstance(module, nn.Conv2d):
                    module.out_channels = len(keep_idx)
    
    # Handle subsequent layer input dimensions
    # (Simplified: in practice need dependency graph like torch-pruning)
    
    param_count = sum(p.numel() for p in model.parameters())
    return model, param_count


# =============================================================================
# 3. Self-Distillation Fine-tuning
# =============================================================================

def self_distillation_finetune(student, teacher, data_loader, epochs=8, lr=1e-3, T=4.0):
    """
    Fine-tune pruned model (student) using frozen teacher.
    
    Loss = CE(y_pred, y_true) + alpha * KL(student_logits/T, teacher_logits/T)
    """
    optimizer = torch.optim.SGD(student.parameters(), lr=lr, momentum=0.9)
    
    for epoch in range(epochs):
        total_loss = 0
        for x, y in data_loader:
            student_logits = student(x)
            
            with torch.no_grad():
                teacher_logits = teacher(x)
            
            # Cross-entropy on true labels
            ce_loss = F.cross_entropy(student_logits, y)
            
            # KL divergence from teacher (temperature scaled)
            kl_loss = F.kl_div(
                F.log_softmax(student_logits / T, dim=-1),
                F.softmax(teacher_logits / T, dim=-1),
                reduction='batchmean'
            ) * (T * T)
            
            loss = ce_loss + 0.5 * kl_loss
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"  Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(data_loader):.4f}")
    
    return student


# =============================================================================
# 4. Complete Pipeline Demo
# =============================================================================

class TinySpeechCNN(nn.Module):
    """
    Ultra-tiny CNN for speech activity detection.
    Inspired by kiloVAD from the paper.
    """
    
    def __init__(self, n_mels=64, num_classes=2):
        super().__init__()
        
        # Adapter: decouples Mel resolution from internal channels
        self.adapter = nn.Conv1d(n_mels, 128, 1)
        
        # Depthwise separable block
        self.dw_conv = nn.Conv1d(128, 128, 11, groups=128, padding=5)
        self.pw_conv1 = nn.Conv1d(128, 64, 1)
        self.pw_conv2 = nn.Conv1d(64, 64, 1)
        
        # Residual and dilated blocks
        self.residual = nn.Conv1d(64, 64, 17, padding=8)
        self.dilated = nn.Conv1d(64, 64, 29, dilation=2, padding=29)
        
        # Classifier (will be frozen as prototype)
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.classifier = nn.Linear(64, num_classes)
    
    def forward(self, x):
        # x: [B, n_mels, time]
        x = F.relu(self.adapter(x))
        x = F.relu(self.dw_conv(x))
        x = F.relu(self.pw_conv1(x))
        x = F.relu(self.pw_conv2(x))
        x = F.relu(self.residual(x))
        x = F.relu(self.dilated(x))
        
        # Global average pooling (same weights for any input length)
        x = self.gap(x).squeeze(-1)  # [B, 64]
        
        # Penultimate features (before classifier)
        self.penultimate = x
        
        logits = self.classifier(x)
        return logits
    
    def get_penultimate(self):
        return self.penultimate if hasattr(self, 'penultimate') else None


def demo():
    print("=" * 70)
    print(" Paper: 2607.25870 - VAD to the Bone")
    print(" Method: Angle-Aware QAT + Structured Pruning + Self-Distillation")
    print("=" * 70)
    
    # Create base model
    print("\n[1] Creating base model (81K params target)...")
    model = TinySpeechCNN(n_mels=64, num_classes=2)
    base_params = sum(p.numel() for p in model.parameters())
    print(f"  Base model parameters: {base_params:,}")
    
    # Simulate training data
    print("\n[2] Simulating training...")
    dummy_data = [(torch.randn(8, 64, 50), torch.randint(0, 2, (8,))) for _ in range(10)]
    
    # === STAGE 1: Structured Pruning ===
    print("\n[3] Applying structured pruning (target: 2.1K params)...")
    
    pruning_ratios = {
        'adapter': 0.5,
        'dw_conv': 0.7,
        'pw_conv1': 0.7,
        'pw_conv2': 0.7,
        'residual': 0.7,
        'dilated': 0.7,
    }
    
    pruned_model, pruned_params = apply_structured_pruning(model, pruning_ratios)
    print(f"  After pruning: {pruned_params:,} parameters")
    print(f"  Compression ratio: {base_params / pruned_params:.1f}x")
    
    # === STAGE 2: Self-Distillation Fine-tuning ===
    print("\n[4] Self-distillation fine-tuning...")
    # Create a fresh teacher (unpruned)
    teacher = TinySpeechCNN(n_mels=64, num_classes=2)
    
    # In practice: teacher is the unpruned base model
    # Here we just demonstrate the API
    print("  (Skipping actual training for demo speed)")
    print("  API: self_distillation_finetune(pruned_model, teacher, data_loader)")
    
    # === STAGE 3: Angle-Aware QAT ===
    print("\n[5] Angle-Aware Quantization-Aware Training...")
    
    # Freeze classifier as prototype
    pruned_model.classifier.weight.requires_grad = False
    prototype = pruned_model.classifier.weight.data.clone().detach()
    print(f"  Frozen classifier prototype shape: {prototype.shape}")
    
    # Create loss function
    loss_fn = AngleAwareLoss(num_classes=2, lambda_repel=1.0)
    
    # Simulate QAT step
    features = torch.randn(16, 64, requires_grad=True)  # penultimate features
    targets = torch.randint(0, 2, (16,))
    
    loss = loss_fn(features, targets, prototype)
    loss.backward()
    
    print(f"  Angle-aware loss: {loss.item():.4f}")
    print(f"  Feature gradients computed: {'✅' if features.grad is not None else '❌'}")
    print(f"  Gradient norm: {features.grad.norm().item():.4f}")
    
    # === STAGE 4: INT4 Quantization (simulated) ===
    print("\n[6] Post-Training Quantization (INT4 RTN)...")
    
    def rtn_quantize(weight, bits=4, group_size=128):
        qmax = 2 ** (bits - 1) - 1
        w_flat = weight.flatten()
        pad = (group_size - w_flat.numel() % group_size) % group_size
        if pad > 0:
            w_flat = F.pad(w_flat, (0, pad))
        blocks = w_flat.reshape(-1, group_size)
        scales = (blocks.abs().amax(dim=1, keepdim=True) / qmax).clamp_min(1e-8)
        w_q = torch.clamp(torch.round(blocks / scales), -qmax - 1, qmax)
        w_dq = (w_q * scales).flatten()[:weight.numel()].reshape(weight.shape)
        return w_dq
    
    for name, module in pruned_model.named_modules():
        if isinstance(module, (nn.Linear, nn.Conv1d)):
            module.weight.data = rtn_quantize(module.weight.data, bits=4)
    
    print("  Applied INT4 RTN to all Linear/Conv layers")
    
    # Verify quantized model still works
    with torch.no_grad():
        test_input = torch.randn(2, 64, 50)
        output = pruned_model(test_input)
    
    print(f"  Quantized model output shape: {output.shape}")
    print(f"  Output range: [{output.min():.3f}, {output.max():.3f}]")
    
    # Summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(f"  Base model:        {base_params:,} params")
    print(f"  After pruning:     {pruned_params:,} params")
    print(f"  With INT4 weights: ~{pruned_params // 4:,} effective bytes (4x smaller)")
    print(f"  Target from paper: 2.1K params, 0.850 AUC")
    print("=" * 70)


if __name__ == "__main__":
    demo()
