# 2608.24469 低秩三值适配复现

从 Qwen3-0.6B 首个 `q_proj` 截取真实 128×128 tile，验证 [Low-Rank Ternary Adaptation（arXiv:2608.24469）](https://arxiv.org/abs/2608.24469) 的核心代数：把离散乘法 mask 表示为两个小三值矩阵的 **Kronecker 积** `A ⊗ B`，用 abs-mean threshold 与 STE 训练 real-valued proxies，最后与三值基座逐元素合并，确保仍严格闭合于 `{-1,0,1}`。论文未绑定 threshold multiplier，脚本的 0.7 是明确的工程选择。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-27）

- 算法一致性：**部分一致**。Kronecker factor shape、ternary proxy/STE、逐元素 keep/zero/flip 与无反量化 merge 已对齐；Qwen3 原模型不是论文的 SpinQuant ternary backbone，脚本的 abs-mean 基座仅为工程迁移，也没有对所有 attention/FFN 层进行一轮真实下游 fine-tuning。
- 修复：原代码把 `A ⊗ B` 错写成普通低秩矩阵乘积 `A @ Bᵀ`，并以所谓 `rank=4` 描述；这会改变参数数、mask 结构与 rank 公式。现使用 `(16×16) ⊗ (8×8)` 精确生成 128×128 mask，仅 320 个 proxy 参数。
- 环境：Python 3.9.6，PyTorch 2.8.0，safetensors 0.7.0；Apple arm64 CPU，CUDA/MPS 不可用。
- 结果：退出码 0，墙钟 0.98 s；真实权重 tile 的目标 mask MSE 从 `0.731445` 降到 `0.000000`，合并权重唯一值严格为 `[-1,0,1]`，mask 实际 rank 128；另有 4×4 Kronecker 小张量闭包测试。
- **真实 Qwen3-0.6B：未跑通量化**（仅真实 q_proj tile 的核心适配与 merge 路径）；全 196 层 ternarization/adapter fine-tuning、下游任务、SpinQuant 800 条校准、A40 kernel 与完整模型生成未跑通。
