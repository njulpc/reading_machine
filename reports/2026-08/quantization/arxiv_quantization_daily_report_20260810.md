# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-08-10 (arXiv公告日) / 2026-08-07 (API发布日期)
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, INT4, INT8, FP4, sparsity, KV cache
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV new listings)

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2608.07019 | ReQuant: Fixed-Grid Discrete Refinement for Post-Training Quantization | Yongge Ma 等 | 08-07 | PTQ, discrete refinement, fixed grid | Quantization |
| 2 | 2608.06916 | MiCoPro: End-to-End Mixed Precision HW/SW Co-design with HW-aware Proxy Model | Zijun Jiang 等 | 08-07 | Mixed precision, HW/SW co-design, latency proxy | Quantization |
| 3 | 2608.06763 | CubicQuant: Parametric Non-Uniform Codebooks for High-Throughput LLM Inference | Xuetian Gao 等 | 08-07 | Non-uniform quantization, cubic curve, 1-8 bit | Quantization |
| 4 | 2608.06901 | Prune Once: Retraining-Free Task-Agnostic Pruning for Vision-Language Models | Minseok Kang 等 | 08-07 | VLM pruning, task-agnostic, activation variation | Pruning |
| 5 | 2608.06849 | Autonomy-of-Heads: Data-Free Sparse Attention from Frozen Query-Key Geometry | Yehan Yang 等 | 08-07 | Sparse attention, spectral geometry, data-free | Pruning |
| 6 | 2608.07088 | RoRA: Role-Oriented Regional Allocation for Visual Token Pruning in MLLMs | Qiyanhui Lu 等 | 08-07 | Visual token pruning, role-oriented, MLLM | Pruning |
| 7 | 2608.07193 | AutoPrune: AI4AI Framework for Visual Token Pruning | Jingwen Fu 等 | 08-07 | LLM-driven, DSL, visual token pruning | Pruning |
| 8 | 2608.07001 | GraceKV: Global Allocation of Resolution and Coverage for KV Cache Compression | Haolin Tian 等 | 08-07 | KV cache, global allocation, prototype tree | KV Cache |
| 9 | 2608.07458 | CoinRAG: Contextualized Information Nugget KV Cache Reuse for Long-Context RAG | Gyuwan Kim 等 | 08-07 | KV cache reuse, nugget, RAG | KV Cache |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 3篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| ReQuant (2608.07019) | INT4/INT8 PTQ后处理 | 通用LLM | 固定网格离散精修，无需反向传播，即插即用 |
| MiCoPro (2608.06916) | 混合精度HW/SW协同 | 边缘AI | 硬件感知代理模型，端到端部署，40%延迟降低 |
| CubicQuant (2608.06763) | 参数化非均匀标量 | LLM推理 | 单调三次曲线映射，1-8位自适应，28% RMSE降低 |

### 2.2 剪枝 (Pruning) — 4篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| PORTA (2608.06901) | 权重剪枝 | VLM (CLIP/BLIP/Qwen2-VL) | 任务无关，基于激活变化，自适应稀疏度 |
| AoH (2608.06849) | 注意力头稀疏 | 长上下文LLM | 数据无关，谱几何分析，50%稀疏保留96.5%性能 |
| RoRA (2608.07088) | 视觉token剪枝 | MLLM | 角色导向区域分配，88.9%剪枝保留96.5% |
| AutoPrune (2608.07193) | 视觉token剪枝 | MLLM | LLM驱动策略搜索，TPDSL，94.4%移除保留99% |

### 2.3 KV Cache压缩 — 2篇

| 论文 | 技术类型 | 目标 | 核心贡献 |
|------|---------|------|---------|
| GraceKV (2608.07001) | 全局资源分配 | 长上下文LLM | 原型树结构，分辨率与覆盖平衡，128倍压缩 |
| CoinRAG (2608.07458) | 细粒度缓存重用 | RAG系统 | Nugget级别复用，两阶段检索，5.3% F1提升 |

---

## 三、量化论文详细评分

| 论文 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 总分 |
|------|:-------:|:-------:|:-----:|:-------:|:----:|
| ReQuant (2608.07019) | 7 | 6 | 8 | 9 | **30** |
| MiCoPro (2608.06916) | 7 | 7 | 8 | 6 | **28** |
| CubicQuant (2608.06763) | 8 | 7 | 9 | 7 | **31** |

**评分说明**（每项1-10分）：
- **精度效果**：量化后模型保留的原始精度比例
- **压缩倍率**：达到的压缩程度（比特宽度降低、参数量减少）
- **创新性**：方法的新颖程度和理论贡献
- **可复现性**：代码开源程度、实验细节清晰度、第三方复现难度

---

## 四、整体分析

### 4.1 趋势观察

**趋势一：后处理优化成为PTQ新方向**
ReQuant代表了PTQ领域的新范式——将量化视为"初始化+精修"两阶段过程。这与传统的一次性量化形成对比，为现有PTQ方法提供了通用的提升路径。

**趋势二：非均匀量化格式的复兴**
CubicQuant在均匀量化和学习码本之间开辟了新的设计空间，通过参数化曲线实现灵活性与效率的平衡。这与近期FP4/FP8等浮点格式的探索形成了互补。

**趋势三：数据无关方法的崛起**
AoH和PORTA都强调无需校准数据或重训练，这反映了实际部署场景对"即插即用"解决方案的强烈需求。

**趋势四：视觉Token剪枝成为MLLM优化热点**
RoRA和AutoPrune均聚焦于MLLM的视觉token剪枝，表明随着多模态模型的普及，视觉端的效率优化日益重要。

### 4.2 亮点论文

1. **CubicQuant**：参数化非均匀量化的优雅设计，理论分析与执行方案的统一，为LLM权重量化提供了新选择。

2. **GraceKV**：将KV Cache压缩提升为全局资源分配问题，原型树结构提供了灵活的层次化压缩能力。

3. **AutoPrune**：AI4AI范式的有趣尝试，利用LLM自动设计剪枝策略，展示了算法自动化的潜力。

### 4.3 局限与开放问题

- **ReQuant**：计算开销较大，对超大模型的可扩展性存疑
- **MiCoPro**：硬件覆盖范围有限，缺乏主流GPU平台的验证
- **CubicQuant**：缺乏真实LLM的端到端精度评估
- **视觉Token剪枝**：方法主要针对视觉端，未考虑文本token的联合优化

---

## 五、复现代码

| 论文 | 代码位置 | 状态 |
|------|---------|------|
| ReQuant (2608.07019) | `scripts/quantization/2608.07019/` | 可运行 (synthetic + 模型支持) |
| MiCoPro (2608.06916) | `scripts/quantization/2608.06916/` | 可运行 (synthetic + 模型支持) |
| CubicQuant (2608.06763) | `scripts/quantization/2608.06763/` | 可运行 (synthetic + 模型支持) |

**运行方式**：
```bash
cd scripts/quantization/<arxiv_id>/
python3 demo.py          # synthetic demo (default)
python3 demo.py --real   # with real Qwen3-0.6B model
```

---

*报告生成时间: 2026-08-11*
*分析人: AI Assistant (Auto-generated)*
