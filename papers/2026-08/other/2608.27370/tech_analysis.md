# 深度技术分析：Puro-2B: Poor Lab's Qwen2-1.5B Trained on RTX 5090 within $5090

> arXiv: [2608.27370](https://arxiv.org/abs/2608.27370)
> v1 提交日期：2026-08-27
> 主分类：Computation and Language (cs.CL)
> 分类：cs.CL, cs.LG
> 作者：Kairong Luo, Jiarui Cui, Yaorui Yin, Shengqi Chen, Yiming Yang, Linxiang Gao, Yanmohan Wang, Mingzhe Zhang 等
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：其他压缩与高效推理。

**一句话总结**：Puro-2B 给出消费级 RTX 5090 上从零训练 2B 模型的开放配方，FP8、优化器与数据课程共同降低预训练成本。

## 2. 研究背景与动机

论文直接针对的瓶颈是：Language model pretraining has become almost synonymous with prohibitive cost, placing it out of reach for much of the academic and open-source communities. 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- 在 RTX 5090 上使用 FP8 低精度训练。
- 结合 hyperball optimization、curriculum model averaging 与完整数据 recipe。
- 以不同 token budget 的模型族拟合成本—性能 scaling law。

- 核心区别：Puro-2B 给出消费级 RTX 5090 上从零训练 2B 模型的开放配方，FP8、优化器与数据课程共同降低预训练成本。

## 4. 实验设计与结果

最佳模型用最多 1.4T token、训练计算成本低于 6.9k 美元，并接近 Qwen2.5-1.5B；拟合的 Puro Cost Scaling Law 估计约 4.4k 美元可达到 Qwen2-1.5B 的评测水平。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

成本口径受电价、硬件采购/折旧与并行效率影响；FP8 是配方组件而非独立量化消融，接近 Qwen 的结论只适用于其评测协议。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

低精度价值应以完整训练账单和可复现 recipe 呈现，而不只报告理论 FLOPs 或单个 kernel。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
