# RFQ（arXiv:2608.26581）Qwen3-0.6B 验证

脚本对真实 Qwen3-0.6B prompt 前向，用 hook 抓取首层 MLP `gate_proj` 输入。量化器实现 block-32、power-of-two shared scale、E2M1 网格 `{0, ±0.5, ±1, ±1.5, ±2, ±3, ±4, ±6}`。先做主 MXFP4，再按 block MSE 选择最差 10% block，将完整残差重新量化到同一 MXFP4 格式并累加，对照主路径与 RFQ 的 MSE/cosine。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --fallback-fraction 0.10
```

这对应论文 Algorithm 1 的 `X≈X~+φ·X^` 数值机制；`φ` 用可复核的 block-MSE top-k 代理。未复现论文约 5B-token QAT、Wan2.2/Qwen3-VL-30B、HiF4 64-element metadata、FP4 Tensor Core streaming kernel，因此不声称论文 VBench 或四个推理基准结果。

## 实际验证（2026-08-29）

arm64 CPU、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；CUDA/MPS 均不可用。真实 prompt 得到 `[1,10,1024]` 激活；主 MXFP4 MSE 0.00298579、cosine 0.992573。对误差最大的 10% block 启用同格式残差后，MSE 降至 0.00185159（下降 37.9866%），cosine 升至 0.995374，命令退出码 0。
