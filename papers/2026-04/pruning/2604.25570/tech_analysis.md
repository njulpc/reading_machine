# 深度技术分析：Vision SmolMamba: Spike-Guided Token Pruning for Energy-Efficient Spiking State-Space Vision Models

## 1. 核心速览

**研究主题**：脉冲状态空间视觉模型：脉冲引导的时空 token 剪枝与线性复杂度架构。

**一句话总结**：Vision SmolMamba 把脉冲驱动动力学与线性时间选择性递归结合，核心为 Spike-Guided 时空 token 剪枝器（SST-TP，以脉冲激活强度与首发脉冲延迟估计 token 重要性、渐进移除冗余 token），SmolMamba 块将脉冲事件直接嵌入双向状态空间递归；ImageNet-1K、CIFAR10/100、CIFAR10-DVS、DVS128 Gesture 上能耗至少降低 1.5× 且精度持平或提升。

## 2. 研究背景与动机

脉冲 Transformer 的二次 token 交互与 SNN 稀疏事件驱动的本质相悖——用稠密二次注意力做脉冲计算浪费了 SNN 的能效优势。需要架构层面与脉冲天然对齐的线性复杂度方案。

## 3. 核心方法与创新点

- **SST-TP 剪枝器**：脉冲激活强度 + 首发脉冲延迟（时间信息）双信号估计 token 重要性，渐进剪枝且随 token 稀疏度高效扩展。
- **SmolMamba 块**：脉冲事件直接进入双向状态空间递归——SNN 与 Mamba 的深度杂交。
- **能效导向**：静态与事件相机数据上能耗降至少 1.5×、精度有竞争力。

## 4. 实验设计与结果

ImageNet-1K、CIFAR10/100（静态）+ CIFAR10-DVS、DVS128 Gesture（事件）：精度-能效权衡一致优于脉冲 Transformer 与 Spiking Mamba 变体。

## 5. 局限性与未来展望

局限：能耗为估算值，需神经形态硬件实测；Mamba 递归的顺序性与脉冲的并行事件性存在概念张力，长序列稳定性待考；模型规模限于视觉骨干，向 LLM 的扩展路径不明。未来方向：神经形态芯片部署实测、脉冲化 Mamba-LLM、与 SNN 量化（QB-LIF、EMD 评估）组合的全栈方案。

## 6. 学术启发

- SNN 与 SSM 的结合是架构创新的前沿：两者都强调事件/状态的稀疏动力学，天然契合。
- 脉冲信号（强度 + 首发延迟）作为 token 重要性度量是 SNN 独有的免费信号——模态特有信号的利用决定压缩方法的天花板。

---

*论文信息：arXiv:2604.25570，Bai Dewei, Peng Hongxiang 等，cs.CV*