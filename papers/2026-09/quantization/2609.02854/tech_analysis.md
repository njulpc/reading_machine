# MuyBridge: Mobile Human Center-of-Mass Estimation from Monocular Video via Sparse Fusion

- arXiv ID：2609.02854
- 作者：Aidan Bradshaw, Marco Giordano, David Rode, Andreas Habersack, Elif Basokur, Annika Kruse, Markus Tilp, Michele Magno, Peter Wolf, Luca Benini, Christoph Leitner
- v1实际提交：2026-09-02T17:38:36Z（UTC）；2026-09-03T01:38:36+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV)
- 本次归类：量化；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.02854)；[官方HTML全文](https://arxiv.org/html/2609.02854)；[PDF](https://arxiv.org/pdf/2609.02854)

## 1. 核心速览

研究主题：量化。MuyBridge 联合姿态裁剪、INT8量化和少步深度估计，实现手机端人体质心测量。

## 2. 研究背景与动机

单摄像头质心估计既需要姿态又需要尺度深度，多模型流水线受端侧延迟与能耗限制。

## 3. 核心方法与创新点

- GroupFisher将姿态通道3336裁至2389，浅层较激进
- 逐通道对称W8、逐张量非对称A8
- 深度使用一致性蒸馏，UNet量化感知训练、VAE训练后量化，敏感注意力等保留FP16。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.02854)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

iPhone15质心误差33–41mm、范围误差2.3–6.6%；姿态63FPS、深度2.86Hz。子模块INT8为224FPS对FP32 123，不能当完整流水线；深度AbsRel从0.132到0.155。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | iPhone15质心误差33–41mm、范围误差2.3–6.6%；姿态63FPS、深度2.86Hz。子模块INT8为224FPS对FP32 123，不能当完整流水线；深度AbsRel从0.132到0.155。 |
| 压缩倍率 | 8 | iPhone15质心误差33–41mm、范围误差2.3–6.6%；姿态63FPS、深度2.86Hz。子模块INT8为224FPS对FP32 123，不能当完整流水线；深度AbsRel从0.132到0.155。 |
| 创新性 | 8 | GroupFisher将姿态通道3336裁至2389，浅层较激进；逐通道对称W8、逐张量非对称A8；深度使用一致性蒸馏，UNet量化感知训练、VAE训练后量化，敏感注意力等保留FP16。 |
| 可复现性 | 6 | Qwen只移植MLP的W8A8静态校准，保留注意力为FP32，没有GroupFisher、视觉训练、几何融合或ANE导出。 |

本地验证：以真实Qwen3-0.6B权重运行数值组件，结果状态`executed`，`full_paper_reproduced=false`。详见[README](../../../../scripts/quantization/2609.02854/README.md)及[原始结果](../../../../scripts/quantization/2609.02854/results.json)。

Qwen MLP PTQ component transfer only; attention and norms kept FP32 rather than paper FP16. No GroupFisher, pose retraining, UNet QAT, latent-consistency distillation, geometric fusion or Apple Neural Engine export. Vision datasets/models unavailable locally.

## 5. 局限性与未来展望

Qwen只移植MLP的W8A8静态校准，保留注意力为FP32，没有GroupFisher、视觉训练、几何融合或ANE导出。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

端侧压缩是多速率流水线的联合预算问题，不能只优化最快的子模型。
