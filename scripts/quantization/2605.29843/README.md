# Paper: 2605.29843

**HARP: Hadamard-Preconditioned Adaptive Rotation Processor for Extreme LLM Quantization**

复现内容：蝶形（Givens 对）块正交级联作为可学习双侧旋转处理器，坐标下降在校准数据上拟合角度，与固定 RHT 对比 W4A4 式激活量化误差。

验证方式：真实 Qwen3-0.6B 嵌入导出激活。实测 HARP 4-bit 激活相对误差 0.0140，优于固定 RHT 的 0.0161。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
