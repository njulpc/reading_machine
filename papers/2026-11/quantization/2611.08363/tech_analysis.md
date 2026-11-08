# StrataFlux: Memory-Hierarchy-Native Low-Bit LLM Inference

> arXiv: 2611.08363；v1：2026-11-05T17:42:06+00:00（UTC） / 2026-11-06T01:42:06+08:00（北京时间）。
> 分类：Machine Learning (cs.LG) ; Distributed, Parallel, and Cluster Computing (cs.DC)。归档以 v1 北京时间月份为准。
> 证据：[官方摘要与提交历史](https://arxiv.org/abs/2611.08363)；[官方PDF](https://arxiv.org/pdf/2611.08363v1)。以下论文结果均为作者报告，本地结果另行标注。

## 1. 核心速览

**研究主题**：quantization / StrataFlux。

**一句话总结**：StrataFlux把低比特常驻底座与按需补充精度分离，拟合被选中通道以补偿遗漏误差；本机验证显示小校准集上的收益明显大于留出集。

## 2. 研究背景与动机

量化丢失精度，传统offload保精度却被带宽和随机访问时延阻塞。误差贡献随输入变化：对R=W−Wq，通道i贡献xiR[:,i]。当前最大的输入通道与校准时静态重要通道不完全相同，KV关注token也随query变化，因此可按当下需求只补一部分精度。

## 3. 核心方法与创新点

1. 每1024输入通道选k个最大|x|，保留其符号。常驻Wq输出上增加选中列C的乘积，补偿矩阵用4bit编码。
2. 不只量化原残差R，而最小化 `E||Rx-Cz_k(x)||²+λ||C-R||²`。令M=E[zzᵀ]、G=E[xzᵀ]，解 `C(M+λI)=RG+λR`，默认λ为M平均对角线；论文用RedPajama校准。
3. KV以KVarN低比特码为底座，用额外位细分其量化区间。每组query head共享的KV head以组内attention质量之和、再跨query head取max选token组；用修正分子与归一化分母同时替换被选项，未选token仍贡献低比特值（式7–8）。
4. Q/K/V和gate/up可提前选通道fetch lead；output/down可延后加入residual stream实现fetch lag。统一内存系统用SSD后台读取和RAM cache，miss可跳过供后续step使用；专用GPU直接从pinned host RAM取。

## 4. 实验设计与结果

主实现在llama.cpp的CUDA/Metal路径，涵盖Llama3.1-8B、Qwen3-8B/32B等。RTX5090、YAQA2bit底座，Llama WikiText-2 PPL9.46→8.40，吞吐245.8→234.4tok/s（保留95.4%），GPU内存均3.9GB；BF16 PPL7.22仍更好（表1、图9）。权重与KV均2bit时Qwen3-8B AIME24/25由11.0%升47.1%；不要与weight-only表2的19.2→46.7混用。主KV设置每组2 token（统一内存4），选1/128组，额外+4/+4bits。外部补偿存储、缓存和元数据不为零。

**本地实测**：见 `scripts/quantization/2611.08363/`。真实Qwen3-0.6B首层q_proj完整2048×1024权重，2×64 token校准、2×64留出，3bit对称per-output-channel RTN底座，per-input-column 4bit补偿，chunk1024/k32，FP64解式4。留出MSE：底座0.00605701、原残差补偿0.00372963、拟合补偿0.00372121；校准拟合0.00055355。6项断言通过，KV修正式与直接替换后dense attention差约2.56e-12。该KV检查为小张量，不是Qwen端到端KV系统。

## 5. 局限性与未来展望

本地只复现数值组件：RTN替代论文YAQA/AWQ，手写文本替代RedPajama；没有KVarN编码、bit packing、神经元bundle、SSD/cache、跨层异步kernel或全模型PPL。没有把浮点仿真解释为真实内存节省。校准/留出差距提示小样本过拟合；外存补精度只有在选择、命中率和传输预算合适时才有系统收益。

## 6. 学术启发

把压缩设计拆成“常驻近似、稀疏修正、交付时机”三个可测模块。用实际部署的选择器z训练补偿器，而非只最小化权重重构误差；校准集与留出集都要报告。精度提升必须按总存储和实际通信成本重新衡量。

**四维评分（1–10，编辑判断而非客观排名）**：精度效果 8/10；压缩倍率 8/10；创新性 9/10；可复现性 7/10。

精度8：多模型低比特恢复但仍低于BF16；压缩8：降低GPU常驻精度但依赖外部补偿存储；创新9：编码、选择与交付联合设计；复现7：真实Qwen投影和代数检查通过，系统级内核与吞吐未复现。
