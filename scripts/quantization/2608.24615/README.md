# 2608.24615 Bangla 量化影响复现

使用本地 Qwen3-0.6B tokenizer 对真实 Bangla 句子分词，读取对应真实 embedding 和首层 `q_proj`，比较 per-output-row W8A16 与 W4A16 fake quant 的投影 MAE/cosine，并报告相对 FP16 的理论权重压缩。默认文本和 seed 固定，可用 `--text` 替换。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

它真实覆盖 Bangla token 和 Qwen 权重的数值路径，但不是论文五个 Bangla benchmark 的生成式零样本准确率，也不复现 LLaMA/GPT-OSS/GGUF/GPTQ kernel。

实测：默认 Bangla 句子产生 68 个 token；W8A16 的 MAE/cosine 为 `0.00019130/0.99996656`，W4A16 为 `0.00345248/0.98955780`，对应理论权重压缩 2x/4x。
