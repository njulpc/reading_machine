# 2608.15602 FluxBin Qwen3-0.6B 核心复现

脚本按论文公式拟合 `alpha_r alpha_c^T` 外积尺度的联合二值基；以完整逆 Hessian 的结构化列分数在每个 128 列 group 选择 8 个显著列，再对残差拟合二值 refinement，并验证 group-8 LUT 与直接乘法一致。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --group-size 128 --base-order 2 --salient-columns 8
python ../full_model_smoke.py --model-dir /path/to/Qwen3-0.6B/snapshot --method flux
```

## 代码审查与验证（2026-08-19）

- **一致性：部分一致。** 代表层覆盖 row-column outer-product bases、联合符号搜索、Hessian 结构列显著性、hybrid refinement 与 LUT；未实现 GPTQ 列误差传播、VCM、LUT-BSF、scale fusion 或 CUDA kernel。
- **修复：** 原代码错误地串联“row basis + column residual basis”，只用 Hessian 对角并选择散乱元素；现按论文 Eq.3-9 改为外积基和每组显著列。
- **代表层结果：** 64×256 真权重，2 个全局基、每组 8 个显著列（6.25%），输出 MSE `0.020650025`，LUT 等价断言通过。
- **整模诊断：** 工程退化为全模型两级贪心二值基，196 个 Linear、440,401,920 参数；前向有限，logits MSE `23.882246`，生成 token `他们`，`2.008s`。该结果不是完整 FluxBin。
- 环境同上：CPU-only，无法验证论文专用 CUDA 性能。
- **真实 Qwen3-0.6B：未跑通（代表层算法核心通过；整模为退化烟测）。**
