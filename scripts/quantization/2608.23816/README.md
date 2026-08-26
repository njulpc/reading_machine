# 2608.23816 AQLoRA 复现

按 [AQLoRA（arXiv:2608.23816）](https://arxiv.org/abs/2608.23816) 的一次无数据 CPU 扫描，对 Qwen3-0.6B 的全部 196 个 Transformer Linear 以 64 元素 absmax-NF4 重构 MSE 排序；按论文 `ceil(ρL)` 保护 Top-K 整层为 FP16，其余执行 NF4 fake quant，并实际完成整模前向与一步生成。脚本同时给出同数量 seeded-random 控制和含 double-quant scale 的分析字节账目。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-27）

- 算法一致性：**部分一致**。公式 (1) 的 64 元素 NF4、无数据层级误差与公式化 Top-K 已对齐；论文还包含真实 bitsandbytes NF4+double-quant、QLoRA/LoRA 训练、全层或顶部 85% block 的 adapter placement、提前停止反向和跨会话 V100 计时，本 CPU reference 不复现这些系统与训练结论。
- 修复：原脚本只扫 112 个 attention projection、默认只取每层前 262,144 元素，且没有量化替换、前向或生成。现默认完整扫描 440,401,920 个权重元素、覆盖 attention+MLP 全部 196 层，并按未保护模块执行整模 fake quant。
- 环境：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，safetensors 0.7.0；Apple arm64 CPU，CUDA/MPS 不可用。
- 结果：退出码 0；扫描 3.737 s；保护 40/196 层（层比例 20.41%，参数比例 24.29%），156 层/333,447,168 元素执行 NF4；有效位宽分析值 7.0104 bit。Top-K/随机保护层的平均 NF4 MSE 为 `9.73975918e-06/6.38628320e-06`，继续支持论文“排序身份未胜过随机控制”的警示。量化后 logits MAE `0.42475188`、末 token cosine `0.98647314`，一步生成成功。
- **真实 Qwen3-0.6B：已跑通**（完整权重扫描、整模 NF4 fake-quant 替换、前向和生成）；真实 QLoRA 长训练、Unsloth/bitsandbytes kernel、速度配置反向提前终止与保存导出未跑通，不能以本结果替代论文训练速度/准确率。
