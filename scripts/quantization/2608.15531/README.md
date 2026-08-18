# 2608.15531 FlashQuant Qwen3-0.6B 数值复现

脚本把真实 Qwen3-0.6B `up_proj` 分成 4-bit affine dense 路径和高精度稀疏异常值路径，验证两路共享输入并在同一输出累加的数值等价性。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --outlier-fraction 0.01
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method flash
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** W4 dense + 高精度 sparse 的数值分解与合并一致；论文核心是 CUDA 的 shared sparse-dense tiling、Tile-COO、warp 调度与片上累加，本机无 CUDA，未复现其 kernel 或速度。
- **修复：** 删除论文无依据的“每行均值 6 倍”阈值，改为显式异常值比例；W4 从对称量化修正为论文给出的 affine scale/zero-point。top-1% 是工程输入，不冒充论文 SpQR 阈值配置。
- **代表层结果：** 128×512 真权重，异常值密度 `0.009766`，输出 MSE `0.0035038129`，融合等价断言通过。
- **整模烟测：** 196 个 Linear、440,401,920 个参数完成 W4+1% 高精度异常值替换；前向有限，logits MSE `0.74375856`，生成 token `more`，耗时 `2.446s`。
- 环境同上：Apple ARM64 CPU，无 CUDA/MPS。
- **真实 Qwen3-0.6B：已跑通（整模数值路径）；FlashQuant CUDA 内核：未跑通。**
