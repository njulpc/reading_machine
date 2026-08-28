# BNN 全局加权剪枝（arXiv:2608.26233）Qwen3-0.6B 验证

脚本把论文 global weighting + single-threshold pruning 迁移到真实 Qwen3-0.6B 的全部 28 层 MLP。默认逐输出通道做 L∞ 归一化，在 264,241,152 个变换后权重上求一个全局 order statistic，再确定性处理阈值并列项，使剪枝数精确匹配目标；保留项用逐输出通道 mean-abs `alpha × sign` 作为 Qwen 无 BatchNorm 时的工程二值代理，随后执行整模前向与单 token 生成。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --pruning-ratio 0.70 --normalization channel --scope all-mlp
```

## 代码审查与验证（2026-08-29）

**算法一致性：部分一致。** 已核对 arXiv v1 官方 PDF。论文先做 300 epoch activation-binary pretraining，在权重二值化前剪枝，再做 100 epoch fine-tuning 和 300 epoch binary training；Algorithm 2 扫描全局排序阈值，以验证集 accuracy/loss 选择最终点。VGG11 的最佳报告使用 BatchNorm folding + layer-wise L∞，达到 70% pruning；Algorithm 1/3、不同模型还使用不同 weighting。Qwen 是 RMSNorm Transformer，没有可等价 fold 的 CNN BatchNorm，因此这里的 channel L∞ 和 `alpha × sign` 都是透明的迁移选择，不能等同论文完整 BNN 训练。

本次修复：由首个 block 的 7 个 Linear 扩到全 28 层 MLP / 84 个 Linear；用 streaming histogram bracket + 局部 order statistic 保持全局排序而不物化 264M score；修复首次运行发现的 threshold tie 过剪 bug；真实替换权重并补齐量化后前向、有限 logits 和生成。脚本也报告理论 FC BMAC 前后计数，但不宣称不规则稀疏可直接获得 kernel 加速。

环境为 Apple M4（10 核、16 GB）arm64 CPU，Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0；CUDA/MPS 均不可用。命令退出码 0，墙钟 4.05 秒；全局阈值 0.26080248，实际剪枝率 0.6999999985，BMAC 代理从 264,241,152 降到 79,272,346，平均 normalized weight MSE 0.45905295。整模 logits MAE 4.59564066、last-token cosine -0.14539239，虽能生成但质量严重退化，是不能省略论文训练阶段的负面证据。

**真实 Qwen3-0.6B：已跑通（全 28 层 MLP 的剪枝/二值工程迁移与整模前向/生成）。** 未跑通论文 VGG11/CIFAR-10 的 700 epoch 训练、validation sweep/accuracy constraint、channel-velocity freezing、FPGA/MCU packing 或实际稀疏 kernel；因此论文方法本体仍未被完整复现。
