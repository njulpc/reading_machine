# 2608.23834 Minima-KV 复现

按 [Minima-KV（arXiv:2608.23834）](https://arxiv.org/abs/2608.23834) 的 Recent/Anchor/Stale 三层设计，在真实 Qwen3-0.6B 128-token、28 层 KV cache 上保留 FP8 recent/anchor 页，将 stale 页做 Walsh-Hadamard rotation 与 3-bit fake quant；K 保留逐 token FP16 norm correction，V 使用 affine scale/zero，并把量化 cache 真正送回模型完成下一 token 解码。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-27）

- 算法一致性：**部分一致**。三层保留语义、FP8/TQ3 混合格式、旋转量化、K norm correction、V scale/zero 与统一逻辑 cache 均已覆盖；论文未公开足以逐 bit 重建 TQ3P 的完整 codec 常数，且实测系统使用 Qwen3.6-27B、1,792-token 页、TileLang/CUDA、物理打包和全局 online-softmax partial merge，本实现是 PyTorch materializing reference。
- 修复：原脚本用随机向量乘首层 K/V 权重，只验证一个扁平 attention 小张量，并把 K/V 都做同一种对称量化；现从真实模型 prefill 获取全部 28 层缓存，分别实现 K norm correction 和 V affine zero-point，再将量化 cache 回灌模型解码。
- 环境：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，safetensors 0.7.0；Apple arm64 CPU，CUDA/MPS 不可用。
- 结果：退出码 0；28 层、8 页均含 `FP8` 与 `TQ3`，含 codec metadata 的分析压缩率为 `2.8896x`（相对 BF16），量化 cache 下一 token logits relative-L2 为 `0.29993153`，下一 token 解码成功，总耗时 0.621 s。
- **真实 Qwen3-0.6B：已跑通**（真实全层 KV prefill、三层量化、cache 回灌与下一 token 解码）；论文物理 TQ3 packing、无 dense shadow、page ownership/retiering、全局 partial-softmax kernel、Blackwell 吞吐及 3.50x 部署账目未跑通。
