# Paper: 2603.16590 — BATQuant (Block-wise Affine Transformation for MXFP4)

复现内容：
1. MXFP4（E2M1，32 元素块共享 E8M0 缩放）量化器
2. 论文核心批评的复现：全局正交旋转把异常值能量跨块转移，MXFP4 下性能崩溃
3. BATQuant：块级仿射变换（与 MXFP 粒度对齐）+ 块级可学习裁剪

目标模型：Qwen3-0.6B 同构 mock 权重/激活。

## 验证方式（如实说明）

- 未下载真实权重，用含异常值的 mock 张量验证。
- 验证项：复现论文论断——全局 Hadamard 旋转在 MXFP4 下反而**升高**块内重构 MSE
  （跨块异常值传播：权重 6.5e-4 → 8.1e-4）；块级仿射变换进一步降到 4.8e-4
  （激活上 3.8e-1 → 6.1e-2，W4A4 设定）。
- 实现说明：量化器不可微，块级仿射参数用 straight-through estimator (STE) 训练
  （朴素反传会得到 d(Q)/d(a)=0 而发散）；"可学习裁剪"以小网格搜索 {1.0, 0.9, 0.8, 0.7} 代替。

## 运行

```bash
python3 demo.py
```
