# Paper: 2603.27467 — TurboAngle (Near-Lossless KV Cache Compression via Uniform Angle Quantization)

复现内容：
1. Fast Walsh-Hadamard 域 + 随机对角旋转，使相邻元素对在单位圆上近似均匀分布
2. 角度均匀量化（每元素 3.28–3.67 角度比特）
3. 逐层 early-boost：按层敏感度独立配置 K/V 码本大小
4. 非对称范数量化（K 8-bit、V 4-bit 对数域）

目标模型：Qwen3-0.6B（mock KV cache，GQA: 14 头 / 2 KV 头）。

## 验证方式（如实说明）

- 未下载真实权重，用 mock KV cache（含真实感相关结构）验证。
- 验证项：旋转后角度分布接近均匀；角度量化-反量化重构 MSE；
  逐层 early-boost 在相同平均比特下比均匀分配 MSE 更低；端到端 KV 重构信噪比。

## 运行

```bash
python3 demo.py
```
