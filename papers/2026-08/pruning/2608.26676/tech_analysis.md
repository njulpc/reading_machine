# 深度技术分析：FOCUS & RePAIR: Mitigating Text Degeneration via Token-Level Guidance for Pruned Large Language Models

> arXiv: [2608.26676](https://arxiv.org/abs/2608.26676)
> v1 提交日期：2026-08-27
> 主分类：Computation and Language (cs.CL)
> 分类：cs.CL, cs.AI, cs.LG
> 作者：Junyoung Lee, Sehyeon Park, Shinhyoung Jang, Seonha Ryu, Hojeong Kim, Hyunsei Lee, Il Hong Suh, Yeseong Kim
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：剪枝/稀疏。

**一句话总结**：FOCUS 与 RePAIR 不只恢复剪枝后的 perplexity，而是针对重复循环的进入风险和持续性做 token 级蒸馏修复。

## 2. 研究背景与动机

论文直接针对的瓶颈是：Pruning is a practical approach to compress large language models (LLMs), but it can amplify text degeneration, especially repetition loops, even when perplexity and task accuracy remain largely unchanged. 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- 把退化动力学拆成 loop entry 与 persistence，并用 plausible alternative 的 escape mass 解释后者。
- FOCUS 强化教师高置信区域，压制剪枝后概率泄漏。
- RePAIR 以循环起点附近的正负 continuation pair 和 margin loss 保留逃逸路径。

- 核心区别：FOCUS 与 RePAIR 不只恢复剪枝后的 perplexity，而是针对重复循环的进入风险和持续性做 token 级蒸馏修复。

## 4. 实验设计与结果

官方全文在开放续写与指令生成上比较剪枝基线、普通恢复微调和两种目标；两者持续降低重复并改善生成质量，而 perplexity/任务准确率原本可能几乎不变。论文未给可跨设置汇总的单一百分点。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

依赖可构造的重复样例与教师分布；采样温度会改变 escape mass，修复训练成本和对非重复任务的潜在偏置需继续审计。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

压缩后恢复应针对行为失效模式设计，不能把 perplexity 接近原模型当作生成稳定性已恢复。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
