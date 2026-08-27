# Hydra（arXiv:2608.25053）Qwen3-0.6B 验证

脚本复现论文最关键的“按阶段、格式和资源统一记录”思想：加载真实 Qwen3-0.6B，分别测量 prefill 与逐 token decode；随后把除 `lm_head` 外全部 196 个 Linear 做 per-output-row W8 fake quant，再以相同 prompt 复测并记录理论 payload、logit MAE 与 cosine。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

验证边界：这是 CPU 上的 W8 软件路径，不是 Hydra 的 Jetson Xavier/Orin/Thor、llama.cpp 后端或 107K trace corpus；Python fake quant 不代表原生 INT8 kernel 的绝对时延。脚本真实加载 596M 参数模型并覆盖全部 Transformer Linear，未伪造 SoC 功耗与五格式结果。

本次实跑（CPU、PyTorch 2.8.0、Transformers 4.57.6）：196 层、440,401,920 个权重完成 W8；FP32/W8 理论 payload 为 1,761,607,680/440,401,920 bytes（4×），last-token cosine 0.99960029、MAE 0.08082828。单次 timing 为 dense/W8 prefill 0.164275/0.075005 s，decode median 0.040450/0.040385 s；只作为本机 smoke test，不作为稳定性能结论。
