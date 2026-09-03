# 2609.01743 — SCULPT 的 PTQ-ready 激活整形

## 方法与实现范围

论文在 EfficientNet-B0 的普通 FP32 微调中同时使用 UADR 与 Adaptive Stable Percentile Clipping：UADR 对 Conv/Linear 输出惩罚正偏度和超过 3 的峰度；SPC 包裹激活函数输出，以 0.001/0.999 分位、最多 100,000 个采样值和逆时 EMA 学习边界，epoch 2 后冻结。部署 PTQ 是逐通道对称权重、逐张量非对称激活，使用 32 个校准 batch，并比较 W8A8/W4A8。

本 demo 实现 UADR 数值算子、分位/逆时 EMA 和 W4A8 部署合同，但没有把 Qwen 重新训练成 SCULPT checkpoint；Qwen 的 pre-Linear 边界只是工程迁移。

## 运行

```bash
python3 scripts/quantization/2609.01743/demo.py --self-test
python3 scripts/quantization/2609.01743/demo.py --output-json /tmp/2609.01743.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** 位宽、权重/激活粒度、0.001/0.999 分位、采样上限、逆时 EMA 与 UADR 目标已对齐；缺少 ImageNette、80 epoch 基线、16 epoch SCULPT 微调、epoch-2 冻结、32 校准 batch 与 matched QDQ supergroup。
- **修复：** 删除固定 99.5% 裸裁剪冒充 SCULPT 的表述；加入 UADR 探针；将 W4A8 扩展到全部 196 个 Linear/440,401,920 权重；用 8 个独立校准 prompt 学习逐层边界，并用另一条文本做整模前向/生成。修复 BF16 `eps` 被误作量化最小步长的问题。
- **结果：** 退出码 0，5.92 s。相对 dense，min/max W4A8 logits MSE `22.4795`、cosine `0.486069`；percentile W4A8 MSE `14.8022`、cosine `0.416119`，均严重退化，不能据此宣称 SCULPT 有效；JSON 导出成功。
- **真实 Qwen3-0.6B：已跑通（PTQ 工程迁移）。** 论文 SCULPT 训练未跑通；没有训练后的 SPC 边界、视觉任务准确率或量化模型保存工件。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；本地完整 Qwen3-0.6B checkpoint。
