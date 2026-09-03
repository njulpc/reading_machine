# 2609.01683 — FORGE 前向统计重校准

## 方法与实现范围

论文在已折叠 BN 的 MCU CNN 中保存 former-BN 输出的干净目标 `β, |γ|`，对测试流逐通道统计均值/方差并以 EMA 更新，再用 FP32 affine 重校准包围真正的 INT8 卷积。论文主设置是逐通道权重、逐张量激活 INT8，且只选择 3/21 个站点。

Qwen3 使用 RMSNorm，没有 Conv→BN 折叠站点。因此本 demo 只做明确标注的工程迁移：全部 196 个 backbone Linear 做逐输出通道对称 INT8 fake quant，在第 0/13/27 层 q_proj 输入注入逐通道漂移，并严格按论文公式用 `m=0.1` 重校准。它不是 ESP32-S3/CNN 复现。

## 运行

```bash
python3 scripts/quantization/2609.01683/demo.py --self-test
python3 scripts/quantization/2609.01683/demo.py --output-json /tmp/2609.01683.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** EMA 更新、逐通道均值/方差、回标到干净统计、FP32 重校准与 INT8 路径边界一致；模型结构、former-BN 目标、单样本流、when-to-adapt gate、21 层排序和 MCU bit-exact 卷积不一致或未覆盖。
- **修复：** 从首层局部矩阵扩为 196 个 Linear/440,401,920 权重的整模 INT8 替换；恢复论文 EMA 公式和 3 个选择站点；补量化后完整前向、一 token 生成、有限值断言和 JSON 记录。
- **结果：** 退出码 0，2.83 s。相对 dense，干净 INT8 logits MSE `0.00993995`；注入漂移后 `0.0206427`；FORGE 迁移后 `0.0145811`，说明恢复了一部分但未回到干净 INT8 水平；生成 token 为“如何”。
- **真实 Qwen3-0.6B：已跑通（工程迁移）。** 论文 FORGE 完整方法未跑通，因为 Qwen 没有目标结构，且本机无 ESP32-S3/ESP-NN；fake quant 未导出压缩权重。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；使用本地完整 Qwen3-0.6B checkpoint（596,049,920 参数），无下载。
