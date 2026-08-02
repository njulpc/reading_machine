# 技术深度分析：Capturing Token Tendencies for Training-Free Token Pruning in Multimodal Large Language Models (arXiv:2607.28341)

> **论文**: Capturing Token Tendencies for Training-Free Token Pruning in Multimodal Large Language Models
> **作者**: Jie Ma, Zhike Qiu, Jie Gao, Jiayi Ji, Qian Chen, Xiaoshuai Sun, Rongrong Ji（厦门大学 多媒体可信感知与高效计算教育部重点实验室 等）
> **arXiv**: https://arxiv.org/abs/2607.28341
> **发表**: ACM Multimedia 2026 (MM '26)，2026年11月10–14日，巴西里约热内卢
> **项目主页**: https://github.com/JieMaMagic/Trend-aware-Pruning

---

## 一、核心速览

### 研究主题

多模态大语言模型（MLLMs）中的视觉 Token 免训练剪枝（Training-Free Token Pruning）。具体而言，本文研究如何在无需任何额外训练的前提下，动态、可逆地削减输入到 LLM 解码器的视觉 Token 数量，以缓解注意力机制二次复杂度带来的推理开销瓶颈，同时尽量保持多模态理解与推理性能。

### 一句话总结

本文提出 **Trend-aware Pruning（趋势感知剪枝）** 框架，将视觉 Token 剪枝从"单层快照式、不可逆的静态过滤"重新定义为"跨层时序轨迹建模问题"，通过捕捉注意力流的动量（momentum）来识别并重新激活那些浅层被低估但深层语义重要性上升的"后起之秀"（late-blooming）Token，在最激进设置下将最终层视觉 Token 削减至约 23 个（削减超过 77.8%），同时保持有竞争力的性能。

---

## 二、研究背景与动机

### 现有研究的痛点

1. **静态启发式的固有缺陷**：现有的免训练剪枝方法（如 FastV、PyramidDrop、SparseVLM 等）依赖静态、瞬时的启发式（如注意力 Top-k）来估计 Token 重要性，并将其作为一次性、不可逆的过滤操作。一旦某个 Token 在浅层被丢弃，其信息便永久丢失。

2. **忽视 MLLM 的层级演化特性**：MLLM 的各层承担不同功能角色——浅层视觉 Token 主要表征低级特征（如纹理），随着深度增加逐渐演化为高级语义实体。论文通过可视化（Figure 2）揭示了一种"层间注意力异质性"（layer-wise attention heterogeneity）：早期层（如 Layer 1、4）注意力分散于路面、车辆和背景结构；中层（Layer 9–15）逐步过滤无关背景并聚焦显著目标；深层（Layer 21–32）注意力集中形成紧凑的高响应区域。这意味着一个在浅层看似冗余的 Token，可能在深层成为推理的关键。

3. **浅层估计导致深层关键线索被过早丢弃**：静态方法用浅层的注意力分数决定 Token 的最终语义价值，往往会误删那些"浅层弱激活、深层强激活"的关键视觉线索。论文在 Figure 1(a) 中直观展示：标准 Top-k 剪枝（红色）严格执行 Token 数量递减，而本文方法（紫色，"+"表示恢复的 Token）能识别并"拯救"那些呈上升趋势的 Token。

### 为什么要做这项研究

论文从人类认知研究中获得启发（Cisek and Kalaska, 2010; Fiebelkorn and Kastner, 2019）：人类的注意力并非固定的快照，而是随理解深化而动态适应的过程。作者由此提出一个根本性问题：**浅层的决策是否足够可靠，以至于能确定一个视觉 Token 的最终语义价值？** 如果不可靠，能否动态恢复信息性 Token 以最小化语义退化？正是基于这一思考，作者将剪枝从局部快照决策提升为时序轨迹建模问题，使剪枝决策具备"可逆性"。

---

## 三、核心方法与创新点

### 方法概述

Trend-aware Pruning 框架由三个核心阶段组成（如 Figure 3 所示）：

**阶段一：Layer-wise Token Collector（逐层 Token 收集器）**

为克服静态剪枝对每层使用相同稀疏率、且认为各层视觉表征相同的假设，引入一个基于短期记忆的滑动观察窗口 $\mathcal{W}_l$。设 $\mathbf{a}_l \in \mathbb{R}^{N^v_l}$ 为当前层 $l$ 的 $N^v_l$ 个视觉 Token 的聚合注意力分数，收集器存储历史注意力状态序列：

$$\mathcal{W}_l = [\mathbf{a}_{l-W+1}, \dots, \mathbf{a}_{l-1}, \mathbf{a}_l]$$

其中 $W$ 为窗口大小，该收集器以先进先出（FIFO）队列方式运作。为保证跨层 Token 对齐，使用当前选定的 Token 索引过滤历史注意力缓存。

在此基础上，计算 **Token Flow（Token 流）** $\mathcal{F}_l$ 作为 Token 动态的定量度量，即窗口内的逐步差分：

$$\boldsymbol{\delta}_k = \mathbf{a}_k - \mathbf{a}_{k-1}, \quad \forall k \in \{l-W+2, \dots, l\}$$
$$\mathcal{F}_l = \{\boldsymbol{\delta}_k\}_{k=l-W+2}^{l}$$

离散 Token 趋势 $\boldsymbol{\delta}_k$ 将表征变化方向与单层重要性分数解耦，为后续的 Flow Activation 提供基础。

**阶段二：Adaptive Flow Identification（自适应流识别）**

视觉表征是任务相关语义线索与随机噪声的混合。为确定保留哪些 Token，首先分析其注意力流的单调性：

- **上升趋势（Upward Trends）** $T_i^{\text{up}}$：Token 注意力逐步增加，表明正在为当前生成任务积累语义重要性：
  $$T_i^{\text{up}} = \frac{1}{W-1}\sum_{k=0}^{W-2}\mathbb{I}(\delta_{l-k,i} > 0)$$

- **下降趋势（Downward Trends）** $T_i^{\text{down}}$：Token 注意力持续下降，表明表征偏移或不相关：
  $$T_i^{\text{down}} = \frac{1}{W-1}\sum_{k=0}^{W-2}\mathbb{I}(\delta_{l-k,i} < 0)$$

- **波动趋势（Fluctuating）** $T_i^{\text{fluct}}$：Token 注意力震荡，反映其相关性在各层间变化，通过 Token 流的波动率量化：
  $$T_i^{\text{fluct}} = \sqrt{\frac{1}{W-2}\sum_{k=l-W+2}^{l}(\delta_{k,i} - \bar{\delta}_i)^2}$$

随后采用分布感知的自适应阈值策略：$\tau(T, \lambda) = \mu_T + \lambda \cdot \sigma_T$，其中 $\mu_T$ 和 $\sigma_T$ 为总体统计量，$\lambda$ 控制趋势变化灵敏度并直接调节剪枝激进程度。保留满足 $(T_i - \mu_T)/\sigma_T > \lambda$ 的候选 Token。

**阶段三：Flow Activation and Dynamic Retention（流激活与动态保留）**

Flow Activation 将粗粒度静态剪枝与细粒度趋势感知激活统一。具体地，首先基于逐层注意力执行 Top-k 剪枝作为粗过滤，移除明显冗余的 Token；在此静态选择之上，趋势感知机制显式建模 Token 重要性的跨层演化。最终保留集为各集合的并集：

$$\mathcal{S}^l_{\text{final}} = \mathcal{S}^l_{\text{rank}} \cup \mathcal{S}^l_{\text{up}} \cup \mathcal{S}^l_{\text{down}} \cup \mathcal{S}^l_{\text{fluct}}$$

其中 $\mathcal{S}^l_{\text{rank}}$ 为 Top-k 保留的 Token 索引，$\mathcal{S}^l_{\text{up}}$、$\mathcal{S}^l_{\text{down}}$、$\mathcal{S}^l_{\text{fluct}}$ 为自适应流识别保留的 Token 索引。该设计能够恢复那些语义关键但被过早剪枝的 Token。

**计算复杂度分析**：标准 Transformer 解码层的计算量为 $\mathcal{C}_{\text{base}}^{(l)} = 4Nd^2 + 2N^2d + 2Ndm$。剪枝后每层复杂度变为 $\mathcal{C}_{\text{ours}}^{(l)} = 4\hat{N}_l d^2 + 2\hat{N}_l^2 d + 2\hat{N}_l dm$。趋势感知剪枝引入的额外开销为 $\mathcal{O}(W\hat{N}^v + \hat{N}^v \log \hat{N}^v)$（包括逐元素操作、Top-k 选择和索引重排序），在实践中相对于 $\mathcal{O}(\hat{N}^v d^2)$ 可忽略不计。

### 核心创新

1. **范式转换——从静态快照到时序轨迹建模**：首次将视觉 Token 剪枝从静态单次操作重新定义为动态跨层过程，显式建模视觉 Token 的语义演化以捕捉现有方法忽略的趋势信息。这是本文最根本的贡献。

2. **趋势感知的剪枝与选择性恢复联合机制**：提出 Trend-aware Pruning 方法，同时引导 Token 丢弃与选择性恢复（reactivation），使被剪枝的 Token 在其语义重要性显现时能被动态恢复，从而缓解不可逆视觉线索丢失带来的性能退化。这是将剪枝从"不可逆过滤"转变为"动态可逆选择"的关键。

3. **三类趋势的显式建模与自适应阈值**：将 Token 划分为 Upward、Downward、Fluctuating 三种演化模式，并通过分布感知的自适应阈值（$\mu_T + \lambda \sigma_T$）而非经验固定值来保留关键视觉线索，提供了数据驱动的剪枝激进程度调节。

4. **免训练、即插即用**：整个框架无需任何额外训练，可直接应用于现有 MLLM 架构，具有良好的通用性和实用性。

---

## 四、实验设计与结果

### 实验设置

- **模型**：LLaVA 系列（LLaVA-v1.5-7B/13B、LLaVA-NeXT-7B、LLaVA-OneVision-0.5B）和 Qwen2.5-VL，覆盖 0.5B、7B、13B 不同参数规模和不同架构。
- **基准**：MME、GQA、POPE、SQA、MMBench、VizWiz、OCRBench、InfoVQA、AI2D 等标准多模态基准。
- **环境**：NVIDIA A100 GPU，Python 3.10，PyTorch 2.1.2，transformers 4.37.2。所有方法在相同实验设置和计算环境下执行，严格遵循各基线模型的官方推理设置。
- **超参数**：窗口大小 $W=5$，阈值 $\lambda=0.5$（经超参数敏感性分析确定，$W=5$ 时平均准确率达 99.71%，$\lambda$ 在 $0.2 \sim 1.0$ 范围内性能稳定）。

### 主要结果（LLaVA-v1.5-7B，Table 1）

在 LLaVA-v1.5-7B 上与代表性免训练剪枝方法（FastV、PyramidDrop/PDrop、FasterVLM、SparseVLM、VisionZip）对比：

| 剪枝率 | 方法 | 平均性能保留 | 最终层 Token 数 | FLOPs |
|:---:|------|:---:|:---:|:---:|
| 50% | FastV | 98.01% | 259 | 60.54% |
| 50% | PDrop | 98.09% | 178 | 63.49% |
| 50% | SparseVLM | 98.33% | 172 | 60.09% |
| 50% | **Ours** | **98.89%** | **~146** | **55.10%** |
| 66.7% | PDrop | 97.02% | 49 | 45.12% |
| 66.7% | SparseVLM | 97.49% | 110 | 44.22% |
| 66.7% | **Ours** | **97.80%** | **~73** | **42.63%** |
| 77.8% | SparseVLM | 96.29% | 36 | 37.41% |
| 77.8% | **Ours** | 96.03% | **~23** | **32.20%** |

关键发现：
- 在 50% 剪枝率下，本文方法取得最高的平均性能保留（98.89%）和最低的 FLOPs（55.10%），同时将最终层视觉 Token 压缩至约 146 个，远少于 FastV（259）和 SparseVLM（172）。
- 在 66.7% 剪枝率下，性能保留 97.80%，超过 PDrop（97.02%）和 VisionZip（96.49%），FLOPs 最低（42.63%），Token 压缩至约 73 个。
- 在最激进的 77.8% 设置下，虽然 SparseVLM 的平均准确率略高（96.29% vs. 96.03%），但本文方法将最终层视觉 Token 大幅削减至仅约 23 个（所有方法中最少），同时 FLOPs 最低（32.20%）。这表明建模 Token 重要性的动态趋势过程能实现比静态方法更精确、更稳定的剪枝决策。

### 跨架构泛化（Table 2 & Table 3）

- **LLaVA-v1.5-13B**：在 45% Token 保留率下平均性能达 100.01%（甚至略超全 Token 基线，说明冗余视觉噪声被有效移除）；在 20% 保留率下超过 FastV 2.55 个百分点（99.11% vs. 96.56%）。
- **LLaVA-NeXT-7B**：在 33% 保留率下平均性能 99.58%，超过 FastV 1.4 个百分点。
- **LLaVA-OV-0.5B**：在 20% 保留率下超过 FastV 1.14 个百分点（91.57% vs. 90.43%）。
- **Qwen2.5-VL**：在 MMBench 和 POPE 任务上分别取得 66.24 和 81.89 分，显著超过静态 Top-k 剪枝基线 14.69 和 10.03 个百分点，表明简单的基于幅值的剪枝在先进架构上难以保持语义完整性，而趋势感知策略能有效保持关键视觉线索。

### 消融实验（Table 4）

在细节密集和 OCR 相关任务（OCRBench、InfoVQA）上进行压力测试，因为小而细粒度的目标在浅层注意力弱，极易被过早丢弃：

| 保留策略 | MMB | GQA | VizWiz | OCRBench | InfoVQA |
|----------|:---:|:---:|:---:|:---:|:---:|
| Top-k（仅静态） | 63.23 | 60.13 | 53.44 | 18.70 | 19.57 |
| + Upward | 63.57 | 60.97 | 53.50 | 25.30 | 19.85 |
| + Upward + Fluctuating | 63.57 | 60.97 | 53.55 | 25.70 | 19.91 |
| + Upward + Fluctuating + Downward | 64.18 | 61.53 | 53.80 | 31.00 | 20.09 |

关键发现：
- 仅依赖静态 Top-k 剪枝在 OCRBench 上仅得 18.70 分，语义退化严重。
- 引入 Upward 趋势 Token 后，OCRBench 提升 6.60 分（18.70→25.30），验证了恢复"后起之秀"Token 的有效性。
- 逐步加入 Fluctuating 和 Downward 趋势 Token 后性能持续提升，最终 OCRBench 达 31.00、InfoVQA 达 20.09，证明趋势感知建模成功保留了静态剪枝无法捕捉的细粒度视觉特征。

---

## 五、局限性与未来展望

### 局限性

1. **固定观察窗口**：当前方法依赖轻量级的跨层统计和固定观察窗口（$W=5$），可能无法充分捕捉长程 Token 依赖或更高级的视觉结构。
2. **任务范围**：实验主要在图像理解基准上验证，未涉及视频理解等更长时序的多模态场景。

### 未来展望

1. **更具表达力的趋势建模**：探索更强大的趋势建模方法，如基于学习的趋势预测。
2. **从 Token 级到区域/概念级**：将剪枝从 Token 级别扩展到区域级或概念级表征。
3. **联合优化与轻量适配**：研究趋势感知剪枝与轻量适配（lightweight adaptation）的联合优化。
4. **自适应窗口机制**：Token Collector 可基于输入序列长度构建自适应窗口机制。
5. **视频理解与长时序推理**：将该方法扩展至视频理解和长时程多模态推理。

---

## 六、学术启发

1. **"可逆性"是剪枝的新维度**：本文最重要的启发在于将"可逆性"引入剪枝范式。传统剪枝一旦决策便不可逆转，而本文证明通过建模 Token 重要性的跨层趋势，可以在 Token 被丢弃后根据其语义上升势头将其"拯救"回来。这一思路对其他需要稀疏化的场景（如 KV-Cache 剪枝、注意力稀疏化）同样具有借鉴价值。

2. **时序轨迹建模的迁移潜力**：将 Token 剪枝类比为时序信号处理（动量、趋势、波动率）是一个巧妙的概念映射。这种将"空间静态问题"转化为"时间动态问题"的思路，可启发更多将信号处理/时间序列分析工具引入模型效率优化的研究。

3. **层级异质性的实证价值**：论文通过详细的注意力热图可视化（Figure 2）提供了 MLLM 层间功能差异的实证证据——浅层分散、中层聚焦、深层集中。这一发现不仅支撑了剪枝方法的设计，也为理解 MLLM 内部表征演化提供了有价值的分析视角。

4. **免训练方法的天花板思考**：在最激进设置（77.8%）下，本文方法在平均准确率上略低于 SparseVLM（96.03% vs. 96.29%），但以更少的 Token（23 vs. 36）和更低的 FLOPs（32.20% vs. 37.41%）实现了极具竞争力的效率-性能折衷。这提示免训练方法在极端稀疏下的性能天花板仍需探索，可能需要与轻量训练或自适应机制结合。

5. **对 OCR/细粒度任务的启示**：消融实验中 OCRBench 从 18.70 跃升至 31.00 的结果尤为亮眼，说明细粒度视觉任务对浅层剪枝极为敏感，趋势感知恢复机制在这类场景中价值最大。这为面向文档理解、OCR、细粒度视觉问答的 MLLM 部署提供了实用参考。
