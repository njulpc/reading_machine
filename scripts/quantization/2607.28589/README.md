# Paper: arXiv:2607.28589 — MixFrag: Fragility-Guided Mixed-Precision Post-Training Quantization

> **MixFrag** is a fragility-guided mixed-precision PTQ framework. It first estimates component-level quantization fragility via isolated quantization and KL divergence, then formulates bit allocation as a Multiple-Choice Knapsack Problem (MCKP) for adaptive precision assignment under a bit budget.

This directory contains a PyTorch reproduction / adaptation of MixFrag for the **Qwen3-0.6B** language model.

---

## 📄 论文信息 / Paper Info

| 项目 | 内容 |
|------|------|
| **标题** | MixFrag: Fragility-Guided Mixed-Precision Post-Training Quantization for Vision Transformers |
| **arXiv** | [arXiv:2607.28589](https://arxiv.org/abs/2607.28589) |
| **作者** | Md Mehrab Hossain Opi et al. |
| **核心方法** | 1) Isolated Quantization + KL-based Fragility Estimation<br>2) MCKP (Multiple-Choice Knapsack Problem) Bit Allocation<br>3) Mixed-Precision Assignment |
| **适配目标** | Qwen3-0.6B (Transformer-based LLM) |

---

## 🗂️ 文件结构

```
2607.28589/
├── demo.py      # 完整的 MixFrag 复现代码（含 Mock 模型 + 真实模型适配）
└── README.md    # 本文档
```

---

## 🚀 运行方法

### 环境依赖

```bash
# 必需
pip install torch>=2.0

# 可选（如需加载真实 Qwen3-0.6B 模型）
pip install transformers>=4.40 accelerate
```

### 运行演示

```bash
cd reading_machine/scripts/quantization/2607.28589
python3 demo.py
```

运行后，脚本将依次执行：

1. **PART 1 — Mock 模型完整流程**：构建一个与 Qwen3-0.6B 架构一致的模拟 Transformer，执行完整的 MixFrag 三阶段流程（脆弱性估计 → MCKP 求解 → 混合精度分配），并输出量化前后的 logits 余弦相似度。
2. **PART 2 — 真实 Qwen3-0.6B（可选）**：若网络畅通且已安装 `transformers`，自动下载并加载真实模型，重复上述流程。
3. **PART 3 — MCKP 求解器验证**：在一个人工构造的小型 MCKP 实例上，验证 DP 与 Greedy 两种求解器的正确性。

---

## 🔬 复现内容

### Stage 1: Fragility Estimation（脆弱性估计）

对模型的每一个 `nn.Linear` 层执行 **孤立量化 (Isolated Quantization)**：

- 仅对当前层的权重进行量化（如 INT8 / INT4 / INT3），其余所有层保持全精度 (FP16)。
- 使用校准数据 (calibration data) 执行一次前向传播。
- 计算全精度输出与孤立量化输出的 **KL 散度** 作为该层的“量化脆弱性分数 (Fragility Score)”。
- KL 散度越大 → 该层对量化越敏感 → 应分配更高精度。

实现细节：
- 使用均匀对称量化 (Uniform Symmetric Quantization)，支持 per-channel / per-tensor scaling。
- KL 计算基于 logits 的 softmax 分布：`KL(P||Q) = Σ P(v)·log(P(v)/Q(v))`。

### Stage 2: Bit Allocation as MCKP（多选背包问题）

将比特分配建模为 **Multiple-Choice Knapsack Problem**：

- **物品组**：每个可量化层为一组。
- **组内选项**：该层可选的多种精度（如 FP16 / INT8 / INT4 / INT3）。
- **成本 (cost)**：选项的比特宽度 × 该层参数量。
- **收益 (profit)**：基准脆弱性 − 当前选项脆弱性（即量化带来的脆弱性降低量）。
- **约束**：总成本 ≤ 比特预算（目标平均比特 × 总参数量）。
- **目标**：最大化总收益 = 最小化总脆弱性。

提供了两种求解器：

| 求解器 | 适用场景 | 时间复杂度 |
|--------|---------|-----------|
| `dp` | 小型模型、精确求解 | O(N × B) — B 为离散化后的预算上限 |
| `greedy`（默认） | 大型 LLM、可扩展启发式 | O(N × C × log(N×C)) — 每次选最优边际收益比升级 |

### Stage 3: Mixed-Precision Assignment（混合精度分配）

根据 MCKP 求解结果，逐层应用对应比特宽度的量化：

- 对分配了低比特（如 INT4/INT3）的层，执行均匀对称量化并替换权重。
- 对分配了 FP16 的层，保持原样。
- 最终得到一个**异构精度**的量化模型。

---

## ⚙️ 配置参数

在 `demo.py` 中可以调整以下参数：

