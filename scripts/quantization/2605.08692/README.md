# Paper: 2605.08692

**AAAC: Activation-Aware Adaptive Codebooks for 4-bit LLM Weight Quantization**

复现内容：双层学习 16 级非标量码本（加权 Lloyd 迭代），每组 128 权重按激活加权 MSE 选择码本（选择编码在组缩放符号位，零存储开销）。

验证方式：真实 Qwen3-0.6B 权重。实测 AAAC 激活加权相对误差 0.0156，优于固定 4-bit 网格基线 0.0177。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
