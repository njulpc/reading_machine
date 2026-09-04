# Hardware-Aware FP4 FlashAttention-4

- arXiv ID：2609.04105
- 作者：Robert Hu
- v1实际提交：2026-09-03T17:12:35Z（UTC）；2026-09-04T01:12:35+08:00（Asia/Shanghai）
- 主分类：Machine Learning (cs.LG)；全部分类：Machine Learning (cs.LG)
- 本次归类：量化；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.04105)；[官方HTML全文](https://arxiv.org/html/2609.04105)；[PDF](https://arxiv.org/pdf/2609.04105)

## 1. 核心速览

研究主题：量化。Direct-P 直接从分数产生 FP4 概率码，并用相同表示计算归一化分母。

## 2. 研究背景与动机

FP4 GEMM 变快后，指数转换和片上依赖成为注意力关键路径；独立近似分母会引入数值失配。

## 3. 核心方法与创新点

- NVFP4 Q/K 与 MXFP4 P/V
- N32 概率块使用 E8M0 幅度，E2M1 仿射映射 A=1.50、B=1.20，Wan 为1.60/0.95
- 按表示后概率累加分母
- 极端 logits 使用采样锚与指数下溢保护。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.04105)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

GB200 非因果 forward 最高 2.13 倍 BF16 吞吐；完整单 GPU 8B 更新最高 1.14 倍。分布式训练保留 FP8 P/V，测试的 MXFP4 P/V 轨迹均发散。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | GB200 非因果 forward 最高 2.13 倍 BF16 吞吐；完整单 GPU 8B 更新最高 1.14 倍。分布式训练保留 FP8 P/V，测试的 MXFP4 P/V 轨迹均发散。 |
| 压缩倍率 | 7 | GB200 非因果 forward 最高 2.13 倍 BF16 吞吐；完整单 GPU 8B 更新最高 1.14 倍。分布式训练保留 FP8 P/V，测试的 MXFP4 P/V 轨迹均发散。 |
| 创新性 | 9 | NVFP4 Q/K 与 MXFP4 P/V；N32 概率块使用 E8M0 幅度，E2M1 仿射映射 A=1.50、B=1.20，Wan 为1.60/0.95；按表示后概率累加分母；极端 logits 使用采样锚与指数下溢保护。 |
| 可复现性 | 5 | kernel 计时不含 QKV 动态量化和重排；CPU demo 验证算子而非 TMEM/Blackwell 内核，没有复制训练吞吐。 |

本地验证：以真实Qwen3-0.6B权重运行数值组件，结果状态`executed`，`full_paper_reproduced=false`。详见[README](../../../../scripts/quantization/2609.04105/README.md)及[原始结果](../../../../scripts/quantization/2609.04105/results.json)。

Real first-layer projections used as noncausal operator inputs before RoPE/QK normalization. V uses block-32 power-of-two MX reconstruction. No folded K64 scales, sampled guard, TMEM packing, backward or full-model substitution. Thus not a complete FP4 attention reproduction and no speedup claimed.

## 5. 局限性与未来展望

kernel 计时不含 QKV 动态量化和重排；CPU demo 验证算子而非 TMEM/Blackwell 内核，没有复制训练吞吐。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

应围绕最终低比特码的决策边界优化，而不是先高精度计算再舍弃；同时维护数值不变量。
