# 2609.02652 — 多壳 24D 低比特布局

## 实现范围

对真实 q_proj 权重执行 24D 多壳稀疏符号向量选择、2-bit shell index 与 bit-plane 驻留位数核算。

## 运行

```bash
python3 scripts/quantization/2609.02652/demo.py --output-json /tmp/2609.02652.json
```

环境：macOS arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；读取本地 Qwen3-0.6B checkpoint，不下载权重。

## 本次真实验证结果

语法、导入、真实 checkpoint 加载和真实 Qwen 张量运行均 **PASS**。估算驻留 1.2348 bpw，输出 cosine=0.933708，shell 直方图=[37, 670, 4675, 80]。

```json
{
  "algorithm": "24D multi-shell signed-vector decoder with bit-plane residency accounting",
  "shell_histogram": [
    37,
    670,
    4675,
    80
  ],
  "resident_bpw_estimate": 1.234771728515625,
  "output": {
    "mse": 0.010499969124794006,
    "mae": 0.07107777893543243,
    "cosine": 0.9337078437151144,
    "relative_l2": 0.3709404468536377
  },
  "boundary": "software transfer reproduces shell selection/layout mechanics, not the paper exact 301-class Leech codebook or fused CUDA kernel",
  "paper_id": "2609.02652",
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
  "elapsed_seconds": 1.22689125,
  "status": "PASS",
  "scope": "real checkpoint and real model activations; CPU numerical reference"
}
```

## 证据边界

未实现论文精确 301-class Leech 码本与融合 CUDA GEMV；只验证多壳选择和布局机制。
