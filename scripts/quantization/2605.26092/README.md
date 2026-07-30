# Paper: 2605.26092

**GoQuant: Geometric Orthogonal Residual Projection for Multiplier-Free PoT Transformer Quantization**

复现内容：4-bit Power-of-Two 对数量化（移位替代乘法）+ 双基几何投影：一级 PoT 格 + 正交旋转二级残差 PoT 格，解析求解、保持 shift-and-add 结构。

验证方式：真实 Qwen3-0.6B 权重。实测 GoQuant 双基 4-bit 权重相对误差 0.0016，显著优于单级 PoT 的 0.0394，且两级均为 2 的幂格（无乘法器）。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
