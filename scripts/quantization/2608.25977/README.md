# Quantized Personality 层级漂移（arXiv:2608.25977）Qwen3-0.6B 验证

脚本使用论文原始 A–G 七选项 prompt，把每层 hidden state 经 final norm/lm_head 映射到 option token sets，精确计算逐层 Shannon entropy、top-1/top-2 confidence gap，并按最大 JSD premature layer 实现 `UALD = log p_mature + lambda log p_premature`。随后比较 FP32、全 196 Linear group-128 W4/W2 RTN 代理，并执行单 token 生成。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --questions 4 --evolution-scale 10
```

## 代码审查与验证（2026-08-28）

**算法一致性：部分一致。** 已对照官方 arXiv v1 PDF §3.3–3.4、附录 A/C/D/E。旧版只报 hidden/logit cosine、entropy 和 top-1 agreement，不是论文的七选项层级指标，也未实现 UALD；现已按公式修正。默认仅使用论文原 60 题中的 4 题做 smoke test，明确不将其称作完整 MBTI 评估；W4/W2 RTN 也不冒充论文 GPTQ/AWQ/AQLM/PV checkpoints。

真实运行退出码 0、墙钟 6.72 秒。FP32 的 first/mid/last entropy 为 1.089033/1.520343/0.227435，gap 为 0.496262/0.206805/0.939103，成熟选择 FFFF，UALD(10) 为 AEAE。W4 RTN 成熟选择 GGGG、与 FP32 agreement 0；W2 为 BFGB、agreement 0.25。两个代理均量化 196 层/440,401,920 权重并完成生成；W4 并未比 W2 更稳，负结果说明简单 RTN 不可代替论文 checkpoint。

**真实 Qwen3-0.6B：已跑通（全模型 W4/W2 RTN 工程代理、逐层 option logits、UALD、前向与生成）。** 论文完整复现未跑通：未覆盖 60 题、16 personality-conditioned prompts、六个 7B–72B 模型、真实 GPTQ/AWQ/AQLM/PV 权重及 `lambda=5..40` 全 sweep；本结果不是心理学或 MBTI 结论。
