# Paper: 2603.27914 — ITQ3_S (Interleaved Ternary Quantization with Rotation-Domain Smoothing)

复现内容：
1. 快速 Walsh-Hadamard 变换（FWHT）预旋转，把权重异常值能量摊平为近似高斯
2. 旋转域均匀三值编码（3-bit 打包格式）
3. 反量化时融合逆 FWHT，验证重构误差仅来自三值网格（论文核心误差界）

目标模型：Qwen3-0.6B（无网络时使用同构 mock 模型）。

## 验证方式（如实说明）

- 本环境**未下载真实 Qwen3-0.6B**，用同构 mock 权重验证全部代码路径。
- 验证项：FWHT/逆 FWHT 精确互逆（误差 < 1e-6，对应论文"逆变换不引入额外误差"）；
  旋转后分布高斯化；ITQ3_S 重构 MSE 显著低于未旋转的均匀 3-bit 基线（对应论文误差界论断）。

## 运行

```bash
python3 demo.py
```
