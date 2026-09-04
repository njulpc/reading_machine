# 2609.03125 — Qwen3-0.6B 数值验证

论文：[A Time-Encoded Analog Photonic Interposer for Energy-EfficientIntegration of Analog Vision Sensors and Analog Accelerators](https://arxiv.org/abs/2609.03125)。

模拟光互连通过6位斜坡比较传递激活，减少模拟计算边界的数字转换。

## 实现范围

电容DAC产生斜坡，计数器与比较器将信号编码为边沿时序，以每PE波长复用传输；研究3×3、九波长设计的精度与系统能耗。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

One activation boundary is transported using a numerical ramp. No analog convolution, photodiodes, circuit noise, wavelength scheduling or energy-delay reproduction. Calibration bounds are a Qwen transfer, not physical voltages.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.03125/demo.py --output-json /tmp/2609.03125.json
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
  "bounds": [
    -3.183000087738037,
    2.192077398300171
  ],
  "bits": 6,
  "levels": 64,
  "heldout_logits": {
    "mse": 0.0021741525270044804,
    "relative_l2": 0.01455691084265709,
    "cosine": 0.999901533126831
  },
  "full_paper_reproduced": false,
  "boundary": "One activation boundary is transported using a numerical ramp. No analog convolution, photodiodes, circuit noise, wavelength scheduling or energy-delay reproduction. Calibration bounds are a Qwen transfer, not physical voltages.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。
