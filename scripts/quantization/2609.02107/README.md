# 2609.02107 — 统一 rate-distortion 量化比较

## 方法与实现范围

论文比较离散视觉 tokenizer 的 VQ、PQ 与 SQ。公平条件是相同 latent 分布以及相同 `T` 和 composite code-space `K`，distortion 为期望平方欧氏误差；这不是 LLM 权重量化方法。

本 demo 从同一 Qwen embedding 张量取 8 维向量，前 4,096 个训练码本、后 1,024 个独立评估；三种方法统一为 `K=256`、8 bit/vector：VQ `1×256`、PQ `2×16`、SQ `8×2`。

## 运行

```bash
python3 scripts/quantization/2609.02107/demo.py --self-test
python3 scripts/quantization/2609.02107/demo.py --output-json /tmp/2609.02107.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** matched source、matched `T/K/rate`、VQ/PQ/SQ 结构与 squared-error distortion 一致；视觉 encoder/decoder、ImageNet/FFHQ/CelebA-HQ、STE 和重建指标未复现。
- **修复：** 原实现让码本在同一批 1,024 向量上训练和评分，且 SQ 使用手工 abs-mean；现改为 4,096/1,024 train/test 分离，并对 SQ/PQ/VQ 都实际拟合码本；显式报告三类码本存储项数，避免只看 nominal rate。
- **结果：** 退出码 0，1.26 s；test MSE 为 SQ `2.38566e-4`、PQ `2.18012e-4`、VQ `1.90419e-4`，在此受控切片上恢复 VQ < PQ < SQ 的 distortion 次序。
- **真实 Qwen3-0.6B：未跑通模型量化（方法不适用）。** 只使用真实 checkpoint 的 embedding 数据做内在 rate-distortion 验证；没有修改模型、前向生成或保存量化模型。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；本地完整 Qwen3-0.6B checkpoint。
