# Sigmoid Attention as a Better Substrate for Learned KV Cache Eviction

> arXiv: [2608.23296](https://arxiv.org/abs/2608.23296) · v1: 2026-08-24 · 主分类: cs.LG
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：attention normalization 对 learned hard KV eviction 的影响。
**一句话总结**：在控制 attention、gate、position encoding 的 2×2×2 实验中，dense 性能较差的 sigmoid attention 反而能让训练期 soft gate 更稳地迁移到物理删除；其 learned hard eviction 相对 no-eviction PPL 变化可忽略，并优于匹配协议的 H₂O/KeyDiff 实现。

## 2. 研究背景与动机

训练时 differentiable gate 只是衰减 token，部署要节省内存却必须真正删除 KV，形成 soft-to-hard mismatch。现有工作多优化 gate，而较少问 softmax normalization 是否使硬删除天然困难。

## 3. 核心方法与创新点

- 在 GPT-2-scale/OpenWebText 下做 attention type × learned gating × positional encoding 的全因子控制。
- 匹配 dense backbone 和 live-cache protocol，避免不同模型容量混杂。
- 比较 soft gate、hard physical eviction 与 post-hoc H₂O/KeyDiff。
- 结论是 attention substrate 会改变 gate 的可离散化，而非 sigmoid dense LM 更强。

## 4. 实验设计与结果

2×2×2 设计显示：sigmoid dense reference 较差，但 learned sigmoid gate 真正删除 KV 后，相对自身 no-eviction reference 的 PPL 变化近乎可忽略；在匹配 live-cache 设置下低于作者实现的 H₂O 与 KeyDiff。softmax gate 并未稳定超过这些 post-hoc 方法。

## 5. 局限性与未来展望

仅 GPT-2-scale 和 OpenWebText，未证明大规模 pretrained Transformer 可低成本改成 sigmoid；“相对自身”保持不等于绝对 PPL 最优。未来需从 softmax checkpoint 转换、长上下文任务和真实 KV kernel 验证。

## 6. 学术启发

压缩可训练性由基础算子决定。若最终需要离散删除，训练目标和 normalization 应从一开始就为 hard decision 设计，而不是在 softmax 模型上事后补 gate。
