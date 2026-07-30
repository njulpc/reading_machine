# Paper: 2605.10793

**ConQuR: Corner Aligned Activation Quantization via Optimized Rotations for LLMs**

复现内容：正交 Procrustes 闭式迭代学习旋转，将归一化激活对齐到内切超立方体角点；在线批处理校准（无需存储激活）。

验证方式：真实 Qwen3-0.6B 嵌入导出激活 + 合成异常通道激活两组场景，静态逐通道缩放的 4-bit 量化对比（无旋转/Hadamard/ConQuR）。实测合成异常通道场景 ConQuR(0.0180) ≤ Hadamard(0.0181) < 无旋转(0.0189)；嵌入激活场景三者接近（该代理下校准收益有限，如实报告）。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
