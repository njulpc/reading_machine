# 2609.00224 — QTEA 三值量化与半结构残差

## 实现范围

真实 Qwen 全部 Transformer Linear 执行 group-128 三值、Hessian 对角显著列与列内 1:4 残差；小 tile 另验证 GPTQ decay。

## 运行

```bash
python3 scripts/quantization/2609.00224/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 Qwen3-0.6B 权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。

```json
{
  "paper_id": "2609.00224",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "QTEA-style by-column ternary weights plus salient-column 1:4 residual compensation",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.020958166,
  "tensor_shape": [
    512,
    1024
  ],
  "salient_column_fraction": 0.25,
  "residual_density": 0.0625,
  "estimated_effective_bits_per_weight": 3.125,
  "ternary_metrics": {
    "mse": 0.00031394368852488697,
    "cosine": 0.8690098527387462,
    "relative_l2": 0.5809196829795837
  },
  "compensated_metrics": {
    "mse": 0.00024123876937665045,
    "cosine": 0.8839877088656946,
    "relative_l2": 0.5092340111732483
  }
}
```

## 证据边界

未实现 GPTQ Hessian、误差衰减、论文 1.7 bit 精确存储布局或 LUT GPU 内核。

## 代码审查与验证（2026-09-03，取代上述初始切片结果）

**算法一致性：部分一致。** 原论文/作者代码使用 group-128 的带偏置三值基座、5% 显著输入列、显著列内沿输出行的 1:4 FP8 残差、逐列 rescale、GPTQ 逆 Hessian 误差传播与位置相关 decay；默认校准为 256 条、序列长 2048。初始实现把 1:4 分组方向写成了“同一行内跨显著列”、用 25% 列和纯权重误差选列，也没有偏置、逐列 rescale 或 decay。

本次修复为：按真实校准激活的 Hessian 对角项和论文公式选择 5% 列；按输出行每四个元素只保留一个残差；加入 group-128 `alpha/beta` 三值拟合和两轮逐列 rescale；对真实校准张量的小 tile 实际执行公式 (6)–(9) 的逆 Hessian/decay；将数值表示应用到 Qwen 的全部 196 个 Transformer Linear（440,401,920 个权重）。整模 CPU 路径为对角 Hessian 工程近似，未冒充作者的完整稠密 GPTQ。

```bash
python3 scripts/quantization/2609.00224/demo.py --self-test
python3 scripts/quantization/2609.00224/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.00224.json
```

环境为 macOS 26.6.2 arm64 CPU（CUDA/MPS 均不可用）、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0。两条命令均退出码 0；整模命令墙钟 5.63 秒。整模校准 1 条/16 token，平均显著列比例 0.050618、残差密度 0.012655；量化后 logits MSE 2.273539、cosine 0.821585，生成 1 token 成功且 logits 有限。**真实 Qwen3-0.6B：已跑通（整模数值路径）；论文 256×2048 校准、完整 GPTQ、紧凑 checkpoint 与 LUT CUDA 内核未跑通。**
