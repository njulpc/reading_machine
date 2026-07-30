# Paper: 2607.27042 — GPTQ-2D: Cubic-Time Two-Sided Adaptive Rounding

See `demo.py` for a standalone, runnable implementation.

Run: `python3 demo.py`

## 复现内容
- 经典单边 GPTQ（Babai 最近平面舍入 + 三角反馈传播）；
- 论文的双边扩展：左/右基矩阵同时作用下的 GPTQ-2D，按反对角线顺序舍入，同对角线元素并行；
- 正确性验证：GPTQ-2D 输出与暴力 Kronecker 向量化 Babai（O(m⁴)）逐元素一致；
- 以 Qwen3-0.6B 为目标模型的权重量化演示。

## 验证方式
- 若本机有缓存的 Qwen/Qwen3-0.6B，则加载真实模型，对其线性层做双边量化并比较 logits 余弦相似度；
- 否则使用与 Qwen3-0.6B 相同维度的 mock 两层的 Transformer 验证全部代码路径；
- 算法一致性在小矩阵上对暴力算法做逐元素断言（不依赖模型）。