```python
# 候选比特宽度（每个层可选的精度配置）
DEFAULT_BIT_CANDIDATES = [
    (16, "FP16 / BF16"),   # 全精度，零量化损失
    (8,  "INT8"),          # 8-bit 均匀量化
    (4,  "INT4"),          # 4-bit 均匀量化
    (3,  "INT3"),          # 3-bit 均匀量化（激进压缩）
]

# MCKP 目标平均比特（预算控制）
target_avg_bits = 4.0   # 例如：4.0 表示所有参数平均占用 4 bit

# 求解器选择
solver = "greedy"       # "dp" 或 "greedy"
```

---

## 📊 预期输出示例

```
==============================================================================
 Paper arXiv:2607.28589 — MixFrag: Fragility-Guided Mixed-Precision PTQ
 Adapted for LLM (Qwen3-0.6B)
==============================================================================

------------------------------------------------------------------------------
 [PART 1] Synthetic Mock-Model Demonstration
------------------------------------------------------------------------------

[Info] Built mock Qwen3-0.6B with 196,704,000 parameters.

[MixFrag] Found 196 quantizable nn.Linear layers.
[MixFrag] No calibration data provided; using synthetic random inputs.

[Stage 1] Fragility Estimation (Isolated Quantization + KL Divergence)

[Fragility Table] (showing first 5 layers)
  embed_tokens
      16b -> KL=0.000000
       8b -> KL=0.001234
       4b -> KL=0.005678
       3b -> KL=0.012345
  layers.0.q_proj
      ...

[Stage 2] Bit Allocation via MCKP (target_avg_bits=4.0)
[MixFrag] Total parameters: 196,704,000
[MixFrag] Target average bits: 4.00
...
[MixFrag] Optimization complete: profit=..., used_budget=..., avg_bits=3.98

==============================================================================
 MixFrag Mixed-Precision Assignment Summary
==============================================================================
  16-bit layers:  28
   8-bit layers:  42
   4-bit layers:  84
   3-bit layers:  42
==============================================================================

[Validation] Logit similarity after mixed-precision quantization
  Cosine similarity (FP vs MixFrag): 0.9876
  MSE: 0.0023
```

---

## ⚠️ 已知限制

1. **Uniform Symmetric Quantization**：本复现使用简单的均匀对称量化（per-channel / per-tensor），而非论文中可能使用的更复杂的量化方案（如 LSQ、GPTQ 等）。这足以展示 MixFrag 的核心算法流程，但实际部署精度可能低于论文报告。

2. **校准数据**：论文使用小型校准集（通常 32–1024 个样本）估计脆弱性。本代码支持真实 token 输入，但默认使用合成随机输入进行演示。使用真实校准数据（如 WikiText-2 子集）可得到更准确的 fragility score。

3. **真实模型加载**：若网络受限或本地未缓存模型，`transformers` 无法下载 Qwen3-0.6B 权重时，代码会自动降级为 **Mock 模型**演示，所有算法逻辑仍然完整可运行。

4. **MCKP 求解器**：
   - `dp` 求解器对大型模型（数十亿参数、数百层）可能内存爆炸，因为状态空间随预算离散粒度指数增长。
   - `greedy` 求解器是启发式的，不保证全局最优，但在实践中与 DP 结果接近（见 PART 3 的验证）。

5. **中间层 vs Logits KL**：论文在 ViT 上可能使用中间层输出的 KL。本代码默认使用最终 logits 的 KL（更适合 LLM），但可通过 `use_intermediate=True` 切换。

6. **Qwen3-0.6B 架构假设**：Mock 模型基于公开的 Qwen3-0.6B 配置参数（hidden_size=576, num_layers=28 等）构建，可能与实际实现存在细微差异（如 RoPE、SwiGLU 实现细节）。

---

## 📚 参考文献

```bibtex
@article{opi2026mixfrag,
  title={MixFrag: Fragility-Guided Mixed-Precision Post-Training Quantization for Vision Transformers},
  author={Opi, Md Mehrab Hossain and others},
  journal={arXiv preprint arXiv:2607.28589},
  year={2026}
}
```

---

## 📝 复现说明

| 检查项 | 状态 |
|--------|------|
| Fragility Estimation（孤立量化 + KL 散度） | ✅ 实现 |
| MCKP 建模（成本 = bits × params，收益 = 脆弱性降低） | ✅ 实现 |
| DP 精确求解器 | ✅ 实现 |
| Greedy 启发式求解器 | ✅ 实现 |
| 混合精度分配与应用 | ✅ 实现 |
| Qwen3-0.6B 适配（真实模型 + Mock 模型） | ✅ 实现 |
| 详细中文/英文注释 | ✅ 完成 |
| 无网络时完整可运行 | ✅ 支持（自动降级为 Mock 模型） |
