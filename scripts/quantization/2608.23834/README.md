# 2608.23834 Minima-KV 复现

从 Qwen3-0.6B 首层真实 K/V projection 生成 128-token 校准缓存，按 16-token 页构造三层策略：近期页和周期锚点页用 E4M3 FP8，旧页先做归一化 Walsh-Hadamard rotation，再用 page-wise 3-bit signed grid 并逆旋转；所有页保留并在同一 softmax 中直接计算，记录相对 BF16 的理论位宽压缩和 attention 输出 relative-L2。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

这是 CPU fake-quant 小张量验证，不是论文 TQ3 packing、Blackwell kernel、Qwen3.6-27B 96GB 长上下文或吞吐复现；因此不能用脚本结果替代论文 3.50x/LongBench 结论。

实测：8 页格式为 4 个 FP8、4 个 TQ3，理论相对 BF16 为 2.9091x，统一 softmax 输出 relative-L2 为 0.42834324。这个较大误差说明小样本固定分层不能替代论文的 anchor 策略和 norm-corrected TQ3P kernel。
