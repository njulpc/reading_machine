# 深度技术分析：FOCUS: FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling

## 1. 核心速览

**研究话题**：面向大语言模型（LLM）的 FP4 后训练量化（PTQ）中的 scale 因子端到端梯度优化方法。

**一句话总结**：本文提出 FOCUS 框架，核心洞察是量化 scale（quantization scale）无需遵守硬件约束（如 E8M0 离散格式），仅 dequantization scale 需要存储部署。基于此提出 Coupled-Relaxation Scaling（CRS）和 Dual-Granularity Scaling（DGS）两个模块，将量化 scale 优化从离散空间解放到连续全精度空间并在子块粒度上细化，在 Qwen3-4B 上 NVFP4 格式下恢复 98.2% 的 FP16 zero-shot 精度，量化仅需单卡 H20 GPU 19 分钟，且无额外推理开销。

---

## 2. 研究背景与动机 (Background & Motivation)

### 2.1 LLM 部署成本与 FP4 量化的兴起

大语言模型（如 Qwen3、Llama 等系列）参数规模已达数百亿乃至万亿级别，部署面临严峻的内存与计算开销。后训练量化（PTQ）作为轻量级压缩方案，已从 8-bit 推进到 4-bit 甚至更低精度。近期，微缩放浮点格式（microscaling floating-point formats）如 MXFP4（Rouhani et al., 2023）和 NVFP4（Nvidia et al., 2025）凭借在现代加速器（如 NVIDIA Blackwell）上的原生硬件支持，成为 W4A4 推理的有力候选路径。

### 2.2 FP4 格式的技术特点

MXFP4 和 NVFP4 均采用 E2M1 浮点元素表示权重，配合块级共享 scale 因子：

- **MXFP4**：块大小 B=32，每块共享一个 E8M0 格式的 scale（仅编码 2 的幂次指数），scale 粒度较粗。
- **NVFP4**：块大小 B=16，采用两级缩放机制——张量级 FP32 全局 scale α 和每块 FP8（E4M3）scale Δ_i，有效 scale 为 S_i = α · Δ_i。

### 2.3 现有方法的不足

尽管有硬件支持，FP4 精度下维持模型准确率仍然困难。已有工作沿几个方向探索：

1. **残差补偿**（ARCQuant, Meng et al., 2026）：通过残差通道补偿量化误差。
2. **格式感知舍入**（FAAR, Li et al., 2026a）：针对 NVFP4 的自适应舍入。
3. **冗余零重映射**（RaZeR, Chen et al., 2026）：利用冗余零扩展可表示值。
4. **变换方法**（MR-GPTQ, QuaRot, SpinQuant, FlatQuant, BATQuant 等）：通过 Hadamard 旋转或仿射变换重塑权重/激活分布，但引入在线计算开销。
5. **Scale 优化**（Four Over Six, Cook et al., 2025; overflow-aware scaling, Chhugani et al., 2026）：基于启发式规则调整 scale，改进有限。

### 2.4 本文要解决的核心问题

上述 scale 优化方法存在一个关键缺陷：它们**紧耦合（tightly couple）量化 scale 和反量化 scale**，强制两者都遵守硬件要求的离散低精度格式。然而，作者敏锐地注意到一个被忽视的事实：**只有反量化 scale 在推理时被存储和部署，必须遵守硬件约束；量化 scale 仅在离线量化过程中使用，从不存储，因此完全不必遵守精度格式或块大小粒度的限制**。这意味着存在一个巨大的、未被利用的优化空间。

现有方法还存在另一个问题：大多基于逐层规则（如 MSE 搜索、absmax 修正），缺乏端到端任务级监督，无法利用全局损失信息进行优化。此前没有工作直接通过梯度学习来优化 FP4 的 scale 因子。

---

## 3. 核心方法与创新点 (Methodology & Innovations)

### 3.1 整体框架：FOCUS

FOCUS 是一个端到端的 PTQ scale 学习框架，核心思想是沿两个维度释放量化 scale 的自由度：

