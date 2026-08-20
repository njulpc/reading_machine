# AViTS: Adaptive Spatiotemporal Token Selection for Efficient Dynamic-Resolution Generation

- arXiv: [2608.17995](https://arxiv.org/abs/2608.17995)
- 提交日期（v1）：2026-08-18
- 作者：Haoran Qin, Zhengan Yan, Shikang Zheng, Xiaobing Tu, Jiacheng Liu, Yuqi Lin, Chang Zou, JinShan Liu, Peiliang Cai, Xiantao Zhang, Jinkui Ren, Linfeng Zhang
- 分类：cs.CV
- 证据边界：基于 arXiv 摘要与 20 页 v1 PDF；方法是训练免费 token 选择/延迟上采样，论文速度来自 A800/H20 上三个特定 diffusion backbone。

## 1. 核心速览

**研究主题：** 在动态分辨率 DiT 中，融合文本语义注意力与跨去噪步骤的 token 变化，优先上采样重要 token。

**一句话总结：** AViTS 在 FLUX.1-dev 的 NFE=18 配置达到 4.73 s、5.45× latency speedup、4.80× FLOPs reduction，同时 ImageReward 0.9959 高于原始 0.9719；与 step distillation 组合最高达 14.76× FLOPs reduction。

## 2. 研究背景与动机

动态分辨率采样先低分辨率去噪，再上采样到目标分辨率，但统一上采样所有 token 会把大量计算浪费在背景或已稳定区域。已有 partial upsampling 常用边缘或单步 feature statistic，难以同时判断“与 prompt 是否相关”和“该 token 是否仍在快速变化”。

## 3. 核心方法与创新点

1. **三阶段采样。** Stage 1 在 `f=2` 低分辨率完成粗结构并收集 `N_T` 个 latent snapshot/attention；Stage 2 只把 top-`ρM'` token 正交上采样；Stage 3 再上采样剩余 token 并细化。
2. **空间重要性。** 聚合 image query 到全部 text key 的 cross-modal attention；MLLM 可直接取子矩阵，FLUX joint-attention 则用 hook 重构 QK softmax。
3. **时间重要性。** 计算每个 token 各 channel 在收集步骤上的无偏方差，再跨 channel 平均，衡量表示是否仍在演化。
4. **联合选择。** 两种 score 分别 min-max 归一化，以 `S_i=αÂ_i+(1-α)V̂_i` 融合并 top-k；只改变上采样优先级，不训练模型参数。

## 4. 实验设计与结果

- 模型/硬件：FLUX.1-dev（A800）、Qwen-Image-Edit 与 FLUX.1-Kontext-dev（H20）；DrawBench 用 ImageReward/CLIP，GEdit 用 SC/PQ/OS。
- FLUX 文生图：原始 50 NFE 为 25.78 s、3719.50 T FLOPs。AViTS 30 NFE 为 8.21 s（3.14×）、ImageReward 1.0104；18 NFE 为 4.73 s（5.45×）、0.9959。
- 极限配置：14/11/9 NFE 分别 7.06×/8.32×/9.78× latency speedup；9 NFE ImageReward 降至 0.9201，显示极端压缩仍有质量代价。
- 编辑：FLUX-Kontext 11 NFE 达 6.92× latency、8.85× FLOPs，OS 6.57（baseline 6.51）；Qwen-Image-Edit 11 NFE 达 6.95×、8.65×，中英文 OS 7.57/7.48。
- 消融：同 NFE=30、同 `ρ` 时，attention-only/variance-only/mix 的 ImageReward 为 0.9875/0.9846/0.9959；随机选择仅 0.9257。
- 组合：AViTS+step distillation 在 6 NFE 达 14.65× latency、14.76× FLOPs；与 INT8 模型组合 18 NFE 达约 9× FLOPs reduction。

## 5. 局限性与未来展望

- 重要性依赖内部 attention/latent hooks，不是所有 fused 或闭源 backbone 都能低成本暴露这些信号。
- 文生图主要依赖自动指标，且某些极端配置 CLIP-IQA 提升但 CLIPScore 下降，仍需更强人评。
- 只验证三种 diffusion 模型与两类硬件；token 排序、混合分辨率和 coordinate-bound noise 的真实收益可能依赖 kernel 实现。
- 论文没有单列 score 收集与 hook 的内存峰值；与缓存/量化/蒸馏组合的误差交互仍需更全面消融。

## 6. 学术启发

token pruning 不一定要永久删除 token。AViTS 把“何时提升 token 的计算分辨率”作为软预算分配，避免不可逆丢信息。空间语义与时间变化的联合 score 也提供了通用模板：对迭代生成或多阶段推理，应同时衡量 token 对条件的相关性和自身尚未收敛的程度。

