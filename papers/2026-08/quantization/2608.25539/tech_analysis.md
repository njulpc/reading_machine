# 深度技术分析：CropCop: An Auditable 120-Class Plant-Health Model from Benchmark Reconstruction to a Quantised Runtime Artifact

> arXiv: [2608.25539](https://arxiv.org/abs/2608.25539)
> v1 提交日期：2026-08-26
> 分类：cs.CV, cs.LG
> 作者：Rana Muhammad Ahmed, Sabahat Abbas
> 证据范围：arXiv 官方摘要与 v1 官方 HTML 全文

## 1. 核心速览

**研究主题**：量化；CropCop: An Auditable 120-Class Plant-Health Model from Benchmark Reconstruction to a Quantised Runtime Artifact。

**一句话总结**：CropCop 的价值不在新量化器，而在把数据去重、验证集 PTQ、转换后 INT8 图与最终 PTE 文件逐层审计到可执行工件。

## 2. 研究背景与动机

论文从以下具体瓶颈出发：A plant-health score can appear precise while resting on duplicated image families, a long-tailed label space, or a runtime file that was never evaluated. 这意味着单看参数量或最终任务分数不足以评价方案，还必须核对训练/校准成本、真实执行格式、token 或状态驻留量，以及方法是否在部署时引入新的算子与元数据。

## 3. 核心方法与创新点

- 先冻结零跨 split 重复的 109,107 图像、120 类 benchmark。
- 仅用验证集选择 dynamic activation 与 per-channel weight INT8 PTQ。
- 直接执行 ExecuTorch/XNNPACK PTE，并逐样本比较转换图与最终工件。

- 方法的核心区别是：CropCop 的价值不在新量化器，而在把数据去重、验证集 PTQ、转换后 INT8 图与最终 PTE 文件逐层审计到可执行工件。

## 4. 实验设计与结果

ConvNeXt-Tiny 参考为 98.51% accuracy/96.87% macro-F1；MobileNetV4 派生模型为 98.46%/96.27%。22.60 MiB PTE 达 98.46%/96.23%，16,363 个 top-1 中仅 6 个在 INT8 图与 PTE 间改变。

这些数字按论文给定模型、数据集、硬件与预算转述；没有跨设置统一口径的指标时，本分析保留证据边界，不用推算值替代作者未报告的实验。

## 5. 局限性与未来展望

没有提出新 distillation 方法，也未在实体 Android 硬件验证；闭集内部测试不能代表新农场/相机，类别均衡指标仍显示小幅损失。

下一步应在等质量、等硬件与等内存预算下复核端到端延迟，并公开失效样本、元数据开销和跨模型迁移结果。

## 6. 学术启发

量化复现应把“Python fake quant 相同”推进到“导出工件逐样本相同”，并对数据泄漏与类别尾部单独审计。

更一般地，模型压缩研究需要把表示层压缩、kernel 可利用性和真实系统收益分开测量，再用同一质量约束闭环。
