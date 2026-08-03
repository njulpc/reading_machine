# ArXiv 量化与模型压缩领域论文日报

**目标日期**: 2026-08-03（周一）
**收集日期范围**: 2026-07-30 ~ 2026-07-31 补充收录（arXiv API 最新可用论文截止于 2026-07-31T17:55Z，08-01 至 08-03 提交的论文尚未进入 API 索引）
**检索关键词**: quantization, quantize, low-bit, model compression, pruning, sparsity, knowledge distillation, KV cache compression, mixed precision, GPTQ, AWQ
**数据来源**: arXiv.org (cs.LG, cs.CL, cs.CV, cs.AI, cs.AR)
**检索方式**: arXiv API (`http://export.arxiv.org/api/query`)，submittedDate 范围 + 关键词过滤

---

## 日期说明

2026-08-03 为周一，arXiv API 的 export 接口存在 1-3 天索引延迟，截至运行时（2026-08-04）最新可用论文截止于 2026-07-31T17:55:02Z，08-01 至 08-03 提交的论文尚未进入 API 索引。8 月 1-2 日为周末（arXiv 不发布新论文）。

本次日报补充收录 2026-07-30 和 2026-07-31 提交但在前日流水线中遗漏的 12 篇模型压缩相关论文，确保覆盖完整。此前流水线已覆盖 07-30 的 12 篇论文（2607.28292 CACHE-UK、2607.28405 QuantWAMs、2607.28589 MixFrag、2607.28319 Fairness Pruning、2607.28341 Token Tendencies、2607.28418 WIDE、2607.28449 Lightning OPD 2.0、2607.28069 SemPIC、2607.28097 Expert Reduction、2607.28196 Fidelity Is Not Safety、2607.28263 CoMem、2607.28627 ReToken），本次新增 12 篇遗漏论文。

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 | 分类 |
|:---:|----------|---------|------|:-------:|-----------|------|------|
| 1 | 2607.27704 | LightRot: A Light-Weighted Rotation Scheme for Low-Bit LLM Inference | Sangjin Kim 等 | 07-30 | Rotation, GLR, ODA, FHT, 4-bit, Hardware | cs.AR, cs.LG | 量化 |
| 2 | 2607.27694 | GyRot: Rotation and Fine-grained Group Quantization for Low-bit LLM | Sangjin Kim 等 | 07-30 | CoRFiG, HAP, INT4, Group Quantization, Hardware | cs.AR, cs.LG | 量化 |
| 3 | 2607.28699 | WitCert: Sound Runtime Risk Observability for KV-Cache Quantization | Fanzhe Wei, Li Liu | 07-30 | KV-cache Quantization, Runtime Certificate, Lean 4, SGLang | cs.AR, cs.AI | 量化 |
| 4 | 2607.29397 | Studying Quantization Trade-offs for Efficient MT Deployment | Jim Zhao 等 | 07-31 | W4A8, W8A8, GPTQ, SmoothQuant, MT, vLLM | cs.CL, cs.PF | 量化 |
| 5 | 2607.29659 | GQ-FSL: Green Quantized Federated Split Learning | Idan Roth, Lutz Lampe | 07-31 | Stochastic Quantization, Federated, Split Learning, Energy | cs.LG, cs.DC | 量化 |
| 6 | 2607.27591 | Prox: Training-Free FFN Activation Sparsity in LLMs | Jinyi Liu 等 | 07-30 | FFN Sparsity, SwiGLU, Training-Free, Proxy | cs.LG, cs.CL | 剪枝 |
| 7 | 2607.27700 | CaRe: Robust Visual Token Reduction against Semantic Drift in VLMs | Jiasheng Li 等 | 07-30 | Visual Token Reduction, Pruning, VLM, Calibration | cs.CV | 剪枝 |
| 8 | 2607.27952 | LAST: Last Query Token Guides Visual Token Pruning for Edge-Cloud MLLM | Feng Yang 等 | 07-30 | Visual Token Pruning, Edge-Cloud, MLLM, Query-aware | cs.CV, cs.AI | 剪枝 |
| 9 | 2607.29591 | ResKV: Reconstructing Omitted Attention for KV Cache Compression | Yuhang Zhan 等 | 07-31 | KV Cache Compression, Residual Cache, Softmax, LongBench | cs.CL | 其他 |
| 10 | 2607.27600 | Back from the Future: KV Cache Management by Counter-Causal Surprise | Stephen Gould 等 | 07-30 | KV Cache Eviction, Counter-Causal, Pruning, LLM | cs.LG | 其他 |
| 11 | 2607.27735 | SparseSpec-L: Train-Free Self-Speculative Decoding | Yuesong Liu 等 | 07-30 | Speculative Decoding, Sparse KV Cache, Self-Speculative | cs.CL | 其他 |
| 12 | 2607.28707 | Demystifying Entropy-based Selection for CoT Compression | Sara Candussio 等 | 07-30 | CoT Compression, Entropy Pruning, Reasoning, Activation Patching | cs.CL | 其他 |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 5 篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| LightRot (2607.27704) | 4-bit 对称 + 旋转 | LLaMA2-13B, LLaMA3-8B | GLR 局部旋转 + ODA 异常值对齐 + 分层 FHT，28nm 下 27.4 TOPS/W |
| GyRot (2607.27694) | INT4 非对称分组 | LLaMA 系列 | CoRFiG 粗旋转细分组 + HAP 谐波排列，全整数反量化，3.4x 加速 |
| WitCert (2607.28699) | INT8/FP8 KV-cache | 7B 级模型, SGLang | 可证明可靠运行时风险度量器，RoPE 带酉性，Lean 4 验证，FP8 从 22.8 恢复到 79.7 |
| MT量化权衡 (2607.29397) | W4A8/W8A8/W4A16 | EuroLLM, Hy-MT2 (1.7B-22B) | 编排级量化评估，文档分块+量化交互，Hy-MT2 鲁棒而 EuroLLM 敏感 |
| GQ-FSL (2607.29659) | 随机量化 1-q_max bit | DNN (边缘设备) | 非对称精度 q_c≠q_s，量化误差界 d_c/2^{2q_c}+d_s/2^{2q_s}，联合优化分割点与精度 |

