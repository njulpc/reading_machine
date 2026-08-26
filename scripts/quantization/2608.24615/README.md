# 2608.24615 Bangla 量化影响复现

用本地 Qwen3-0.6B tokenizer 和真实 Bangla 文本执行一个明确标注的 **W8A16 per-output-row RTN 工程迁移**：加载全模型、量化除 `lm_head` 外全部 196 个 Linear、比较最后 token 全词表 logits，并实际生成下一 token。它用于验证 Bangla 输入穿过真实整模 W8 路径，不伪装成论文 GPTQ checkpoint 或基准准确率。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-27）

- 算法一致性：**部分一致**（仅研究问题和 INT8 范围相符）。[原论文（arXiv:2608.24615）](https://arxiv.org/abs/2608.24615) 比较 Qwen2.5-7B GPTQ-Int8、LLaMA-3.1-8B GPTQ-Q8、GPT-OSS-20B GGUF-W8A16 的已量化检查点，并用 lm-eval-harness 对五个 Bangla 零样本数据集做候选 log-likelihood 准确率；它没有 W4 实验，也不是简单逐行 RTN。
- 修复：移除原脚本无论文依据的 W4 对照和首层 embedding→q_proj MAE 代理，改为与论文位宽范围一致的 W8，并覆盖全模型量化替换、前向和生成；输出明确标为 RTN engineering transfer，不能声称 GPTQ。
- 环境：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，safetensors 0.7.0；Apple arm64 CPU，CUDA/MPS 不可用。
- 结果：退出码 0，墙钟 3.68 s；Bangla 文本 68 token；196 层/440,401,920 权重元素完成 W8 RTN，平均权重 MAE `2.10971703e-04`，最后 token logits MAE `0.07954194`、cosine `0.99957269`，一步生成成功，理论权重 payload 相对 FP16 为 2.00x。
- **真实 Qwen3-0.6B：已跑通**（W8 RTN 工程迁移的整模加载、量化替换、前向和生成）；论文指定的 Qwen2.5-7B GPTQ checkpoint、五基准 lm-eval 准确率、LLaMA/GPT-OSS/GGUF 与跨格式比较未跑通。
