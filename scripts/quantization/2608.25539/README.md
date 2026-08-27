# CropCop INT8 工件路径（arXiv:2608.25539）Qwen3-0.6B 验证

按论文最终选择的“dynamic activations + per-channel weights”，脚本对真实 Qwen3-0.6B 除 `lm_head` 外全部 196 个 Linear 执行 per-output-channel W8 fake quant，并以显式 `per_token` 工程粒度动态量化输入激活；三条中英文 prompt 做逐 logits、top-1、cosine 与单 token 生成核验。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-28）

**算法一致性：部分一致。** 已对照官方 arXiv v1 PDF §5、表 5–7 与附录表 16。论文不是新量化器，而是 validation-only PTQ selection → converted graph → XNNPACK lowering → PTE serialization → 同一 16,363 test rows 直接执行的证据链。脚本的 W8A8 方向一致，但 Qwen 迁移没有论文 MobileNetV4/图像数据/ExecuTorch 工件。审查新增量化后真实生成、权重 scale 元数据计数和可选 activation 粒度；论文未公开 dynamic activation 的细粒度，默认 per-token 必须视为工程代理而非反推事实。

真实运行退出码 0、墙钟 2.67 秒；196 层、440,401,920 权重完成 W8，含 FP32 per-channel scales 的解析 payload 为 441,778,176 bytes；三条 prompt top-1 match 1.0、平均 cosine 0.99585170、logits MAE 0.23607825，量化后生成“y”。

**真实 Qwen3-0.6B：已跑通（全模型 W8A8 fake-quant、前向与生成）。** 未跑通：CropCop 的 120 类/109,107 图 benchmark、validation 0/1,440/2,880-row 三候选选择、MobileNetV4、torchao/ExecuTorch 1.3.1、XNNPACK lowering、23,696,352-byte PTE、SHA-256 与 16,363-row 工件一致性。Python fake quant 不是整数 kernel，也不是论文最终工件。
