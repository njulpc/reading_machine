# ArXiv 量化与模型压缩领域论文日报

**目标日期**: 2026-08-04（周一）
**收集日期范围**: 2026-08-01 ~ 2026-08-03（arXiv API 索引延迟，截至运行时 2026-08-05 最新可用论文截止于 2026-08-03T17:57Z，08-04 提交的论文尚未进入 API 索引）
**检索关键词**: quantization, quantize, low-bit, model compression, compress, pruning, sparsity, knowledge distillation, KV cache compression, mixed precision, GPTQ, AWQ
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV, cs.AI, cs.AR, cs.IR)
**检索方式**: arXiv API (`http://export.arxiv.org/api/query`)，submittedDate 范围 + 关键词过滤

---

## 日期说明

2026-08-04 为周一，arXiv API 的 export 接口存在 1-3 天索引延迟，截至运行时（2026-08-05）最新可用论文截止于 2026-08-03T17:57:01Z，08-04 提交的论文尚未进入 API 索引。8 月 3 日为周日（arXiv 不发布新论文），实际有效提交日为 8 月 1 日（周五）和 8 月 2 日（周六，少量提交）。

本次日报收录 2026-08-01 至 2026-08-03 期间提交的 12 篇模型压缩相关论文，覆盖量化（5 篇）、剪枝与稀疏化（4 篇）、知识蒸馏（1 篇）、KV 缓存/VLM 压缩等其他方向（2 篇）。

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 | 分类 |
|:---:|----------|---------|------|:-------:|-----------|------|------|
| 1 | 2608.01847 | FOCUS: FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling | Xianglong Yan 等 | 08-03 | FP4, MXFP4, NVFP4, Scale Learning, PTQ | cs.AI | 量化 |
| 2 | 2608.01078 | Attend to Your Own Thoughts: Breaking the Barrier for PTQ of Reasoning LLMs through 1.58-Bit Quantization | Shigeng Wang 等 | 08-02 | Ternary, 1.58-bit, AYOT, CAT-Q, Reasoning | cs.CL, cs.AI | 量化 |
| 3 | 2608.01653 | Hadamard-Domain Model Quantization for Learned Image Coding | Junqi Shi 等 | 08-03 | INT8, Hadamard, PTQ, QAT, LIC | cs.CV | 量化 |
| 4 | 2608.01343 | DeVIT: Low-Power Vision Transformer Acceleration Using Delta Computation | Reyhaneh Hosseinzadeh 等 | 08-02 | Low-bit, Delta Computation, ViT, Multiplier-less | cs.AR | 量化 |
| 5 | 2608.00859 | SparseKAN: Compressing Kolmogorov-Arnold Networks Across Basis Functions, Neurons, and Bits | Kazi Ahmed Asif Fuad 等 | 08-01 | KAN, Pruning, Quantization, FPGA, INT8/4-bit | cs.LG | 量化 |
| 6 | 2608.00481 | F-WANDA: Fisher-Reweighted Post-Training Pruning for Sustainable Deployment of LLMs | Himanshu Mishra | 08-01 | Pruning, Fisher Information, WANDA, LLM | cs.LG | 剪枝 |
| 7 | 2608.01985 | DiffPrune: differentiable information throttling for token pruning in vision-language models | Landi He 等 | 08-03 | Token Pruning, VLM, Differentiable, Information Throttling | cs.CV | 剪枝 |
| 8 | 2608.01979 | ET-Prune: Evidence-Aware Dynamic Budgeting for Visual Token Pruning in Text-Rich MLLMs | Zizhong Ding 等 | 08-03 | Visual Token Pruning, MLLM, Evidence-Aware, OCR | cs.CV | 剪枝 |
| 9 | 2608.01536 | Celty: SpMspV GPU Kernel and SIMT Co-Design for Efficient Dual-Sparse LLM Inference | Ruokai Yin 等 | 08-02 | Dual-Sparsity, spMspV, GPU Kernel, SIMT, LLM | cs.AR | 剪枝 |
| 10 | 2608.00129 | Progressive²: A Teacher-Student Progressive Co-Evolving Knowledge Distillation Method for Substantial Model Compression | Tiancong Cheng 等 | 07-31 | Knowledge Distillation, Progressive, Compression, Adapter | cs.CV | 知识蒸馏 |
| 11 | 2608.01631 | Does Accuracy Equal Evidence? Reasoning Faithfulness under KV Cache Compression | Mengting Ai 等 | 08-03 | KV Cache Compression, Reasoning, Faithfulness, Token Eviction | cs.CL | 其他 |
| 12 | 2608.02134 | Messages, Not Tokens: Grounded Coresets for Faithful VLM Compression | Long Qian 等 | 08-03 | VLM Compression, Coreset, Visual Token, Pruning | cs.CV | 其他 |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 5 篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| FOCUS (2608.01847) | FP4 (MXFP4/NVFP4) PTQ | 多 LLM 系列 | CRS 松弛量化/反量化尺度耦合 + DGS 子块级尺度优化，SOTA FP4 精度无额外推理开销 |
| ScaleQ-1.58 (2608.01078) | 1.58-bit 三值 PTQ | Qwen3 (1.7B-235B), MoE | AYOT 校准（推理链作为上下文）+ CAT-Q 可微三值化，4M token 达 BitNet b1.58 90.52% |
| HaTQ (2608.01653) | INT8 PTQ/QAT | 学习图像编码 (LIC) | Hadamard 正交变换重参数化，Double-Hadamard 与 Weight-only 两种形式，敏感层自适应分配 |
| DeVIT (2608.01343) | 低比特 + 差分计算 | Vision Transformer | 利用低比特值局部性，差分编码消除乘法，移位-加法替代矩阵乘法 |
| SparseKAN (2608.00859) | INT8/4-bit QAT + 剪枝 | KAN 网络 | 三轴压缩（基函数门控 + 神经元剪枝 + 量化），FPGA 上 23.63× 延迟降低 |

