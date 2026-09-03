# 2609.02846 — UE5M3 FP4 block scaling

## 方法与实现范围

论文使用 E2M1 4-bit payload 与 unsigned E5M3 8-bit block scale。UE5M3 的最小 subnormal 为 `2^-17`、最大有限值 61,440；默认 block 16、scale target 448，权重采用 16×16 二维块。完整训练 recipe 为各 operand 独立的 50-step sample-and-hold tensor amax、无 RHT、仅 dY stochastic rounding、全部 eligible Linear FP4，输出头 FP32。

本 demo 实现与作者参考代码一致的有限值集合、ties-to-even、零 scale→1、运算顺序、二维权重块和一维激活块，并把它作为当前 amax (`D=1`) 的 Qwen3-0.6B W4A4 inference transfer；不是论文的预训练实验。

## 运行

```bash
python3 scripts/quantization/2609.02846/demo.py --self-test
python3 scripts/quantization/2609.02846/demo.py --output-json /tmp/2609.02846.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** E2M1/UE5M3 值集、block-16、2D weight scaling、target 448、ties-to-even 与零 scale 规则一致；缺 D=50 训练状态、独立 operand cache、dY stochastic rounding、两条 backward GEMM、probe-matched accumulator、Nemotron-H 和原生吞吐。
- **修复：** 原 UE5M3 把指数直接 clamp 到 `[-15,16]`，最大值和 subnormal 均错误，也遗漏 tensor reference/target 与 2D 权重缩放；现按论文式 (6)(7) 和作者实现修正，并从首层切片扩为 196 个 Linear/440,401,920 权重及全部 Linear 激活的整模前向/生成。
- **证据：** 官方源码 `MrHuff/ue5m3-fp4@1707f273` 只读核对 `formats.py` 与金值；其当前代码使用 Python `StrEnum`，本机 Python 3.9 无法直接导入，仓库内独立金值测试已 PASS。
- **结果：** 退出码 0，4.77 s；1,720,320 个权重 scale code，估算 payload+scale `221,921,280` byte（未实际 pack）。相对 dense，W4A4 logits MSE `0.924935`、cosine `0.944238`，生成“这句话”。
- **真实 Qwen3-0.6B：已跑通（inference transfer）。** 论文 188.7B-token 预训练未跑通；没有 CUDA 原生 kernel、训练 checkpoint 或吞吐结论。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；本地完整 Qwen3-0.6B checkpoint。
