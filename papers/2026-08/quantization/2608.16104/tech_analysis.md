# Nexus：技术精读

> arXiv: [2608.16104](https://arxiv.org/abs/2608.16104) · submitted 2026-08-17 · Yizhao Wang · cs.CV

## 1. 核心速览

**研究主题**：MoE、线性注意力与 per-expert 4-bit QAT 联合的高效文生图 rectified-flow 模型。
**一句话总结**：Nexus 不是把三种效率技术串联，而是让稀疏激活、DeltaNet 线性注意力和专家独立量化统计共同训练。

## 2. 研究背景与动机

高分辨率生成同时受 FFN 计算、二次注意力和权重/激活内存约束；单独剪枝、线性注意力或低比特会留下另一瓶颈，并可能累积质量损失。

## 3. 核心方法与创新点

- MoE FFN 仅激活部分专家，gated DeltaNet 将注意力复杂度降为线性。
- 所有 linear layer 做 QAT：权重对称 INT4、激活非对称 FP4。
- 激活范围按专家动态统计，在 **99.9 percentile** 裁剪；每个专家独立学习 scale/zero-point，router 与内部 state 保持高精度。

## 4. 实验设计与结果

在 COCO-30K 与 LAION-5K 用 zero-shot FID/CLIP 评估，效率在单张 A100-80GB 测量。Nexus 共 7B 参数但只激活 **1.6B**；相对 SD3-Medium 约 **2.8×** 加速、**1.7×** 峰值内存下降。论文还报告 4-bit attention QAT 在 RTX 5090 约 **1.5×** 加速，并声称质量可比 SDXL/SD3。

## 5. 局限性与未来展望

单作者稿件的训练细节和独立复现实证有限；FP4 速度依赖新硬件，A100 上的效率不等于原生 FP4。组合设计也难分离每个组件在不同分辨率的收益。

## 6. 学术启发

MoE 量化应按专家维护激活统计；统一全层 scale 会掩盖专家分布差异。router/state 保持高精度也是混合精度边界的实用选择。

**证据边界**：已核对官方 HTML 全文；复现把 Qwen3 FFN 行分组模拟专家并实现 per-expert INT4/FP4 fake quant，不声称复现图像生成训练。
