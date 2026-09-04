# DSAQuant: Denoising-Stage-Aligned Quantization-Aware Training for Video Generation

- arXiv ID：2609.04031
- 作者：Shuaiting Li, Zelin Gao, Haibin Shen, Yujun Shen, Haotong Qin, Yinghao Xu
- v1实际提交：2026-09-03T16:09:25Z（UTC）；2026-09-04T00:09:25+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV)
- 本次归类：量化；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.04031)；[官方HTML全文](https://arxiv.org/html/2609.04031)；[PDF](https://arxiv.org/pdf/2609.04031)

## 1. 核心速览

研究主题：量化。DSA 按去噪阶段切换监督来源，并把低比特误差与CFG调度共同处理。

## 2. 研究背景与动机

固定强度教师蒸馏在晚期可能保留教师误差，视频低比特训练对时间步尤其敏感。

## 3. 核心方法与创新点

- 式5/6令教师权重随t从噪声端到数据端指数衰减，原生flow目标权重互补
- 式11在后期关闭CFG。W4A4使用逐通道权重和逐token激活的对称量化，W3A3使用非对称设置。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.04031)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

Wan1.3B VBench 67.21，对QVGen 63.56、BF16 66.28；CogVideoX2B为64.42，对62.80和65.57。最激进配置最高改善6.60分。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | Wan1.3B VBench 67.21，对QVGen 63.56、BF16 66.28；CogVideoX2B为64.42，对62.80和65.57。最激进配置最高改善6.60分。 |
| 压缩倍率 | 9 | Wan1.3B VBench 67.21，对QVGen 63.56、BF16 66.28；CogVideoX2B为64.42，对62.80和65.57。最激进配置最高改善6.60分。 |
| 创新性 | 9 | 式5/6令教师权重随t从噪声端到数据端指数衰减，原生flow目标权重互补；式11在后期关闭CFG。W4A4使用逐通道权重和逐token激活的对称量化，W3A3使用非对称设置。 |
| 可复现性 | 5 | 训练使用24–64张H20及视频数据。Qwen演示只执行W4A4前向与调度公式数值测试，没有视频QAT、VBench或原生去噪时间，不能称为DSA完整复现。 |

本地验证：以真实Qwen3-0.6B权重运行数值组件，结果状态`executed`，`full_paper_reproduced=false`。详见[README](../../../../scripts/quantization/2609.04031/README.md)及[原始结果](../../../../scripts/quantization/2609.04031/results.json)。

Qwen is autoregressive, has no native denoising time, video target or CFG. Exact stage functions tested independently; full Qwen forward only validates W4A4. No DSA video training or VBench reproduction; paper needs 24-64 H20 GPUs and synthetic video data.

## 5. 局限性与未来展望

训练使用24–64张H20及视频数据。Qwen演示只执行W4A4前向与调度公式数值测试，没有视频QAT、VBench或原生去噪时间，不能称为DSA完整复现。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

量化误差可以随生成阶段改变；应调节可靠监督的来源，而非只调一个全局蒸馏系数。
