# 2608.15636 SpecVLA Qwen3-0.6B 数值迁移

脚本构造两个相邻时刻特征，计算 `Delta X_i=X_i-X_{i-1}`，按每个固定 block 的绝对值和，以两个阈值分配 0/4/8-bit，再将量化残差输出累加到上一时刻输出。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --block 64
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method specvla
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** 0/4/8-bit 特征残差分块与上一时刻累加符合论文；Qwen 没有视觉帧、动作头、状态预测、sVLA 或异构 speculative dataflow。
- **修复：** 原代码量化的是权重 block，并用权重量化误差选 4/8-bit，且没有 0-bit；这与论文 `Delta X` 方法不一致，现已重写。
- **代表层结果：** 0/4/8-bit block 比例 `35.94%/58.59%/5.47%`，差分累加输出 MSE `0.00044923485`。
- **整模烟测：** 对 196 个 Transformer Linear 安装状态化残差激活钩子，以不同等长 prompt 做相邻状态；前向有限，logits MSE `0.627909`，生成 token `more`，`1.610s`。
- 环境同上：CPU-only；阈值按论文平均比例构造，是工程替代而非论文任务校准阈值。
- **真实 Qwen3-0.6B：已跑通（整模差分量化迁移路径）；论文 SpecVLA：未跑通。**
