# 2608.19837：E4M3 逐层 exponent-bias 校准复现

本目录把论文的核心数值算法移植到真实 Qwen3-0.6B：有限值 E4M3 fake quantization，以及以校准误差为目标的逐层 exponent-bias 选择。论文原场景是 FFT-LeNet-5 + FPGA；Qwen 不包含 FFT 卷积，因此 inverse-FFT `1/N` weight scaling 与 PBA 蝶形逐级偏置递减没有伪装成 Transformer 算法。

## 对齐与差异

- 对齐：E4M3（4-bit exponent、3-bit mantissa）、层级 bias 可配置、运行时校准样本、以量化输出误差选择每层 bias。
- 论文用小校准子集和 Bayesian optimization 搜索多层组合；本复现候选只有 7 个离散 bias，逐层穷举得到精确最优，避免引入没有必要的优化器随机性。
- 同一个候选 bias 同时量化该 Linear 的输入和权重，反量化到 FP32 做误差评估；不代表原生 FP8 存储、FPGA datapath、FFT 或吞吐。
- 默认只校准前 7 个 Qwen Linear，避免 CPU 上重复量化完整 0.6B 模型；可增大 `--max-layers`。

## 运行

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
PYTHONPYCACHEPREFIX=/private/tmp/pycache_quant_20260822 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py \
  --self-test --max-layers 7 --max-tokens 32
```

只验证量化算子：

```bash
/private/tmp/arxiv_tilemix_venv/bin/python demo.py --self-test-only
```

输出逐层 selected bias、校准 MSE、固定标准 bias=7 的 MSE，以及完整 JSON sweep。实验结果必须解读为 Qwen3 上的数值移植，不是论文 LeNet-5 准确率或 FPGA 2.5× 能效复现。

## 证据边界

本机 Apple CPU 无 CUDA/MPS，且没有论文的 Xilinx XC7A200T、工业 X 光数据和 FFT RTL。能够验证的是 E4M3 数值路径、真实 Qwen 权重/激活、逐层 calibration 与误差改善；不能验证 PBA、FPGA 面积/功耗、1.91 ms latency 或原生 FP8 kernel。

## 实际验证（2026-08-22）

语法编译和纯张量自测均通过。真实加载 Qwen3-0.6B 的 596,049,920 个参数，使用 32-token 提示校准第一层 Q/K/V/O 与 gate/up/down 共 7 个 Linear、15,728,640 个权重元素。候选 bias 为 5–11；各层最优值为 10/11/10/10/11/11/11。相对固定 bias=7，逐层最优校准 MSE 的几何平均比为 **0.876381**，即在这组 Qwen 激活上降低约 **12.36%**。

所有结果来自 FP32 dequantized fake-quant。它验证了论文“逐层 bias 比统一格式更好”的数值方向，但不等于论文 3,208 张工业图像上的 84.13% 准确率，也不代表原生 FP8 或 FPGA 能效。
