# 2608.23018 复现：SplitLite quantized low-rank residual

demo 读取真实 Qwen3-0.6B `q_proj` 维度，用两次 rank-r LoRA 更新构造相邻 epoch residual（理论 rank ≤ 2r），截断到 rank-2r 后对 SVD factors 做对称 INT8，报告重构误差与相对 dense FP32 residual 的编码倍率。

```bash
PYTHONPATH=/private/tmp/arxiv_pydeps python3 demo.py --checkpoint /path/to/model.safetensors --rank 8
```

本次验证成功读取 `q_proj` 真实形状 2048×1024，并在 256×256、LoRA rank 8 的小规模 residual 上通过 rank≤2r 断言。INT8 rank-16 factors 的 relative error = **0.01202756**，相对 dense FP32 residual 的编码估算为 **31.969×**。由于没有论文的 GLUE split-federated 客户端、相邻 epoch 激活/梯度轨迹和网络传输环境，residual 由真实模型维度上的确定性 LoRA 更新合成；不声称复现 93.5% uplink 或 83.7% total-communication 结果。
