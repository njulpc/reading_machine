# RFQ（arXiv:2608.26581）Qwen3-0.6B 验证

脚本实现论文 Algorithm 1 的软件参考：按最后一维切 block-32，使用公式 (3) 的 `2^floor(log2(max_abs))` shared scale 与 E2M1 网格量化 activation 和 weight；对 `phi(p,r)=1` 的激活块计算完整残差、再次量化到同一 FP4 并累加。真实模型路径预量化全部 196 个 Transformer Linear 权重，并通过 pre-hook 对每次 Linear 输入执行 base MXFP4 或 RFQ，`lm_head`/embedding 保持浮点，最后比较整模 logits 并生成。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --fallback-fraction 0.10
```

## 代码审查与验证（2026-08-29）

**算法一致性：部分一致。** 已核对 arXiv v1 官方 PDF 的公式 (3)–(12) 与 Algorithm 1。原脚本只有一个 activation tensor 的重构，scale 使用 `ceil(log2(max/6))`，按 block MSE 选 top-k，既没有量化 Y，也没有执行 `X~Y~ + phi X^Y~` GEMM；现已按论文 scale 公式修正并增加 X/Y 同格式量化、base GEMM、residual GEMM、全模型权重/激活路径。论文只称 `phi` 识别显著 outlier block，没有公开可复核阈值算法；本脚本采用 block max-abs top fraction，明确标为工程规则而非论文细节。

环境为 Apple M4（10 核、16 GB）arm64 CPU，Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0；CUDA/MPS 均不可用。命令退出码 0，墙钟 6.03 秒。小张量 Algorithm 1 测试中 base/RFQ output MSE 为 9.18407440/8.48005676。真实整模量化 196 个 Linear / 440,401,920 权重；单次前向触发 196 次、89,600 个 activation block，RFQ 精确选择 8,960 个（10%）。相对浮点 logits，W4A4 base MAE 为 2.60931373，RFQ 为 1.87788212，下降 28.0316%；量化后单 token 生成成功。

**真实 Qwen3-0.6B：已跑通（全 196 个 Transformer Linear 的 W4A4 fake-quant、RFQ 前向与生成）。** 这是纯文本 0.6B 的软件迁移；未跑通论文 Qwen3-VL-30B/Wan2.2、约 5B-token QAT、HiF4、vision 模块、真实 FP4 Tensor Core streaming kernel、VBench/四项视觉问答基准或低比特模型导出。代码不把 fake quant 的数值改善表述为真实硬件加速。
