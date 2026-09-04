# Beyond Retrieval: Progressive Latent Memory Evolution for Streaming Video Understanding

- arXiv ID：2609.04131
- 作者：Hongyu Qu, Guangming Yao, Ling Xing, Xiaobin Hu, Rongxing Ding, Guibin Zhang, Fan Zhang, Yi Yuan, Xiangbo Shu, Shuicheng Yan
- v1实际提交：2026-09-03T17:28:14Z（UTC）；2026-09-04T01:28:14+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV)
- 本次归类：其他模型压缩；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.04131)；[官方HTML全文](https://arxiv.org/html/2609.04131)；[PDF](https://arxiv.org/pdf/2609.04131)

## 1. 核心速览

研究主题：其他模型压缩。LatentStream 用查询无关的分层潜在记忆持续压缩视频，再按问题读取证据。

## 2. 研究背景与动机

无限增长的视频流无法一直保留全部视觉token；预先绑定查询又不能支持后来的问题。

## 3. 核心方法与创新点

- 短中长期记忆以Jenks式分组逐步合并
- 潜在组扩大感受野，检索后渐进吸收证据，并以组熵奖励调整记忆表示。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.04131)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

Qwen2.5-VL-7B、1fps在OVO-Bench从54.0升至64.2，StreamingBench从73.9至76.9；峰值显存30.80降至21.97GB，TPOT 6.45降至3.16ms，但TTFT 7.63升至8.41秒。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | Qwen2.5-VL-7B、1fps在OVO-Bench从54.0升至64.2，StreamingBench从73.9至76.9；峰值显存30.80降至21.97GB，TPOT 6.45降至3.16ms，但TTFT 7.63升至8.41秒。 |
| 压缩倍率 | 8 | Qwen2.5-VL-7B、1fps在OVO-Bench从54.0升至64.2，StreamingBench从73.9至76.9；峰值显存30.80降至21.97GB，TPOT 6.45降至3.16ms，但TTFT 7.63升至8.41秒。 |
| 创新性 | 8 | 短中长期记忆以Jenks式分组逐步合并；潜在组扩大感受野，检索后渐进吸收证据，并以组熵奖励调整记忆表示。 |
| 可复现性 | 7 | 方法无需离线训练，但推理中的潜在记忆优化增加首token开销；查询无关压缩可能丢失后来相关的细节。熵置信度并不保证证据真实，需审计检索与生成。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

方法无需离线训练，但推理中的潜在记忆优化增加首token开销；查询无关压缩可能丢失后来相关的细节。熵置信度并不保证证据真实，需审计检索与生成。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

应把长期记忆压缩与问题触发的读取分别设计，使空间预算独立于视频持续时长。
