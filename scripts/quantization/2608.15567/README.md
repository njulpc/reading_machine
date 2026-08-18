# 2608.15567 SchurQuant Qwen3-0.6B 核心复现

脚本在 `q_proj` 的 32×256 真权重上运行 2-bit、group-size=128 的 SchurOpt：由 96 个校准激活形成二次统计，显式计算 Schur 的曲率 `S` 与线性项 `T`，并交替执行离散 zero-point 枚举、闭式 scale 重拟合和整数码坐标下降。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --group-size 128
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method schur
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** 当前代表层实现覆盖论文 SchurOpt 的 `S/T`、每行 scale/zero-point 更新和坐标下降；未覆盖完整 SchurQuant 的 quantized-prefix teacher、reference anchor、residual-add target、`rho=8` token weighting 和逐层前缀传播。
- **修复：** 原实现只用误差二次型，遗漏 `T` 和已量化前缀影响；zero-point 连续裁剪也不符合论文枚举。现已补齐，并将 group size 改为论文默认 128。
- **代表层结果：** affine 初始化输出 MSE `0.059796643`，SchurOpt 后 `0.010652055`。
- **整模诊断：** 为确认加载/替换/前向链路，工程退化为全模型 2-bit affine：196 个 Linear、440,401,920 参数，前向有限，logits MSE `29.856966`，生成 token `plash`，`1.657s`。该结果不是 SchurQuant。
- 环境同上：CPU-only；完整逐层 SchurQuant 的计算与教师缓存路径尚未实现。
- **真实 Qwen3-0.6B：未跑通（仅代表层 SchurOpt；整模为 affine 退化烟测）。**
