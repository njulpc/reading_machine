# Precision-Aware Variable Bit Processing Elements for Hardware-Efficient Systolic Array Designs

> arXiv: [2608.22378](https://arxiv.org/abs/2608.22378) · v1: 2026-08-23 · 主分类: cs.AR
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：面向深度学习 systolic array 的可变精度近似浮点乘法。
**一句话总结**：论文在 FP32、TF32、BF16 multiplier 的 partial-product matrix 中做列截断并配置正负 compressor，再用 NSGA-II 搜索硬件-精度 Pareto 解；CIFAR-10 top-10 精度设计报告 66%–92% footprint、60%–93% power 节省与 21%–54% delay 改善。

## 2. 研究背景与动机

统一使用精确乘法器会为误差容忍的 DNN 推理支付过高面积和功耗，而只切换格式又没有利用 mantissa partial product 的近似空间。目标是在 weight-stationary 阵列中联合设计格式和电路近似。

## 3. 核心方法与创新点

- 对 FP32/TF32/BF16 的 PPM 选择性截列，减少乘法器逻辑。
- 正、负 compressor 处理截断残差和符号相关误差。
- NSGA-II 同时搜索面积、功耗、时延和应用精度，而非手工选 bit。
- 把 approximate PE 嵌入完整 systolic array，再以 CNN 任务验证误差容忍度。

## 4. 实验设计与结果

模型覆盖 MNIST、F-MNIST、CIFAR-10。CIFAR-10 上入选的 top-10 CNN-performance 设计相对文献精确实现节省 66%–92% footprint、60%–93% power，并改善 21%–54% delay；作者称分类精度可比。区间跨多个设计和格式，不能把三个上界同时视为一个设计点。

## 5. 局限性与未来展望

验证以小型 CNN/数据集和综合指标为主，距离现代 Transformer、实际布线后频率与端到端能耗仍有差距。近似误差也不是标准 PTQ 误差，复现只能模拟数值路径，不能声称复现 ASIC/FPGA PPA。

## 6. 学术启发

低精度研究应把“数值格式”和“实现电路”分开建模；Pareto 搜索得到的是一组部署点，不应只报最优单指标。模型侧还可用校准样本把各层误差预算映射到 PE 设计。
