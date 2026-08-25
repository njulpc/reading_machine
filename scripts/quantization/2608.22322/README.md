# 2608.22322 复现：Adaptive Log-Space optimizer state

本目录复现论文 [Beyond Dense Adam States: Adaptive Log-Space Quantization for Memory-Efficient Optimizers](https://arxiv.org/abs/2608.22322) 的 AL8 非负状态编码和 UF8 有符号动量编码，并提供真实 Qwen3-0.6B 单步训练路径。

## 算法与参数

- 非负状态按 2048 元素分块；code 0 只表示精确零，其余 255 个 AL8 code 均匀覆盖块内非零 log2 区间。
- 每块保存 FP32 `min_log` 与 `delta_log`；应用数值 floor、上界 126 和单值块扩展 1 个 log2 单位。
- 一阶动量按 256 元素分块，使用作者实现的 UF8：absmax/128、整数范围 [-128, 127]。
- `--full-model` 冻结其余参数，仅对首个 `q_proj` 做一次真实 loss/backward，量化 Adam 风格 M/V、更新权重，再执行前向和单 token 生成。

## 运行

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --full-model \
  --save-state /private/tmp/arxiv_quant_review_20260826/2608.22322-state.pt
```

依赖：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0。验证机器为 Apple arm64 CPU，CUDA/MPS 均不可用。

## 代码审查与验证（2026-08-26）

**算法一致性：部分一致。** AL8/UF8 的编码、精确零、分块和元数据现在与论文公式及作者公开 PyTorch fallback 一致。初始代码把二阶矩默认块设为 256、单值块宽度设为 1e-12、未应用 log floor/上界，并把 UF8 写成 absmax/127；同时只把静态权重平方当作状态。现已修正，并新增真实反传、状态量化更新、前向/生成和状态包保存/重载。

验证结果：

- 语法、导入、自测和 524,288 元素真实权重算子路径退出码均为 0；AL8 V relative L2 为 0.02219608，UF8 M 为 0.00727717，估算状态压缩 3.961x。
- 真实模型加载 596,049,920 参数；首个 `q_proj` 的 2,097,152 个参数完成真梯度单步更新。loss 7.61162138，AL8 V relative L2 0.01790705，UF8 M 0.01399476。
- 更新后 logits MAE 0.02740215、last-token cosine 0.99995863，生成成功；量化状态包保存并重新加载成功。最终复测脚本内部耗时 2.089 秒，命令墙钟 3.93 秒。

**真实 Qwen3-0.6B：已跑通（限定为首个 q_proj 的一步量化优化器状态路径）。** 未跑论文 TinyLlama-1.1B/WikiText-103 的 20K step、全参数状态、Adafactor/CAME/APOLLO、CUDA fused kernel、PPL/吞吐或长期收敛，因此不能视为论文完整训练复现。
