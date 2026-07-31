# 深度技术分析：HiFloat4 Format for End-To-End Reinforcement Learning Post-Training of Large Language Models

## 1. 核心速览

**研究话题**：端到端 FP4 精度强化学习（RL）后训练，同时涵盖前向与反向传播

**一句话总结**：本文首次实现了全流程 FP4 精度的 RL 后训练，发现 rollout 阶段激活量化中的异常值导致的 underflow 是主要误差源，提出 Rollout-ResQ 残差修正与 HiFloat4 三级层次化缩放格式，在 Qwen2.5-3B/7B 上将 BF16 精度差距从 4.9% 缩小至 1.1%。

---

## 2. 研究背景与动机

### 2.1 RL 后训练的计算瓶颈

大型语言模型（LLM）通过强化学习（RL）进行后训练已在数学推理、代码生成等任务上取得显著成功，代表性方法包括 GRPO、PPO 等。然而 RL 后训练的计算开销极为庞大：

- **推理（rollout）阶段**：每个训练步需要生成大量推理轨迹（reasoning trajectories），涉及长序列的前向传播
- **训练阶段**：策略梯度更新需要计算梯度，涉及反向传播
- **显存占用**：同时维护 rollout policy 和 training policy 两份参数，加上大量中间激活值

以 Qwen2.5-Math-7B 为例，全精度 BF16 RL 训练需要数十 GB 显存，严重限制了可扩展性。

### 2.2 低精度 RL 训练的空白

现有的低精度研究主要集中在：
- **推理阶段量化**：如 GPTQ、AWQ 等权重量化方法，仅优化前向传播
- **训练阶段量化**：如 FP8、BF16 混合精度训练
- **PTQ 后量化**：对预训练模型进行量化，不涉及 RL 训练过程

**FP4 在 RL 全链路中的应用是完全空白**。FP4 仅 4-bit，相比 FP8/BF16 可进一步降低 2-4 倍显存占用和计算开销，但挑战也更为严峻：
- 激活中的异常值（outliers）在 FP4 的紧窄动态范围下大量 underflow 到零
- rollout 和 training policy 之间的精度不匹配会导致训练不稳定
- 反向传播中的梯度量化误差会累积放大

### 2.3 核心发现：rollout–training mismatch 是主因

作者通过系统性实验发现了一个反直觉的现象：
- **将 training policy 恢复为高精度**（保留 FP4 rollout），精度反而**比全 FP4 更差**
- 这说明 rollout 和 training 之间的精度不匹配（mismatch）是主要失效模式
- 单纯提高 training 精度无法解决问题，必须从 rollout 端的激活量化入手

---

## 3. 核心方法与创新点

### 3.1 方法概述

本文提出两个互补组件：

**组件一：Rollout Residual Quantization (Rollout-ResQ)**
- 在 FP4 rollout 的矩阵乘法中加入一个稀疏残差修正项
- 该残差项受限于硬件友好的稀疏模式（如 block-sparse）
- 仅修正 outlier 导致的 underflow，不增加 rollout 的计算 footprint

**组件二：HiFloat4 (HiF4) 格式**
- 三级层次化缩放（three-level hierarchical scaling）
- 相比标准 MXFP4 的单层 block 缩放，HiF4 在保持硬件效率的同时保留了更多分辨率

### 3.2 分点创新

**创新点一：首次端到端 FP4 RL 后训练**

此前所有低精度 RL 工作均停留在 FP8 或更高精度。本文首次将 rollout policy 和 training policy 的前向/反向传播全部置于 FP4 精度下运行，验证了可行性并量化了精度损失。

**创新点二：Rollout-ResQ 残差修正机制**

关键洞察：FP4 RL 中的主要误差不是 training 端的量化误差，而是 rollout 端激活中的异常值使动态范围过度拉伸，导致大量值 underflow 到零。

Rollout-ResQ 的设计：
- 在 FP4 matmul 后添加一个残差项：$Y_{corrected} = Y_{FP4} + \Delta Y_{sparse}$
- $\Delta Y_{sparse}$ 采用硬件友好的稀疏模式（如 2:4 稀疏或 block-sparse）
- 稀疏性保证了额外计算开销极低
- 残差项捕捉了被 FP4 underflow 丢失的 outlier 信息

**创新点三：HiFloat4 三级层次化缩放格式**

标准 MXFP4 使用单层 block 缩放（32 元素共享一个 E8M0 指数），在异常值存在时分辨率不足。HiF4 引入三级层次化缩放：

1. **张量级（Tensor-level）缩放**：全局缩放因子
2. **块级（Block-level）缩放**：如 MXFP4 的 32 元素块
3. **子块级（Sub-block-level）缩放**：更细粒度的局部缩放

这种层次化结构在硬件上可通过额外的元数据高效实现，同时显著提升了异常值区域的分辨率。

**创新点四：对 FP4 格式选择的系统性分析**

作者对比了 HiF4 与开放标准 MXFP4：
- 在 HiF4 + Rollout-ResQ 下，BF16 差距从 4.9% 降至 1.1%
- 在 MXFP4 + Rollout-ResQ 下，BF16 差距从 13.6% 降至 5.3%
- **结论：FP4 格式本身是决定可恢复精度上限的关键因素**

---

## 4. 实验设计与结果

### 4.1 实验设置

**模型**：
- Qwen2.5-3B
- Qwen2.5-Math-7B

**任务**：
- 数学推理（使用 RLVR / GRPO 风格训练）
- 代码生成

