# 层级量化优先级（arXiv:2608.26926）Qwen3-0.6B 验证

脚本按论文 SA-PTQ 公式 (3)–(5) 做逐输出通道非对称 min/max Q8/Q4，捕获真实 prompt 在每个 MLP 的 last-token 输入，分别计算干净/量化 SwiGLU 完整输出的 SQNR；再按公式 (11)/(12) 归一化 quality，用真实 CPU FP32 前向作为 anchor、可配置带宽计算 Q8 单层 roofline saving 和 `log2(speedup)` speed score，并以公式 (26) 的 alpha 合成排序。默认把 10 个最低 Q8 quality 层保留为 Q8，其余 18 层改为 Q4，实际替换全部 84 个 MLP Linear 后执行整模前向与生成。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --quality-weight 0.5 --bandwidth-gbps 50 --q8-layers 10
```

## 代码审查与验证（2026-08-29）

**算法一致性：部分一致。** 已核对 arXiv v1 官方 PDF 的 SA-PTQ、FFN output SQNR、归一化、roofline 与 unified metric。原脚本把论文逐行非对称 Q8 改成对称 INT4，计算 weight SQNR 而非激活条件下的 FFN output SQNR，只看第 0 block 的 7 个 Linear，并用样本内 min-max 归一化速度；这些都会改变排名。现已改为论文公式，覆盖 28 个 FFN，并实际落地 Q8/Q4 混合配置。

迁移仍有明确边界：论文以 Gemma 3 1B 为主，用多个 prompt/10-token generation、T4 llama-bench F16 anchor 和 llama.cpp Q8_0，且 block-level metric还包含 tied embedding/lm_head；本脚本只用一个中文 prompt 的 last-token hidden、Apple CPU 单次前向 anchor，并只做 layer-wise FFN。Qwen 28 层形状相同，所以本次单层 speed score 均为 0.00224933，排序实质由 output SQNR 决定；50 GB/s 是显式 roofline 假设，不是本机低比特 benchmark。

环境为 Apple M4（10 核、16 GB）arm64 CPU，Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0；CUDA/MPS 均不可用。命令退出码 0，墙钟 2.85 秒。Q8 output SQNR 为 32.33099–40.49512 dB；最低的 10 层为 2、3、4、5、7、9、10、14、16、19，配置为 Q8，其余 18 层 Q4，共替换 264,241,152 个 FFN 权重。50 GB/s 模型预测 1.06117×，量化整模 logits MAE 0.74198663、last-token cosine 0.97351050，单 token 生成成功。

**真实 Qwen3-0.6B：已跑通（28 层真实 hidden 校准、全 MLP Q8/Q4 fake quant、整模前向/生成）。** 未跑通论文 Gemma/Qwen2.5 多 prompt 全实验、embedding/lm_head ranking、llama.cpp Q8_0/真实 INT kernel、T4 benchmark 或跨架构约 4% 预测误差复核；因此不能把本次 CPU roofline 结果当作实测加速。
