# 2608.30908 — GradCodes 量化码空间微调

## 实现范围

固定 4-bit scale，在整数 code 上用 surrogate gradient 与投影搜索逼近目标更新。

## 运行

```bash
python3 scripts/quantization/2608.30908/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

小切片和合成目标更新只验证 code-space 优化，不代表论文完整微调基准。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30908/demo.py`

```json
{
  "paper_id": "2608.30908",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "4-bit code-surrogate gradient with guided integer projection",
  "steps": 12,
  "initial_target_mse": 0.0012729353038594127,
  "final_target_mse": 4.052614895044826e-05,
  "changed_code_fraction": 0.90228271484375
}
```
