# 2609.02854 — Qwen3-0.6B 数值验证

论文：[MuyBridge: Mobile Human Center-of-Mass Estimation from Monocular Video via Sparse Fusion](https://arxiv.org/abs/2609.02854)。

MuyBridge 联合姿态裁剪、INT8量化和少步深度估计，实现手机端人体质心测量。

## 实现范围

GroupFisher将姿态通道3336裁至2389，浅层较激进；逐通道对称W8、逐张量非对称A8；深度使用一致性蒸馏，UNet量化感知训练、VAE训练后量化，敏感注意力等保留FP16。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

Qwen MLP PTQ component transfer only; attention and norms kept FP32 rather than paper FP16. No GroupFisher, pose retraining, UNet QAT, latent-consistency distillation, geometric fusion or Apple Neural Engine export. Vision datasets/models unavailable locally.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.02854/demo.py --output-json /tmp/2609.02854.json
```

可选指定检查点：

```sh
export QWEN_MODEL_PATH=/path/to/Qwen3-0.6B
```

校准文本与独立测试文本在`../numerics.py`明示。涉及全模型前向的验证使用不同的校准/测试文本；算子与码本测试仅检验组件误差，不做泛化声称。

## 实测结果与配置

```json
{
  "model": "Qwen3-0.6B",
  "linears": 84,
  "weight_bits": 8,
  "activation_bits": 8,
  "weight_granularity": "per output channel symmetric",
  "activation_granularity": "static per tensor asymmetric",
  "heldout_logits": {
    "mse": 0.6911038160324097,
    "relative_l2": 0.2595379650592804,
    "cosine": 0.9657615423202515
  },
  "full_paper_reproduced": false,
  "boundary": "Qwen MLP PTQ component transfer only; attention and norms kept FP32 rather than paper FP16. No GroupFisher, pose retraining, UNet QAT, latent-consistency distillation, geometric fusion or Apple Neural Engine export. Vision datasets/models unavailable locally.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。
