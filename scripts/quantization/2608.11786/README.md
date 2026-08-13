# Paper: 2608.11786 - LCD

## Language-Conditional Dequantization Demo

This script demonstrates Language-Conditional Dequantization (LCD) for recovering multilingual capabilities of quantized LLMs.

**Note**: Qwen3-0.6B model download requires HuggingFace access. The demo includes both model-based and synthetic tests.

## Run

```bash
pip install torch transformers peft accelerate
python3 demo.py
```

## Core Algorithm

1. **Quantize model** with GPTQ (INT3/INT4)
2. **Attach per-language rank-2 LoRA** to linear layers of quantized model
3. **Train LoRA** on target language corpus (20 min on single GPU)
4. **Switch LoRA at inference** based on detected language
