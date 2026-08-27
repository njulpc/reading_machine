# Great Inversion（arXiv:2608.25188）Qwen3-0.6B 验证

脚本从真实 Qwen3-0.6B 首层 `q_proj` 读取 1024×1024 权重 tile，执行严格可逆的归一化 Walsh–Hadamard 变换，并分别比较 group-128 对称 INT4 与 block-32、power-of-two scale 的 E2M1/MXFP4 软件量化误差。它直接检验论文的变换—分组—格式共同设计观点，而不是把 rotation 当成与格式无关的固定收益。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

验证边界：这是论文综述/理论命题的真实权重小张量验证；没有复跑 200 篇文献、43 方法或 GPTQ 搜索，也没有原生 MXFP4 指令。脚本使用 UOS 7.25 的 E2M1 软件投影来固定复核口径，输出中的收益或退化均保留，不预设 rotation 必胜。

本次实跑：Hadamard 严格逆变换断言通过；group peak 均值从 0.08731062 降到 0.08372293。rotation 后 INT4 MSE 比为 0.87685116，而 MXFP4 MSE 比仅 0.97387533，直接显示同一变换对不同格式的收益不同。
