# 2608.16104 Nexus Qwen3-0.6B 复现

Qwen3-0.6B 是 dense 模型，脚本把真实 `up_proj` 输出行分成 8 个“伪专家”，对每个分区独立执行对称 INT4 权重和 E2M1 风格 FP4 激活 fake quant；激活按 99.9 percentile 校准，每个专家记录独立 scale，并用 STE 做 5 个小型 QAT 步骤。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --experts 8 --qat-steps 5
```

这验证论文 per-expert 低比特训练核心。Qwen3-0.6B 没有 MoE router/DeltaNet，也不是文生图模型，因此不复现 FID、A100/RTX5090 延迟或生成质量。

**2026-08-19 实测**：8 个分区、5 个 STE-QAT 步骤后输出 MSE `0.00612305`；真实 Qwen 权重加载与语法检查通过。
