# Quantized Personality 层级漂移（arXiv:2608.25977）Qwen3-0.6B 验证

脚本用两条人格式中英文 prompt 在真实 Qwen3-0.6B 上取得 FP32、全 196 Linear 的 group-128 W4 与 W2 RTN 前向；逐层比较最后 token hidden cosine，并记录最终 logits cosine、entropy 与 top-1 一致性。它复现论文“量化影响应沿层审计，2-bit 风险可能先表现为一致性下降”的测量骨架。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

验证边界：W4/W2 RTN 是透明的工程代理，不冒充 GPTQ、AWQ 或 AQLM checkpoint；两条 prompt 不是完整 MBTI 问卷，也不能重现论文跨模型人格分布。脚本真实量化 440,401,920 个 Qwen 权重并完成三次全模型前向，报告的是数值漂移，不把它解释成心理学结论。

本次实跑：W4 的 final-logit cosine 为 0.81128311、最差层 cosine 0.75306976；W2 分别降到 0.07925478 和 -0.02273615。两个代理的 top-1 match 都为 0，显示简单 RTN 不能代替论文 GPTQ/AWQ/AQLM 检查点，也支持“极低比特需沿层审计”的方向性结论。