**基线**：
- BF16 全精度
- FP4 基线（无 Rollout-ResQ）
- FP4 + 高精度 training policy（反直觉的消融）
- HiF4 + Rollout-ResQ（完整方法）
- MXFP4 + Rollout-ResQ（格式对比）

### 4.2 核心实验结果

**结果一：端到端精度恢复**

| 配置 | Qwen2.5-3B 差距 | Qwen2.5-Math-7B 差距 |
|------|----------------|---------------------|
| BF16 | 0% (baseline) | 0% (baseline) |
| FP4 基线 | 4.9% | ~5% |
| FP4 + HiF4 | 显著改善 | 显著改善 |
| FP4 + Rollout-ResQ | 改善 | 改善 |
| **HiF4 + Rollout-ResQ** | **1.1%** | **~1.1%** |
| MXFP4 + Rollout-ResQ | 5.3% | ~5.3% |

**结果二：Rollout–training mismatch 验证**

| 配置 | 精度差距 |
|------|---------|
| 全 FP4 | 4.9% |
| FP4 rollout + BF16 training | **比全 FP4 更差** |

这一反直觉结果证明了 mismatch 是主要失效模式。

**结果三：FP4 格式对比**

| 格式 | BF16 差距 |
|------|----------|
| MXFP4 基线 | 13.6% |
| MXFP4 + Rollout-ResQ | 5.3% |
| HiF4 基线 | 显著优于 MXFP4 |
| **HiF4 + Rollout-ResQ** | **1.1%** |

### 4.3 结果讨论

**为什么 Rollout-ResQ 有效？**

Rollout 阶段的激活异常值使 FP4 的动态范围被过度拉伸。Rollout-ResQ 通过稀疏残差项专门补偿这些 outlier 损失的信息，而不改变 FP4 的核心计算路径。

**为什么 HiF4 优于 MXFP4？**

MXFP4 的单层 block 缩放（32 元素共享指数）在异常值存在时被迫使用大缩放因子，导致正常值的分辨率急剧下降。HiF4 的三级层次化缩放允许在异常值区域使用局部细粒度缩放，在正常区域保持粗粒度效率。

---

## 5. 局限性与未来展望

### 5.1 局限性

**局限一：仅在 Qwen 系列验证**

实验仅在 Qwen2.5-3B 和 Qwen2.5-Math-7B 上验证。在 Llama、GPT 等其他架构上的有效性有待验证。

**局限二：HiF4 硬件支持有限**

HiF4 的三级层次化缩放需要自定义硬件支持。当前仅有华为自研芯片支持，NVIDIA/AMD 等主流硬件尚未支持该格式。

**局限三：任务范围有限**

主要在数学推理和代码生成任务上验证。在开放式对话、多模态等更广泛任务上的效果未知。

**局限四：稀疏残差模式未充分探索**

Rollout-ResQ 中的稀疏模式（如 2:4、block-sparse）的选择对效果有重要影响，但本文未做系统性比较。

### 5.2 未来展望

**方向一：扩展到更多模型架构**

在 Llama、Mistral、GPT 等主流架构上验证 HiF4 + Rollout-ResQ 的通用性。

**方向二：与现有量化方法结合**

将 Rollout-ResQ 与 GPTQ、AWQ 等权重量化方法结合，实现权重+激活的全 FP4 推理和训练。

**方向三：自适应稀疏率**

根据 layer/head 的重要性动态调整 Rollout-ResQ 的稀疏率，在精度和效率之间取得更优平衡。

**方向四：FP4 预训练**

本文聚焦于 RL 后训练，未来可探索从预训练阶段就使用 FP4 的可行性。

---

## 6. 学术启发

### 6.1 可迁移思路

**思路一：rollout-training 精度对称性**

本文的核心洞察——rollout 和 training 的精度必须对称匹配——可以推广到其他训练场景：
- **蒸馏训练**：teacher 和 student 的精度配置需要协调
- **GAN 训练**：generator 和 discriminator 的精度配置
- **多模态训练**：不同模态编码器的精度配置

**思路二：稀疏残差补偿量化误差**

Rollout-ResQ 的思想可以推广到：
- 静态量化中的稀疏补偿
- 动态量化中的 outlier 处理
- 混合精度中的精度边界平滑

**思路三：层次化缩放格式设计**

HiF4 的三级层次化缩放为低精度格式设计提供了新范式：
- 不同粒度缩放应对不同分布特征
- 元数据开销与精度增益的权衡

### 6.2 实验设计借鉴

**借鉴一：反直觉消融实验**

"提高 training 精度反而使结果更差"这一消融实验设计极具洞察力。它通过违反直觉的结果揭示了真正的问题所在，而非简单地验证假设。

**借鉴二：格式对比的系统方法**

本文不仅提出新方法，还与开放标准（MXFP4）做了公平对比，证明了格式设计的重要性。

---

## 7. 总结

HiFloat4 + Rollout-ResQ 首次实现了端到端 FP4 精度的 RL 后训练，将 BF16 精度差距从 4.9% 缩小至 1.1%。其核心贡献在于：

1. **识别了 rollout 激活量化中的 outlier-driven underflow 是主要误差源**
2. **提出 Rollout-ResQ 稀疏残差修正机制**
3. **设计 HiFloat4 三级层次化缩放格式**
4. **揭示了 FP4 格式选择是决定精度上限的关键因素**

这项工作为 LLM RL 后训练的低成本化提供了重要路径，但受限于 HiF4 的硬件支持范围，短期内更可能在自研芯片场景落地。

---

*论文信息：arXiv:2607.26515，Hei Yi Mak 等，Huawei*
