# CC-4DGS: Computational Deformation and Point-Cloud Compression for Storage-Efficient Dynamic Gaussian Splatting

- arXiv ID：2609.02184
- 作者：Kyungdae Park, Chae Eun Rhee
- v1实际提交：2026-09-02T06:47:19Z（UTC）；2026-09-02T14:47:19+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV)
- 本次归类：量化；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.02184)；[官方HTML全文](https://arxiv.org/html/2609.02184)；[PDF](https://arxiv.org/pdf/2609.02184)

## 1. 核心速览

研究主题：量化。CC4DGS 联合压缩动态形变场和高斯属性，在相近渲染质量下降低动态场景存储。

## 2. 研究背景与动机

动态高斯表示同时包含时空形变与大量属性，单独压缩其中一项会留下主要存储瓶颈。

## 3. 核心方法与创新点

- CDF以稠密哈希及小神经解码器表达形变
- CCA让位置与SH-DC保留32位、旋转尺度不透明度12位，以条件自编码器压缩SH-AC并配合256项残差码本及Zstandard。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.02184)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

N3DV的CDF基线86MB/32.07dB，经CCA为30MB/32.06dB（约2.87倍）；Technicolor从93MB/33.29dB到32MB/33.30dB。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 9 | N3DV的CDF基线86MB/32.07dB，经CCA为30MB/32.06dB（约2.87倍）；Technicolor从93MB/33.29dB到32MB/33.30dB。 |
| 压缩倍率 | 8 | N3DV的CDF基线86MB/32.07dB，经CCA为30MB/32.06dB（约2.87倍）；Technicolor从93MB/33.29dB到32MB/33.30dB。 |
| 创新性 | 8 | CDF以稠密哈希及小神经解码器表达形变；CCA让位置与SH-DC保留32位、旋转尺度不透明度12位，以条件自编码器压缩SH-AC并配合256项残差码本及Zstandard。 |
| 可复现性 | 7 | 不能把不同表示方法的容量比都归给量化。Qwen演示仅迁移条件AE、残差码本及标量量化组件，没有场景、CDF和真实渲染。 |

本地验证：以真实Qwen3-0.6B权重运行数值组件，结果状态`executed`，`full_paper_reproduced=false`。详见[README](../../../../scripts/quantization/2609.02184/README.md)及[原始结果](../../../../scripts/quantization/2609.02184/results.json)。

Qwen rows and row statistics replace SH-AC/geometric conditions for component verification only. 8D latent, 8bit latent, mu=255 and 40 training steps are demo choices, not claimed paper defaults. No CDF deformation hash, scene rendering, archive Zstandard, or compressed Qwen checkpoint.

## 5. 局限性与未来展望

不能把不同表示方法的容量比都归给量化。Qwen演示仅迁移条件AE、残差码本及标量量化组件，没有场景、CDF和真实渲染。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

不同属性的视觉敏感度应决定不同码率；条件与残差量化可减少只靠统一位宽的损失。