### 2.2 剪枝与稀疏化 (Pruning & Sparsity) — 4 篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| F-WANDA (2608.00481) | 权重非结构化剪枝 | LLaMA-2 (7B/13B/70B) | Fisher 信息重加权逐行预算分配，50% 稀疏度 MMLU +1.6pp，能耗仅 SparseGPT 1/3 |
| DiffPrune (2608.01985) | 视觉 token 剪枝 | VLMs (DeiT 探针) | 信息节流器替代 Gumbel-STE，梯度一致性提升 4.4×-28.4×，保留 96.5% 精度加速 2.85× |
| ET-Prune (2608.01979) | 视觉 token 剪枝 | MLLM (Qwen3-VL-8B, InternVL3.5-8B) | 证据感知动态预算，training-free，OCRBench-v2 上 +1.80/+0.68pp |
| Celty (2608.01536) | 双稀疏 (权重+激活) | LLaMA-2-13B | RLC-CSC 格式 + spMspV kernel + Sparse SIMT 微架构，5.3× 加速 |

### 2.3 知识蒸馏 (Knowledge Distillation) — 1 篇

| 论文 | 蒸馏类型 | 目标 | 核心贡献 |
|------|---------|------|---------|
| Progressive² (2608.00129) | 渐进式师生协同蒸馏 | 图像分类模型 | 表示空间渐进（教师纳入层 + 学生缩小层），本征维度诊断师生失配 |

### 2.4 其他 (KV Cache / VLM 压缩) — 2 篇

| 论文 | 技术类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| KV Cache Faithfulness (2608.01631) | KV cache 压缩评估 | 推理 LLMs | 发现"答案-证据鸿沟"，量化比驱逐在证据保真上更安全 |
| GMC (2608.02134) | VLM 视觉 token 压缩 | Qwen2.5-VL-7B 等 | 解码器消息核心集，支撑分配 + 群体传输，减 80.2% token 保留 97.78% 能力 |

---

## 三、评分总览

### 评分标准说明
- **精度效果** (1-10)：量化/压缩后模型性能保持程度
- **压缩倍率** (1-10)：实际压缩比与加速效果
- **创新性** (1-10)：方法的新颖性与理论贡献
- **可复现性** (1-10)：代码可用性与方法描述的完整度

### 3.1 完整评分表

