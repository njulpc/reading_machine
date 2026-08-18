# 2608.16756 BinRVR / DAB-Conv Qwen3-0.6B 数值迁移

脚本把 DAB-Conv 迁移到 Qwen `gate_proj`：权重和激活均为 1-bit；加入可学习 channel bias，按每通道 mean/absolute-mean/std 拼接后用 stride-3 Conv1D+Sigmoid 预测 activation scale，并与 abs-mean 基线比较。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --steps 100
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method binrvr
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** weight L1 scale、可学习 activation bias、三统计量、Conv1D+Sigmoid 与 1-bit 符号路径符合论文；Qwen Linear 不具备深度卷积、空间残差或 RPReLU 的形状语义。
- **修复：** 原实现用逐通道 MLP 且缺失论文的 bias/Conv1D/Sigmoid；现按 Eq.12-14 修正可迁移部分。
- **代表层结果：** abs-mean baseline MSE `0.28092414`；100 步 DAB 迁移 MSE `0.31369084`，没有取得正收益。该负结果如实保留，说明视觉卷积机制不能直接外推到 Qwen Linear。
- **整模诊断：** 全模型 binary weight + abs-mean activation 退化烟测替换 196 个 Linear/440,401,920 参数；前向有限，logits MSE `32.984409`，生成 token `бол`，`1.644s`。该路径不包含已训练 DAB。
- 缺失：RAW 视频、BIIM、时序 shift/window、grouped strip convolution、RPReLU、残差训练和真实二值 kernel。
- **真实 Qwen3-0.6B：未跑通（代表层 DAB 迁移无收益；整模仅退化烟测）。**
