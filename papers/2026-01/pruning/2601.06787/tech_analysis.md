# 技术深度分析：Garbage Attention in Large Language Models: BOS Sink Heads and Sink-aware Pruning (arXiv:2601.06787)

> **论文**: Garbage Attention in Large Language Models: BOS Sink Heads and Sink-aware Pruning
> **作者**: Jaewon Sok, Jewon Yeom, Seonghyeon Park 等
> **arXiv**: https://arxiv.org/abs/2601.06787 ｜ 提交: 2026-01-11 ｜ 分类: cs.CL

---

## 一、核心速览

### 研究主题

为 LLM 的层间冗余差异提供机制性解释：BOS sink 现象是高 BOS 沉没分数注意力头功能冗余的关键驱动，并据此提出 sink 感知剪枝。

### 一句话总结

高 BOS sink 分数的头（尤其在深层）对预测性能贡献很小，实为多余注意力权重的"垃圾场"；按此剪枝在 Gemma-3、Llama-3.1、Qwen3 上比基于权重或激活的准则更可靠地识别冗余组件，同时保持接近原模型的性能。

---

## 二、研究背景与动机

LLM 存在大量冗余已是共识，但"为何某些组件（尤其高层）更冗余"一直缺乏系统解释。attention sink（大量注意力质量沉积在 BOS token）此前被视为数值稳定现象，本文将其重新解读为功能冗余的标记——不干活把头把注意力"倒"在 BOS 上。

---

## 三、核心方法与创新点

- **冗余的机制性解释**：BOS sink 分数与功能冗余强相关，为既往结构性冗余的观察提供功能解释。
- **sink 感知剪枝**：移除高 BOS sink 头的简单策略。
- **跨模型验证**：Gemma-3、Llama-3.1、Qwen3 三族模型上优于权重/激活基准则。

---

## 四、实验设计与结果

在 Gemma-3、Llama-3.1、Qwen3 上实验：sink 感知剪枝比基于权重或激活的准则更可靠地识别冗余 Transformer 组件，剪枝后性能保持接近原模型（摘要未给出具体剪枝率与精度数字）。

---

## 五、局限性与未来展望

局限：BOS sink 与冗余的相关性在注意力 sink 被有意训练的模型（如 sink token 设计）上可能失效；头级剪枝粒度较粗；与 KV cache 压缩的交互（sink token 本就占用 KV）未讨论。未来方向：sink 分数与量化敏感度的联合分析、细粒度（维度级）sink 剪枝、训练期 sink 正则化。

---

## 六、学术启发

- **从"现象"到"剪枝信号"**：attention sink 这一广为人知的现象被转化为可操作的重要性准则——压缩研究应深挖模型已知现象的功能含义。
- **机制可解释性指导压缩**是 2026 年的明显趋势（与 DART 知识神经元剪枝等呼应）。

---

*分析时间: 2026-01 月度回填 ｜ 分析人: AI Assistant*
