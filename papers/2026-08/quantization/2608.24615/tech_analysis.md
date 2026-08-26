# 深度技术分析：Quantization Effects on Bangla Language Understanding in Large Language Models: A Systematic Evaluation

> arXiv: [2608.24615](https://arxiv.org/abs/2608.24615)
> v1 提交日期：2026-08-25
> 分类：cs.CL
> 证据：arXiv 官方摘要与官方全文（HTML/PDF）

## 1. 核心速览

**研究主题**：量化；Quantization Effects on Bangla Language Understanding in Large Language Models: A Systematic Evaluation。

**一句话总结**：Bangla NLU 上量化稳健性主要由模型家族和格式决定，而不是简单由位宽决定：Qwen/LLaMA 的 GPTQ 稳定，GPT-OSS 的 GGUF-W8A16 可严重退化。

## 2. 研究背景与动机

这项工作针对的不是抽象的“模型更小”，而是部署链条中的可测瓶颈：模型状态、token/KV、训练监督或实际数据搬运。作者在官方摘要中把问题界定为：Post-training quantization lowers the memory footprint of Large Language Models (LLMs) and speeds up inference, which is why it is now common for on-device deployment。因此，评价重点应同时包含任务质量、资源口径与实现边界，而不能只报告单一压缩率。

## 3. 核心方法与创新点

- 三模型家族对比全精度与 GPTQ-Int8/GPTQ-Q8/GGUF-W8A16。
- 在五个 Bangla 零样本基准统一使用 lm-evaluation-harness。
- 按推理、常识和阅读理解任务拆分。

- 核心创新可概括为：Bangla NLU 上量化稳健性主要由模型家族和格式决定，而不是简单由位宽决定：Qwen/LLaMA 的 GPTQ 稳定，GPT-OSS 的 GGUF-W8A16 可严重退化。

## 4. 实验设计与结果

Qwen-2.5-7B 与 LLaMA-3.1-8B 的 GPTQ 在五基准绝对损失不超过 1.5%；GPT-OSS-20B 在推理任务最高损失 57.35%，而 BoolQ-BN 各格式较稳定。

上述数字均来自论文官方全文或摘要；它们是作者在特定模型、数据集、硬件和预算下的报告，不自动构成跨模型普遍结论。复现实验应优先固定基线、质量阈值、真实驻留/读取字节和端到端延迟口径。

## 5. 局限性与未来展望

检查点校准语料并不等价，尤其 GPT-OSS 格式与其他模型不同；零样本准确率不能解释内部误差，也没有吞吐/显存的同机测量。

后续最有价值的验证是把方法放进真实服务或训练路径，使用等预算基线、跨模型/跨任务测试和公开可审计的内存—延迟—质量三维记录。

## 6. 学术启发

部署评测必须覆盖目标语言和任务，不能用英语平均分替代量化风险审计。

这篇论文也提示：压缩研究应主动公布负结果和失效区间，并区分算法表示压缩、kernel 可利用性与真实端到端收益。
