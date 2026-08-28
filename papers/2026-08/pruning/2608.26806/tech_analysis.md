# 深度技术分析：Multi-Image Visual Token Pruning in Large Visual Language Models

> arXiv: [2608.26806](https://arxiv.org/abs/2608.26806)
> v1 提交日期：2026-08-27
> 主分类：Computer Vision and Pattern Recognition (cs.CV)
> 分类：cs.CV
> 作者：Rongyang Zhang, Chengqiang Lu, Cong Li, Hongchao Gu, Tingjia Shen, Xuyang Zhi, Qimeng Wang, Yan Gao 等
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：剪枝/稀疏。

**一句话总结**：AVTP 不依赖 attention score，按架构选择剪枝层并按多图重要性动态分配视觉 token，兼容 FlashAttention。

## 2. 研究背景与动机

论文直接针对的瓶颈是：With the growing demand for processing multiple image sequences in real-world applications, various visual token pruning methods have emerged to mitigate the computational and context length constraints faced by Large Vision Language Models (LVLMs). 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- 先分析不同 LVLM 的视觉注意演化以选择剪枝层。
- 多图输入中按图像重要性分配不同 token 保留比例。
- 训练免费且不需要显式 attention matrix。

- 核心区别：AVTP 不依赖 attention score，按架构选择剪枝层并按多图重要性动态分配视觉 token，兼容 FlashAttention。

## 4. 实验设计与结果

Qwen3VL-8B 达到 2× 推理加速并保留 96.1% 原准确率；InternVL3.5-8B 保留 94.1%，LLaVA-OV-7B 甚至超过未剪基线。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

重要性估计和层选择仍由经验分析驱动；不同分辨率、图片数量和 FlashAttention 后端会改变收益，超过基线也可能来自正则化而非稳定现象。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

视觉 token 剪枝应把预算在图片之间动态分配，并用不 materialize attention 的评分器对齐现代 kernel。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
