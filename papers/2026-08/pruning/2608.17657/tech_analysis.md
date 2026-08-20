# Denoised Variance-Based Pruning with Optimal Brain Bias Compensation

- arXiv: [2608.17657](https://arxiv.org/abs/2608.17657)
- 提交日期（v1）：2026-08-18
- 作者：Geon Tack Lee, Jaegul Choo, Kang Eun Jeon
- 分类：cs.CV
- 证据边界：基于 arXiv 摘要与 25 页 v1 PDF；主结果为 ImageNet-1K 上 training-free 结构剪枝，Qwen2.5-1.5B 仅出现在附录扩展实验。

## 1. 核心速览

**研究主题：** 用 Marchenko–Pastur 谱去噪改进 activation variance 排序，并把均值偏移补偿纳入 OBC，闭式更新剪枝后的剩余权重。

**一句话总结：** DVBP+OB²C 在 50% MLP 结构剪枝时显著优于 VBP；Swin-S Top-1 由 69.91% 提升到 77.24%，ConvNeXt-T 由 15.44% 提升到 44.90%，无需微调。

## 2. 研究背景与动机

非结构稀疏很难在通用硬件上获得真实加速；结构剪枝能直接删除 neuron/channel，却容易造成性能崩溃。VBP 发现低方差激活近似常量，可把其均值贡献吸收到 bias 中，但有限校准样本导致 covariance 谱含噪，且仅改 bias 无法补偿完整线性重构误差。

## 3. 核心方法与创新点

1. **在线中心协方差。** 用批量版 Chan/Pébay 更新累计激活均值和 covariance，不保存全部激活；默认校准 8,192 个 ImageNet 样本。
2. **MP 谱去噪。** 拟合 Marchenko–Pastur 噪声区间，仅保留高于 `λ+` 的 signal eigenvectors，重构去噪 covariance，再以对角方差形成 neuron score。
3. **OB²C。** 在 OBC 的层输出重构中显式优化 bias。消去最优 bias 后，Hessian 精确化为中心化激活 covariance 的 `2NC`，同一统计量同时服务选择和补偿。
4. **闭式多权重恢复。** 对被删通道集合 `P`，用 `C^{-1}` 更新其余权重并加入 mean-shift bias；无反向传播和 retraining。

## 4. 实验设计与结果

- 模型：DeiT、Swin、ConvNeXt Tiny/Small/Base，ImageNet-1K；单 RTX 3090。主实验 50% MLP 结构剪枝。
- Swin-S：完整模型 83.32%，VBP 69.91%，本文 77.24%；DeiT-B 为 81.98%→68.92%→75.85%。
- ConvNeXt：Tiny/Small/Base 的本文结果为 44.90/50.01/70.76%，相对 VBP 绝对提升 29.46/21.88/14.64pp。
- 成本：峰值显存低于 10 GB；Swin-B 处理 66.92 s、8.11 GB，约为 VBP 时间的 2×，仍无需训练。
- 消融：去噪多数只贡献约 1–2pp，主要提升来自 OB²C（例如 DeiT-T 由 42.90% 到 56.40%）；高剪枝率时 MP 去噪价值增大。
- 附录 Qwen2.5-1.5B：50% MLP pruning 时 WikiText-2 PPL，LLM-Pruner 9557.71、VBP 28.35、本文 16.66，full 为 8.19。

## 5. 局限性与未来展望

- covariance 的 `d×d` 存储和求逆随通道数二次/三次增长；blockwise 实现虽控制显存，对超大 LLM 仍有代价。
- 校准分布敏感：Swin-S 需约 32k 样本才趋于收敛，默认 8,192 并不总是充分。
- 主要比较集中于视觉 MLP，attention 与 LLM 结果只在附录；尚缺端到端真实延迟和能耗。
- MP 假设与实际深层激活并非严格同分布，谱阈值是统计近似；不同数据域需重新验证。

## 6. 学术启发

均值中心化不是一个实现细节：加入可优化 bias 后，OBC 的二阶对象从未中心化二阶矩转为 covariance，使“低方差可删”与“剩余权重如何补偿”落在同一数学对象上。它提示后续剪枝设计应让选择准则和恢复目标共享统计量，而非先用启发式删、再独立微调。

