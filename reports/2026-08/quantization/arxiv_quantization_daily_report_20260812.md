# ArXiv 量化与模型压缩领域论文日报

**收集日期范围**: 2026-08-12 (UTC published date)  
**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, low-bit, sparsity  
**数据来源**: arXiv.org

---

## 一、论文总览表

| 序号 | arXiv ID | 论文标题 | 作者 | 提交日期 | 核心关键词 | 领域 |
|:---:|----------|---------|------|:-------:|-----------|------|
| 1 | 2608.12239 | HAMP-LIC: Hessian-Aware Mixed-Precision Post-Training Quantization for Learned Image Compression | Yuefeng Zhang | 08-12 | Hessian, Mixed-Precision, PTQ, LIC | cs.CV |
| 2 | 2608.12026 | SoftWater: Class-Aware Rate Allocation for Softmax Quantization | Joao V. Cavalcanti, Ashia C. Wilson | 08-12 | Softmax, KL-divergence, Class-aware, LM Head | cs.LG |
| 3 | 2608.11786 | Language-Conditional Dequantization: Recovering What Quantization Steals from Non-English Languages | Nirmal Thomas | 08-12 | LoRA, Multilingual, GPTQ, Dequantization | cs.CL |
| 4 | 2608.12259 | Calibration Bets on the Past: Post-Training Quantization for Financial Time-Series Forecasting | Junyi Ye, Ivy Gateri Wanjiku | 08-12 | Calibration, Time-Series, Finance, PTQ | cs.LG |
| 5 | 2608.11693 | Spec Sheets Are Not Kernels: An ISA- and Source-Level Audit of INT8 Availability on NVIDIA Blackwell Ultra | Teng-Ruei Chen | 08-12 | INT8, B300, Hardware Audit, W8A8 | cs.AR |
| 6 | 2608.12140 | FQTree: Fine-grained Quantization and Hardware Generation of Boosted Decision Trees | Zhiqiang Que et al. | 08-12 | BDT, FPGA, Quantization-Aware Training, Leaf Quantization | cs.AR |
| 7 | 2608.12032 | LoSA: Near-Lossless Sparse Attention for Training-Free Video Diffusion Acceleration | Enhuai Liu et al. | 08-12 | Sparse Attention, Video Diffusion, Training-Free | cs.CV |
| 8 | 2608.11829 | Towards Understanding On-Policy Distillation through the Lens of Test-Time Scaling | Xinmu Ge et al. | 08-12 | Distillation, Test-Time Scaling, Capability Boundary | cs.LG |
| 9 | 2608.12099 | RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive Knowledge Distillation | Rong Chao et al. | 08-12 | Mamba, Knowledge Distillation, Speech Enhancement | cs.SD |
| 10 | 2608.11981 | Benchmarking Trustworthiness of SLMs: Pre-trained vs. Compressed | Haokun Lin et al. | 08-12 | Trustworthiness, SLM, Quantization, Pruning | cs.CL |

---

## 二、按技术方向分类

### 2.1 量化 (Quantization) — 6篇

| 论文 | 量化类型 | 目标模型 | 核心贡献 |
|------|---------|---------|---------|
| HAMP-LIC (2608.12239) | Mixed-Precision PTQ | Learned Image Compression | Hessian-aware 4.85x压缩，0.59% BD-rate损失 |
| SoftWater (2608.12026) | Class-Aware LM Head | LLM (1B-32B) | KL最优softmax量化，2-bit head减少45-60%存储 |
| LCD (2608.11786) | Post-hoc LoRA Dequantization | Multilingual LLM (3B) | per-language rank-2 LoRA恢复70-83%多语言性能 |
| Calibration Bets (2608.12259) | Activation Calibration | Financial Forecasting | 系统研究校准策略，percentile恢复53-94%退化 |
| INT8 Audit (2608.11693) | INT8 W8A8 | NVIDIA B300 GPU | 全栈审计发现INT8在B300默认不可部署 |
| FQTree (2608.12140) | Fine-grained Leaf QAT | Boosted Decision Trees | LUT减少26-57%，匹配或提升精度 |

### 2.2 剪枝/稀疏 (Pruning/Sparsity) — 1篇

| 论文 | 技术 | 目标模型 | 核心贡献 |
|------|------|---------|---------|
| LoSA (2608.12032) | Sparse Attention | Video Diffusion Transformer | 99%质量保留阈值，3.2x加速 |

### 2.3 知识蒸馏 (Distillation) — 2篇