- **精度维度**：量化 scale 不必遵守硬件离散格式 → CRS
- **粒度维度**：量化 scale 不必遵循预定义块大小 → DGS

最终输出模型仅存储 FP4 权重和反量化 scale，量化 scale 被丢弃，因此**推理时零额外开销**。

### 3.2 基线框架：端到端 Scale 学习

FOCUS 的基线是一个端到端的 scale 学习框架：冻结原始 FP16 权重，通过 Straight-Through Estimator（STE）学习 FP8 格式的 scale 参数，在量化-反量化过程中最小化任务损失。这一基线将 scale 优化从规则驱动提升为梯度驱动，但仍受限于 FP8 的离散格式。

### 3.3 Coupled-Relaxation Scaling (CRS)

**核心思想**：在量化 scale 和反量化 scale 之间引入一个可学习的全精度系数，解除两者的紧耦合。

在标准 FP4 量化中，量化 scale 和反量化 scale 共享同一个值 S_i，该值必须量化到 E8M0（MXFP4）或 E4M3（NVFP4）格式。CRS 引入一个可学习的全精度系数 r_i，使得：

- 量化 scale：S_q = r_i · S_dq（其中 S_dq 是遵守硬件格式的反量化 scale）
- r_i 在优化过程中保持全精度，可被梯度自由更新

这一设计将量化 scale 的优化从离散低精度空间**提升到连续全精度空间**，使梯度下降能够有效探索更优的 scale 配置，同时不破坏推理时的硬件合规性——因为最终存储和部署的只有 S_dq。

CRS 的关键优势在于：它不改变推理路径，量化 scale 的优化自由度完全在离线阶段被利用，部署时量化 scale 被丢弃。

### 3.4 Dual-Granularity Scaling (DGS)

**核心思想**：将量化 scale 分配到比反量化 scale 更细的子块粒度。

在标准方案中，量化 scale 和反量化 scale 共享同一个块大小（MXFP4 为 32，NVFP4 为 16）。DGS 将每个块进一步划分为子块，为每个子块分配独立的量化 scale 系数。这使得量化 scale 能够捕捉单个块级 scale 无法表示的**局部权重分布变化**。

例如，在一个大小为 32 的 MXFP4 块中，DGS 可以将其划分为多个子块，每个子块拥有独立的量化 scale，而反量化 scale 仍按原始块粒度存储。由于量化 scale 不被存储，更细的粒度不会增加推理开销。

### 3.5 FOCUS without Extra Transforms

与变换方法（如 Hadamard 旋转）不同，FOCUS 不引入任何在线变换操作，保证与现有推理框架的无缝兼容。变换方法虽能提升精度，但需要额外的在线计算（如 Hadamard 旋转）并对推理框架进行适配。FOCUS 仅优化 scale 参数，输出的量化模型在结构上与标准 FP4 模型完全一致。

---

## 4. 实验设计与结果 (Experiments & Results)

### 4.1 实验设置

- **模型族**：多个 LLM 家族，包括 Qwen3 系列（如 Qwen3-4B 等）
- **量化格式**：MXFP4 和 NVFP4
- **基线方法**：包括 Four Over Six、overflow-aware scaling、MR-GPTQ、BATQuant、FAAR、ARCQuant、RaZeR 等
- **评估基准**：多个 zero-shot 基准测试
- **硬件**：单卡 H20 GPU

### 4.2 主要结果

| 模型 | 格式 | 指标 | 结果 |
|------|------|------|------|
| Qwen3-4B | NVFP4 | FP16 zero-shot 恢复率 | **98.2%** |
| Qwen3-4B | MXFP4 | 恢复率 | 持续优于所有基线 |
| 多模型族 | NVFP4/MXFP4 | SOTA FP4 精度 | **FOCUS 全面领先** |

在 Qwen3-4B 上，FOCUS 在 NVFP4 和 MXFP4 两种格式下均一致性地超越所有现有基线方法。

### 4.3 量化成本

- 量化 Qwen3-4B 仅需 **单卡 H20 GPU 19 分钟**
- 无额外推理开销（推理时与标准 FP4 模型完全一致）
- 无需对推理框架进行额外适配