| 序号 | arXiv ID | 论文标题 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合均分 |
|:---:|----------|---------|:---:|:---:|:---:|:---:|:---:|
| 1 | 2608.01847 | FOCUS | 9 | 8 | 9 | 8 | 8.5 |
| 2 | 2608.01078 | ScaleQ-1.58 / AYOT | 9 | 10 | 9 | 7 | 8.8 |
| 3 | 2608.01653 | HaTQ | 8 | 7 | 7 | 7 | 7.3 |
| 4 | 2608.01343 | DeVIT | 7 | 8 | 7 | 6 | 7.0 |
| 5 | 2608.00859 | SparseKAN | 7 | 8 | 8 | 8 | 7.8 |
| 6 | 2608.00481 | F-WANDA | 8 | 7 | 7 | 7 | 7.3 |
| 7 | 2608.01985 | DiffPrune | 8 | 8 | 8 | 7 | 7.8 |
| 8 | 2608.01979 | ET-Prune | 8 | 7 | 7 | 7 | 7.3 |
| 9 | 2608.01536 | Celty | 7 | 9 | 9 | 6 | 7.8 |
| 10 | 2608.00129 | Progressive² | 7 | 7 | 7 | 6 | 6.8 |
| 11 | 2608.01631 | KV Cache Faithfulness | 7 | 6 | 8 | 8 | 7.3 |
| 12 | 2608.02134 | GMC | 9 | 8 | 8 | 7 | 8.0 |

### 3.2 评分明细说明

**FOCUS (2608.01847)** — 精度 9 / 压缩 8 / 创新 9 / 复现 8
- SOTA FP4 精度，MXFP4/NVFP4 双格式支持，无额外推理开销
- CRS 松弛量化/反量化尺度耦合的洞察新颖且深刻；代码将开源 (AngelSlim)

**ScaleQ-1.58 / AYOT (2608.01078)** — 精度 9 / 压缩 10 / 创新 9 / 复现 7
- 1.58-bit 三值量化压缩比极高（~10×），Qwen3-1.7B 达 BitNet b1.58 90.52% 性能
- AYOT "推理链作为校准上下文"的洞察极具创新性；仅 4M 校准 token（减少 100 万倍）
- 代码将开源 (BitTern)，但 CAT-Q 可微三值化复现复杂度较高

**HaTQ (2608.01653)** — 精度 8 / 压缩 7 / 创新 7 / 复现 7
- Hadamard 变换使权重分布峰度从 3.76 降至 0.03，INT8 量化显著改善
- 敏感层自适应分配 Double-Hadamard / Weight-only 形式实用性强；代码将公开

**DeVIT (2608.01343)** — 精度 7 / 压缩 8 / 创新 7 / 复现 6
- 低比特值局部性 + 差分计算消除乘法，15.7% 乘法消除率
- 无乘法矩阵乘法思路新颖，但加速比受限于差分编码效率

**SparseKAN (2608.00859)** — 精度 7 / 压缩 8 / 创新 8 / 复现 8
- 三轴压缩（基函数 + 神经元 + 精度）系统性框架，MNIST 上移除 73% 参数无精度损失
- FPGA 上 23.63× 延迟降低；代码已开源 (OSU-STARLAB/SparseKAN)

**F-WANDA (2608.00481)** — 精度 8 / 压缩 7 / 创新 7 / 复现 7
- Fisher 信息重加权逐行预算，LLaMA-2-7B 50% 稀疏 MMLU +1.6pp
- 关键洞察：Fisher 加权分数在逐行 top-k 下退化为恒等，必须作用在预算维度

**DiffPrune (2608.01985)** — 精度 8 / 压缩 8 / 创新 8 / 复现 7
- 信息节流器替代 Gumbel-STE，梯度一致性提升 4.4×-28.4×
- 保留 96.5% 精度加速 2.85×，仅 0.69ms 推理开销；代码将公开

**ET-Prune (2608.01979)** — 精度 8 / 压缩 7 / 创新 7 / 复现 7
- Training-free 证据感知动态预算，OCR 任务上显著领先
- 15,194 样本分析证明固定比例失效，实证扎实

