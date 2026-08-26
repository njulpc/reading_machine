# 2608.24173 SandwichQuant 复现

按 [SandwichQuant（arXiv:2608.24173）](https://arxiv.org/abs/2608.24173) Algorithm 1，在 Qwen3-0.6B 全部 196 个 Linear 上建立 W3A16、group-size 128 的 RTN 图，只训练 normalization-affine 参数。pre 阶段后完整丢弃探测图，重新从 dense checkpoint 加载，只迁移 `Φ_pre`，再从头 PTQ 并做 post 阶段；目标为下一词 CE 与全词表 teacher KD 等权和。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-27）

- 算法一致性：**部分一致**。两侧 affine、immutable dense snapshot、只迁移 affine、重新 PTQ、冻结量化图、CE+KD 与 W3A16 g128 已对齐。论文使用 Qwen3-8B、128 条 C4×2048 校准、每阶段 200 步×256 token，并覆盖 GPTQ/AWQ/GPTAQ/ResComp 和 W2A4KV4；本 CPU smoke 仅用固定 32-token 文本、每阶段 1 步和 RTN。
- 修复：原实现只优化首层 RMSNorm→q_proj 的随机高斯局部 MSE，并在同一权重图上连续做 pre/post，违反 Algorithm 1 的“恢复 S0、只迁移 affine、从头重建 PTQ”。现已改为全模型 teacher/task objective 和真正的两次独立 PTQ。
- 环境：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，safetensors 0.7.0；Apple arm64 CPU，CUDA/MPS 不可用。
- 结果：退出码 0；两次均量化 196 层/440,401,920 元素，仅 65,536 个 affine 参数可训练。pre loss `10.00121689`，post loss `9.60256672`；整模 logits MSE 从 `4.93351507` 降至 `4.69099665`，闭合 `4.9157%`，量化后前向与一步生成成功，总耗时 1.990 s。
- **真实 Qwen3-0.6B：已跑通**（全模型 W3 RTN、两阶段 affine、前向与生成）；论文 200+200 步、C4 校准、Qwen3-8B/多后端、困惑度与六任务评测以及量化权重导出未跑通。
