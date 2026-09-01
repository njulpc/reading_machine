# 2608.30439 — 稀疏量化事件驱动激活

## 实现范围

在 Qwen 投影激活上按 40% 分位阈值置零，再做逐 Token INT4，并统计有效运算下降。

## 运行

```bash
python3 scripts/quantization/2608.30439/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

未复现神经形态芯片和训练阈值；软件路径不等价于论文 37x/16x 硬件预测。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30439/demo.py`

```json
{
  "paper_id": "2608.30439",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "trainable-threshold proxy + INT4 event-driven activations",
  "threshold_quantile": 0.4,
  "activation_sparsity": 0.399993896484375,
  "effective_op_reduction": 1.6666497126290627,
  "mse": 0.023033909499645233,
  "cosine": 0.9756960868835449,
  "relative_l2": 0.2201398437192899
}
```
