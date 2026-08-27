# 深度技术分析：APT: Accelerating Diffusion Transformers via Attention Probability-Guided Pruning and Quantization

> arXiv: [2608.25380](https://arxiv.org/abs/2608.25380)
> v1 提交日期：2026-08-26
> 分类：cs.AR
> 作者：Sungyeob Yoo, Seeyeon Kim, Joonyong Park, Seunghee Han, Joo-Young Kim
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：量化；APT: Accelerating Diffusion Transformers via Attention Probability-Guided Pruning and Quantization。

**一句话总结**：APT 用预测的注意力概率同时决定元素是否剪除和剩余元素的精度，再以软硬件协同执行不规则稀疏与双精度 DiT attention。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：Recent advances in generative AI have significantly increased the demand for high-resolution image and video generation, positioning diffusion models as a core technology. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- APDT 用两个阈值从 attention probability 同时产生 pruning mask 与 precision assignment。
- TAFA 利用 diffusion timestep 相似性预测概率，兼容 memory-efficient FlashAttention。
- 专用加速器实现动态 mask、地址翻译、双精度计算单元和 tile dataflow。

- 方法的核心区别是：APT 用预测的注意力概率同时决定元素是否剪除和剩余元素的精度，再以软硬件协同执行不规则稀疏与双精度 DiT attention。

## 4. 实验设计与结果

在 PixArt-α、Stable Diffusion 3 和 FLUX 上，作者报告相对 NVIDIA A100 最高 8.16 倍加速、14.98 倍能效；相对 EXION 最高 3.01 倍加速、2.04 倍能效。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

收益依赖定制硬件与时序相似性；用概率代理误差可能漏掉低概率但关键贡献，跨 timestep 预测误差和阈值校准也会随 prompt/分辨率变化。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

同一个连续重要性分数可以联合产生 sparsity 与 precision，而不是先剪枝再独立量化。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
