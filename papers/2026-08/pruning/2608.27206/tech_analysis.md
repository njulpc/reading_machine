# 深度技术分析：PACE: A Unified Condense-and-Extract Paradigm for Fast VLM Inference

> arXiv: [2608.27206](https://arxiv.org/abs/2608.27206)
> v1 提交日期：2026-08-27
> 主分类：Computer Vision and Pattern Recognition (cs.CV)
> 分类：cs.CV, cs.AI
> 作者：Junjie Liu, Shengyuan Ye, Xu Chen
> 证据范围：arXiv 官方摘要、Submission history 与官方 HTML 全文

## 1. 核心速览

**研究主题**：剪枝/稀疏。

**一句话总结**：PACE 在视觉编码前先按像素信息密度下采样，再在编码后融合视觉与语言信号剪 token，同时压缩 encoder 与 LLM 两段成本。

## 2. 研究背景与动机

论文直接针对的瓶颈是：Vision-Language Models (VLMs) demonstrate exceptional visual reasoning capabilities, yet their inference costs escalate rapidly with the proliferation of visual tokens. 这类工作不能只看名义参数、token 或位宽，还需同时核对质量约束、额外元数据/控制器、真实 kernel 可利用性，以及训练或校准成本是否被转移到系统其他阶段。

## 3. 核心方法与创新点

- Adaptive Pixel Compressor 在进入 vision encoder 前压缩冗余像素。
- Dynamic Dual-Attention Extractor 融合 encoder 内部视觉信号和 LLM 语义信号。
- 训练免费地联合优化全局上下文和细节保留。

- 核心区别：PACE 在视觉编码前先按像素信息密度下采样，再在编码后融合视觉与语言信号剪 token，同时压缩 encoder 与 LLM 两段成本。

## 4. 实验设计与结果

Qwen2.5-VL-7B 仅使用 10% 视觉 token 时保留 93.8% 原性能，并将 TTFT 加速 3.1×。

上述数字均按论文给定模型、数据集、硬件和预算转述；没有统一汇总指标时保留作者的证据边界，不用推算值代替未报告实验。

## 5. 局限性与未来展望

像素下采样错误在 encoder 前不可逆；10% token 的结果依视觉任务和分辨率，dual-attention 的额外打分成本需计入端到端。

后续应在等质量、等硬件、等内存/通信预算下复核端到端时延，并公开最差样本、控制器与元数据成本，以及跨模型迁移结果。

## 6. 学术启发

视觉压缩要覆盖 encoder 之前的像素阶段，否则只剪 LLM token 会遗漏大量前端延迟。

更一般地，模型压缩应把数值/结构压缩、训练额外成本、kernel 可实现性和真实系统收益分开测量，再用共同的质量约束闭环。
