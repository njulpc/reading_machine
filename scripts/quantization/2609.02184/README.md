# 2609.02184 — Qwen3-0.6B 数值验证

论文：[CC-4DGS: Computational Deformation and Point-Cloud Compression for Storage-Efficient Dynamic Gaussian Splatting](https://arxiv.org/abs/2609.02184)。

CC4DGS 联合压缩动态形变场和高斯属性，在相近渲染质量下降低动态场景存储。

## 实现范围

CDF以稠密哈希及小神经解码器表达形变；CCA让位置与SH-DC保留32位、旋转尺度不透明度12位，以条件自编码器压缩SH-AC并配合256项残差码本及Zstandard。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

Qwen rows and row statistics replace SH-AC/geometric conditions for component verification only. The paper-default 14/12/16-bit CCA profile and 256-entry residual codebook are exercised, but the 8D latent, mu=255 and 40 training steps are explicit engineering choices. No CDF deformation hash, scene rendering, Zstandard archive, or compressed Qwen checkpoint.

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
  "profile": "CCA-Default",
  "latent_bits": 14,
  "residual_codebook": 256,
  "scalar_bits": 12,
  "dynamic_bits": 16,
  "autoencoder_only": {
    "mse": 0.7930220365524292,
    "relative_l2": 0.8905292749404907,
    "cosine": 0.45493730902671814
  },
  "autoencoder_residual": {
    "mse": 0.317650705575943,
    "relative_l2": 0.5636122226715088,
    "cosine": 0.8260396122932434
  },
  "scalar_12bit_error": {
    "mse": 2.1004659345180698e-07,
    "relative_l2": 0.0003038749273400754,
    "cosine": 1.0000001192092896
  },
  "dynamic_mulaw_16bit_error": {
    "mse": 7.08537395421871e-11,
    "relative_l2": 4.73956715723034e-05,
    "cosine": 1.0
  },
  "full_paper_reproduced": false,
  "boundary": "Qwen rows and row statistics replace SH-AC/geometric conditions for component verification only. The paper-default 14/12/16-bit CCA profile and 256-entry residual codebook are exercised, but the 8D latent, mu=255 and 40 training steps are explicit engineering choices. No CDF deformation hash, scene rendering, Zstandard archive, or compressed Qwen checkpoint.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。

## 代码审查与验证（2026-09-05）

- 一致性结论：**部分一致**。官方 v1 的 CCA-Default 明确规定 AE latent 14 bit、256 项残差码本、scalar 12 bit、dynamic 16 bit；代码现已按该档位执行条件 AE、残差 K-means、标量量化与 μ-law 动态量量化。Qwen 行向量及统计量只是 SH-AC/几何条件的工程替代。
- 修复：原实现错误使用 8-bit latent，且只验证 μ-law 往返、没有真正量化动态量；现改为 14-bit latent，并加入 μ-law 后 16-bit 动态量量化与误差验证。
- 实测命令：`python3 scripts/quantization/2609.02184/demo.py --output-json /private/tmp/2609.02184.review.json`；退出码 0，墙钟 6.26 秒。语法检查、小张量检查和 256 项码本路径通过。
- 真实 Qwen3-0.6B：**完整量化未跑通**。已使用真实第一层 q_proj 权重执行 CCA 数值组件；没有 CDF、4DGS 场景、渲染、Zstandard 工件或整模量化/生成，不能表述为论文或 Qwen 整模复现。
