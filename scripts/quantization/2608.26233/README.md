# BNN 全局加权剪枝（arXiv:2608.26233）Qwen3-0.6B 验证

脚本加载真实 Qwen3-0.6B 首个 Transformer block 的 7 个 Linear。按照论文 §4 的 global weighting 思路，对每个输出通道做 `L∞` 归一化，再把全部变换后权重拼接，用单一阈值剪除 70%；保留项按通道均值尺度二值化。输出实际稀疏率与归一化 MSE。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --pruning-ratio 0.70
```

Qwen 使用 RMSNorm，没有论文 CNN 的 BatchNorm folding，因此这里选择论文明确比较的 `L∞` channel/layer weighting。验证覆盖真实权重排序、全局阈值和二值化数值路径；不声称复现 VGG11 的 300+100+300 epoch 训练、CIFAR-10 准确率、FPGA BMAC 或结构化 kernel 加速。

## 实际验证（2026-08-29）

arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；CUDA/MPS 均不可用。命令退出码 0：首 block 7 个 Linear、15,728,640 个权重完成全局排序，阈值 0.267196，实际剪枝率 0.7000099；剪枝后二值代理的平均归一化 MSE 为 0.460083。该结果只验证算法路径，不代表无需训练即可保持 Qwen 准确率。
