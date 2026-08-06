# SSTQ: Privacy-Preserving Vector Quantization via Subsampled Stochastic TurboQuant

## 论文信息
- **标题**: SSTQ: Privacy-Preserving Vector Quantization via Subsampled Stochastic TurboQuant
- **arXiv**: 2608.05127
- **关键词**: 本地差分隐私 (LDP)、过完备紧框架、随机旋转、坐标子采样、随机化响应

## 方法概述

SSTQ 面向联邦学习本地差分隐私 (LDP) 场景的极低比特向量量化。通过三大组件，
在每客户端仅用 `ceil(log2 N) + b` 比特的预算下实现 eps-LDP，并将 MSE 由直接
量化的 `O(4^b)` 降至 `O(2^b)`：

1. **过完备紧框架 / 随机旋转 (Overcomplete Tight Frame)**
   - 生成 N×d 随机紧框架 R，满足 `R^T R = (N/d) I_d` (N≥d)。
   - 旋转 `y = R x` 将能量均匀分散到 N 个坐标，消除权重离群大值。
   - N=d 时即正交随机旋转；N>d 时为过完备框架，提供冗余采样空间。

2. **坐标子采样 (Coordinate Subsampling)**
   - 从 N 个旋转坐标中无放回抽取 s 个，仅传输被采样坐标。
   - 单坐标通信成本 = `ceil(log2 N)` (索引) + `b` (量化值) 比特。

3. **隐私感知一维量化 (Privacy-Aware 1D Quantization)**
   - 随机一比特符号量化 (无偏)：`E[Q(y)] = y`。
   - **Flat Randomized Response**：以概率 `e^eps/(e^eps+1)` 上报真实符号，否则
     随机上报 ±1，实现 eps-LDP；服务端去偏因子 `(e^eps+1)/(e^eps-1)`。
   - **Metric-Aware Laplace**：注入 `Lap(0, 2/eps)` 噪声 (敏感度 2，值域 [-1,1])，
     实现 eps-LDP，服务端直接用含噪值 (无偏)。

服务端用紧框架伪逆 `x_hat = norm · (d/N) R^T y_hat` 重构，得到 x 的无偏估计。

**使用方式 (联邦 LDP)**：单个客户端的一比特随机量化估计是无偏但高方差的
(E[x_hat]=x，方差 ~O(d/s))；服务端聚合 K 个客户端的独立估计后，噪声以
O(1/K) 衰减，从而在保护每客户端隐私的同时恢复聚合信号。旋转使各坐标能量
均衡，子采样不再因离群值而浪费，从而在同等比特预算下取得更优的隐私-效用
权衡 (论文将 MSE 标度由 O(4^b) 降至 O(2^b))。

## 文件列表
- `demo.py` — SSTQ 完整实现与对比验证脚本

## 运行方式

```bash
cd scripts/quantization/2608.05127
python3 demo.py
```

脚本自动尝试加载 Qwen3-0.6B；若不可用则回退到 MockTransformer。运行后输出：
- 旋转前后坐标能量分散度对比；
- 联邦聚合：K 客户端平均下 MSE 以 ~1/K 衰减、cosine 趋近 1；
- 无偏性验证 (大 K 下 ||E[x_hat]-x||/||x|| → 0)；
- 隐私-效用权衡：不同 eps / 机制 (RR vs Laplace) 下的平均 cosine；
- 权重分组联邦压缩应用示例 (比特/客户端)。
