# 2608.23144 复现：Activation-Weighted Seeded Residual Coding

本目录复现论文 [Activation-Weighted Seeded Residual Coding for Low-Bit LLM Weight Repair](https://arxiv.org/abs/2608.23144) 的 AWSRC-U 核心编码器，并用真实 Qwen3-0.6B 做 INT4 主干和 sidecar 验证。

## 算法与参数

- backbone 为逐行、group-128 对称 INT4 RTN（-7..7）。
- residual 按行切为 C=128 tile；每个 seed 生成 sign pattern、coordinate permutation 和归一化 Hadamard 的 P=2 列。
- 以校准输入二阶矩 D 做加权最小二乘；系数在 seed 选择前量化为 signed 4-bit，每个 tile 共享一个 2 的幂 scale。
- 只保留正收益记录，并按 activation-weighted gain/serialized byte 排序。记录包含 tile index、seed selector、P 个 coefficient 和 scale exponent；码率包含 904-byte header 与字节取整。

## 运行

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --full-model \
  --save-sidecar /private/tmp/arxiv_quant_review_20260826/2608.23144-sidecar.pt
```

依赖：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0。验证机器为 Apple arm64 CPU，CUDA/MPS 均不可用。

## 代码审查与验证（2026-08-26）

**算法一致性：部分一致。** 初始代码把整张矩阵 flatten 后 group-64 INT4，按每个 block/候选临时随机生成单个 ±1 basis，只拟合一个系数，使用非幂次共享 scale，也没有行 tile、Hadamard 子空间、加权正规方程、正收益选择或真实字节核算。现按论文 AWSRC-U 的 (C,P,b,S)=(128,2,4,2) 修正，RTN 改为 group-128，并在 coefficient 量化后选 seed。

验证结果：

- 256x256 真实权重切片、64 个固定随机校准激活的算子路径退出码 0；INT4 output MSE 0.004215201829，修复后 0.004191650078，局部 gap closed 0.559%；保留 52/512 tiles，含 header sidecar 1,112 bytes（0.135742 incremental bpw）。
- 真实 Qwen 加载 596,049,920 参数，以 4 条固定文本采集 84 个 MLP 投影的 activation diagonal，对全部 264,241,152 个 MLP 权重做 group-128 INT4，并对首个 MLP 模块应用 AWSRC-U 10% tile sidecar。完整前向、单 token 生成以及 sidecar 保存/重载/确定性解码退出码为 0，解码权重与内存重构逐 bit 相同。
- INT4 parent 估算 4.25 bpw、logits MAE 0.73013002；单模块 sidecar 保留 2,458 tiles、10,736 bytes（相对全 MLP scope +0.00032504 bpw），但 repaired logits MAE 为 0.73043519，整模 gap closed **-0.042%**。该负结果说明小切片局部收益不能外推到缩小的整模 repair scope。last-token cosine 0.95430267；round-trip 最终复测脚本内部耗时 1.530 秒，命令墙钟 3.35 秒。

**真实 Qwen3-0.6B：已跑通（全 84 个 MLP 的 INT4 主干 + 单模块 AWSRC-U sidecar）。** 未跑论文 Qwen2.5-3B-Instruct 的 108 矩阵、32 条校准文本、WikiText-2、完整预算分配、Fisher/progressive 变体、SDQ、PPL/KL/6 项准确率或 standalone 量化 checkpoint；保存的 sidecar 依赖当前 INT4 backbone，不是独立可部署模型。因此不能宣称复现论文 88.2%/78.9%/71.3% gap recovery 或 49.25 MB artifact。