| 论文 | 蒸馏类型 | 应用 |
|------|---------|------|
| On-Policy Distillation (2608.11829) | 分析性研究 | LLM推理能力 |
| RT-SEMamba (2608.12099) | Progressive KD | 实时语音增强 |

### 2.4 其他压缩/评估 (Other) — 1篇

| 论文 | 内容 |
|------|------|
| Trustworthiness of SLMs (2608.11981) | 压缩对SLM可信度影响评估 |

---

## 三、按应用领域分类

| 应用领域 | 论文数量 | 代表性论文 |
|---------|:-------:|-----------|
| **大语言模型 (LLM)** | 3 | SoftWater, LCD, Trustworthiness of SLMs |
| **计算机视觉 (CV)** | 2 | HAMP-LIC, LoSA |
| **语音处理** | 1 | RT-SEMamba |
| **金融时序** | 1 | Calibration Bets on the Past |
| **硬件/边缘** | 2 | INT8 Audit, FQTree |

---

## 四、值得关注的高亮点

1. **LM Head量化突破**: [2608.12026] SoftWater首次实现2-bit LM Head量化，perplexity仅增加2.9-3.7%，使LLM的实际压缩率大幅提升。

2. **多语言量化公平性**: [2608.11786] 发现INT3 GPTQ对非英语语言的perplexity损害是英语的2-4倍，LCD以0.12%额外参数恢复70-83%性能。

3. **硬件审计警示**: [2608.11693] NVIDIA B300 GPU上INT8 W8A8虽存在于规格书，但在PTX ISA、CUTLASS、vLLM/SGLang三层一致撤回，默认不可部署。

4. **蒸馏本质洞察**: [2608.11829] 揭示On-Policy Distillation主要是"幻觉蒸馏"——提升采样效率而非真正扩展能力边界。

5. **金融PTQ校准**: [2608.12259] 560模型×8年回测证明4-bit PTQ中校准策略是性能首要决定因素。

---

## 五、量化论文评分汇总

| arXiv ID | 论文标题 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 平均分 |
|---------|---------|:-------:|:-------:|:-----:|:-------:|:-----:|
| 2608.12239 | HAMP-LIC | 9 | 8 | 8 | 7 | **8.0** |
| 2608.12026 | SoftWater | 9 | 9 | 9 | 8 | **8.8** |
| 2608.11786 | LCD | 8 | 9 | 9 | 9 | **8.8** |
| 2608.12259 | Calibration Bets | 7 | 6 | 7 | 9 | **7.3** |
| 2608.11693 | INT8 Audit | 6 | 5 | 9 | 10 | **7.5** |
| 2608.12140 | FQTree | 8 | 8 | 8 | 7 | **7.8** |

**评分说明**:
- **精度效果**: 量化后模型性能保留程度（10=无损）
- **压缩倍率**: 压缩效率（10=极高压缩比）
- **创新性**: 方法新颖程度（10=突破性创新）
- **可复现性**: 实验可复现程度（10=完全可复现）

---

## 六、整体分析

### 6.1 当日研究趋势

**趋势一：从通用量化到任务/结构专用量化**

今日6篇量化论文中有5篇针对特定场景设计：图像压缩(HAMP-LIC)、LM Head(SoftWater)、多语言(LCD)、金融时序(Calibration Bets)、决策树(FQTree)。这表明领域正在从"通用PTQ工具"向"专用高精度方案"演进。

**趋势二：量化可信度的觉醒**

LCD关注多语言公平性，INT8 Audit关注部署可靠性，Trustworthiness评估关注压缩对伦理的影响。量化研究正在从单纯的精度-效率权衡扩展到更全面的AI系统质量保障。

**趋势三：训练自由与后 hoc 修正**

LoSA(稀疏注意力)和LCD(LoRA修正)都强调无需重新训练即可部署，这对生产环境极具吸引力。未来可能出现更多"即插即用"的压缩后修正工具。

### 6.2 实践建议

1. **LM Head量化**: 对于1B-7B模型的边缘部署，SoftWater使2-bit head成为实际可行方案，可立即应用。
2. **多语言模型**: 在量化多语言LLM时，必须为不同语言预留修正预算，LCD提供了一种极轻量的解决方案。
3. **硬件采购**: 在评估新GPU时，不能仅看规格书，必须进行全栈可用性审计（如INT8在B300上的案例）。
4. **金融部署**: 4-bit PTQ在金融时序任务中需要谨慎选择校准策略，percentile校准比abs-max更可靠。

---

*报告生成时间: 2026-08-14 06:00 GMT+8*  
*分支: feature/arxiv-daily-2026-08-14*
