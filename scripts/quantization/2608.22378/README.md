# 2608.22378 复现：Variable-bit approximate PE

本目录审查论文 [Precision-Aware Variable Bit Processing Elements for Hardware-Efficient Systolic Array Designs](https://arxiv.org/abs/2608.22378)。论文对象是 weight-stationary systolic array 中的近似浮点乘法器，不是常规 PTQ 权重量化器。

## 软件参考范围

- FP32/TF32/BF16 分别按 24/11/8 位有效 significand 建模。
- 小矩阵路径把浮点数拆成整数 significand，显式清除乘积最低 PPM 列后重构并累加。
- `--full-model` 仅把 Qwen Transformer 内全部 Linear 权重和输入激活截到指定 mantissa 位数，用于验证 operand-format 全模型数值路径；它不等价于论文的 compressor 或 systolic-array RTL。
- 论文的 TBITS、ABITS 与 8 种正/负 compressor 由 NSGA-II 为每个 PE 联合搜索。没有 RTL、compressor 真值表、综合工具和任务配置时，不用普通 mantissa 截断冒充这些硬件步骤。

## 运行

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --full-model --full-keep-bits 7
```

依赖：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0。验证机器为 Apple arm64 CPU，CUDA/MPS 均不可用。

## 代码审查与验证（2026-08-26）

**算法一致性：部分一致。** 初始 demo 只是对两个 operand 先截 FP32 mantissa 再调用普通矩阵乘，却把它描述成 partial-product 列截断；也没有 TBITS/ABITS、正负 compressor、PE 异构配置或 NSGA-II。现新增可核查的整数 significand PPM-LSB 截列算子并明确证据边界。论文没有给出 Qwen 配置，硬件收益只在论文 CNN/图像任务和综合流程中成立。

验证结果：

- 语法、自测和 64x64 真实 Qwen 权重切片路径退出码为 0。截 3 个 PPM LSB 列时，FP32/TF32/BF16 relative L2 分别为 0.00000014/0.00019883/0.00149801。
- operand-format 压力路径加载真实 596,049,920 参数 Qwen，处理 196 个 Transformer Linear、440,401,920 个权重元素，并对其输入激活应用 7-bit mantissa 截断；完整前向和单 token 生成退出码 0，logits relative L2 0.00649652、cosine 经数值夹紧为 1.0，最终复测脚本内部耗时 0.793 秒，命令墙钟 2.61 秒。

**真实 Qwen3-0.6B：未跑通论文提出的 approximate-PE 硬件路径。** 已跑通的是全模型 operand-format 软件替代，不含 compressor、WS systolic dataflow、NSGA-II、RTL、FPGA/ASIC 综合或 PPA，因此不能宣称复现论文 66%-92% footprint、60%-93% power 或 21%-54% delay 收益。
