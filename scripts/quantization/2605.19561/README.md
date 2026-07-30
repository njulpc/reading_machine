# Paper: 2605.19561

**TORQ: Two-Level Orthogonal Rotation for MXFP4 Quantization**

复现内容：忠实 MXFP4（E2M1，block=32，E8M0 共享指数）量化器；TORQ 两级正交旋转（宏观全基混合均衡块间能量 + 微观块内 Hadamard 抗码本坍塌）。

验证方式：真实 Qwen3-0.6B 嵌入导出激活 + 块不平衡合成激活。实测两组场景 TORQ 均降低 MXFP4 误差（0.0386→0.0383；0.0409→0.0400）。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
