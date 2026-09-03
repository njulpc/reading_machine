# 2609.02107 — 统一 rate-distortion 量化比较

## 实现范围

在 1,024 个真实 Qwen embedding 8 维切片上，以同为 8 bit/vector 比较 SQ、PQ、VQ。

## 运行

```bash
python3 scripts/quantization/2609.02107/demo.py --output-json /tmp/2609.02107.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。同 8 bit/vector 下 SQ/PQ/VQ MSE=0.000261143/0.000159213/7.65529e-05。

```json
{
  "algorithm": "equal-8-bit rate-distortion comparison on real Qwen embedding vectors",
  "vectors": 1024,
  "dimension": 8,
  "scalar_1bit_per_dim": {
    "mse": 0.0002611425006762147,
    "mae": 0.0127183236181736,
    "cosine": 0.8408767056185644,
    "relative_l2": 0.5412279963493347
  },
  "product_two_8bit_codes": {
    "mse": 0.0001592132612131536,
    "mae": 0.009909344837069511,
    "cosine": 0.9063160443638452,
    "relative_l2": 0.42260152101516724
  },
  "vector_single_8bit_code": {
    "mse": 7.655288936803117e-05,
    "mae": 0.006617601495236158,
    "cosine": 0.9561013510426224,
    "relative_l2": 0.2930367588996887
  },
  "rate_bits_per_vector": 8,
  "note": "codebook storage amortization is excluded equally from this intrinsic distortion smoke test",
  "paper_id": "2609.02107",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "transformers": "4.57.6",
    "platform": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false,
    "mps": false
  },
  "elapsed_seconds": 1.119618542,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

只验证固定码率下的内在失真；没有复现视觉 tokenizer 训练与码本存储摊销。
