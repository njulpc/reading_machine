# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-07-30 00:00–23:59 UTC  
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, sparsity, KV cache  
**数据来源**: arXiv.org

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2607.28589 | MixFrag: Fragility-Guided Mixed-Precision Post-Training Quantization for Vision Transformers | — | 07-30 | PTQ, Mixed-Precision, ViT, Fragility, MCKP | cs.CV |
| 2 | 2607.28495 | Stage-Replay Divergence Follows the KV Cache: Fixed-Prefix Precision Controls and Bidirectional Cache Transplantation | — | 07-30 | KV Cache, Precision Control, Cache Transplantation, BF16 | cs.LG |
| 3 | 2607.28418 | WIDE: Boosting Adaptive LLM Inference via Token-level Dynamic Width Pruning | — | 07-30 | Dynamic Pruning, Token-level, Width Pruning, LLM | cs.AI |
| 4 | 2607.28069 | SemPIC: Learning Semantic Position-Independent KV Caches | — | 07-30 | KV Cache, Position-Independent, LoRA, Semantic Caching | cs.AI |
| 5 | 2607.28341 | Capturing Token Tendencies for Training-Free Token Pruning in Multimodal Large Language Models | — | 07-30 | Token Pruning, MLLM, Training-Free, Attention Flow | cs.CV |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 1篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| MixFrag (2607.28589) | Mixed-Precision PTQ | Vision Transformers | KL散度脆弱性估计 + MCKP比特分配，COCO上提升9.6 AP |

### 2.2 剪枝 (Pruning) — 2篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| WIDE (2607.28418) | Dynamic Width Pruning | LLMs | Token级动态宽度剪枝，端到端加速1.68x |
| Trend-aware Pruning (2607.28341) | Training-Free Token Pruning | MLLMs | 注意力流动量捕捉，77.8%视觉Token压缩 |

### 2.3 KV Cache 优化 — 2篇

| 论文 | 优化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Stage-Replay Divergence (2607.28495) | Precision-Controlled KV Cache | Qwen2.5-derived | 固定前缀精度控制，双向缓存移植，证明KV Cache是发散轨迹的因果充分载体 |
| SemPIC (2607.28069) | Semantic Position-Independent Cache | LLMs | LoRA行为蒸馏编译语义位置无关KV，micro-F1从0.53提升至0.60 |

---

## 三、按应用领域分类

| 应用领域 | 论文数量 | 代表性论文 |
|---------|:-------:|-----------|
| **计算机视觉 (CV)** | 2 | MixFrag (ViT量化), Trend-aware Pruning (MLLM Token剪枝) |
| **大语言模型 (LLM)** | 3 | WIDE (动态宽度剪枝), SemPIC (KV Cache), Stage-Replay (KV Cache) |
| **多模态 (MLLM)** | 1 | Trend-aware Pruning (视觉Token剪枝) |

---

## 四、量化论文评分表

| 论文 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合 |
|------|:-------:|:-------:|:------:|:-------:|:----:|
| MixFrag (2607.28589) | 8 | 7 | 9 | 8 | **8.0** |

### 评分说明

**MixFrag (2607.28589)** — 综合评分 8.0/10

- **精度效果 (8/10)**: 在ImageNet-1K上保持竞争力分类性能，在COCO检测/分割任务上较先前最佳方法提升最高9.6 AP，MP3/MP3严苛设定下表现突出。
- **压缩倍率 (7/10)**: 混合精度策略（3-bit/4-bit/8-bit组合）提供灵活压缩，但未报告具体模型大小压缩比，依赖目标比特预算。
- **创新性 (9/10)**: 核心创新在于将"孤立量化+KL散度"用于组件级脆弱性估计，并将比特分配建模为MCKP，方法框架优雅且可扩展。
- **可复现性 (8/10)**: 基于标准PTQ流程，仅需小校准集；MCKP有成熟求解器；已提供完整PyTorch复现代码（基于Qwen3-0.6B适配）。

---

## 五、值得关注的高亮点

1. **混合精度PTQ新突破**: [2607.28589] MixFrag 提出基于KL散度的组件级脆弱性估计，将比特分配建模为MCKP，在COCO上较先前最佳提升 **9.6 AP**，为ViT部署提供了精细化的精度-效率权衡方案。

2. **Token级动态宽度剪枝**: [2607.28418] WIDE 首次实现端到端可微分的Token级动态宽度剪枝，支持prefill和decode双场景，在50%稀疏度下实现 **1.98x prefill** 和 **4.95x decode** 内核级加速。

3. **KV Cache因果充分性证明**: [2607.28495] 通过固定前缀2×2实验设计，首次在Qwen2.5系统上证明边界K/V缓存是发散轨迹的因果充分载体，双向移植实验 **43/43** 完全跟随donor，为KV Cache优化提供了理论基础。

4. **语义位置无关KV缓存**: [2607.28069] SemPIC 通过LoRA行为蒸馏编译语义位置无关的逐层文档KV，在3个模型4个任务上micro-F1从 **0.53提升至0.60**，逼近全重计算的0.62。

5. **Training-Free时序Token剪枝**: [2607.28341] 提出Trend-aware Pruning，将剪枝从局部快照决策提升为时序轨迹建模，捕捉注意力流动量并重新激活"late-blooming" token，实现 **77.8%** 视觉Token压缩。

---

## 六、整体分析

### 6.1 技术趋势观察

**动态与自适应成为主线**: 今日5篇核心论文中，4篇涉及"动态"或"自适应"策略（WIDE的动态宽度、MixFrag的自适应混合精度、Trend-aware的动态token重要性、SemPIC的自适应语义缓存）。这表明模型压缩领域正从静态、统一的压缩策略向输入感知、组件感知的精细化方向演进。

**KV Cache成为热点**: 2篇论文聚焦KV Cache优化，分别从精度控制（Stage-Replay）和语义重用（SemPIC）两个角度切入。随着长上下文LLM的普及，KV Cache的存储和计算效率已成为与权重量化同等重要的优化目标。

**细粒度剪枝回归**: WIDE将剪枝粒度从层级下探到token级和神经元块级，配合可微分训练和内核协同设计，代表了结构化剪枝向超细粒度发展的新方向。

### 6.2 方法论启示

- **孤立扰动+分布距离**可作为通用的组件敏感性度量范式，不仅限于量化。
- **组合优化视角**（MCKP、动态规划）为资源分配问题提供了数学上可解释的最优解。
- **因果推断实验设计**（Stage-Replay的2×2控制）为诊断模型行为差异提供了严谨框架。

---

*报告生成时间: 2026-07-31*  
*分析人: AI Assistant (Auto-generated)*
