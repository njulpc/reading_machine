# Paper: 2603.01776 — FreeAct (Freeing Activations for LLM Quantization)

复现内容：
1. 激活秩亏性质：验证激活矩阵低秩 → 激活变换可超越"逆矩阵"约束
2. token 类型特异性激活变换：为视觉/文本（或掩码/非掩码）token 分配各自的激活变换矩阵
3. 权重侧统一静态变换，端到端量化 MSE 对比（静态一对一 vs FreeAct 动态）

目标模型：Qwen3-0.6B 同构 mock（模拟多模态两类 token 的异质激活）。

## 验证方式（如实说明）

- 未下载真实权重，用合成的异质双分布激活（模拟视觉/文本 token）验证。
- 验证项：激活矩阵有效秩 ≪ 维度（秩亏）；FreeAct 的逐类型变换较统一变换
  显著降低量化后输出 MSE；权重侧仅需一套变换（存储开销不变）。

## 运行

```bash
python3 demo.py
```
