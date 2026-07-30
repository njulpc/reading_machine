# Paper: 2603.01599 — BBQ (Boosting entropy with Bell Box Quantization)

复现内容：BBQ 的核心思想——"量化器输出不必与输入同域"
1. 输入域：信息论最优（ITO）分数量化（Quantile/NormalFloat 风格）
2. 输出域：把 ITO 电平一一映射到计算高效的整数码字（Bell Box 映射）
3. 验证：同等比特下 BBQ（ITO+映射）较均匀整数量化的 PPL 代理指标（量化 MSE / 表示熵）更优，且整数码字可直接用于整数 MAC

目标模型：Qwen3-0.6B 同构 mock 权重。

## 验证方式（如实说明）

- 未下载真实权重，用 mock 权重验证。
- 验证项：Bell Box 双域映射可逆；相同比特预算下 BBQ 的量化 MSE 低于均匀量化；
  映射后的码字为非负整数（计算高效域）；熵利用率（有效码字数/总码字数）提升。

## 运行

```bash
python3 demo.py
```
