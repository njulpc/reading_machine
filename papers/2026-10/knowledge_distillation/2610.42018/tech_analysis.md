# Asynchronous Flow Map Language Models

- arXiv：[2610.42018](https://arxiv.org/abs/2610.42018)；[官方 HTML v1](https://arxiv.org/html/2610.42018v1)
- v1 实际提交：2026-10-30T16:51:40+00:00（UTC）；2026-10-31T00:51:40+08:00（Asia/Shanghai）。
- 官方分类（主分类在前）：Computation and Language (cs.CL)
- 压缩归类：knowledge_distillation。证据为官方摘要与上述全文方法、实验及相关附录；以下数字均为论文报告，非本机复现。

## 1. 核心速览

研究主题：knowledge_distillation / Asynchronous Flow Map Language Models。

一句话总结：aFMLM 把异步token生成次序蒸馏进流映射，使单次前向并行生成保留部分顺序推理能力。

## 2. 研究背景与动机

自回归与多步扩散可通过生成次序先解决容易token，再利用它们推理其他token。普通单步并行生成失去这一机制。本文压缩的是串行生成轨迹，研究如何把调度的作用转移到网络内部。

## 3. 核心方法与创新点

1. **异步状态**：每个token拥有时间tau_i，将token表示和时间一起作为ODE状态。scheduler给出各位置推进速度；区分预设路径与依赖当前预测的自适应路径。
2. **flow map自蒸馏**：预测两时刻之间的平均token速度及时间速度，用“两次短跳=一次长跳”的半群一致性构造stop-gradient目标。token分布用KL，时间速率用平方误差；对角边界由denoiser/scheduler监督。
3. **训练分支**：自适应路径需先训练teacher并生成联合状态；预设路径可直接采样interpolant并用数据监督，从头训练而不依赖外部teacher。推理N=1直接输出整个序列，无需运行scheduler。
4. **设置**：Sudoku约29M、8层、hidden512；TinyGSM约168M、12层、hidden768。AdamW、lr3e-4、BF16 mixed、EMA0.9999；课程初始rollout32步，每轮2000训练步。

## 4. 实验设计与结果

表1–4：Sudoku-Hard单步exact accuracy，普通FMLM4.9%，同步aFMLM6.4%，异步EB11.8%，top-K14.4%；Easy的top-K81.4%。GSM8K任务为TinyGSM代码生成迁移：单步EB11.4%，top-K10.5%，同步1.6%，AlphaDLM6.3%。这些绝对准确率仍低，不能把相对改善解释成通用高可靠推理。

Sudoku-Hard训练成本：learned schedule teacher1.7 GPU-h、蒸馏3.3h、合计5.0h；prescribed schedule无需teacher、训练3.2h。GSM蒸馏170k步、batch512；Sudoku10k步、batch256。一次网络调用不是权重缩小，也不等于与任意AR系统可直接按序列长度换算加速。

## 5. 局限性与未来展望

state-adaptive情况下scheduler-independent denoiser并不保证精确恢复数据分布，理论保证条件必须区分。实验集中在Sudoku与短数学代码，未证明大语言模型通用能力与开放文本质量。未测本地时延，也未运行训练。

## 6. 学术启发

压缩推理轨迹可保留生成顺序作为训练信号，而在部署时去掉调度器。验证时应同时看单步准确率、teacher成本和总训练成本，并设置同步同架构对照隔离“异步次序”的贡献。

评分（1–10）：精度效果6，压缩倍率/资源削减7，创新性9，可复现性7。

准确率6：单步相对增益大但绝对准确率低；压缩7：轨迹压到单调用但缺统一时延；创新9：联合时间状态与半群蒸馏；复现7：小模型设置充分，本轮未训练。

本轮为非量化论文精读，未执行论文训练或运行时基准；可复现性评分衡量公开方法的可操作程度，不表示本轮已复现。分析日期：2026-11-03。
