# Attention Quantization for Tabular Foundation Models：Qwen3-0.6B 数值复现

论文：[arXiv:2609.13031](https://arxiv.org/abs/2609.13031)，[官方方法与表格](https://arxiv.org/html/2609.13031v1)。

实现的是逐头动态 absmax / 448 的 E4M3FN Q/K/V 量化、FP32 尺度、在线 softmax 中 256 指数提升和 FP8 P。无静态校准集、训练或权重量化。小张量配对 ICL 测试让 train–train 与 test–train 共享 K/V 和训练 Q 尺度，验证测试批次不变性。Qwen 适配保留其 Q/K norm、RoPE、GQA 和因果 mask，替换真实 28 层 attention 计算。

CPU 可执行参考使用真实 `torch.float8_e4m3fn` 转换和一字节存储，GEMM 前反量化为 FP32；不是 NVIDIA Triton FP8 融合内核。在线计算只分块沿 K，Q 全行保留；数值递推不等于原论文内核实现。Qwen 没有表格 ICL 双调用，其尺度按当前因果 prefill 张量确定，不能声称跨逐 token 解码保持尺度不变。本 demo 不实现持久 FP8 KV 或权重压缩。

## 运行

依赖已存在：Python 3.9、PyTorch 2.8.0、Transformers 4.57.6，macOS 26.6.2 arm64，CPU 4 线程。需要本地 Qwen3-0.6B 权重缓存；脚本 `local_files_only=True`，不会默默下载替代模型。

在此目录执行：

```sh
python3 demo.py --self-test-only --output tensor_results.json
python3 demo.py --model Qwen/Qwen3-0.6B --force-small --output results.json
python3 demo.py --model Qwen/Qwen3-0.6B --output gate_results.json
```

本次实际模型参数传入本地快照绝对路径：`/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca`。完整实际命令等价于上面的第二/三条替换 `--model` 值，其他参数默认 `--tokens 96 --tile 64 --threads 4`。

默认遵循论文 `N > 8192` 门控（Qwen 中以 key 长度类比 N），短输入不启用 FP8。`--force-small` 明确用于数值误差测试，不能用其计时复现原论文大表加速。

## 本次实测

权重 FP32，596,049,920 参数，3 段源码内固定中英文文本、70/81/91 token、`use_cache=False`。暖机一次，每段单次计时，未把单次时延当稳健性能结论。

| token | 基线 CE | FP8 参考 CE | logits 相对 L2 | argmax 一致率 | 基线/参考秒 |
|---:|---:|---:|---:|---:|---:|
| 70 | 2.317776 | 2.281809 | 0.071643 | 0.957143 | 0.1742 / 0.1971 |
| 81 | 2.180148 | 2.162833 | 0.067547 | 0.925926 | 0.1789 / 0.2115 |
| 91 | 1.753602 | 1.758144 | 0.060050 | 0.934066 | 0.1985 / 0.2169 |

`results.json` 记录 84 次量化注意力调用。参考路径更慢；三段小样本损失变化不能证明基准精度改善。`gate_results.json` 记录 84 次门控回退，所有 logits 相对误差为 0。

小张量检查通过：FP8 dtype/范围、零张量、非量化在线注意力对齐 SDPA、因果 mask、配对 train/test 共享尺度。测试批次拆分前后最大差 1.19209e-7。示例 FP16/FP8+尺度 QKV payload 比 1.971×，只描述该张量存储，不能当模型文件或进程内存倍率。

## 未完成的原论文复现

没有 NVIDIA GPU，未实现或执行 Triton FP8 原生 GEMM；未运行 TabPFN-v3/TabICLv2、TabArena/BeyondArena 或 N>8192 的端到端表格基准。论文的重要双调用结论仅以小张量机制验证，Qwen 运行属于因果模型迁移。所有结果都标记 `full_paper_reproduction=false`；没有伪造论文的 1.67× 加速。
