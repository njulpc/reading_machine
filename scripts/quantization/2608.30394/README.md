# 2608.30394 — TopGQ 拓扑分组 PTQ

## 实现范围

用真实权重行的局部相似度作 TopPIN 代理，分四组共享 INT8 scale。

## 运行

```bash
python3 scripts/quantization/2608.30394/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

没有图数据邻接矩阵；局部相似度只是拓扑代理，不能替代完整 GNN 实验。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30394/demo.py`

```json
{
  "paper_id": "2608.30394",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "TopGQ topology-proxy grouped INT8",
  "groups": 4,
  "scales": [
    0.002076156437397003,
    0.001476377947255969,
    0.0027374508790671825,
    0.0028143455274403095
  ],
  "mse": 4.558265800369554e-07,
  "cosine": 0.9997313022613525,
  "relative_l2": 0.021891800311176348
}
```
