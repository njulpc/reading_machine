# CropCop INT8 工件路径（arXiv:2608.25539）Qwen3-0.6B 验证

按论文最终选择的“dynamic activations + per-channel weights”，脚本对真实 Qwen3-0.6B 除 `lm_head` 外全部 196 个 Linear 执行 per-output-channel W8 fake quant，并用 forward pre-hook 对每个 token 动态量化输入激活；三条中英文 prompt 做逐 logits、top-1 和 cosine 核验。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

验证边界：论文最终产物是 MobileNetV4 的 ExecuTorch/XNNPACK PTE，Qwen 验证不能替代 120 类植物 benchmark、22.60 MiB PTE 或 Android 运行时。这里真实覆盖全模型 W8A8 数值路径，但不声称 fake quant 已导出整数 kernel 或复现论文 16,363 样本逐工件比较。

本次实跑：196 层、440,401,920 权重均量化；三条 prompt 的 last-token top-1 match 为 1.0，平均 cosine 0.99585170、logits MAE 0.23607825，全部 finite 断言通过。
