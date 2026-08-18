# 2608.15475 Bit-Flip Attack / Qwen3-0.6B 数值复现

`demo.py` 对真实 Qwen3-0.6B 第一层 `q_proj` 做 per-output-channel symmetric INT8，并按论文的固定方向目标计算每个 two's-complement bit 的正向收益；每个标量权重只保留一个最佳 bit，再选 top-k。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --flips 5
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method bitflip
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** INT8 公式、two's-complement 翻转、固定方向梯度收益和“每权重至多一位”已与论文一致；Qwen 不是 VLA，没有动作解码头、`<=6` 帧真实机器人校准、Rowhammer 或闭环评估。
- **修复：** 码值范围由错误的 `[-127,127]` 改为论文 `[-128,127]`；去掉绝对值排名和同一权重多位同时入选；校准样本从 32 改为 6。
- **代表层结果：** 64×256 真权重，INT8 MSE `1.5867241e-05`；5 个唯一权重翻转后 MSE `0.031024294`，方向均值位移 `0.025076203`。
- **整模烟测：** 196 个 Linear、440,401,920 个参数替换为 INT8 反量化值；前向有限，logits MSE `0.017280446`，生成 token `more`，耗时 `2.776s`。
- 环境：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0、Apple ARM64 CPU；CUDA/MPS 均不可用。
- **真实 Qwen3-0.6B：已跑通（INT8 整模数值路径）；论文 VLA 攻击：未跑通。**
