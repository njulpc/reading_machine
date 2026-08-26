# 2608.24173 SandwichQuant 复现

在 Qwen3-0.6B 首层真实 RMSNorm→`q_proj` 路径上，用 32 个固定随机校准 token、W4 group-size 128 和 affine-only Adam，依次做 40 步 pre-stage 与冻结量化图后的 40 步 post-stage；报告量化输出 MSE 和误差闭合率。可训练量仅为 RMSNorm 的 1024 个 affine 参数，不改变推理算子。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

这是论文“高杠杆 affine 子空间”的真实 Qwen 小校准验证，不复现三模型族、激活/KV 联合量化、数据集准确率或后端 kernel。

实测：W4 基线输出 MSE `5.68100135e-04`，pre-stage 后 `5.42642490e-04`，post-stage 后 `5.40942303e-04`，共闭合 4.7805% 量化误差。