**Celty (2608.01536)** — 精度 7 / 压缩 9 / 创新 9 / 复现 6
- 软硬件协同设计（RLC-CSC + kernel + 微架构），5.3× 加速
- 双稀疏 spMspV 场景创新性强，但依赖硬件协同设计，纯软件复现受限

**Progressive² (2608.00129)** — 精度 7 / 压缩 7 / 创新 7 / 复现 6
- 表示空间渐进蒸馏 + 本征维度诊断，四基准持续超 SOTA
- 方法描述完整但无代码公开

**KV Cache Faithfulness (2608.01631)** — 精度 7 / 压缩 6 / 创新 8 / 复现 8
- "答案-证据鸿沟"概念新颖，量化比驱逐更安全的结论有实践指导意义
- 代码已开源 (famous-blue-raincoat/Safe_KV_Compress)，固定轨迹重放协议可复现

**GMC (2608.02134)** — 精度 9 / 压缩 8 / 创新 8 / 复现 7
- 解码器消息核心集范式转换，Qwen2.5-VL-7B 减 80.2% token 保留 97.78% 能力
- 支撑分配 + 群体传输两耦合组件理论扎实

---

## 四、值得关注的高亮点

1. **FP4 尺度优化突破**: [2608.01847] FOCUS 发现量化尺度无需遵循硬件离散格式约束，通过 CRS 松弛耦合 + DGS 子块级优化实现 SOTA FP4 精度，无额外推理开销。

2. **1.58-bit 推理量化**: [2608.01078] ScaleQ-1.58 提出 AYOT 校准——用模型自身推理链作为校准上下文，仅 4M token 即可让 Qwen3-1.7B 三值量化达到 BitNet b1.58 90.52% 性能，比传统方法减少 100 万倍校准数据。

3. **Hadamard 变换量化**: [2608.01653] HaTQ 用正交 Hadamard 变换将权重分布峰度从 3.76 降至 0.03，使重尾分布变为均匀分布，显著提升 INT8 量化精度。

4. **可微 token 剪枝**: [2608.01985] DiffPrune 用信息节流器（保方差噪声注入）替代 Gumbel-STE 的离散选择近似，使损失沿真实信息节流路径可微，梯度一致性提升 4.4×-28.4×。

5. **双稀疏 GPU 协同设计**: [2608.01536] Celty 针对权重+激活双稀疏场景设计 RLC-CSC 格式和 Sparse SIMT 微架构，在 70% 双稀疏度下达 5.3× 加速。

6. **VLM 消息核心集**: [2608.02134] GMC 将视觉压缩从"保留重要 token"范式转换为"保留解码器消息"，通过支撑分配和群体传输，减 80.2% token 保留 97.78% 能力。

---

## 五、量化论文代码复现总结

| 论文 | 代码路径 | 运行状态 | 核心实现 |
|------|---------|:-------:|---------|
| FOCUS (2608.01847) | scripts/quantization/2608.01847/ | ✅ 已验证 | CRS 耦合松弛 + DGS 双粒度缩放，FP4 (E2M1) 量化，端到端尺度学习 |
| ScaleQ-1.58 (2608.01078) | scripts/quantization/2608.01078/ | ✅ 已验证 | 三值量化 + AYOT 校准数据构建 + CAT-Q 可微三值化训练 |
| HaTQ (2608.01653) | scripts/quantization/2608.01653/ | ✅ 已验证 | Hadamard 正交变换重参数化 + INT8 量化 + 敏感层识别 |
| DeVIT (2608.01343) | scripts/quantization/2608.01343/ | ✅ 已验证 | 低比特量化 + 差分编码 + 移位-加法替代乘法 |
| SparseKAN (2608.00859) | scripts/quantization/2608.00859/ | ✅ 已验证 | 可微门控剪枝 + INT8/4-bit 量化感知训练 + 三轴压缩 |

所有 demo.py 均以 Qwen3-0.6B 为目标模型，共享 `scripts/quantization/quantization_toolkit.py` 工具包。真实模型权重已缓存可加载，代码在 CPU 上可运行。

---

*报告生成时间: 2026-08-05 (Asia/Shanghai)*
