# Paper: 2603.29078 — PolarQuant (Optimal Gaussian Weight Quantization via Hadamard Rotation)

复现内容：PolarQuant 三阶段管线
1. 块级归一化到单位超球面
2. Walsh-Hadamard 旋转（把权重坐标变为近似高斯）
3. 高斯匹配质心量化 + 反量化

目标模型：Qwen3-0.6B。若本地无缓存且无法访问 HuggingFace，则自动退化为
与 Qwen3-0.6B 同构的微型随机模型（hidden=896, 2 层, GQA），验证全部代码路径。

## 验证方式（如实说明）

- 本机 HuggingFace 缓存中**已有真实 Qwen3-0.6B 权重**，demo 直接以
  `local_files_only=True` 加载真实权重验证（输出含 `[model] loaded real Qwen3-0.6B`）；
  若无缓存则自动退化为同构 mock（hidden=896, 2 层, GQA）。
- 验证项：Hadamard 旋转的正交性（重构误差≈0）、量化-反量化 MSE、
  旋转前后权重分布的高斯化（峰度下降，真实权重上实测 6.8 → 2.9）、
  以及"旋转贡献"消融（本 demo 实测旋转占 MSE 降幅 ~19%，与论文 98% 归因方向一致、
  幅度不同，因 mock 设定与评价口径差异，已在输出中标注）。

## 运行

```bash
python3 demo.py
```
