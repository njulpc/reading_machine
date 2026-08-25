# DiaRelay: Relaying Dialogue Context with a Constant-Size Memory for Emotion Recognition in Conversation

> arXiv: [2608.22745](https://arxiv.org/abs/2608.22745) · v1: 2026-08-24 · 主分类: cs.CL
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：对话情绪识别的常量大小状态压缩。
**一句话总结**：DiaRelay 在 LoRA 上加入 Selective Relay Memory Transition 与 Dual-axis Read，把远距情绪证据递推进有界状态；仅增加 7.1M 可训练参数，在 MELD 达到 SOTA weighted F1/accuracy，并避免反复编码完整历史。

## 2. 研究背景与动机

短窗口漏掉远距情绪线索，长窗口则反复编码重叠 utterance、扩大显存与延迟，还会引入无关内容。普通 LoRA 是固定低秩映射，不维护随对话演化的状态。

## 3. 核心方法与创新点

- Selective Relay Memory Transition 逐轮聚合有用证据并限制 memory 尺寸。
- 早期线索离开局部窗口后仍通过 relay state 影响后续预测。
- Dual-axis Read 用 memory 动态调制低秩变换，使 adapter 依赖当前上下文。
- 无需测试时梯度更新，也不扩展 backbone context length。

## 4. 实验设计与结果

MELD 上达到论文报告的 SOTA weighted F1 与 accuracy，IEMOCAP 上有竞争力；额外可训练参数为 7.1M。全文比较显示收益来自显式 relay 状态而非单纯加大 LoRA，但摘要未给出统一内存压缩倍率。

## 5. 局限性与未来展望

只在 ERC 场景验证，常量 memory 是否能容纳超长、多主题对话仍未知；递推状态一旦污染可能持续传播。未来应加入可解释写入、状态重置和更长对话压力测试。

## 6. 学术启发

上下文压缩可以学习一个任务状态，而不是选择原始 token。常量状态适合在线任务，但必须评价信息丢失、错误累积与状态可恢复性。
