# Reservoir of Importance: Learning Semi-Structured Sparsity with Differentiable Subset Sampling

> arXiv: [2608.23048](https://arxiv.org/abs/2608.23048) · v1: 2026-08-24 · 主分类: cs.LG
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：可扩展 N:M 半结构化 LLM 剪枝。
**一句话总结**：RoI 用 O(M) compact logits 和无放回 differentiable subset sampling 学习 N:M mask，避免枚举组合模式；在 Qwen2.5 0.5B–7B 上以 1.5–8.75× 更少可训练 mask 参数获得有竞争力的性能。

## 2. 研究背景与动机

N:M sparsity 对硬件友好，但常见 learnable-mask 方法为每个可行 pattern 建完整 categorical distribution，组合数随 M 急增；在大模型或激进稀疏率下，mask 参数和优化内存本身成为瓶颈。

## 3. 核心方法与创新点

- compact-logit parameterization 把组合 mask 的表示降到 O(M)。
- differentiable sampling without replacement 确保一个 M-block 内恰选 N 个位置。
- 训练阶段学习 importance reservoir，部署阶段输出标准 N:M pattern。
- 目标是同时保持硬件兼容、学习稳定性和大模型可扩展性。

## 4. 实验设计与结果

覆盖 Qwen2.5 0.5B、若干中间规模至 7B，并比较多种 N:M 强度。RoI 的 mask 可训练参数比强基线少 1.5–8.75×，内存更低，在更激进 sparsity 下仍保持竞争性能和稳定性。该倍率是 mask-learning overhead，不等同模型参数压缩倍率。

## 5. 局限性与未来展望

摘要未给出真实稀疏 kernel 端到端 latency；硬件收益依赖后端是否支持对应 N:M。mask 学习仍需训练数据与额外阶段。未来应联合 kernel cost model，并测试 30B+ MoE 与动态稀疏。

## 6. 学术启发

剪枝算法自身的优化状态也需要“被压缩”。评价 learnable sparsity 时，应把 mask 参数、训练峰值内存和部署 kernel 支持列为一等指标。