### 2.2 剪枝与稀疏化 (Pruning & Sparsity) — 3 篇

| 论文 | 剪枝类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| Prox (2607.27591) | FFN 激活稀疏化 | 10 个 LLM (6 个模型族) | 两阶段代理框架，SwiGLU 中间态通道选择，70% 稀疏度下 1.99x 加速 |
| CaRe (2607.27700) | 视觉 token 剪枝 | VLMs | "先校准再推理"原则，剪枝 94.4% 视觉 token 保留 96.4% 性能，2.30x 加速 |
| LAST (2607.27952) | 视觉 token 剪枝 | MLLM (边缘-云) | 最后查询 token 注意力引导，保留 12.5% token 保持 95.4% 精度 |

### 2.3 其他 (KV Cache / 推测解码 / 推理压缩) — 4 篇

| 论文 | 技术类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| ResKV (2607.29591) | KV cache 压缩 | LLMs (LongBench, RULER) | 残差缓存重建被驱逐 token 的注意力贡献，共享 softmax 归一化 |
| Back from the Future (2607.27600) | KV cache 驱逐 | 开源 LLMs | 反因果惊喜驱逐，复用已有 KV cache，单层近似 7-9x 加速 |
| SparseSpec-L (2607.27735) | 自推测解码 | LLMs (长上下文) | 动态稀疏可召回 KV cache，回收注意力统计，在线熵控制器 |
| CoT Compression (2607.28707) | 推理链压缩 | 推理 LLMs | 证伪熵选择优于随机剪枝，激活 patching 证明信息分布在整个推理链 |

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
| 1 | 2607.27704 | LightRot | 8 | 9 | 8 | 6 | 7.8 |
| 2 | 2607.27694 | GyRot | 8 | 9 | 9 | 6 | 8.0 |
| 3 | 2607.28699 | WitCert | 9 | 7 | 10 | 7 | 8.3 |
| 4 | 2607.29397 | MT量化权衡 | 7 | 7 | 5 | 8 | 6.8 |
| 5 | 2607.29659 | GQ-FSL | 6 | 6 | 7 | 6 | 6.3 |
| 6 | 2607.27591 | Prox | 8 | 8 | 7 | 7 | 7.5 |
| 7 | 2607.27700 | CaRe | 9 | 8 | 7 | 7 | 7.8 |
| 8 | 2607.27952 | LAST | 8 | 8 | 7 | 7 | 7.5 |
| 9 | 2607.29591 | ResKV | 8 | 7 | 8 | 6 | 7.3 |
| 10 | 2607.27600 | Back from the Future | 7 | 7 | 8 | 8 | 7.5 |
| 11 | 2607.27735 | SparseSpec-L | 7 | 7 | 7 | 6 | 6.8 |
| 12 | 2607.28707 | CoT Compression | 6 | 5 | 8 | 7 | 6.5 |

