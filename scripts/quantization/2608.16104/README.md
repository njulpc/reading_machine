# 2608.16104 Nexus Qwen3-0.6B 数值迁移

Qwen3-0.6B 是 dense 模型。脚本将样本路由到 8 个伪专家和对应 `up_proj` 行分区，执行 symmetric INT4 weight 与 99.9% clipping 的 asymmetric 4-bit activation fake-QAT，并为每个专家独立学习 scale/zero-point。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --experts 8 --qat-steps 5
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method nexus
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** 权重 INT4、激活非对称 4-bit、99.9% clipping、per-expert scale/zero-point 与 STE 路径一致；论文未公开 FP4 指数编码细节，因此这里明确采用 16-level affine 工程替代。
- **修复：** 原代码使用对称固定 E2M1-like grid、所有伪专家共享完全相同 scale、且没有 zero-point；现改为真实路由子样本和独立可学习参数。
- **代表层结果：** 8 专家、5 步 QAT，输出 MSE `0.0066576889`；scale 为 `0.383077..0.434171`，zero-point 为 `7.23727..8.17437`。
- **整模诊断：** 全模型 W4 + 动态 asymmetric-A4 钩子替换 196 个 Linear/440,401,920 参数；前向有限，logits MSE `21.092062`，生成 token `rie`，`1.752s`。这不是 per-expert Nexus。
- 缺失：MoE top-2 router、Gated DeltaNet、FP16 router/state、LAION QAT、图像生成和 A100/RTX5090 kernel。
- **真实 Qwen3-0.6B：未跑通（代表层 per-expert 机制通过；整模无 MoE）。**
