# 深度技术分析：Minima-KV: Retention-Preserving KV Cache Compression with Mixed-Format Paged Attention

> arXiv: [2608.23834](https://arxiv.org/abs/2608.23834)
> v1 提交日期：2026-08-24
> 分类：cs.AI
> 证据：arXiv 官方摘要与官方全文（HTML/PDF）

## 1. 核心速览

**研究主题**：量化；Minima-KV: Retention-Preserving KV Cache Compression with Mixed-Format Paged Attention。

**一句话总结**：Minima-KV 以 FP8 保存近期/锚点页、以打包 TQ3 保存旧页，并让异构格式直接参加统一 softmax，避免保留稠密影子缓存。

## 2. 研究背景与动机

这项工作针对的不是抽象的“模型更小”，而是部署链条中的可测瓶颈：模型状态、token/KV、训练监督或实际数据搬运。作者在官方摘要中把问题界定为：The key-value (KV) cache is a primary capacity and bandwidth bottleneck in long-context LLM serving。因此，评价重点应同时包含任务质量、资源口径与实现边界，而不能只报告单一压缩率。

## 3. 核心方法与创新点

- 三层 retention-preserving paged KV 层级。
- 格式专用内核分别计算 attention partial state，再做全局归一化在线 softmax 合并。
- 页面所有权安全转换，所有活跃页仍可寻址。

- 核心创新可概括为：Minima-KV 以 FP8 保存近期/锚点页、以打包 TQ3 保存旧页，并让异构格式直接参加统一 softmax，避免保留稠密影子缓存。

## 4. 实验设计与结果

Qwen3.6-27B 单卡报告 18.3 KiB/token，相对 BF16 为 3.50×、相对 FP8 为 1.75×；LongBench v2 在 16K/32K/64K 的下降为 0.80/0.60/0.40 个百分点，单对 canary 测得 3.625× 活跃 KV 压缩但吞吐仅 0.9821×。

上述数字均来自论文官方全文或摘要；它们是作者在特定模型、数据集、硬件和预算下的报告，不自动构成跨模型普遍结论。复现实验应优先固定基线、质量阈值、真实驻留/读取字节和端到端延迟口径。

## 5. 局限性与未来展望

证据只覆盖一款模型和一张 RTX PRO 6000；聚合字节账目尚缺逐层/元数据完整对账，多请求、长稳态和质量覆盖有限。

后续最有价值的验证是把方法放进真实服务或训练路径，使用等预算基线、跨模型/跨任务测试和公开可审计的内存—延迟—质量三维记录。

## 6. 学术启发

KV 压缩必须同时报告驻留字节、读取字节、是否存在 dense shadow 与直接解码吞吐。

这篇论文也提示：压缩研究应主动公布负结果和失效区间，并区分算法表示压缩、kernel 可利用性与真实端到端收益。
