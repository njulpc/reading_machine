# DynaForcing: Overcoming Dynamic Collapse in Self-Forcing Distillation for Streaming Avatar Generation

- arXiv: [2608.17707](https://arxiv.org/abs/2608.17707)
- 提交日期（v1）：2026-08-18
- 作者：Yubo Huang, Sirui Zhao, Xinchen Yao, Zhengye Zhang, Jinyang Huang, Fengqi Cui, Shiwei Wu, Enhong Chen
- 分类：cs.CV, cs.MM
- 证据边界：基于 arXiv 摘要与 12 页 v1 PDF；训练规模为 14B video model 与 H100 集群，不能以小模型实验替代其生成质量结论。

## 1. 核心速览

**研究主题：** 修复 streaming video 的 self-forcing/DMD 蒸馏把 student 推向近静态模式的“dynamic collapse”。

**一句话总结：** DynaForcing 以 ground-truth 混合起点、动态奖励和 reference perturbation 三层干预，将短视频 Dyn-Deg 从 LiveAvatar 的 0.31 提升到 0.73、Sync-C 从 7.03 提升到 7.68，同时用图剪枝与 gradient replay 把训练从 128×H100/7,111 GPU·h 降到 8×H100/667 GPU·h。

## 2. 研究背景与动机

self-forcing 让少步扩散 student 逐块生成，并用自己的历史构造 KV cache，适合实时 streaming。然而 reverse-KL 的 mode-seeking 倾向会偏爱“画质好但几乎不动”的静态模式；一旦早期块失去动作，后续块继续条件化在静态历史上，形成反馈坍缩。avatar 对唇形和微表情极敏感，因此该失败尤其明显。

## 3. 核心方法与创新点

1. **Hybrid Forcing。** 以概率 `p_data` 从加噪真实 latent 而非纯 Gaussian 开始整段 rollout，为动态结构提供锚点；主设定 `p_data=0.3`。
2. **Dynamics-Aware Reward。** 用 SyncNet 的 Sync-C 与 3DMM expression variance 组成 `R_dyn`，以 `exp(α·stopgrad(R_dyn))` 重加权 DMD gradient；`λ_sync=1.0, λ_exp=0.5, α=0.1`。
3. **Reference Perturbation。** 通过视角、背景和光照编辑破坏 reference 与目标的像素捷径；ArcFace 相似度需 >0.9，并按 SSIM 分成 5 桶均匀采样。
4. **训练内存压缩。** detach 跨块 KV cache，删除影响很小的跨块梯度；rollout 无梯度保存中间量，再逐块 replay 梯度，峰值 activation 约降 `K×`。

## 4. 实验设计与结果

- 基础模型 WanS2V 14B；AVSpeech 40 万个 >10s 样本；训练 4,000 steps、8×H100。评测含 100 个约 10s 样本和 15 个 >5min 样本，720×400。
- 短视频：DynaForcing ASE/IQA 3.55/4.58、Sync-C 7.68、ExpVar 2.02、Dyn-Deg 0.73、45.2 FPS；LiveAvatar 对应 3.44/4.51、7.03、0.69、0.31、45.2 FPS。
- 长视频：ExpVar 1.93、Dyn-Deg 0.68；LiveAvatar 降到 0.57、0.28，说明方法抑制长期 KV 累积的静态化。
- 消融：移除 Hybrid Forcing，ExpVar 2.02→1.18、Sync-C 7.68→6.78，是最大退化；`p_data=1.0` 虽使 ExpVar 2.10，却使 ASE 3.42、Dino-S 0.93，显示 train-test mismatch。
- 训练效率：图剪枝+replay 由 7,111 降至 667 GPU·h（10.7×），质量指标差异 ≤0.02；代价是每 step 约 1.5× wall time。

## 5. 局限性与未来展望

- reward 依赖预训练 SyncNet 与 3DMM，其偏差可能被 student 利用；Sync-C/ExpVar 又直接进入训练奖励，需依赖未优化的 Dyn-Deg 和用户研究交叉验证。
- 结论集中在 audio-driven avatar，尚未系统验证通用 text-to-video 或其他 streaming generative tasks。
- 仍需 14B teacher 与 8×H100，所谓压缩主要是推理步数/训练显存而非端侧小模型。
- replay 带来约 1.5× 单步时间；detach 跨块梯度的普适安全性尚未证明。

## 6. 学术启发

蒸馏失败不一定表现为画质或静态指标下降，而可能是输出分布某个维度的“安静坍缩”。对于 autoregressive/self-conditioning student，应同时检查 teacher-student 目标的 mode preference 与历史反馈环。DynaForcing 的三层干预框架——数据起点、损失权重、条件信息——可迁移到其他需要长期动态一致性的蒸馏任务。

