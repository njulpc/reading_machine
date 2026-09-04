# 2609.02184 — Qwen3-0.6B 数值验证

论文：[CC-4DGS: Computational Deformation and Point-Cloud Compression for Storage-Efficient Dynamic Gaussian Splatting](https://arxiv.org/abs/2609.02184)。

CC4DGS 联合压缩动态形变场和高斯属性，在相近渲染质量下降低动态场景存储。

## 实现范围

CDF以稠密哈希及小神经解码器表达形变；CCA让位置与SH-DC保留32位、旋转尺度不透明度12位，以条件自编码器压缩SH-AC并配合256项残差码本及Zstandard。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

Qwen rows and row statistics replace SH-AC/geometric conditions for component verification only. 8D latent, 8bit latent, mu=255 and 40 training steps are demo choices, not claimed paper defaults. No CDF deformation hash, scene rendering, archive Zstandard, or compressed Qwen checkpoint.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.02184/demo.py --output-json /tmp/2609.02184.json
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
  "rows": 1024,
  "residual_codebook": 256,
  "scalar_bits": 12,
  "autoencoder_only": {
    "mse": 0.7930701971054077,
    "relative_l2": 0.890556275844574,
    "cosine": 0.4548839330673218
  },
  "autoencoder_residual": {
    "mse": 0.3168783187866211,
    "relative_l2": 0.5629268884658813,
    "cosine": 0.8265063762664795
  },
  "scalar_12bit_error": {
    "mse": 2.1004659345180698e-07,
    "relative_l2": 0.0003038749273400754,
    "cosine": 1.0000001192092896
  },
  "full_paper_reproduced": false,
  "boundary": "Qwen rows and row statistics replace SH-AC/geometric conditions for component verification only. 8D latent, 8bit latent, mu=255 and 40 training steps are demo choices, not claimed paper defaults. No CDF deformation hash, scene rendering, archive Zstandard, or compressed Qwen checkpoint.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。
