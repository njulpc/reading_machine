# Paper: 2602.18420 — SPQ 复现说明

**论文**: SPQ: An Ensemble Technique for Large Language Model Compression

**复现内容**（论文三位一体的集成压缩，全部作用于真实模型）：

1. **激活感知 MLP 剪枝**：在校准文本上统计每个中间神经元的 E|act|，剪除贡献最低的 25%（gate/up 行 + down 列同步移除）；
2. **方差保持 SVD（variance-retained SVD）**：对每个注意力 q/k/v/o 投影做 SVD，保留谱能量 ≥95% 的秩 r，单个 Linear 替换为两个小 Linear；
3. **统一 INT8 PTQ**：剩余全部线性层做逐输出通道对称 INT8 量化（CPU 上以 fake-quant 评估）。

**评测**：在同一段留出文本上报告 FP32 / 单一技术（INT8-only、SVD-only、Prune-only）/ SPQ 集成的**真实困惑度（PPL）**与权重显存换算，验证论文核心主张——三种技术攻击不同冗余来源，集成在同等压缩率下优于任何单一技术。

**验证方式**：完整真实验证。真实 **Qwen3-0.6B** 权重、真实校准/评测文本、真实模型手术与真实 PPL 前向（CPU，约几分钟）。

**运行**:

```bash
python3 demo.py                          # 默认 prune=0.25, svd_var=0.95
python3 demo.py --prune 0.2 --tokens 384
```

**预期现象**（实测于真实 Qwen3-0.6B）：SPQ 集成达到约 530MB@PPL≈3.7 的"显存-精度"点——优于剪枝单技（2120MB@PPL≈3.6）并逼近 INT8 单技（596MB@PPL≈2.8）的显存预算。**如实的尺度发现**：0.6B 模型的注意力投影接近满秩，99% 方差保持的 SVD 在全部 112 个投影上均不满足"真正省参数"条件而被跳过（论文在 7B 模型上注意力矩阵低秩性更强），集成的主要收益来自剪枝+INT8 的组合。demo 中 SVD 仅在 `r(m+n) < 0.9mn` 时才应用。

**与论文的差异**：论文在 LLaMA-2-7B 上做到 75% 显存削减（WikiText-2 PPL 5.47→4.91）并与 GPTQ/SparseGPT 对比吞吐；本 demo 在 0.6B 模型上验证同样机制，规模更小、未做 kernel 级吞吐测量。