### 3.2 评分明细说明

**LightRot (2607.27704)** — 精度 8 / 压缩 9 / 创新 8 / 复现 6
- 4-bit 推理在 LLaMA2-13B/LLaMA3-8B 上准确，MT-Bench 验证；27.4 TOPS/W 能效突出
- GLR+ODA 算法创新性强但依赖 28nm 硬件，纯软件复现受限

**GyRot (2607.27694)** — 精度 8 / 压缩 9 / 创新 9 / 复现 6
- INT4 SOTA 精度，3.4x 加速 + 3.6x 能效；CoRFiG+HAP 首次解决旋转-分组冲突
- 硬件加速器仿真，软件层面复现困难

**WitCert (2607.28699)** — 精度 9 / 压缩 7 / 创新 10 / 复现 7
- FP8 从 22.8 恢复到 79.7，认证 INT8 服务 1.88x 更多 KV token
- Lean 4 机器验证 + SGLang 集成，理论贡献极高；代码部分开源

**MT量化权衡 (2607.29397)** — 精度 7 / 压缩 7 / 创新 5 / 复现 8
- W8A8 匹配 BF16 基线，系统级编排评估实用
- 实证研究而非新方法，创新性有限但可复现性高

**GQ-FSL (2607.29659)** — 精度 6 / 压缩 6 / 创新 7 / 复现 6
- 非对称精度解耦能耗与收敛，理论分析完整
- 联邦学习场景特定，通用性有限

**Prox (2607.27591)** — 精度 8 / 压缩 8 / 创新 7 / 复现 7
- 70% FFN 稀疏度下 1.99x 加速，10 个 LLM 验证
- 两阶段代理框架实用，与量化和稀疏注意力兼容

**CaRe (2607.27700)** — 精度 9 / 压缩 8 / 创新 7 / 复现 7
- 剪枝 94.4% 视觉 token 保留 96.4% 性能，2.30x 加速
- "先校准再推理"原则新颖，无训练框架实用

**LAST (2607.27952)** — 精度 8 / 压缩 8 / 创新 7 / 复现 7
- 保留 12.5% token 保持 95.4% 精度，边缘-云协同创新
- 最后查询 token 注意力信号轻量高效

**ResKV (2607.29591)** — 精度 8 / 压缩 7 / 创新 8 / 复现 6
- 残差缓存重建被驱逐 token 贡献，共享 softmax 归一化
- LongBench 和 RULER 上广泛改进，理论洞察深

**Back from the Future (2607.27600)** — 精度 7 / 压缩 7 / 创新 8 / 复现 8
- 反因果惊喜驱逐策略新颖，代码开源
- 单层近似 7-9x 加速，无需训练

**SparseSpec-L (2607.27735)** — 精度 7 / 压缩 7 / 创新 7 / 复现 6
- 统一效率分析 + 动态稀疏可召回 KV cache
- 投稿 AAAI 2027，具体加速倍数在摘要中未明确

