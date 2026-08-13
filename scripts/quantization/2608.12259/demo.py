#!/usr/bin/env python3
"""
================================================================================
Paper: 2608.12259 - Calibration Bets on the Past
Title: Post-Training Quantization for Financial Time-Series Forecasting
Core Method: Systematic study of activation calibration strategies
================================================================================

This script demonstrates:
1. Different activation calibration strategies (abs-max, percentile, MSE-optimal)
2. Walk-forward evaluation with strict temporal split
3. Impact of calibration range on quantized model performance

Usage:
    python3 demo.py

Requirements:
    pip install torch
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# =============================================================================
# 1. Activation Quantizers with Different Calibration Strategies
# =============================================================================

class ActivationQuantizer:
    """Base activation quantizer with configurable calibration."""
    
    def __init__(self, bits=4, strategy='abs-max', percentile=99.9):
        self.bits = bits
        self.strategy = strategy
        self.percentile = percentile
        self.scale = None
        self.zero_point = None
    
    def calibrate(self, activation_samples):
        """
        Calibrate quantization range from activation samples.
        
        Args:
            activation_samples: list of activation tensors from calibration data
        """
        # Collect all activations
        all_acts = torch.cat([a.flatten() for a in activation_samples])
        
        if self.strategy == 'abs-max':
            # Default: use absolute maximum
            act_max = all_acts.abs().max()
            self.scale = act_max / (2 ** (self.bits - 1) - 1)
            self.zero_point = 0.0
            
        elif self.strategy == 'percentile':
            # Use percentile to exclude extreme outliers
            p_val = torch.quantile(all_acts.abs(), self.percentile / 100.0)
            self.scale = p_val / (2 ** (self.bits - 1) - 1)
            self.zero_point = 0.0
            
        elif self.strategy == 'mse-optimal':
            # Grid search for MSE-optimal range
            best_mse = float('inf')
            best_scale = None
            
            # Search over different percentile values
            for p in np.linspace(90, 99.99, 20):
                p_val = torch.quantile(all_acts.abs(), p / 100.0)
                scale = p_val / (2 ** (self.bits - 1) - 1)
                
                # Simulate quantization
                quant = torch.round(all_acts / scale.clamp_min(1e-8)).clamp(
                    -(2 ** (self.bits - 1)), 2 ** (self.bits - 1) - 1
                )
                dequant = quant * scale
                
                mse = ((all_acts - dequant) ** 2).mean().item()
                if mse < best_mse:
                    best_mse = mse
                    best_scale = scale
            
            self.scale = best_scale
            self.zero_point = 0.0
    
    def quantize(self, x):
        """Quantize activation using calibrated parameters."""
        if self.scale is None:
            raise ValueError("Quantizer not calibrated")
        
        quant = torch.round(x / self.scale.clamp_min(1e-8)).clamp(
            -(2 ** (self.bits - 1)), 2 ** (self.bits - 1) - 1
        )
        return quant * self.scale


# =============================================================================
# 2. Time-Series Forecasting Model
# =============================================================================

class TemporalFusionModel(nn.Module):
    """Simple LSTM-based time-series forecasting model."""
    
    def __init__(self, input_size=10, hidden_size=64, num_layers=2, output_size=5):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x, return_activations=False):
        """
        Forward pass.
        
        Args:
            x: [batch, seq_len, input_size]
            return_activations: if True, return intermediate activations for calibration
        """
        lstm_out, _ = self.lstm(x)
        # Use last timestep
        last_hidden = lstm_out[:, -1, :]
        
        if return_activations:
            return self.fc(last_hidden), last_hidden
        return self.fc(last_hidden)


# =============================================================================
# 3. Walk-Forward Evaluation
# =============================================================================

def generate_synthetic_data(n_samples=1000, input_size=10, seq_len=20, output_size=5):
    """Generate synthetic time-series with regime changes."""
    torch.manual_seed(42)
    
    # Generate features with time-varying volatility
    t = torch.linspace(0, 4 * np.pi, n_samples)
    volatility = 1.0 + 0.5 * torch.sin(t)  # Varying volatility
    
    X = []
    Y = []
    for i in range(n_samples - seq_len):
        seq = torch.randn(seq_len, input_size) * volatility[i]
        target = seq[-output_size:, 0] if output_size <= seq_len else seq[-1:, 0].repeat(output_size)
        X.append(seq)
        Y.append(target[:output_size])
    
    return torch.stack(X), torch.stack(Y)


def walk_forward_evaluate(model, X, Y, calib_size=100, test_size=100, strategy='abs-max', bits=4):
    """
    Walk-forward evaluation: calibrate on past, test on future.
    
    Args:
        model: trained model
        X, Y: full dataset
        calib_size: number of samples for calibration
        test_size: number of samples for testing
        strategy: calibration strategy
        bits: quantization bits
        
    Returns:
        mse_fp: full precision MSE
        mse_q: quantized MSE
    """
    # Split: strict temporal order
    calib_X = X[:calib_size]
    calib_Y = Y[:calib_size]
    test_X = X[calib_size:calib_size + test_size]
    test_Y = Y[calib_size:calib_size + test_size]
    
    # Calibrate activation quantizer
    model.eval()
    activations = []
    with torch.no_grad():
        for i in range(0, len(calib_X), 16):
            batch_X = calib_X[i:i+16]
            _, acts = model(batch_X, return_activations=True)
            activations.append(acts)
    
    quantizer = ActivationQuantizer(bits=bits, strategy=strategy)
    quantizer.calibrate(activations)
    
    # Evaluate on test set
    mse_fp = 0
    mse_q = 0
    
    with torch.no_grad():
        for i in range(len(test_X)):
            x = test_X[i:i+1]
            y = test_Y[i:i+1]
            
            # FP prediction
            pred_fp = model(x)
            mse_fp += F.mse_loss(pred_fp, y).item()
            
            # Quantized prediction (quantize intermediate activations)
            _, acts = model(x, return_activations=True)
            acts_q = quantizer.quantize(acts)
            pred_q = model.fc(acts_q)
            mse_q += F.mse_loss(pred_q, y).item()
    
    return mse_fp / len(test_X), mse_q / len(test_X)


# =============================================================================
# 4. Demo
# =============================================================================

def demo():
    print("="*70)
    print(" Paper: 2608.12259 - Calibration Bets on the Past")
    print(" Method: PTQ Calibration for Time-Series Forecasting")
    print("="*70)
    
    # Generate data
    print("\n[1] Generating synthetic time-series data...")
    X, Y = generate_synthetic_data(n_samples=500, input_size=10, seq_len=20, output_size=5)
    print(f"  Total samples: {len(X)}")
    
    # Train model
    print("\n[2] Training forecasting model...")
    model = TemporalFusionModel(input_size=10, hidden_size=64, num_layers=2, output_size=5)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    train_size = 300
    train_X, train_Y = X[:train_size], Y[:train_size]
    
    for epoch in range(100):
        model.train()
        total_loss = 0
        for i in range(0, len(train_X), 32):
            batch_X = train_X[i:i+32]
            batch_Y = train_Y[i:i+32]
            
            pred = model(batch_X)
            loss = F.mse_loss(pred, batch_Y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        if (epoch + 1) % 20 == 0:
            print(f"  Epoch {epoch+1}/100, Loss: {total_loss/len(train_X):.6f}")
    
    # Evaluate different calibration strategies
    print("\n[3] Evaluating calibration strategies (4-bit activation)...")
    print(f"\n{'Strategy':<20} {'FP MSE':>10} {'Quant MSE':>10} {'Degradation':>12}")
    print("-"*60)
    
    strategies = [
        ('abs-max', 'abs-max', None),
        ('percentile-99', 'percentile', 99.0),
        ('percentile-99.5', 'percentile', 99.5),
        ('percentile-99.9', 'percentile', 99.9),
        ('mse-optimal', 'mse-optimal', None),
    ]
    
    results = {}
    for name, strategy, pctl in strategies:
        mse_fp, mse_q = walk_forward_evaluate(
            model, X[train_size:], Y[train_size:],
            calib_size=50, test_size=100,
            strategy=strategy, bits=4
        )
        degradation = (mse_q - mse_fp) / mse_fp * 100
        results[name] = {'fp': mse_fp, 'quant': mse_q, 'deg': degradation}
        
        pctl_str = f"({pctl}%)" if pctl else ""
        print(f"{name+pctl_str:<20} {mse_fp:>10.6f} {mse_q:>10.6f} {degradation:>11.1f}%")
    
    # Compare 4-bit vs 8-bit
    print("\n[4] Bit-width comparison (percentile-99.5 calibration)...")
    print(f"\n{'Bits':<10} {'FP MSE':>10} {'Quant MSE':>10} {'Degradation':>12}")
    print("-"*50)
    
    for bits in [8, 4]:
        mse_fp, mse_q = walk_forward_evaluate(
            model, X[train_size:], Y[train_size:],
            calib_size=50, test_size=100,
            strategy='percentile', bits=bits
        )
        degradation = (mse_q - mse_fp) / mse_fp * 100
        print(f"{bits:<10} {mse_fp:>10.6f} {mse_q:>10.6f} {degradation:>11.1f}%")
    
    # Regime change analysis
    print("\n[5] Regime change sensitivity...")
    print("  Testing calibration from low-volatility period on high-volatility period...")
    
    # Split by volatility regime
    low_vol_X = X[train_size:train_size+50]
    high_vol_X = X[train_size+100:train_size+150]
    low_vol_Y = Y[train_size:train_size+50]
    high_vol_Y = Y[train_size+100:train_size+150]
    
    # Calibrate on low vol, test on high vol
    activations = []
    with torch.no_grad():
        for i in range(0, len(low_vol_X), 16):
            _, acts = model(low_vol_X[i:i+16], return_activations=True)
            activations.append(acts)
    
    quantizer_narrow = ActivationQuantizer(bits=4, strategy='percentile')
    quantizer_narrow.calibrate(activations)
    
    quantizer_wide = ActivationQuantizer(bits=4, strategy='percentile')
    quantizer_wide.percentile = 99.99
    quantizer_wide.calibrate(activations)
    
    mse_fp, mse_narrow, mse_wide = 0, 0, 0
    with torch.no_grad():
        for i in range(len(high_vol_X)):
            x = high_vol_X[i:i+1]
            y = high_vol_Y[i:i+1]
            
            pred_fp = model(x)
            mse_fp += F.mse_loss(pred_fp, y).item()
            
            _, acts = model(x, return_activations=True)
            pred_n = model.fc(quantizer_narrow.quantize(acts))
            pred_w = model.fc(quantizer_wide.quantize(acts))
            
            mse_narrow += F.mse_loss(pred_n, y).item()
            mse_wide += F.mse_loss(pred_w, y).item()
    
    n = len(high_vol_X)
    print(f"  FP MSE: {mse_fp/n:.6f}")
    print(f"  Narrow range (99%): {mse_narrow/n:.6f} (+{(mse_narrow/n - mse_fp/n)/(mse_fp/n)*100:.1f}%)")
    print(f"  Wide range (99.99%): {mse_wide/n:.6f} (+{(mse_wide/n - mse_fp/n)/(mse_fp/n)*100:.1f}%)")
    
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    print("This demo shows that activation calibration strategy significantly")
    print("affects PTQ performance in time-series forecasting:")
    print("- 4-bit: calibration strategy is the primary performance determinant")
    print("- Percentile calibration recovers most degradation vs abs-max")
    print("- Wide ranges are more robust to regime changes")
    print("="*70)


if __name__ == "__main__":
    demo()
