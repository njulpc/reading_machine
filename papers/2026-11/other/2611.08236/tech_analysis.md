# Beyond Quadratic Attention: Separable Gaussian Operators for ODE Vision Transformers

> arXiv: 2611.08236；v1：2026-11-05T16:17:48+00:00（UTC） / 2026-11-06T00:17:48+08:00（北京时间）。
> 分类：Machine Learning (cs.LG) ; Computer Vision and Pattern Recognition (cs.CV)。归档以 v1 北京时间月份为准。
> 证据：[官方摘要与提交历史](https://arxiv.org/abs/2611.08236)；[官方HTML全文](https://arxiv.org/html/2611.08236v1)。以下论文结果均为作者报告，本地结果另行标注。

## 1. 核心速览

**研究主题**：other / SSoG。

**一句话总结**：SSoG用可分离高斯空间算子替代dense attention以减少参数和计算；内存优势取决于基线是否使用融合kernel。

## 2. 研究背景与动机

共享深度或连续ODE虽减少独立参数，仍需多次执行token mixer。dense QK attention成本随N平方增长，且全局Lipschitz性质不成立。SSoG尝试把空间先验直接写进算子，既减去Q/K投影又避免完整token-pair矩阵。

## 3. 核心方法与创新点

1. 只投影V，不计算Q/K。每head有R个各向异性Gaussian atom，沿x/y独立归一化，输出为多个 `Ay V Axᵀ` 的softmax加权和。
2. 对平方网格，固定R的算术复杂度O(RN^(3/2)D)，不是O(ND)。宽度用softplus加正下界，防止核退化。
3. fixed版本的中心/尺度/混合权重不依赖输入；LookAt版本用有界tanh扰动中心、尺度和权重。fixed可证明全局Lipschitz，content-steered仅在有界token范数集合上有相应结论。
4. CLS不走二维Gaussian滤波，接收patch投影值均值；同一替换比较离散ViT、共享参数looped及连续深度ODE。

## 4. 实验设计与结果

CIFAR-100 224²上，同深度和训练配方下离散/连续设置Top1提升2.2–4.1点、参数少8.8–16.6%；looped提高5.4–8.1点。ImageNet D=768表2：连续MHA63.04→SSoG64.02，离散76.47→77.89，looped73.72→73.37，不能概括成全部获胜。

A40 FP16 profiling用10次warm-up和50次测量，输入分辨率至1024²。ODE最高吞吐+154%、峰值内存降低超过60%的基线不使用fused attention。附录表3严格isolated算子与fused MHA对照反而是SSoG更占内存：224²为47.6/29.2MiB，1024²为689.0/304.3MiB（2.26倍）。离散整模型固定参数部分与算子内存不可混为一谈。

cold-init连续配置NFE12、R4时fixed74.22%，full steering70.89%；可见内容条件化并非总能提升。本次无训练或硬件复跑。

## 5. 局限性与未来展望

主要比较dense attention，缺少线性attention/SSM对照；ImageNet收益收窄，looped可轻微下降。高分辨率测试是计算压力测试，不应直接当作高分辨率任务泛化证明。理论保证ODE解存在唯一，不保证分类精度。未来需融合SSoG kernel并做相同优化级别的算子与整模型双重比较。

## 6. 学术启发

渐近复杂度与实测内存可能方向相反；用数学量级解释趋势前，应固定kernel融合、模型总参数和batch。删掉Q/K并注入空间先验是一种结构替代，不是对任意预训练attention的无损压缩。

**四维评分（1–10，编辑判断而非客观排名）**：精度效果 7/10；压缩倍率 5/10；创新性 7/10；可复现性 6/10。

精度7：CIFAR改善、ImageNet looped略降；压缩5：参数少8.8–16.6%，非量化且内存对照依赖实现；创新7：算子结构与ODE全局适定性连接；复现6：公式明确，本次无训练/速度重跑。
