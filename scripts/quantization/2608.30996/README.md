# 2608.30996 — 离线 KV 缓存量化可信度审计

## 实现范围

由 Qwen Q/K/V 真权重生成 32 Token 缓存，比较 INT8/INT4 的输出余弦和 top-evidence 翻转率。

## 运行

```bash
python3 scripts/quantization/2608.30996/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

未运行 RGB/HotpotQA 与外部 hallucination judge；翻转率是可重复的局部忠实度代理。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30996/demo.py`

```json
{
  "paper_id": "2608.30996",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "offline per-token KV-cache INT8/INT4 audit",
  "sequence": 32,
  "head_width_proxy": 1024,
  "results": {
    "8": {
      "mse": 7.746721166768111e-06,
      "cosine": 0.999925434589386,
      "relative_l2": 0.012217945530907395,
      "top_evidence_flip_rate": 0.0
    },
    "4": {
      "mse": 0.0031896759755909443,
      "cosine": 0.971488893032074,
      "relative_l2": 0.2479203981645887,
      "top_evidence_flip_rate": 0.25
    }
  }
}
```
