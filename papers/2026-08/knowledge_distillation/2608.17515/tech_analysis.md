# Beyond FLOPs: Energy-Aware Knowledge Distillation for Sustainable LLMs on Code-Related Task

- arXiv: [2608.17515](https://arxiv.org/abs/2608.17515)
- 提交日期（v1）：2026-08-18
- 作者：Enrique Barba Roque, Luís Cruz, Annibale Panichella
- 分类：cs.SE, cs.AI
- 证据边界：基于 arXiv 摘要与 20 页 v1 PDF。能耗绝对值依赖 RTX 4090/AMD 7900X、数据集和测量协议，不应跨硬件直接比较。

## 1. 核心速览

**研究主题：** 把实测 CPU/GPU 推理能耗的代理模型加入多目标知识蒸馏，以替代并检验 FLOPs 这一常用效率指标。

**一句话总结：** 能耗代理在 clone detection 上把中位推理能耗从 5,355.83 J 降至 3,604.50 J（-39%）；对 CodeT5+ 代码摘要，最节能 student 比 830 MB teacher 节能 90%，但 ROUGE-L 从 0.229 降至 0.194。

## 2. 研究背景与动机

蒸馏论文通常把 FLOPs 当成能耗代理，但同样 FLOPs 在不同激活函数、padding、kernel 与硬件上可能对应完全不同的时间和能耗。若多目标搜索直接优化错误代理，所得模型未必真正节能。论文扩展 Morph 多目标蒸馏，将模型大小、效果、鲁棒性和效率同时纳入搜索，并用实测能耗训练 surrogate。

## 3. 核心方法与创新点

1. **能耗 surrogate。** 用 Latin Hypercube Sampling 覆盖 student 超参数空间，对每个样本配置重复测量 CPU/GPU 能耗，训练 Gradient Boosting Regression 预测能耗。
2. **替换优化目标。** 在 Morph 中用预测 CPU+GPU Joules 替代 FLOPs，搜索 Pareto front；最终模型仍以真实能耗复测。
3. **生成任务扩展。** 对 CodeT5+-220M 代码摘要搜索 1–12 层、16–768 hidden size、1–12 heads 等架构和训练超参，以 size/energy/ROUGE-L 为三目标。
4. **weight subcloning 与在线蒸馏。** 先用约 80k token 的 teacher 激活排序，复制重要 neuron/head 权重到 student；由于生成 logits 体积巨大，训练时同时加载 teacher/student，以平均 KL 与 ground-truth cross entropy 为损失。

## 4. 实验设计与结果

- 任务：BigCloneBench clone detection、Devign vulnerability prediction、The Heap 上的 Python code summarization；teacher 为 GraphCodeBERT 与 CodeT5+-220M。
- 能耗协议：AMD Ryzen 9 7900X + RTX 4090，EnergiBridge（RAPL/NVML），每模型随机顺序执行 20 次并取中位数，测量仅含 inference。
- FLOPs 可靠性：clone detection 中 FLOPs 与能耗不显著相关；vulnerability prediction 有统计相关，但相同 FLOPs 仍出现不同能耗。
- 能耗优化：clone detection 中能耗 surrogate 虽使 GFLOPs 增加 21%，却使中位能耗下降 39%，`p<0.01, A12=0.925`；vulnerability prediction 能耗反增约 30%，差异不显著（`p>0.2`）。
- 生成任务：teacher 为 830 MB、82,396 J、ROUGE-L 0.229；最准确 student 为 114 MB（-86%）、13,600 J（-83%）、0.199（-13%）；最节能 student 为 157 MB、8,059 J（-90%）、0.194（-15%）。

## 5. 局限性与未来展望

- 只在一套硬件与三个 SE 任务上测量；surrogate 本身必须重做实测，迁移到其他硬件的成本较高。
- 生成效果主要用 ROUGE-L，无法衡量语义等价；0.18 的可接受阈值来自有限人工观察。
- 采用标准 KL+CE，未比较更新的蒸馏损失；在线 teacher 使搜索训练昂贵。
- The Heap 上 teacher 自身只有约 0.22 ROUGE-L，说明分布外泛化较弱；节能收益伴随不可忽略的质量下降。

## 6. 学术启发

“压缩倍率”不应只由参数或 FLOPs 定义。真正部署目标是任务×软件×硬件的联合函数，FLOPs 只给出数学上界。一个实用流程是先用廉价代理探索，再对 Pareto 候选做真实延迟、能耗和内存复测；如果代理与目标不相关，应把测量模型直接纳入搜索。