### 4.4 消融研究

论文设计了消融实验验证 CRS 和 DGS 两个模块各自的贡献：

- **CRS** 的贡献：将 scale 优化从离散空间提升到连续空间，显著改善了梯度优化的有效性
- **DGS** 的贡献：更细粒度的量化 scale 能更好地适应局部权重分布，进一步提升精度
- 两个模块互补：CRS 沿精度维度释放自由度，DGS 沿粒度维度释放自由度，组合使用效果最佳

---

## 5. 局限性与未来展望 (Limitations & Future Work)

### 5.1 局限性

1. **仅针对 scale 优化**：FOCUS 聚焦于 scale 因子的优化，未涉及权重舍入策略（如 AdaRound 风格的自适应舍入）或变换方法（如 Hadamard 旋转）的联合优化。在实际应用中，将 scale 优化与舍入优化结合可能进一步提升精度。

2. **FP4 格式限制**：方法针对 MXFP4 和 NVFP4 两种特定格式设计，对于其他低精度浮点格式（如 FP6、FP8）的适用性需要进一步验证。

3. **实验规模**：虽然覆盖了多个 LLM 家族，但论文展示的核心数字（如 98.2% 恢复率）主要在 Qwen3-4B 上报告。对于更大规模模型（如 70B+）的表现需要更多验证。

4. **Scale 学习基线的依赖**：FOCUS 建立在端到端 scale 学习基线之上，该基线使用 STE 进行梯度近似，在极端低精度下可能存在梯度估计不准的问题。

### 5.2 未来展望

1. **与变换方法联合**：探索 FOCUS 与 Hadamard 旋转等变换方法的联合优化，可能在精度上取得进一步突破，尽管需要权衡推理开销。

2. **扩展到更低精度**：将 CRS 和 DGS 的思想推广到 FP2 或 INT2 等极低精度场景，进一步压缩模型。

3. **联合舍入优化**：将 scale 学习与自适应舍入（AdaRound）结合，形成更完整的 PTQ 优化框架。

4. **激活量化优化**：目前主要聚焦于权重 scale，未来可探索对激活量化的 scale 进行类似的解耦优化。

---

## 6. 学术启发 (Takeaways for My Research)

### 6.1 "不被存储的参数不受硬件约束"这一洞察的普适性

FOCUS 的核心洞察——量化 scale 不被存储因此无需遵守硬件格式——是一个极具启发性的思路。这一"区分在线/离线约束"的原则可以推广到许多量化场景：任何仅在离线优化中使用、不在推理时存储的参数，都可以被释放到全精度空间进行优化。在我的研究中，可以审视量化流程中哪些中间变量被不必要地约束到了低精度。

### 6.2 端到端梯度优化 vs 规则启发式

FOCUS 将 scale 优化从规则驱动（absmax、MSE 搜索）提升为端到端梯度驱动，这是一个重要的方法论转变。在 PTQ 研究中，许多参数（scale、clipping threshold、rounding decision）仍采用启发式确定。将这些参数纳入端到端可微分优化框架，利用任务级损失信号进行指导，是一个有前景的研究方向。

### 6.3 精度-粒度双维度解耦

CRS 和 DGS 分别沿精度维度和粒度维度释放优化自由度，这种"多维度解耦"的思路值得借鉴。在量化研究中，可以系统性地审视哪些维度被不必要地耦合（如量化与反量化 scale 的耦合、块大小的一致性等），并探索解耦带来的优化空间。

### 6.4 零推理开销设计原则

FOCUS 的一个重要设计原则是：离线优化的复杂度不影响推理效率。在我的量化研究中，应始终关注优化方法是否引入额外的推理开销，确保方法的实际可部署性。

### 6.5 实验设计的参考

FOCUS 的实验设计值得学习：使用"FP16 恢复率"作为统一指标，便于跨模型、跨格式比较；报告量化时间成本（单卡 19 分钟）使方法的实用性可评估；消融实验清晰隔离了两个模块的贡献。这些做法值得在我的实验中采纳。
