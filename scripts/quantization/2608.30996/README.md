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

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF §3、Eq.（1）、§4 和 Appendix A，结论为**部分一致**。

- 原实现直接由随机 hidden state 和 Q/K/V 权重计算一层 attention，并对 INT4 错用 per-token symmetric；论文要求对完整 retrieved context 做一次 position-consistent unified prefill，INT8 per-token asymmetric，INT4 group-64 asymmetric，然后离线存储/反量化再 decode。
- 修复：真实 Qwen 64-token prefill 生成 28 层 DynamicCache；逐层按论文粒度量化/dequantize，再用该 cache 单 token decode。元数据按每组 FP16 scale + FP16 zero-point 计账。
- 实际命令：`python3 scripts/quantization/2608.30996/demo.py --tokens 64 --output-json /private/tmp/arxiv_quant_review_20260902/2608.30996.json`；INT8/INT4 compression `1.9394×/3.5556×`，logits MSE `0.001361/2.567670`，两者均生成 `下一个`，退出码 0，1.43 秒。
- **真实 Qwen3-0.6B：已跑通** 28 层 unified KV cache round-trip 与量化后 decode；未跑通 Qwen2.5-7B、RGB/HotpotQA 3,600 generations、HHEM/NLI/LLM judge/McNemar。
- 环境同批次公共环境；JSON 导出已验证。
