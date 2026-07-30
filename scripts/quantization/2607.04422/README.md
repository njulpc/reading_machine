# Paper: 2607.04422 — Full-Stack FP4: Stable LLM Pretraining

Run: `python3 demo.py`

## 复现内容
- 线性投影：LoRA-SVD 轻量分解（低秩结构高精度 + 残差 NVFP4）打破直接量化误差上限；
- 优化器：AdamW 二阶矩 log 域变换的 NVFP4 存储，保护低精度分母；
- 注意力：统一张量复用保持前向-反向量化一致性（与 P-Reordering/PNQ 同构验证）；
- 以 Qwen3-0.6B 为目标模型的投影量化演示。

## 验证方式
- [1]–[3] 在合成数据上逐项对比（直接 NVFP4 vs LoRA-SVD；直接 vs 变换二阶矩；对齐 vs 失配行和）；
- [4] 真实 Qwen/Qwen3-0.6B 前 2 个线性层 LoRA-SVD FP4 量化并比较 logits 余弦相似度（无模型时以同维度 mock 验证）。