**CoT Compression (2607.28707)** — 精度 6 / 压缩 5 / 创新 8 / 复现 7
- 系统性证伪熵选择假设，激活 patching 因果证据
- 负面结果研究，压缩效果有限但科学价值高

---

## 四、整体分析

### 4.1 技术趋势

本次收录的 12 篇论文呈现出以下技术趋势：

1. **旋转量化持续深化**：LightRot 和 GyRot（均来自 KAIST 同一团队）将旋转量化从算法推向硬件实现，分别解决旋转开销（GLR/FHT）和旋转-分组冲突（CoRFiG/HAP）问题，标志旋转量化进入硬件部署阶段。

2. **KV cache 量化/压缩成为热点**：5 篇论文涉及 KV cache（WitCert 量化风险、ResKV 残差重建、Back from the Future 反因果驱逐、SparseSpec-L 稀疏推测），反映长上下文推理的内存瓶颈是当前最紧迫问题。

3. **运行时安全与可证明保证**：WitCert 首次为 KV-cache 量化提供可证明可靠的运行时风险度量，使用 Lean 4 机器验证核心定理，代表压缩安全性的新范式。

4. **视觉 token 剪枝成熟**：CaRe 和 LAST 分别从校准保真和边缘-云协同角度推进视觉 token 剪枝，均实现 >94% 剪枝率下 >95% 性能保持。

5. **系统级评估重要性凸显**：MT 量化权衡研究揭示标准基准无法预测量化与长上下文的交互，GQ-FSL 将量化与能耗/通信联合优化。

### 4.2 量化方法对比

| 方法 | 比特 | 旋转 | 分组 | 硬件 | 精度保持 | 特色 |
|------|------|------|------|------|---------|------|
| LightRot | 4-bit | GLR 局部 | 否 | 28nm ASIC | 高 (MT-Bench) | FHT 低开销旋转 |
| GyRot | INT4 | CoRFiG 粗 | 32 通道 | INT4 PE | SOTA | 旋转-分组协同 |
| WitCert | INT8/FP8 | 否 | 否 | SGLang | 恢复至 79.7 | 运行时风险证书 |
| MT权衡 | W4A8/W8A8 | 否 | 否 | A100/H100 | 模型依赖 | 编排级评估 |
| GQ-FSL | 1-q_max | 否 | 否 | 边缘设备 | 收敛保证 | 非对称精度 |

### 4.3 可复现性评估

本次 5 篇量化论文均已实现 Qwen3-0.6B 代码复现：

| 论文 | 复现路径 | 验证状态 | 核心实现 |
|------|---------|---------|---------|
| LightRot | scripts/quantization/2607.27704/ | ✅ 运行通过 | GLR+ODA+FHT 4-bit 量化，MSE 改善 5.9% |
| GyRot | scripts/quantization/2607.27694/ | ✅ 运行通过 | CoRFiG+HAP+非对称 INT4，改善 4.1% |
| WitCert | scripts/quantization/2607.28699/ | ✅ 运行通过 | RoPE 带酉性+TV 上界+门控，Theorem 1 验证 |
| MT量化 | scripts/quantization/2607.29397/ | ✅ 运行通过 | SmoothQuant+GPTQ W4A8/W8A8/W4A16 |
| GQ-FSL | scripts/quantization/2607.29659/ | ✅ 运行通过 | 随机量化+非对称精度+误差界验证 |

---

## 五、推荐阅读优先级

1. **WitCert (2607.28699)** — 理论贡献最高，可证明可靠的运行时量化风险度量，Lean 4 验证
2. **GyRot (2607.27694)** — HPCA 2026，首次解决旋转与分组量化的根本冲突
3. **LightRot (2607.27704)** — JETCAS，旋转量化硬件部署的完整方案
4. **ResKV (2607.29591)** — KV cache 残差重建思路新颖
5. **Prox (2607.27591)** — FFN 激活稀疏化的实用无训练框架
6. **CaRe (2607.27700)** — 视觉 token 剪枝的校准保真新范式
