# Ankhdjet（arXiv:2608.26206）Qwen3-0.6B 验证

脚本加载本地真实 Qwen3-0.6B，取首个 `q_proj` 的 1,048,576 个权重，按共享均值尺度三值化到 `{-1,0,+1}`，再以论文“权重到掩膜”思想编码成 2-bit mask program（每字节 4 个权重），并做逐元素精确解码验证。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

这是真实模型权重上的数值/掩膜编译参考，不是 SKY130 版图工具链。论文的 KLayout DRC、netgen LVS、时序、寄生能耗与流片结果需要 OpenROAD/PDK/EDA 环境；脚本不会用软件 packing 冒充硅上 0.98–1.73 pJ 测量。

## 实际验证（2026-08-29）

arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；CUDA/MPS 均不可用。命令退出码 0：1,048,576 个真实 `q_proj` 权重中零值占 0.339342，2-bit packing 为 262,144 bytes，round-trip 逐元素完全一致；相对 L2 为 0.581702，说明简单三值化数值损失明显，不能把编译正确性误写成任务精度保持。
