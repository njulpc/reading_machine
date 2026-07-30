# Paper: 2605.02404

**Statistically-Lossless Quantization of Large Language Models (SLQ)**

复现内容：对称 vs 非对称量化的 gamma^2 方差律实测；SLQ 逐层非均匀非对称量化（k-means 码本 + 比特宽度搜索）；EAR（Expected Acceptance Rate）代理指标。

验证方式：真实 Qwen3-0.6B 权重（down_proj 与 lm_head）。实测 3/4-bit 下对称量化噪声方差分别为非对称的 1.45/1.32 倍（定性验证 gamma^2 律）；SLQ 4-bit 权重相对误差 0.0106，EAR 代理（argmax 一致率）0.834。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
