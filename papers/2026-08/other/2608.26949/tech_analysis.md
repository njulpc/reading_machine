# 深度技术分析：A Table Is Worth 64 Tokens: Pixel-level Compression for Multi-Table Document Question Answering

> arXiv: [2608.26949](https://arxiv.org/abs/2608.26949)
> v1 提交日期：2026-08-27
> 主分类：Artificial Intelligence (cs.AI)
> 分类：cs.AI
> 作者：Iñigo Alonso, Mirella Lapata
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：其他压缩与高效推理。

**一句话总结**：该方法先用高度像素压缩的表格只做相关性筛选，再以原分辨率读取少数相关表，避免低清表格诱发更长推理抵消 token 节省。

## 2. 研究背景与动机

论文直接针对的瓶颈是：Answering questions over real-world documents requires processing long inputs that interleave text with tables. 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- 在 5 个 VLM、2 个 benchmark、5 档 visual-token budget 上审计像素压缩。
- 第一阶段以低分辨率多表上下文选择相关表。
- 第二阶段只对入选表使用原分辨率完成问答。

- 核心区别：该方法先用高度像素压缩的表格只做相关性筛选，再以原分辨率读取少数相关表，避免低清表格诱发更长推理抵消 token 节省。

## 4. 实验设计与结果

长文档上，两阶段方案比原分辨率单步 QA 节省 41% 总 token 并提高 7 个准确率点；比最省 token 的单步压缩配置再少 15% token，且无准确率损失。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

收益依赖可分解的“筛表—答题”任务；相关表召回错误不可恢复，视觉 token 与文本 token 成本也可能因后端计价不同。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

输入压缩可利用非对称信息需求：粗表示足以检索，精表示只留给最终推理。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
