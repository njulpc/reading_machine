# 层级量化优先级（arXiv:2608.26926）Qwen3-0.6B 验证

脚本加载真实 Qwen3-0.6B 首个 Transformer block 的 7 个 Linear，对每层做逐输出通道对称 INT4 fake quant，计算 SQNR 质量分；再用可配置 memory-bandwidth/peak-FLOPs roofline 估算 FP16 与带 FP16 row-scale 的 INT4 payload 时间，归一化后以 `quality_weight=0.5` 合成优先级并排序。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --quality-weight 0.5 --bandwidth-gbps 50 --peak-gflops 100
```

这是论文“信息保留 + 速度收益”复合指标在真实 Qwen 权重上的小规模实现。roofline 参数是透明假设，不是本机 benchmark；未复现 Gemma 3 1B、真实 INT4 kernel、任务准确率和论文约 4% 的跨架构速度预测误差。

## 实际验证（2026-08-29）

arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；CUDA/MPS 均不可用。命令退出码 0。7 个 Linear 的 INT4 SQNR 为 14.4324–16.4305 dB；在显式假设 50 GB/s、100 GFLOP/s、单 token 的 roofline 下，所有层落入 compute floor、预测 speedup 均为 2.0，因此本次 0.5/0.5 复合排序主要由 SQNR 区分，`k_proj` 最高、`o_proj` 最低。这也暴露了简单 roofline 在形状相近层上的分辨率边界。
