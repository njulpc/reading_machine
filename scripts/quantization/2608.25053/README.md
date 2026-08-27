# Hydra（arXiv:2608.25053）Qwen3-0.6B 验证

Hydra 是阶段感知的边缘 LLM 测量框架，不是新量化算法。脚本加载真实 Qwen3-0.6B，分别记录 tokenization、prefill stage/phase、TTFT、逐 token generation、de-tokenization、ITL、decode phase 和端到端时间；随后把除 `lm_head` 外全部 196 个 Linear 做 block-32 对称 INT8 fake quant，并按 Q8_0 的“32 个 INT8 + 1 个 FP16 scale”计入元数据。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --decode-steps 2
```

## 代码审查与验证（2026-08-28）

**算法一致性：部分一致。** 已对照官方 arXiv v1 PDF 的 §III–IV、表 II–III。阶段边界、公共 per-prompt schema、greedy token-by-token decode 与 KV-cache reuse 和论文一致；修复了旧版只报 prefill/decode、把逐行 W8 当成 Q8_0、漏算 block scale 并据此错误报告 4× payload 的问题。论文实际比较 HF bf16 与 llama.cpp F16/Q8_0/Q6_K/Q4_K_M，Q8_0 约 8.5 bit/weight；本脚本是 CPU/PyTorch 数值代理，不是 GGML pack/kernel。

真实运行环境：Apple M4（10 核、16 GB），arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0。命令退出码 0，墙钟 5.78 秒；196 层、440,401,920 个权重完成量化，Q8_0 理论 payload 467,927,040 bytes（相对 FP32 3.764706×），prefill logits cosine 0.99990648、MAE 0.03219194，量化后缓存 decode 生成“预填充”。单次 dense/Q8 prefill 0.375520/0.074225 秒含冷启动差异，不作为性能结论。

**真实 Qwen3-0.6B：已跑通（全 196 Linear 的 Q8_0 数值代理、prefill、KV-cache decode 与文本解码）。** 未跑通/不适用：Jetson Xavier/Orin/Thor、CUDA 同步、tegrastats/NVML、llama.cpp 原生格式、IFEval/RULER 约 107K records、功耗/能耗/温度与稳定性能测量；不得用本机 timing 代替论文系统结论。
