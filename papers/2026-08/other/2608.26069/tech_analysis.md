# 深度技术分析：Group-Shared Low-Rank Approximation for Mobile-Efficient Pointwise Convolutions in Large-Kernel CNNs

> arXiv: [2608.26069](https://arxiv.org/abs/2608.26069)
> v1 提交日期：2026-08-26
> 分类：cs.LG
> 作者：Hao Luo, Yiting Yang, Wenyi Zhao, Man Jiang, Zhijun Lin, Ghulam Mohiuddin, Ting Jiang, Kunming Luo 等
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：其他压缩与高效推理；Group-Shared Low-Rank Approximation for Mobile-Efficient Pointwise Convolutions in Large-Kernel CNNs。

**一句话总结**：CGS 对 large-kernel CNN 中真正占参数主导的 pointwise convolution 做组共享低秩分解，用共享投影加组专属对角缩放降低存储。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：Large-kernel Convolutional Neural Networks (CNNs) deliver remarkable performance in vision tasks by significantly expanding receptive fields, yet their quadratic parameter growth critically impedes storage-efficient edge deployment. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- 将 pointwise convolution 写成与 SVD 同构的低秩 down/up projection。
- 多个 channel group 共享高成本投影矩阵。
- 仅保留低成本 group-specific diagonal scales 适配组差异。

- 方法的核心区别是：CGS 对 large-kernel CNN 中真正占参数主导的 pointwise convolution 做组共享低秩分解，用共享投影加组专属对角缩放降低存储。

## 4. 实验设计与结果

RepLKNet-31B 等模型中 pointwise convolution 占参数超过 87%；在 RepLKNet、ConvNeXt、SLaK 上，CGS 在竞争性精度下显著降低存储、加载带宽和加载延迟。摘要未给统一压缩倍数。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

共享投影可能限制组特异表达；收益集中于 large-kernel CNN，移动端真实 kernel、量化叠加和不同 rank 的端到端延迟仍需公开。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

先重新做参数归因：优化传统上被关注的 depthwise 部分，可能错过真正占存储的 pointwise 层。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
