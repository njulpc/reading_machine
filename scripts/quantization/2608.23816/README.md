# 2608.23816 AQLoRA 复现

复现论文的一次无数据 CPU 扫描：对 Qwen3-0.6B 各 attention projection 按 64 元素 NF4 重构 MSE 排序，在 `--protect-fraction` 内将 Top-K 层保留 FP16，其余按 NF4 计费；同时给出同数量 seeded-random 控制，呼应论文“数量有效、排序身份未显著胜过随机”的负结果。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

默认只扫描每层前 262,144 个元素以控制 CPU 时间。它验证算法分配与真实 Qwen 权重，不复现 QLoRA 长训练、Unsloth kernel 或论文跨会话吞吐。

实测（Apple CPU）：扫描 112 个 projection，保护 17 层（15.18%），估算有效位宽 5.8214 bit；Top-K NF4 MSE 为 `9.6594e-06`，seeded-random 为 `6.8329e-06`，真实重现了“误差排序没有胜过随机控制”的警示。
