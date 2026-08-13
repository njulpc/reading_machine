# Paper: 2608.12259 - Calibration Bets on the Past

## PTQ Calibration Strategy Demo for Time-Series

This script demonstrates different activation calibration strategies for post-training quantization in time-series forecasting.

## Run

```bash
pip install torch
python3 demo.py
```

## Core Algorithm

1. **abs-max calibration**: Use absolute maximum as quantization range.
2. **percentile calibration**: Use percentile (e.g., 99.9%) as range.
3. **MSE-optimal**: Grid search for min MSE on calibration data.
4. **Walk-forward evaluation**: Strict temporal split avoiding lookahead bias.
