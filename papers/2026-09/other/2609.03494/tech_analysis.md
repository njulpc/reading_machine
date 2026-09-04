# GrowPage: On-Demand KV Budgeting for Efficient LLM Reasoning Serving

- arXiv ID：2609.03494
- 作者：Qiankun Ma, Yanjiang Zhou, Zinan Xiong, Haofei Wang, Zhen Song, Yang Xiang, Ziyao Zhang, Hairong Zheng
- v1实际提交：2026-09-03T07:53:05Z（UTC）；2026-09-03T15:53:05+08:00（Asia/Shanghai）
- 主分类：Artificial Intelligence (cs.AI)；全部分类：Artificial Intelligence (cs.AI)
- 本次归类：其他模型压缩；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.03494)；[官方HTML全文](https://arxiv.org/html/2609.03494)；[PDF](https://arxiv.org/pdf/2609.03494)

## 1. 核心速览

研究主题：其他模型压缩。GrowPage 根据实时注意力需求，在压缩已有KV与申请新页之间决策。

## 2. 研究背景与动机

固定KV预算忽视请求间不同的记忆需求，过早裁剪损害质量，过晚扩容浪费服务容量。

## 3. 核心方法与创新点

- 双时间尺度查询摘要估计注意力覆盖需求
- 以达到累计概率p所需的最小token数形成需求信号，在页边界选择压缩或扩容，并接入PagedAttention连续批处理和前缀缓存。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.03494)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

DeepSeek-R1-Distill-Llama-8B平均质量68.7，对完整vLLM 69.2；吞吐2417对1472 token/s，Zipage为1936。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | DeepSeek-R1-Distill-Llama-8B平均质量68.7，对完整vLLM 69.2；吞吐2417对1472 token/s，Zipage为1936。 |
| 压缩倍率 | 8 | DeepSeek-R1-Distill-Llama-8B平均质量68.7，对完整vLLM 69.2；吞吐2417对1472 token/s，Zipage为1936。 |
| 创新性 | 8 | 双时间尺度查询摘要估计注意力覆盖需求；以达到累计概率p所需的最小token数形成需求信号，在页边界选择压缩或扩容，并接入PagedAttention连续批处理和前缀缓存。 |
| 可复现性 | 8 | 吞吐依赖服务负载与调度，不是单请求固定加速；自适应页数不能换算成统一KV压缩率。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

吞吐依赖服务负载与调度，不是单请求固定加速；自适应页数不能换算成统一KV压缩率。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

将精度预算映射为分页资源决策，比孤立优化token选择更贴近部署。
